from __future__ import annotations

from typing import Any, Dict, List

from simulation.metrics import compare_results, murphy_score


def _station_map(result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(x.get("Posto")): x for x in result.get("stations", [])}


def resilience_index(result: Dict[str, Any]) -> Dict[str, Any]:
    """Índice explicável de robustez operacional (0–100).

    É deliberadamente simples e auditável: combina SLA, qualidade Murphy,
    desbalanceamento e pressão do gargalo. Não é uma previsão estatística do
    mundo real; é um índice comparativo dentro do modelo.
    """
    sla = max(0.0, min(100.0, float(result.get("sla_pct", 0))))
    quality = max(0.0, min(100.0, float(murphy_score(result))))
    balance = max(0.0, min(100.0, float(result.get("balance_loss_pp", 0))))
    smap = _station_map(result)
    bottleneck = smap.get(str(result.get("bottleneck")), {})
    wait = max(0.0, float(bottleneck.get("Espera média (min)", 0)))
    queue = max(0.0, float(bottleneck.get("Fila máx.", 0)))
    pressure_penalty = min(100.0, wait * 1.2 + queue * 3.0)

    score = (
        0.42 * sla
        + 0.28 * quality
        + 0.16 * (100.0 - balance)
        + 0.14 * (100.0 - pressure_penalty)
    )
    score = round(max(0.0, min(100.0, score)), 1)
    if score >= 80:
        band = "ROBUSTO"
    elif score >= 60:
        band = "ATENÇÃO"
    elif score >= 40:
        band = "FRÁGIL"
    else:
        band = "CRÍTICO"
    return {
        "score": score,
        "band": band,
        "components": {
            "SLA": round(sla, 1),
            "Saúde Murphy (maior é melhor)": round(quality, 1),
            "Desbalanceamento": round(balance, 1),
            "Pressão do gargalo": round(pressure_penalty, 1),
        },
    }


