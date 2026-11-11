"""Exemplo inteiramente SINTETICO. Nao e saida instrumentada da V30.2."""
from pathlib import Path
import json

from simulation_contract import (
    ActionInfo, BranchSummary, BranchTimeline, CommonHistory, ComparisonBundle,
    ConstraintCheck, EventDelta, FactoryDefinition, FlowEdge, ForkPoint,
    IncidentDefinition, OrderDefinition, OrderState, Position,
    SimulationSnapshot, StationDefinition, StationState, Topology, UnitState,
    apply_delta, apply_to_branch, canonical_model_sha256, export_bundle, hours_to_us,
)

H = hours_to_us


def example_bundle() -> ComparisonBundle:
    factory = FactoryDefinition(
        stations={
            "CORTE": StationDefinition(id="CORTE", name="Corte", machine_ids=["M-CORTE"], x=.12, y=.5),
            "CNC": StationDefinition(id="CNC", name="CNC", machine_ids=["M-CNC"], required_skills=["CNC"], x=.5, y=.5),
            "MONTAGEM": StationDefinition(id="MONTAGEM", name="Montagem", machine_ids=["M-MONTAGEM"], x=.88, y=.5),
        },
        orders={"OP-1": OrderDefinition(id="OP-1", quantity=2, due_us=H(10),
                                         route_station_ids=["CORTE", "CNC", "MONTAGEM"])},
    )
    topology = Topology(edges=[
        FlowEdge(source="CORTE", target="CNC", waypoints=[Position(x=.31, y=.5)]),
        FlowEdge(source="CNC", target="MONTAGEM", waypoints=[Position(x=.68, y=.5)]),
    ])
    stations = {
        "CORTE": StationState(id="CORTE", status="idle", machine_capacity=1,
                              workers_available=1, busy_slots=0, queue_unit_ids=["OP-1#2"]),
        "CNC": StationState(id="CNC", status="idle", machine_capacity=1,
                            workers_available=1, busy_slots=0, queue_unit_ids=["OP-1#1"]),
        "MONTAGEM": StationState(id="MONTAGEM", status="idle", machine_capacity=1,
                                 workers_available=1, busy_slots=0, queue_unit_ids=[]),
    }
    units = {
        "OP-1#1": UnitState(id="OP-1#1", order_id="OP-1", route_step=1,
                            station_id="CNC", phase="queued"),
        "OP-1#2": UnitState(id="OP-1#2", order_id="OP-1", route_step=0,
                            station_id="CORTE", phase="queued"),
    }
    initial = SimulationSnapshot(branch_id="common", seq=0, time_us=0,
                                 stations=stations, units=units,
                                 orders={"OP-1": OrderState(id="OP-1", completed_units=0)})
    down = StationState(id="CNC", status="down", machine_capacity=1,
                        workers_available=1, busy_slots=0, queue_unit_ids=["OP-1#1"])
    start = EventDelta(seq=1, time_us=H(1), kind="outage_start", entity_id="CNC",
                       station_upserts={"CNC": down})
    common_end = apply_delta(initial, start)
    common = CommonHistory(provenance="synthetic_fixture", keyframes=[initial, common_end], events=[start])
    running = StationState(id="CNC", status="running", machine_capacity=1,
                           workers_available=1, busy_slots=1, queue_unit_ids=[],
                           processing_unit_ids=["OP-1#1"])
    processing = UnitState(id="OP-1#1", order_id="OP-1", route_step=1,
                           station_id="CNC", machine_id="M-CNC", phase="processing")
    # A e B compartilham exatamente o passado ate t=1.5 h.
    # Fork pode existir ENTRE dois eventos, sem inventar um evento no tempo 1.5 h.
    a_events = [EventDelta(seq=2, time_us=H(4), kind="outage_end", entity_id="CNC",
                           station_upserts={"CNC": running}, unit_upserts={"OP-1#1": processing})]
    b_events = [
        EventDelta(seq=2, time_us=H(1.5), kind="action_applied", entity_id="EXPRESS_REPAIR"),
        EventDelta(seq=3, time_us=H(2.5), kind="outage_end", entity_id="CNC",
                   station_upserts={"CNC": running}, unit_upserts={"OP-1#1": processing}),
    ]
    def terminal(branch_id, events):
        current = apply_to_branch(common_end, branch_id)
        for ev in events:
            current = apply_delta(current, ev)
        return current
    checks = [
        ConstraintCheck(name="operator_skill", status="unknown", subject_id="CNC",
                        evidence="Esta fixture nao possui matriz real de habilitacao."),
        ConstraintCheck(name="buffer_capacity", status="unknown", subject_id="CNC",
                        evidence="Capacidade de buffer ainda nao parametrizada no motor."),
    ]
    summary = BranchSummary(feasible="unverified", checks=checks)
    digest = canonical_model_sha256({
        "stations": {"CORTE": {"cycle_min": 35}, "CNC": {"cycle_min": 90},
                     "MONTAGEM": {"cycle_min": 30}},
        "order": {"id": "OP-1", "quantity": 2, "due_h": 10},
        "incident": {"station": "CNC", "start_h": 1, "duration_h": 3}, "seed": 42,
        "note": "Inputs ilustrativos; NAO e prova de modelo V30.2 completo.",
    })
    a = BranchTimeline(branch_id="A", run_id="mock-A", scenario_label="Sem intervencao",
                       provenance="synthetic_fixture", model_sha256=digest, seed=42,
                       events=a_events, keyframes=[terminal("A", a_events)], summary=summary)
    b = BranchTimeline(branch_id="B", run_id="mock-B", scenario_label="Reparo expresso hipotetico",
                       provenance="synthetic_fixture", model_sha256=digest, seed=42,
                       action=ActionInfo(action_id="EXPRESS_REPAIR", label="Reparo expresso",
                                         requested_us=H(1.5), effective_us=H(1.5)),
                       events=b_events, keyframes=[terminal("B", b_events)], summary=summary)
    return ComparisonBundle(
        experiment_id="SYNTHETIC-SLICE-001", definition=factory, topology=topology,
        incident=IncidentDefinition(incident_id="INC-1", station_id="CNC",
                                    start_us=H(1), planned_end_us=H(4)),
        fork=ForkPoint(seq=1, time_us=H(1.5), reason="intervention_requested"),
        common_history=common, branch_a=a, branch_b=b,
    )


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    bundle = example_bundle()
    export_bundle(bundle, root / "example_split_futures.json")
    (root / "simulation_contract.schema.json").write_text(
        json.dumps(ComparisonBundle.model_json_schema(by_alias=True), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Fixture e schema v1.1.0 gerados")
