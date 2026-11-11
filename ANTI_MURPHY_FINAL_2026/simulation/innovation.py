from __future__ import annotations

from copy import deepcopy
from math import isfinite
import random
from typing import Any, Dict, List

from simulation.engine import run_simulation
from simulation.numeric import metric, product_ratio, present
from simulation.metrics import compare_results
from simulation.factory import ScenarioConfig


def stress_test(
    base_config: ScenarioConfig,
    runs: int = 24,
    max_absent: int = 1,
    demand_low: float = 0.9,
    demand_high: float = 1.3,
    durations: tuple[float, ...] = (1.5, 3.0, 5.0),
    seed: int = 2026,
) -> Dict[str, Any]:
    """Executa uma bateria determinística de cenários de estresse.

    Não tenta prever o mundo real. O objetivo é comparar a robustez relativa do
    modelo sob perturbações coerentes com o próprio motor de simulação.
    """
    rng = random.Random(seed)
    station_ids = list(base_config.stations.keys())
    rows: List[Dict[str, Any]] = []
    station_hits = {sid: [] for sid in station_ids}

    for i in range(max(1, int(runs))):
        cfg = base_config.clone(name=f"Stress {i+1:02d}")
        sid = rng.choice(station_ids)
        cfg.seed = seed + i + 1
        cfg.demand_multiplier = round(rng.uniform(demand_low, demand_high), 2)
        cfg.chaos_station = sid
        cfg.chaos_start_h = round(rng.uniform(1.0, 12.0), 1)
        cfg.chaos_duration_h = float(rng.choice(durations))
        absent = rng.randint(0, max(0, int(max_absent)))
        cfg.absent_workers = {sid: absent} if absent else {}
        result = run_simulation(cfg)
        row = {
            "Run": i + 1,
            "feasible":bool(result.get("feasible",True)),
            "reason":"; ".join(result.get("warnings",[])) if not result.get("feasible",True) else "",
            "Posto afetado": sid,
            "Demanda x": cfg.demand_multiplier,
            "Parada (h)": cfg.chaos_duration_h,
            "Ausências": absent,
            "Throughput": metric(result, "throughput_h") if result.get("feasible",True) else None,
            "SLA": metric(result, "sla_pct") if result.get("feasible",True) else None,
            "Makespan": metric(result, "makespan_h") if result.get("feasible",True) else None,
            "Custo/un": metric(result, "unit_cost") if result.get("feasible",True) else None,
            "Gargalo": result["bottleneck"],
            "result": result,
            "config": cfg,
        }
        rows.append(row)
        station_hits[sid].append(row)

    def avg(xs, key):
        vals = [float(x[key]) for x in xs if x["feasible"]]
        return sum(vals) / len(vals) if vals else None

    fragility = []
    for sid, items in station_hits.items():
        if not items:
            continue
        # Mais espera/queda de SLA e makespan alto => maior fragilidade.
        mean_sla = avg(items, "SLA")
        mean_mk = avg(items, "Makespan")
        mean_tp = avg(items, "Throughput")
        score = ((100 - mean_sla) * 0.52 + mean_mk * 0.85 + (1 / max(mean_tp, 0.01)) * 7) if mean_sla is not None else None
        fragility.append({
            "Posto": sid,
            "Índice de fragilidade": round(score, 1) if score is not None else None,
            "SLA médio": round(mean_sla, 1) if mean_sla is not None else None,
            "Makespan médio": present(mean_mk, 1) if mean_mk is not None else None,
            "Throughput médio": present(mean_tp, 2) if mean_tp is not None else None,
            "Cenários": len(items),
            "Viáveis":sum(x["feasible"] for x in items),
            "Inviáveis":sum(not x["feasible"] for x in items),
            "Taxa inviáveis (%)":100*sum(not x["feasible"] for x in items)/len(items),
        })
    fragility.sort(key=lambda x: (x["Taxa inviáveis (%)"],x["Índice de fragilidade"] if x["Índice de fragilidade"] is not None else -1), reverse=True)

    viable=[x for x in rows if x["feasible"]]
    slas = sorted(float(x["SLA"]) for x in viable)
    makespans = sorted(float(x["Makespan"]) for x in viable)
    unit_costs = sorted(float(x["Custo/un"]) for x in viable)
    throughputs = sorted(float(x["Throughput"]) for x in viable)

    def percentile(vals, p):
        if not vals:
            return None
        idx = min(len(vals) - 1, max(0, round((len(vals) - 1) * p)))
        return vals[idx]

    summary = {
        "runs": len(rows),
        "viable_runs":len(viable),"infeasible_runs":len(rows)-len(viable),
        "statistics_scope":"viable_only",
        "infeasible_rate":100*(len(rows)-len(viable))/len(rows),
        "sla_avg": round(sum(slas) / len(slas), 1) if slas else None,
        "sla_worst": round(min(slas), 1) if slas else None,
        "makespan_p90": present(percentile(makespans, 0.90), 2) if makespans else None,
        "unit_cost_p90": present(percentile(unit_costs, 0.90), 2) if unit_costs else None,
        "throughput_p10": present(percentile(throughputs, 0.10), 3) if throughputs else None,
        "resilience_rate": round(100 * sum(1 for x in viable if x["SLA"] >= 80) / len(rows), 1),
        "most_fragile": fragility[0]["Posto"] if fragility else "-",
    }
    return {"summary": summary, "runs": rows, "fragility": fragility}


