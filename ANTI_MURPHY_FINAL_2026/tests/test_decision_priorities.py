import json
from dataclasses import replace
import pytest
from simulation.nexus import ExperimentSpec,execute,current_analysis,current_spec,selected_action
from simulation.operation import initialize_operation,handle_command,memo,report
from simulation.nexus_ai import make_proposal,execute_proposal


def workspace():
    s={};initialize_operation(s);return s


def send(s,kind,body=None):
    handle_command(s,{'id':str(len(s['op_seen'])),'token':s['op_token'],'kind':kind,'body':body or {}})


def test_priorities_choose_different_simulated_outcomes_for_the_same_incident():
    s=workspace();base=ExperimentSpec(duration_h=5,min_sla=0,budget_is_limit=True)
    analyses=[execute(s,replace(base,objective=goal,critical_order=critical)) for goal,critical in [('cost',''),('delivery',''),('critical','OP-101')]]
    assert len({a['leader']['action'] for a in analyses})==3
    cost,delivery,critical=analyses
    assert cost['leader']['decision_cost']<delivery['leader']['decision_cost']
    assert delivery['leader']['sla_pct']>=cost['leader']['sla_pct']
    assert delivery['leader']['makespan_h']<cost['leader']['makespan_h']
    assert critical['leader']['critical_finish_h']==min(r['critical_finish_h'] for r in critical['rows'] if r['feasible'] and r['within_budget'])
    assert len({a['run_id'] for a in analyses})==3


def test_zero_budget_is_a_real_limit_in_the_new_workflow():
    s=workspace();a=execute(s,ExperimentSpec(duration_h=8,budget=0,min_sla=0,budget_is_limit=True))
    assert any(r['within_budget'] for r in a['rows'])
    assert all(r['investment']==0 for r in a['rows'] if r['within_budget'])
    assert all(not r['within_budget'] for r in a['rows'] if r['investment']>0)
    legacy=execute(s,ExperimentSpec(duration_h=8,budget=0,budget_is_limit=False))
    assert all(r['within_budget'] for r in legacy['rows'])


def test_invalid_critical_order_does_not_publish_half_an_experiment():
    s=workspace();send(s,'demo');before=current_analysis(s);spec=s['nx_spec'].copy();delay=s['op_delay']
    send(s,'simulate',{'objective':'critical','critical_order':'OP-INEXISTENTE','delay_h':3})
    assert current_analysis(s) is before and s['nx_spec']==spec and s['op_delay']==delay
    assert 'pertencer' in s['op_notice']


def test_delaying_an_examined_action_keeps_it_even_when_it_becomes_unprofitable():
    s=workspace();send(s,'demo');action=selected_action(s)['action']
    send(s,'simulate',{'delay_h':8,'focus_action':action})
    r=selected_action(s);assert r['action']==action and r['requested_h']==12
    assert r['savings']==-1800
    assert json.loads(memo(s))['examined_action']['action']==action


def test_priority_change_invalidates_a_prepared_authorization():
    s=workspace();send(s,'demo');plan=make_proposal(s,current_spec(s))
    execute(s,replace(current_spec(s),objective='delivery'))
    with pytest.raises(ValueError,match='mudaram'):execute_proposal(s,plan)


def test_no_critical_improvement_is_reported_without_a_recommendation():
    s=workspace();a=execute(s,ExperimentSpec(station='SOLDA',duration_h=5,min_sla=0,objective='critical',critical_order='OP-101',budget_is_limit=True))
    assert a['leader'] is None
    assert a['policy_status']!='RESPOSTA PROMISSORA'


def test_murphy_explains_the_examined_response_instead_of_another_recommendation():
    s=workspace();send(s,'demo');a=current_analysis(s)
    r=next(r for r in a['rows'] if r['action'].startswith('+1 operador') and r['action']!=a['leader']['action'])
    send(s,'select',{'signature':r['signature']});send(s,'ask',{'question':'Por que esta resposta?'})
    text=s['nx_messages'][-1]['text']
    assert text.startswith('**Em exame: '+r['action'])
    assert len(text)<1000


def test_budget_question_prepares_zero_limit_without_running_it():
    s=workspace();send(s,'demo');before=current_analysis(s)
    send(s,'ask',{'question':'Tenho R$ 0. Compare as respostas.'})
    plan=s['nx_pending'];assert plan['spec']['budget']==0 and plan['spec']['budget_is_limit']
    assert current_analysis(s) is before
    send(s,'authorize',{'proposal_id':plan['id']})
    assert all(r['investment']==0 for r in current_analysis(s)['rows'] if r['within_budget'])


def test_report_preserves_recorded_and_examined_choices_and_escapes_notes():
    s=workspace();send(s,'demo');send(s,'record',{'note':'Confirmar <script>alert(1)</script>'})
    record=s['op_record'].copy();reference=next(r for r in current_analysis(s)['rows'] if r['action']=='Não intervir')
    send(s,'select',{'signature':reference['signature']})
    exported=json.loads(memo(s));html=report(s).decode()
    assert exported['record']['signature']==record['signature']
    assert exported['examined_action']['signature']==reference['signature']
    assert '&lt;script&gt;' in html and '<script>alert(1)</script>' not in html
    assert 'difere da decisão registrada' in html and '<style>' in html


def test_request_for_unlimited_budget_keeps_it_distinct_from_zero_investment():
    s=workspace();send(s,'demo');send(s,'ask',{'question':'Compare as respostas sem teto de orçamento.'})
    plan=s['nx_pending'];assert plan['spec']['budget']==0 and not plan['spec']['budget_is_limit']
    send(s,'authorize',{'proposal_id':plan['id']})
    assert all(r['within_budget'] for r in current_analysis(s)['rows'])


def test_export_without_an_examined_response_does_not_invent_zero_results():
    s=workspace();execute(s,ExperimentSpec(duration_h=8,budget=0,min_sla=100,budget_is_limit=True))
    assert selected_action(s) is None
    html=report(s).decode()
    assert 'Nenhuma resposta está em exame' in html
    assert 'Economia líquida prevista' not in html
