from __future__ import annotations

from typing import Any, Dict, List, Optional
from simulation.numeric import metric, product_ratio


def _round_or_none(value: Optional[float], digits: int = 2):
    if value is None:
        return None
    return round(float(value), digits)


def _safe_pct(numer: float, denom: float) -> float:
    if denom == 0:
        return 0.0
    magnitude = product_ratio((abs(numer), 100), (abs(denom),), 'Percentual de recuperação')
    return -magnitude if (numer < 0) != (denom < 0) else magnitude


def classify_decision(row: Dict[str, Any], incident: Dict[str, Any], normal: Dict[str, Any], *, sla_floor: float = 0.0) -> Dict[str, Any]:
    """Classifica uma alternativa de decisão de forma explicável.

    O objetivo não é substituir a análise humana; é evitar narrativas enganosas,
    especialmente quando uma alternativa parece barata, mas compromete serviço.
    """
    reasons: List[str] = []
    if not row.get("feasible", True):
        reasons.append("inviável no modelo")
    if not row.get("within_budget", True):
        reasons.append("ultrapassa o teto de investimento")
    if not row.get("meets_sla", True):
        reasons.append(f"não atende ao SLA mínimo ({sla_floor:.0f}%)")

    decision_cost = metric(row, "decision_cost") if row.get("decision_cost") is not None else None
    incident_cost = metric(incident, "total_cost", 0.0)
    normal_cost = metric(normal, "total_cost", 0.0)
    incident_sla = metric(incident, "sla_pct", 0.0)
    normal_sla = metric(normal, "sla_pct", 0.0)
    incident_makespan = metric(incident, "makespan_h", 0.0)
    normal_makespan = metric(normal, "makespan_h", 0.0)

    if decision_cost is not None:
        savings_vs_incident = incident_cost - float(decision_cost)
        gap_vs_normal = float(decision_cost) - normal_cost
    else:
        savings_vs_incident = None
        gap_vs_normal = None

    service_gain = metric(row, "sla_pct", 0.0) - incident_sla
    makespan_gain = incident_makespan - metric(row, "makespan_h", 0.0)

    is_reference = row.get('action') == 'Não intervir'
    material_gain = ((savings_vs_incident is not None and savings_vs_incident > .005)
                     or service_gain > .005 or makespan_gain > .005)
    if is_reference:
        verdict = 'REFERÊNCIA'
        reasons.append('incidente sem intervenção; referência de comparação, não uma ação recomendada')
    elif not reasons:
        if not material_gain:
            verdict = 'SEM BENEFÍCIO'
            reasons.append('nenhuma melhora mensurável de custo, SLA ou tempo frente ao incidente')
        elif (decision_cost is not None and float(decision_cost) <= incident_cost + .005 and service_gain >= -.005 and makespan_gain >= -.005):
            verdict = "RECOMENDADA"
            reasons.append("melhora ou preserva serviço sem custar mais do que não intervir")
        elif service_gain > 0 and makespan_gain > 0:
            verdict = "PROMISSORA"
            reasons.append("recupera serviço e tempo, mas exige trade-off econômico")
        elif service_gain >= 0 and savings_vs_incident is not None and savings_vs_incident > 0:
            verdict = "CONDICIONAL"
            reasons.append("economiza frente ao incidente, mas o ganho operacional é limitado")
        else:
            verdict = "NÃO RECOMENDADA"
            reasons.append("não entrega recuperação suficientemente clara")
    else:
        verdict = "RESTRITA"

    recovery_den = incident_cost - normal_cost
    if savings_vs_incident is None or recovery_den <= .005:
        economic_recovery_pct = None
    else:
        economic_recovery_pct = _safe_pct(savings_vs_incident, recovery_den)

    service_recovery_den = normal_sla - incident_sla
    service_recovery_pct = _safe_pct(service_gain, service_recovery_den) if normal_sla > incident_sla else 0.0
    time_recovery_den = incident_makespan - normal_makespan
    time_recovery_pct = _safe_pct(makespan_gain, time_recovery_den) if incident_makespan > normal_makespan else 0.0

    tradeoff = []
    if savings_vs_incident is not None:
        if savings_vs_incident > 0:
            tradeoff.append(f"economia estimada de R$ {savings_vs_incident:,.2f} vs. não intervir")
        elif savings_vs_incident < 0:
            tradeoff.append(f"custo adicional de R$ {abs(savings_vs_incident):,.2f} vs. não intervir")
    if service_gain > 0:
        tradeoff.append(f"SLA +{service_gain:.1f} p.p.")
    elif service_gain < 0:
        tradeoff.append(f"SLA {service_gain:.1f} p.p.")
    if makespan_gain > 0:
        tradeoff.append(f"redução de {makespan_gain:.2f} h no makespan")
    elif makespan_gain < 0:
        tradeoff.append(f"aumento de {abs(makespan_gain):.2f} h no makespan")

    return {
        "verdict": verdict,
        "verdict_reason": "; ".join(reasons),
        "savings_vs_incident": _round_or_none(savings_vs_incident, 2),
        "cost_gap_vs_normal": _round_or_none(gap_vs_normal, 2),
        "service_gain_pp": round(service_gain, 1),
        "makespan_gain_h": round(makespan_gain, 2),
        "economic_recovery_pct": _round_or_none(economic_recovery_pct, 1),
        "service_recovery_pct": round(service_recovery_pct, 1),
        "time_recovery_pct": round(time_recovery_pct, 1),
        "tradeoff_note": " · ".join(tradeoff) if tradeoff else "Sem trade-off resumido.",
    }