def copilot_recommendations(result: Dict[str, Any], stations: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gera recomendações explicáveis a partir do estado simulado.

    O nome 'Copilot' é intencional: são heurísticas transparentes, não uma IA
    generativa opaca. Cada sugestão vem acompanhada do sinal que a motivou.
    """
    rows = result.get("stations", [])
    if not rows:
        return []
    smap = _station_map(result)
    bn = str(result.get("bottleneck", rows[0].get("Posto")))
    b = smap.get(bn, rows[0])
    cfg = stations.get(bn, {})
    util = float(b.get("Utilização máquina (%)", 0))
    wutil = float(b.get("Utilização mão de obra (%)", 0))
    wait = float(b.get("Espera média (min)", 0))
    queue = int(b.get("Fila máx.", 0))
    machines = int(b.get("Máquinas", cfg.get("maquinas", 1)))
    workers = int(b.get("Operadores", cfg.get("operadores", 0)))
    op_per_machine = float(cfg.get("operadores_por_maquina", 1.0) or 1.0)
    required_workers = max(1.0, machines * op_per_machine)

    recs: List[Dict[str, Any]] = []

    if workers < required_workers or wutil >= 88:
        recs.append({
            "priority": 1,
            "title": f"Teste +1 operador em {bn}",
            "why": f"Mão de obra em {wutil:.0f}% de utilização e {workers}/{required_workers:g} operadores para a capacidade nominal.",
            "action": "Murphy Lab · Δ operadores = +1",
            "confidence": min(96, int(58 + wutil * 0.35 + min(wait, 30) * 0.3)),
            "signal": "MÃO DE OBRA",
        })

    if util >= 82 or queue >= 4:
        recs.append({
            "priority": 1,
            "title": f"Teste +1 máquina em {bn}",
            "why": f"Utilização de máquina em {util:.0f}% com fila máxima de {queue} e espera média de {wait:.1f} min.",
            "action": "Murphy Lab · Δ máquinas = +1",
            "confidence": min(98, int(52 + util * 0.38 + min(queue, 10) * 1.2)),
            "signal": "CAPACIDADE",
        })

    if float(result.get("sla_pct", 0)) < 85:
        recs.append({
            "priority": 2,
            "title": "Compare EDD contra a regra atual",
            "why": f"O SLA atual é {float(result.get('sla_pct', 0)):.0f}%. Priorizar prazos pode reduzir atrasos mesmo sem comprar recurso.",
            "action": "Murphy Lab · Regra de despacho = EDD",
            "confidence": 78,
            "signal": "PRAZO",
        })

    if float(result.get("balance_loss_pp", 0)) >= 35:
        low = min(rows, key=lambda x: float(x.get("Utilização máquina (%)", 0)))
        recs.append({
            "priority": 2,
            "title": f"Investigue realocação entre {low.get('Posto')} e {bn}",
            "why": f"O desbalanceamento entre postos é {float(result.get('balance_loss_pp', 0)):.0f} p.p.; há capacidade relativamente ociosa em {low.get('Posto')}.",
            "action": "Opportunity Engine · testar realocação",
            "confidence": 73,
            "signal": "BALANCEAMENTO",
        })

    recs.append({
        "priority": 3,
        "title": f"Estresse {bn} antes de investir",
        "why": "Uma melhoria local pode apenas transferir o gargalo. Rode a bateria de estresse para observar robustez e migração da restrição.",
        "action": "Stress Lab · 24+ cenários",
        "confidence": 70,
        "signal": "RISCO",
    })

    recs.sort(key=lambda x: (x["priority"], -x["confidence"]))
    return recs[:4]


def explain_comparison(base: Dict[str, Any], alt: Dict[str, Any]) -> Dict[str, Any]:
    d = compare_results(base, alt)
    bmap = _station_map(base)
    amap = _station_map(alt)
    old_bn = str(base.get("bottleneck", "-"))
    new_bn = str(alt.get("bottleneck", "-"))
    old = bmap.get(old_bn, {})
    new_same = amap.get(old_bn, {})

    wait_before = float(old.get("Espera média (min)", 0))
    wait_after = float(new_same.get("Espera média (min)", 0))
    wait_delta = wait_after - wait_before
    queue_before = int(old.get("Fila máx.", 0))
    queue_after = int(new_same.get("Fila máx.", 0))

    if d["throughput_pct"] > 1:
        headline = "A decisão destravou capacidade do sistema."
    elif d["throughput_pct"] < -1:
        headline = "A decisão reduziu a capacidade efetiva do sistema."
    else:
        headline = "A decisão mudou pouco o throughput global."

    causes = []
    if abs(wait_delta) >= 1:
        verb = "caiu" if wait_delta < 0 else "subiu"
        causes.append(f"A espera no antigo gargalo {old_bn} {verb} de {wait_before:.1f} para {wait_after:.1f} min.")
    if queue_before != queue_after:
        causes.append(f"A fila máxima em {old_bn} passou de {queue_before} para {queue_after} unidades.")
    if old_bn != new_bn:
        causes.append(f"A restrição migrou de {old_bn} para {new_bn}; isso indica que o sistema respondeu à intervenção e criou um novo limite operacional.")
    else:
        causes.append(f"O gargalo permaneceu em {old_bn}; a intervenção ainda não eliminou a principal restrição.")

    if d["unit_cost_pct"] < -1:
        causes.append(f"O custo unitário caiu {abs(d['unit_cost_pct']):.1f}%, sugerindo melhor diluição do custo operacional no cenário simulado.")
    elif d["unit_cost_pct"] > 1:
        causes.append(f"O custo unitário subiu {d['unit_cost_pct']:.1f}%; o ganho operacional deve ser confrontado com esse aumento antes da implementação.")

    return {
        "headline": headline,
        "causes": causes[:4],
        "delta": d,
        "bottleneck_migrated": old_bn != new_bn,
        "old_bottleneck": old_bn,
        "new_bottleneck": new_bn,
    }


def propagation_levels(result: Dict[str, Any], source_sid: str | None = None) -> List[Dict[str, Any]]:
    rows = result.get("stations", [])
    source_sid = str(source_sid or result.get("bottleneck", ""))
    if not rows:
        return []
    ids = [str(r.get("Posto")) for r in rows]
    try:
        src_idx = ids.index(source_sid)
    except ValueError:
        src_idx = 0
    out = []
    for i, r in enumerate(rows):
        util = float(r.get("Utilização máquina (%)", 0))
        wait = float(r.get("Espera média (min)", 0))
        queue = float(r.get("Fila máx.", 0))
        distance = abs(i - src_idx)
        operational = min(100.0, util * 0.58 + min(wait, 50) * 0.9 + min(queue, 15) * 2.2)
        propagated = max(0.0, 100.0 - distance * 18.0)
        impact = round(min(100.0, 0.7 * operational + 0.3 * propagated), 1)
        out.append({
            "Posto": str(r.get("Posto")),
            "Nome": str(r.get("Nome", r.get("Posto"))),
            "impact": impact,
            "distance": distance,
            "source": i == src_idx,
            "wait": wait,
            "queue": int(queue),
            "util": util,
        })
    return out
