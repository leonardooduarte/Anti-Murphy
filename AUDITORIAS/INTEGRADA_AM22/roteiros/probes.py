from pathlib import Path
import os
import sys,json,tempfile,math,heapq,random,hashlib,time
from copy import deepcopy
sys.path.insert(0,os.environ['ANTI_MURPHY_AUDIT_APP'])
from atelier.service import Studio
from simulation.factory import ScenarioConfig,TimedAction
from simulation.engine import run_simulation
r=Path(os.environ['ANTI_MURPHY_AUDIT_OUT']);out={'numeric_references':[]}
station={'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':5,'setup_min':0}
for minutes,eff,availability,machines,workers,ratio,quantity in [(.06,1,1,1,1,1,1),(1e-5,1,1,1,1,1,1),(.06,.001,1,1,1,1,1),(60,1,.5,2,2,1,7),(1,1,1,4,1,.5,9),(2,1,1,3,6,2,8)]:
 st={**station,'maquinas':machines,'operadores':workers,'operadores_por_maquina':ratio,'eficiencia_operador':eff,'disponibilidade':availability}
 orders=[{'id':'A','quantidade':quantity,'prazo_h':10000,'multa_hora':0,'route':[['P',minutes]]}]
 cfg=ScenarioConfig('Referência independente',{'P':st},orders,seed=42)
 durations=[]
 for u in range(quantity):
  seed=int.from_bytes(hashlib.blake2b(f'42|A|{u}|0'.encode(),digest_size=8).digest(),'big')
  durations.append(minutes*random.Random(seed).triangular(.96,1.05,1.)/60/eff/availability)
 heap=[0.] * min(machines,math.floor(workers/ratio));heapq.heapify(heap)
 for duration in durations:heapq.heappush(heap,heapq.heappop(heap)+duration)
 end=max(heap);busy=sum(durations)
 expected={'makespan_h':end,'throughput_h':quantity/end,'operating_cost':end*(machines*10+workers*5)}
 t=time.perf_counter();actual=run_simulation(cfg);elapsed=time.perf_counter()-t
 checks={k:math.isclose(actual['precise'][k],v,rel_tol=1e-12,abs_tol=1e-14) for k,v in expected.items()}
 checks['machine_util_pct']=math.isclose(actual['stations'][0]['precise']['machine_util_pct'],busy/end/machines*100,rel_tol=1e-12)
 checks['worker_util_pct']=math.isclose(actual['stations'][0]['precise']['worker_util_pct'],busy*ratio/end/workers*100,rel_tol=1e-12)
 assert all(checks.values()),(expected,actual)
 out['numeric_references'].append({'minutes':minutes,'efficiency':eff,'availability':availability,'machines':machines,'workers':workers,'labor_per_machine':ratio,'units':quantity,'expected':expected,'checks':checks,'elapsed_s':elapsed})
with tempfile.TemporaryDirectory() as d:
 s=Studio(Path(d));s.set_model({'stations':{'P':station},'orders':[{'id':'CURTA','quantidade':1,'prazo_h':.0005,'multa_hora':10000,'route':[['P',.06]]}]})
 s.calculate({'station':'P','start_h':10,'duration_h':1})
 from simulation.nexus import current_analysis
 a=current_analysis(s.state);result=a['normal'];audit=s.technical_audit()['orders']['normal'][0]
 assert result['orders'][0]['lateness_h']>0 and audit['slack_h']>=0
 out['short_order_report']={'engine_order':result['orders'][0],'technical_audit_order':audit,'makespan_h':result['precise']['makespan_h']}
with tempfile.TemporaryDirectory() as d:
 s=Studio(Path(d));a=s.save_experiment('Registro válido');p=s.experiments_dir/'invalid.json';p.write_text('[]')
 before=p.read_bytes()
 try:s.experiment_list();out['malformed_experiment']={'unexpected_success':True}
 except Exception as e:out['malformed_experiment']={'type':type(e).__name__,'message':str(e),'valid_experiment':a['id'],'file_preserved':p.read_bytes()==before}
# Temporal response: work completed before response must be identical.
cfg=ScenarioConfig('Temporal',{'P':deepcopy(station)},[{'id':'A','quantidade':20,'prazo_h':10,'multa_hora':0,'route':[['P',1]]}])
baseline=run_simulation(cfg);action=TimedAction(at_h=.05,workers_delta={'P':1},machines_delta={'P':1});response=run_simulation(cfg,action)
prefix=lambda x:[o for o in x['operations'] if o['end_h']<=.05]
assert prefix(baseline)==prefix(response)
end=response['precise']['makespan_h'];expected_cost=min(end,.05)*15+max(0,end-.05)*30
assert math.isclose(response['precise']['operating_cost'],expected_cost,rel_tol=1e-12)
out['temporal_reference']={'shared_completed_operations':len(prefix(baseline)),'cost_expected':expected_cost,'cost_actual':response['precise']['operating_cost']}
(r/'probes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