def goal_seek(
    base_config: ScenarioConfig,
    base_result: Dict[str, Any],
    target_throughput: float,
    target_sla: float,
    max_extra_workers: int = 3,
    max_extra_machines: int = 2,
    max_results: int = 12,
) -> List[Dict[str, Any]]:
    """Busca mudanças discretas simples capazes de atingir uma meta operacional.

    Explora ações de baixo grau (uma ou duas alterações) para manter o resultado
    explicável e apresentável ao gestor.
    """
    station_ids = list(base_config.stations.keys())
    candidates: List[ScenarioConfig] = []

    # Ações simples.
    for sid in station_ids:
        for w in range(1, max(0, int(max_extra_workers)) + 1):
            c = base_config.clone(name=f"+{w} op. em {sid}")
            c.stations[sid]["operadores"] += w
            candidates.append(c)
        for m in range(1, max(0, int(max_extra_machines)) + 1):
            c = base_config.clone(name=f"+{m} maq. em {sid}")
            c.stations[sid]["maquinas"] += m
            candidates.append(c)

    # Combinações pequenas focadas em pares de postos.
    for i, a in enumerate(station_ids):
        for b in station_ids[i + 1:]:
            if max_extra_workers >= 2:
                c = base_config.clone(name=f"+1 op. {a} +1 op. {b}")
                c.stations[a]["operadores"] += 1
                c.stations[b]["operadores"] += 1
                candidates.append(c)
            if max_extra_machines >= 1 and max_extra_workers >= 1:
                c = base_config.clone(name=f"+1 maq. {a} +1 op. {b}")
                c.stations[a]["maquinas"] += 1
                c.stations[b]["operadores"] += 1
                candidates.append(c)

    rows = []
    seen = set()
    for cfg in candidates:
        if cfg.name in seen:
            continue
        seen.add(cfg.name)
        r = run_simulation(cfg)
        d = compare_results(base_result, r)
        workers_added = sum(
            max(0, cfg.stations[s]["operadores"] - base_config.stations[s]["operadores"])
            for s in station_ids
        )
        machines_added = sum(
            max(0, cfg.stations[s]["maquinas"] - base_config.stations[s]["maquinas"])
            for s in station_ids
        )
        feasible = metric(r, "throughput_h") >= target_throughput and metric(r, "sla_pct") >= target_sla
        # Penaliza complexidade e custo, valoriza proximidade da meta quando inviável.
        gap = max(0.0, target_throughput - metric(r, "throughput_h")) * 22 + max(0.0, target_sla - metric(r, "sla_pct")) * 0.8
        complexity = workers_added * 2.0 + machines_added * 4.5
        score = (0 if feasible else 1000) + gap + complexity + max(0, d["unit_cost_pct"]) * 0.7
        rows.append({
            "Cenário": cfg.name,
            "Atinge meta": "Sim" if feasible else "Não",
            "Throughput": metric(r, "throughput_h"),
            "SLA": metric(r, "sla_pct"),
            "Custo/un": metric(r, "unit_cost"),
            "Makespan": metric(r, "makespan_h"),
            "Operadores +": workers_added,
            "Máquinas +": machines_added,
            "Throughput Δ (%)": round(d["throughput_pct"], 1),
            "SLA Δ (p.p.)": round(d["sla_pp"], 1),
            "Custo/un Δ (%)": round(d["unit_cost_pct"], 1),
            "score": score,
            "result": r,
            "config": cfg,
        })
    rows.sort(key=lambda x: (x["score"], x["Custo/un"], x["Máquinas +"], x["Operadores +"]))
    for row in rows:
        row["score"] = round(row["score"], 2)
    return rows[:max_results]


def finance_lens(base_result: Dict[str, Any], alt_result: Dict[str, Any], contribution_margin_per_unit: float, hours_per_day: float = 8.0, one_time_investment: float = 0.0) -> Dict[str, Any]:
    # Cost rates require an actual positive simulated horizon. An infeasible
    # zero-horizon result has no economic rate; do not invent one with a floor.
    if not all(isfinite(float(v)) for v in (contribution_margin_per_unit, hours_per_day, one_time_investment)):
        raise ValueError('Parâmetros financeiros devem ser finitos.')
    if hours_per_day < 0:
        raise ValueError('As horas por dia devem ser não negativas.')

    def daily_cost(result):
        horizon = metric(result, "makespan_h")
        if horizon <= 0:
            raise ValueError('O custo diário exige horizonte de simulação positivo.')
        cost = product_ratio([metric(result, "operating_cost"), hours_per_day],
                             [horizon], 'Custo diário')
        if not isfinite(cost):
            raise ValueError('Custo diário fora do intervalo numérico representável.')
        return cost

    delta_tp = metric(alt_result, "throughput_h") - metric(base_result, "throughput_h")
    extra_units_day = delta_tp * max(0.0, hours_per_day)
    extra_contribution_day = extra_units_day * max(0.0, contribution_margin_per_unit)
    base_daily_cost = daily_cost(base_result)
    alt_daily_cost = daily_cost(alt_result)
    incremental_cost_day = alt_daily_cost - base_daily_cost
    net_day = extra_contribution_day - incremental_cost_day
    if not all(isfinite(v) for v in (delta_tp, extra_units_day, extra_contribution_day, incremental_cost_day, net_day)):
        raise ValueError('Resultado financeiro fora do intervalo numérico representável.')
    payback_days = None
    if one_time_investment > 0 and net_day > 0:
        payback_days = one_time_investment / net_day
        if not isfinite(payback_days):
            raise ValueError('Payback fora do intervalo numérico representável.')
    return {
        "extra_units_day": round(extra_units_day, 2),
        "extra_contribution_day": round(extra_contribution_day, 2),
        "incremental_cost_day": round(incremental_cost_day, 2),
        "net_day": round(net_day, 2),
        "payback_days": None if payback_days is None else round(payback_days, 1),
    }
