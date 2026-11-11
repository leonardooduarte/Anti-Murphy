from __future__ import annotations

from typing import Any, Dict, List

from simulation.metrics import compare_results


def _penalties(result: Dict[str, Any]) -> float:
    if "penalty_total" in result:
        return float(result.get("penalty_total", 0) or 0)
    return sum(float(x.get("Multa (R$)", 0) or 0) for x in result.get("orders", []))


def decision_scorecard(base: Dict[str, Any], alt: Dict[str, Any]) -> Dict[str, Any]:
    """Transparent multi-dimensional score. It is a decision aid, not a probability."""
    d = compare_results(base, alt)
    tp = float(d.get("throughput_pct", 0))
    sla = float(d.get("sla_pp", 0))
    cost = float(d.get("unit_cost_pct", 0))
    mk = float(d.get("makespan_pct", 0))

    # 50 = neutral. Each dimension is intentionally bounded and explainable.
    flow = max(0.0, min(100.0, 50.0 + tp * 2.2))
    service = max(0.0, min(100.0, 50.0 + sla * 1.25))
    economics = max(0.0, min(100.0, 50.0 - cost * 2.0))
    speed = max(0.0, min(100.0, 50.0 - mk * 1.45))
    overall = 0.27 * flow + 0.30 * service + 0.23 * economics + 0.20 * speed

    if overall >= 72 and service >= 50:
        band, verdict = "STRONG", "Candidato forte para validação"
    elif overall >= 58 and service >= 42:
        band, verdict = "PROMISING", "Promissor, com trade-offs a validar"
    elif overall >= 42:
        band, verdict = "MIXED", "Trade-off relevante; não decidir só pelo throughput"
    else:
        band, verdict = "WEAK", "Resultado fraco para os objetivos atuais"

    return {
        "overall": round(overall, 1), "band": band, "verdict": verdict,
        "flow": round(flow, 1), "service": round(service, 1),
        "economics": round(economics, 1), "speed": round(speed, 1),
        "delta": d,
    }


def value_at_stake(base: Dict[str, Any], alt: Dict[str, Any] | None = None) -> Dict[str, Any]:
    base_pen = _penalties(base)
    late = sum(1 for x in base.get("orders", []) if float(x.get("Atraso (h)", 0) or 0) > 0)
    total = len(base.get("orders", []))
    out = {
        "base_penalties": base_pen,
        "late_orders": late,
        "total_orders": total,
        "late_share": (100.0 * late / total) if total else 0.0,
    }
    if alt:
        alt_pen = _penalties(alt)
        out.update({
            "alt_penalties": alt_pen,
            "penalty_recovery": base_pen - alt_pen,
            "penalty_recovery_pct": (100.0 * (base_pen-alt_pen) / base_pen) if base_pen else 0.0,
        })
    return out


def station_pressure(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows=[]
    for r in result.get("stations", []):
        q=float(r.get("Fila máx.",0) or 0)
        w=float(r.get("Espera média (min)",0) or 0)
        u=float(r.get("Utilização máquina (%)",0) or 0)
        lu=float(r.get("Utilização mão de obra (%)",0) or 0)
        score=min(100.0, q*0.65 + min(w,360)/6.0 + max(u,lu)*0.25)
        rows.append({
            "station":str(r.get("Posto","-")), "name":str(r.get("Nome",r.get("Posto","-"))),
            "score":round(score,1), "queue":int(q), "wait":round(w,1), "util":round(max(u,lu),1),
        })
    return sorted(rows,key=lambda x:x["score"],reverse=True)


def portfolio_frontier(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return non-dominated scenarios using throughput↑, SLA↑, cost↓, makespan↓."""
    if not history:
        return []
    rows=[]
    for h in history:
        rows.append({
            "name":h.get("name","Scenario"), "source":h.get("source","-"),
            "throughput":float(h.get("throughput",0)), "sla":float(h.get("sla",0)),
            "unit_cost":float(h.get("unit_cost",0)), "makespan":float(h.get("makespan",0)),
            "bottleneck":h.get("bottleneck","-"), "result":h.get("result")
        })
    frontier=[]
    for a in rows:
        dominated=False
        for b in rows:
            if a is b: continue
            no_worse=(b["throughput"]>=a["throughput"] and b["sla"]>=a["sla"] and b["unit_cost"]<=a["unit_cost"] and b["makespan"]<=a["makespan"])
            strictly=(b["throughput"]>a["throughput"] or b["sla"]>a["sla"] or b["unit_cost"]<a["unit_cost"] or b["makespan"]<a["makespan"])
            if no_worse and strictly:
                dominated=True; break
        if not dominated:
            frontier.append(a)
    return frontier


def workspace_payload(stations: Dict[str, Any], orders: List[Dict[str, Any]], history: List[Dict[str, Any]]) -> Dict[str, Any]:
    clean_hist=[]
    for h in history[-30:]:
        clean_hist.append({k:h.get(k) for k in ["name","source","bottleneck","throughput","sla","unit_cost","makespan"]})
    return {"format":"ANTI-MURPHY-WORKSPACE","version":24,"stations":stations,"orders":orders,"decision_history":clean_hist}
