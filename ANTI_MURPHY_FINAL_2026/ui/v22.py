from __future__ import annotations

from html import escape
from typing import Any, Dict, List
import streamlit as st


def inject_v22_css() -> None:
    st.markdown(r'''<style>
:root{--ai-ink:#0D1C21;--ai-panel:#102126;--ai-orange:#FF681B;--ai-teal:#57B8AE;--ai-line:#D8E1DE;--ai-paper:#FCFDFC}
.am-ai-hero{display:grid;grid-template-columns:1.35fr .65fr;gap:12px;margin:8px 0 14px}.am-ai-main{background:linear-gradient(145deg,#09191D,#10282D);color:#F6FAF9;border:1px solid #294249;border-radius:14px;padding:22px;position:relative;overflow:hidden;min-height:185px}.am-ai-main:after{content:"";position:absolute;width:260px;height:260px;border:1px solid rgba(87,184,174,.12);border-radius:50%;right:-90px;top:-120px;box-shadow:0 0 0 42px rgba(87,184,174,.025),0 0 0 84px rgba(255,104,27,.018)}.am-ai-ey{font:800 .43rem "Cascadia Mono",monospace;letter-spacing:.14em;color:#80A49D}.am-ai-title{font:720 1.55rem "Aptos Display","Segoe UI Variable Display",sans-serif;line-height:1.05;margin:8px 0 7px;max-width:680px}.am-ai-title span{color:var(--ai-orange)}.am-ai-copy{font-size:.70rem;line-height:1.55;color:#AFC0BB;max-width:680px}.am-ai-pills{display:flex;gap:6px;flex-wrap:wrap;margin-top:16px}.am-ai-pill{font-size:.48rem;border:1px solid #35535A;border-radius:999px;padding:5px 9px;color:#B8C7C3;background:#11262B}.am-ai-side{display:grid;grid-template-columns:1fr;gap:8px}.am-ai-stat{background:var(--ai-paper);border:1px solid var(--ai-line);border-radius:10px;padding:13px 14px}.am-ai-stat .k{font:800 .38rem "Cascadia Mono",monospace;letter-spacing:.12em;color:#899792}.am-ai-stat .v{font:720 .88rem "Aptos Display",sans-serif;margin-top:4px;color:#17262A}.am-ai-stat .s{font-size:.50rem;color:#7D8B86;margin-top:3px;line-height:1.35}.am-ai-trust{border-left:3px solid var(--ai-teal)}.am-ai-context{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:7px 0 12px}.am-ai-context>div{background:#fff;border:1px solid var(--ai-line);border-radius:8px;padding:10px 11px}.am-ai-context .k{font:800 .34rem "Cascadia Mono",monospace;letter-spacing:.11em;color:#87958F}.am-ai-context .v{font-weight:720;font-size:.72rem;margin-top:4px;color:#17262A}.am-ai-context .hot{color:var(--ai-orange)}.am-ai-mode{display:inline-flex;gap:6px;align-items:center;border:1px solid #D6E0DD;border-radius:999px;padding:4px 8px;font-size:.47rem;color:#53635E;background:#fff}.am-ai-dot{width:6px;height:6px;border-radius:50%;background:var(--ai-teal);box-shadow:0 0 0 3px rgba(87,184,174,.10)}.am-ai-note{background:#F7FAF9;border:1px solid var(--ai-line);border-left:3px solid var(--ai-orange);padding:10px 12px;border-radius:8px;font-size:.55rem;color:#65736E;line-height:1.5}.am-ai-action{background:linear-gradient(140deg,#102126,#132C31);border:1px solid #304B52;border-radius:10px;padding:13px;color:#F2F7F5;margin:7px 0}.am-ai-action .k{font:800 .37rem "Cascadia Mono",monospace;color:#7E9A94;letter-spacing:.12em}.am-ai-action .v{font-size:.74rem;font-weight:720;margin-top:5px}.am-ai-action .s{font-size:.50rem;color:#A8B8B3;margin-top:4px;line-height:1.4}
/* Chat styles live in ui/design_system.py; keep ONE authoritative chat theme. */
@media(max-width:1100px){.am-ai-hero{grid-template-columns:1fr}.am-ai-context{grid-template-columns:1fr 1fr}}@media(max-width:700px){.am-ai-context{grid-template-columns:1fr}}
</style>''', unsafe_allow_html=True)