def enrich_decision_rows(rows: List[Dict[str, Any]], incident: Dict[str, Any], normal: Dict[str, Any], *, sla_floor: float = 0.0) -> List[Dict[str, Any]]:
    enriched = []
    for row in rows:
        extra = classify_decision(row, incident, normal, sla_floor=sla_floor)
        merged = dict(row)
        merged.update(extra)
        enriched.append(merged)
    return enriched


def select_recommended_action(rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    # Nunca apresente como líder uma opção que viola restrições ou é inviável.
    rows = [r for r in rows if r.get('action') != 'Não intervir'
            and r.get('verdict') in {'RECOMENDADA','PROMISSORA','CONDICIONAL'}
            and r.get("feasible", False)
            and r.get("within_budget", False) and r.get("meets_sla", False)]
    if not rows:
        return None
    order = {
        "RECOMENDADA": 0,
        "PROMISSORA": 1,
        "CONDICIONAL": 2,
        "NÃO RECOMENDADA": 3,
        "RESTRITA": 4,
    }
    ranked = sorted(
        rows,
        key=lambda r: (
            order.get(str(r.get("verdict", "RESTRITA")), 9),
            999999999 if r.get("decision_cost") is None else metric(r,"decision_cost"),
            -float(r.get("sla_pct", 0.0)),
            float(r.get("makespan_h", 0.0)),
        ),
    )
    return ranked[0] if ranked else None


def blocked_station_fixes(stations: Dict[str, Dict[str, Any]], orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    used = {sid for o in orders for sid, _mins in o.get("route", [])}
    fixes: List[Dict[str, Any]] = []
    for sid, s in stations.items():
        if sid not in used:
            continue
        machines = int(s.get("maquinas", 0))
        workers = int(s.get("operadores", 0))
        opm = float(s.get("operadores_por_maquina", 1) or 1)
        required = max(1, int(machines * opm))
        if workers <= 0:
            fixes.append({
                "station": sid,
                "severity": "CRÍTICO",
                "problem": "posto sem operadores declarados",
                "fix": f"Adicionar pelo menos {required} operador(es) ao posto {sid} ou reduzir a capacidade modelada.",
            })
        elif workers < required:
            fixes.append({
                "station": sid,
                "severity": "ATENÇÃO",
                "problem": f"capacidade simultânea abaixo da nominal ({workers}/{required} operadores)",
                "fix": f"Operação ainda pode ser viável em {sid}. Considere testar mais operadores ou reduzir máquinas ativas; não presuma que isso aumentará o throughput.",
            })
    return fixes
