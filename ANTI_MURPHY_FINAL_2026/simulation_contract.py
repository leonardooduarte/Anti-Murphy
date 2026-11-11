"""Anti-Murphy Factory Command — contrato de visualizacao de eventos v1.1.0.

FORMATO: um historico comum + duas ramificacoes apos o ponto de bifurcacao.
UNIDADE: microsegundos de tempo SIMULADO (nao precisao fisica de sensores).
FONTE DA VERDADE: motor Python; frontend interpola APENAS elementos visuais.
NAO implementa nem altera o motor V30.2.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
from hashlib import sha256
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "1.1.0"
MAX_SAFE_JS_INT = 9_007_199_254_740_991


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False,
                              populate_by_name=True)


class Position(StrictModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class StationDefinition(StrictModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    machine_ids: list[str] = Field(min_length=1)
    required_skills: list[str] = Field(default_factory=list)
    buffer_capacity: int | None = Field(default=None, ge=0)
    x: float = Field(ge=0, le=1, description="Posicao visual, nao distancia fisica")
    y: float = Field(ge=0, le=1, description="Posicao visual, nao distancia fisica")

    @model_validator(mode="after")
    def validate_machines(self):
        if len(set(self.machine_ids)) != len(self.machine_ids):
            raise ValueError("maquinas duplicadas na estacao")
        return self


class FlowEdge(StrictModel):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    waypoints: list[Position] = Field(default_factory=list)
    # Representa conectividade logica. Nao implica transporte fisico modelado.


class Topology(StrictModel):
    edges: list[FlowEdge] = Field(default_factory=list)
    transport_semantics: Literal["logical_instantaneous"] = "logical_instantaneous"

    @model_validator(mode="after")
    def unique_edges(self):
        pairs = [(e.source, e.target) for e in self.edges]
        if len(pairs) != len(set(pairs)) or any(a == b for a, b in pairs):
            raise ValueError("arestas duplicadas ou autorreferentes")
        return self


class OrderDefinition(StrictModel):
    id: str = Field(min_length=1)
    quantity: int = Field(ge=1)
    due_us: int = Field(ge=0, le=MAX_SAFE_JS_INT)
    route_station_ids: list[str] = Field(min_length=1)


class FactoryDefinition(StrictModel):
    stations: dict[str, StationDefinition]
    orders: dict[str, OrderDefinition]

    @model_validator(mode="after")
    def consistency(self):
        if not self.stations or not self.orders:
            raise ValueError("fabrica exige estacoes e pedidos")
        machines = []
        for sid, station in self.stations.items():
            if sid != station.id:
                raise ValueError("chave/id de estacao inconsistente")
            machines.extend(station.machine_ids)
        if len(set(machines)) != len(machines):
            raise ValueError("maquina atribuida a mais de uma estacao")
        for oid, order in self.orders.items():
            if oid != order.id or not set(order.route_station_ids) <= set(self.stations):
                raise ValueError("pedido ou roteiro invalido")
        return self


class StationState(StrictModel):
    id: str = Field(min_length=1)
    status: Literal["idle", "running", "down", "blocked", "setup"]
    machine_capacity: int = Field(ge=0)
    workers_available: int = Field(ge=0)
    busy_slots: int = Field(ge=0)
    # Buffer: IDs ORDENADOS de unidades/pecas, da proxima a ser despachada para a ultima.
    # Obrigatorio em TODO keyframe, inclusive quando vazio. Nao e apenas um contador.
    queue_unit_ids: list[str]
    processing_unit_ids: list[str] = Field(default_factory=list)
    paused_unit_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_occupancy(self):
        if self.busy_slots > self.machine_capacity:
            raise ValueError(f"{self.id}: ocupacao excede capacidade")
        if len(self.processing_unit_ids) + len(self.paused_unit_ids) > self.busy_slots:
            raise ValueError(f"{self.id}: unidades em processamento excedem slots ocupados")
        ids = self.queue_unit_ids + self.processing_unit_ids + self.paused_unit_ids
        if len(ids) != len(set(ids)):
            raise ValueError(f"{self.id}: unidade duplicada")
        if self.status == "down" and self.processing_unit_ids:
            raise ValueError(f"{self.id}: processamento durante parada")
        return self


class UnitState(StrictModel):
    id: str = Field(min_length=1)
    order_id: str = Field(min_length=1)
    route_step: int = Field(ge=0)
    station_id: str | None = None
    machine_id: str | None = None
    phase: Literal["unreleased", "queued", "processing", "paused", "completed", "blocked"]


class OrderState(StrictModel):
    id: str = Field(min_length=1)
    completed_units: int = Field(ge=0)
    completion_us: int | None = Field(default=None, ge=0, le=MAX_SAFE_JS_INT)


class SimulationSnapshot(StrictModel):
    """Estado completo APOS o evento seq; seq=0 corresponde ao inicio da rodada."""
    branch_id: Literal["common", "A", "B"]
    seq: int = Field(ge=0)
    time_us: int = Field(ge=0, le=MAX_SAFE_JS_INT)
    stations: dict[str, StationState]
    units: dict[str, UnitState]
    orders: dict[str, OrderState]

    @model_validator(mode="after")
    def local_consistency(self):
        for collection in (self.stations, self.units, self.orders):
            if any(key != value.id for key, value in collection.items()):
                raise ValueError("snapshot com chave/id divergente")
        refs: dict[str, tuple[str, str]] = {}
        for sid, station in self.stations.items():
            for phase, ids in (("queued", station.queue_unit_ids),
                               ("processing", station.processing_unit_ids),
                               ("paused", station.paused_unit_ids)):
                for uid in ids:
                    if uid in refs or uid not in self.units:
                        raise ValueError("unidade repetida ou nao cadastrada em fila")
                    refs[uid] = (sid, phase)
        for uid, unit in self.units.items():
            if unit.phase in {"queued", "processing", "paused"}:
                if refs.get(uid) != (unit.station_id, unit.phase):
                    raise ValueError(f"{uid}: fila e fase divergentes")
            elif uid in refs:
                raise ValueError(f"{uid}: referencia indevida de unidade")
        return self


class EventDelta(StrictModel):
    """Upserts absolutos (idempotentes), ordenados por seq no dominio de cada ramo."""
    seq: int = Field(ge=1)
    time_us: int = Field(ge=0, le=MAX_SAFE_JS_INT)
    kind: Literal[
        "queue_enter", "queue_leave", "operation_start", "operation_pause",
        "operation_resume", "operation_finish", "outage_start", "outage_end",
        "resource_changed", "setup_start", "setup_finish", "order_completed",
        "action_applied", "model_blocked"
    ]
    entity_id: str | None = None
    station_upserts: dict[str, StationState] = Field(default_factory=dict)
    unit_upserts: dict[str, UnitState] = Field(default_factory=dict)
    order_upserts: dict[str, OrderState] = Field(default_factory=dict)

    @model_validator(mode="after")
    def keys_match(self):
        for records in (self.station_upserts, self.unit_upserts, self.order_upserts):
            if any(key != value.id for key, value in records.items()):
                raise ValueError("upsert com chave/id inconsistente")
        return self


class ConstraintCheck(StrictModel):
    name: Literal["operator_skill", "buffer_capacity", "sequence_setup",
                  "machine_capacity", "worker_capacity", "budget", "other"]
    status: Literal["pass", "fail", "unknown"]
    subject_id: str | None = None
    evidence: str = Field(min_length=1)


class BranchSummary(StrictModel):
    feasible: Literal["feasible", "infeasible", "unverified"]
    checks: list[ConstraintCheck] = Field(default_factory=list)
    total_cost_cents: int | None = Field(default=None, ge=0)
    sla_pct: float | None = Field(default=None, ge=0, le=100)
    makespan_us: int | None = Field(default=None, ge=0, le=MAX_SAFE_JS_INT)
    late_orders: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def feasibility(self):
        values = [check.status for check in self.checks]
        required = "infeasible" if "fail" in values else (
            "unverified" if not values or "unknown" in values else "feasible"
        )
        if self.feasible != required:
            raise ValueError("viabilidade difere das restricoes avaliadas")
        return self


class ActionInfo(StrictModel):
    action_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    requested_us: int = Field(ge=0, le=MAX_SAFE_JS_INT)
    effective_us: int | None = Field(default=None, ge=0, le=MAX_SAFE_JS_INT)

    @model_validator(mode="after")
    def timing(self):
        if self.effective_us is not None and self.effective_us < self.requested_us:
            raise ValueError("acao efetiva antes da solicitacao")
        return self


class IncidentDefinition(StrictModel):
    incident_id: str = Field(min_length=1)
    station_id: str = Field(min_length=1)
    start_us: int = Field(ge=0, le=MAX_SAFE_JS_INT)
    planned_end_us: int = Field(ge=0, le=MAX_SAFE_JS_INT)

    @model_validator(mode="after")
    def window(self):
        if self.planned_end_us <= self.start_us:
            raise ValueError("incidente exige duracao positiva")
        return self


class ForkPoint(StrictModel):
    """Ultimo seq comum, horario de separacao logica; nao precisa existir evento nesse horario."""
    seq: int = Field(ge=0)
    time_us: int = Field(ge=0, le=MAX_SAFE_JS_INT)
    reason: Literal["decision_boundary", "intervention_requested"] = "decision_boundary"


class CommonHistory(StrictModel):
    provenance: Literal["engine_native", "trace_derived", "synthetic_fixture"]
    keyframes: list[SimulationSnapshot] = Field(min_length=1)
    events: list[EventDelta] = Field(default_factory=list)

    @model_validator(mode="after")
    def integrity(self):
        if [e.seq for e in self.events] != list(range(1, len(self.events) + 1)):
            raise ValueError("sequencia comum invalida")
        times = [e.time_us for e in self.events]
        if times != sorted(times):
            raise ValueError("tempo comum nao monotono")
        expected = {0: 0, **{e.seq: e.time_us for e in self.events}}
        keys = [kf.seq for kf in self.keyframes]
        if keys != sorted(set(keys)) or keys[0] != 0 or keys[-1] != len(self.events):
            raise ValueError("keyframes comuns devem conter inicio e fim")
        if any(kf.branch_id != "common" or expected.get(kf.seq) != kf.time_us for kf in self.keyframes):
            raise ValueError("keyframe comum com seq/tempo/ramo invalido")
        return self


class BranchTimeline(StrictModel):
    branch_id: Literal["A", "B"]
    run_id: str = Field(min_length=1)
    scenario_label: str = Field(min_length=1)
    provenance: Literal["engine_native", "trace_derived", "synthetic_fixture"]
    model_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    seed: int = Field(ge=0)
    action: ActionInfo | None = None
    # Contem APENAS eventos e keyframes APOS o fork. Sem copia do estado no fork.
    keyframes: list[SimulationSnapshot] = Field(default_factory=list)
    events: list[EventDelta] = Field(default_factory=list)
    summary: BranchSummary


class ComparisonBundle(StrictModel):
    schema_version: Literal["1.1.0"] = SCHEMA_VERSION
    experiment_id: str = Field(min_length=1)
    time_unit: Literal["simulated_microsecond"] = "simulated_microsecond"
    time_origin: Literal["simulation_start"] = "simulation_start"
    definition: FactoryDefinition
    topology: Topology
    incident: IncidentDefinition
    fork: ForkPoint
    common_history: CommonHistory
    branch_a: BranchTimeline = Field(alias="branch_A")
    branch_b: BranchTimeline = Field(alias="branch_B")

    @model_validator(mode="after")
    def validate_graph_and_timelines(self):
        valid_stations = set(self.definition.stations)
        if self.incident.station_id not in valid_stations:
            raise ValueError("incidente referencia estacao inexistente")
        links = {(edge.source, edge.target) for edge in self.topology.edges}
        if any(edge.source not in valid_stations or edge.target not in valid_stations for edge in self.topology.edges):
            raise ValueError("topologia referencia estacao inexistente")
        for order in self.definition.orders.values():
            if any(pair not in links for pair in zip(order.route_station_ids, order.route_station_ids[1:])):
                raise ValueError("rota nao conectada na topologia")
        common = self.common_history
        if self.fork.seq != len(common.events) or self.fork.time_us < common.keyframes[-1].time_us:
            raise ValueError("fork nao corresponde ao historico comum")
        a, b = self.branch_a, self.branch_b
        if a.branch_id != "A" or b.branch_id != "B" or a.run_id == b.run_id:
            raise ValueError("ramos A/B invalidos")
        if a.action is not None or b.action is None:
            raise ValueError("A e' referencia sem acao; B exige acao")
        if a.seed != b.seed or a.model_sha256 != b.model_sha256:
            raise ValueError("ramos nao compartilham modelo/seed")
        if b.action.requested_us < self.fork.time_us:
            raise ValueError("acao solicitada antes do fork")
        for branch in (a, b):
            expected_seq = list(range(self.fork.seq + 1, self.fork.seq + len(branch.events) + 1))
            if [e.seq for e in branch.events] != expected_seq:
                raise ValueError("ramo com sequencia pos-fork invalida")
            times = [e.time_us for e in branch.events]
            if times != sorted(times) or (times and times[0] < self.fork.time_us):
                raise ValueError("ramo com tempo anterior ao fork")
            keys = [kf.seq for kf in branch.keyframes]
            if keys != sorted(set(keys)) or (not branch.events and keys) or (branch.events and (not keys or keys[-1] != branch.events[-1].seq)):
                raise ValueError("ramo exige ultimo keyframe pos-fork")
            expected_times = {event.seq: event.time_us for event in branch.events}
            if any(kf.branch_id != branch.branch_id or expected_times.get(kf.seq) != kf.time_us for kf in branch.keyframes):
                raise ValueError("keyframe pos-fork com sequencia/tempo divergente")
        for snapshot in [*common.keyframes, *a.keyframes, *b.keyframes]:
            self._validate_snapshot_against_factory(snapshot)
        return self

    def _validate_snapshot_against_factory(self, snapshot: SimulationSnapshot) -> None:
        if set(snapshot.stations) != set(self.definition.stations) or set(snapshot.orders) != set(self.definition.orders):
            raise ValueError("keyframe com postos/pedidos divergentes")
        units_by_order: dict[str, int] = {}
        for unit in snapshot.units.values():
            if unit.order_id not in self.definition.orders:
                raise ValueError("unidade sem pedido no modelo")
            units_by_order[unit.order_id] = units_by_order.get(unit.order_id, 0) + 1
            if unit.station_id is not None and unit.station_id not in snapshot.stations:
                raise ValueError("unidade associada a posto inexistente")
            if unit.machine_id is not None:
                if unit.station_id is None or unit.machine_id not in self.definition.stations[unit.station_id].machine_ids:
                    raise ValueError("unidade associada a maquina incorreta")
            route = self.definition.orders[unit.order_id].route_station_ids
            if unit.phase in {"queued", "processing", "paused"} and (
                unit.route_step >= len(route) or route[unit.route_step] != unit.station_id
            ):
                raise ValueError("unidade fora da etapa do roteiro")
        for sid, state in snapshot.stations.items():
            station = self.definition.stations[sid]
            if state.machine_capacity > len(station.machine_ids):
                raise ValueError("capacidade acima das maquinas cadastradas")
            if station.buffer_capacity is not None and len(state.queue_unit_ids) > station.buffer_capacity:
                raise ValueError("buffer excede capacidade configurada")
        for oid, state in snapshot.orders.items():
            if state.completed_units > self.definition.orders[oid].quantity:
                raise ValueError("mais unidades concluidas que planejadas")
            if units_by_order.get(oid, 0) > self.definition.orders[oid].quantity:
                raise ValueError("mais entidades unitarias que demanda")


def apply_delta(snapshot: SimulationSnapshot, event: EventDelta) -> SimulationSnapshot:
    if event.seq != snapshot.seq + 1 or event.time_us < snapshot.time_us:
        raise ValueError("delta fora de ordem")
    return SimulationSnapshot(
        branch_id=snapshot.branch_id, seq=event.seq, time_us=event.time_us,
        stations={**snapshot.stations, **event.station_upserts},
        units={**snapshot.units, **event.unit_upserts},
        orders={**snapshot.orders, **event.order_upserts},
    )


def apply_to_branch(snapshot: SimulationSnapshot, branch_id: Literal["A", "B"]) -> SimulationSnapshot:
    """Reutiliza o estado final comum sem duplicar seu JSON em ambos os ramos."""
    return SimulationSnapshot(**{**snapshot.model_dump(), "branch_id": branch_id})


def validate_reconstruction(bundle: ComparisonBundle) -> None:
    """Confere toda a cadeia e todos os keyframes, tambem entre eventos."""
    current = bundle.common_history.keyframes[0]
    common_kf = {kf.seq: kf for kf in bundle.common_history.keyframes}
    bundle._validate_snapshot_against_factory(current)
    for delta in bundle.common_history.events:
        current = apply_delta(current, delta)
        bundle._validate_snapshot_against_factory(current)
        if delta.seq in common_kf and current != common_kf[delta.seq]:
            raise ValueError(f"keyframe comum adulterado em seq={delta.seq}")
    if current != bundle.common_history.keyframes[-1]:
        raise ValueError("ultimo keyframe comum invalido")
    for branch in (bundle.branch_a, bundle.branch_b):
        branch_current = apply_to_branch(current, branch.branch_id)
        branch_kf = {kf.seq: kf for kf in branch.keyframes}
        for delta in branch.events:
            branch_current = apply_delta(branch_current, delta)
            bundle._validate_snapshot_against_factory(branch_current)
            if delta.seq in branch_kf and branch_current != branch_kf[delta.seq]:
                raise ValueError(f"keyframe {branch.branch_id} adulterado em seq={delta.seq}")
        if branch.keyframes and branch_current != branch.keyframes[-1]:
            raise ValueError(f"ultimo keyframe {branch.branch_id} invalido")


def seek(bundle: ComparisonBundle, branch_id: Literal["A", "B"], time_us: int) -> SimulationSnapshot:
    """Consulta deterministica (tempo, seq); nao simula nem interpola estado industrial."""
    if not 0 <= time_us <= MAX_SAFE_JS_INT:
        raise ValueError("instante invalido")
    common = bundle.common_history
    base_kf = common.keyframes[0]
    if time_us < bundle.fork.time_us:
        for frame in common.keyframes:
            if frame.time_us <= time_us:
                base_kf = frame
            else:
                break
        state = base_kf
        for ev in common.events:
            if ev.seq > state.seq and ev.time_us <= time_us:
                state = apply_delta(state, ev)
        return apply_to_branch(state, branch_id)
    branch = bundle.branch_a if branch_id == "A" else bundle.branch_b
    for frame in branch.keyframes:
        if frame.time_us <= time_us:
            base_kf = frame
        else:
            break
    if base_kf.branch_id == "common":
        base_kf = apply_to_branch(common.keyframes[-1], branch_id)
    state = base_kf
    for ev in branch.events:
        if ev.seq > state.seq and ev.time_us <= time_us:
            state = apply_delta(state, ev)
    return state


def export_bundle(bundle: ComparisonBundle, path: str | Path) -> None:
    validate_reconstruction(bundle)
    Path(path).write_text(bundle.model_dump_json(indent=2, by_alias=True), encoding="utf-8")


def canonical_model_sha256(operational_inputs: dict) -> str:
    """Hash dos inputs completos, excluindo geometria visual e acao pos-fork."""
    if not isinstance(operational_inputs, dict) or not operational_inputs:
        raise ValueError("inputs operacionais obrigatorios")
    data = json.dumps(operational_inputs, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256(data).hexdigest()


def hours_to_us(hours: float) -> int:
    t = Decimal(str(hours)) * Decimal(3_600_000_000)
    if not t.is_finite() or t < 0:
        raise ValueError("tempo invalido")
    us = int(t.to_integral_value(rounding=ROUND_HALF_EVEN))
    if us > MAX_SAFE_JS_INT:
        raise ValueError("tempo excede inteiro seguro JS")
    return us
