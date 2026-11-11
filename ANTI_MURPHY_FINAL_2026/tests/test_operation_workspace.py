import json
from copy import deepcopy
import pytest
from simulation.operation import initialize_operation,handle_command,payload,memo
from simulation.nexus import current_analysis,current_spec,invalidate_model
from simulation.nexus_ai import make_proposal,execute_proposal


def workspace():
    state={};initialize_operation(state);return state


def send(state,kind,body=None,id=None,token=None):
    command={'id':id or kind+str(len(state['op_seen'])),'token':token or state['op_token'],'kind':kind,'body':body or {}}
    return handle_command(state,command)


def test_complete_response_workflow_and_export():
    state=workspace();send(state,'demo')
    data=current_analysis(state);assert data['timed_response']
    assert data['decision_h']==6
    leader=data['leader'];assert leader['timed_action']
    send(state,'timing');assert len(state['op_timing']['points'])>=5
    send(state,'sensitivity');plan=state['nx_pending']
    assert not state.get('nx_sensitivity')
    send(state,'authorize',{'proposal_id':plan['id']})
    assert len(state['nx_sensitivity']['pairs'])==8
    send(state,'record')
    result=json.loads(memo(state))
    assert result['examined_action']['requested_h']==6
    assert result['recommended_action']['action']==leader['action']
    assert result['record']['signature']==leader['signature']
    assert len(result['sha256'])==64
    json.dumps(payload(state))


def test_duplicate_and_stale_commands_cannot_execute_again():
    state=workspace();token=state['op_token']
    send(state,'demo',id='once')
    audit=deepcopy(state['audit_log'])
    assert not send(state,'demo',id='once')
    assert state['audit_log']==audit
    send(state,'simulate',{'duration_h':12.},id='stale',token=token)
    assert 'alterado' in state['op_notice']
    assert state['audit_log']==audit


def test_invalid_experiment_does_not_half_commit_parameters():
    state=workspace();send(state,'demo')
    spec=deepcopy(state['nx_spec']);delay=state['op_delay'];analysis=current_analysis(state)
    send(state,'simulate',{'station':'INVALID','delay_h':3.})
    assert state['nx_spec']==spec and state['op_delay']==delay
    assert current_analysis(state) is analysis


def test_question_only_prepares_a_budget_experiment_then_authorization_runs_it():
    state=workspace();send(state,'demo');run=current_analysis(state)['run_id']
    send(state,'ask',{'question':'Tenho apenas R$ 3.000 para resolver o problema.'})
    plan=state['nx_pending'];assert plan['spec']['budget']==3000
    assert current_analysis(state)['run_id']==run
    send(state,'authorize',{'proposal_id':plan['id']})
    assert current_analysis(state)['policy_inputs']['budget']==3000
    assert current_analysis(state)['timed_response']
    assert plan['id'] in state['nx_consumed']


def test_authorization_is_bound_to_response_time():
    state=workspace();send(state,'demo')
    plan=make_proposal(state,current_spec(state))
    state['op_delay']=4.
    with pytest.raises(ValueError,match='alterado'):execute_proposal(state,plan)


def test_examining_a_different_row_preserves_recommendation():
    state=workspace();send(state,'demo');data=current_analysis(state)
    reference=next(r for r in data['rows'] if r['action']=='Não intervir')
    send(state,'select',{'signature':reference['signature']})
    exported=json.loads(memo(state))
    assert exported['examined_action']['action']=='Não intervir'
    assert exported['recommended_action']['action']!='Não intervir'


def test_recalculation_and_model_changes_clear_old_decision_records():
    state=workspace();send(state,'demo');send(state,'record')
    assert state.get('op_record')
    send(state,'simulate',{'duration_h':6.})
    assert not state.get('op_record')
    invalidate_model(state);assert current_analysis(state) is None
    assert not state.get('nx_pending')
