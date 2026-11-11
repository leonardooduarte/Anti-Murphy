from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
from unittest.mock import Mock
import pytest
from simulation.nexus import (initialize, current_spec, base_config, current_analysis, execute,
    nominal, ExperimentSpec, use_demo, restore_model, invalidate_model)
from simulation.nexus_ai import (local_answer, make_proposal, execute_proposal, read_budget,
    propose_for_question, generative_answer)
from simulation.decision_council import classify_decision, select_recommended_action
from simulation.replay import replay_payload, snapshot
from simulation.atlas import DecisionPolicy
from simulation.engine import run_simulation
from ui.motion import twin_html

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def state():
    s={};initialize(s);return s


def test_reference_and_noop_are_never_recommended():
    incident={'total_cost':1000,'sla_pct':100,'makespan_h':10}
    r={'action':'Não intervir','feasible':True,'within_budget':True,'meets_sla':True,
       'decision_cost':1000,'sla_pct':100,'makespan_h':10}
    assert classify_decision(r,incident,incident)['verdict']=='REFERÊNCIA'
    r['action']='Adicionar recurso sem efeito'
    assert classify_decision(r,incident,incident)['verdict']=='SEM BENEFÍCIO'
    r.update(classify_decision(r,incident,incident))
    assert select_recommended_action([r]) is None


def test_all_views_share_authoritative_leader(state):
    a=execute(state,current_spec(state))
    assert a['recommended'] is a['leader']
    assert state['v27_decisions'] is state['v29_analysis']
    assert a['leader']['action']!='Não intervir'
    assert a['leader']['savings']==pytest.approx(a['incident']['total_cost']-a['leader']['decision_cost'],abs=.01)
    assert a['leader']['decision_cost']==pytest.approx(a['leader']['result']['total_cost']+a['leader']['investment'],abs=.01)


def test_policy_and_model_changes_hide_old_decisions(state):
    execute(state,current_spec(state));assert current_analysis(state)
    state['nx_spec']['budget']=100
    assert current_analysis(state) is None
    execute(state,current_spec(state));assert current_analysis(state)
    state['stations']['CNC']['operadores']+=1
    assert current_analysis(state) is None


@pytest.mark.parametrize('change',['model','policy'])
def test_plan_cannot_execute_against_changed_context(state,change):
    prop=make_proposal(state,current_spec(state))
    if change=='model':state['stations']['CORTE']['custo_maquina_h']+=10
    else:state['nx_spec']['min_sla']=100
    with pytest.raises(ValueError,match='mudaram'):execute_proposal(state,prop)
    assert 'v29_analysis' not in state


def test_plan_tampering_and_repeat_execution_rejected(state):
    p=make_proposal(state,current_spec(state));bad=deepcopy(p);bad['spec']['budget']=50000
    with pytest.raises(ValueError,match='alterado'):execute_proposal(state,bad)
    result=execute_proposal(state,p)
    assert result['run_id']
    with pytest.raises(ValueError,match='já foi executado'):execute_proposal(state,p)


def test_interpreting_ai_request_never_runs_engine(state,monkeypatch):
    engine=Mock(side_effect=AssertionError('Execution during interpretation'))
    monkeypatch.setattr('simulation.nexus_ai.execute',engine)
    out=local_answer('Minha CNC quebrou por 3 horas, início em 2 horas. Tenho R$ 3.000.',state)
    assert out['proposal']['spec']['duration_h']==3
    assert out['proposal']['spec']['start_h']==2
    assert out['proposal']['spec']['budget']==3000
    assert out['proposal']['requires_confirmation']
    assert 'v29_analysis' not in state
    engine.assert_not_called()


@pytest.mark.parametrize('q,amount',[('Tenho apenas R$ 3.000',3000),('Orçamento de 3 mil',3000),
    ('tenho R$ 2.500,50',2500.50),('orcamento: 3000',3000),('Qual o gargalo?',None)])
def test_portuguese_budgets(q,amount):assert read_budget(q)==amount