def ai_hero(context: Dict[str, Any], connected: bool, model: str) -> None:
    b=context.get('baseline',{}); c=context.get('constraint',{}); ri=b.get('resilience',{})
    mode='API configurada · não verificada' if connected else 'Modo local · regras e simulação'
    st.markdown(f'''<div class="am-ai-hero"><div class="am-ai-main"><div class="am-ai-ey">MURPHY AI · DECISION COPILOT</div><div class="am-ai-title">Pergunte à operação. <span>Não ao dashboard.</span></div><div class="am-ai-copy">O copiloto lê o estado simulado, compara cenários e traduz sinais técnicos em próximos experimentos. KPIs continuam vindo do motor DES; a IA interpreta, explica e orienta testes.</div><div class="am-ai-pills"><span class="am-ai-pill">Explain</span><span class="am-ai-pill">Recommend</span><span class="am-ai-pill">Compare</span><span class="am-ai-pill">Brief</span><span class="am-ai-pill">Experiment</span></div></div><div class="am-ai-side"><div class="am-ai-stat"><div class="k">MODE</div><div class="v">{escape(mode)}</div><div class="s">{escape(model if connected else 'Sem chave/API necessária')}</div></div><div class="am-ai-stat"><div class="k">CURRENT CONSTRAINT</div><div class="v">{escape(str(c.get('station','-')))}</div><div class="s">fila {c.get('max_queue',0)} · espera {float(c.get('avg_wait_min',0)):.1f} min</div></div><div class="am-ai-stat am-ai-trust"><div class="k">GROUNDING</div><div class="v">Simulation first</div><div class="s">A IA não inventa resultados não simulados.</div></div></div></div>''',unsafe_allow_html=True)
    st.markdown(f'''<div class="am-ai-context"><div><div class="k">THROUGHPUT</div><div class="v">{float(b.get('throughput_h',0)):.2f} un/h</div></div><div><div class="k">SLA</div><div class="v hot">{float(b.get('sla_pct',0)):.0f}%</div></div><div><div class="k">RESILIENCE</div><div class="v">{float(ri.get('score',0)):.0f}/100 · {escape(str(ri.get('band','-')))}</div></div><div><div class="k">PENALTIES</div><div class="v">R$ {float(b.get('penalties_total',0)):,.0f}</div></div></div>''',unsafe_allow_html=True)


def recommended_action_card(rec: Dict[str, Any] | None) -> None:
    if not rec:
        return
    st.markdown(f'''<div class="am-ai-action"><div class="k">NEXT EXPERIMENT · HEURISTIC</div><div class="v">{escape(str(rec.get('title','-')))}</div><div class="s">{escape(str(rec.get('why','')))} · força da regra {int(rec.get('confidence',0))}/100 (não é probabilidade)</div></div>''',unsafe_allow_html=True)


def trust_note() -> None:
    st.markdown('''<div class="am-ai-note"><b>Arquitetura de confiança:</b> a simulação calcula filas, gargalos, SLA, custos e tempos. O Murphy AI recebe um pacote estruturado desses resultados e atua como camada de interpretação. Se uma hipótese ainda não foi simulada, o copiloto deve propor o experimento em vez de fabricar um resultado.</div>''',unsafe_allow_html=True)


def mode_badge(connected: bool) -> None:
    label='Chave configurada · teste ao usar' if connected else 'Inteligência local'
    st.markdown(f'<span class="am-ai-mode"><span class="am-ai-dot"></span>{label}</span>', unsafe_allow_html=True)
