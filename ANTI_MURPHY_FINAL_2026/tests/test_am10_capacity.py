from itertools import product
from unittest.mock import patch
from copy import deepcopy
import pytest
from simulation.factory import ScenarioConfig
from simulation.engine import run_simulation
from simulation.innovation import goal_seek,_capacity_plans
from atelier.service import Studio


def cfg():
 return ScenarioConfig('Ref',{'P':{'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':10,'setup_min':0}},[{'id':'A','quantidade':20,'prazo_h':100,'multa_hora':10,'route':[('P',60)]}])


def vector(plan,stations):
 return tuple(next((n for sid,f,n in plan if sid==s and f==field),0) for s in sorted(stations) for field in ['operadores','maquinas'])


@pytest.mark.parametrize('workers,machines',[(0,0),(1,0),(0,1),(1,1),(2,1),(2,2),(3,2)])
def test_enumeration_matches_independent_cartesian_reference(workers,machines):
 stations=['A','B'];plans=_capacity_plans(stations,workers,machines);got=[vector(x,stations) for x in plans]
 expected={v for v in product(range(workers+1),range(machines+1),range(workers+1),range(machines+1)) if 1<=sum(x>0 for x in v)<=2 and v[0]+v[2]<=workers and v[1]+v[3]<=machines}
 assert set(got)==expected;assert len(got)==len(set(got))
 assert [vector(x,stations) for x in _capacity_plans(stations[::-1],workers,machines)]==got


def test_real_same_station_combination_reaches_independent_reference():
 c=cfg();before=deepcopy(c);report={}
 with patch('simulation.engine._noise',return_value=1):
  base=run_simulation(c);rows=goal_seek(c,base,1.5,80,1,1,20,search_report=report)
 assert rows[0]['Atinge meta']=='Sim';assert rows[0]['Throughput']==2
 assert rows[0]['Makespan']==10;assert len(rows[0]['changes'])==2
 assert report['candidates_evaluated']==3 and report['returned_count']==3
 assert len([r for r in rows if r['Atinge meta']=='Não'])==2
 assert c==before


@pytest.mark.parametrize('limits',[(-1,1),(1,-1),(1.5,1),(True,1),(float('inf'),1)])
def test_invalid_budget_rejected(limits):
 with pytest.raises(ValueError):_capacity_plans(['P'],*limits)


def test_space_limit_explicit_before_any_simulation():
 c=cfg();base=run_simulation(c)
 with patch('simulation.innovation.run_simulation') as simulate:
  with pytest.raises(ValueError,match='10000'):goal_seek(c,base,1.5,80,10001,0)
  simulate.assert_not_called()


def test_zero_limit_and_result_truncation_do_not_change_evaluated_count():
 c=cfg();base=run_simulation(c);report={}
 assert goal_seek(c,base,1,80,0,0,12,search_report=report)==[];assert report['candidates_evaluated']==0
 result=goal_seek(c,base,1.5,80,1,1,1,search_report=report)
 assert len(result)==1;assert report['candidates_evaluated']==3;assert report['returned_count']==1
 with patch('simulation.innovation.run_simulation') as simulate:
  assert goal_seek(c,base,1,80,1,1,0)==[];simulate.assert_not_called()


def test_goal_satisfaction_precedes_cost_score_and_blocked_is_not_approved():
 c=cfg();base=run_simulation(c)
 def result(config):
  both=config.stations['P']['maquinas']==2 and config.stations['P']['operadores']==2
  return {**base,'precise':{**base['precise'],'throughput_h':2 if both else 1,'unit_cost':1e8 if both else 1}}
 with patch('simulation.innovation.run_simulation',side_effect=result):rows=goal_seek(c,base,1.5,80,1,1,1)
 assert rows[0]['Atinge meta']=='Sim'
 with patch('simulation.innovation.run_simulation',return_value={**base,'feasible':False}):
  assert all(r['Atinge meta']=='Não' for r in goal_seek(c,base,0,0,1,1,20))


def test_context_and_service_declare_actual_space(tmp_path):
 s=Studio(tmp_path);c=cfg();s.set_model({'stations':c.stations,'orders':c.orders})
 r=s.lab({'mode':'capacity','min_sla':80,'target_throughput':1.5})
 assert r['search_space']['candidates_evaluated']==5
 assert r['search_space']['max_extra_workers']==2
 assert any(x['goal_met'] for x in r['points'])
 assert r['provenance']['dependencies']['search_policy']=='station-resource-pairs-v2'
 assert any('maquinas' in x['changes'] and 'operadores' in x['changes'] for x in r['points'])
