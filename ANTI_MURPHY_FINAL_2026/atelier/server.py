"""Local-only HTTP server for the integrated Anti-Murphy workbench.
No npm, cloud services, Streamlit, database or optional Python packages required.
"""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote
import json, mimetypes, os, re, sys, threading, traceback, webbrowser

from atelier.service import Studio, StudioError

ROOT=Path(__file__).resolve().parents[1]
WEB=Path(__file__).resolve().parent/'web'
STUDIO=None


def _local_authority(value, port):
    """Accept only explicit loopback names at this HTTP listener's port.

    No DNS lookup: a remote name resolving to loopback is still untrusted.
    localhost and numeric loopback remain distinct browser origins.
    """
    match=re.fullmatch(r'(localhost|127\.0\.0\.1|\[::1\])(?::([0-9]{1,5}))?',value,re.IGNORECASE|re.ASCII)
    if match is None:
        return None
    effective_port=int(match.group(2)) if match.group(2) else 80
    if effective_port!=port:
        return None
    return match.group(1).lower(),effective_port


class Handler(BaseHTTPRequestHandler):
    server_version='AntiMurphy/0.1'
    def log_message(self, fmt, *args):
        sys.stdout.write('[http] '+fmt%args+'\n')

    def send_bytes(self, content, status=200, mime='application/json; charset=utf-8',filename=None):
        self.send_response(status)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(content)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store' if mime.startswith('application/json') else 'public, max-age=300')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
        if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
        self.end_headers();self.wfile.write(content)

    def send_json(self,payload,status=200):
        self.send_bytes(json.dumps(payload,ensure_ascii=False,allow_nan=False,default=str).encode('utf8'),status)

    def _fail(self,error,status=400):
        self.send_json({'error':str(error)},status)

    def _allow_local_request(self):
        hosts=self.headers.get_all('Host',[])
        origins=self.headers.get_all('Origin',[])
        authority=_local_authority(hosts[0],self.server.server_port) if len(hosts)==1 else None
        if authority is None or not self.path.startswith('/'):
            self._fail('Endereço da requisição não autorizado. Use o endereço local exibido na inicialização.',403)
            return False
        if origins:
            origin=origins[0]
            # Serialized browser origins contain only scheme and authority.
            origin_authority=(_local_authority(origin[7:],self.server.server_port)
                              if origin.startswith('http://') else None)
            if len(origins)!=1 or origin_authority!=authority:
                self._fail('Origem da requisição não autorizada.',403)
                return False
        return True

    def do_GET(self):
        if not self._allow_local_request():return
        try:
            path=unquote(urlparse(self.path).path)
            if path=='/api/state':return self.send_json(STUDIO.info())
            if path=='/api/history':return self.send_json(STUDIO.history())
            if path=='/api/projects':return self.send_json(STUDIO.projects())
            if path=='/api/experiments':return self.send_json(STUDIO.experiment_list())
            if path=='/api/experiment-library':return self.send_json(STUDIO.experiment_library())
            if path=='/api/dashboards':return self.send_json(STUDIO.dashboards())
            if path=='/api/technical-audit':return self.send_json(STUDIO.technical_audit())
            if path=='/api/record/export':
                return self.send_bytes(STUDIO.export_decision(),mime='application/json; charset=utf-8',filename='anti_murphy_experimento.json')
            if path=='/api/model/export':
                return self.send_bytes(STUDIO.export_model(),mime='application/json; charset=utf-8',filename='anti_murphy_modelo.json')
            if path.startswith('/api/history/'):
                return self.send_json(STUDIO.read_history(path.rsplit('/',1)[-1]))
            if path.startswith('/api/'):return self._fail('Rota não encontrada.',404)
            rel=path.lstrip('/') or 'index.html'
            target=(WEB/rel).resolve()
            if not target.is_relative_to(WEB.resolve()) or not target.is_file():return self._fail('Arquivo não encontrado.',404)
            mime=mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
            if mime.startswith('text/') or mime in ('application/javascript','image/svg+xml'):
                mime+='; charset=utf-8'
            return self.send_bytes(target.read_bytes(),mime=mime)
        except StudioError as e:return self._fail(e)
        except (OSError,ValueError,KeyError,TypeError) as e:return self._fail(e)
        except Exception:
            traceback.print_exc();return self._fail('Falha interna. Consulte o registro de inicialização.',500)

    def do_POST(self):
        if not self._allow_local_request():return
        if self.headers.get('Content-Type','').split(';',1)[0].strip()!='application/json':
            return self._fail('Envie dados em JSON.',415)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<0 or size>2_000_000:return self._fail('Dados excedem o limite de 2 MB.',413)
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict):raise StudioError('Formato de dados inválido.')
            path=urlparse(self.path).path
            if path=='/api/run':response=STUDIO.calculate(body)
            elif path=='/api/select':response=STUDIO.select(str(body.get('signature','')))
            elif path=='/api/model':response=STUDIO.set_model(body)
            elif path=='/api/reset':response=STUDIO.reset()
            elif path=='/api/record':response=STUDIO.decision(body)
            elif path=='/api/assistant':response=STUDIO.assistant(body.get('question',''))
            elif path=='/api/lab':response=STUDIO.lab(body)
            elif path=='/api/advanced':response=STUDIO.advanced(body)
            elif path=='/api/project/create':response=STUDIO.create_project(body.get('name'),body.get('duplicate',True))
            elif path=='/api/project/open':response=STUDIO.open_project(str(body.get('id','')))
            elif path=='/api/project/rename':response=STUDIO.rename_project(body.get('name'))
            elif path=='/api/experiment/save':response=STUDIO.save_experiment(body.get('name'))
            elif path=='/api/experiment/compare':response=STUDIO.compare_experiments(body.get('first'),body.get('second'))
            else:return self._fail('Rota não encontrada.',404)
            self.send_json(response)
        except (StudioError,ValueError,KeyError,TypeError,OverflowError) as e:return self._fail(e)
        except Exception:
            traceback.print_exc();return self._fail('Falha interna. Consulte o registro de inicialização.',500)


def main(open_browser=True, port=0):
    global STUDIO
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--port',type=int,default=port)
    args=parser.parse_args()
    STUDIO=Studio(ROOT/'workspace')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    url=f'http://127.0.0.1:{server.server_port}/'
    # Saved locally so preserved ATLAS/NEXUS screens can return to the active workbench.
    (ROOT/'workspace').mkdir(exist_ok=True)
    (ROOT/'workspace'/'.main_url.json').write_text(json.dumps({'port':server.server_port}),encoding='utf8')
    print('Anti-Murphy disponível em',url,flush=True)
    def _open_app():
        if os.name=='nt':
            try:
                os.startfile(url)  # Uses the Windows default browser.
                return
            except OSError:
                pass
        webbrowser.open(url,new=2)
    if open_browser and not args.no_browser:
        threading.Timer(.7,_open_app).start()
    try:server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:print('Encerrando Anti-Murphy.')
    finally:
        server.server_close()
        try:(ROOT/'workspace'/'.main_url.json').unlink(missing_ok=True)
        except OSError:pass


if __name__=='__main__':main()
