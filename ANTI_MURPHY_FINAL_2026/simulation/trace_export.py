"""Trace adapter for Factory Command schema v1.1.0.

Read-only observer. All economic calculations remain in simulation.engine.
The trace is a replay of engine *domain transitions*, not a telemetry/digital twin feed.
"""
from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal, ROUND_HALF_EVEN
from hashlib import sha256
import json
from collections import defaultdict
from pathlib import Path

from simulation.factory import ScenarioConfig, TimedAction
from simulation.engine import run_simulation
from simulation_contract import (
    ActionInfo, BranchSummary, BranchTimeline, CommonHistory, ComparisonBundle,
    ConstraintCheck, FactoryDefinition, FlowEdge, ForkPoint, IncidentDefinition,
    OrderDefinition, OrderState, SimulationSnapshot, StationDefinition, StationState,
    Topology, UnitState, apply_delta, apply_to_branch, export_bundle,
    hours_to_us, validate_reconstruction,
)
from observer_protocol import RecordingObserver


def stable_model_digest(cfg: ScenarioConfig) -> str:
    payload = json.dumps(asdict(cfg), ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                         allow_nan=False)
    return sha256(payload.encode('utf-8')).hexdigest()


def factory_definition(cfg: ScenarioConfig, action: TimedAction):
    keys = list(cfg.stations)
    definitions = {}
    for i, (sid, st) in enumerate(cfg.stations.items()):
        cap = int(st['maquinas']) + max(0, (action.machines_delta or {}).get(sid, 0))
        definitions[sid] = StationDefinition(
            id=sid, name=st.get('nome', sid),
            machine_ids=[f'{sid}:slot:{n}' for n in range(cap)],
            # Empty skills list says nothing about industrial qualification.
            required_skills=list(st.get('required_skills', [])),
            buffer_capacity=st.get('buffer_capacity'),
            x=0.12 + 0.76*i/max(1, len(keys)-1),
            y=0.42 + 0.13*(i % 2),
        )
    orders = {
        o['id']: OrderDefinition(
            id=o['id'], quantity=max(1, int(round(int(o['quantidade'])*cfg.demand_multiplier))),
            due_us=hours_to_us(o['prazo_h']),
            route_station_ids=[sid for sid, _ in o['route']],
        ) for o in cfg.orders
    }
    edges = sorted({(a, b) for o in cfg.orders for a,b in zip(
        [s for s,_ in o['route']], [s for s,_ in o['route']][1:])})
    return FactoryDefinition(stations=definitions, orders=orders), Topology(
        edges=[FlowEdge(source=a, target=b) for a,b in edges]
    )


