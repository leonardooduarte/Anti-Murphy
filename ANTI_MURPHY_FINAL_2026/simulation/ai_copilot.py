from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from simulation.intelligence import resilience_index, copilot_recommendations, explain_comparison
from simulation.metrics import compare_results, murphy_score
from simulation.ai_orchestrator import diagnose_operation, response_playbook, executive_brief


def _station_map(result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(x.get("Posto")): x for x in result.get("stations", [])}


def _penalty_total(result: Optional[Dict[str, Any]]) -> float:
    if not result:
        return 0.0
    return float(sum(float(x.get("Multa (R$)", 0) or 0) for x in result.get("orders", [])))


def build_ai_context(
    base: Dict[str, Any],
    stations: Dict[str, Dict[str, Any]],
    scenario: Optional[Dict[str, Any]] = None,
    decision_history: Optional[List[Dict[str, Any]]] = None,
    opportunities: Optional[List[Dict[str, Any]]] = None,
    stress_results: Optional[List[Dict[str, Any]]] = None,
    goal_results: Optional[List[Dict[str, Any]]] = None,
    decision_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Builds a compact, explicit context packet for the copilot.

    The packet contains only values produced by the Anti-Murphy model or configured
    by the user. This keeps the LLM in an interpretation role rather than letting it
    become a second simulation engine.
    """
    ri = resilience_index(base)
    recs = copilot_recommendations(base, stations)
    smap = _station_map(base)
    diagnosis = diagnose_operation(base, stations, scenario=scenario)
    bn = str(base.get("bottleneck", "-"))
    bn_row = smap.get(bn, {})
    ctx: Dict[str, Any] = {
        "product": "ANTI-MURPHY Decision Twin",
        "grounding_policy": "Simulation outputs are the quantitative source of truth. Do not invent KPIs or unsimulated outcomes.",
        "baseline": {
            "throughput_h": round(float(base.get("throughput_h", 0)), 4),
            "sla_pct": round(float(base.get("sla_pct", 0)), 2),
            "makespan_h": round(float(base.get("makespan_h", 0)), 3),
            "unit_cost": round(float(base.get("unit_cost", 0)), 2),
            "bottleneck": bn,
            "murphy_quality": round(float(murphy_score(base)), 1),
            "resilience": ri,
            "penalties_total": round(_penalty_total(base), 2),
            "orders_total": len(base.get("orders", [])),
            "orders_late": sum(1 for x in base.get("orders", []) if str(x.get("Status", "")).lower() not in {"no prazo", "on time"}),
        },
        "constraint": {
            "station": bn,
            "name": bn_row.get("Nome", stations.get(bn, {}).get("nome", bn)),
            "machine_util_pct": float(bn_row.get("Utilização máquina (%)", 0)),
            "labor_util_pct": float(bn_row.get("Utilização mão de obra (%)", 0)),
            "avg_wait_min": float(bn_row.get("Espera média (min)", 0)),
            "max_queue": int(bn_row.get("Fila máx.", 0)),
        },
        "stations": [
            {
                "id": str(x.get("Posto")),
                "name": str(x.get("Nome", x.get("Posto"))),
                "machine_util_pct": round(float(x.get("Utilização máquina (%)", 0)), 1),
                "labor_util_pct": round(float(x.get("Utilização mão de obra (%)", 0)), 1),
                "avg_wait_min": round(float(x.get("Espera média (min)", 0)), 1),
                "max_queue": int(x.get("Fila máx.", 0)),
            }
            for x in base.get("stations", [])
        ],
        "heuristic_next_tests": recs[:4],
        "diagnosis": diagnosis,
        "executive_brief": executive_brief(base, diagnosis),
        "playbook": response_playbook(diagnosis),
        "decision_history": [
            {k: h.get(k) for k in ["name", "source", "throughput", "sla", "unit_cost", "makespan", "bottleneck"]}
            for h in (decision_history or [])[-8:]
        ],
    }

    if scenario:
        d = compare_results(base, scenario)
        expl = explain_comparison(base, scenario)
        ctx["active_scenario"] = {
            "name": scenario.get("name", "Decision world"),
            "throughput_h": round(float(scenario.get("throughput_h", 0)), 4),
            "sla_pct": round(float(scenario.get("sla_pct", 0)), 2),
            "makespan_h": round(float(scenario.get("makespan_h", 0)), 3),
            "unit_cost": round(float(scenario.get("unit_cost", 0)), 2),
            "bottleneck": str(scenario.get("bottleneck", "-")),
            "penalties_total": round(_penalty_total(scenario), 2),
            "delta": {k: round(float(v), 3) if isinstance(v, (int, float)) else v for k, v in d.items()},
            "explanation": expl,
        }
    if decision_data:
        recommended = decision_data.get("leader") or decision_data.get("recommended")
        ctx["decision_evidence"] = {
            "policy_status": decision_data.get("policy_status", "Não informado"),
            "policy_explanation": decision_data.get("policy_explanation", ""),
            "recommended": {k: recommended.get(k) for k in ["action", "verdict", "verdict_reason", "tradeoff_note", "decision_cost", "sla_pct", "makespan_h", "savings_vs_incident"]} if recommended else None,
            "alternatives": [
                {k: row.get(k) for k in ["action", "verdict", "decision_cost", "sla_pct", "makespan_h", "savings_vs_incident", "pareto"]}
                for row in (decision_data.get("rows") or [])[:8]
            ],
        }
        ctx["executive_brief"] = executive_brief(base, diagnosis, recommended)

    if opportunities:
        ctx["opportunities"] = [
            {k: o.get(k) for k in ["Ação", "Score", "Throughput Δ (%)", "SLA Δ (p.p.)", "Custo/un Δ (%)", "Makespan Δ (%)"]}
            for o in opportunities[:8]
        ]
    if stress_results:
        rows = (stress_results.get("runs", []) if isinstance(stress_results, dict) else stress_results)[:8]
        ctx["stress_sample"] = [
            {k: r.get(k) for k in ["Posto afetado", "Demanda x", "Parada (h)", "Ausências", "Throughput", "SLA", "Makespan", "Custo/un"]}
            for r in rows
        ]
    if goal_results:
        ctx["goal_routes"] = [
            {k: r.get(k) for k in ["Cenário", "Throughput", "SLA", "Custo/un", "Operadores +", "Máquinas +", "Investimento estimado", "Atinge meta"]}
            for r in goal_results[:6]
        ]
    return ctx


def context_json(context: Dict[str, Any]) -> str:
    return json.dumps(context, ensure_ascii=False, indent=2, default=str)


def local_copilot_answer(question: str, context: Dict[str, Any]) -> str:
    """Offline fallback. It never invents a new simulation result."""
    q = (question or "").strip().lower()
    b = context.get("baseline", {})
    c = context.get("constraint", {})
    recs = context.get("heuristic_next_tests", [])
    active = context.get("active_scenario")
    diagnosis = context.get("diagnosis", {})
    playbook = context.get("playbook", [])
    evidence = context.get("decision_evidence", {})
    brief = context.get("executive_brief")

    if not q:
        return "Pergunte sobre gargalo, SLA, custo, risco, próximo teste, bloqueios do modelo ou decisão recomendada."
    if any(x in q for x in ["resumo", "executivo", "briefing", "diretoria"]):
        return brief or "Rode o cenário-base para consolidar um resumo com indicadores verificados."
    if any(x in q for x in ["bloqueio", "sem operador", "inviável", "inviavel", "corrigir modelo"]):
        fixes = diagnosis.get("blocked_fixes", [])
        if fixes:
            top = fixes[0]
            return f"O modelo apresenta um bloqueio em **{top.get('station')}**: {top.get('problem')}. Correção sugerida: {top.get('fix')}"
        return "Não detectei bloqueios estruturais óbvios no contexto atual. Se houver uma falha de cenário, revise operadores, máquinas e roteiros."
    if any(x in q for x in ["gargalo", "restrição", "problema principal", "pressão"]):
        return (f"No cenário-base, a restrição identificada pelo modelo é **{c.get('station','-')} · {c.get('name','-')}**. "
                f"Ela registra fila máxima de **{c.get('max_queue',0)}**, espera média de **{c.get('avg_wait_min',0):.1f} min** e utilização de máquina de **{c.get('machine_util_pct',0):.1f}%**. "
                "Isso é diagnóstico do modelo simulado; não substitui validação com dados do chão de fábrica.")
    if any(x in q for x in ["sla", "prazo", "atras"]):
        return (f"O SLA simulado do cenário-base é **{b.get('sla_pct',0):.0f}%**, com **{b.get('orders_late',0)}/{b.get('orders_total',0)} ordens atrasadas**. "
                f"A exposição acumulada em penalidades no modelo é **R$ {b.get('penalties_total',0):,.2f}**. "
                f"A restrição atual está em **{c.get('station','-')}**, com espera média de **{c.get('avg_wait_min',0):.1f} min**.")
    if any(x in q for x in ["plano", "playbook", "como agir", "o que faço agora", "passo a passo"]):
        if not playbook:
            return "Ainda não há playbook disponível. Rode o cenário-base para eu estruturar uma sequência de ação."
        return "\n".join([f"**{step.get('phase')}** — {step.get('goal')} {step.get('action')}" for step in playbook])
    if any(x in q for x in ["próximo", "proximo", "testar", "recomenda", "ação", "acao"]):
        if evidence and not evidence.get("recommended") and evidence.get("policy_status") in (
            'MODELO BLOQUEADO','SEM IMPACTO MENSURÁVEL','RESTRIÇÕES NÃO ATENDIDAS','SEM MELHORIA VIÁVEL'):
            return ("**Nenhuma recomendação automática admissível no incidente analisado.** "
                    + str(evidence.get('policy_explanation','Revise restrições e dados.')))
        rec = evidence.get("recommended") or (recs[0] if recs else None)
        if rec:
            why = rec.get('verdict_reason') or rec.get('why', '')
            return (f"A próxima alternativa mais forte no contexto atual é **{rec.get('action') or rec.get('title')}**. "
                    f"Motivo principal: {why} "
                    f"Resumo do trade-off: {rec.get('tradeoff_note', '')}"
                    " O Anti-Murphy recomenda **simular primeiro**; isso não é uma ordem de implementação real.")
        return "Ainda não há uma sugestão disponível. Rode o cenário-base e, idealmente, o Decision Evidence Studio."
    if any(x in q for x in ["cenário", "cenario", "compar", "decisão", "decisao"]):
        if evidence and evidence.get("policy_status") in ("MODELO BLOQUEADO", "SEM IMPACTO MENSURÁVEL", "RESTRIÇÕES NÃO ATENDIDAS", "SEM MELHORIA VIÁVEL"):
            return str(evidence.get("policy_explanation","Nenhuma resposta atende às restrições atuais."))
        if evidence.get("recommended"):
            rec = evidence["recommended"]
            return (f"No Decision Evidence Studio, a alternativa líder atual é **{rec.get('action','-')}** com veredito **{rec.get('verdict','-')}**. "
                    f"Ela apresenta custo de decisão de **R$ {float(rec.get('decision_cost',0)):,.2f}**, SLA de **{float(rec.get('sla_pct',0)):.1f}%** e makespan de **{float(rec.get('makespan_h',0)):.2f} h**. "
                    f"Justificativa: {rec.get('verdict_reason','-')}")
        if not active:
            return "Não existe um cenário alternativo ativo. Crie um experimento no Scenario Studio ou rode o Decision Evidence Studio para eu comparar com o baseline."
        d = active.get("delta", {})
        return (f"O cenário **{active.get('name')}** altera throughput em **{float(d.get('throughput_pct',0)):+.1f}%**, "
                f"SLA em **{float(d.get('sla_pp',0)):+.1f} p.p.**, custo/un em **{float(d.get('unit_cost_pct',0)):+.1f}%** e makespan em **{float(d.get('makespan_pct',0)):+.1f}%**. "
                f"O gargalo do cenário é **{active.get('bottleneck','-')}**.")
    if any(x in q for x in ["resili", "risco", "murphy"]):
        ri = b.get("resilience", {})
        risks = diagnosis.get('risks', [])
        risk_txt = " ".join(r.get('message','') for r in risks[:2])
        return (f"O índice interno de resiliência está em **{ri.get('score',0):.0f}/100 · {ri.get('band','-')}** e a pontuação Murphy (maior = melhor) em **{b.get('murphy_quality',0):.0f}/100**. "
                f"Riscos em destaque: {risk_txt or 'sem alertas adicionais estruturados.'} "
                "Esses índices são comparativos e explicáveis dentro do modelo, não probabilidades reais de falha.")
    if any(x in q for x in ["custo", "dinheiro", "penal", "não agir", "nao agir"]):
        msg = f"No baseline, o custo unitário simulado é **R$ {b.get('unit_cost',0):,.2f}** e as penalidades acumuladas são **R$ {b.get('penalties_total',0):,.2f}**."
        if active:
            msg += f" No cenário ativo, as penalidades são **R$ {active.get('penalties_total',0):,.2f}**."
        if evidence.get('recommended'):
            rec = evidence['recommended']
            msg += f" A alternativa líder do DES indica **{rec.get('tradeoff_note','sem trade-off resumido')}**."
        return msg + " Use o Decision Evidence Studio para confrontar ganho operacional, custo e exposição de serviço."
    return (f"O estado atual do modelo tem throughput **{b.get('throughput_h',0):.2f} un/h**, SLA **{b.get('sla_pct',0):.0f}%**, makespan **{b.get('makespan_h',0):.1f} h** e gargalo em **{b.get('bottleneck','-')}**. "
            "Posso explicar gargalo, prazo, custo, risco, bloqueios do modelo, decisão recomendada ou sugerir o próximo experimento sem inventar resultados não simulados.")


def ask_openai(api_key: str, model: str, question: str, context: Dict[str, Any], history: Optional[List[Dict[str, str]]] = None) -> str:
    """Calls OpenAI Responses API. The key is supplied at runtime and never persisted here."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    history = history or []
    transcript = []
    for m in history[-8:]:
        role = m.get("role", "user")
        content = str(m.get("content", ""))
        if content:
            transcript.append({"role": role if role in {"user", "assistant"} else "user", "content": content})
    transcript.append({"role": "user", "content": question})

    instructions = """Você é o Murphy AI, copiloto operacional do software ANTI-MURPHY.
Seu papel é interpretar resultados da simulação, explicar causa e efeito, sugerir EXPERIMENTOS e produzir sínteses executivas.
Regras obrigatórias:
1) Os números do JSON CONTEXTO ANTI-MURPHY são a fonte quantitativa de verdade. Nunca invente KPI, ganho, probabilidade, payback ou resultado não simulado.
2) Se o usuário perguntar 'o que acontece se...' e o cenário não estiver no contexto, diga que precisa ser simulado e proponha um teste concreto no Scenario Studio.
3) Diferencie claramente resultado simulado, heurística e recomendação gerencial.
4) Não apresente confiança heurística como probabilidade real.
5) Seja conciso, técnico e orientado a decisão. Em português do Brasil, salvo pedido contrário.
6) Ao sugerir uma ação, explique o sinal que motivou o teste e o que medir depois.
7) Você não controla a fábrica real. Nunca afirme que uma ação foi implementada; apenas que pode ser simulada no Anti-Murphy.
"""
    packed = context_json(context)
    full_instructions = instructions + "\n\nCONTEXTO ANTI-MURPHY (dados estruturados do modelo):\n" + packed
    response = client.responses.create(model=model, instructions=full_instructions, input=transcript)
    return (getattr(response, "output_text", None) or "").strip() or "A API não retornou texto."


def first_recommended_action(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    recs = context.get("heuristic_next_tests", []) or []
    return recs[0] if recs else None


def scenario_prefill_from_recommendation(rec: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not rec:
        return None
    title = str(rec.get("title", ""))
    out: Dict[str, Any] = {"name": f"AI · {title[:48]}"}
    if "+1 operador em " in title:
        out["target"] = title.split("+1 operador em ", 1)[1].strip()
        out["delta_workers"] = 1
    elif "+1 máquina em " in title:
        out["target"] = title.split("+1 máquina em ", 1)[1].strip()
        out["delta_machines"] = 1
    elif "EDD" in title.upper():
        out["rule"] = "EDD"
    else:
        return None
    return out
