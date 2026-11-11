from __future__ import annotations

from copy import deepcopy
from math import exp
from typing import Any, Dict, List

from simulation.engine import run_simulation
from simulation.factory import ScenarioConfig
from simulation.metrics import compare_results


def scheduling_benchmark(base_config: ScenarioConfig) -> List[Dict[str, Any]]:
    """Compare dispatching rules using the exact same model and seed.

    This is deterministic with respect to the chosen seed/model; it is a policy benchmark,
    not an optimization guarantee.
    """
    rows: List[Dict[str, Any]] = []
    for rule in ["EDD", "SPT", "FIFO"]:
        cfg = base_config.clone(name=f"Scheduling · {rule}")
        cfg.dispatch_rule = rule
        result = run_simulation(cfg)
        rows.append({
            "rule": rule,
            "throughput": float(result.get("throughput_h", 0)),
            "sla": float(result.get("sla_pct", 0)),
            "makespan": float(result.get("makespan_h", 0)),
            "unit_cost": float(result.get("unit_cost", 0)),
            "penalty": float(result.get("penalty_total", 0)),
            "bottleneck": str(result.get("bottleneck", "-")),
            "result": result,
            "config": cfg,
        })
    return rows


def calibration_summary(base_result: Dict[str, Any], real: Dict[str, float]) -> Dict[str, Any]:
    """Compare simulated KPIs to user-supplied real observations.

    No parameter fitting is performed here; this is a transparent validation snapshot.
    """
    specs = [
        ("throughput", "throughput_h", "Throughput", False),
        ("sla", "sla_pct", "SLA", False),
        ("makespan", "makespan_h", "Makespan", True),
        ("unit_cost", "unit_cost", "Custo/un", True),
    ]
    rows=[]
    errors=[]
    for key, result_key, label, lower_better in specs:
        rv = real.get(key)
        sim = float(base_result.get(result_key, 0) or 0)
        if rv is None or float(rv) <= 0:
            continue
        rv=float(rv)
        err_pct = 100.0 * (sim-rv) / rv
        abs_err = abs(err_pct)
        errors.append(abs_err)
        rows.append({"metric":label,"real":rv,"simulated":sim,"error_pct":err_pct,"abs_error_pct":abs_err,"lower_better":lower_better})
    mape = sum(errors)/len(errors) if errors else None
    if mape is None:
        score=None; band="NO DATA"
    else:
        score=max(0.0, min(100.0, 100.0-mape*2.0))
        band="HIGH" if score>=85 else ("MEDIUM" if score>=65 else "LOW")
    return {"rows":rows,"mape":mape,"score":score,"band":band}


def reliability_analysis(stations: Dict[str, Dict[str, Any]], reliability_inputs: Dict[str, Dict[str, float]], horizon_h: float, downtime_cost_h: float) -> List[Dict[str, Any]]:
    """Simple reliability lens using exponential time-to-failure assumptions.

    MTBF/MTTR are provided by the user. Availability already stored in the model is shown
    as context but is not silently converted to failure distributions.
    """
    rows=[]
    H=max(0.1,float(horizon_h))
    cost=max(0.0,float(downtime_cost_h))
    for sid,s in stations.items():
        inp=reliability_inputs.get(sid,{})
        mtbf=max(0.1,float(inp.get("mtbf_h", 120.0)))
        mttr=max(0.0,float(inp.get("mttr_h", 3.0)))
        p_fail=1.0-exp(-H/mtbf)
        expected_failures=H/mtbf
        expected_downtime=expected_failures*mttr
        exposure=expected_downtime*cost
        # Transparent risk score: probability dominates, repair duration adds severity.
        risk=min(100.0, p_fail*70.0 + min(mttr/12.0,1.0)*30.0)
        rows.append({
            "station":sid,"name":s.get("nome",sid),"mtbf_h":mtbf,"mttr_h":mttr,
            "availability_model":float(s.get("disponibilidade",1.0))*100.0,
            "failure_probability":p_fail*100.0,"expected_failures":expected_failures,
            "expected_downtime_h":expected_downtime,"downtime_exposure":exposure,"risk_score":risk,
        })
    return sorted(rows,key=lambda x:x["risk_score"],reverse=True)


def skill_coverage(stations: Dict[str, Dict[str, Any]], skills: Dict[str, List[str]]) -> Dict[str, Any]:
    """Summarize cross-training coverage from a user-maintained skill map."""
    station_ids=list(stations)
    coverage={sid:0 for sid in station_ids}
    for _, station_list in skills.items():
        for sid in set(station_list):
            if sid in coverage:
                coverage[sid]+=1
    gaps=[sid for sid,n in coverage.items() if n==0]
    single=[sid for sid,n in coverage.items() if n==1]
    avg=(sum(coverage.values())/len(coverage)) if coverage else 0.0
    score=min(100.0, avg/2.0*100.0) if coverage else 0.0
    return {"coverage":coverage,"gaps":gaps,"single_points":single,"avg_qualified":avg,"score":score}


def pareto_frontier(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Non-dominated rows for throughput↑, SLA↑, unit cost↓, makespan↓."""
    clean=[]
    for r in rows:
        if not r: continue
        clean.append(r)
    frontier=[]
    for a in clean:
        dominated=False
        for b in clean:
            if a is b: continue
            no_worse=(float(b.get("throughput",0))>=float(a.get("throughput",0)) and
                      float(b.get("sla",0))>=float(a.get("sla",0)) and
                      float(b.get("unit_cost",1e18))<=float(a.get("unit_cost",1e18)) and
                      float(b.get("makespan",1e18))<=float(a.get("makespan",1e18)))
            strict=(float(b.get("throughput",0))>float(a.get("throughput",0)) or
                    float(b.get("sla",0))>float(a.get("sla",0)) or
                    float(b.get("unit_cost",1e18))<float(a.get("unit_cost",1e18)) or
                    float(b.get("makespan",1e18))<float(a.get("makespan",1e18)))
            if no_worse and strict:
                dominated=True; break
        if not dominated:
            frontier.append(a)
    return frontier
