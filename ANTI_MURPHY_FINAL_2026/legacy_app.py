from __future__ import annotations

from copy import deepcopy
from html import escape as html_escape
import plotly.io as pio
from pathlib import Path
from io import BytesIO
import json
import os
import pandas as pd
import streamlit as st
import time

from data.scenarios import STATIONS_BASE, ORDERS_BASE, DEFAULT_RULE, DEFAULT_SEED
from data.importer import read_client_workbook, make_template
from simulation.factory import build_scenario
from simulation.engine import run_simulation
from simulation.validation import validate_model
from simulation.decision_lab import evaluate_decisions, paired_stress_test, decision_report, config_signature
from simulation.decisions import generate_opportunities
from simulation.events import EVENT_PRESETS
from simulation.metrics import compare_results, murphy_score
from simulation.innovation import stress_test, goal_seek, finance_lens
from simulation.intelligence import resilience_index, copilot_recommendations, explain_comparison
from simulation.ai_copilot import (build_ai_context, local_copilot_answer, ask_openai,
                                   first_recommended_action, scenario_prefill_from_recommendation, context_json)
from simulation.decision_council import blocked_station_fixes
from simulation.ai_orchestrator import diagnose_operation, response_playbook, executive_brief
from simulation.advanced import (operating_alerts, sensitivity_analysis, demand_breakpoint, absentee_breakpoint, portfolio_summary, recovery_plan,
                                monte_carlo_analysis, resilience_surface, model_confidence)
from simulation.v23 import decision_scorecard, value_at_stake, station_pressure, portfolio_frontier, workspace_payload
from simulation.v24 import scheduling_benchmark, calibration_summary, reliability_analysis, skill_coverage, pareto_frontier
from simulation.v25 import root_cause_explorer, decision_autopilot, scenario_portfolio, change_digest, audit_entry
from ui.components import inject_css, splash, topbar, metric_card, page_intro
from ui.factory_view import render_flow
from ui.dashboard import utilization_chart, compare_bar, radar, render_delta
from ui.cinematic import render_cinematic_twin, render_decision_reveal, render_opportunity_radar
from ui.experience import render_replay, render_fragility_map, render_goal_path
from ui.premium import render_copilot_panel, render_propagation_map, render_demo_story, render_decision_timeline
from ui.v13 import render_alert_center, sensitivity_chart, rupture_chart, render_portfolio, render_migration
from ui.v14 import inject_v14_css, section_header, decision_rail, insight_strip, compare_summary, neutral_compare_state
from ui.v15 import (inject_v15_css, pagebar, module_hero, cockpit_kpis,
                    stage_label, decision_deck, station_gallery, compare_story, scenario_preview,
                    opportunity_matrix, stress_landscape, route_cards)
from ui.v16 import (inject_v16_css, sidebar_brand, sidebar_state, topbar as v16_topbar,
                    page_head as v16_page_head, metric_rail, workspace_label, intelligence_panel,
                    signal_strip, causal_chain, review_cards, decision_confidence, confidence_card,
                    scenario_canvas, opportunity_leaderboard, stress_summary_panel, goal_route_strip,
                    scenario_delta_chart, recovery_cards, model_quality_strip)
from ui.v17 import (inject_v17_css, station_inspector, decision_verdict,
                    model_cards, opportunity_quadrants, section_note)
from ui.v18 import (inject_v18_css, executive_pulse, economics_strip, model_flow,
                    decision_lens, resilience_callout)
from ui.v19 import inject_v19_css
from ui.v20 import (inject_v20_css, workflow_ribbon, stale_scenario_notice,
                    opportunity_detail, baseline_target_warning, station_edit_header, decision_economics)
from ui.v21 import (inject_v21_css, model_confidence_panel, scenario_intervention_map, decision_narrative,
                    monte_carlo_panel, resilience_surface_chart, frontier_summary)
from ui.v22 import inject_v22_css, ai_hero, recommended_action_card, trust_note, mode_badge
from ui.v23 import (inject_v23_css, executive_hero, executive_snapshot, decision_scorecard_ui,
                    decision_thread, ai_action_plan, portfolio_scatter, pressure_strip)
from ui.v24 import inject_v24_css, trust_header, agent_architecture, scheduling_row, reliability_strip, pareto_chart
from ui.v25 import inject_v25_css, mode_badge_v25, portfolio_leaders, root_cause_panel, root_cause_chart, agent_run_header, change_digest_ui, presentation_hero
from ui.v28 import war_room_hero
from ui.design_system import inject_design_system
from ui.v29 import inject_atlas_css, hero as atlas_hero, kpi_strip as atlas_kpi_strip, stage as atlas_stage, signal as atlas_signal, plant_flow as atlas_plant_flow, comparison_chart as atlas_comparison_chart, frontier_chart as atlas_frontier_chart
from simulation.atlas import analyze_incident, DecisionPolicy, decision_memo, safe_summary
from simulation.murphy_agent import propose_simulation, call_optional_llm, explanation_from_data
from ui.v26 import inject_v26_css, executive_strip, station_inspector as context_inspector, ai_context_bar, trust_dashboard, skill_heatmap, portfolio_cards as portfolio_cards_v26, mission_target_hero, presentation_story

BRAND_DIR = Path(__file__).resolve().parent / "assets" / "brand"
# A configuração da página é realizada uma única vez em app.py.
inject_css()
inject_v14_css()
inject_v15_css()
inject_v16_css()
inject_v17_css()
inject_v18_css()
inject_v19_css()
inject_v20_css()
inject_v21_css()
inject_v22_css()
inject_v23_css()
inject_v24_css()
inject_v25_css()
inject_v26_css()
inject_atlas_css()
inject_design_system()
# V30: return to the unified workspace; the original modules remain available.
from ui.nexus_design import inject as inject_nexus_skin
inject_nexus_skin()
if st.session_state.get('am_unified_shell',False):
    st.markdown('<style>'+(Path(__file__).resolve().parent/'ui'/'unified_shell.css').read_text('utf8')+'</style>',unsafe_allow_html=True)
def _return_to_operation():
    st.session_state['am_area'] = 'Operação'
    st.session_state['op_historical'] = False
    st.session_state['nx_legacy'] = False
    st.session_state['nx_legacy_returned'] = True
if not st.session_state.get('am_unified_shell',False):
    st.button('← Voltar para operação e decisões', key='nx_return_from_legacy', on_click=_return_to_operation)
# The historical environment keeps a permanent route back to the new workbench.
try:
    import html as _html, json as _json, socket as _socket
    _record=Path(__file__).resolve().parent/'workspace'/'.main_url.json'
    if _record.exists():
        _value=_json.loads(_record.read_text(encoding='utf8'))
        _port=int(_value['port'])
        if 1024 <= _port <= 65535:
            with _socket.create_connection(('127.0.0.1',_port),timeout=.1):pass
            st.markdown(f'<a class="am-main-return" href="http://127.0.0.1:{_port}/#simulacao" target="_self">← Voltar à página inicial do Anti-Murphy</a>',unsafe_allow_html=True)
except (OSError,ValueError,KeyError,TypeError):
    pass

pio.templates.default = "plotly_dark"

if "stations" not in st.session_state:
    st.session_state.stations = deepcopy(STATIONS_BASE)
if "orders" not in st.session_state:
    st.session_state.orders = deepcopy(ORDERS_BASE)
if "base_result" not in st.session_state:
    st.session_state.base_result = None
if "scenario_result" not in st.session_state:
    st.session_state.scenario_result = None
if "scenario_config" not in st.session_state:
    st.session_state.scenario_config = None
if "decision_history" not in st.session_state:
    st.session_state.decision_history = []
if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []
if "am_ai_key" not in st.session_state:
    st.session_state.am_ai_key = ""
if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "Operator"
if "presentation_mode" not in st.session_state:
    st.session_state.presentation_mode = False
if "scenario_notes" not in st.session_state:
    st.session_state.scenario_notes = {}
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "v25_ops_meta" not in st.session_state:
    st.session_state.v25_ops_meta = {}
if "v26_ai_context" not in st.session_state:
    st.session_state.v26_ai_context = ""

# One-time branded launch sequence. It runs only once per browser session.
if not st.session_state.get("am_booted", False):
    st.session_state.am_booted = True

workers_total = sum(int(s.get("operadores", 0)) for s in st.session_state.stations.values())
model_state = "Experimento pronto" if st.session_state.scenario_result is not None else "Cenário-base ativo"

# V16.2 uses an in-canvas navigation rail instead of Streamlit's native sidebar.
# This avoids browser/sidebar collapse state and makes navigation part of the product UI.
NAV_GROUPS = [
    ("CENTRAL", [("War Room", "◉  Central de decisões"), ("Murphy AI", "✦  Murphy AI"), ("Decision Evidence", "◆  Comparar respostas"), ("Modelar", "◇  Modelo industrial")]),
    ("GESTÃO", [("Visão 360", "◎  Visão operacional"), ("Comparar", "⇄  Comparar cenários"), ("Executive Room", "▣  Sala executiva")]),
]
ADVANCED_PAGES = [("Operations Studio", "⌘  Operações"), ("Trust Center", "◎  Confiança"),
    ("Murphy Lab", "↯  Laboratório"), ("Scenario Portfolio", "▤  Portfólio"),
    ("Opportunity Engine", "✦  Oportunidades"), ("Optimization Hub", "◈  Otimização"),
    ("Stress Lab", "⌁  Resiliência"), ("Mission Control", "◎  Metas")]
PAGE_SECTION = {
    "War Room":"Control Room", "Visão 360":"Control Room", "Executive Room":"Control Room", "Murphy AI":"AI Command", "Trust Center":"AI Command", "Modelar":"Model", "Operations Studio":"Model", "Murphy Lab":"Experiment",
    "Decision Evidence":"Experiment", "Comparar":"Experiment", "Opportunity Engine":"Intelligence", "Optimization Hub":"Intelligence", "Stress Lab":"Intelligence",
    "Scenario Portfolio":"Planning", "Mission Control":"Planning",
}
if "active_page" not in st.session_state:
    st.session_state.active_page = "War Room"

page = st.session_state.active_page


def route_to_text(route):
    return "; ".join(f"{sid}:{float(minutes):g}" for sid, minutes in route)


def parse_route(text: str, valid_stations: set[str]):
    route = []
    raw = str(text or "").strip()
    if not raw:
        raise ValueError("O roteiro não pode ficar vazio.")
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(f"Etapa inválida '{part}'. Use POSTO:minutos.")
        sid, mins = [x.strip() for x in part.split(":", 1)]
        sid = sid.upper()
        if sid not in valid_stations:
            raise ValueError(f"Posto '{sid}' não existe no modelo.")
        try:
            mins = float(mins.replace(",", "."))
        except Exception as exc:
            raise ValueError(f"Tempo inválido em '{part}'.") from exc
        if mins <= 0:
            raise ValueError(f"O tempo de '{sid}' deve ser maior que zero.")
        route.append((sid, mins))
    if not route:
        raise ValueError("O roteiro precisa ter pelo menos uma etapa.")
    return route


def normalize_station_id(value: str) -> str:
    return "_".join(str(value or "").strip().upper().replace("-", " ").split())


def frames_from_current():
    station_rows = []
    for sid, s in st.session_state.stations.items():
        station_rows.append({
            "ID": sid, "Posto": s["nome"], "Máquinas": s["maquinas"], "Operadores": s["operadores"],
            "Operadores/máquina": s.get("operadores_por_maquina", 1),
            "Eficiência operador": s["eficiencia_operador"], "Disponibilidade": s["disponibilidade"],
            "Setup (min)": s.get("setup_min", 0.0), "Custo operador/h": s["custo_operador_h"],
            "Custo máquina/h": s["custo_maquina_h"],
        })
    order_rows = []
    for o in st.session_state.orders:
        order_rows.append({
            "ID": o["id"], "Cliente": o["cliente"], "Produto": o["produto"],
            "Quantidade": o["quantidade"], "Prazo (h)": o["prazo_h"], "Multa/h (R$)": o["multa_hora"],
            "Prioridade": o.get("prioridade", 3), "Roteiro": route_to_text(o["route"]),
        })
    return pd.DataFrame(station_rows), pd.DataFrame(order_rows)


def frames_to_model(station_df: pd.DataFrame, order_df: pd.DataFrame):
    new_stations = {}
    for i, r in station_df.iterrows():
        sid = normalize_station_id(r.get("ID", ""))
        nome = str(r.get("Posto", "")).strip()
        if not sid:
            raise ValueError(f"A linha {i+1} da estrutura produtiva precisa de um ID.")
        if not nome:
            raise ValueError(f"O posto {sid} precisa de um nome.")
        if sid in new_stations:
            raise ValueError(f"ID de posto duplicado: {sid}.")
        new_stations[sid] = {
            "nome": nome, "setor": nome,
            "maquinas": max(1, int(float(r.get("Máquinas", 1) or 1))),
            "operadores": max(0, int(float(r.get("Operadores", 0) or 0))),
            "operadores_por_maquina": float(r.get("Operadores/máquina", 1) or 1),
            "eficiencia_operador": float(r.get("Eficiência operador", 1.0) or 1.0),
            "disponibilidade": float(r.get("Disponibilidade", 1.0) or 1.0),
            "custo_operador_h": float(r.get("Custo operador/h", 0.0) or 0.0),
            "custo_maquina_h": float(r.get("Custo máquina/h", 0.0) or 0.0),
            "setup_min": float(r.get("Setup (min)", 0.0) or 0.0), "icone": "◇",
        }
        if not 0.50 <= new_stations[sid]["disponibilidade"] <= 1.0:
            raise ValueError(f"Disponibilidade de {sid} deve estar entre 0,50 e 1,00.")
        if not 0.55 <= new_stations[sid]["eficiencia_operador"] <= 1.20:
            raise ValueError(f"Eficiência do operador em {sid} deve estar entre 0,55 e 1,20.")

    valid_ids = set(new_stations)
    new_orders = []
    seen_orders = set()
    for i, r in order_df.iterrows():
        oid = str(r.get("ID", "")).strip().upper()
        if not oid:
            raise ValueError(f"A linha {i+1} da carteira precisa de um ID de ordem.")
        if oid in seen_orders:
            raise ValueError(f"ID de ordem duplicado: {oid}.")
        seen_orders.add(oid)
        cliente = str(r.get("Cliente", "")).strip()
        produto = str(r.get("Produto", "")).strip()
        if not cliente or not produto:
            raise ValueError(f"A ordem {oid} precisa de cliente e produto.")
        new_orders.append({
            "id": oid, "cliente": cliente, "produto": produto,
            "quantidade": max(1, int(float(r.get("Quantidade", 1) or 1))),
            "prazo_h": float(r.get("Prazo (h)", 1.0) or 1.0),
            "multa_hora": float(r.get("Multa/h (R$)", 0.0) or 0.0),
            "prioridade": int(float(r.get("Prioridade", 3) or 3)),
            "route": parse_route(r.get("Roteiro", ""), valid_ids),
        })
    if not new_orders:
        raise ValueError("A carteira precisa ter pelo menos uma ordem.")
    return new_stations, new_orders


def reset_analysis_state():
    st.session_state.base_result = None
    st.session_state.scenario_result = None
    st.session_state.scenario_config = None
    st.session_state.decision_history = []  # Impede comparação de resultados de outro modelo.
    st.session_state.scenario_notes = {}
    st.session_state.ai_messages = []  # Evita diálogo apoiado em modelo substituído.
    st.session_state.v26_ai_context = ""
    for key in ["opportunities", "stress_results", "goal_results", "demo_story", "scenario_input_signature","v21_mc","v21_surface","ai_scenario_prefill","ai_prefill_pending","v23_exec_notes","v24_mc","v24_calibration","v24_schedule","v24_reliability","v24_skills","v25_autopilot","v25_ops_meta","v25_portfolio_compare","v25_shifts","v25_skill_df","v25_skills","v25_rel_df","v25_reliability","v27_decisions","v27_incident","v27_robustness","v29_analysis","v29_pending_proposal","v29_demo_mode","v29_demo_pending"]:
        st.session_state.pop(key, None)


def register_decision(name: str, source: str, result):
    base = ensure_base()
    d = compare_results(base, result)
    entry = {
        "name": name or result.get("name", "Cenário"), "source": source,
        "bottleneck": result.get("bottleneck", "-"), "delta": d,
        "throughput": result.get("throughput_h", 0), "sla": result.get("sla_pct", 0),
        "unit_cost": result.get("unit_cost", 0), "makespan": result.get("makespan_h", 0),
        "result": result,
    }
    entry["model_fingerprint"] = config_signature(current_base_config())
    st.session_state.decision_history.append(entry)
    st.session_state.decision_history = st.session_state.decision_history[-30:]
    st.session_state.audit_log.append(audit_entry("decision", entry["name"], f"{source} · gargalo {entry['bottleneck']} · SLA {entry['sla']:.0f}%"))
    st.session_state.audit_log = st.session_state.audit_log[-80:]


