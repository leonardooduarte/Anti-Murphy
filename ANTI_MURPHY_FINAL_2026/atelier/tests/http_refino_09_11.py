"""Post-release HTTP smoke of the decision review and real decision registration.

Uses localhost with a TEMPORARY workspace. No browser, npm, APIs or Streamlit.
Run from the project root: python -m atelier.tests.http_refino_09_11
"""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from atelier import server
from atelier.service import Studio


def test():
    with TemporaryDirectory() as tmp:
        server.STUDIO=Studio(Path(tmp))
        httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        thread=Thread(target=httpd.serve_forever,daemon=True)
        thread.start()
        base=f'http://127.0.0.1:{httpd.server_port}'
        try:
            for path in ('/','/app.js','/polimento_09_11.css','/api/state','/api/dashboards'):
                with urlopen(base+path,timeout=8) as res:
                    assert res.status==200,path
                    raw=res.read();assert len(raw)>100,path
                    if path=='/':assert b'polimento_09_11.css' in raw
            def post(path,body):
                req=Request(base+path,data=json.dumps(body).encode(),method='POST',headers={'Content-Type':'application/json'})
                with urlopen(req,timeout=10) as res:return json.load(res)
            state=post('/api/run',{'station':'CNC','start_h':4,'duration_h':8,'min_sla':40})
            other=next(a for a in state['alternatives'] if a['action']=='Não intervir')
            state=post('/api/select',{'signature':other['signature']})
            assert state['decision_review']['status']=='dominated'
            target=state['decision_review']['dominated_by'][0]
            assert target['action']=='Manutenção expressa · CNC'
            state=post('/api/select',{'signature':target['signature']})
            assert state['decision_review']['status']=='non_dominated'
            saved=post('/api/record',{'signature':target['signature'],'note':'Risco comparado e anotado pela equipe; sem operação real.',
                                      'risks':'Verificar habilitação, manutenção e custos evitáveis.','responsible':'Equipe de validação',
                                      'constraints_ack':True})
            assert saved['record']['decision_review']['status']=='non_dominated'
            with urlopen(base+'/api/history',timeout=5) as r:
                records=json.load(r)
            assert len(records)==1 and records[0]['action']==target['action']
            with urlopen(base+'/api/history/'+saved['filename'],timeout=5) as r:
                archive=json.load(r)
            assert 'Verificar habilitação' in archive['record']['risks']
            assert archive['record']['decision_review']['status']=='non_dominated'
            print('HTTP refinamento 09/11: CSS + status multicritério + seleção + registro + histórico OK',flush=True)
        finally:
            httpd.shutdown();httpd.server_close();thread.join(timeout=5)

if __name__=='__main__':test()
