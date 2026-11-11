import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from simulation_contract import ComparisonBundle, validate_reconstruction, seek
import pytest

@pytest.fixture(scope='module')
def bundle():
    b=ComparisonBundle.model_validate_json((ROOT/'simulation_snapshot.json').read_text(encoding='utf8'))
    validate_reconstruction(b)
    return b

def test_real_bundle_valid(bundle):
    assert bundle.schema_version=='1.1.0'
    assert bundle.branch_a.summary.total_cost_cents == 159861
    assert bundle.branch_b.summary.total_cost_cents == 137760
    assert bundle.branch_a.summary.feasible=='unverified'
    assert bundle.branch_b.summary.feasible=='unverified'

def test_two_futures_share_prefix(bundle):
    for time in [0, 100_000_000, bundle.incident.start_us, bundle.fork.time_us-1]:
        a=seek(bundle,'A',time);b=seek(bundle,'B',time)
        assert a.stations==b.stations and a.units==b.units and a.orders==b.orders

def test_exact_event_timing(bundle):
    for branch, timeline in [('A',bundle.branch_a),('B',bundle.branch_b)]:
        for ev in timeline.events:
            at=seek(bundle,branch,ev.time_us)
            assert at.seq>=ev.seq

def test_branches_differ_after_intervention(bundle):
    t=6_840_000_000  # 1.9 simulated hours
    a=seek(bundle,'A',t);b=seek(bundle,'B',t)
    assert a.stations['CNC'].status=='down'
    assert b.stations['CNC'].status=='running'

def test_real_frontend_is_no_longer_mock():
    json_file=ROOT/'frontend/src/data/simulation_snapshot.json'
    b=ComparisonBundle.model_validate_json(json_file.read_text(encoding='utf8'))
    assert b.experiment_id=='FC-V302-THREE-STATIONS'

def test_ts_client_replays_real_json(bundle):
    script=ROOT/'tests/verify_replay.cjs'
    folder=ROOT/'js_test'
    if not (folder/'engine/ReplayEngine.js').exists():
        pytest.skip('tsc compilation output unavailable')
    output=subprocess.check_output(['node',str(script),str(ROOT/'simulation_snapshot.json'),str(folder)],text=True)
    observed=json.loads(output)
    for row in observed:
        actual=seek(bundle,row['branch'],row['time_us'])
        assert actual.seq==row['seq']
        assert {sid:v.status for sid,v in actual.stations.items()}==row['statuses']
        assert {sid:v.queue_unit_ids for sid,v in actual.stations.items()}==row['queues']
