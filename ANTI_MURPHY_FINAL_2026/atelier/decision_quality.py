"""Auditable finite-alternative dominance screen for the workbench.

This is *not* an optimization algorithm, an industrial feasibility verdict, or an
assertion of a unique best decision. It only compares three modeled indicators
within the alternatives that the original engine has actually enumerated.
"""
from __future__ import annotations
from math import isfinite
from typing import Any
from simulation.numeric import metric

EPS_COST = 0.01      # reais
EPS_H = 0.005        # simulation hours
EPS_SLA = 0.005      # percentage points


def _numbers(item: dict[str, Any]):
    try:
        values = (metric(item,'decision_cost'), metric(item,'makespan_h'), metric(item,'sla_pct'))
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    return values if all(map(isfinite, values)) else None


def _eligible(item: dict[str, Any]) -> bool:
    return all(item.get(k) is True for k in ('feasible', 'within_budget', 'meets_sla')) and _numbers(item) is not None


def _dominates(other: dict[str, Any], selected: dict[str, Any]) -> bool:
    a = _numbers(other)
    b = _numbers(selected)
    if a is None or b is None:
        return False
    better_or_equal = a[0] <= b[0] + EPS_COST and a[1] <= b[1] + EPS_H and a[2] >= b[2] - EPS_SLA
    strictly_better = a[0] < b[0] - EPS_COST or a[1] < b[1] - EPS_H or a[2] > b[2] + EPS_SLA
    return better_or_equal and strictly_better


def review_alternatives(alternatives: list[dict[str, Any]], signature: str | None) -> dict[str, Any]:
    """Compare alternatives only in modeled cost, makespan, and SLA.

    A status of 'non_dominated' means no *eligible enumerated* rival dominates
    the selection in these three indicators; it says nothing about global
    optimality or real-world execution.
    """
    candidates = [r for r in alternatives if isinstance(r, dict)]
    chosen = next((r for r in candidates if r.get('signature') == signature), None)
    count = sum(_eligible(x) for x in candidates)
    base = {'status': 'unknown', 'selected': signature, 'eligible_count': count,
            'evaluated_count': len(candidates), 'dominated_by': [],
            'metrics': ['decision_cost', 'makespan_h', 'sla_pct'],
            'physical_feasibility_verified': False}
    if chosen is None or _numbers(chosen) is None:
        return base
    if not _eligible(chosen):
        return {**base, 'status': 'outside_criteria'}
    rivals = [r for r in candidates if r.get('signature') != signature and _eligible(r) and _dominates(r, chosen)]
    rivals.sort(key=lambda r: (r['decision_cost'], r['makespan_h'], -r['sla_pct'], str(r.get('signature'))))
    return {**base, 'status': 'dominated' if rivals else 'non_dominated',
            'dominated_by': [{k: r.get(k) for k in ('signature', 'action', 'decision_cost', 'makespan_h', 'sla_pct')}
                             for r in rivals]}