def test_unknown_broken_station_is_not_silently_assigned(state):
    out=local_answer('Minha máquina quebrou',state)
    assert out['proposal'] is None
    assert 'Informe o posto' in out['text']


def test_constraints_really_apply_to_ai_authorized_result(state):
    out=local_answer('Minha CNC quebrou. Tenho R$ 100. SLA mínimo 100%.',state)
    a=execute_proposal(state,out['proposal'])
    assert a['policy_inputs']['budget']==100 and a['policy_inputs']['min_sla']==100
    if a['leader']:
        assert a['leader']['investment']<=100 and a['leader']['sla_pct']>=100
    assert 'authorization' in state['audit_log'][-1]


def test_demo_is_reproducible_and_restores_original_model(state):
    state['stations']['CNC']['operadores']=3
    original=deepcopy(base_config(state))
    use_demo(state);run1=state['v29_analysis']['run_id'];ops=state['v29_analysis']['incident']['operations']
    use_demo(state)
    assert state['v29_analysis']['run_id']==run1
    assert state['v29_analysis']['incident']['operations']==ops
    restore_model(state)
    assert state['stations']==original.stations
    assert current_analysis(state) is None


def test_replay_mass_balance_outage_and_exact_completion(state):
    data=execute(state,current_spec(state));p=replay_payload(data['incident'])
    mid=snapshot(p,5)
    cnc=next(s for s in mid['stations'] if s['id']=='CNC')
    assert cnc['down'] and cnc['processing']==0
    assert cnc['queue']>0
    end=snapshot(p,p['horizon'])
    assert end['completed']==data['incident']['total_units']
    assert all(s['queue']==0 and s['active']==0 for s in end['stations'])
    assert sum(s['completed_operations'] for s in end['stations'])==len(data['incident']['operations'])
    for op in data['incident']['operations']:
        assert sum(b-a for a,b in op['process_segments'])==pytest.approx(op['Processando (h)'],abs=.000051)
        assert op['arrival_h']<=op['start_h']<=op['end_h']
        if op['Posto']=='CNC':
            assert all(b<=4 or a>=9 for a,b in op['process_segments'])


def test_no_machine_lane_overlaps(state):
    r=run_simulation(base_config(state));lanes={}
    for op in r['operations']:
        key=(op['Posto'],op['machine_slot']);lanes.setdefault(key,[]).append((op['start_h'],op['end_h']))
    for lane in lanes.values():
        intervals=sorted(lane)
        assert all(b<=c+1e-9 for (_,b),(c,_) in zip(intervals,intervals[1:]))


def test_browser_counter_core_matches_python_at_boundaries(state):
    p=replay_payload(execute(state,current_spec(state))['incident'])
    times=[0,3.9999,4,5,8.9999,9,p['horizon']]
    js="const c=require(process.argv[1]);let x='';process.stdin.on('data',d=>x+=d);process.stdin.on('end',()=>{const p=JSON.parse(x);console.log(JSON.stringify(p.ts.map(t=>c.snapshot(p.p,t))))});"
    import shutil
    node=shutil.which('node')
    if not node:pytest.skip('Node optional; run tools/test_motion.js for browser core checks')
    result=subprocess.run([node,'-e',js,str(ROOT/'ui/motion/replay-core.js')],input=json.dumps({'p':p,'ts':times}),text=True,capture_output=True,check=True)
    snaps=json.loads(result.stdout)
    for t,s in zip(times,snaps):
        py=snapshot(p,t)
        assert s['completed']==py['completed']
        assert [(x['id'],x['queue'],x['active'],x['processing'],x['down']) for x in s['stations']]==[(x['id'],x['queue'],x['active'],x['processing'],x['down']) for x in py['stations']]


def test_html_cannot_break_script_with_uploaded_names(state):
    state['stations']['CNC']['nome']='</script><script>alert(1)</script>'
    r=nominal(state);html=twin_html(r)
    assert '</script><script>alert(1)</script>' not in html
    assert '\\u003c/script\\u003e' in html