def executive_report_html(base, alt=None):
    alt = alt or base
    expl = explain_comparison(base, alt) if alt is not base else None
    rows = "".join(
        f"<tr><td>{html_escape(str(r['Posto']))}</td><td>{html_escape(str(r['Nome']))}</td><td>{r['Utilização máquina (%)']:.1f}%</td><td>{r['Espera média (min)']:.1f}</td><td>{r['Fila máx.']}</td></tr>"
        for r in alt.get("stations", [])
    )
    narrative = "Cenário-base documentado." if expl is None else expl["headline"] + " " + " ".join(expl["causes"])
    narrative = html_escape(str(narrative))
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Relatório Anti-Murphy</title><style>body{{font-family:Arial,sans-serif;color:#1D292D;max-width:980px;margin:40px auto;padding:0 24px}}h1{{font-size:34px}}.k{{color:#FF681B;font-weight:bold;letter-spacing:.08em}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.card{{border:1px solid #ddd6ca;border-radius:14px;padding:14px}}.card b{{display:block;font-size:24px;margin-top:6px}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{text-align:left;padding:9px;border-bottom:1px solid #e3ddd3;font-size:13px}}.note{{border-left:4px solid #FF681B;background:#f7f3eb;padding:14px 16px;margin:22px 0}}</style></head><body><div class='k'>ANTI-MURPHY · DECISION TWIN</div><h1>Relatório executivo de cenário</h1><p><b>Cenário:</b> {html_escape(str(alt.get('name','Base')))}</p><div class='metrics'><div class='card'>Throughput<b>{alt['throughput_h']:.2f} un/h</b></div><div class='card'>SLA<b>{alt['sla_pct']:.0f}%</b></div><div class='card'>Custo/un<b>R$ {alt['unit_cost']:.2f}</b></div><div class='card'>Makespan<b>{alt['makespan_h']:.1f} h</b></div></div><div class='note'>{narrative}</div><h2>Pressão por posto</h2><table><thead><tr><th>Posto</th><th>Nome</th><th>Utilização</th><th>Espera (min)</th><th>Fila máx.</th></tr></thead><tbody>{rows}</tbody></table><p style='color:#777;font-size:11px;margin-top:30px'>Relatório gerado pelo Anti-Murphy a partir da simulação de eventos discretos. Resultados são cenários do modelo e não previsões determinísticas do mundo real.</p></body></html>""".encode("utf-8")



def scenario_input_signature(target, delta_workers, delta_machines, demand, rule, event_name, chaos_start, absent, scenario_name):
    payload = {
        "target": str(target), "delta_workers": int(delta_workers), "delta_machines": int(delta_machines),
        "demand": round(float(demand), 4), "rule": str(rule), "event": str(event_name),
        "chaos_start": round(float(chaos_start), 3), "absent": int(absent),
        "name": str(scenario_name or "Experimento").strip(),
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def current_base_config():
    return build_scenario("Cenário Base", st.session_state.stations, st.session_state.orders, dispatch_rule=DEFAULT_RULE, seed=DEFAULT_SEED)


def ensure_base():
    # Protect against legacy editors mutating the model without calling reset_analysis_state.
    signature=config_signature(current_base_config())
    previous=st.session_state.get('base_result_signature')
    if st.session_state.base_result is None or previous!=signature:
        if previous is not None and previous != signature:
            st.session_state.scenario_result=None
            st.session_state.scenario_config=None
            st.session_state.decision_history=[]
            st.session_state.ai_messages=[]
            for stale in ('v29_analysis','v27_decisions','v25_autopilot','opportunities',
                          'goal_results','stress_results','v24_mc','v24_calibration'):
                st.session_state.pop(stale,None)
        st.session_state.base_result = run_simulation(current_base_config())
        st.session_state.base_result_signature=signature
    return st.session_state.base_result


def current_atlas_analysis():
    candidate=st.session_state.get('v29_analysis')
    if not candidate:
        return None
    if candidate.get('baseline_signature')!=config_signature(current_base_config()):
        return None
    return candidate


def run_atlas(station, start_h, duration_h, budget, sla, cw=1200., cm=6500., ce=1800.):
    outcome=analyze_incident(current_base_config(),station,float(start_h),float(duration_h),
          DecisionPolicy(float(budget),float(sla),float(cw),float(cm),float(ce)))
    st.session_state.v29_analysis=outcome
    st.session_state.audit_log.append(audit_entry('simulação','Atlas / War Room',
          f"{station}: {duration_h:g}h · {outcome['policy_status']} · {len(outcome['rows'])} alternativas"))
    st.session_state.audit_log=st.session_state.audit_log[-80:]
    return outcome


# Product-shell navigation: independent of Streamlit sidebar state.
nav_col, main_col = st.columns([0.001, 0.999], gap="small") if (st.session_state.presentation_mode or st.session_state.get("am_unified_shell", False)) else st.columns([0.155, 0.845], gap="medium")
with nav_col:
    if not st.session_state.presentation_mode and not st.session_state.get("am_unified_shell", False):
      with st.container(key="am16_navrail"):
          sidebar_brand()
          sidebar_state(model_state, len(st.session_state.stations), workers_total, len(st.session_state.orders))
          for group, items in NAV_GROUPS:
              st.markdown(f"<div class='am16-side-sec'>{group}</div>", unsafe_allow_html=True)
              for page_name, label in items:
                  if st.button(label, key=f"v162_nav_{page_name}", type="primary" if page == page_name else "secondary", use_container_width=True):
                      st.session_state.active_page = page_name
                      st.rerun()
          with st.expander("▤  Análises avançadas", expanded=False):
              for adv_page, adv_label in ADVANCED_PAGES:
                  if st.button(adv_label, key=f"v29_advanced_{adv_page}", use_container_width=True):
                      st.session_state.active_page=adv_page; st.rerun()
          st.markdown("<div class='am16-side-sec'>MODO</div>", unsafe_allow_html=True)
          new_mode = st.radio("Modo", ["Operator","Executive"], horizontal=True, label_visibility="collapsed", key="v25_mode_radio", index=0 if st.session_state.ui_mode=="Operator" else 1)
          if new_mode != st.session_state.ui_mode:
              st.session_state.ui_mode = new_mode
              st.session_state.active_page = "Executive Room" if new_mode == "Executive" else "Visão 360"
              st.rerun()
          mode_badge_v25(st.session_state.ui_mode)
          st.markdown("<div class='am16-side-sec'>COMMAND</div>", unsafe_allow_html=True)
          with st.expander("⌘ Command Center", expanded=False):
              commands = {
                  "Abrir War Room":"War Room",
                  "Abrir Centro de decisão":"Visão 360",
                  "Abrir Executive Room":"Executive Room",
                  "Conversar com Murphy AI":"Murphy AI",
                  "Abrir Model Trust Center":"Trust Center",
                  "Editar modelo":"Modelar",
                  "Abrir Operations Studio":"Operations Studio",
                  "Criar novo experimento":"Murphy Lab",
                  "Validar alternativas sob a mesma falha":"Decision Evidence",
                  "Revisar última decisão":"Comparar",
                  "Buscar oportunidades":"Opportunity Engine",
                  "Abrir Optimization Hub":"Optimization Hub",
                  "Testar resiliência":"Stress Lab",
                  "Abrir Scenario Portfolio":"Scenario Portfolio",
                "Buscar rota para meta":"Mission Control",
              }
              cmd = st.selectbox("Ir para", list(commands), key="v20_cmd_select", label_visibility="collapsed")
              if st.button("Executar comando", key="v20_cmd_go", use_container_width=True):
                  st.session_state.active_page=commands[cmd]; st.rerun()
              st.caption("Atalhos orientados ao fluxo Observe → Diagnose → Experiment → Decide.")
          if st.button("↺  Restaurar modelo", key="v162_reset", use_container_width=True):
              st.session_state.stations = deepcopy(STATIONS_BASE)
              st.session_state.orders = deepcopy(ORDERS_BASE)
              st.session_state.base_result = None
              st.session_state.scenario_result = None
              st.session_state.scenario_config = None
              for key in ["opportunities","stress_results","goal_results","demo_story","demand_rupture","abs_rupture","scenario_input_signature","v21_mc","v21_surface","ai_scenario_prefill","ai_prefill_pending","v23_exec_notes","v24_mc","v24_calibration","v24_schedule","v24_reliability","v24_skills","v25_autopilot","v25_ops_meta","v25_portfolio_compare","v25_shifts","v25_skill_df","v25_skills","v25_rel_df","v25_reliability","v27_decisions","v27_incident","v27_robustness","v29_analysis","v29_pending_proposal","v29_demo_mode","v29_demo_pending"]:
                  st.session_state.pop(key, None)
              st.session_state.decision_history = []
              st.session_state.active_page = "War Room"
              st.rerun()
          st.markdown("<div class='am16-side-footer'>Operational Digital Twin · DES · AI · Optimization<br>Resultados representam cenários do modelo.</div>", unsafe_allow_html=True)
with main_col:
    if st.session_state.presentation_mode:
        exit_col, _ = st.columns([.18,.82])
        with exit_col:
            if st.button("← Sair da apresentação", use_container_width=True, key="v25_exit_presentation"):
                st.session_state.presentation_mode=False; st.rerun()
    else:
        v16_topbar(PAGE_SECTION.get(page,"Workspace"), page, model_state, "Operational Decision Twin · V29 ATLAS")
    _stage_map = {
        "War Room":"DECIDE", "Visão 360":"OBSERVE", "Executive Room":"DECIDE", "Murphy AI":"DIAGNOSE", "Trust Center":"DIAGNOSE", "Modelar":"DIAGNOSE", "Operations Studio":"DIAGNOSE", "Murphy Lab":"EXPERIMENT",
        "Comparar":"DECIDE", "Opportunity Engine":"EXPERIMENT", "Optimization Hub":"DECIDE", "Stress Lab":"DIAGNOSE",
        "Scenario Portfolio":"DECIDE", "Mission Control":"DECIDE",
    }
    if not st.session_state.presentation_mode and not st.session_state.get("am_unified_shell", False):
        workflow_ribbon(_stage_map.get(page, "OBSERVE"))
    if page == "War Room":
        if st.session_state.pop('v29_demo_pending',False):
            # Reset before widgets are instantiated on this rerun.
            st.session_state['v29_station']='CNC' if 'CNC' in st.session_state.stations else next(iter(st.session_state.stations))
            st.session_state['v29_start']=4.0
            st.session_state['v29_duration']=5.0
            st.session_state['v29_sla']=80
            st.session_state['v29_budget']=10000.0
            st.session_state['v29_cw']=1200.0
            st.session_state['v29_cm']=6500.0
            st.session_state['v29_ce']=1800.0
        base=ensure_base()
        atlas= current_atlas_analysis()
        diagnosis=diagnose_operation(base, st.session_state.stations, scenario=st.session_state.scenario_result)
        fixes=blocked_station_fixes(st.session_state.stations,st.session_state.orders)
        leader=atlas.get('leader') if atlas else None
        atlas_hero('Quando a operação falha, a decisão não pode.',
              'Simule rupturas industriais, compare respostas sob o mesmo incidente e descubra o que melhora custos, prazos e fluxo — com hipóteses explícitas.')
        atlas_kpi_strip([
          ('Throughput nominal',f"{base['throughput_h']:.2f} un/h",'Simulado · carteira atual'),
          ('Cumprimento de prazo',f"{base['sla_pct']:.0f}%",'SLA no modelo'),
          ('Custo da operação',f"R$ {base['total_cost']:,.0f}",'Capacidade e penalidades'),
          ('Gargalo principal',base.get('bottleneck','—'),'Restrição detectada')])
        st.markdown('### Linha produtiva · visão rápida')
        atlas_plant_flow(base.get('stations',[]),base.get('bottleneck'),
                  atlas['incident_parameters']['station'] if atlas else None)
        st.markdown('### Da ruptura à decisão')
        s1,s2,s3=st.columns(3,gap='medium')
        with s1: atlas_stage('01','Operação','Entenda capacidade, filas, gargalo e desempenho do modelo atual.')
        with s2: atlas_stage('02','Evento Murphy','Escolha o posto, início e duração da parada, sem alterar a operação real.')
        with s3: atlas_stage('03','Resposta','Compare intervenções sob o mesmo incidente e verifique as restrições.')
        with st.container(border=True):
            st.markdown('### Simulador de resposta · configure e execute')
            c1,c2,c3,c4=st.columns(4)
            sids=list(st.session_state.stations)
            with c1: station=st.selectbox('Posto afetado',sids,index=sids.index('CNC') if 'CNC' in sids else 0,key='v29_station')
            with c2: start_h=st.number_input('Início (horas)',min_value=0.,max_value=500.,value=4.,step=.5,key='v29_start')
            with c3: duration_h=st.number_input('Duração (horas)',min_value=.5,max_value=168.,value=5.,step=.5,key='v29_duration')
            with c4: sla=st.slider('SLA mínimo (%)',min_value=0,max_value=100,value=80,step=5,key='v29_sla')
            with st.expander('Restrições econômicas e premissas de investimento',expanded=False):
                p1,p2,p3,p4=st.columns(4)
                with p1: budget=st.number_input('Orçamento máximo (R$); zero = sem teto',min_value=0.,value=10000.,step=500.,key='v29_budget')
                with p2: cw=st.number_input('Custo/operador (R$)',min_value=0.,value=1200.,step=100.,key='v29_cw')
                with p3: cm=st.number_input('Custo/máquina (R$)',min_value=0.,value=6500.,step=500.,key='v29_cm')
                with p4: ce=st.number_input('Manutenção expressa (R$)',min_value=0.,value=1800.,step=100.,key='v29_ce')
                st.caption('Premissas editáveis deste experimento, não cotações reais ou custos comprovados.')
            # Defaults persist even if the expander has not been opened.
            budget=st.session_state.get('v29_budget',10000.)
            cw=st.session_state.get('v29_cw',1200.)
            cm=st.session_state.get('v29_cm',6500.)
            ce=st.session_state.get('v29_ce',1800.)
            go, demo, helpcol=st.columns([1.2,1,.8])
            with go:
                if st.button('▶ SIMULAR E COMPARAR',type='primary',use_container_width=True,key='v29_go'):
                    try:
                        with st.spinner('Executando o motor e avaliando as alternativas...'):
                            run_atlas(station,start_h,duration_h,budget,sla,cw,cm,ce)
                        st.session_state.v29_demo_mode=False
                        st.rerun()
                    except ValueError as exc:
                        st.error(f'Não foi possível processar o modelo: {exc}')
            with demo:
                if st.button('▣ Demo de 2 minutos',use_container_width=True,key='v29_demo_go'):
                    try:
                        with st.spinner('Preparando narrativa com cálculos reais do simulador...'):
                            run_atlas('CNC' if 'CNC' in sids else sids[0],4.,5.,10000.,80.)
                        st.session_state.v29_demo_mode=True
                        st.session_state.v29_demo_pending=True
                        st.rerun()
                    except ValueError as exc:
                        st.error(f'Não foi possível preparar a demonstração: {exc}')
            with helpcol:
                if st.button('✦ Perguntar à IA',use_container_width=True,key='v29_ai_from_war'):
                    st.session_state.active_page='Murphy AI';st.rerun()
        atlas=current_atlas_analysis()
        if atlas is not None and (
            atlas['incident_parameters']['station']!=station
            or abs(atlas['incident_parameters']['start_h']-start_h)>1e-9
            or abs(atlas['incident_parameters']['duration_h']-duration_h)>1e-9
            or atlas['policy_inputs']!={'budget':float(budget),'min_sla':float(sla),
                        'cost_worker':float(cw),'cost_machine':float(cm),'cost_express':float(ce)}
        ):
            st.warning('Os parâmetros exibidos foram alterados após o último teste. Execute novamente para evitar interpretar uma simulação antiga.')
            atlas=None
        if atlas is not None:
            leader=atlas.get('leader')
            atlas_signal(atlas['policy_status'],atlas['policy_explanation'])
            outcome=atlas['incident']; normal=atlas['normal']
            atlas_kpi_strip([
               ('Custo com incidente',f"R$ {outcome['total_cost']:,.0f}",f"Normal: R$ {normal['total_cost']:,.0f}"),
               ('Tempo até concluir',f"{outcome['makespan_h']:.1f} h",f"Normal: {normal['makespan_h']:.1f} h"),
               ('SLA da crise',f"{outcome['sla_pct']:.0f}%",f"Normal: {normal['sla_pct']:.0f}%"),
               ('Alternativas testadas',str(len(atlas['rows'])),f"{atlas['eligible_count']} atendem às restrições")])
            if st.session_state.get('v29_demo_mode'):
                st.info('MODO PITCH · Explique a situação nominal → a falha CNC → a recomendação; duração sugerida da demonstração: 2 minutos.')
            plotl,plotr=st.columns([1,1],gap='medium')
            with plotl:
                st.plotly_chart(atlas_comparison_chart(normal,outcome,leader),use_container_width=True)
            with plotr:
                st.plotly_chart(atlas_frontier_chart(atlas['rows']),use_container_width=True)
            if leader:
                st.markdown('### Resposta líder · por que considerar?')
                st.success(f"**{leader['action']}** · {leader.get('verdict','Resposta simulada')}")
                st.markdown(f"**Economia estimada vs não intervir:** R$ {float(leader.get('savings') or 0):,.2f} nesta carteira.")
                st.markdown(f"**Evidência:** SLA {leader['sla_pct']:.1f}% · conclusão {leader['makespan_h']:.2f} h · investimento assumido R$ {leader['investment']:,.2f}.")
                st.caption('Realocação exige comprovação de habilidades e disponibilidade. A resposta é uma hipótese simulada, não execução industrial.')
            else:
                st.warning('Nenhuma ação é apresentada como recomendação segura. Reveja o incidente, as restrições ou os recursos.')
            with st.expander('Comparação detalhada · decisões e limites',expanded=not bool(leader)):
                st.dataframe(pd.DataFrame([{'Alternativa':r['action'],'Status':r.get('verdict','-'),
                    'Custo da decisão (R$)':r.get('decision_cost'), 'Economia (R$)':r.get('savings'),
                    'SLA (%)':r['sla_pct'],'Conclusão (h)':r['makespan_h'],
                    'Orçamento OK':r['within_budget'],'SLA OK':r['meets_sla']} for r in atlas['rows']]),use_container_width=True,hide_index=True)
            export1,export2=st.columns(2)
            with export1:
                st.download_button('↓ Exportar memorando auditável (.json)',decision_memo(atlas),
                    file_name='anti_murphy_v291_memorando.json',mime='application/json',use_container_width=True,key='v29_mem_export')
            with export2:
                st.download_button('↓ Exportar alternativas (.csv)',pd.DataFrame([{k:v for k,v in r.items() if k not in ('result','config')} for r in atlas['rows']]).to_csv(index=False).encode('utf-8-sig'),
                    file_name='anti_murphy_v291_alternativas.csv',mime='text/csv',use_container_width=True,key='v29_csv_export')
            st.caption('Identificador do modelo: '+atlas['baseline_signature']+' · Dados sintéticos, custos hipotéticos e ausência de validação industrial.')
        else:
            st.info('Selecione o incidente e execute a simulação para transformar o diagnóstico em evidência de decisão.')
        with st.expander('Leitura técnica, hipóteses e próximos passos',expanded=False):
            for risk in diagnosis.get('risks',[]):
                st.markdown(f"- **{risk.get('type','RISCO').upper()}:** {risk.get('message','')}")
            if fixes:
                for fix in fixes:
                    st.warning(f"{fix['station']}: {fix['fix']}")
            for step in response_playbook(diagnosis):
                st.markdown(f"- **{step['phase']}** · {step['action']}")
    elif page == "Executive Room":
        base = ensure_base()
        resilience = resilience_index(base)
        mconf = model_confidence(st.session_state.stations, st.session_state.orders)
        value = value_at_stake(base, st.session_state.scenario_result)
        v16_page_head("EXECUTIVE / VALUE", "Executive Room", "Uma sala executiva para comunicar estado, risco, evidência de decisão e valor potencial sem abrir mão da rastreabilidade do modelo.", "evidence · value · portfolio · export")
        executive_hero(base, resilience, mconf)
        executive_snapshot(base, value, len(st.session_state.decision_history))
        if st.session_state.presentation_mode:
            presentation_story(base, st.session_state.scenario_result, value)
        else:
            pc1,pc2=st.columns([.72,1.28])
            with pc1:
                if st.button("▣ Presentation Mode", type="primary", use_container_width=True, key="v25_presentation_on"):
                    st.session_state.presentation_mode=True; st.rerun()
            with pc2:
                st.caption("Oculta a navegação e transforma a Executive Room em uma narrativa limpa para banca, diretoria ou investidor.")

        ex1, ex2 = st.columns([1.15, .85], gap="medium")
        with ex1:
            st.markdown("### Decision Thread")
            st.caption("Linha do tempo dos experimentos testados nesta sessão. O objetivo é mostrar aprendizado acumulado, não apenas o último resultado.")
            decision_thread(st.session_state.decision_history)
            frontier = portfolio_frontier(st.session_state.decision_history)
            if st.session_state.decision_history:
                st.markdown("### Portfolio frontier")
                st.caption("Cenários não dominados em custo × SLA. Um ponto na fronteira só permanece se nenhum outro cenário for simultaneamente melhor em throughput/SLA e pior em custo/makespan.")
                st.plotly_chart(portfolio_scatter(frontier, st.session_state.decision_history), use_container_width=True)
        with ex2:
            st.markdown("### Value at stake")
            st.metric("Exposição de penalidade · base", f"R$ {value.get('base_penalties',0):,.2f}")
            st.metric("Ordens atrasadas", f"{value.get('late_orders',0)}/{value.get('total_orders',0)}", f"{value.get('late_share',0):.0f}% da carteira")
            if st.session_state.scenario_result is not None:
                recovered=float(value.get('penalty_recovery',0))
                label_pen = 'Redução de penalidade vs base' if recovered >= 0 else 'Aumento de penalidade vs base'
                st.metric(label_pen, f"R$ {abs(recovered):,.2f}", f"{value.get('penalty_recovery_pct',0):+.1f}%")
                score=decision_scorecard(base, st.session_state.scenario_result)
                decision_scorecard_ui(score)
            else:
                st.info("Rode um cenário alternativo para transformar esta sala em um business case comparativo.")

            st.markdown("### Investor-ready evidence")
            st.caption("O que já existe no produto e pode ser demonstrado sem narrativa artificial.")
            st.markdown(f"- **Modelo:** {len(st.session_state.stations)} postos · {len(st.session_state.orders)} ordens · completude {mconf.get('score',0)}/100")
            st.markdown(f"- **Decision Twin:** gargalo atual em **{base.get('bottleneck','-')}**")
            st.markdown(f"- **Resiliência:** {resilience.get('score',0):.0f}/100 · {resilience.get('band','-')}")
            st.markdown(f"- **Experimentos acumulados:** {len(st.session_state.decision_history)}")
            st.markdown("- **Murphy AI:** interpretação grounded, com fallback local e API generativa opcional")

        st.markdown("### Executive package")
        p1,p2,p3=st.columns(3)
        with p1:
            st.download_button("↓ Relatório executivo HTML", data=executive_report_html(base, st.session_state.scenario_result), file_name="anti_murphy_executive_report.html", mime="text/html", use_container_width=True)
        with p2:
            workspace_json=json.dumps(workspace_payload(st.session_state.stations, st.session_state.orders, st.session_state.decision_history), ensure_ascii=False, indent=2, default=str).encode("utf-8")
            st.download_button("↓ Snapshot do workspace", data=workspace_json, file_name="anti_murphy_workspace_v27.json", mime="application/json", use_container_width=True)
        with p3:
            if st.button("Abrir Murphy AI com briefing", use_container_width=True, key="v23_exec_ai"):
                st.session_state.ai_pending_prompt="Produza um briefing para um potencial investidor ou diretor industrial. Use apenas evidências do modelo: problema, capacidade do produto, risco, decisões testadas e próximo passo. Não invente mercado, receita ou ROI."
                st.session_state.active_page="Murphy AI"
                st.rerun()

    elif page == "Murphy AI":
        base = ensure_base()
        ctx = build_ai_context(
            base, st.session_state.stations,
            scenario=st.session_state.scenario_result,
            decision_history=st.session_state.decision_history,
            opportunities=st.session_state.get("opportunities"),
            stress_results=st.session_state.get("stress_results"),
            goal_results=st.session_state.get("goal_results"),
            decision_data=current_atlas_analysis(),
        )
        v16_page_head("AI / COPILOT", "Murphy AI", "Uma camada de inteligência sobre o Decision Twin: explique, compare e transforme sinais do modelo em experimentos verificáveis.", "grounded · explainable · simulation-first")

        st.markdown('### ✦ AI Action Desk · simulações comandadas por você')
        st.caption('Descreva uma falha em linguagem natural. O Murphy AI prepara o teste, mas só o executa quando você autorizar.')
        cmd_left,cmd_go=st.columns([3,1])
        with cmd_left:
            proposal_text=st.text_input('Solicitação de experimento',placeholder='Simule uma parada de 3 horas na CNC, iniciando em 4 horas',key='v29_ai_command')
        with cmd_go:
            if st.button('Interpretar pedido',use_container_width=True,key='v29_propose'):
                p=propose_simulation(proposal_text,st.session_state.stations)
                if p:
                    st.session_state.v29_pending_proposal=p.as_dict()
                else:
                    st.warning('Não consegui identificar uma falha e um posto válidos. Ex.: simule parada de 3 horas na CNC.')
        prop=st.session_state.get('v29_pending_proposal')
        if prop:
            st.info(f"Experimento preparado: {prop['station']} · início {prop['start_h']:g}h · duração {prop['duration_h']:g}h. Nenhuma simulação foi executada ainda.")
            execute,discard=st.columns([1,1])
            with execute:
                if st.button('✓ Autorizar simulação',type='primary',use_container_width=True,key='v29_ai_execute'):
                    try:
                        with st.spinner('Executando simulação aprovada...'):
                            result=run_atlas(prop['station'],prop['start_h'],prop['duration_h'],10000,80)
                        st.session_state.ai_messages.append({'role':'assistant','content':explanation_from_data(result)})
                        st.session_state.pop('v29_pending_proposal',None)
                        st.session_state.active_page='War Room';st.rerun()
                    except ValueError as exc:
                        st.error(f'Simulação não executada: {exc}')
            with discard:
                if st.button('Descartar pedido',use_container_width=True,key='v29_ai_discard'):
                    st.session_state.pop('v29_pending_proposal',None);st.rerun()

        if st.session_state.get("v26_ai_context"):
            ai_context_bar(st.session_state.v26_ai_context)
            if not st.session_state.get("ai_pending_prompt"):
                st.session_state.ai_pending_prompt = f"Analise este contexto específico do Anti-Murphy e explique causa, risco e próximo teste sem inventar resultados: {st.session_state.v26_ai_context}"

        # API key can come from environment, Streamlit secrets, or session-only user input.
        env_key = os.environ.get("OPENAI_API_KEY", "")
        secret_key = ""
        try:
            secret_key = str(st.secrets.get("OPENAI_API_KEY", ""))
        except Exception:
            secret_key = ""
        runtime_key = st.session_state.get("am_ai_key", "")
        effective_key = runtime_key or env_key or secret_key
        default_model = os.environ.get("ANTI_MURPHY_AI_MODEL", "gpt-4.1-mini")
        if "am_ai_model" not in st.session_state:
            st.session_state.am_ai_model = default_model
        connected = bool(effective_key)
        ai_hero(ctx, connected, st.session_state.am_ai_model)
        agent_architecture()

        settings_col, action_col = st.columns([.72, 1.28], gap="medium")
        with settings_col:
            with st.expander("AI connection & privacy", expanded=not connected):
                mode_badge(connected)
                st.caption("A chave digitada aqui fica apenas na sessão do Streamlit e não é gravada no projeto.")
                key_value = st.text_input("OpenAI API key", value=st.session_state.get("am_ai_key", ""), type="password", placeholder="sk-...", key="v22_key_input")
                if key_value != st.session_state.get("am_ai_key", ""):
                    st.session_state.am_ai_key = key_value
                    st.rerun()
                st.text_input("Modelo", key="am_ai_model", help="Padrão: gpt-4.1-mini (caso disponível na sua API). Verifique os modelos autorizados na sua conta.")
                st.caption("Sem chave, o Murphy AI continua funcionando em modo local com heurísticas e dados do modelo.")
            with st.expander("O que a IA consegue ver", expanded=False):
                st.json(ctx, expanded=False)
                st.download_button("↓ Baixar contexto enviado à IA", data=context_json(ctx).encode("utf-8"), file_name="anti_murphy_ai_context.json", mime="application/json", use_container_width=True)
        with action_col:
            st.markdown("### Ações rápidas")
            qa1,qa2,qa3 = st.columns(3)
            quick = None
            with qa1:
                if st.button("Diagnosticar agora", use_container_width=True, key="v22_diag"):
                    quick = "Faça um diagnóstico do estado atual. Explique a principal restrição, o efeito sobre SLA/custo e o que merece investigação primeiro."
            with qa2:
                if st.button("Próximo experimento", use_container_width=True, key="v22_next"):
                    quick = "Qual é o próximo experimento mais útil para reduzir risco ou melhorar serviço? Não invente resultado; diga exatamente o que devo simular e por quê."
            with qa3:
                if st.button("Briefing executivo", use_container_width=True, key="v22_brief"):
                    quick = "Produza um briefing executivo curto do estado atual e do cenário ativo, se houver. Destaque risco, trade-offs e próximo passo."
            if quick:
                st.session_state.ai_pending_prompt = quick

            rec = first_recommended_action(ctx)
            recommended_action_card(rec)
            ai_action_plan(rec, base)
            act1, act2 = st.columns(2)
            with act1:
                if st.button("Preparar experimento sugerido", use_container_width=True, key="v22_prepare"):
                    prefill = scenario_prefill_from_recommendation(rec)
                    if prefill:
                        st.session_state.ai_scenario_prefill = prefill
                        st.session_state.ai_prefill_pending = True
                        st.session_state.active_page = "Murphy Lab"
                        st.rerun()
                    else:
                        st.info("A sugestão atual pede investigação em outro módulo. Use o texto da recomendação como guia.")
            with act2:
                if st.button("Abrir Opportunity Engine", use_container_width=True, key="v22_opp"):
                    st.session_state.active_page = "Opportunity Engine"
                    st.rerun()
        trust_note()

        st.markdown("### Decision Autopilot · busca agentic controlada")
        st.caption("O LLM não calcula KPIs. O autopilot diagnostica, gera microdecisões, executa o DES e ranqueia resultados reais do modelo.")
        ap1,ap2,ap3=st.columns([1,1,1.3])
        with ap1:
            ap_sla=st.slider("Meta de SLA", 20, 100, 90, 5, key="v25_ap_sla")
        with ap2:
            ap_n=st.slider("Rotas finais", 3, 8, 5, 1, key="v25_ap_n")
        with ap3:
            if st.button("✦ Executar Decision Autopilot", type="primary", use_container_width=True, key="v25_ap_run"):
                with st.spinner("Diagnosis → Generate → Simulate → Rank → Handoff..."):
                    st.session_state.v25_autopilot=decision_autopilot(current_base_config(), base, float(ap_sla), int(ap_n))
                st.session_state.audit_log.append(audit_entry("autopilot","Decision Autopilot",f"Meta SLA {ap_sla}% · {len(st.session_state.v25_autopilot)} rotas"))
                st.rerun()
        if st.session_state.get("v25_autopilot"):
            ap=st.session_state.v25_autopilot
            agent_run_header(float(ap_sla),len(ap))
            ap_df=pd.DataFrame([{k:v for k,v in x.items() if k not in ["result","config","source"]} for x in ap])
            st.dataframe(ap_df,use_container_width=True,hide_index=True)
            best_ap=ap[0]
            aa,ab=st.columns(2)
            with aa:
                if st.button("Abrir melhor rota no Decision Review",use_container_width=True,key="v25_ap_review"):
                    st.session_state.scenario_result=best_ap["result"]; st.session_state.scenario_config=best_ap["config"]
                    register_decision(best_ap["action"],"Decision Autopilot",best_ap["result"])
                    st.session_state.active_page="Comparar"; st.rerun()
            with ab:
                if st.button("Levar rota ao Scenario Studio",use_container_width=True,key="v25_ap_studio"):
                    st.session_state.scenario_result=best_ap["result"]; st.session_state.scenario_config=best_ap["config"]
                    st.session_state.active_page="Murphy Lab"; st.rerun()

        st.markdown("### Conversa com a operação")
        st.caption("Pergunte em linguagem natural. Em modo generativo, os números continuam vindo do pacote estruturado do Anti-Murphy.")
        for msg in st.session_state.ai_messages[-12:]:
            with st.chat_message(msg.get("role", "assistant")):
                st.markdown(msg.get("content", ""))

        pending = st.session_state.pop("ai_pending_prompt", None)
        typed = st.chat_input("Ex.: Por que meu SLA está baixo? Vale mais operador ou máquina?")
        prompt = typed or pending
        if prompt:
            st.session_state.ai_messages.append({"role":"user", "content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            proposal_issued=False
            with st.chat_message("assistant"):
                proposed=propose_simulation(prompt,st.session_state.stations)
                if proposed:
                    st.session_state.v29_pending_proposal=proposed.as_dict()
                    proposal_issued=True
                    answer=f"Proponho simular uma parada de **{proposed.duration_h:g} h** em **{proposed.station}**, iniciando em **{proposed.start_h:g} h**. Revise o pedido acima e clique em **Autorizar simulação**. Nada foi executado ainda."
                elif connected:
                    try:
                        with st.spinner("Murphy AI verificando evidências..."):
                            answer,tool_proposal=call_optional_llm(effective_key,st.session_state.am_ai_model,prompt,ctx,st.session_state.stations)
                            if tool_proposal:
                                st.session_state.v29_pending_proposal=tool_proposal.as_dict()
                                proposal_issued=True
                    except Exception as exc:
                        answer=local_copilot_answer(prompt,ctx)+f"\n\n> **Modo local ativado:** serviço generativo indisponível ({type(exc).__name__})."
                else:
                    answer=local_copilot_answer(prompt,ctx)
                st.markdown(answer)
            st.session_state.ai_messages.append({"role":"assistant", "content":answer})
            if proposal_issued:
                st.rerun()  # Mostra os botões de autorização acima do chat.

        cc1,cc2 = st.columns([1,4])
        with cc1:
            if st.button("Limpar conversa", use_container_width=True, key="v22_clear"):
                st.session_state.ai_messages=[]
                st.rerun()
        with cc2:
            st.caption("Murphy AI pode propor e, após autorização, executar simulações internas; nunca atua na fábrica. Decisões reais exigem validação humana.")


    elif page == "Trust Center":
        base = ensure_base()
        mconf = model_confidence(st.session_state.stations, st.session_state.orders)
        cal = st.session_state.get("v24_calibration")
        mc = st.session_state.get("v24_mc")
        v16_page_head("AI / TRUST", "Model Trust Center", "Separe completude do cadastro, aderência ao mundo real e incerteza simulada antes de promover uma decisão.", "verify · validate · calibrate · quantify uncertainty")
        trust_header(float(mconf.get("score",0)), cal, mc, "local")
        cal_now=(st.session_state.get("v24_calibration") or {}).get("score")
        mc_now=(st.session_state.get("v24_mc") or {}).get("bottleneck_share")
        trust_dashboard(0.0,float(mconf.get("score",0)),cal_now,mc_now,float(mconf.get("score",0)))
        st.info("Cadastro e verificação interna não constituem validação fabril. Calibração e análise de incerteza só são exibidas quando houver dados/replicações correspondentes.")
        ai_context_bar("Trust Center: identifique separadamente lacunas de cadastro, verificação computacional, calibração real e análise de incerteza.")
        if st.button("✦ Perguntar ao Murphy AI como elevar a confiança",use_container_width=True,key="v26_trust_ai"):
            st.session_state.v26_ai_context=(f"Cadastro/verificação: {mconf.get('score',0):.0f}/100; "
                f"calibração real: {cal_now if cal_now is not None else 'pendente'}; "
                f"replicações de incerteza: {mc_now if mc_now is not None else 'não executadas'}. "
                "Esses números NÃO podem ser agregados em um índice de validação industrial.")
            st.session_state.active_page="Murphy AI"; st.rerun()

        t1,t2 = st.columns([1.02,.98], gap="medium")
        with t1:
            st.markdown("### Verification · estrutura e consistência")
            st.caption("Essas verificações dizem se o modelo está bem cadastrado; não provam que ele representa a fábrica real.")
            checks=pd.DataFrame([{"Check":label,"Status":"OK" if ok else "PENDENTE","Peso":w} for label,ok,w in mconf.get("checks",[])])
            st.dataframe(checks,use_container_width=True,hide_index=True)
            if mconf.get("missing"):
                st.warning("Pendências estruturais: "+", ".join(mconf.get("missing",[])))
            else:
                st.success("Estrutura cadastrada sem pendências nos checks internos.")

        with t2:
            st.markdown("### Validation · real × simulated")
            st.caption("Informe observações reais da operação. O Anti-Murphy apenas mede o desvio; ele não ajusta parâmetros silenciosamente.")
            c1,c2=st.columns(2)
            with c1:
                real_tp=st.number_input("Throughput real (un/h) · 0 = não informado",min_value=0.0,value=float(st.session_state.get("v24_real_tp",0.0)),step=0.1,key="v24_real_tp")
                real_mk=st.number_input("Makespan real (h) · 0 = não informado",min_value=0.0,value=float(st.session_state.get("v24_real_mk",0.0)),step=0.5,key="v24_real_mk")
            with c2:
                real_sla=st.number_input("SLA real (%) · 0 = não informado",min_value=0.0,max_value=100.0,value=float(st.session_state.get("v24_real_sla",0.0)),step=5.0,key="v24_real_sla")
                real_cost=st.number_input("Custo/un real (R$) · 0 = não informado",min_value=0.0,value=float(st.session_state.get("v24_real_cost",0.0)),step=1.0,key="v24_real_cost")
            if st.button("Calcular aderência real × simulado",use_container_width=True,key="v24_calibrate"):
                st.session_state.v24_calibration=calibration_summary(base,{"throughput":real_tp,"sla":real_sla,"makespan":real_mk,"unit_cost":real_cost})
                st.rerun()
            if st.session_state.get("v24_calibration"):
                cal=st.session_state.v24_calibration
                if cal.get("score") is not None:
                    st.metric("Calibration score",f"{cal['score']:.0f}/100",f"MAPE {cal['mape']:.1f}%")
                    st.dataframe(pd.DataFrame(cal.get("rows",[])),use_container_width=True,hide_index=True)
                else:
                    st.info("Informe pelo menos uma observação real maior que zero.")

        st.markdown("### Uncertainty · Monte Carlo do cenário-base")
        st.caption("Repete o mesmo modelo com sementes diferentes para medir dispersão interna. Não transforma incerteza simulada em probabilidade do mundo real.")
        mc1,mc2,mc3=st.columns([1,1,2])
        with mc1:
            mc_runs=st.slider("Replicações",4,40,12,2,key="v24_mc_runs")
        with mc2:
            mc_seed=st.number_input("Seed inicial",min_value=1,value=2400,step=10,key="v24_mc_seed")
        with mc3:
            if st.button("Executar evidência Monte Carlo",use_container_width=True,key="v24_mc_run"):
                with st.spinner("Executando replicações controladas..."):
                    st.session_state.v24_mc=monte_carlo_analysis(current_base_config(),int(mc_runs),int(mc_seed))
                st.rerun()
        if st.session_state.get("v24_mc"):
            mc=st.session_state.v24_mc
            monte_carlo_panel(mc)
            st.caption(f"Gargalo dominante: {mc.get('dominant_bottleneck','-')} em {mc.get('bottleneck_share',0):.0f}% das replicações.")

        st.markdown("### Parecer de evidência")
        if cal_now is None:
            st.warning("Validação com dados reais: PENDENTE. Nenhuma pontuação do cadastro permite afirmar precisão industrial.")
        else:
            st.info(f"Calibração informada: {cal_now:.0f}/100. É uma comparação com os valores inseridos, não homologação industrial.")
        if mc_now is None:
            st.caption("Estabilidade de replicações: não avaliada nesta sessão.")
        else:
            st.caption(f"Gargalo dominante em {mc_now:.0f}% das replicações sintéticas. Não equivale a probabilidade industrial.")

    elif page == "Operations Studio":
        base = ensure_base()
        v16_page_head("MODEL / OPERATIONS", "Operations Studio", "Modele a camada humana e operacional que costuma ficar fora dos simuladores: calendário, competências, confiabilidade e política de setup.", "calendar · skills · reliability · process policy")
        module_hero("OPERATIONAL TWIN LAYER", "Da máquina isolada ao sistema de trabalho.", "Esta área organiza metadados industriais que tornam o Decision Twin mais auditável e preparado para calibração. Somente parâmetros explicitamente aplicados alteram o motor DES.", ["Turnos", "Skills", "MTBF / MTTR", "Setup"])
        executive_strip([("WORKFORCE",f"{workers_total} pessoas","quadro declarado","#0B171A"),("STATIONS",f"{len(st.session_state.stations)}","cobertura operacional","#0B171A"),("LAYER","Human + Assets","calendário, skills e reliability","#3E9B91"),("POLICY","Explicit apply","nada altera o DES silenciosamente","#FF681B")])

        st.markdown("### Production Calendar")
        st.caption("Organize a capacidade temporal da operação. Nesta V26 o calendário funciona como camada de governança e planejamento; não altera silenciosamente o relógio do DES.")
        if "v25_shifts" not in st.session_state:
            st.session_state.v25_shifts = pd.DataFrame([
                {"Turno":"Turno A","Início":"06:00","Fim":"14:00","Horas/dia":8.0,"Dias/sem":5,"Pessoas":max(1,workers_total//2)},
                {"Turno":"Turno B","Início":"14:00","Fim":"22:00","Horas/dia":8.0,"Dias/sem":5,"Pessoas":max(1,workers_total-workers_total//2)},
            ])
        shift_df=st.data_editor(st.session_state.v25_shifts,num_rows="dynamic",use_container_width=True,hide_index=True,key="v25_shift_editor")
        sh1,sh2,sh3=st.columns(3)
        weekly_hours=float((shift_df["Horas/dia"].fillna(0)*shift_df["Dias/sem"].fillna(0)).sum()) if len(shift_df) else 0.0
        coverage_people=int(shift_df["Pessoas"].fillna(0).sum()) if len(shift_df) else 0
        with sh1: st.metric("Horas de calendário / semana",f"{weekly_hours:.0f} h")
        with sh2: st.metric("Alocações declaradas",str(coverage_people))
        with sh3: st.metric("Cobertura vs quadro",f"{(coverage_people/max(1,workers_total))*100:.0f}%")
        if st.button("Salvar calendário operacional",use_container_width=True,key="v25_save_shifts"):
            st.session_state.v25_shifts=shift_df.copy(); st.session_state.audit_log.append(audit_entry("model","Production Calendar",f"{len(shift_df)} turno(s) · {weekly_hours:.0f} h/sem")); st.success("Calendário salvo no workspace.")

        st.markdown("### Skills Matrix · cobertura e dependência humana")
        st.caption("Defina quais postos cada operador consegue cobrir. O score mede redundância de competências, não produtividade individual.")
        if "v25_skill_df" not in st.session_state:
            skill_rows=[]
            n=max(1,workers_total)
            station_ids=list(st.session_state.stations.keys())
            for i in range(n):
                primary=station_ids[i%len(station_ids)] if station_ids else ""
                skill_rows.append({"Operador":f"OP-{i+1:02d}","Competências":primary,"Proficiência média (%)":100})
            st.session_state.v25_skill_df=pd.DataFrame(skill_rows)
        skill_df=st.data_editor(st.session_state.v25_skill_df,num_rows="dynamic",use_container_width=True,hide_index=True,key="v25_skill_editor")
        skill_map={}
        for _,r in skill_df.iterrows():
            worker=str(r.get("Operador","")).strip()
            skills=[x.strip().upper() for x in str(r.get("Competências","")).replace(";",",").split(",") if x.strip()]
            if worker: skill_map[worker]=skills
        cov=skill_coverage(st.session_state.stations,skill_map)
        sk1,sk2,sk3=st.columns(3)
        with sk1: st.metric("Skills coverage",f"{cov.get('score',0):.0f}/100")
        with sk2: st.metric("Postos sem backup",len(cov.get('gaps',[])))
        with sk3: st.metric("Single points",len(cov.get('single_points',[])))
        if cov.get('gaps'): st.warning("Sem cobertura declarada: "+", ".join(cov.get('gaps',[])))
        elif cov.get('single_points'): st.info("Conhecimento concentrado em uma pessoa: "+", ".join(cov.get('single_points',[])))
        else: st.success("Todos os postos possuem pelo menos duas coberturas declaradas.")
        with st.expander("Visualizar mapa de cobertura",expanded=True):
            st.plotly_chart(skill_heatmap(skill_df,list(st.session_state.stations.keys())),use_container_width=True)
        if st.button("Salvar matriz de competências",use_container_width=True,key="v25_save_skills"):
            st.session_state.v25_skill_df=skill_df.copy(); st.session_state.v25_skills=skill_map; st.session_state.audit_log.append(audit_entry("model","Skills Matrix",f"coverage {cov.get('score',0):.0f}/100")); st.success("Skills Matrix salva.")

        st.markdown("### Asset Reliability Board")
        st.caption("MTBF e MTTR informados pelo usuário alimentam um lens transparente de probabilidade de falha e exposição de downtime.")
        if "v25_rel_df" not in st.session_state:
            st.session_state.v25_rel_df=pd.DataFrame([{"Posto":sid,"MTBF (h)":120.0,"MTTR (h)":3.0,"Custo downtime/h (R$)":350.0} for sid in st.session_state.stations])
        rel_df=st.data_editor(st.session_state.v25_rel_df,use_container_width=True,hide_index=True,key="v25_rel_editor")
        horizon=st.slider("Horizonte de confiabilidade (h)",8,336,72,8,key="v25_rel_horizon")
        rel_inputs={str(r['Posto']):{"mtbf_h":float(r['MTBF (h)']),"mttr_h":float(r['MTTR (h)'])} for _,r in rel_df.iterrows() if str(r.get('Posto','')) in st.session_state.stations}
        avg_cost=float(rel_df["Custo downtime/h (R$)"].mean()) if len(rel_df) else 0.0
        rel_rows=reliability_analysis(st.session_state.stations,rel_inputs,float(horizon),avg_cost)
        if rel_rows:
            reliability_strip(rel_rows[0])
            with st.expander("Todos os ativos",expanded=False): st.dataframe(pd.DataFrame(rel_rows),use_container_width=True,hide_index=True)
        if st.button("Salvar confiabilidade",use_container_width=True,key="v25_save_rel"):
            st.session_state.v25_rel_df=rel_df.copy(); st.session_state.v25_reliability=rel_rows; st.session_state.audit_log.append(audit_entry("model","Reliability Board",f"horizonte {horizon}h")); st.success("Parâmetros de confiabilidade salvos.")

        st.markdown("### Process Policy · setup aplicado ao DES")
        st.caption("Diferente das camadas acima, o setup abaixo já é um parâmetro ativo do motor de simulação. Aplique somente quando quiser reconstruir o cenário-base.")
        setup_df=pd.DataFrame([{"Posto":sid,"Nome":x.get('nome',sid),"Setup atual (min)":float(x.get('setup_min',0))} for sid,x in st.session_state.stations.items()])
        setup_edit=st.data_editor(setup_df,use_container_width=True,hide_index=True,key="v25_setup_editor")
        if st.button("Aplicar setups ao modelo e recalcular",type="primary",use_container_width=True,key="v25_apply_setup"):
            for _,r in setup_edit.iterrows():
                sid=str(r['Posto'])
                if sid in st.session_state.stations: st.session_state.stations[sid]['setup_min']=max(0.0,float(r['Setup atual (min)']))
            reset_analysis_state(); st.session_state.audit_log.append(audit_entry("model","Setup Policy","setups aplicados ao motor DES")); st.success("Setups aplicados. O cenário-base será recalculado."); st.rerun()

    elif page == "Modelar":
        v16_page_head("01 / MODEL", "Modelo da operação", "Construa o sistema produtivo, importe dados e mantenha uma única fonte de verdade para a simulação.", "estrutura · ordens · dados")
        model_quality_strip(st.session_state.stations, st.session_state.orders)
        model_confidence_panel(model_confidence(st.session_state.stations, st.session_state.orders))
        module_hero("MODEL FOUNDATION", "A fábrica antes da simulação.", "Modele recursos e roteiros com precisão. A tabela continua disponível como modo avançado, mas a leitura visual passa a mostrar rapidamente capacidade, cobertura de mão de obra e parâmetros de cada posto.", ["Quick Builder", "Data Bridge", "Modo avançado", "Backup do modelo"])
        base_for_model = ensure_base()
        model_flow(st.session_state.stations, base_for_model.get("bottleneck"))

        st.markdown("### Visual Model Editor")
        st.caption("Selecione um posto, ajuste propriedades e aplique. A tabela completa fica reservada ao modo avançado.")
        edit_sid = st.selectbox("Posto para editar", list(st.session_state.stations.keys()),
                                format_func=lambda x: f"{x} · {st.session_state.stations[x]['nome']}", key="v20_edit_station")
        edit_s = st.session_state.stations[edit_sid]
        station_edit_header(edit_sid, edit_s.get("nome", edit_sid))
        with st.form("v20_visual_station_form", clear_on_submit=False):
            ve1,ve2,ve3,ve4 = st.columns(4)
            with ve1:
                ve_name = st.text_input("Nome do posto", value=str(edit_s.get("nome",edit_sid)), key=f"v20_ve_name_{edit_sid}")
                ve_m = st.number_input("Máquinas", 1, 30, int(edit_s.get("maquinas",1)), 1, key=f"v20_ve_m_{edit_sid}")
            with ve2:
                ve_w = st.number_input("Operadores", 0, 60, int(edit_s.get("operadores",0)), 1, key=f"v20_ve_w_{edit_sid}")
                ve_opm = st.number_input("Operadores/máquina", 0.25, 5.0, float(edit_s.get("operadores_por_maquina",1.0)), 0.25, key=f"v20_ve_opm_{edit_sid}")
            with ve3:
                ve_av = st.slider("Disponibilidade", 0.50, 1.00, float(edit_s.get("disponibilidade",1.0)), 0.01, key=f"v20_ve_av_{edit_sid}")
                ve_eff = st.slider("Eficiência do operador", 0.55, 1.20, float(edit_s.get("eficiencia_operador",1.0)), 0.01, key=f"v20_ve_eff_{edit_sid}")
            with ve4:
                ve_setup = st.number_input("Setup (min)", 0.0, 480.0, float(edit_s.get("setup_min",0.0)), 1.0, key=f"v20_ve_setup_{edit_sid}")
                ve_mc = st.number_input("Custo máquina/h", 0.0, 100000.0, float(edit_s.get("custo_maquina_h",0.0)), 1.0, key=f"v20_ve_mc_{edit_sid}")
            ve_wc = st.number_input("Custo operador/h", 0.0, 10000.0, float(edit_s.get("custo_operador_h",0.0)), 1.0, key=f"v20_ve_wc_{edit_sid}")
            ve_submit = st.form_submit_button("Aplicar alterações ao posto", use_container_width=True, type="primary")
        if ve_submit:
            st.session_state.stations[edit_sid].update({
                "nome":ve_name.strip() or edit_sid, "setor":ve_name.strip() or edit_sid,
                "maquinas":int(ve_m), "operadores":int(ve_w), "operadores_por_maquina":float(ve_opm),
                "disponibilidade":float(ve_av), "eficiencia_operador":float(ve_eff),
                "setup_min":float(ve_setup), "custo_maquina_h":float(ve_mc), "custo_operador_h":float(ve_wc),
            })
            reset_analysis_state()
            st.success(f"{edit_sid} atualizado no modelo.")
            st.rerun()

        st.markdown("### Estrutura produtiva")
        st.caption("Adicione ou remova postos diretamente na tabela. IDs são usados nos roteiros das ordens (ex.: CORTE, CNC, SOLDA).")
        df, odf = frames_from_current()

        with st.expander("＋ Quick Builder · adicionar um posto sem editar a tabela", expanded=False):
            qb1,qb2,qb3,qb4 = st.columns(4)
            with qb1:
                qb_id = st.text_input("ID do posto", placeholder="INSPECAO", key="qb_id")
                qb_name = st.text_input("Nome", placeholder="Inspeção final", key="qb_name")
            with qb2:
                qb_m = st.number_input("Máquinas", 1, 30, 1, key="qb_m")
                qb_w = st.number_input("Operadores", 0, 60, 1, key="qb_w")
            with qb3:
                qb_av = st.slider("Disponibilidade", 0.50, 1.00, 0.95, 0.01, key="qb_av")
                qb_eff = st.slider("Eficiência", 0.55, 1.20, 0.95, 0.01, key="qb_eff")
            with qb4:
                qb_setup = st.number_input("Setup (min)", 0.0, 480.0, 5.0, 1.0, key="qb_setup")
                qb_cost = st.number_input("Custo máquina/h", 0.0, 100000.0, 30.0, 5.0, key="qb_cost")
            if st.button("Adicionar posto ao modelo", use_container_width=True, key="qb_add"):
                sid = normalize_station_id(qb_id)
                if not sid or not qb_name.strip():
                    st.error("Informe ID e nome do posto.")
                elif sid in st.session_state.stations:
                    st.error(f"O posto {sid} já existe.")
                else:
                    st.session_state.stations[sid] = {"nome":qb_name.strip(),"setor":qb_name.strip(),"maquinas":int(qb_m),"operadores":int(qb_w),"operadores_por_maquina":1.0,"eficiencia_operador":float(qb_eff),"disponibilidade":float(qb_av),"custo_operador_h":25.0,"custo_maquina_h":float(qb_cost),"setup_min":float(qb_setup),"icone":"◇"}
                    reset_analysis_state(); st.success(f"Posto {sid} adicionado."); st.rerun()

        with st.expander("↥ Data Bridge · importar dados reais do cliente", expanded=False):
            st.caption("Importe Excel (.xlsx) com abas Postos/Ordens ou um CSV. O Anti-Murphy reconhece nomes comuns de colunas e valida o modelo antes de usar os dados.")
            up1, up2 = st.columns([1.5, 1])
            with up1:
                client_file = st.file_uploader("Planilha do cliente", type=["xlsx", "csv"], key="client_import")
            with up2:
                template = make_template(df, odf)
                st.download_button("↓ Baixar modelo Excel", data=template, file_name="anti_murphy_modelo_cliente.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            if client_file is not None:
                try:
                    imp_st, imp_or, warnings = read_client_workbook(client_file)
                    for msg in warnings:
                        st.warning(msg)
                    p1, p2 = st.columns(2)
                    with p1:
                        st.markdown("**Postos reconhecidos**")
                        st.dataframe(imp_st if imp_st is not None else pd.DataFrame(), use_container_width=True, hide_index=True, height=180)
                    with p2:
                        st.markdown("**Ordens reconhecidas**")
                        st.dataframe(imp_or if imp_or is not None else pd.DataFrame(), use_container_width=True, hide_index=True, height=180)
                    if st.button("Validar e carregar dados no Anti-Murphy", type="primary", use_container_width=True, key="apply_import"):
                        final_st = imp_st if imp_st is not None else df
                        final_or = imp_or if imp_or is not None else odf
                        new_stations, new_orders = frames_to_model(final_st, final_or)
                        st.session_state.stations = new_stations
                        st.session_state.orders = new_orders
                        reset_analysis_state()
                        st.success(f"Data Bridge concluído: {len(new_stations)} postos e {len(new_orders)} ordens carregados.")
                        st.rerun()
                except Exception as exc:
                    st.error(f"Não foi possível interpretar a planilha: {exc}")

        with st.expander("Modo avançado · tabela completa de postos", expanded=False):
            edited = st.data_editor(
                df, use_container_width=True, hide_index=True, num_rows="dynamic", key="station_editor",
                column_config={
                    "ID": st.column_config.TextColumn(help="Código curto e único, sem espaços. Ex.: INSPECAO"),
                    "Posto": st.column_config.TextColumn(required=True),
                    "Máquinas": st.column_config.NumberColumn(min_value=1, max_value=30, step=1),
                    "Operadores": st.column_config.NumberColumn(min_value=0, max_value=60, step=1),
                    "Operadores/máquina": st.column_config.NumberColumn(min_value=0.25, max_value=5.0, step=0.25),
                    "Eficiência operador": st.column_config.NumberColumn(min_value=0.55, max_value=1.20, step=0.01, format="%.2f"),
                    "Disponibilidade": st.column_config.NumberColumn(min_value=0.50, max_value=1.00, step=0.01, format="%.2f"),
                    "Setup (min)": st.column_config.NumberColumn(min_value=0.0, max_value=480.0, step=1.0),
                    "Custo operador/h": st.column_config.NumberColumn(min_value=0.0, max_value=10000.0, step=1.0),
                    "Custo máquina/h": st.column_config.NumberColumn(min_value=0.0, max_value=100000.0, step=1.0),
                }
            )

        st.markdown("### Carteira de ordens")
        st.caption("Também é possível adicionar novas OPs. Em Roteiro, use POSTO:minutos separados por ponto e vírgula. Ex.: CORTE:4; CNC:9; PINTURA:5; MONTAGEM:6")
        with st.expander("Modo avançado · tabela completa de ordens", expanded=False):
            oedited = st.data_editor(
                odf, use_container_width=True, hide_index=True, num_rows="dynamic", key="order_editor",
                column_config={
                    "ID": st.column_config.TextColumn(help="Código único da ordem. Ex.: OP-106"),
                    "Cliente": st.column_config.TextColumn(required=True),
                    "Produto": st.column_config.TextColumn(required=True),
                    "Quantidade": st.column_config.NumberColumn(min_value=1, max_value=100000, step=1),
                    "Prazo (h)": st.column_config.NumberColumn(min_value=0.1, max_value=100000.0, step=0.5),
                    "Multa/h (R$)": st.column_config.NumberColumn(min_value=0.0, max_value=10000000.0, step=10.0),
                    "Prioridade": st.column_config.NumberColumn(min_value=1, max_value=9, step=1),
                    "Roteiro": st.column_config.TextColumn(width="large", help="Formato: POSTO:minutos; POSTO:minutos"),
                }
            )

        with st.expander("⇢ Route Builder · criar uma OP visualmente", expanded=False):
            rb1,rb2,rb3 = st.columns(3)
            with rb1:
                ro_id=st.text_input("ID da nova OP", placeholder="OP-106", key="ro_id")
                ro_client=st.text_input("Cliente", placeholder="Cliente X", key="ro_client")
            with rb2:
                ro_product=st.text_input("Produto", placeholder="Produto A", key="ro_product")
                ro_qty=st.number_input("Quantidade",1,100000,10,key="ro_qty")
            with rb3:
                ro_dead=st.number_input("Prazo (h)",0.1,100000.0,24.0,0.5,key="ro_dead")
                ro_priority=st.number_input("Prioridade",1,9,3,key="ro_priority")
            route_ids=st.multiselect("Fluxo da OP · selecione na ordem desejada", list(st.session_state.stations.keys()), key="ro_route")
            default_times=", ".join(["5" for _ in route_ids])
            ro_times=st.text_input("Tempos por etapa (min) · na mesma ordem", value=default_times, key="ro_times")
            if route_ids:
                try:
                    vals=[float(x.strip().replace(",",".")) for x in ro_times.replace(";",",").split(",") if x.strip()]
                    preview=" → ".join(f"{sid} ({vals[i]:g} min)" if i < len(vals) else f"{sid} (?)" for i,sid in enumerate(route_ids))
                    st.caption("Fluxo: "+preview)
                except Exception:
                    vals=[]
            else:
                vals=[]
            if st.button("Adicionar OP à carteira", use_container_width=True, key="ro_add"):
                oid=str(ro_id).strip().upper()
                if not oid or not ro_client.strip() or not ro_product.strip() or not route_ids:
                    st.error("Preencha ID, cliente, produto e ao menos uma etapa.")
                elif any(o.get("id")==oid for o in st.session_state.orders):
                    st.error(f"A ordem {oid} já existe.")
                elif len(vals)!=len(route_ids) or any(v<=0 for v in vals):
                    st.error("Informe um tempo positivo para cada etapa selecionada.")
                else:
                    st.session_state.orders.append({"id":oid,"cliente":ro_client.strip(),"produto":ro_product.strip(),"quantidade":int(ro_qty),"prazo_h":float(ro_dead),"multa_hora":0.0,"prioridade":int(ro_priority),"route":list(zip(route_ids,vals))})
                    reset_analysis_state(); st.success(f"{oid} adicionada à carteira."); st.rerun()

        c_apply, c_hint = st.columns([1, 2.5])
        with c_apply:
            apply_model = st.button("Aplicar alterações", type="primary", use_container_width=True)
        with c_hint:
            st.caption("Ao aplicar, o cenário-base é recalculado e os experimentos anteriores são descartados para manter a comparação coerente.")

        if apply_model:
            try:
                new_stations, new_orders = frames_to_model(edited, oedited)
                st.session_state.stations = new_stations
                st.session_state.orders = new_orders
                reset_analysis_state()
                st.success(f"Modelo atualizado: {len(new_stations)} postos e {len(new_orders)} ordens.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível aplicar o modelo: {exc}")

        st.markdown("#### Portabilidade do modelo")
        e1, e2 = st.columns(2)
        with e1:
            export_xlsx = make_template(edited, oedited)
            st.download_button("↓ Exportar modelo atual (.xlsx)", data=export_xlsx, file_name="anti_murphy_modelo_atual.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with e2:
            model_json = json.dumps({"stations": st.session_state.stations, "orders": st.session_state.orders}, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button("↓ Backup técnico (.json)", data=model_json, file_name="anti_murphy_modelo.json", mime="application/json", use_container_width=True)

        with st.expander("Workspace portability · salvar e restaurar projeto", expanded=False):
            ws_payload = workspace_payload(st.session_state.stations, st.session_state.orders, st.session_state.decision_history)
            st.download_button("↓ Exportar workspace V23", data=json.dumps(ws_payload,ensure_ascii=False,indent=2,default=str).encode("utf-8"), file_name="anti_murphy_workspace_v27.json", mime="application/json", use_container_width=True, key="v23_ws_export")
            ws_file=st.file_uploader("Restaurar workspace JSON", type=["json"], key="v23_ws_import")
            if ws_file is not None and st.button("Validar e restaurar workspace", use_container_width=True, key="v23_ws_restore"):
                try:
                    payload=json.loads(ws_file.getvalue().decode("utf-8"))
                    if payload.get("format") != "ANTI-MURPHY-WORKSPACE":
                        raise ValueError("arquivo não é um workspace Anti-Murphy")
                    stations=payload.get("stations") or {}
                    orders=payload.get("orders") or []
                    if not isinstance(stations,dict) or not isinstance(orders,list) or not stations or not orders:
                        raise ValueError("estrutura de stations/orders inválida")
                    # normalize routes that were serialized as lists
                    for o in orders:
                        if "route" in o:
                            o["route"]=[tuple(x) for x in o["route"]]
                    st.session_state.stations=stations
                    st.session_state.orders=orders
                    st.session_state.decision_history=[]
                    reset_analysis_state()
                    st.success("Workspace restaurado. O cenário-base será recalculado.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Não foi possível restaurar o workspace: {exc}")


    elif page == "Visão 360":
        base = ensure_base()
        resilience = resilience_index(base)
        recommendations = copilot_recommendations(base, st.session_state.stations)
        alerts = operating_alerts(base)
        v16_page_head("00 / CONTROL ROOM", "Centro de decisão", "Um cockpit operacional para entender o estado do sistema, localizar a restrição e transformar sinais em experimentos.", "observe → explique → teste → decida")
        executive_pulse(base, resilience, recommendations)
        metric_rail(base, resilience, murphy_score(base))

        workspace_label("LIVE DECISION TWIN", "modelo ativo · fluxo e restrição em tempo simulado")
        twin_col, intel_col = st.columns([2.55, 0.85], gap="medium")
        with twin_col:
            render_cinematic_twin(base)
        with intel_col:
            confidence = int(min(92, 64 + len(st.session_state.decision_history)*3 + (8 if recommendations else 0)))
            intelligence_panel(base, resilience, recommendations, alerts, confidence)

        signal_strip(base, resilience, recommendations)
        economics_strip(base)
        pressure_strip(station_pressure(base))
        rc = root_cause_explorer(base)
        root_cause_panel(rc)
        with st.expander("Root Cause Explorer · decompor a pressão do sistema", expanded=False):
            st.plotly_chart(root_cause_chart(rc), use_container_width=True)
            st.dataframe(pd.DataFrame(rc.get("rows",[])), use_container_width=True, hide_index=True)

        st.markdown("### Context Inspector")
        ci1,ci2=st.columns([1.25,.75],gap="medium")
        with ci1:
            station_ids_focus = [x.get("Posto") for x in base.get("stations", [])]
            default_focus = station_ids_focus.index(base.get("bottleneck")) if base.get("bottleneck") in station_ids_focus else 0
            focus_id = st.selectbox("Posto em foco", station_ids_focus, index=default_focus, key="v17_station_focus", label_visibility="collapsed")
            focus_row = next((x for x in base.get("stations", []) if x.get("Posto") == focus_id), base.get("stations", [{}])[0])
            share=next((float(x.get("share_pct",0)) for x in rc.get("rows",[]) if x.get("station")==focus_id),0.0)
            context_inspector(focus_row,share)
        with ci2:
            ai_context_bar(f"Posto {focus_id}: pressione, fila, espera e capacidade já carregadas como contexto.")
            if st.button("✦ Ask Murphy about this station",use_container_width=True,key="v26_station_ai"):
                st.session_state.v26_ai_context=f"Analise o posto {focus_id} ({focus_row.get('Nome','')}): utilização {focus_row.get('Utilização máquina (%)',0):.1f}%, espera {focus_row.get('Espera média (min)',0):.1f} min, fila máxima {focus_row.get('Fila máx.',0)}, pressure share {share:.0f}%. Explique causa, risco e qual experimento testar."
                st.session_state.active_page="Murphy AI"; st.rerun()
            if st.button("↯ Testar este posto no Scenario Studio",use_container_width=True,key="v26_station_test"):
                st.session_state.studio_target=focus_id; st.session_state.active_page="Murphy Lab"; st.rerun()

        with st.expander("Análises profundas · causal trace, replay, copilot e telemetria", expanded=False):
            tab_trace, tab_replay, tab_copilot, tab_brief = st.tabs(["Causal trace", "Black Box Replay", "Murphy Copilot", "Executive Brief"])
            with tab_trace:
                causal_chain(base)
                render_propagation_map(base, base["bottleneck"])
            with tab_replay:
                render_replay(base)
            with tab_copilot:
                render_copilot_panel(recommendations, resilience)
                st.caption("Recomendações são heurísticas transparentes construídas sobre o resultado da simulação.")
            with tab_brief:
                bottleneck = next(r for r in base["stations"] if r["Posto"] == base["bottleneck"])
                b1,b2 = st.columns([1.15,.85])
                with b1:
                    st.markdown(f"### O que exige atenção agora")
                    st.markdown(f"**{base['bottleneck']} · {bottleneck['Nome']}** concentra a pressão sistêmica. A fila máxima chegou a **{bottleneck['Fila máx.']}**, a espera média a **{bottleneck['Espera média (min)']:.1f} min** e o SLA está em **{base['sla_pct']:.0f}%**.")
                    st.markdown(f"A exposição financeira por atraso no lote simulado é de **R$ {base.get('penalty_total',0):,.2f}**. O índice de resiliência está em **{resilience['score']:.0f}/100 · {resilience['band']}**.")
                with b2:
                    st.dataframe(pd.DataFrame(base["orders"])[["OP","Cliente","Status","Atraso (h)","Multa (R$)"]], use_container_width=True, hide_index=True, height=230)

            st.markdown("### Demo narrativa")
            demo_a, demo_b = st.columns([1.55, .75])
            with demo_a:
                st.caption("Apresenta automaticamente o arco Anti-Murphy: operação-base → perturbação → decisão → recuperação. Feito para apresentação e demonstração executiva.")
            with demo_b:
                if st.button("▶ Executar narrativa Murphy", type="primary", use_container_width=True):
                    bn = base["bottleneck"]
                    crisis_cfg = current_base_config().clone(name="Demo · Evento Murphy")
                    crisis_cfg.chaos_station = bn
                    crisis_cfg.chaos_start_h = 4.0
                    crisis_cfg.chaos_duration_h = 4.0
                    if crisis_cfg.stations[bn].get("operadores", 0) > 1:
                        crisis_cfg.absent_workers = {bn: 1}
                    crisis = run_simulation(crisis_cfg)
                    recovery_cfg = crisis_cfg.clone(name="Demo · Resposta Anti-Murphy")
                    bstats = next(x for x in base["stations"] if x["Posto"] == bn)
                    needed = recovery_cfg.stations[bn].get("maquinas", 1) * recovery_cfg.stations[bn].get("operadores_por_maquina", 1)
                    if recovery_cfg.stations[bn].get("operadores", 0) < needed or bstats.get("Utilização mão de obra (%)", 0) >= 88:
                        recovery_cfg.stations[bn]["operadores"] += 1
                        intervention = f"+1 operador em {bn}"
                    else:
                        recovery_cfg.stations[bn]["maquinas"] += 1
                        intervention = f"+1 máquina em {bn}"
                    recovery_cfg.chaos_duration_h = 1.5
                    recovery = run_simulation(recovery_cfg)
                    st.session_state.demo_story = (crisis, recovery, intervention)
            if "demo_story" in st.session_state:
                crisis, recovery, intervention = st.session_state.demo_story
                render_demo_story(base, crisis, recovery, intervention)

            st.markdown("### Telemetria operacional")
            left,right = st.columns([1.28,1], gap="medium")
            with left:
                st.plotly_chart(utilization_chart(base), use_container_width=True)
            with right:
                render_alert_center(alerts, height=310)

    elif page == "Decision Evidence":
        v16_page_head("03 / DECISION", "Decision Evidence Studio", "Mesmo incidente. Mesma demanda. Mesma semente. Decisões comparáveis, custo de implantação e transparência nas premissas.", "observe · stress · compare · decide")
        st.caption("V29.1 · Motor de eventos reproduzível + War Room · Todas as simulações são sintéticas; nenhuma economia está validada em fábrica real.")
        issues = validate_model(st.session_state.stations, st.session_state.orders)
        if issues:
            st.error("Corrija o modelo antes de simular: " + " | ".join(issues[:5]))
        else:
            sids = list(st.session_state.stations)
            a,b,c,d = st.columns(4)
            with a:
                incident_sid = st.selectbox("Posto afetado", sids, index=sids.index("CNC") if "CNC" in sids else 0, key="v27_sid")
            with b:
                outage_start = st.number_input("Início da falha (h)", min_value=0., max_value=1000., value=4., step=.5, key="v27_start")
            with c:
                outage_length = st.number_input("Duração da falha (h)", min_value=0.5, max_value=168., value=5., step=.5, key="v27_duration")
            with d:
                budget = st.number_input("Teto de investimento (R$) · 0 = livre", min_value=0., value=10000., step=1000., key="v27_budget")
            opt1,opt2,opt3,opt4 = st.columns(4)
            with opt1: cost_worker = st.number_input("Custo inicial / operador (R$)", min_value=0.,value=1200.,step=100.,key="v27_cw")
            with opt2: cost_machine = st.number_input("Custo inicial / máquina (R$)", min_value=0.,value=6500.,step=500.,key="v27_cm")
            with opt3: cost_express = st.number_input("Manutenção expressa (R$)", min_value=0.,value=1800.,step=100.,key="v27_ce")
            with opt4: sla_floor = st.slider("SLA mínimo (%)",0,100,80,5,key="v27_sla_floor")
            st.caption("Custos acima são hipóteses editáveis para a demonstração, NÃO preços de mercado confirmados. Investimento é lançado integralmente nesta carteira de ordens.")
            input_stamp = (config_signature(current_base_config()), incident_sid, outage_start, outage_length, budget, cost_worker, cost_machine, cost_express, sla_floor)
            if st.button("▶ SIMULAR FALHA E COMPARAR RESPOSTAS", key="v27_go", type="primary",use_container_width=True):
                icfg=current_base_config().clone("Incidente sem intervenção")
                icfg.chaos_station=incident_sid
                icfg.chaos_start_h=outage_start
                icfg.chaos_duration_h=outage_length
                with st.spinner("Executando alternativas pareadas..."):
                    st.session_state.v27_decisions=evaluate_decisions(icfg,budget=budget,sla_floor=sla_floor,
                        cost_worker=cost_worker,cost_machine=cost_machine,cost_express=cost_express)
                    st.session_state.v27_incident=icfg
                    st.session_state.v27_stamp=input_stamp
                    st.session_state.pop("v27_robustness",None)
            if 'v27_decisions' not in st.session_state:
                st.info("Configure uma falha e clique em Simular. Para o pitch: comece com o posto CNC, 4h de início e 5h de duração.")
            elif st.session_state.get('v27_stamp') != input_stamp:
                st.warning("Os parâmetros ou o modelo mudaram. Execute novamente para evitar análise de resultados antigos.")
            else:
                data=st.session_state.v27_decisions
                incident=data['incident']; normal=data['normal']; rows=data['rows']
                if not incident.get('feasible',True):
                    st.error('Cenário sem recursos necessários: '+ ' | '.join(incident.get('warnings',[])))
                    st.info('Corrija a alocação de operadores no Modelar antes de considerar decisões econômicas.')
                else:
                    st.markdown("### 1 · A crise tem impacto mensurável?")
                    k1,k2,k3,k4 = st.columns(4)
                    with k1: st.metric("Custo sem falha",f"R$ {normal['total_cost']:,.0f}")
                    with k2: st.metric("Custo com falha",f"R$ {incident['total_cost']:,.0f}",f"R$ {incident['total_cost']-normal['total_cost']:+,.0f} vs normal",delta_color="inverse")
                    with k3: st.metric("SLA com falha",f"{incident['sla_pct']:.0f}%",f"{incident['sla_pct']-normal['sla_pct']:+.1f} p.p.")
                    with k4: st.metric("Tempo para concluir",f"{incident['makespan_h']:.1f} h",f"{incident['makespan_h']-normal['makespan_h']:+.1f} h",delta_color="inverse")
                    st.markdown("### 2 · Alternativas sob o MESMO incidente")
                    valid=[r for r in rows if r['feasible'] and r['within_budget']]
                    view=[{
                        'Ação':r['action'],'Custo total + implantação (R$)':r['decision_cost'],
                        'Economia vs. não intervir (R$)':r['savings'], 'SLA (%)':r['sla_pct'],
                        'Makespan (h)':r['makespan_h'],'Investimento (R$)':r['investment'],
                        'Pareto': 'Sim' if r['pareto'] else 'Não',
                        'Veredito': r.get('verdict','-'),
                        'Condição':'Aprovável no modelo' if r['feasible'] and r['within_budget'] and r['meets_sla'] else 'Restrição não atendida'
                    } for r in rows]
                    st.dataframe(pd.DataFrame(view),use_container_width=True,hide_index=True,height=375)
                    if valid:
                        import plotly.graph_objects as go
                        fig=go.Figure()
                        fig.add_trace(go.Scatter(x=[r['decision_cost'] for r in valid],y=[r['makespan_h'] for r in valid],
                            mode='markers+text',text=[r['action'] if r['pareto'] else '' for r in valid],textposition='top center',
                            marker=dict(size=[16 if r['pareto'] else 9 for r in valid],color=['#f47b32' if r['pareto'] else '#94a3b8' for r in valid]),
                            customdata=[[r['action'],r['sla_pct']] for r in valid],
                            hovertemplate='%{customdata[0]}<br>Custo: R$ %{x:,.2f}<br>Tempo: %{y:.2f}h<br>SLA: %{customdata[1]:.1f}%<extra></extra>'))
                        fig.update_layout(title='Trade-off · custo total da decisão × tempo de conclusão',xaxis_title='Custo operacional + multa + investimento (R$)',yaxis_title='Conclusão da carteira (h)',height=400,margin=dict(l=15,r=15,t=55,b=10))
                        st.plotly_chart(fig,use_container_width=True)
                    st.markdown("### 3 · Escolha justificada e evidências")
                    possible=[r for r in rows if r['feasible'] and r['within_budget'] and r['meets_sla']]
                    if data.get('recommended'):
                        rec=data['recommended']
                        st.success(f"Recomendação líder do War Room: {rec.get('action','-')} · {rec.get('verdict','-')}")
                        st.caption(rec.get('tradeoff_note',''))
                    if not possible:
                        st.warning('Nenhuma alternativa testada atende ao SLA mínimo e ao orçamento. Revise as restrições ou melhore o modelo.')
                    selectable=possible if possible else [r for r in rows if r['feasible']]
                    if selectable:
                        names=[r['action'] for r in selectable]
                        selection=st.selectbox("Ação a investigar",names,key="v27_select")
                        picked=next(r for r in selectable if r['action']==selection)
                        x1,x2,x3,x4=st.columns(4)
                        with x1: st.metric('Economia estimada / carteira',f"R$ {picked['savings']:,.2f}")
                        with x2: st.metric('Investimento',f"R$ {picked['investment']:,.2f}")
                        with x3: st.metric('SLA',f"{picked['sla_pct']:.0f}%")
                        with x4: st.metric('Não dominada (Pareto)','Sim' if picked['pareto'] else 'Não')
                        st.markdown(f"**Hipótese operacional:** {picked['rationale']}")
                        st.markdown(f"**Veredito Anti-Murphy:** {picked.get('verdict','-')} — {picked.get('verdict_reason','-')}")
                        st.caption('Melhor alternativa listada = menor custo entre as alternativas testadas que atendem às restrições; não é garantia de ótimo global.')
                        b1,b2=st.columns(2)
                        with b1:
                            st.download_button("↓ Decision Memo auditável (.json)",decision_report(data,picked),
                                file_name='anti_murphy_v28_decision_memo.json',mime='application/json',key='v27_memo',use_container_width=True)
                        with b2:
                            st.download_button("↓ Matriz de decisões (.csv)",pd.DataFrame(view).to_csv(index=False).encode('utf-8-sig'),
                                file_name='anti_murphy_v28_decisoes.csv',mime='text/csv',key='v27_csv',use_container_width=True)
                        with st.expander('◷ Gantt verificado · primeira unidade de cada ordem', expanded=False):
                            operation_rows=[op for op in picked['result'].get('operations',[]) if op.get('Unidade')==1]
                            if operation_rows:
                                gantt=go.Figure()
                                station_palette=['#FF681B','#288C98','#8A65D5','#1F9F69','#D6A64D','#DE5D7B']
                                stations_g=list(dict.fromkeys(op['Posto'] for op in operation_rows))
                                for j,sid in enumerate(stations_g):
                                    ops=[op for op in operation_rows if op['Posto']==sid]
                                    gantt.add_trace(go.Bar(name=sid,orientation='h',
                                        y=[f"{op['OP']} · etapa {op['Etapa']}" for op in ops],
                                        base=[op['Início (h)'] for op in ops],
                                        x=[op['Fim (h)']-op['Início (h)'] for op in ops],
                                        marker_color=station_palette[j%len(station_palette)],
                                        customdata=[[op['Processando (h)'],op['Parada (h)'],op['Espera (h)']] for op in ops],
                                        hovertemplate='Posto: '+sid+'<br>Intervalo: %{base:.2f}h + %{x:.2f}h<br>Processamento: %{customdata[0]:.2f}h<br>Parada: %{customdata[1]:.2f}h<br>Espera: %{customdata[2]:.2f}h<extra></extra>'))
                                gantt.update_layout(title='Linha do tempo real gerada pelo motor V28',barmode='overlay',
                                    xaxis_title='Horas simuladas',yaxis_title='OP / etapa',height=500,margin=dict(l=15,r=15,t=55,b=15))
                                st.plotly_chart(gantt,use_container_width=True)
                                st.dataframe(pd.DataFrame(operation_rows),use_container_width=True,hide_index=True)
                                st.caption('Amostra visual: primeira unidade de cada OP; o motor registra todas as operações. Paradas não são tratadas como tempo produtivo.')
                        st.markdown('### 4 · Sensibilidade da decisão (mesmas sementes)')
                        run_n=st.slider('Replicações de tempos operacionais sintéticos',3,16,6,1,key='v27_runs')
                        if st.button('⌁ Testar estabilidade da escolha',key='v27_robust_run',use_container_width=True):
                            with st.spinner('Rodando experimentos pareados...'):
                                st.session_state.v27_robustness=(selection,run_n,paired_stress_test(st.session_state.v27_incident,picked['config'],runs=run_n))
                        if 'v27_robustness' in st.session_state:
                            sel,n,rob=st.session_state.v27_robustness
                            if sel==selection and n==run_n and rob['feasible']:
                                st.metric('Economia operacional média ANTES do investimento',f"R$ {rob['mean_cost_saving_before_investment']:,.2f}")
                                st.dataframe(pd.DataFrame(rob['pairs']),use_container_width=True,hide_index=True)
                                st.caption(rob['interpretation']+' O investimento da ação deve ser subtraído da economia operacional para avaliar cada resultado.')
                            elif sel!=selection or n!=run_n:
                                st.info('Seleção ou número de replicações alterado. Execute o teste novamente.')
                    st.caption('Arquivo-modelo: '+data['model_signature']+' · SHA-256 curto de entrada, NÃO é o hash SHA-512 para registro no INPI.')
    elif page == "Murphy Lab":
        base = ensure_base()
        v16_page_head("02 / EXPERIMENT", "Scenario Studio", "Um ambiente de composição de mundos alternativos: configure a intervenção à esquerda e leia o cenário antes de executá-lo.", "compose → simulate → explain")
        station_ids = list(st.session_state.stations.keys())
        # Murphy AI can prepare a scenario, but the user still sees and executes it manually.
        if st.session_state.get("ai_prefill_pending"):
            pf = st.session_state.get("ai_scenario_prefill", {})
            if pf.get("target") in station_ids: st.session_state.studio_target = pf.get("target")
            st.session_state.studio_delta_workers = int(pf.get("delta_workers", 0))
            st.session_state.studio_delta_machines = int(pf.get("delta_machines", 0))
            st.session_state.studio_demand = float(pf.get("demand", 1.0))
            st.session_state.studio_rule = str(pf.get("rule", DEFAULT_RULE))
            st.session_state.studio_event = str(pf.get("event", list(EVENT_PRESETS.keys())[0]))
            st.session_state.studio_absent = int(pf.get("absent", 0))
            st.session_state.studio_name = str(pf.get("name", "AI Experiment"))
            st.session_state.ai_prefill_pending = False
        st.session_state.setdefault("studio_target", station_ids[0])
        st.session_state.setdefault("studio_delta_workers", 0)
        st.session_state.setdefault("studio_delta_machines", 0)
        st.session_state.setdefault("studio_absent", 0)
        st.session_state.setdefault("studio_demand", 1.0)
        st.session_state.setdefault("studio_rule", DEFAULT_RULE if DEFAULT_RULE in ["EDD","SPT","FIFO"] else "EDD")
        st.session_state.setdefault("studio_event", list(EVENT_PRESETS.keys())[0])
        st.session_state.setdefault("studio_chaos_start", 6.0)
        st.session_state.setdefault("studio_name", "Experimento A")

        controls, preview = st.columns([1.22, .78], gap="large")
        with controls:
            st.markdown("### Scenario setup")
            ca, cb = st.columns(2)
            with ca:
                target = st.selectbox("Posto-alvo", station_ids, format_func=lambda x: f"{x} · {st.session_state.stations[x]['nome']}", key="studio_target")
                delta_workers = st.number_input("Δ operadores", min_value=-3, max_value=6, step=1, key="studio_delta_workers")
                delta_machines = st.number_input("Δ máquinas / postos", min_value=-2, max_value=4, step=1, key="studio_delta_machines")
                absent = st.number_input("Ausências", min_value=0, max_value=5, step=1, key="studio_absent")
            with cb:
                demand = st.slider("Demanda", 0.5, 2.0, step=0.1, key="studio_demand")
                rule = st.selectbox("Regra de despacho", ["EDD","SPT","FIFO"], key="studio_rule")
                event_name = st.selectbox("Murphy Event", list(EVENT_PRESETS.keys()), key="studio_event")
                chaos_start = st.slider("Início do evento (h)", 0.0, 20.0, step=0.5, key="studio_chaos_start")
            scenario_name = st.text_input("Nome do cenário", placeholder="Ex.: Corte +1 máquina · pico 20%", key="studio_name")
            chaos_station = target
            current_sig = scenario_input_signature(target, delta_workers, delta_machines, demand, rule, event_name, chaos_start, absent, scenario_name)
            previous_sig = st.session_state.get("scenario_input_signature")
            scenario_dirty = bool(st.session_state.scenario_result is not None and previous_sig != current_sig)
            no_change = (int(delta_workers)==0 and int(delta_machines)==0 and abs(float(demand)-1.0)<1e-9 and rule==DEFAULT_RULE and EVENT_PRESETS[event_name]["duration_h"]<=0 and int(absent)==0)
            if scenario_dirty:
                stale_scenario_notice()
            if st.button("▶ Executar mundo alternativo", type="primary", use_container_width=True, disabled=no_change):
                cfg = current_base_config().clone(name=scenario_name or "Experimento")
                cfg.dispatch_rule = rule
                cfg.demand_multiplier = demand
                cfg.stations[target]["operadores"] = max(0, cfg.stations[target]["operadores"] + int(delta_workers))
                cfg.stations[target]["maquinas"] = max(1, cfg.stations[target]["maquinas"] + int(delta_machines))
                cfg.chaos_station = chaos_station if EVENT_PRESETS[event_name]["duration_h"] > 0 else None
                cfg.chaos_start_h = chaos_start
                cfg.chaos_duration_h = EVENT_PRESETS[event_name]["duration_h"]
                cfg.absent_workers = {target: int(absent)} if absent else {}
                with st.status("Construindo mundo alternativo…", expanded=True) as status:
                    st.write("01 / Clone · recursos, ordens e regras")
                    time.sleep(0.10)
                    st.write("02 / Simulate · filas, eventos e contenção")
                    result = run_simulation(cfg)
                    st.write("03 / Diagnose · gargalo, prazo, custo e resiliência")
                    time.sleep(0.10)
                    status.update(label="Mundo alternativo calculado", state="complete", expanded=False)
                st.session_state.scenario_config = cfg
                st.session_state.scenario_result = result
                st.session_state.scenario_input_signature = current_sig
                register_decision(cfg.name, "Scenario Studio", result)
                st.rerun()
        with preview:
            scenario_canvas(target, st.session_state.stations[target]["nome"], int(delta_workers), int(delta_machines), float(demand), rule, event_name, int(absent))
            scenario_intervention_map(target, st.session_state.stations[target]["nome"], st.session_state.stations[target], int(delta_workers), int(delta_machines), float(demand), rule, event_name, int(absent))

        if st.session_state.scenario_result and not scenario_dirty:
            alt = st.session_state.scenario_result
            d = compare_results(base, alt)
            explanation = explain_comparison(base, alt)
            st.markdown("### Decision readout")
            decision_scorecard_ui(decision_scorecard(base, alt))
            review_cards(base, alt, d)
            causal_chain(base, alt, explanation)
            ri_alt = resilience_index(alt)
            metric_rail(base, ri_alt, murphy_score(alt), alt=alt)
            cinfo = decision_confidence(base, alt, len(st.session_state.decision_history))
            q1,q2 = st.columns([.72,1.28], gap="medium")
            with q1:
                confidence_card(cinfo)
            with q2:
                st.markdown(f"**{explanation['headline']}**")
                for cause in explanation["causes"][:4]:
                    st.markdown(f"- {cause}")
            with st.expander("Ver o fluxo do cenário calculado", expanded=False):
                render_flow(alt)
        elif scenario_dirty:
            st.info("O Decision Readout foi ocultado porque os controles mudaram desde a última simulação. Execute o cenário para produzir resultados sincronizados.")

    elif page == "Comparar":
        st.caption("Comparação legada contra operação normal. Para isolar o efeito de uma resposta à mesma falha, use Decision Evidence Studio.")
        base = ensure_base()
        alt = st.session_state.scenario_result
        v16_page_head("03 / REVIEW", "Decision Review", "Compare o estado anterior e posterior da operação sem misturar escalas ou esconder trade-offs.", "antes → depois · causa → efeito")
        if not alt:
            st.warning("Crie um experimento no Murphy Lab primeiro.")
        else:
            d = compare_results(base, alt)
            expl = explain_comparison(base, alt)
            decision_scorecard_ui(decision_scorecard(base, alt))
            review_cards(base, alt, d)
            decision_verdict(base, alt, d)
            decision_lens(base, alt, d)
            decision_economics(base, alt)
            decision_narrative(base, alt, d)
            total_change = abs(float(d.get("throughput_pct",0))) + abs(float(d.get("sla_pp",0))) + abs(float(d.get("unit_cost_pct",0))) + abs(float(d.get("makespan_pct",0)))
            if total_change < 0.05:
                neutral_compare_state()
                st.info("O cenário reproduz o estado-base. Configure uma intervenção real no Scenario Studio para gerar contraste decisório.")
            else:
                l,r = st.columns([1.05,.95], gap="medium")
                with l:
                    st.markdown("### Decision impact vector")
                    st.plotly_chart(scenario_delta_chart(base, alt), use_container_width=True)
                with r:
                    st.markdown("### Causa → efeito")
                    causal_chain(base, alt, expl)
                cinfo = decision_confidence(base, alt, len(st.session_state.decision_history))
                confidence_card(cinfo)
            st.markdown("### Simulation Confidence")
            st.caption("Repita o mesmo cenário com sementes diferentes para medir a dispersão interna do modelo. Isso não é probabilidade do mundo real; é consistência da simulação sob a variabilidade já modelada.")
            mc1, mc2 = st.columns([.35,.65])
            with mc1:
                mc_runs = st.slider("Replicações", 6, 30, 12, 2, key="v21_mc_runs")
                if st.button("Rodar replicações", use_container_width=True, key="v21_mc_run"):
                    with st.spinner("Executando replicações do cenário..."):
                        cfg_mc = st.session_state.scenario_config or alt.get("config")
                        if cfg_mc is not None:
                            st.session_state.v21_mc = monte_carlo_analysis(cfg_mc, runs=int(mc_runs), seed_start=2400)
            with mc2:
                if "v21_mc" in st.session_state:
                    monte_carlo_panel(st.session_state.v21_mc, label=str(alt.get("name","Decision world")))
                else:
                    st.info("Rode replicações para ver intervalo de confiança, dispersão e estabilidade do gargalo.")

            st.markdown("### Comparação por posto")
            bdf = pd.DataFrame(base["stations"])[["Posto","Utilização máquina (%)","Espera média (min)","Fila máx."]].set_index("Posto")
            adf = pd.DataFrame(alt["stations"])[["Posto","Utilização máquina (%)","Espera média (min)","Fila máx."]].set_index("Posto")
            comp = bdf.join(adf, lsuffix=" · Base", rsuffix=" · Cenário")
            st.dataframe(comp, use_container_width=True)
            st.markdown("### Decision Workspace")
            st.caption("Seu histórico vira um portfólio comparável: veja migração do gargalo, fronteira custo × desempenho e recupere cenários já testados.")
            render_decision_timeline(st.session_state.decision_history)
            render_migration(base.get("bottleneck","-"), st.session_state.decision_history)
            if st.session_state.decision_history:
                render_portfolio(st.session_state.decision_history, portfolio_summary(st.session_state.decision_history))
                pick_names=[f"{i+1:02d} · {h['name']} · {h['source']}" for i,h in enumerate(st.session_state.decision_history)]
                sel=st.selectbox("Recuperar cenário do histórico", pick_names, key="history_pick")
                if st.button("Carregar cenário selecionado", use_container_width=True, key="history_load"):
                    idx=pick_names.index(sel); st.session_state.scenario_result=st.session_state.decision_history[idx].get("result")
                    st.success("Cenário recuperado do histórico."); st.rerun()
            r1, r2 = st.columns(2)
            with r1:
                st.download_button("↓ Relatório executivo do cenário (.html)", data=executive_report_html(base, alt), file_name="anti_murphy_relatorio_cenario.html", mime="text/html", use_container_width=True)
            with r2:
                comparison_csv = comp.reset_index().to_csv(index=False).encode("utf-8-sig")
                st.download_button("↓ Comparação por posto (.csv)", data=comparison_csv, file_name="anti_murphy_comparacao_postos.csv", mime="text/csv", use_container_width=True)

    elif page == "Opportunity Engine":
        base = ensure_base()
        v16_page_head("04 / INTELLIGENCE", "Opportunity Engine", "Varra microdecisões automaticamente e encontre intervenções que merecem teste humano.", "impacto · custo · saturação · migração")
        module_hero("COUNTERFACTUAL SCAN", "Transforme tentativa e erro em busca orientada.", "O motor cria alternativas, mede ganho operacional, observa custo e expõe quando capacidade adicional deixa de trazer retorno relevante.", ["Quick wins", "Realocação", "Capacidade", "Sensitivity Lab"])
        if "opportunities" not in st.session_state:
            st.markdown("""
            <div class="am-empty">
              <div class="am-empty-eyebrow">Exploração contrafactual</div>
              <div class="am-empty-title">Descubra onde uma pequena decisão muda o sistema inteiro.</div>
              <div class="am-empty-copy">O Opportunity Engine cria microcenários automaticamente e mede impacto em fluxo, SLA, custo e makespan antes de você alterar a operação real.</div>
              <div class="am-empty-grid">
                <div class="am-empty-item"><b>Capacidade</b>Testa +1 operador e +1 posto em cada etapa.</div>
                <div class="am-empty-item"><b>Realocação</b>Experimenta movimentos de mão de obra sem contratar.</div>
                <div class="am-empty-item"><b>Impacto sistêmico</b>Mostra ganhos, perdas e migração do gargalo.</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")
        if st.button("Explorar microdecisões →", type="primary"):
            with st.spinner("Rodando cenários contrafactuais..."):
                st.session_state.opportunities = generate_opportunities(current_base_config(), base)
        if "opportunities" in st.session_state:
            opps = st.session_state.opportunities
            opportunity_leaderboard(opps)
            opportunity_quadrants()
            if opps:
                opp_labels=[f"{i+1:02d} · {o.get('Ação','Oportunidade')}" for i,o in enumerate(opps[:12])]
                opp_sel=st.selectbox("Inspecionar oportunidade", opp_labels, key="v20_opp_pick")
                opp_idx=opp_labels.index(opp_sel); selected_opp=opps[opp_idx]
                opportunity_detail(selected_opp)
                oa,ob=st.columns(2)
                with oa:
                    if st.button("Abrir oportunidade no Decision Review", use_container_width=True, key="v20_opp_review"):
                        st.session_state.scenario_result=selected_opp["result"]
                        st.session_state.scenario_config=selected_opp["config"]
                        st.session_state.pop("scenario_input_signature", None)
                        register_decision(selected_opp.get("Ação","Oportunidade"), "Opportunity Engine", selected_opp["result"])
                        st.session_state.active_page="Comparar"; st.rerun()
                with ob:
                    if st.button("Usar como referência no Scenario Studio", use_container_width=True, key="v20_opp_studio"):
                        st.session_state.scenario_result=selected_opp["result"]
                        st.session_state.scenario_config=selected_opp["config"]
                        st.session_state.pop("scenario_input_signature", None)
                        st.session_state.active_page="Murphy Lab"; st.rerun()
            st.markdown("### Opportunity map · impacto × custo")
            om = opportunity_matrix(opps)
            if om is not None:
                st.plotly_chart(om, use_container_width=True)
            render_opportunity_radar(opps)
            view = pd.DataFrame([{k:v for k,v in x.items() if k not in ["result","config"]} for x in opps])
            st.dataframe(view, use_container_width=True, hide_index=True)
            if opps:
                top = opps[0]
                st.markdown(f"""
                <div class="insight"><b>Cenário de maior oportunidade no conjunto testado:</b> {top['Ação']}. No modelo, ele altera o throughput em <b>{top['Throughput Δ (%)']:+.1f}%</b>, o SLA em <b>{top['SLA Δ (p.p.)']:+.1f} p.p.</b> e o custo por unidade em <b>{top['Custo/un Δ (%)']:+.1f}%</b>.</div>
                """, unsafe_allow_html=True)
                if st.button("Abrir melhor cenário na comparação"):
                    st.session_state.scenario_result = top["result"]
                    st.session_state.scenario_config = top["config"]
                    register_decision(top.get("Ação", "Oportunidade"), "Opportunity Engine", top["result"])
                    st.success("Cenário carregado. Abra a aba Comparar.")

            st.markdown("### Sensitivity Lab · quanto vale mais um recurso?")
            st.caption("Teste ganho marginal em sequência para evitar contratar ou comprar capacidade que já entrou em saturação.")
            sn1,sn2,sn3 = st.columns([1.2,1,1])
            with sn1:
                sens_station = st.selectbox("Posto da sensibilidade", list(st.session_state.stations.keys()), index=list(st.session_state.stations.keys()).index(base.get("bottleneck")) if base.get("bottleneck") in st.session_state.stations else 0, key="sens_station")
            with sn2:
                sens_res = st.selectbox("Recurso", ["Operadores","Máquinas"], key="sens_res")
            with sn3:
                sens_n = st.slider("Até +", 1, 5, 3, key="sens_n")
            if st.button("Calcular curva de sensibilidade", use_container_width=True, key="sens_run"):
                st.session_state.sensitivity_rows = sensitivity_analysis(current_base_config(), base, sens_station, "maquinas" if sens_res=="Máquinas" else "operadores", sens_n)
                st.session_state.sensitivity_label = sens_res
            if "sensitivity_rows" in st.session_state:
                srows=st.session_state.sensitivity_rows
                st.plotly_chart(sensitivity_chart(srows, st.session_state.get("sensitivity_label","Recursos")), use_container_width=True)
                if len(srows)>1:
                    gains=[float(x.get("Ganho marginal TP",0)) for x in srows[1:]]
                    peak=max(gains) if gains else 0
                    saturation=next((x for x in srows[1:] if peak>0 and float(x.get("Ganho marginal TP",0)) <= peak*0.10), None)
                    if saturation:
                        st.markdown(f"<div class='insight'><b>Sinal de saturação:</b> a partir de +{saturation['Adição']} recurso(s), o ganho marginal de throughput cai para {saturation['Ganho marginal TP']:.3f} un/h. Vale confrontar esse ponto com o custo incremental.</div>", unsafe_allow_html=True)



    elif page == "Optimization Hub":
        base=ensure_base()
        v16_page_head("05 / OPTIMIZATION", "Optimization Hub", "Compare políticas, fronteiras de decisão e risco de ativos sem esconder os trade-offs.", "scheduling · pareto · reliability · workforce")
        module_hero("DECISION OPTIMIZATION", "Não procure uma resposta única. Procure a fronteira certa.", "O hub combina regras de despacho, cenários já testados e análises de confiabilidade para revelar alternativas não dominadas e políticas operacionais melhores.", ["Scheduling Lab","Pareto Explorer","Asset Reliability","Skills Coverage"])

        st.markdown("### Scheduling Lab · política antes de capacidade")
        st.caption("EDD, SPT e FIFO são executados sobre exatamente o mesmo modelo e seed. Isso compara política de despacho; não garante ótimo global.")
        if st.button("Comparar regras de despacho",use_container_width=True,key="v24_schedule_run"):
            with st.spinner("Executando benchmark de regras..."):
                st.session_state.v24_schedule=scheduling_benchmark(current_base_config())
        sched=st.session_state.get("v24_schedule",[])
        if sched:
            objective=st.selectbox("Critério para destacar",["SLA","Menor makespan","Menor custo/un","Throughput"],key="v24_sched_obj")
            if objective=="SLA": best=max(sched,key=lambda x:(x['sla'],x['throughput'],-x['unit_cost']))
            elif objective=="Menor makespan": best=min(sched,key=lambda x:x['makespan'])
            elif objective=="Menor custo/un": best=min(sched,key=lambda x:x['unit_cost'])
            else: best=max(sched,key=lambda x:x['throughput'])
            for row in sched: scheduling_row(row,row is best)
            a,b=st.columns(2)
            with a:
                if st.button("Enviar política destacada para Decision Review",use_container_width=True,key="v24_sched_compare"):
                    st.session_state.scenario_result=best['result'];st.session_state.scenario_config=best['config'];register_decision(f"Scheduling · {best['rule']}","Optimization Hub",best['result']);st.session_state.active_page="Comparar";st.rerun()
            with b:
                if st.button("Usar política no Scenario Studio",use_container_width=True,key="v24_sched_studio"):
                    st.session_state.ai_scenario_prefill={"rule":best['rule'],"name":f"Scheduling · {best['rule']}"};st.session_state.ai_prefill_pending=True;st.session_state.active_page="Murphy Lab";st.rerun()

        st.markdown("### Pareto Explorer · melhores compromissos")
        pool=[]
        for h in st.session_state.decision_history:
            pool.append({"name":h.get("name","Scenario"),"throughput":float(h.get("throughput",0)),"sla":float(h.get("sla",0)),"unit_cost":float(h.get("unit_cost",0)),"makespan":float(h.get("makespan",0)),"source":h.get("source","history"),"result":h.get("result")})
        for r in sched:
            pool.append({"name":f"Rule {r['rule']}","throughput":r['throughput'],"sla":r['sla'],"unit_cost":r['unit_cost'],"makespan":r['makespan'],"source":"Scheduling","result":r['result']})
        for o in st.session_state.get("opportunities",[]) or []:
            rr=o.get("result")
            if rr: pool.append({"name":o.get("Ação","Opportunity"),"throughput":float(rr.get("throughput_h",0)),"sla":float(rr.get("sla_pct",0)),"unit_cost":float(rr.get("unit_cost",0)),"makespan":float(rr.get("makespan_h",0)),"source":"Opportunity","result":rr})
        frontier=pareto_frontier(pool) if pool else []
        if pool:
            st.plotly_chart(pareto_chart(pool,frontier),use_container_width=True)
            st.caption(f"{len(frontier)} de {len(pool)} alternativas permanecem não dominadas em throughput↑, SLA↑, custo↓ e makespan↓.")
        else:
            st.info("Rode Scheduling Lab, Opportunity Engine ou outros experimentos para construir uma fronteira comparável.")

        st.markdown("### Asset Reliability · manutenção baseada em hipótese explícita")
        st.caption("Informe MTBF/MTTR estimados. O cálculo usa distribuição exponencial simples e não transforma disponibilidade histórica em taxa de falha sem sua autorização.")
        if "v24_reliability_table" not in st.session_state:
            st.session_state.v24_reliability_table=pd.DataFrame([{"Posto":sid,"MTBF (h)":120.0,"MTTR (h)":3.0} for sid in st.session_state.stations])
        rel_table=st.data_editor(st.session_state.v24_reliability_table,use_container_width=True,hide_index=True,key="v24_rel_editor")
        st.session_state.v24_reliability_table=rel_table
        r1,r2=st.columns(2)
        with r1: rel_h=st.number_input("Horizonte de risco (h)",min_value=1.0,value=168.0,step=24.0,key="v24_rel_h")
        with r2: down_cost=st.number_input("Custo de parada (R$/h)",min_value=0.0,value=1500.0,step=100.0,key="v24_down_cost")
        rel_inputs={}
        for _,row in rel_table.iterrows():
            sid=str(row.get("Posto",""));rel_inputs[sid]={"mtbf_h":float(row.get("MTBF (h)",120) or 120),"mttr_h":float(row.get("MTTR (h)",3) or 3)}
        rel_rows=reliability_analysis(st.session_state.stations,rel_inputs,rel_h,down_cost)
        if rel_rows:
            reliability_strip(rel_rows[0])
            st.dataframe(pd.DataFrame(rel_rows),use_container_width=True,hide_index=True)

        st.markdown("### Skills Coverage · risco de pessoa única")
        st.caption("Cadastre uma matriz simples de qualificação. O objetivo é enxergar postos sem cobertura e pontos únicos de conhecimento.")
        if "v24_skills_table" not in st.session_state:
            st.session_state.v24_skills_table=pd.DataFrame([{"Operador":"Operador 1","Postos qualificados":",".join(list(st.session_state.stations)[:2])},{"Operador":"Operador 2","Postos qualificados":",".join(list(st.session_state.stations)[2:])}])
        skills_df=st.data_editor(st.session_state.v24_skills_table,num_rows="dynamic",use_container_width=True,hide_index=True,key="v24_skills_editor")
        st.session_state.v24_skills_table=skills_df
        skills={}
        for _,row in skills_df.iterrows():
            name=str(row.get("Operador","")).strip()
            if name:
                skills[name]=[x.strip().upper() for x in str(row.get("Postos qualificados","")).split(",") if x.strip()]
        cov=skill_coverage(st.session_state.stations,skills)
        sc1,sc2,sc3=st.columns(3)
        with sc1: st.metric("Coverage score",f"{cov.get('score',0):.0f}/100")
        with sc2: st.metric("Postos sem cobertura",len(cov.get('gaps',[])))
        with sc3: st.metric("Pontos únicos",len(cov.get('single_points',[])))
        if cov.get('gaps'): st.error("Sem cobertura: "+", ".join(cov['gaps']))
        elif cov.get('single_points'): st.warning("Cobertura por uma única pessoa: "+", ".join(cov['single_points']))
        else: st.success("Todos os postos possuem pelo menos duas qualificações cadastradas.")

    elif page == "Stress Lab":
        base = ensure_base()
        v16_page_head("05 / RESILIENCE", "Resilience Lab", "Submeta a operação a futuros adversos e descubra fragilidade, tolerância e ponto de ruptura.", "stress · ruptura · robustez")
        module_hero("RESILIENCE ENGINE", "Não pergunte apenas se funciona. Descubra até onde aguenta.", "Combine ausências, picos de demanda e indisponibilidade para revelar a fronteira entre operação controlada e falha sistêmica.", ["Stress Scan", "Fragilidade", "Rupture Lab", "Worst case"])
        a,b,c,d = st.columns(4)
        with a: runs = st.slider("Cenários de estresse", 8, 60, 24, 4)
        with b: max_abs = st.slider("Ausências máximas", 0, 3, 1)
        with c: dem_hi = st.slider("Pico de demanda", 1.0, 1.8, 1.3, 0.1)
        with d: stress_seed = st.number_input("Seed da bateria", 1, 99999, 2026, 1)
        if st.button("⚡ Iniciar bateria de estresse", type="primary", use_container_width=True):
            with st.spinner("Provocando a operação em múltiplos futuros..."):
                st.session_state.stress_results = stress_test(current_base_config(), runs=runs, max_absent=max_abs, demand_high=dem_hi, seed=int(stress_seed))
        if "stress_results" in st.session_state:
            sr = st.session_state.stress_results
            sm = sr["summary"]
            stress_summary_panel(sm)
            st.markdown("### Resilience Scan")
            r1,r2,r3,r4,r5 = st.columns(5)
            with r1: metric_card("Resiliência", f"{sm['resilience_rate']:.0f}%", "cenários com SLA ≥ 80%", "#2B7A5A")
            with r2: metric_card("SLA médio", f"{sm['sla_avg']:.0f}%", f"pior caso {sm['sla_worst']:.0f}%", "#1D292D")
            with r3: metric_card("P90 makespan", f"{sm['makespan_p90']:.1f} h", "90% dos cenários abaixo disso", "#1D292D")
            with r4: metric_card("P10 throughput", f"{sm['throughput_p10']:.2f}", "cauda inferior da capacidade", "#1D292D")
            with r5: metric_card("Posto frágil", sm['most_fragile'], "maior impacto quando perturbado", "#FF681B", emphasis=True)
            st.markdown("#### Mapa de fragilidade")
            render_fragility_map(sr["fragility"])
            dfstress = pd.DataFrame([{k:v for k,v in x.items() if k not in ['result','config']} for x in sr['runs']])
            cl,cr=st.columns([1.1,1])
            with cl:
                st.markdown("#### Paisagem de resiliência")
                sl = stress_landscape(sr)
                if sl is not None:
                    st.plotly_chart(sl, use_container_width=True)
            with cr:
                st.markdown("#### Cenários mais severos")
                severe=dfstress.sort_values(["SLA","Makespan"],ascending=[True,False]).head(8)
                st.dataframe(severe, use_container_width=True, hide_index=True, height=330)
            worst = sr["runs"][dfstress.sort_values(["SLA","Makespan"],ascending=[True,False]).index[0]] if sr["runs"] else None
            if worst:
                st.markdown(f"<div class='insight'><b>What broke the system?</b> O caso mais severo atingiu <b>{worst['Posto afetado']}</b>, com demanda <b>{worst['Demanda x']:.2f}×</b>, parada de <b>{worst['Parada (h)']:.1f} h</b> e {worst['Ausências']} ausência(s). O SLA caiu para <b>{worst['SLA']:.0f}%</b> e o gargalo terminou em <b>{worst['Gargalo']}</b>.</div>", unsafe_allow_html=True)
                st.markdown("### Recovery Planner")
                st.caption("Mantém o mesmo pior cenário e testa respostas simples para recuperar serviço, fluxo e tempo. É uma exploração contrafactual, não uma ordem de implementação.")
                if st.button("Construir plano de recuperação do pior caso", use_container_width=True, key="recovery_run"):
                    with st.spinner("Testando respostas sobre o mesmo cenário de crise..."):
                        st.session_state.recovery_rows = recovery_plan(worst["config"], worst["result"], max_results=5)
                if "recovery_rows" in st.session_state:
                    recovery_cards(st.session_state.recovery_rows)
                    rdf=pd.DataFrame([{k:v for k,v in x.items() if k not in ["result","config"]} for x in st.session_state.recovery_rows])
                    st.dataframe(rdf, use_container_width=True, hide_index=True)
                    if st.session_state.recovery_rows:
                        best_rec=st.session_state.recovery_rows[0]
                        if st.button("Levar melhor recuperação ao Decision Review", use_container_width=True, key="recovery_compare"):
                            st.session_state.scenario_result=best_rec["result"]
                            st.session_state.scenario_config=best_rec["config"]
                            register_decision(best_rec["Ação"], "Recovery Planner", best_rec["result"])
                            st.session_state.active_page="Comparar"
                            st.rerun()

        st.markdown("### Survival Map · demanda × ausência")
        st.caption("Mapeie uma fronteira operacional 2D. Cada célula é uma simulação que cruza pressão de demanda com ausência no posto escolhido.")
        sf1,sf2,sf3 = st.columns(3)
        with sf1:
            surface_station = st.selectbox("Posto da fronteira", list(st.session_state.stations.keys()), index=list(st.session_state.stations.keys()).index(base.get("bottleneck")) if base.get("bottleneck") in st.session_state.stations else 0, key="v21_surface_station")
        with sf2:
            surface_floor = st.slider("Piso SLA da fronteira", 0, 100, max(20, min(100, int(base.get("sla_pct",20)))), 5, key="v21_surface_floor")
        with sf3:
            surface_abs = st.slider("Ausências máximas no mapa", 0, 3, 2, 1, key="v21_surface_abs")
        if st.button("Mapear fronteira operacional", use_container_width=True, key="v21_surface_run"):
            with st.spinner("Construindo superfície de sobrevivência operacional..."):
                demand_levels=[1.0,1.1,1.2,1.3,1.4,1.5,1.6]
                absent_levels=list(range(0,int(surface_abs)+1))
                st.session_state.v21_surface = resilience_surface(current_base_config(), surface_station, demand_levels, absent_levels, float(surface_floor))
        if "v21_surface" in st.session_state:
            frontier_summary(st.session_state.v21_surface)
            st.plotly_chart(resilience_surface_chart(st.session_state.v21_surface), use_container_width=True)

        st.markdown("### Rupture Lab · descubra o limite da operação")
        st.caption("Em vez de testar um único pico, aumente a pressão gradualmente até encontrar o primeiro nível em que o SLA deixa de atender o piso definido.")
        rb1,rb2,rb3 = st.columns(3)
        with rb1:
            rupture_default = max(20, min(100, int(round(float(base.get("sla_pct",20))/5.0)*5)))
            rupture_floor = st.slider("Piso de SLA", 20, 100, rupture_default, 5, key="rupt_floor")
        with rb2:
            rupture_max = st.slider("Demanda máxima", 1.10, 2.50, 1.80, 0.10, key="rupt_max")
        with rb3:
            rupture_station = st.selectbox("Posto para teste de ausência", list(st.session_state.stations.keys()), index=list(st.session_state.stations.keys()).index(base.get("bottleneck")) if base.get("bottleneck") in st.session_state.stations else 0, key="rupt_station")
        if float(base.get("sla_pct",0)) < float(rupture_floor):
            baseline_target_warning(float(base.get("sla_pct",0)), float(rupture_floor))
        rr1,rr2=st.columns(2)
        with rr1:
            if st.button("Encontrar limite de demanda", use_container_width=True, key="rupt_demand"):
                with st.spinner("Aumentando demanda até o ponto de ruptura..."):
                    st.session_state.demand_rupture = demand_breakpoint(current_base_config(), rupture_floor, 1.0, rupture_max, 0.05)
        with rr2:
            if st.button("Encontrar limite de ausências", use_container_width=True, key="rupt_abs"):
                with st.spinner("Testando tolerância a ausências..."):
                    st.session_state.abs_rupture = absentee_breakpoint(current_base_config(), rupture_station, rupture_floor, 5)
        if "demand_rupture" in st.session_state:
            scan=st.session_state.demand_rupture
            st.plotly_chart(rupture_chart(scan), use_container_width=True)
            fb=scan.get("first_break"); safe=scan.get("last_safe")
            if fb:
                safe_txt=f"{safe['Demanda x']:.2f}×" if safe else "abaixo do cenário-base"
                st.markdown(f"<div class='insight'><b>Limite detectado:</b> o último nível testado ainda compatível com SLA ≥ {rupture_floor}% foi <b>{safe_txt}</b>. A primeira ruptura ocorreu em <b>{fb['Demanda x']:.2f}×</b> de demanda, com SLA de <b>{fb['SLA']:.0f}%</b> e gargalo em <b>{fb['Gargalo']}</b>.</div>", unsafe_allow_html=True)
        if "abs_rupture" in st.session_state:
            ar=st.session_state.abs_rupture; afb=ar.get("first_break")
            adf=pd.DataFrame([{k:v for k,v in x.items() if k!='result'} for x in ar.get('points',[])])
            st.dataframe(adf, use_container_width=True, hide_index=True)
            if afb:
                st.warning(f"Ruptura por mão de obra: {afb['Ausências']} ausência(s) em {ar['station']} derrubam o SLA para {afb['SLA']:.0f}% no modelo.")

    elif page == "Scenario Portfolio":
        base=ensure_base()
        pf=scenario_portfolio(st.session_state.decision_history,base)
        v16_page_head("DECIDE / PORTFOLIO", "Scenario Portfolio", "Transforme experimentos soltos em memória decisória: compare, documente, recupere e exporte os cenários que realmente importam.", "rank · compare · annotate · audit")
        module_hero("DECISION MEMORY", "Seu histórico de testes vira ativo do projeto.", "O portfólio preserva alternativas, trade-offs, gargalos e evidências. Assim a equipe não precisa repetir experimentos nem depender da memória de quem operou o software.", ["Leaders","Pareto","Notes","Audit trail"])
        portfolio_leaders(pf.get('leaders',{}))
        items=pf.get('items',[])
        portfolio_cards_v26(items,st.session_state.scenario_notes,limit=6)
        if len(items)<=1:
            st.info("O cenário-base já está no portfólio. Rode experimentos no Scenario Studio, Opportunity Engine ou Decision Autopilot para construir memória decisória.")
        labels=[f"{i:02d} · {x.get('name')} · {x.get('source')}" for i,x in enumerate(items)]
        selected=st.multiselect("Comparar até 3 cenários",labels,default=labels[:min(3,len(labels))],max_selections=3,key="v25_portfolio_multi") if labels else []
        chosen=[items[labels.index(x)] for x in selected] if selected else []
        if chosen:
            comp=pd.DataFrame([{"Cenário":x['name'],"Origem":x['source'],"Throughput":x['throughput'],"SLA (%)":x['sla'],"Custo/un (R$)":x['unit_cost'],"Makespan (h)":x['makespan'],"Gargalo":x['bottleneck']} for x in chosen])
            st.dataframe(comp,use_container_width=True,hide_index=True)
            if len(chosen)>=2:
                change_digest_ui(change_digest(chosen[0]['result'],chosen[-1]['result']))
        st.markdown("### Pareto portfolio")
        pareto_rows=[{"name":x['name'],"throughput":x['throughput'],"sla":x['sla'],"unit_cost":x['unit_cost'],"makespan":x['makespan']} for x in items]
        frontier=pareto_frontier(pareto_rows)
        st.plotly_chart(pareto_chart(pareto_rows,frontier),use_container_width=True)
        st.caption("Laranja = cenários não dominados simultaneamente em throughput↑, SLA↑, custo↓ e makespan↓.")

        st.markdown("### Scenario notebook")
        if len(items)>1:
            note_labels=[f"{i:02d} · {x['name']}" for i,x in enumerate(items[1:],start=1)]
            note_pick=st.selectbox("Cenário",note_labels,key="v25_note_pick")
            idx=int(note_pick.split(' · ')[0]); item=items[idx]; note_key=f"{item['name']}::{item['source']}"
            prior=st.session_state.scenario_notes.get(note_key,{"note":"","tags":"","favorite":False})
            n1,n2=st.columns([1.3,.7])
            with n1:
                note=st.text_area("Nota de decisão",value=prior.get('note',''),placeholder="Por que este cenário foi testado? O que aprendemos?",key="v25_note_text")
                tags=st.text_input("Tags",value=prior.get('tags',''),placeholder="capacity, urgent, customer-A",key="v25_note_tags")
            with n2:
                fav=st.checkbox("Fixar como favorito",value=bool(prior.get('favorite',False)),key="v25_note_fav")
                if st.button("Salvar nota",use_container_width=True,key="v25_note_save"):
                    st.session_state.scenario_notes[note_key]={"note":note,"tags":tags,"favorite":fav}; st.session_state.audit_log.append(audit_entry("portfolio",item['name'],"nota/tags atualizadas")); st.success("Anotação salva.")
                if st.button("Abrir no Decision Review",use_container_width=True,key="v25_portfolio_open"):
                    st.session_state.scenario_result=item['result']; st.session_state.active_page="Comparar"; st.rerun()

        st.markdown("### Decision audit trail")
        audit=st.session_state.audit_log[-30:]
        if audit:
            st.dataframe(pd.DataFrame(audit[::-1]),use_container_width=True,hide_index=True)
        else:
            st.caption("O audit trail será preenchido conforme modelos, agentes e cenários forem alterados nesta sessão.")
        export_df=pd.DataFrame([{k:v for k,v in x.items() if k!='result'} for x in items])
        st.download_button("↓ Exportar Scenario Portfolio (.csv)",data=export_df.to_csv(index=False).encode('utf-8-sig'),file_name="anti_murphy_scenario_portfolio_v26.csv",mime="text/csv",use_container_width=True)

    elif page == "Mission Control":
        base = ensure_base()
        v16_page_head("06 / PLANNING", "Mission Control", "Comece pela meta e deixe o Anti-Murphy explorar rotas operacionais compatíveis com suas restrições.", "meta · orçamento · recursos · payback")
        module_hero("GOAL SEEK", "Diga onde quer chegar; o sistema procura caminhos plausíveis.", "Combine metas de throughput e SLA com limites de contratação, máquinas e orçamento para comparar rotas de implantação antes de decidir.", ["Target", "Budget", "Routes", "Finance Lens"])
        m1,m2,m3,m4 = st.columns(4)
        with m1: target_tp = st.number_input("Meta de throughput (un/h)", min_value=0.1, value=float(round(base['throughput_h']*1.20,2)), step=0.1)
        with m2: target_sla = st.slider("Meta de SLA (%)", 0, 100, min(100, int(max(80, base['sla_pct']))), 5)
        with m3: max_w = st.slider("Máx. operadores extras", 0, 4, 2)
        with m4: max_m = st.slider("Máx. máquinas extras", 0, 3, 1)
        mc1,mc2,mc3 = st.columns(3)
        with mc1: budget_cap = st.number_input("Orçamento máximo de implantação (R$) · 0 = sem limite", min_value=0.0, value=0.0, step=5000.0)
        with mc2: worker_impl_cost = st.number_input("Custo de implantação por operador (R$)", min_value=0.0, value=3000.0, step=500.0)
        with mc3: machine_impl_cost = st.number_input("Investimento por máquina/posto (R$)", min_value=0.0, value=25000.0, step=2500.0)
        if st.button("◎ Buscar rotas para a meta", type="primary", use_container_width=True):
            with st.spinner("Explorando combinações de capacidade e restrições..."):
                raw_rows = goal_seek(current_base_config(), base, target_tp, target_sla, max_w, max_m, max_results=40)
                for row in raw_rows:
                    row["Investimento estimado"] = float(row.get("Operadores +",0))*worker_impl_cost + float(row.get("Máquinas +",0))*machine_impl_cost
                filtered=[x for x in raw_rows if budget_cap<=0 or x["Investimento estimado"]<=budget_cap]
                st.session_state.goal_results = filtered[:12]
                st.session_state.goal_target = (target_tp,target_sla)
                st.session_state.goal_budget = budget_cap
        if "goal_results" in st.session_state:
            rows=st.session_state.goal_results
            gtp,gsla=st.session_state.get("goal_target",(target_tp,target_sla))
            if rows:
                route_cards(rows, limit=3)
                goal_route_strip(rows, gtp, gsla)
            if not rows:
                st.warning("Nenhuma rota ficou dentro das restrições escolhidas. Aumente orçamento/recursos ou revise a meta.")
            else:
                render_goal_path(rows, gtp, gsla)
            feasible=[x for x in rows if x['Atinge meta']=='Sim']
            best=(feasible or rows)[0] if rows else None
            if best:
                mission_target_hero(best,gtp,gsla)
                ai_context_bar("Mission Control: explique por que esta rota domina ou quais riscos ainda precisam ser stress-tested antes da implementação.")
                mcai1,mcai2=st.columns(2)
                with mcai1:
                    if st.button("✦ Ask Murphy about this route",use_container_width=True,key="v26_mission_ai"):
                        st.session_state.v26_ai_context=f"Analise a rota {best.get('Cenário','')}: throughput {best.get('Throughput',0):.2f}, SLA {best.get('SLA',0):.0f}%, custo/un R$ {best.get('Custo/un',0):.2f}, investimento R$ {best.get('Investimento estimado',0):,.0f}. Explique trade-offs e o stress-test necessário antes de aprovar."
                        st.session_state.active_page="Murphy AI"; st.rerun()
                with mcai2:
                    if st.button("⌁ Stress-test this route",use_container_width=True,key="v26_mission_stress"):
                        st.session_state.scenario_result=best['result']; st.session_state.scenario_config=best['config']; st.session_state.active_page="Stress Lab"; st.rerun()
                st.markdown("### Melhor rota encontrada")
                x1,x2,x3,x4,x5=st.columns(5)
                with x1: metric_card("Throughput", f"{best['Throughput']:.2f} un/h", f"{best['Throughput Δ (%)']:+.1f}% vs. base", "#3F8E89")
                with x2: metric_card("SLA", f"{best['SLA']:.0f}%", f"{best['SLA Δ (p.p.)']:+.1f} p.p.", "#2B7A5A")
                with x3: metric_card("Recursos", f"+{best['Operadores +']} op. · +{best['Máquinas +']} maq.", "mudança estrutural", "#1D292D")
                with x4: metric_card("Custo/un", f"R$ {best['Custo/un']:.2f}", f"{best['Custo/un Δ (%)']:+.1f}% vs. base", "#1D292D")
                with x5: metric_card("Implantação", f"R$ {best.get('Investimento estimado',0):,.0f}", "estimativa configurável", "#FF681B")
                if st.button("Carregar rota no Comparar"):
                    st.session_state.scenario_result=best['result']; st.session_state.scenario_config=best['config']
                    register_decision(best.get('Cenário','Rota para meta'), "Mission Control", best['result'])
                    st.success("Rota carregada. Abra Comparar.")
                st.markdown("### Finance Lens")
                f1,f2,f3=st.columns(3)
                with f1: margin=st.number_input("Margem de contribuição por unidade (R$)",min_value=0.0,value=50.0,step=5.0)
                with f2: hours=st.number_input("Horas produtivas/dia",min_value=1.0,max_value=24.0,value=8.0,step=1.0)
                with f3: investment=st.number_input("Investimento inicial estimado (R$)",min_value=0.0,value=0.0,step=1000.0)
                fin=finance_lens(base,best['result'],margin,hours,investment)
                q1,q2,q3,q4=st.columns(4)
                with q1: st.metric("Unidades extras/dia", f"{fin['extra_units_day']:.1f}")
                with q2: st.metric("Contribuição adicional/dia", f"R$ {fin['extra_contribution_day']:.2f}")
                with q3: st.metric("Resultado líquido/dia", f"R$ {fin['net_day']:.2f}")
                with q4: st.metric("Payback", "—" if fin['payback_days'] is None else f"{fin['payback_days']:.1f} dias")
            view=pd.DataFrame([{k:v for k,v in x.items() if k not in ['result','config','score']} for x in rows])
            st.markdown("### Rotas exploradas")
            st.dataframe(view,use_container_width=True,hide_index=True)
