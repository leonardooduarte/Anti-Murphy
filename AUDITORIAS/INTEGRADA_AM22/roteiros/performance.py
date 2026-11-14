from pathlib import Path
import os
import sys,tempfile,time,json,resource
from copy import deepcopy
from unittest.mock import patch
sys.path.insert(0,os.environ['ANTI_MURPHY_AUDIT_APP'])
from atelier.service import Studio,StudioError
out={'environment':'Linux/Python 3.12, execução local sintética; não é benchmark no Windows','cases':[]}
with tempfile.TemporaryDirectory() as d:
 t=time.perf_counter();s=Studio(Path(d));out['default_start_s']=time.perf_counter()-t
 t=time.perf_counter();s.advanced({'mode':'uncertainty'});out['default_uncertainty_12_s']=time.perf_counter()-t
 station={'nome':'P','maquinas':2,'operadores':2,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':5,'setup_min':0}
 for units,steps in [(100,5),(2500,10)]:
  model={'stations':{'P':deepcopy(station)},'orders':[{'id':'A','quantidade':units,'prazo_h':100000,'multa_hora':1,'route':[['P',1]]*steps}]}
  t=time.perf_counter();info=s.set_model(model);elapsed=time.perf_counter()-t
  t=time.perf_counter();raw=json.dumps(info,ensure_ascii=False,allow_nan=False).encode();serialization=time.perf_counter()-t
  out['cases'].append({'units':units,'route_steps':steps,'operations_per_scenario':units*steps,'calculation_s':elapsed,'state_json_bytes':len(raw),'json_serialization_s':serialization,'workload':info['workload']})
 model['orders'][0]['route'].append(['P',1]);before=s.info()['run_id']
 with patch('atelier.service.execute') as execute:
  try:s.set_model(model);raise AssertionError('excess workload accepted')
  except StudioError as e:out['excessive_workload']={'error':str(e),'engine_called':execute.called,'run_preserved':s.info()['run_id']==before}
 assert not out['excessive_workload']['engine_called'] and out['excessive_workload']['run_preserved']
out['process_peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
Path(str(Path(os.environ['ANTI_MURPHY_AUDIT_OUT'])/'performance.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
