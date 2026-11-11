from data.scenarios import STATIONS_BASE, ORDERS_BASE, DEFAULT_RULE, DEFAULT_SEED
from simulation.factory import build_scenario
from simulation.engine import run_simulation
from simulation.decision_lab import evaluate_decisions
from simulation.ai_copilot import build_ai_context, local_copilot_answer
from simulation.decision_council import blocked_station_fixes


def test_decision_evidence_exposes_verdicts_and_recommendation():
    cfg = build_scenario('base', STATIONS_BASE, ORDERS_BASE, dispatch_rule=DEFAULT_RULE, seed=DEFAULT_SEED)
    incident = cfg.clone('incident')
    incident.chaos_station = 'CNC'
    incident.chaos_start_h = 4
    incident.chaos_duration_h = 5
    data = evaluate_decisions(incident, budget=10000, sla_floor=80)
    assert data['recommended'] is not None
    assert 'verdict' in data['recommended']
    assert any('verdict' in row for row in data['rows'])


def test_ai_context_has_brief_and_local_answer_uses_it():
    cfg = build_scenario('base', STATIONS_BASE, ORDERS_BASE, dispatch_rule=DEFAULT_RULE, seed=DEFAULT_SEED)
    base = run_simulation(cfg)
    incident = cfg.clone('incident')
    incident.chaos_station = 'CNC'
    incident.chaos_start_h = 4
    incident.chaos_duration_h = 5
    decisions = evaluate_decisions(incident, budget=10000, sla_floor=80)
    ctx = build_ai_context(base, STATIONS_BASE, decision_data=decisions)
    assert 'executive_brief' in ctx
    ans = local_copilot_answer('qual é a decisão recomendada?', ctx)
    assert 'alternativa líder' in ans.lower() or 'próxima alternativa' in ans.lower() or 'proxima alternativa' in ans.lower()


def test_blocked_station_fixes_detect_zero_operators():
    stations = {k: dict(v) for k, v in STATIONS_BASE.items()}
    stations['CORTE']['operadores'] = 0
    fixes = blocked_station_fixes(stations, ORDERS_BASE)
    assert fixes
    assert any(x['station'] == 'CORTE' for x in fixes)