def test_sensitivity_reports_net_savings_and_consumes_authorization(state):
    a=execute(state,current_spec(state));action=a['leader']
    prop=make_proposal(state,current_spec(state),kind='sensitivity',action_signature=action['signature'])
    result=execute_proposal(state,prop)
    assert len(result['pairs'])==8
    assert result['mean_net_saving']==pytest.approx(result['mean_cost_saving_before_investment']-action['investment'],abs=.01)
    assert result['run_id']==a['run_id']


@pytest.mark.parametrize('value',[float('nan'),float('inf')])
def test_non_finite_policy_rejected(value):
    with pytest.raises(ValueError):DecisionPolicy(budget=value).validate()


def test_generative_tool_only_prepares_plan(state,monkeypatch):
    import sys,types
    fn=types.SimpleNamespace(type='function_call',name='prepare_experiment',arguments=json.dumps({'station':'CNC','start_h':4,'duration_h':2,'budget':3000,'min_sla':80}))
    resp=types.SimpleNamespace(output=[fn],output_text='Preparei uma hipótese.')
    create=Mock(return_value=resp)
    client=Mock();client.responses.create=create
    monkeypatch.setitem(sys.modules,'openai',types.SimpleNamespace(OpenAI=Mock(return_value=client)))
    out=generative_answer('Investigue a falha CNC',state,'test-key','configured-model')
    assert out['proposal']['spec']['budget']==3000
    assert 'v29_analysis' not in state
    assert create.call_args.kwargs['store'] is False
    packet=json.dumps(create.call_args.kwargs['input'])
    assert 'AutoPeças Alvorada' not in packet and 'test-key' not in packet


def test_budget_followup_preserves_pending_incident_not_defaults(state):
    first=local_answer('Minha CNC quebrou por 3 horas, início em 2 horas',state)
    state['nx_pending']=first['proposal']
    second=local_answer('Tenho apenas R$ 3.000.',state)
    assert second['proposal']['spec']['duration_h']==3
    assert second['proposal']['spec']['start_h']==2
    assert second['proposal']['spec']['budget']==3000


def test_comparing_calculated_alternatives_does_not_propose_redundant_run(state):
    execute(state,current_spec(state))
    out=local_answer('Compare realocar operadores com manutenção expressa.',state)
    assert out['rows']
    assert out['proposal'] is None


def test_new_explicit_test_can_repeat_same_parameters(state):
    p=make_proposal(state,current_spec(state));execute_proposal(state,p)
    p2=make_proposal(state,current_spec(state));assert p2['id']!=p['id']
    execute_proposal(state,p2)


def test_examined_export_keeps_recommendation_and_manual_selection_distinct(state):
    from simulation.atlas import decision_memo
    a=execute(state,current_spec(state));ref=next(r for r in a['rows'] if r['action']=='Não intervir')
    memo=json.loads(decision_memo(a,ref))
    assert memo['examined_action']['action']=='Não intervir'
    assert memo['recommended_action']['action']==a['leader']['action']


def test_model_editor_rejects_fractional_or_negative_resources():
    from simulation.model_io import integer
    for v in [1.5,-1,float('nan'),float('inf')]:
        with pytest.raises(ValueError):integer(v,'Recurso')


def test_json_automation_flag_cannot_turn_string_false_into_unmanned_capacity(state):
    from simulation.validation import validate_model
    state['stations']['CORTE']['automatizada']='false'
    assert any('automatizada' in e for e in validate_model(state['stations'],state['orders']))


def test_ai_does_not_offer_delay_reduction_when_no_orders_are_late(state):
    a=execute(state,current_spec(state));assert a['incident']['late_orders']==0
    out=local_answer('Qual alternativa reduz os atrasos sem aumentar os custos?',state)
    assert out['rows']==[]
    assert 'Nenhuma opção' in out['text']


def test_economic_recovery_ratio_is_undefined_when_crisis_adds_no_cost():
    b={'total_cost':1000,'sla_pct':100,'makespan_h':10}
    r={'action':'SMED','feasible':True,'within_budget':True,'meets_sla':True,'decision_cost':900,'sla_pct':100,'makespan_h':9}
    assert classify_decision(r,b,b)['economic_recovery_pct'] is None