class EngineTraceObserver:
    """Captures exact engine domain transitions; uses the v1.1 RecordingObserver."""

    def __init__(self, *, keyframe_every: int = 60):
        self.recorder: RecordingObserver | None = None
        self.keyframe_every = keyframe_every
        self._completed_us: dict[str,int] = {}
        self._model: ScenarioConfig | None = None
        self._last_actual: SimulationSnapshot | None = None
        self.transition_count = 0

    def on_initial(self, *, config, action, stations, orders):
        self._model = config
        units = {
            f'{order["id"]}#{n+1}': UnitState(
                id=f'{order["id"]}#{n+1}', order_id=order['id'], route_step=0,
                station_id=None, machine_id=None, phase='unreleased',
            ) for order in orders for n in range(order['quantidade_sim'])
        }
        states = {sid: StationState(
            id=sid, status='idle', machine_capacity=int(st['maquinas']),
            workers_available=int(st['available_workers']), busy_slots=0, queue_unit_ids=[],
        ) for sid, st in stations.items()}
        initial = SimulationSnapshot(
            branch_id='common', seq=0, time_us=0, stations=states, units=units,
            orders={o['id']: OrderState(id=o['id'], completed_units=0) for o in orders},
        )
        self._last_actual = initial
        self.recorder = RecordingObserver(initial, self.keyframe_every,
                                          verify_state=lambda: self._last_actual)

    def on_transition(self, *, kind, now_h, entity_id, stations, orders,
                      queue, active, running, units, order_completed, outage_active):
        if self.recorder is None:
            raise RuntimeError('observer not initialized')
        time_us = hours_to_us(now_h)
        if time_us < self.recorder.state.time_us:
            raise ValueError('engine emitted a non-monotonic transition')
        completed_units = {o['id']: int(order_completed[o['id']]) for o in orders}
        for o in orders:
            oid=o['id']
            if completed_units[oid] == o['quantidade_sim'] and oid not in self._completed_us:
                self._completed_us[oid] = time_us
        st_states = {}
        for sid, st in stations.items():
            ordered_queue = sorted(queue[sid])
            queue_ids = [f'{oid}#{n+1}' for _p,_seq,_arrival,oid,n,_step in ordered_queue]
            processing_ids = sorted(uid for uid, v in units.items()
                                    if v['station_id'] == sid and v['phase'] == 'processing')
            paused_ids = sorted(uid for uid, v in units.items()
                                if v['station_id'] == sid and v['phase'] == 'paused')
            # Only the affected station is actually down; outage_active is global.
            down = bool(outage_active and sid == self._model.chaos_station)
            status = ('down' if down else 'running' if processing_ids else
                      'blocked' if not st.get('automatizada',False) and
                      int(st['available_workers']) <= 0 else 'idle')
            st_states[sid] = StationState(
                id=sid, status=status, machine_capacity=int(st['maquinas']),
                workers_available=int(st['available_workers']), busy_slots=int(active[sid]),
                queue_unit_ids=queue_ids, processing_unit_ids=processing_ids,
                paused_unit_ids=paused_ids,
            )
        unit_states = {uid: UnitState(id=uid, **entry) for uid,entry in units.items()}
        order_states = {oid: OrderState(
            id=oid, completed_units=count, completion_us=self._completed_us.get(oid),
        ) for oid,count in completed_units.items()}
        current = self.recorder.state
        actual = SimulationSnapshot(
            branch_id='common', seq=current.seq+1, time_us=time_us,
            stations=st_states, units=unit_states, orders=order_states,
        )
        self._last_actual = actual
        self.recorder.emit(
            time_us=time_us, kind=kind, entity_id=entity_id,
            station_upserts={k:v for k,v in st_states.items() if current.stations[k]!=v},
            unit_upserts={k:v for k,v in unit_states.items() if current.units[k]!=v},
            order_upserts={k:v for k,v in order_states.items() if current.orders[k]!=v},
        )
        self.transition_count += 1


def _keyframes_from_events(initial, events, *, branch_id, stride=60):
    state = apply_to_branch(initial, branch_id) if initial.branch_id != branch_id else initial
    frames = [state] if branch_id=='common' else []
    for i,e in enumerate(events,1):
        state = apply_delta(state, e)
        if i % stride == 0 or i == len(events):
            frames.append(state)
    return frames


def _checks(cfg: ScenarioConfig, action: TimedAction | None):
    # Explicitly acknowledge not-enforced industrial constraints.
    return [
        ConstraintCheck(name='operator_skill', status='unknown' if action and
                        action.workers_delta else 'pass',
                        evidence='Transferencias nao validadas por matricula individual de skills.'
                        if action and action.workers_delta else 'Sem realocacao de trabalhadores.'),
        ConstraintCheck(name='buffer_capacity', status='unknown',
                        evidence='Motor V30.2 nao aplica bloqueio por lotacao do buffer.'),
        ConstraintCheck(name='sequence_setup', status='unknown',
                        evidence='Setup fixo nao equivale a setup dependente de sequencia.'),
        ConstraintCheck(name='machine_capacity', status='pass',
                        evidence='Motor impede inicio acima da capacidade disponivel.'),
        ConstraintCheck(name='worker_capacity', status='pass',
                        evidence='Motor limita paralelismo por trabalhadores disponiveis.'),
    ]


