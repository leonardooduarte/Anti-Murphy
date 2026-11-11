"""Suite independente do engine: teste de contrato, dados e busca temporal."""
import json
from copy import deepcopy
import pytest
from pydantic import ValidationError
from make_example import example_bundle
from simulation_contract import (
    BranchSummary, ComparisonBundle, ConstraintCheck, EventDelta, FlowEdge,
    OrderState, SimulationSnapshot, StationState, apply_delta,
    hours_to_us, seek, validate_reconstruction, export_bundle,
)

H = hours_to_us


def data():
    return example_bundle().model_dump(by_alias=True)


def test_roundtrip_v110():
    b = example_bundle()
    revived = ComparisonBundle.model_validate_json(b.model_dump_json(by_alias=True))
    assert revived == b
    validate_reconstruction(revived)


def test_bundle_has_single_shared_prefix():
    b = example_bundle()
    assert len(b.common_history.events) == 1
    assert len(b.branch_a.events) == 1
    assert len(b.branch_b.events) == 2
    assert all(e.time_us >= b.fork.time_us for branch in (b.branch_a, b.branch_b) for e in branch.events)
    assert all(f.branch_id != 'common' for branch in (b.branch_a, b.branch_b) for f in branch.keyframes)
    assert b.branch_a.events[0].seq == b.branch_b.events[0].seq == b.fork.seq + 1
    assert b.branch_a.keyframes[0].seq == 2 and b.branch_b.keyframes[0].seq == 3


def test_no_redundant_prefork_on_branches():
    d = data()
    assert 'common_history' in d and 'branch_A' in d and 'branch_B' in d
    assert all(e['time_us'] > d['fork']['time_us'] or e['seq'] == d['fork']['seq']+1
               for e in d['branch_A']['events'] + d['branch_B']['events'])


def test_topology_root_and_coordinates():
    b = example_bundle()
    assert len(b.topology.edges) == 2
    assert (b.topology.edges[0].source, b.topology.edges[0].target) == ('CORTE','CNC')
    assert b.topology.edges[0].waypoints[0].x == .31
    assert b.topology.transport_semantics == 'logical_instantaneous'


def test_topology_missing_route_rejected():
    d = data()
    d['topology']['edges'].pop()
    with pytest.raises(ValidationError, match='rota nao conectada'):
        ComparisonBundle.model_validate(d)


def test_topology_dangling_edge_rejected():
    d = data()
    d['topology']['edges'][0]['target'] = 'FANTASMA'
    with pytest.raises(ValidationError, match='topologia referencia'):
        ComparisonBundle.model_validate(d)


def test_topology_repeated_edges_rejected():
    d = data()
    d['topology']['edges'].append(deepcopy(d['topology']['edges'][0]))
    with pytest.raises(ValidationError, match='duplicadas'):
        ComparisonBundle.model_validate(d)


def test_keyframe_requires_queue_ids():
    d = data()
    del d['common_history']['keyframes'][0]['stations']['CNC']['queue_unit_ids']
    with pytest.raises(ValidationError, match='queue_unit_ids'):
        ComparisonBundle.model_validate(d)


def test_queues_have_individual_units_and_order():
    b = example_bundle()
    assert b.common_history.keyframes[0].stations['CORTE'].queue_unit_ids == ['OP-1#2']
    assert b.common_history.keyframes[0].units['OP-1#2'].order_id == 'OP-1'


def test_cannot_duplicate_same_unit_in_two_queues():
    d = data()
    d['common_history']['keyframes'][0]['stations']['CORTE']['queue_unit_ids'].append('OP-1#1')
    with pytest.raises(ValidationError, match='repetida'):
        ComparisonBundle.model_validate(d)


def test_seek_identical_until_fork():
    b = example_bundle()
    for h in (0, .9, 1, 1.499):
        a, c = seek(b,'A',H(h)), seek(b,'B',H(h))
        assert a.model_dump(exclude={'branch_id'}) == c.model_dump(exclude={'branch_id'})


def test_seek_event_at_fork_is_applied_to_b_only():
    b=example_bundle()
    a, c = seek(b,'A',H(1.5)), seek(b,'B',H(1.5))
    assert a.seq == 1 and c.seq == 2
    assert a.stations == c.stations  # a acao ainda nao altera a fabrica na fixture


