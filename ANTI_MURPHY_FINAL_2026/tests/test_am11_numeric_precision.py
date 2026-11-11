"""Independent dimensional references for AM-11, without editing the DES clock.

Noise=1 gives exact classroom references. One case keeps the actual seeded noise.
Legacy presentation keys remain available; calculation consumers use precise values.
"""
from copy import deepcopy
import math

import pytest

from simulation.engine import run_simulation
from simulation.factory import TimedAction, build_scenario
from simulation.numeric import metric
from simulation.validation import validate_model


def scenario(*, minutes=0.06, quantity=1, machines=1, workers=1,
             efficiency=1.0, availability=1.0, automated=False,
             deadline=100.0, release=0.0):
    stations = {'P': {
        'nome': 'Posto de referência', 'maquinas': machines,
        'operadores': workers, 'operadores_por_maquina': 1,
        'eficiencia_operador': efficiency, 'disponibilidade': availability,
        'custo_maquina_h': 10.0, 'custo_operador_h': 20.0,
        'setup_min': 0.0, 'automatizada': automated,
    }}
    orders = [{
        'id': 'REF', 'cliente': 'Referência', 'produto': 'Peça',
        'quantidade': quantity, 'prazo_h': deadline, 'multa_hora': 100.0,
        'prioridade': 1, 'release_h': release, 'route': [('P', minutes)],
    }]
    return build_scenario('Referência dimensional AM-11', stations, orders)


@pytest.fixture
def exact_noise(monkeypatch):
    monkeypatch.setattr('simulation.engine._noise', lambda *_args: 1.0)


def test_one_thousandth_hour_reference_has_positive_horizon_and_full_utilization(exact_noise):
    # 0.06 min / 60 = 0.001 h; one unit / 0.001 h = 1,000 units/h.
    cfg = scenario()
    result = run_simulation(cfg)
    assert result['makespan_h'] > 0, 'Presentation must never turn a positive horizon into zero.'
    assert metric(result, 'makespan_h') == pytest.approx(0.001)
    assert metric(result, 'throughput_h') == pytest.approx(1000.0)
    assert result['stations'][0]['Utilização máquina (%)'] == 100.0
    assert result['stations'][0]['Utilização mão de obra (%)'] == 100.0
    assert metric(result, 'operating_cost') == pytest.approx(0.001 * (10 + 20))
    assert result['precise']['makespan_h'] == pytest.approx(0.001)
    assert cfg.stations['P']['eficiencia_operador'] == 1.0


@pytest.mark.parametrize('capacity', [1, 2, 4])
@pytest.mark.parametrize('batches', [1, 3])
def test_parallel_capacity_uses_actual_machine_and_worker_hours(capacity, batches, exact_noise):
    quantity = capacity * batches
    result = run_simulation(scenario(quantity=quantity, machines=capacity, workers=capacity))
    horizon = batches * 0.001
    assert metric(result, 'makespan_h') == pytest.approx(horizon)
    assert metric(result, 'throughput_h') == pytest.approx(quantity / horizon)
    assert result['stations'][0]['Utilização máquina (%)'] == 100.0
    assert result['stations'][0]['Utilização mão de obra (%)'] == 100.0
    assert metric(result, 'operating_cost') == pytest.approx(horizon * capacity * 30)


@pytest.mark.parametrize('field', ['eficiencia_operador', 'disponibilidade'])
@pytest.mark.parametrize('factor', [0.001, 0.009, 0.01, 0.1, 1.0])
def test_positive_factors_are_preserved_without_hidden_floor(field, factor, exact_noise):
    cfg = scenario(minutes=60, deadline=100)
    cfg.stations['P'][field] = factor
    before = deepcopy(cfg)
    assert validate_model(cfg.stations, cfg.orders) == []
    result = run_simulation(cfg)
    horizon = 1.0 / factor
    penalty = max(0.0, horizon - 100.0) * 100.0
    assert metric(result, 'makespan_h') == pytest.approx(horizon)
    assert metric(result, 'throughput_h') == pytest.approx(1.0 / horizon)
    assert metric(result, 'operating_cost') == pytest.approx(horizon * 30)
    assert metric(result, 'penalty_total') == pytest.approx(penalty)
    assert metric(result, 'total_cost') == pytest.approx(horizon * 30 + penalty)
    assert result['sla_pct'] == (0.0 if horizon > 100 else 100.0)
    assert cfg == before


@pytest.mark.parametrize('field', ['eficiencia_operador', 'disponibilidade'])
@pytest.mark.parametrize('value', [None, 0, -0.001, math.nan, math.inf, -math.inf])
def test_invalid_factors_are_rejected_before_simulation(field, value):
    cfg = scenario()
    cfg.stations['P'][field] = value
    with pytest.raises(ValueError):
        run_simulation(cfg)


