from pathlib import Path
import os,json,subprocess,sys,time
r=Path('/workspace/work/verificacao-final');app=r/'base/ANTI_MURPHY_FINAL_2026';rows=[]
cases=[('int01','INT01_QA_OUT'),('int02','INT02_QA_OUT'),('int03','INT03_QA_OUT'),('int04','INT04_QA_OUT'),('am08','AM08_QA_OUT'),('acabamento_final',None)]
for name,key in cases:
 out=r/('capturas-'+name);env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
 if key:env[key]=str(out)
 t=time.monotonic()
 with (r/('browser-'+name+'.log')).open('w') as f:
  p=subprocess.run([sys.executable,'-m','atelier.tests.browser_'+name],cwd=app,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 row={'name':name,'exit_code':p.returncode,'elapsed_s':round(time.monotonic()-t,2)};rows.append(row);(r/'contract-results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
 if p.returncode:break
if all(x['exit_code']==0 for x in rows) and len(rows)==len(cases):
 out=r/'capturas-banca';out.mkdir()
 with (r/'browser-banca.log').open('w') as f:
  p=subprocess.run([sys.executable,'docs/AM19/evidencias/actual_http_browser.py'],cwd=app,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','AM19_BANCA_OUT':str(out)},stdout=f,stderr=subprocess.STDOUT,timeout=120)
 rows.append({'name':'banca_http','exit_code':p.returncode});(r/'contract-results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[-1]),flush=True)
