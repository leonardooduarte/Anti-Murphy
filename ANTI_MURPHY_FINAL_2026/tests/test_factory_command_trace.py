"""Sprint 3: bridge between V30.2's real simulation and schema v1.1.0."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from simulation.factory import TimedAction
from simulation.engine import run_simulation
from simulation.trace_export import (
    EngineTraceObserver, factory_definition, export_comparison_json,
    generate_comparison,
)
from simulation_contract import ComparisonBundle, hours_to_us, seek, validate_reconstruction
from tools.export_factory_command import demo_scenario


def normalized(r):
    d=dict(r)
    d.pop('config',None)
    return d


def test_instrumentation_preserves_all_engine_metrics_and_outputs():
    cfg,action=demo_scenario()
    for candidate in (None,action):
        original=run_simulation(cfg, candidate)
        obs=EngineTraceObserver(keyframe_every=5)
        instrumented=run_simulation(cfg,candidate,observer=obs)
        assert normalized(original)==normalized(instrumented)
        assert len(obs.recorder.events)>0
        assert all(e.time_us>=0 for e in obs.recorder.events)
        assert obs.recorder.events == sorted(obs.recorder.events, key=lambda e:(e.time_us,e.seq))


def test_comparison_roundtrips_replay_and_fork():
    cfg,act=demo_scenario()
    bundle, a, b = generate_comparison(cfg,act,keyframe_every=3)
    validate_reconstruction(bundle)
    again=ComparisonBundle.model_validate_json(bundle.model_dump_json(by_alias=True))
    assert again==bundle
    assert bundle.common_history.provenance=='engine_native'
    assert bundle.branch_a.provenance==bundle.branch_b.provenance=='engine_native'
    assert bundle.fork.time_us==hours_to_us(act.at_h)
    assert bundle.branch_b.action.requested_us==hours_to_us(act.at_h)
    assert bundle.branch_b.action.effective_us==hours_to_us(b['intervention']['effective_h'])
    assert a['total_cost']!=b['total_cost']
    for t in [0,.1,.5,.999]:
        x=seek(bundle,'A',hours_to_us(t))
        y=seek(bundle,'B',hours_to_us(t))
        assert x.model_dump(exclude={'branch_id'})==y.model_dump(exclude={'branch_id'})
    assert seek(bundle,'A',hours_to_us(.5)).stations['CNC'].status=='down'
    assert seek(bundle,'A',hours_to_us(.5)).stations['CNC'].paused_unit_ids
    assert seek(bundle,'A',hours_to_us(2.0)).stations['CNC'].status=='down'
    assert seek(bundle,'B',hours_to_us(2.0)).stations['CNC'].status=='running'
    assert all(s.phase=='completed' for s in seek(bundle,'B',hours_to_us(12)).units.values())
    assert bundle.branch_b.summary.feasible=='unverified'
    assert bundle.branch_b.summary.total_cost_cents == 137760


def test_export_json_is_engine_derived(tmp_path):
    cfg,action=demo_scenario()
    path=tmp_path/'simulation_snapshot.json'
    expected,a,b=export_comparison_json(cfg,action,path,keyframe_every=2)
    d=json.loads(path.read_text(encoding='utf-8'))
    assert d['schema_version']=='1.1.0'
    assert d['common_history']['provenance']=='engine_native'
    assert d['branch_A']['summary']['total_cost_cents']==159861
    assert d['branch_B']['summary']['total_cost_cents']==137760
    assert ComparisonBundle.model_validate(d)==expected


def test_sequential_events_with_same_timestamp():
    cfg,action=demo_scenario()
    cfg.chaos_start_h=0.2
    cfg.chaos_duration_h=1.5
    action=TimedAction(at_h=.7,label='Repair',repair_remaining_factor=.5)
    bundle,a,b=generate_comparison(cfg,action,keyframe_every=8)
    validate_reconstruction(bundle)
    events=bundle.common_history.events + bundle.branch_b.events
    duplicates=[(a,b) for a,b in zip(events,events[1:]) if a.time_us==b.time_us]
    assert duplicates
    assert all(b.seq==a.seq+1 for a,b in duplicates)


def test_four_parallel_slots_and_machine_reinforcement():
    cfg,act=demo_scenario()
    cfg.stations['CNC']['maquinas']=2
    cfg.stations['CNC']['operadores']=2
    cfg.orders[0]['quantidade']=8
    act=TimedAction(at_h=1.,label='add machine and worker', machines_delta={'CNC':1},workers_delta={'CNC':1})
    bundle,_,_=generate_comparison(cfg,act,keyframe_every=10)
    assert len(bundle.definition.stations['CNC'].machine_ids)==3
    assert max(s.stations['CNC'].machine_capacity for s in bundle.branch_b.keyframes)==3
    assert bundle.branch_b.summary.feasible=='unverified'
    validate_reconstruction(bundle)


def test_no_false_skill_or_buffer_verification():
    cfg,act=demo_scenario()
    bundle,_,_=generate_comparison(cfg,act)
    checks={x.name:x.status for x in bundle.branch_b.summary.checks}
    assert checks['operator_skill']=='pass'  # no worker transfer was requested
    assert checks['buffer_capacity']=='unknown'
    assert checks['sequence_setup']=='unknown'


def test_invalid_comparisons_rejected():
    cfg,act=demo_scenario()
    cfg.chaos_duration_h=0
    with pytest.raises(ValueError,match='incident'):
        generate_comparison(cfg,act)
    cfg,act=demo_scenario()
    act=TimedAction(at_h=.1,repair_remaining_factor=.5)
    with pytest.raises(ValueError,match='follow incident'):
        generate_comparison(cfg,act)