@pytest.mark.parametrize('value', [None, 0, -0.001, math.nan, math.inf, -math.inf])
def test_zero_negative_and_nonfinite_processing_durations_are_rejected(value):
    with pytest.raises(ValueError):
        run_simulation(scenario(minutes=value))


def test_actual_seeded_noise_still_obeys_dimensional_metrics():
    result = run_simulation(scenario())
    horizon = max(op['end_h'] for op in result['operations'])
    assert 0 < horizon < 0.01
    assert metric(result, 'makespan_h') == pytest.approx(horizon)
    assert metric(result, 'throughput_h') == pytest.approx(1 / horizon)
    assert result['stations'][0]['Utilização máquina (%)'] == 100.0
    assert result['stations'][0]['Utilização mão de obra (%)'] == 100.0


def test_releases_and_multiple_orders_include_idle_time_in_plan_horizon(exact_noise):
    cfg = scenario()
    cfg.orders = [dict(cfg.orders[0], id=f'O{i}', release_h=release)
                  for i, release in enumerate([0.0, 0.001, 0.005])]
    result = run_simulation(cfg)
    # Three busy intervals of 0.001 h, including 0.003 h idle between them.
    assert metric(result, 'makespan_h') == pytest.approx(0.006)
    assert metric(result, 'throughput_h') == pytest.approx(3 / 0.006)
    assert result['stations'][0]['Utilização máquina (%)'] == 50.0
    assert result['stations'][0]['Utilização mão de obra (%)'] == 50.0
    assert metric(result, 'operating_cost') == pytest.approx(0.006 * 30)


def test_automated_station_with_no_workers_has_defined_zero_labor_utilization(exact_noise):
    result = run_simulation(scenario(workers=0, automated=True))
    assert result['feasible']
    assert result['stations'][0]['Utilização máquina (%)'] == 100.0
    assert result['stations'][0]['Utilização mão de obra (%)'] == 0.0
    assert metric(result, 'operating_cost') == pytest.approx(0.001 * 10)


def test_timed_worker_addition_integrates_capacity_and_keeps_in_flight_operations(exact_noise):
    cfg = scenario(quantity=4, machines=2, workers=1)
    action = TimedAction(0.0015, workers_delta={'P': 1})
    baseline = run_simulation(cfg)
    result = run_simulation(cfg, action)
    assert result['intervention']['effective_h'] == pytest.approx(0.0015)
    # Intervals: [0,.001], [.001,.002], [.0015,.0025], [.002,.003].
    assert metric(result, 'makespan_h') == pytest.approx(0.003)
    assert metric(result, 'throughput_h') == pytest.approx(4 / 0.003)
    machine_hours = 2 * 0.003
    worker_hours = 0.0015 + 2 * 0.0015
    assert result['stations'][0]['Utilização máquina (%)'] == pytest.approx(round(100 * 0.004 / machine_hours, 1))
    assert result['stations'][0]['Utilização mão de obra (%)'] == pytest.approx(round(100 * 0.004 / worker_hours, 1))
    assert metric(result, 'operating_cost') == pytest.approx(machine_hours * 10 + worker_hours * 20)
    assert result['stations'][0]['precise']['machine_util_pct'] == pytest.approx(100 * 0.004 / machine_hours)
    assert result['stations'][0]['precise']['worker_util_pct'] == pytest.approx(100 * 0.004 / worker_hours)
    prefix = lambda r: sorted((op['Unidade'], op['start_h'], min(op['end_h'], action.at_h))
                              for op in r['operations'] if op['start_h'] < action.at_h)
    assert prefix(result) == prefix(baseline)


def test_precise_values_are_not_rounded_before_ratio_or_cost_calculation(exact_noise):
    minutes = 0.07407
    horizon = minutes / 60
    result = run_simulation(scenario(minutes=minutes))
    assert metric(result, 'makespan_h') == pytest.approx(horizon, rel=1e-13)
    assert metric(result, 'throughput_h') == pytest.approx(1 / horizon, rel=1e-13)
    assert metric(result, 'operating_cost') == pytest.approx(horizon * 30, rel=1e-13)
    assert metric(result, 'unit_cost') == pytest.approx(horizon * 30, rel=1e-13)


@pytest.mark.parametrize('mutate', [
    lambda cfg: cfg.stations['P'].update(eficiencia_operador=1e-308, disponibilidade=1e-308),
    lambda cfg: cfg.orders[0].update(route=[('P', 1e-320)]),
    lambda cfg: cfg.orders[0].update(release_h=1e20),
])
def test_unrepresentable_overflow_underflow_or_clock_progress_is_explicitly_rejected(mutate, exact_noise):
    cfg = scenario()
    mutate(cfg)
    with pytest.raises(ValueError):
        run_simulation(cfg)


