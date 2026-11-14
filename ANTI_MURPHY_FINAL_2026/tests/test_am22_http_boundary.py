"""AM22: real HTTP must validate authority before any model access or write."""
import http.client
from http.server import ThreadingHTTPServer
from threading import Thread
from unittest.mock import Mock

import pytest
from atelier import server
from atelier.service import Studio


@pytest.fixture
def endpoint(tmp_path,monkeypatch):
    studio=Studio(tmp_path)
    spy=Mock(wraps=studio)
    monkeypatch.setattr(server,'STUDIO',spy)
    httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
    thread=Thread(target=httpd.serve_forever,daemon=True);thread.start()
    yield httpd.server_port,studio,spy
    httpd.shutdown();httpd.server_close();thread.join(timeout=3)


def request(port,method='GET',path='/api/state',headers=None,body=None):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
    c.putrequest(method,path,skip_host=True,skip_accept_encoding=True)
    for key,value in (headers or []):c.putheader(key,value)
    if body is not None:
        c.putheader('Content-Type','application/json');c.putheader('Content-Length',str(len(body)))
    c.endheaders(body)
    r=c.getresponse();result=r.status,r.read(),r.getheaders();c.close();return result


@pytest.mark.parametrize('method',['GET','POST'])
@pytest.mark.parametrize('bad',[
    'external.example:{port}','127.0.0.1.external.example:{port}',
    'localhost.external.example:{port}','127.0.0.2:{port}','0.0.0.0:{port}',
    'localhost.:{port}','user@localhost:{port}','localhost:1',
    'localhost:65536','localhost:{port}/','localhost:{port},external.example',
    '',None,
])
def test_untrusted_host_rejected_before_service(endpoint,method,bad):
    port,studio,spy=endpoint
    host=bad.format(port=port) if bad else bad
    headers=[] if host is None else [('Host',host)]
    if method=='POST' and host:headers.append(('Origin','http://'+host))
    before=(studio.storage/'projeto_confirmado.json').read_bytes()
    status,_,_=request(port,method,headers=headers,body=b'{"min_sla":71}' if method=='POST' else None)
    assert status==403
    assert not spy.method_calls
    assert (studio.storage/'projeto_confirmado.json').read_bytes()==before


@pytest.mark.parametrize('method',['GET','POST'])
@pytest.mark.parametrize('origin',[
    'null','https://127.0.0.1:{port}','http://external.example:{port}',
    'http://localhost:{port}','http://127.0.0.1:1',
    'http://user@127.0.0.1:{port}','http://127.0.0.1:{port}/',
    'http://127.0.0.1:{port}?x=1','http://127.0.0.1:{port}#fragment','',
])
def test_untrusted_origin_rejected_before_service(endpoint,method,origin):
    port,_,spy=endpoint
    status,_,_=request(port,method,headers=[('Host',f'127.0.0.1:{port}'),('Origin',origin.format(port=port))],body=b'{}' if method=='POST' else None)
    assert status==403
    assert not spy.method_calls


@pytest.mark.parametrize('header',['Host','Origin'])
def test_duplicate_boundary_headers_rejected(endpoint,header):
    port,_,spy=endpoint;host=f'127.0.0.1:{port}'
    headers=[('Host',host),('Origin','http://'+host)]
    headers.append((header,host if header=='Host' else 'http://'+host))
    assert request(port,headers=headers)[0]==403
    assert not spy.method_calls


@pytest.mark.parametrize('host',['127.0.0.1','localhost','LOCALHOST','[::1]'])
@pytest.mark.parametrize('with_origin',[False,True])
def test_local_clients_and_same_origin_browser_are_preserved(endpoint,host,with_origin):
    port,studio,_=endpoint;headers=[('Host',f'{host}:{port}')]
    if with_origin:headers.append(('Origin',f'http://{host}:{port}'))
    assert request(port,headers=headers)[0]==200
    assert request(port,'POST','/api/run',headers,b'{"min_sla":71}')[0]==200
    assert studio.info()['spec']['min_sla']==71


def test_static_files_and_exports_require_local_host(endpoint):
    port,_,spy=endpoint
    for path in ['/','/app.js','/api/model/export','/api/record/export']:
        assert request(port,path=path,headers=[('Host',f'external.example:{port}')])[0]==403
    assert not spy.method_calls


def test_absolute_request_target_is_rejected(endpoint):
    port,_,spy=endpoint
    assert request(port,path=f'http://external.example:{port}/api/state',headers=[('Host',f'localhost:{port}')])[0]==403
    assert not spy.method_calls


@pytest.mark.parametrize('host,port,expected',[
    ('localhost',80,('localhost',80)),
    ('127.0.0.1',80,('127.0.0.1',80)),
    ('localhost',8080,None),
    ('[::1]:8080',8080,('[::1]',8080)),
    ('::1:8080',8080,None),
    ('localhost:8080\t',8080,None),
    ('http://localhost:8080',8080,None),
    ('localhost:8080@external.example',8080,None),
])
def test_authority_has_explicit_http_default_port_and_strict_syntax(host,port,expected):
    assert server._local_authority(host,port)==expected
