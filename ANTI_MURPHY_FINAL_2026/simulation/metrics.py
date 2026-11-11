from __future__ import annotations

from typing import Dict, Any, List
from math import isfinite

from simulation.numeric import finite, metric, product_ratio


def compare_results(base: Dict[str, Any], alt: Dict[str, Any]) -> Dict[str, float]:
    def pct(new, old):
        # A zero reference has no defined percentage change; retain the existing
        # neutral convention. Every nonzero reference uses its actual value.
        change = 0.0 if old == 0 else ((new - old) / old) * 100.0
        if not isfinite(change):
            raise ValueError('Variação percentual fora do intervalo numérico representável.')
        return change

    return {
        "throughput_pct": pct(metric(alt, "throughput_h"), metric(base, "throughput_h")),
        "makespan_pct": pct(metric(alt, "makespan_h"), metric(base, "makespan_h")),
        "total_cost_pct": pct(metric(alt, "total_cost"), metric(base, "total_cost")),
        "unit_cost_pct": pct(metric(alt, "unit_cost"), metric(base, "unit_cost")),
        "sla_pp": metric(alt, "sla_pct") - metric(base, "sla_pct"),
        "penalty_delta": metric(alt, "penalty_total") - metric(base, "penalty_total"),
    }


def murphy_score(result: Dict[str, Any]) -> float:
    """Índice próprio de resiliência operacional (0–100), sem pretensão normativa."""
    sla = float(metric(result, "sla_pct"))
    balance = max(0.0, 100.0 - float(metric(result, "balance_loss_pp")))
    penalty_factor = max(0.0, 100.0 - min(100.0, metric(result, "penalty_total") / 80.0))
    util_map = {r["Posto"]: finite(r.get('precise', {}).get('machine_util_pct',
                                                    r["Utilização máquina (%)"]), 'Utilização máquina')
                for r in result["stations"]}
    avg_util = sum(util_map.values()) / max(1, len(util_map))
    utilization_quality = max(0.0, 100.0 - abs(78.0 - avg_util) * 1.4)
    score = 0.40 * sla + 0.25 * balance + 0.20 * penalty_factor + 0.15 * utilization_quality
    return round(max(0.0, min(100.0, score)), 1)


def fingerprint(result: Dict[str, Any], base: Dict[str, Any] | None = None) -> Dict[str, float]:
    base = base or result
    max_tp = max(metric(base, "throughput_h"), metric(result, "throughput_h"))
    tp = 0.0 if max_tp == 0 else min(100.0, product_ratio(
        [100.0, metric(result, "throughput_h")], [max_tp], 'Fluxo normalizado'))
    sla = float(metric(result, "sla_pct"))
    balance = max(0.0, 100.0 - float(metric(result, "balance_loss_pp")))
    base_cost, actual_cost = metric(base, "unit_cost"), metric(result, "unit_cost")
    if base_cost == 0:
        # With no reference cost, distinguish another zero from a new expense;
        # no finite percentage ratio exists for a positive cost over zero.
        cost_eff = 100.0 if actual_cost == 0 else 0.0
    else:
        ratio = product_ratio([actual_cost], [base_cost], 'Custo unitário relativo')
        cost_eff = max(0.0, 100.0 - min(100.0, (ratio - 0.65) * 120))
    resilience = murphy_score(result)
    return {
        "Fluxo": round(tp, 1),
        "SLA": round(sla, 1),
        "Balanceamento": round(balance, 1),
        "Eficiência de custo": round(cost_eff, 1),
        "Resiliência": round(resilience, 1),
    }
