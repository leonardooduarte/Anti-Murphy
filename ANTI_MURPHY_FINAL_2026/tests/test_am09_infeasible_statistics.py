from unittest.mock import patch
from copy import deepcopy
import statistics
import json
import pytest
from simulation.factory import ScenarioConfig
from simulation.innovation import stress_test
from simulation.advanced import monte_carlo_analysis
from atelier.service import Studio


def cfg():
 return ScenarioConfig('Ref',{'P':{'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':10,'setup_min':0}},[{'id':'A','quantidade':20,'prazo_h':100,'multa_hora':10,'route':[('P',60)]}])


def packet(feasible=True,value=10):
 return {'feasible':feasible,'throughput_h':value,'sla_pct':100 if feasible else 0,'makespan_h':value,'unit_cost':value,'bottleneck':'P','warnings':[] if feasible else ['Sem equipe em P']}


def test_real_stress_separates_eleven_infeasible_trials():
 r=stress_test(cfg(),runs=16,max_absent=1,demand_low=.9,demand_high=1.2,durations=(2.,4.,8.),seed=2026)
 valid=[x for x in r['runs'] if x['feasible']];bad=[x for x in r['runs'] if not x['feasible']]
 assert len(valid)==5 and len(bad)==11
 assert r['summary']['viable_runs']==5;assert r['summary']['infeasible_runs']==11
 assert r['fragility'][0]['Makespan médio']==round(statistics.mean(x['Makespan'] for x in valid),1)
 assert r['fragility'][0]['Makespan médio']>20
 for row in bad:assert row['Makespan'] is None;assert row['Custo/un'] is None;assert row['reason']
 assert r['summary']['resilience_rate']==round(100*sum(x['SLA']>=80 for x in valid)/16,1)
 json.dumps(r['summary'],allow_nan=False)


def test_stress_all_invalid_has_no_zero_statistics():
 with patch('simulation.innovation.run_simulation',return_value=packet(False)):
  r=stress_test(cfg(),runs=4)
 for key in ['sla_avg','sla_worst','makespan_p90','unit_cost_p90','throughput_p10']:assert r['summary'][key] is None
 assert r['summary']['resilience_rate']==0
 assert r['fragility'][0]['Índice de fragilidade'] is None


def test_stress_mixed_statistics_and_percentiles_use_valid_subset():
 with patch('simulation.innovation.run_simulation',side_effect=[packet(False),packet(True,10),packet(True,20)]):
  r=stress_test(cfg(),runs=3)
 assert r['summary']['makespan_p90']==20
 assert r['summary']['unit_cost_p90']==20
 assert r['fragility'][0]['Makespan médio']==15
 assert r['summary']['viable_runs']==2


@pytest.mark.parametrize('invalid_count',[0,1,3,4])
def test_monte_carlo_counts_and_missing_metrics(invalid_count):
 inputs=[packet(False)]*invalid_count+[packet(True,10)]*(4-invalid_count)
 with patch('simulation.advanced.run_simulation',side_effect=inputs):r=monte_carlo_analysis(cfg(),runs=4)
 n=4-invalid_count;assert r['sample']['viable_runs']==n;assert r['sample']['infeasible_runs']==invalid_count
 for key in ['makespan','throughput','sla','unit_cost']:
  a=r['summary'][key];assert a['n']==n
  assert a['mean']==(None if n==0 else 100 if key=='sla' else 10)
  if n<2:assert a['sd'] is None;assert a['ci_low'] is None;assert a['ci_high'] is None
 for row in r['runs']:
  if not row['feasible']:assert row['makespan'] is None;assert row['reason']
 json.dumps(r,allow_nan=False)


def test_monte_carlo_independent_valid_mean_variance_and_interval():
 with patch('simulation.advanced.run_simulation',side_effect=[packet(False),packet(True,10),packet(True,20),packet(False)]):r=monte_carlo_analysis(cfg(),runs=4)
 a=r['summary']['makespan'];assert a['mean']==15
 assert a['sd']==pytest.approx(50**.5)
 assert a['ci_low']==pytest.approx(15-1.96*5)
 assert r['bottleneck_share']==100


def test_all_viable_repeatability_and_seeds_unchanged():
 c=cfg();a=stress_test(c,runs=4,max_absent=0);b=stress_test(c,runs=4,max_absent=0)
 assert a['summary']==b['summary'];assert a['summary']['viable_runs']==4
 assert [x['config'].seed for x in a['runs']]==[2027,2028,2029,2030]
 assert c.absent_workers is None


def test_studio_preserves_feasibility_and_reason_in_lab_payload(tmp_path):
 s=Studio(tmp_path);c=cfg();s.set_model({'stations':c.stations,'orders':c.orders})
 r=s.lab({'mode':'stress'})
 assert r['summary']['infeasible_runs']>0
 assert any(p['feasible'] is False and p['reason'] and p['unit_cost'] is None for p in r['points'])
 assert r['provenance']['dependencies']['statistics_policy']=='am09-viable-only-v1'


def test_new_policy_only_invalidates_affected_experiments(tmp_path):
 s=Studio(tmp_path);contexts=s._analysis_contexts()
 assert 'statistics_policy' in contexts['lab:stress']['dependencies']
 assert 'statistics_policy' in contexts['advanced:uncertainty']['dependencies']
 assert 'statistics_policy' not in contexts['lab:duration']['dependencies']