def _summary(result, cfg, action):
    checks=_checks(cfg,action)
    feasible=('infeasible' if not result['feasible'] else
              'unverified' if any(c.status=='unknown' for c in checks) else 'feasible')
    return BranchSummary(
        feasible=feasible, checks=checks,
        total_cost_cents=int((Decimal(str(result['total_cost']))*100).quantize(Decimal('1'),rounding=ROUND_HALF_EVEN)),
        sla_pct=result['sla_pct'], makespan_us=hours_to_us(
            max((op['end_h'] for op in result['operations']), default=0)),
        late_orders=result['late_orders'],
    )


def generate_comparison(cfg: ScenarioConfig, action: TimedAction,
                        *, keyframe_every: int = 60, experiment_id='FC-RUN-001'):
    if not cfg.chaos_station or cfg.chaos_duration_h <= 0:
        raise ValueError('An incident is required')
    if action.at_h < cfg.chaos_start_h:
        raise ValueError('Decision must follow incident onset')
    reference = EngineTraceObserver(keyframe_every=keyframe_every)
    response = EngineTraceObserver(keyframe_every=keyframe_every)
    result_a = run_simulation(cfg, observer=reference)
    result_b = run_simulation(cfg, action=action, observer=response)
    if not result_a['feasible'] or not result_b['feasible']:
        raise ValueError('Comparison requires two executable engine runs')
    a = reference.recorder
    b = response.recorder
    fork_us=hours_to_us(action.at_h)
    common_a=[e for e in a.events if e.time_us < fork_us]
    common_b=[e for e in b.events if e.time_us < fork_us]
    if common_a != common_b or a.keyframes[0] != b.keyframes[0]:
        raise ValueError('Scenario histories differ BEFORE intervention; comparison invalid')
    common_frames=_keyframes_from_events(a.keyframes[0],common_a,branch_id='common',stride=keyframe_every)
    last_common=common_frames[-1]
    prefix_seq=len(common_a)
    branch_a=[e for e in a.events if e.seq>prefix_seq]
    branch_b=[e for e in b.events if e.seq>prefix_seq]
    if any(e.time_us<fork_us for e in branch_a+branch_b):
        raise ValueError('Branch event occurred before fork')
    def branch_frames(events, name):
        if not events:return []
        return _keyframes_from_events(last_common,events,branch_id=name,stride=keyframe_every)
    definition,topology=factory_definition(cfg,action)
    action_info=ActionInfo(
        action_id='scheduled_response', label=action.label,
        requested_us=fork_us,
        effective_us=hours_to_us(result_b['intervention']['effective_h'])
        if result_b['intervention']['effective_h'] is not None else None,
    )
    digest=stable_model_digest(cfg)
    bundle=ComparisonBundle(
        experiment_id=experiment_id,
        definition=definition, topology=topology,
        incident=IncidentDefinition(
            incident_id=f'incident-{cfg.chaos_station}',station_id=cfg.chaos_station,
            start_us=hours_to_us(cfg.chaos_start_h),
            planned_end_us=hours_to_us(cfg.chaos_start_h+cfg.chaos_duration_h)),
        fork=ForkPoint(seq=prefix_seq,time_us=fork_us,reason='intervention_requested'),
        common_history=CommonHistory(
            provenance='engine_native',keyframes=common_frames,events=common_a),
        branch_A=BranchTimeline(
            branch_id='A',run_id=f'{experiment_id}-A',scenario_label='Sem intervencao',
            provenance='engine_native',model_sha256=digest,seed=cfg.seed,
            events=branch_a,keyframes=branch_frames(branch_a,'A'),summary=_summary(result_a,cfg,None)),
        branch_B=BranchTimeline(
            branch_id='B',run_id=f'{experiment_id}-B',scenario_label=action.label,
            provenance='engine_native',model_sha256=digest,seed=cfg.seed,action=action_info,
            events=branch_b,keyframes=branch_frames(branch_b,'B'),summary=_summary(result_b,cfg,action)),
    )
    validate_reconstruction(bundle)
    return bundle, result_a, result_b


def export_comparison_json(cfg: ScenarioConfig, action: TimedAction, path: str | Path,
                          *, keyframe_every=60, experiment_id='FC-RUN-001'):
    bundle,a,b=generate_comparison(cfg,action,keyframe_every=keyframe_every,experiment_id=experiment_id)
    export_bundle(bundle, Path(path))
    return bundle,a,b
