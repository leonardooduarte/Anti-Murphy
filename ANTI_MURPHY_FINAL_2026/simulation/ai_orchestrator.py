from __future__ import annotations

from typing import Any, Dict, List, Optional

from simulation.intelligence import resilience_index, copilot_recommendations
from simulation.metrics import murphy_score
from simulation.decision_council import blocked_station_fixes


def _station_map(result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(x.get("Posto")): x for x in result.get("stations", [])}


def diagnose_operation(base: Dict[str, Any], stations: Dict[str, Dict[str, Any]], scenario: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    smap = _station_map(base)
    bn = str(base.get("bottleneck", "-"))
    bn_row = smap.get(bn, {})
    ri = resilience_index(base)
    blocked = blocked_station_fixes(stations, [{"route": [(r.get("Posto"), 1)]} for r in base.get("stations", [])])

    risks: List[Dict[str, Any]] = []
    if float(base.get("sla_pct", 0.0)) < 90:
        risks.append({"type": "service", "level": "high", "message": f"SLA em {base.get('sla_pct', 0):.0f}% exige ação para reduzir atrasos."})
    if float(base.get("balance_loss_pp", 0.0)) >= 30:
        risks.append({"type": "flow", "level": "medium", "message": f"Desbalanceamento de {base.get('balance_loss_pp', 0):.1f} p.p. sugere pressão localizada."})
    if float(base.get("penalty_total", 0.0)) > 0:
        risks.append({"type": "cost", "level": "high", "message": f"Penalidades simuladas de R$ {base.get('penalty_total', 0):,.2f} pressionam o custo total."})
    if ri.get("score", 0) < 60:
        risks.append({"type": "resilience", "level": "high", "message": f"Resiliência interna em {ri.get('score', 0):.0f}/100 indica fragilidade sistêmica."})

    narrative = [
        f"Gargalo atual: {bn} · {bn_row.get('Nome', stations.get(bn, {}).get('nome', bn))}.",
        f"Utilização de máquina: {float(bn_row.get('Utilização máquina (%)', 0)):.1f}% · Espera média: {float(bn_row.get('Espera média (min)', 0)):.1f} min · Fila máx.: {int(bn_row.get('Fila máx.', 0))}.",
        f"SLA: {float(base.get('sla_pct', 0)):.1f}% · Throughput: {float(base.get('throughput_h', 0)):.2f} un/h · Makespan: {float(base.get('makespan_h', 0)):.2f} h.",
        f"Murphy score: {float(murphy_score(base)):.1f}/100 · Resiliência: {ri.get('score', 0):.1f}/100 ({ri.get('band', '-')}).",
    ]
    if scenario:
        narrative.append(f"Cenário ativo: {scenario.get('name', 'Alternativo')} com gargalo em {scenario.get('bottleneck', '-')}.")

    return {
        "headline": f"A maior restrição do sistema está em {bn}.",
        "narrative": narrative,
        "risks": risks,
        "recommended_tests": copilot_recommendations(base, stations),
        "blocked_fixes": blocked,
        "resilience": ri,
        "constraint": {
            "station": bn,
            "name": bn_row.get("Nome", stations.get(bn, {}).get("nome", bn)),
            "machine_util_pct": float(bn_row.get("Utilização máquina (%)", 0)),
            "labor_util_pct": float(bn_row.get("Utilização mão de obra (%)", 0)),
            "avg_wait_min": float(bn_row.get("Espera média (min)", 0)),
            "max_queue": int(bn_row.get("Fila máx.", 0)),
        },
    }


def response_playbook(diagnosis: Dict[str, Any]) -> List[Dict[str, str]]:
    steps: List[Dict[str, str]] = [
        {"phase": "1 · Estabilizar", "goal": "Eliminar bloqueios e confirmar recursos mínimos do modelo.", "action": "Corrigir postos sem equipe ou com capacidade humana insuficiente antes de qualquer comparação econômica."},
        {"phase": "2 · Proteger serviço", "goal": "Atacar a restrição com maior impacto no SLA.", "action": "Simular primeiro intervenções focadas no gargalo atual e medir SLA, makespan e penalidades."},
        {"phase": "3 · Confirmar trade-offs", "goal": "Evitar uma economia aparente que destrua o nível de serviço.", "action": "Usar o Decision Evidence Studio com o mesmo incidente para comparar custo total + implantação, SLA e tempo."},
        {"phase": "4 · Handoff executivo", "goal": "Comunicar o porquê da decisão.", "action": "Resumir risco, alternativa escolhida, evidência, limite do modelo e próxima medição necessária."},
    ]
    if diagnosis.get("blocked_fixes"):
        steps.insert(1, {"phase": "1A · Reparar o modelo", "goal": "Resolver inviabilidades estruturais.", "action": diagnosis['blocked_fixes'][0]['fix']})
    return steps


def executive_brief(base: Dict[str, Any], diagnosis: Dict[str, Any], recommended: Optional[Dict[str, Any]] = None) -> str:
    sentence = (
        f"O Anti-Murphy identifica {diagnosis.get('constraint', {}).get('station', '-')} como principal restrição, "
        f"com SLA atual de {float(base.get('sla_pct', 0)):.0f}% e custo total simulado de R$ {float(base.get('total_cost', 0)):,.2f}."
    )
    if recommended:
        sentence += (
            f" A melhor resposta simulada no momento é '{recommended.get('action', '-')}', "
            f"classificada como {recommended.get('verdict', '-').lower()}, "
            f"porque {recommended.get('verdict_reason', '-')}."
        )
    else:
        sentence += " Ainda não existe uma alternativa recomendada consolidada; o próximo passo é simular respostas sob o mesmo incidente."
    return sentence
