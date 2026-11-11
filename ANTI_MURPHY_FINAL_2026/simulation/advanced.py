from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from simulation.engine import run_simulation
from simulation.numeric import metric
from simulation.metrics import compare_results
from simulation.factory import ScenarioConfig, TimedAction


def _metric_or_zero(result, key):
    # Preserve optional legacy packets; live engine results also carry `precise`.
    return metric(result, key) if key in result else 0.0


def operating_alerts(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gera alertas explicáveis e ordenados por severidade a partir do cenário."""
    rows = result.get("stations", [])
    alerts: List[Dict[str, Any]] = []
    for row in rows:
        sid = str(row.get("Posto", "-"))
        name = str(row.get("Nome", sid))
        util = float(row.get("Utilização máquina (%)", 0))
        wait = float(row.get("Espera média (min)", 0))
        queue = int(row.get("Fila máx.", 0))
        if queue >= 20 or wait >= 120:
            alerts.append({"level":"CRÍTICO","station":sid,"title":f"Pressão severa em {sid}","detail":f"{name}: fila {queue} e espera média {wait:.1f} min.","score":100 + queue + min(wait,300)/10})
        elif queue >= 5 or wait >= 30 or util >= 85:
            alerts.append({"level":"ATENÇÃO","station":sid,"title":f"Capacidade tensionada em {sid}","detail":f"Utilização {util:.0f}%, fila {queue}, espera {wait:.1f} min.","score":60 + queue + util/10})
        elif util <= 35 and queue == 0:
            alerts.append({"level":"OPORTUNIDADE","station":sid,"title":f"Folga operacional em {sid}","detail":f"Utilização de {util:.0f}% sem fila relevante; avalie realocação antes de contratar.","score":20 + (35-util)})
    if float(_metric_or_zero(result, 'sla_pct')) < 80:
        alerts.append({"level":"CRÍTICO","station":"SLA","title":"Risco de prazo elevado","detail":f"SLA atual em {float(_metric_or_zero(result, 'sla_pct')):.0f}%; priorize experimentos de prazo e gargalo.","score":150-float(_metric_or_zero(result, 'sla_pct'))})
    return sorted(alerts, key=lambda x: x["score"], reverse=True)[:8]


def sensitivity_analysis(base_config: ScenarioConfig, base_result: Dict[str, Any], station_id: str, resource: str = "operadores", max_add: int = 4) -> List[Dict[str, Any]]:
    """Curva de ganho marginal ao adicionar recursos a um posto."""
    rows: List[Dict[str, Any]] = []
    prev_tp = float(_metric_or_zero(base_result, 'throughput_h'))
    for add in range(0, max(0, int(max_add)) + 1):
        if add == 0:
            r = base_result
        else:
            cfg = base_config.clone(name=f"Sensibilidade {station_id} +{add} {resource}")
            if resource == "maquinas":
                cfg.stations[station_id]["maquinas"] = max(1, int(cfg.stations[station_id].get("maquinas", 1)) + add)
            else:
                cfg.stations[station_id]["operadores"] = max(0, int(cfg.stations[station_id].get("operadores", 0)) + add)
            r = run_simulation(cfg)
        tp = float(_metric_or_zero(r, 'throughput_h'))
        d = compare_results(base_result, r)
        marginal = 0.0 if add == 0 else (tp - prev_tp)
        rows.append({
            "Adição": add,
            "Throughput": tp,
            "SLA": float(_metric_or_zero(r, 'sla_pct')),
            "Custo/un": float(_metric_or_zero(r, 'unit_cost')),
            "Makespan": float(_metric_or_zero(r, 'makespan_h')),
            "Ganho marginal TP": marginal,
            "Throughput Δ (%)": float(d.get("throughput_pct", 0)),
            "Gargalo": str(r.get("bottleneck", "-")),
            "result": r,
        })
        prev_tp = tp
    return rows


def demand_breakpoint(base_config: ScenarioConfig, sla_floor: float = 80.0, demand_start: float = 1.0, demand_stop: float = 2.0, step: float = 0.05) -> Dict[str, Any]:
    """Aumenta demanda até encontrar o primeiro ponto em que o SLA cai abaixo do piso."""
    points: List[Dict[str, Any]] = []
    x = demand_start
    first_break = None
    while x <= demand_stop + 1e-9:
        cfg = base_config.clone(name=f"Ruptura demanda {x:.2f}x")
        cfg.demand_multiplier = round(x, 2)
        r = run_simulation(cfg)
        row = {"Demanda x":round(x,2),"SLA":float(_metric_or_zero(r, 'sla_pct')),"Throughput":float(_metric_or_zero(r, 'throughput_h')),"Makespan":float(_metric_or_zero(r, 'makespan_h')),"Gargalo":str(r.get("bottleneck","-")),"result":r}
        points.append(row)
        if first_break is None and row["SLA"] < sla_floor:
            first_break = row
        x += step
    last_safe = None
    for row in points:
        if row["SLA"] >= sla_floor:
            last_safe = row
    return {"points":points,"first_break":first_break,"last_safe":last_safe,"sla_floor":sla_floor}


def absentee_breakpoint(base_config: ScenarioConfig, station_id: str, sla_floor: float = 80.0, max_absent: int = 5) -> Dict[str, Any]:
    """Testa ausências crescentes em um posto e encontra o primeiro nível de ruptura."""
    points=[]
    first_break=None
    workers=int(base_config.stations[station_id].get("operadores",0))
    upper=min(max_absent, max(0, workers))
    for n in range(0, upper+1):
        cfg=base_config.clone(name=f"Ausência {n} em {station_id}")
        cfg.absent_workers={station_id:n} if n else {}
        r=run_simulation(cfg)
        row={"Ausências":n,"SLA":float(_metric_or_zero(r, 'sla_pct')),"Throughput":float(_metric_or_zero(r, 'throughput_h')),"Makespan":float(_metric_or_zero(r, 'makespan_h')),"Gargalo":str(r.get("bottleneck","-")),"result":r}
        points.append(row)
        if first_break is None and row["SLA"] < sla_floor:
            first_break=row
    return {"points":points,"first_break":first_break,"sla_floor":sla_floor,"station":station_id}


def portfolio_summary(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Seleciona destaques do histórico sem impor uma decisão única ao usuário."""
    if not history:
        return {}
    best_tp=max(history,key=lambda x:float(x.get("throughput",0)))
    best_sla=max(history,key=lambda x:float(x.get("sla",0)))
    best_cost=min(history,key=lambda x:float(x.get("unit_cost",1e18)))
    best_time=min(history,key=lambda x:float(x.get("makespan",1e18)))
    return {"throughput":best_tp,"sla":best_sla,"cost":best_cost,"makespan":best_time}


def recovery_plan(crisis_config: ScenarioConfig, crisis_result: Dict[str, Any],
                  max_results: int = 5, action_at_h: float | None = None) -> List[Dict[str, Any]]:
    """Compare post-incident *timed* capacity/dispatch responses.

    No candidate edits the initial ScenarioConfig; identical runs share a
    physical history up to the action (including work already in progress).
    These are operational, not pre-installed structural-capacity scenarios.
    """
    from math import isfinite
    instant = (float(crisis_config.chaos_start_h) + 2.0
               if action_at_h is None else float(action_at_h))
    if not isfinite(instant) or instant < 0:
        raise ValueError('Instante de resposta inválido.')
    affected = str(crisis_config.chaos_station or crisis_result.get('bottleneck', ''))
    bn = str(crisis_result.get('bottleneck', affected))
    candidates: List[TimedAction] = []
    for sid in dict.fromkeys([affected, bn]):
        if sid not in crisis_config.stations:
            continue
        candidates.append(TimedAction(instant, f'+1 operador em {sid}', workers_delta={sid:1}))
        candidates.append(TimedAction(instant, f'+1 máquina em {sid}', machines_delta={sid:1}))
    if crisis_config.dispatch_rule != 'EDD':
        candidates.append(TimedAction(instant, 'priorizar EDD', dispatch_rule='EDD'))
    rows=[]
    for action in candidates:
        result=run_simulation(crisis_config, action=action)
        if not result.get('feasible', True):
            continue
        d=compare_results(crisis_result,result)
        score=(float(d.get('sla_pp',0))*2.4 + float(d.get('throughput_pct',0))*1.1
               - float(d.get('makespan_pct',0))*.7 - max(0,float(d.get('unit_cost_pct',0)))*.35)
        rows.append({
            'Ação':action.label,
            'SLA':float(_metric_or_zero(result, 'sla_pct')),
            'SLA Δ (p.p.)':round(float(d.get('sla_pp',0)),1),
            'Throughput':float(_metric_or_zero(result, 'throughput_h')),
            'Throughput Δ (%)':round(float(d.get('throughput_pct',0)),1),
            'Makespan':float(result.get('makespan_h',0)),  # legacy table presentation
            'Custo/un':float(_metric_or_zero(result, 'unit_cost')),
            'Custo cenário (R$)':float(_metric_or_zero(result, 'total_cost')),
            'Investimento adicional (R$)':None,  # No calibration available.
            'Solicitação (h)':instant,
            'Efetivação (h)':result.get('intervention',{}).get('effective_h'),
            'Recovery score':score,
            'Gargalo':str(result.get('bottleneck','-')),
            'result':result,
            'config':crisis_config,
            'action':action,
        })
    rows.sort(key=lambda x:(-x['Recovery score'],-x['SLA'],x['Custo/un']))
    for row in rows:
        row['Recovery score']=round(row['Recovery score'],1)
    return rows[:max_results]


def monte_carlo_analysis(config: ScenarioConfig, runs: int = 12, seed_start: int = 2100) -> Dict[str, Any]:
    """Repete o mesmo cenário com sementes diferentes e resume incerteza simulada.

    A variabilidade vem do tempo de processo triangular já usado pelo motor. O resultado
    não representa incerteza do mundo real; é uma medida de dispersão interna do modelo.
    """
    import math
    import statistics

    runs = max(4, min(60, int(runs)))
    rows: List[Dict[str, Any]] = []
    for i in range(runs):
        cfg = config.clone(name=f"{config.name} · MC {i+1:02d}")
        cfg.seed = int(seed_start) + i
        r = run_simulation(cfg)
        rows.append({
            "run": i + 1,
            "seed": cfg.seed,
            "throughput": float(_metric_or_zero(r, 'throughput_h')),
            "sla": float(_metric_or_zero(r, 'sla_pct')),
            "makespan": float(_metric_or_zero(r, 'makespan_h')),
            "unit_cost": float(_metric_or_zero(r, 'unit_cost')),
            "bottleneck": str(r.get("bottleneck", "-")),
        })

    def metric_summary(key: str) -> Dict[str, float]:
        vals = [float(x[key]) for x in rows]
        mean = statistics.fmean(vals) if vals else 0.0
        sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
        half = 1.96 * sd / math.sqrt(len(vals)) if vals else 0.0
        sv = sorted(vals)
        def pct(p: float) -> float:
            if not sv: return 0.0
            pos = (len(sv)-1) * p
            lo = int(math.floor(pos)); hi = int(math.ceil(pos))
            if lo == hi: return sv[lo]
            return sv[lo] + (sv[hi]-sv[lo]) * (pos-lo)
        return {"mean": mean, "sd": sd, "ci_low": mean-half, "ci_high": mean+half,
                "p10": pct(.10), "p50": pct(.50), "p90": pct(.90)}

    bn_counts: Dict[str, int] = {}
    for x in rows:
        bn_counts[x["bottleneck"]] = bn_counts.get(x["bottleneck"], 0) + 1
    dominant_bn = max(bn_counts, key=bn_counts.get) if bn_counts else "-"
    return {
        "runs": rows,
        "summary": {k: metric_summary(k) for k in ["throughput", "sla", "makespan", "unit_cost"]},
        "dominant_bottleneck": dominant_bn,
        "bottleneck_share": (bn_counts.get(dominant_bn, 0) / max(1, len(rows))) * 100,
    }


def resilience_surface(base_config: ScenarioConfig, station_id: str, demand_levels: List[float], absent_levels: List[int], sla_floor: float = 80.0) -> Dict[str, Any]:
    """Cria uma pequena superfície demanda × ausências para leitura de fronteira operacional."""
    points: List[Dict[str, Any]] = []
    for a in absent_levels:
        for d in demand_levels:
            cfg = base_config.clone(name=f"Fronteira {station_id} · {d:.2f}x · abs {a}")
            cfg.demand_multiplier = float(d)
            cfg.absent_workers = {station_id: int(a)} if int(a) > 0 else {}
            r = run_simulation(cfg)
            points.append({
                "station": station_id,
                "demand": round(float(d), 2),
                "absent": int(a),
                "sla": float(_metric_or_zero(r, 'sla_pct')),
                "throughput": float(_metric_or_zero(r, 'throughput_h')),
                "makespan": float(_metric_or_zero(r, 'makespan_h')),
                "unit_cost": float(_metric_or_zero(r, 'unit_cost')),
                "bottleneck": str(r.get("bottleneck", "-")),
                "safe": float(_metric_or_zero(r, 'sla_pct')) >= float(sla_floor),
            })
    safe = [p for p in points if p["safe"]]
    return {"points": points, "safe_count": len(safe), "total": len(points), "sla_floor": float(sla_floor), "station": station_id}


def model_confidence(stations: Dict[str, Any], orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Confiança no cadastro ≠ validação com dados fabris.

    Endereça o falso 100/100 quando um roteiro aponta para um posto inexistente.
    Não há evidências de calibração, logo 100/100 significa apenas cadastro íntegro.
    """
    from simulation.validation import validate_model
    issues=validate_model(stations,orders)
    checks: List[tuple[str,bool,int]]=[]
    checks.append(("postos cadastrados",len(stations)>=2,10))
    checks.append(("ordens cadastradas",len(orders)>=1,10))
    checks.append(("custos preenchidos",bool(stations) and all(float(s.get('custo_maquina_h',0))>=0 and float(s.get('custo_operador_h',0))>=0 for s in stations.values()),15))
    checks.append(("disponibilidade válida",bool(stations) and all(0<float(s.get('disponibilidade',0))<=1 for s in stations.values()),10))
    checks.append(("eficiência válida",bool(stations) and all(float(s.get('eficiencia_operador',0))>0 for s in stations.values()),10))
    checks.append(("roteiros com postos e tempos válidos",bool(orders) and all(
        o.get('route') and all(isinstance(step,(list,tuple)) and len(step)==2 and step[0] in stations
                          and float(step[1])>0 for step in o['route']) for o in orders),25))
    checks.append(("prazos e quantidades",bool(orders) and all(float(o.get('prazo_h',0))>0 and int(o.get('quantidade',0))>0 for o in orders),15))
    checks.append(("cadastro sem erros",not issues,5))
    score=sum(w for _,ok,w in checks if ok)
    if issues:
        score=min(score,60)  # Erros invalidam classificação HIGH, mesmo com muitos campos preenchidos.
    missing=[label for label,ok,_ in checks if not ok]+issues
    band="HIGH" if score>=85 else ("MEDIUM" if score>=65 else "LOW")
    return {'score':score,'band':band,'missing':missing,'checks':checks,
            'validation_errors':issues,'calibration':'NÃO COMPROVADA',
            'notice':'Nota de completude do cadastro; não é probabilidade de previsão correta.'}