def test_seek_diverges_only_after_action():
    b = example_bundle()
    assert seek(b,'A',H(2.5)).stations['CNC'].status == 'down'
    assert seek(b,'B',H(2.5)).stations['CNC'].status == 'running'
    assert seek(b,'A',H(4)).stations['CNC'].status == 'running'


def test_fork_without_synthetic_event():
    b=example_bundle()
    assert b.fork.time_us == H(1.5)
    assert b.common_history.events[-1].time_us == H(1)


def test_shared_history_sequence_hole_rejected():
    d=data(); d['common_history']['events'][0]['seq']=7
    with pytest.raises(ValidationError, match='sequencia comum'):
        ComparisonBundle.model_validate(d)


def test_branch_sequence_hole_rejected():
    d=data(); d['branch_B']['events'][1]['seq']=19
    with pytest.raises(ValidationError, match='sequencia pos-fork'):
        ComparisonBundle.model_validate(d)


def test_branch_event_before_fork_rejected():
    d=data(); d['branch_B']['events'][0]['time_us']=H(1.1)
    with pytest.raises(ValidationError, match='anterior ao fork'):
        ComparisonBundle.model_validate(d)


def test_branch_keyframe_must_not_copy_common():
    d=data(); d['branch_A']['keyframes'].insert(0, {**d['common_history']['keyframes'][-1], 'branch_id': 'A'})
    with pytest.raises(ValidationError, match='keyframe pos-fork'):
        ComparisonBundle.model_validate(d)


def test_fork_must_match_common_last_seq():
    d=data(); d['fork']['seq']=0
    with pytest.raises(ValidationError, match='fork nao corresponde'):
        ComparisonBundle.model_validate(d)


def test_seed_difference_rejected():
    d=data(); d['branch_B']['seed']+=1
    with pytest.raises(ValidationError, match='modelo/seed'):
        ComparisonBundle.model_validate(d)


def test_unknown_constraints_not_feasible():
    with pytest.raises(ValidationError):
        BranchSummary(feasible='feasible', checks=[ConstraintCheck(name='operator_skill', status='unknown', evidence='nao testada')])


def test_corrupted_common_keyframe_detected():
    d=data(); d['common_history']['keyframes'][-1]['stations']['CORTE']['workers_available']=55
    b=ComparisonBundle.model_validate(d)
    with pytest.raises(ValueError, match='keyframe comum adulterado'):
        validate_reconstruction(b)


def test_corrupted_branch_keyframe_detected():
    d=data(); d['branch_B']['keyframes'][0]['stations']['CORTE']['workers_available']=55
    b=ComparisonBundle.model_validate(d)
    with pytest.raises(ValueError, match='keyframe B adulterado'):
        validate_reconstruction(b)


def test_invalid_upsert_rejected():
    d=data(); d['branch_A']['events'][0]['station_upserts']['CNC']['id']='OUTRO'
    with pytest.raises(ValidationError, match='chave/id'):
        ComparisonBundle.model_validate(d)


def test_export_outputs_aliases_and_parses(tmp_path):
    b=example_bundle();path=tmp_path/'fixture.json'; export_bundle(b,path)
    obj=json.loads(path.read_text(encoding='utf-8'))
    assert 'branch_A' in obj and 'branch_a' not in obj
    assert 'common_history' in obj and 'topology' in obj
    ComparisonBundle.model_validate(obj)


def test_schema_regenerated_matches_file():
    from pathlib import Path
    on_disk=json.loads(Path(__file__).with_name('simulation_contract.schema.json').read_text(encoding='utf-8'))
    assert on_disk == ComparisonBundle.model_json_schema(by_alias=True)


def test_quantization_is_deterministic():
    assert H(1)==3_600_000_000
    assert H(1.5)==5_400_000_000
    with pytest.raises(ValueError): H(float('inf'))
    with pytest.raises(ValueError): H(-1)


def test_snapshot_down_does_not_allow_processing():
    d=data(); s=d['common_history']['keyframes'][-1]['stations']['CNC']
    s['status']='down';s['queue_unit_ids']=[];s['processing_unit_ids']=['OP-1#1'];s['busy_slots']=1
    with pytest.raises(ValidationError):
        ComparisonBundle.model_validate(d)


def test_no_branch_action_before_fork():
    d=data();d['branch_B']['action']['requested_us']=H(1.1)
    with pytest.raises(ValidationError, match='solicitada antes'):
        ComparisonBundle.model_validate(d)
