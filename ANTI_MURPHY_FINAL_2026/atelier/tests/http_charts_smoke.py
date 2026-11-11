"""Local HTTP smoke test for the engineering-charts release.
Run: python atelier/tests/http_charts_smoke.py
No browser automation, npm or external network required.
"""
import subprocess,sys,time,json
from pathlib import Path
from urllib.request import urlopen,Request
ROOT=Path(__file__).resolve().parents[2];PORT=18893;BASE=f'http://127.0.0.1:{PORT}'
def get(path):
    with urlopen(BASE+path,timeout=15) as r:
        assert r.status==200,(path,r.status)
        return r.read()
def post(path,data):
    req=Request(BASE+path,data=json.dumps(data).encode('utf8'),headers={'Content-Type':'application/json'},method='POST')
    with urlopen(req,timeout=25) as r:
        assert r.status==200
        return json.loads(r.read())
proc=subprocess.Popen([sys.executable,'-m','atelier.server','--no-browser','--port',str(PORT)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(70):
        try:state=json.loads(get('/api/state'));break
        except Exception:time.sleep(.2)
    else:raise RuntimeError('Servidor HTTP não iniciou')
    for path in ('/','/app.js','/engineering_charts.js','/engineering_charts.css','/final_banca.css','/api/dashboards'):
        assert len(get(path))>100,path
    assert b'engineering_charts.js' in get('/') and b'final_banca.css' in get('/') and b'presentation-guide' in get('/')
    for scope,modes in (
        ('lab',['duration','dispatch','robustness','goal','stress','capacity']),
        ('advanced',['diagnostic','opportunities','sensitivity','demand','uncertainty','recovery']),
    ):
        for mode in modes:
            result=post('/api/'+scope,{'mode':mode,'station':'CNC','resource':'operadores','min_sla':80,'target_throughput':5.5})
            assert result['mode']==mode
            points=result.get('points',result.get('pairs',result.get('rows',result.get('stations',[]))))
            assert len(points)>0,(scope,mode)
            if scope=='advanced':assert result['experiment_id']==state['run_id']
    new=json.loads(get('/api/state'))
    assert state['run_id']==new['run_id'] and state['selected']==new['selected']
    print('HTTP OK · 6 rotas estáticas/dados · 12 análises reais · modelo/seleção preservados')
finally:
    proc.terminate()
    try:proc.wait(timeout=7)
    except subprocess.TimeoutExpired:proc.kill()
