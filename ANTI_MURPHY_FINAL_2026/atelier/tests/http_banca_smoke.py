"""Exercises actual localhost HTTP endpoints against a real Studio process.

Invoked manually in a fresh extraction, not from pytest; writes a temporary
workspace only in the current program folder.
"""
import json, subprocess, sys, time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[2]
PORT=18849
BASE=f'http://127.0.0.1:{PORT}'
process=subprocess.Popen([sys.executable,'-m','atelier.server','--no-browser','--port',str(PORT)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(80):
        try:
            with urlopen(BASE+'/api/state',timeout=2) as r:
                state=json.load(r);break
        except Exception:time.sleep(.2)
    else:raise RuntimeError('Server did not start')
    checks=[]
    for path in ['/','/app.js','/banca.css','/dashboards.css','/api/dashboards','/api/technical-audit']:
        with urlopen(BASE+path,timeout=5) as r:
            assert r.status==200
            body=r.read()
            checks.append((path,len(body)))
            if path.endswith('technical-audit'):
                audit=json.loads(body)
                assert audit['run_id']==state['run_id']
                assert audit['costs']['all_reconciled']
    alts=[x for x in state['alternatives'] if x['signature']!=state['selected']]
    assert alts
    req=Request(BASE+'/api/select',data=json.dumps({'signature':alts[0]['signature']}).encode(),headers={'Content-Type':'application/json'},method='POST')
    with urlopen(req,timeout=5) as r: selected=json.load(r)
    with urlopen(BASE+'/api/technical-audit',timeout=5) as r: audit2=json.load(r)
    assert audit2['selected_signature']==selected['selected']==alts[0]['signature']
    print('HTTP checks OK',checks,'selection updated')
finally:
    process.terminate()
    try:process.wait(timeout=7)
    except subprocess.TimeoutExpired:process.kill()
    # The runtime workspace is intentionally not bundled in the release.
