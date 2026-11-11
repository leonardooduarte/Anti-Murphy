from make_example import example_bundle
from observer_protocol import RecordingObserver
from simulation_contract import hours_to_us, apply_to_branch
import pytest


def test_observer_emits_absolute_patches_and_terminal_keyframe():
    bundle = example_bundle()
    initial = bundle.common_history.keyframes[0]
    recorder = RecordingObserver(initial, keyframe_every=2)
    ev = bundle.common_history.events[0]
    recorder.emit(time_us=ev.time_us, kind=ev.kind, entity_id=ev.entity_id,
                  station_upserts=ev.station_upserts)
    frames, events = recorder.finalize()
    assert [f.seq for f in frames] == [0, 1]
    assert events[0].seq == 1
    assert frames[-1] == bundle.common_history.keyframes[-1]


def test_observer_branch_starts_after_shared_seq():
    b=example_bundle()
    initial=apply_to_branch(b.common_history.keyframes[-1], 'B')
    recorder=RecordingObserver(initial, keyframe_every=1)
    for ev in b.branch_b.events:
        recorder.emit(time_us=ev.time_us, kind=ev.kind, entity_id=ev.entity_id,
                      station_upserts=ev.station_upserts, unit_upserts=ev.unit_upserts)
    frames, events = recorder.finalize()
    assert [f.seq for f in frames] == [1, 2, 3]
    assert [e.seq for e in events] == [2, 3]
    assert recorder.state == b.branch_b.keyframes[-1]
    # frames[0] e' o estado herdado; exportador da branch deve removê-lo.


def test_observer_rejects_decreasing_time():
    b=example_bundle()
    recorder=RecordingObserver(b.common_history.keyframes[0])
    recorder.emit(time_us=hours_to_us(3),kind='outage_start')
    with pytest.raises(ValueError, match='fora de ordem'):
        recorder.emit(time_us=hours_to_us(1),kind='outage_end')


def test_observer_can_verify_engine_state():
    b=example_bundle()
    initial=b.common_history.keyframes[0]
    recorder=RecordingObserver(initial, verify_state=lambda: initial)
    with pytest.raises(ValueError, match='estado real'):
        recorder.emit(time_us=hours_to_us(1),kind='outage_start',
                      station_upserts=b.common_history.events[0].station_upserts)
    assert not recorder.events
