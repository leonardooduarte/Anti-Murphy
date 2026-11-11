"""Independent AM-05 dependency and origin contracts (no UI recalculation)."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from atelier.analysis_provenance import contexts, inputs, signature, LAB_MODES, ADVANCED_MODES
from atelier.service import Studio
from simulation.nexus import current_analysis, selected_action


@pytest.fixture(scope='module')
def reference():
    with TemporaryDirectory() as folder:
        studio=Studio(Path(folder))
        analysis=current_analysis(studio.state)
        yield deepcopy(studio.state), deepcopy(selected_action(studio.state,analysis))


def context_keys():
    return {'lab:'+x for x in LAB_MODES}|{'advanced:'+x for x in ADVANCED_MODES}


def changed(reference, mutate):
    state,row=reference
    before=contexts(state,'P',row)
    after_state=deepcopy(state);mutate(after_state)
    after=contexts(after_state,'P',row)
    return {k for k in before if before[k]['context_signature']!=after[k]['context_signature']}


def test_all_twelve_tools_have_named_context(reference):
    state,row=reference
    assert set(contexts(state,'P',row))==context_keys()


@pytest.mark.parametrize('field', ['nome','custo_maquina_h','eficiencia_operador','maquinas'])
def test_model_inputs_change_every_tool(reference,field):
    def modify(s):
        station=s['stations'][next(iter(s['stations']))]
        station[field]=station[field]+' extra' if isinstance(station[field],str) else station[field]+1
    assert changed(reference,modify)==context_keys()


def test_orders_change_every_tool(reference):
    assert changed(reference,lambda s:s['orders'][0].update(quantidade=s['orders'][0]['quantidade']+1))==context_keys()


def test_project_identity_invalidates_every_context_even_identical_model(reference):
    state,row=reference
    a,b=contexts(state,'principal',row),contexts(state,'clone',row)
    assert all(a[k]['context_signature']!=b[k]['context_signature'] for k in a)


@pytest.mark.parametrize('field', ['nx_source','nx_page','nx_reduced_motion','nx_selected'])
def test_presentation_and_examined_selection_do_not_change_dependencies(reference,field):
    assert changed(reference,lambda s:s.update({field:'different'}))==set()


def test_seed_affects_only_tools_that_use_it(reference):
    expected=context_keys()-{'lab:stress','lab:robustness','advanced:uncertainty'}
    assert changed(reference,lambda s:s.update(nx_seed=s['nx_seed']+1))==expected


def test_original_dispatch_rule_irrelevant_when_tool_sweeps_it(reference):
    assert 'lab:dispatch' not in changed(reference,lambda s:s.update(nx_rule='FIFO'))


def test_duration_change_ignored_by_duration_sweep_and_nominal_tools(reference):
    actual=changed(reference,lambda s:s['nx_spec'].update(duration_h=1))
    assert actual=={'lab:dispatch','lab:robustness','lab:goal','advanced:diagnostic','advanced:uncertainty','advanced:recovery'}


@pytest.mark.parametrize('field,value', [('start_h',1),('station','SOLDA')])
def test_incident_location_time_dependencies(reference,field,value):
    actual=changed(reference,lambda s:s['nx_spec'].update({field:value}))
    assert actual=={'lab:duration','lab:dispatch','lab:robustness','lab:goal','advanced:diagnostic','advanced:uncertainty','advanced:recovery'}


def test_delay_only_changes_tools_which_use_response_time(reference):
    assert changed(reference,lambda s:s.update(op_delay=12))=={'lab:goal','advanced:recovery'}
    # The paired experiment follows the selected immutable action, whose at_h is
    # its input. A real recomputation changes that action separately.


def test_selected_response_changes_only_paired_experiment(reference):
    state,row=reference
    a=contexts(state,'P',row);b=contexts(state,'P',None)
    assert {k for k in a if a[k]['context_signature']!=b[k]['context_signature']}=={'lab:robustness'}


@pytest.mark.parametrize('field,value', [('budget',0),('min_sla',100),('cost_worker',999),('objective','delivery')])
def test_policy_only_changes_goal_tool(reference,field,value):
    assert changed(reference,lambda s:s['nx_spec'].update({field:value}))=={'lab:goal'}


def test_station_iteration_order_is_a_real_seeded_dependency(reference):
    def reorder(s):s['stations']=dict(reversed(list(s['stations'].items())))
    assert changed(reference,reorder)==context_keys()


@pytest.mark.parametrize('scope,mode,payload,expected', [
 ('lab','duration',{'min_sla':90,'station':'CNC'},{}),
 ('lab','goal',{}, {'min_sla':80}),
 ('lab','capacity',{}, {'min_sla':80,'target_throughput':5.5}),
 ('advanced','demand',{}, {'min_sla':80}),
 ('advanced','sensitivity',{'resource':'maquinas'}, {'station':'CNC','resource':'maquinas'}),
 ('advanced','uncertainty',{'min_sla':100},{}),
])
def test_normalized_inputs_are_only_effective_controls(reference,scope,mode,payload,expected):
    state,_=reference
    assert inputs(scope,mode,payload,state)==expected


def test_canonical_signature_equivalent_numbers_and_dict_key_order():
    assert signature({'x':80,'y':[1,2]})==signature({'y':(1.,2.),'x':80.})


def test_stamp_deterministic_without_timestamp_and_preserves_origin():
    with TemporaryDirectory() as tmp:
        s=Studio(Path(tmp))
        a=s.lab({'mode':'goal','min_sla':0})
        b=s.lab({'mode':'goal','min_sla':0.0})
        c=s.lab({'mode':'goal','min_sla':100})
        assert len(a['points'])==18 and len(c['points'])==1
        assert a['provenance']['signature']==b['provenance']['signature']
        assert a['provenance']['calculated_at']!=b['provenance']['calculated_at']
        assert a['provenance']['context_signature']==c['provenance']['context_signature']
        assert a['provenance']['signature']!=c['provenance']['signature']
        assert a['provenance']['inputs']=={'min_sla':0}
        assert a['provenance']['project_name']=='Projeto principal'
        assert 'stations' in a['provenance']['dependencies']
        origin=deepcopy(a['provenance'])
        s.rename_project('Novo nome')
        assert a['provenance']==origin
        assert s.lab({'mode':'goal','min_sla':0})['provenance']['signature']==origin['signature']


def test_signature_preserved_for_irrelevant_selection_and_result_points():
    with TemporaryDirectory() as tmp:
        s=Studio(Path(tmp));a=s.lab({'mode':'duration'})
        other=next(x for x in s.info()['alternatives'] if x['action']=='Não intervir')
        s.select(other['signature']);b=s.lab({'mode':'duration'})
        assert a['points']==b['points']
        assert a['provenance']['signature']==b['provenance']['signature']


@pytest.mark.parametrize('mode',ADVANCED_MODES)
def test_advanced_scope_and_origin_explicit(mode):
    with TemporaryDirectory() as tmp:
        s=Studio(Path(tmp));out=s.advanced({'mode':mode})
        pr=out['provenance']
        assert pr['scope']=='advanced'
        assert pr['context_key']=='advanced:'+mode
        assert pr['context_signature']==s.info()['analysis_contexts'][pr['context_key']]['context_signature']
        assert pr['project_id']==s.project_id and pr['source']
        if mode=='diagnostic':assert out['bottleneck']==s.info()['metrics']['incident']['bottleneck']


def test_info_contexts_are_small_and_do_not_run_engine():
    with TemporaryDirectory() as tmp:
        s=Studio(Path(tmp))
        with patch('atelier.service.run_simulation',side_effect=AssertionError('no recalc')):
            view=s.info()
        assert all(set(value)=={'context_signature'} for value in view['analysis_contexts'].values())


def test_dashboard_and_audit_snapshots_guard_current_complete_analysis_context():
    with TemporaryDirectory() as tmp:
        s=Studio(Path(tmp));view=s.info()
        old=s.dashboards();audit=s.technical_audit()
        assert old['analysis_signature']==audit['analysis_signature']==view['analysis_signature']
        other=next(x for x in view['alternatives'] if x['action']=='Não intervir')
        s.select(other['signature']);new=s.info()
        assert old['analysis_signature']!=new['analysis_signature']
        assert s.dashboards()['analysis_signature']==new['analysis_signature']
        assert s.technical_audit()['analysis_signature']==new['analysis_signature']
