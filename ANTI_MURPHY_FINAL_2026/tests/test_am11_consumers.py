"""Independent references for numeric consumers, without changing search scope."""
from copy import deepcopy
from unittest.mock import patch

import pytest

from simulation.advanced import (
    demand_breakpoint, monte_carlo_analysis, recovery_plan, sensitivity_analysis,
)
from simulation.factory import ScenarioConfig
from simulation.innovation import finance_lens, goal_seek
from simulation.metrics import compare_results, fingerprint, murphy_score


def packet(**updates):
    raw = dict(makespan_h=1.0, throughput_h=1.0, sla_pct=100.0,
               total_cost=10.0, unit_cost=10.0, operating_cost=10.0,
               penalty_total=0.0, balance_loss_pp=0.0)
    raw.update(updates)
    return {**{k: round(v, 1 if k == 'sla_pct' else 2) for k, v in raw.items()},
            'precise': raw, 'feasible': True, 'bottleneck': 'P',
            'stations': [], 'intervention': {'effective_h': 2.0}}


def config():
    return ScenarioConfig('reference', {'P': {'maquinas': 1, 'operadores': 1}}, [],
                          chaos_station='P', chaos_start_h=1, chaos_duration_h=2)


def test_percent_change_preserves_nonzero_small_reference():
    a = packet(makespan_h=1e-12, throughput_h=1e-12, total_cost=1e-12, unit_cost=1e-12)
    b = packet(makespan_h=2e-12, throughput_h=2e-12, total_cost=2e-12, unit_cost=2e-12)
    changes = compare_results(a, b)
    for key in ('makespan_pct', 'throughput_pct', 'total_cost_pct', 'unit_cost_pct'):
        assert changes[key] == pytest.approx(100)


def test_percentage_zero_reference_keeps_legacy_neutral_convention():
    assert compare_results(packet(throughput_h=0), packet(throughput_h=1))['throughput_pct'] == 0


def test_finance_uses_cost_rate_over_actual_short_horizon():
    # Base 0.01 / 0.001 = 10/h; alternative 0.04 / 0.002 = 20/h.
    # Over eight hours the incremental capacity cost is 80, not 8.
    a = packet(makespan_h=.001, operating_cost=.01)
    b = packet(makespan_h=.002, operating_cost=.04)
    lens = finance_lens(a, b, contribution_margin_per_unit=0, hours_per_day=8)
    assert lens['incremental_cost_day'] == 80
    assert lens['net_day'] == -80


@pytest.mark.parametrize('horizon', [0.0, -1.0, float('inf'), float('nan')])
def test_finance_rejects_horizon_without_finite_positive_rate(horizon):
    with pytest.raises(ValueError):
        finance_lens(packet(makespan_h=horizon), packet(), 1)


@pytest.mark.parametrize('field', ['contribution_margin_per_unit', 'hours_per_day', 'one_time_investment'])
def test_finance_rejects_nonfinite_input(field):
    args = dict(contribution_margin_per_unit=1, hours_per_day=8, one_time_investment=0)
    args[field] = float('nan')
    with pytest.raises(ValueError):
        finance_lens(packet(), packet(), **args)


def test_goal_sla_threshold_does_not_approve_rounded_up_fraction():
    candidate = packet(sla_pct=200 / 3)
    assert candidate['sla_pct'] == 66.7
    with patch('simulation.innovation.run_simulation', return_value=candidate):
        rows = goal_seek(config(), packet(), target_throughput=0, target_sla=66.68,
                         max_extra_workers=1, max_extra_machines=0)
    assert rows[0]['Atinge meta'] == 'Não'


def test_goal_throughput_threshold_does_not_reject_rounded_down_value():
    candidate = packet(throughput_h=1.0004)
    assert candidate['throughput_h'] == 1.0
    with patch('simulation.innovation.run_simulation', return_value=candidate):
        rows = goal_seek(config(), packet(), target_throughput=1.0002, target_sla=80,
                         max_extra_workers=1, max_extra_machines=0)
    assert rows[0]['Atinge meta'] == 'Sim'
    assert rows[0]['Throughput'] == 1.0004


def test_sensitivity_keeps_true_small_marginal_gain():
    baseline = packet(throughput_h=1)
    candidate = packet(throughput_h=1.0004)
    with patch('simulation.advanced.run_simulation', return_value=candidate):
        rows = sensitivity_analysis(config(), baseline, 'P', max_add=1)
    assert rows[1]['Ganho marginal TP'] == pytest.approx(.0004)


def test_demand_breakpoint_compares_exact_sla():
    candidate = packet(sla_pct=200 / 3)
    with patch('simulation.advanced.run_simulation', return_value=candidate):
        result = demand_breakpoint(config(), sla_floor=66.68, demand_start=1, demand_stop=1)
    assert result['first_break'] is not None
    assert result['last_safe'] is None


def test_monte_carlo_statistics_use_unrounded_values():
    candidate = packet(throughput_h=1.0004, makespan_h=.00123, unit_cost=.01234, sla_pct=200 / 3)
    with patch('simulation.advanced.run_simulation', return_value=candidate):
        result = monte_carlo_analysis(config(), runs=4)
    assert result['summary']['throughput']['mean'] == pytest.approx(1.0004)
    assert result['summary']['makespan']['mean'] == pytest.approx(.00123)
    assert result['summary']['unit_cost']['mean'] == pytest.approx(.01234)
    assert result['summary']['sla']['mean'] == pytest.approx(200 / 3)


def test_recovery_ranks_before_rounding_heuristic_score():
    baseline = packet(throughput_h=100, unit_cost=100)
    first = packet(throughput_h=100.018, unit_cost=1)
    second = packet(throughput_h=100.02, unit_cost=2)
    # Both displayed scores round to 0.0. The larger exact gain must win,
    # rather than using unit cost to break an artificial rounded tie.
    with patch('simulation.advanced.run_simulation', side_effect=[first, second]):
        rows = recovery_plan(config(), baseline, max_results=2, action_at_h=2)
    assert rows[0]['Ação'] == '+1 máquina em P'
    assert rows[0]['Recovery score'] == rows[1]['Recovery score'] == 0.0


def test_fingerprint_preserves_small_positive_scale_ratios():
    base = packet(throughput_h=2e-6, unit_cost=5e-6)
    result = packet(throughput_h=1e-6, unit_cost=5e-6)
    radar = fingerprint(result, base)
    assert radar['Fluxo'] == 50.0
    # Same real unit cost has ratio1:100-(1-.65)*120=58.
    assert radar['Eficiência de custo'] == 58.0


def test_fingerprint_zero_reference_has_explicit_meaning():
    base = packet(throughput_h=0, unit_cost=0)
    same_zero = fingerprint(base, base)
    assert same_zero['Fluxo'] == 0
    assert same_zero['Eficiência de custo'] == 100
    assert fingerprint(packet(unit_cost=1), base)['Eficiência de custo'] == 0


def test_murphy_score_uses_precise_station_utilization():
    result = packet()
    result['stations'] = [{'Posto': 'P', 'Utilização máquina (%)': 0,
                           'precise': {'machine_util_pct': 78}}]
    assert murphy_score(result) == 100.0
