from simulation.nexus import initialize
from bridge.experiment_source import bundle_from_workspace
from simulation_contract import ComparisonBundle, validate_reconstruction

def test_current_workspace_generates_a_real_bundle():
    state={};initialize(state)
    bundle, a, b = bundle_from_workspace(state)
    validated=ComparisonBundle.model_validate(bundle)
    validate_reconstruction(validated)
    assert len(bundle['definition']['stations'])==len(state['stations'])
    assert a['feasible'] and b['feasible']
    assert bundle['branch_A']['summary']['feasible']=='unverified'
    assert bundle['branch_B']['summary']['feasible']=='unverified'

def test_model_changes_affect_trace():
    state={};initialize(state)
    bundle, _, _ = bundle_from_workspace(state)
    state['nx_spec']['duration_h']=float(state['nx_spec']['duration_h'])+1.0
    changed, _, _ = bundle_from_workspace(state)
    assert bundle['incident']['planned_end_us'] != changed['incident']['planned_end_us']
