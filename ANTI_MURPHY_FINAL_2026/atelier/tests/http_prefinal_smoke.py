"""Smoke test of the real loopback HTTP server, separate from Chromium DOM tests."""
from pathlib import Path
import subprocess,sys,time,urllib.request,urllib.error,json,os
root=Path(__file__).resolve().parents[2]
port=18921
proc=subprocess.Popen([sys.executable,'-m','atelier.server','--no-browser','--port',str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
base=f'http://127.0.0.1:{port}'
try:
 for retry in range(55):
  if proc.poll() is not None:raise RuntimeError('Servidor encerrou no início: '+proc.stderr.read().decode('utf8'))
  try:
   urllib.request.urlopen(base+'/api/state',timeout=1).close();break
  except (urllib.error.URLError,TimeoutError):time.sleep(.16)
 else:raise RuntimeError('Servidor não respondeu')
 def get(path):
  with urllib.request.urlopen(base+path,timeout=8) as r:return r.status,r.headers.get('Content-Type'),r.read()
 def post(path,payload):
  req=urllib.request.Request(base+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
  with urllib.request.urlopen(req,timeout=12) as r:return r.status,json.loads(r.read())
 checks=[]
 for path in ['/','/app.js','/styles.css','/prefinal_polish.css','/brand/logo-dark.svg','/api/dashboards','/api/state']:
  status,kind,content=get(path);assert status==200 and len(content)>0,(path,status)
  checks.append((path,status,len(content)))
 a=json.loads(get('/api/state')[2]); b=json.loads(get('/api/dashboards')[2])
 assert a['run_id']==b['run_id']
 status,reply=post('/api/assistant',{'question':'Qual gargalo e quais pedidos estão em risco?'})
 assert status==200 and 'Gargalo identificado' in reply['text']
 assert 'Pedidos com atraso previsto' in reply['text']
 assert not json.loads(get('/api/history')[2])
 # No state mutation for assistant.
 assert a['selected']==json.loads(get('/api/state')[2])['selected']
 print('HTTP PASS',checks)
 print('Assistant label',reply['label'])
finally:
 proc.terminate()
 try:proc.wait(timeout=4)
 except subprocess.TimeoutExpired:proc.kill();proc.wait()
 # Remove temporary workspace: only test-created files, never a user's model.
 # Tests execute against the isolated release-candidate copy.
