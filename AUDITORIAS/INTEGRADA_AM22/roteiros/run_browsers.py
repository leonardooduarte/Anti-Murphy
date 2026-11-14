from pathlib import Path
import os
import os,subprocess,json,sys,time
r=Path(os.environ['ANTI_MURPHY_AUDIT_OUT']);app=Path(os.environ['ANTI_MURPHY_AUDIT_APP']);results=[]
modules=[('am07','AM07_QA_OUT'),('am08','AM08_QA_OUT'),('am09','AM09_QA_OUT'),('am10','AM10_QA_OUT'),('am12','AM12_QA_OUT'),('am13','AM13_QA_OUT'),('am14','AM14_QA_OUT'),('am15','AM15_QA_OUT'),('am16','AM16_QA_OUT'),('am17','AM17_QA_OUT'),('am22','AM22_QA_OUT'),('startup_recovery','RECOVERY_QA_OUT'),('optional_priority','PRIORITY_QA_OUT')]
for module,envkey in modules:
 log=r/f'browser-{module}.log';t=time.monotonic()
 try:
  with log.open('w') as f:
   p=subprocess.run([sys.executable,'-m','atelier.tests.browser_'+module],cwd=app,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1',envkey:str(r/f'capturas-{module}')},stdout=f,stderr=subprocess.STDOUT,timeout=120)
  row={'module':module,'exit_code':p.returncode,'elapsed_s':round(time.monotonic()-t,2),'log':log.name}
 except subprocess.TimeoutExpired:row={'module':module,'timeout_s':120,'log':log.name}
 results.append(row);(r/'browser-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(row),flush=True)
