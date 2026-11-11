from copy import deepcopy
from dataclasses import replace
import pytest
from data.scenarios import STATIONS_BASE,ORDERS_BASE
from simulation.factory import build_scenario,TimedAction
from simulation.engine import run_simulation
from simulation.response import analyze_response,timing_frontier,paired_response
from simulation.atlas import DecisionPolicy


def scenario():
    return build_scenario('Teste',STATIONS_BASE,ORDERS_BASE,chaos_station='CNC',chaos_start_h=4.,chaos_duration_h=8.)


def prefix(result,t):
    return sorted((o['OP'],o['Unidade'],o['Etapa'],o['arrival_h'],o['start_h'],
        tuple((a,min(b,t)) for a,b in o['process_segments'] if a<t)) for o in result['operations'] if o['start_h']<t)


@pytest.mark.parametrize('action',[
    TimedAction(6.,workers_delta={'CNC':1}),TimedAction(6.,machines_delta={'CNC':1}),
    TimedAction(6.,workers_delta={'MONTAGEM':-1,'CNC':1}),
    TimedAction(6.,dispatch_rule='SPT'),TimedAction(6.,repair_remaining_factor=.5)])
def test_responses_preserve_the_past_and_all_units(action):
    cfg=scenario();old=deepcopy(cfg)
    a=run_simulation(cfg);b=run_simulation(cfg,action)
    assert prefix(a,action.at_h)==prefix(b,action.at_h)
    assert len(a['operations'])==len(b['operations'])
    assert a['total_units']==b['total_units']==96
    assert cfg==old


def test_express_repair_only_changes_remaining_downtime():
    cfg=scenario();r=run_simulation(cfg,TimedAction(6.,repair_remaining_factor=.5))
    assert r['config'].chaos_duration_h==5.
    for o in r['operations']:
        for a,b in o['process_segments']:
            assert not(o['Posto']=='CNC' and max(a,4)<min(b,9))
    late=run_simulation(cfg,TimedAction(13.,repair_remaining_factor=.5))
    incident=run_simulation(cfg)
    assert late['makespan_h']==incident['makespan_h']
    assert late['total_cost']==incident['total_cost']


def test_transfer_waits_for_a_free_operator_and_never_double_books():
    cfg=scenario();cfg.stations['MONTAGEM']['operadores']=2
    action=TimedAction(13.,workers_delta={'MONTAGEM':-1,'CNC':1})
    r=run_simulation(cfg,action)
    effective=r['intervention']['effective_h'];assert effective>=13.
    for sid,s in cfg.stations.items():
        operations=[o for o in r['operations'] if o['Posto']==sid]
        for t in {o['start_h'] for o in operations}:
            active=sum(o['start_h']<=t<o['end_h'] for o in operations)
            workers=s['operadores']+((action.workers_delta or {}).get(sid,0) if t>=effective else 0)
            assert active<=s['maquinas']
            assert active*s.get('operadores_por_maquina',1)<=workers


def test_busy_donor_releases_the_worker_only_after_finishing_work():
    cfg=scenario();cfg.chaos_station=None;cfg.chaos_duration_h=0
    cfg.orders=[{**cfg.orders[0],'quantidade':2,'route':[('MONTAGEM',60.),('CNC',30.)]}]
    cfg.stations['MONTAGEM']['maquinas']=2
    result=run_simulation(cfg,TimedAction(.1,workers_delta={'MONTAGEM':-1,'CNC':1}))
    effective=result['intervention']['effective_h']
    assert effective>.1
    finishes=[o['end_h'] for o in result['operations'] if o['Posto']=='MONTAGEM']
    assert effective==min(finishes)


def test_cost_integrates_capacity_before_and_after_effective_transfer():
    cfg=scenario();r=run_simulation(cfg,TimedAction(6.,workers_delta={'MONTAGEM':-1,'CNC':1}))
    # Exact horizon is available in traces, while makespan_h is a rounded presentation value.
    horizon=max(o['end_h'] for o in r['operations']);at=r['intervention']['effective_h']
    total=0
    for sid,s in cfg.stations.items():
        delta={'MONTAGEM':-1,'CNC':1}.get(sid,0)
        total+=horizon*s['maquinas']*s['custo_maquina_h']
        total+=(min(at,horizon)*s['operadores']+max(0,horizon-at)*(s['operadores']+delta))*s['custo_operador_h']
    assert r['operating_cost']==round(total,2)


def test_action_after_completion_does_not_extend_the_horizon():
    cfg=scenario();a=run_simulation(cfg);b=run_simulation(cfg,TimedAction(100.,workers_delta={'CNC':1}))
    assert a['makespan_h']==b['makespan_h']
    assert a['total_cost']==b['total_cost']


@pytest.mark.parametrize('action',[TimedAction(float('nan')),TimedAction(-1),TimedAction(1,workers_delta={'CNC':-1}),TimedAction(6,repair_remaining_factor=0),TimedAction(3,repair_remaining_factor=.5)])
def test_invalid_responses_fail_before_simulation(action):
    with pytest.raises(ValueError):run_simulation(scenario(),action)


def test_timing_and_paired_sensitivity_use_the_same_response():
    cfg=scenario();cfg.chaos_station=None;cfg.chaos_duration_h=0
    data=analyze_response(cfg,'CNC',4.,8.,DecisionPolicy(),delay_h=2.)
    row=data['leader'];assert row is not None
    assert row['requested_h']==6.
    frontier=timing_frontier(data,row)
    assert next(p for p in frontier if p['delay_h']==2)['net_saving']==row['savings']
    assert len({p['net_saving'] for p in frontier})>1
    sensitivity=paired_response(row)
    assert len(sensitivity['pairs'])==8
    assert all(p['net_saving']==round(p['cost_saving']-row['investment'],2) for p in sensitivity['pairs'])
