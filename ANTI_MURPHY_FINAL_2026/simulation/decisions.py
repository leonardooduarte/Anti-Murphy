from __future__ import annotations

from copy import deepcopy
from itertools import islice
from typing import Dict, Any, List, Tuple

from simulation.factory import ScenarioConfig
from simulation.engine import run_simulation
from simulation.metrics import compare_results


def _opportunity_candidates(base_config):
    """Build only candidates requested by the caller, in the historical order."""

    for sid in base_config.stations:
        c = base_config.clone(name=f"+1 operador em {sid}")
        c.stations[sid]["operadores"] += 1
        yield c.name, c, f"Adicionar 1 operador em {sid}"

        c2 = base_config.clone(name=f"+1 máquina em {sid}")
        c2.stations[sid]["maquinas"] += 1
        yield c2.name, c2, f"Adicionar 1 posto/máquina em {sid}"

    # Realocações: tira 1 operador de um posto com folga e leva a outro.
    for src in base_config.stations:
        if base_config.stations[src]["operadores"] <= 1:
            continue
        for dst in base_config.stations:
            if src == dst:
                continue
            c = base_config.clone(name=f"Realocar {src} → {dst}")
            c.stations[src]["operadores"] -= 1
            c.stations[dst]["operadores"] += 1
            yield c.name, c, f"Realocar 1 operador de {src} para {dst}"


    # Melhorias de processo: reduzir setup em 25% quando houver setup relevante.
    for sid, stn in base_config.stations.items():
        setup = float(stn.get("setup_min", 0) or 0)
        if setup >= 4:
            c = base_config.clone(name=f"-25% setup em {sid}")
            c.stations[sid]["setup_min"] = max(0.0, setup * 0.75)
            yield c.name, c, f"Reduzir setup em 25% em {sid}"

    # Regras de despacho são contrafactuais de baixo custo e alto valor gerencial.
    for rule in ["EDD", "SPT", "FIFO"]:
        if rule != base_config.dispatch_rule:
            c = base_config.clone(name=f"Despacho {rule}")
            c.dispatch_rule = rule
            yield c.name, c, f"Alterar regra de despacho para {rule}"

def generate_opportunities(base_config: ScenarioConfig, base_result: Dict[str, Any], max_candidates: int = 36) -> List[Dict[str, Any]]:
    """Quantify the same finite candidates without constructing discarded models."""
    candidates = _opportunity_candidates(base_config)
    selected = islice(candidates, max_candidates) if max_candidates >= 0 else list(candidates)[:max_candidates]
    rows = []
    for name, cfg, action in selected:
        r = run_simulation(cfg)
        if not r.get("feasible",True):
            continue  # Sem postos funcionais, não existem métricas econômicas para ranquear.
        d = compare_results(base_result, r)
        # Índice de oportunidade: valoriza throughput/SLA e penaliza custo unitário.
        score = d["throughput_pct"] * 1.5 + d["sla_pp"] * 0.8 - max(0.0, d["unit_cost_pct"]) * 0.7
        rows.append({
            "Ação": action,
            "Cenário": name,
            "Throughput Δ (%)": round(d["throughput_pct"], 1),
            "SLA Δ (p.p.)": round(d["sla_pp"], 1),
            "Custo/un Δ (%)": round(d["unit_cost_pct"], 1),
            "Makespan Δ (%)": round(d["makespan_pct"], 1),
            "Score de oportunidade": round(score, 1),
            "result": r,
            "config": cfg,
        })
    return sorted(rows, key=lambda x: x["Score de oportunidade"], reverse=True)