def test_metric_helper_keeps_legacy_result_dictionary_compatibility():
    assert metric({'makespan_h': 1.25}, 'makespan_h') == 1.25
    assert metric({'makespan_h': 1.25, 'precise': {'makespan_h': 1.254}}, 'makespan_h') == 1.254


def test_order_reference_keeps_completion_and_lateness_before_display_rounding(exact_noise):
    cfg = scenario(minutes=0.06, deadline=0.0012)
    cfg.orders[0]['route'] = [('P', 0.06), ('P', 0.03)]
    result = run_simulation(cfg)
    row = result['orders'][0]
    assert row['completion_h'] == pytest.approx(0.0015)
    assert row['lateness_h'] == pytest.approx(0.0003)
    assert row['penalty'] == pytest.approx(0.03)
    assert result['late_orders'] == 1
    assert metric(result, 'sla_pct') == 0.0
    assert metric(result, 'penalty_total') == pytest.approx(0.03)


def three_order_sla_reference():
    cfg = scenario(minutes=60)
    cfg.orders = [dict(cfg.orders[0], id=oid, prazo_h=due)
                  for oid, due in [('A', 1.5), ('B', 2.5), ('C', 2.6)]]
    return cfg


@pytest.mark.parametrize('minimum,expected', [(66.66, True), (66.68, False)])
def test_temporal_response_sla_eligibility_uses_two_thirds_before_display_rounding(minimum, expected, exact_noise):
    from simulation.atlas import DecisionPolicy
    from simulation.response import analyze_response
    cfg = three_order_sla_reference()
    # This incident is after completion, so the service reference stays 2/3.
    data = analyze_response(cfg, 'P', 10.0, 1.0, DecisionPolicy(min_sla=minimum))
    row = next(item for item in data['rows'] if item['action'] == 'Não intervir')
    assert row['result']['sla_pct'] == 66.7  # Existing display contract stays rounded.
    assert metric(row['result'], 'sla_pct') == pytest.approx(200 / 3)
    assert row['meets_sla'] is expected


@pytest.mark.parametrize('minimum,expected', [(66.66, True), (66.68, False)])
def test_structural_decisions_sla_eligibility_uses_unrounded_two_thirds(minimum, expected, exact_noise):
    from simulation.decision_lab import evaluate_decisions
    data = evaluate_decisions(three_order_sla_reference(), sla_floor=minimum, max_actions=1)
    row = next(item for item in data['rows'] if item['action'] == 'Não intervir')
    assert row['result']['sla_pct'] == 66.7
    assert metric(row['result'], 'sla_pct') == pytest.approx(200 / 3)
    assert row['meets_sla'] is expected


@pytest.mark.parametrize('target,expected', [(1.0002, 'Sim'), (1.0005, 'Não')])
def test_capacity_goal_threshold_reads_precise_throughput(target, expected, exact_noise):
    from simulation.innovation import goal_seek
    cfg = scenario(minutes=60 / 1.0004)
    baseline = run_simulation(cfg)
    assert baseline['throughput_h'] == 1.0  # Rounded display is insufficient for this goal.
    assert metric(baseline, 'throughput_h') == pytest.approx(1.0004)
    rows = goal_seek(cfg, baseline, target_throughput=target, target_sla=100,
                     max_extra_workers=1, max_extra_machines=0)
    # Extra worker cannot change the single machine's throughput.
    assert len(rows) == 1
    assert rows[0]['Atinge meta'] == expected
    assert rows[0]['Throughput'] == pytest.approx(1.0004)


def test_precise_metrics_survive_plain_json_archive_roundtrip(exact_noise):
    import json
    result = run_simulation(scenario(minutes=0.07407))
    payload = {key: value for key, value in result.items() if key != 'config'}
    archived = json.loads(json.dumps(payload, allow_nan=False))
    assert metric(archived, 'makespan_h') == pytest.approx(0.07407 / 60, rel=1e-13)
    assert metric(archived, 'throughput_h') == pytest.approx(60 / 0.07407, rel=1e-13)
    assert metric(archived, 'operating_cost') == pytest.approx(0.07407 / 60 * 30, rel=1e-13)


def test_representable_duration_is_recovered_when_naive_intermediate_division_underflows(exact_noise):
    # min positive float/min positive efficiency = 1 minute, still representable.
    # Dividing minutes by 60 first would underflow before efficiency cancels it.
    tiny = math.nextafter(0.0, 1.0)
    result = run_simulation(scenario(minutes=tiny, efficiency=tiny))
    assert metric(result, 'makespan_h') == pytest.approx(1 / 60)
    assert metric(result, 'throughput_h') == pytest.approx(60.0)
    assert metric(result, 'operating_cost') == pytest.approx(0.5)
    assert result['stations'][0]['Utilização máquina (%)'] == 100.0
