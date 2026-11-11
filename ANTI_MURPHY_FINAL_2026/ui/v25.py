from __future__ import annotations
from html import escape
from typing import Any, Dict, List
import streamlit as st
import plotly.graph_objects as go


def _e(v: Any) -> str: return escape(str(v))


def inject_v25_css() -> None:
    st.markdown(r'''<style>
:root{--v25-bg:#EEF2F1;--v25-paper:#FAFCFB;--v25-paper2:#F5F8F7;--v25-ink:#0B171A;--v25-muted:#60706B;--v25-line:#D8E1DE;--v25-dark:#06161A;--v25-dark2:#10272C;--v25-orange:#FF681B;--v25-teal:#3E9B91;--v25-green:#24745E;--v25-red:#C64A42}
.stApp{background:radial-gradient(circle at 76% -10%,rgba(62,155,145,.08),transparent 28%),linear-gradient(180deg,#F7F9F8 0%,#EEF3F1 42%,#EBF0EE 100%)!important;color:var(--v25-ink)}
.block-container{max-width:1920px!important;padding:.58rem .85rem 3.5rem!important}
.am16_navrail{background:linear-gradient(180deg,#061619 0%,#0A2024 100%)!important;border:1px solid #1A353A!important;border-radius:14px!important;padding:11px 9px!important;box-shadow:0 24px 72px rgba(6,22,25,.14)!important}
.am16-topbar{border-radius:10px!important;background:rgba(250,252,251,.91)!important;backdrop-filter:blur(22px) saturate(130%);border:1px solid rgba(206,218,214,.86)!important;box-shadow:0 7px 25px rgba(9,27,31,.035)!important}
.am16-pagehead h1{font-family:"Segoe UI Variable Display","Aptos Display","Segoe UI",sans-serif!important;font-weight:680!important;font-size:1.92rem!important;letter-spacing:-.052em!important}
h1,h2,h3{font-family:"Segoe UI Variable Display","Aptos Display","Segoe UI",sans-serif!important;letter-spacing:-.025em}p,div,label,input,button,textarea{font-family:"Segoe UI Variable Text","Aptos","Segoe UI",sans-serif}
.v20-workflow{opacity:.92;border-radius:8px!important}.v20-stage{min-height:34px!important}.v20-stage .t{font-size:.57rem!important;letter-spacing:.09em!important}
[data-testid="stVerticalBlock"]{gap:.24rem!important}[data-testid="stHorizontalBlock"]{gap:.35rem!important}
.v25-shell{background:rgba(250,252,251,.84);border:1px solid var(--v25-line);border-radius:11px;padding:12px 13px;margin:7px 0 9px}.v25-shell.dark{background:linear-gradient(145deg,#06161A,#0D252A);color:white;border-color:#234047}.v25-ey{font:800 .34rem "Cascadia Mono",Consolas,monospace;letter-spacing:.14em;color:#7D8E88;text-transform:uppercase}.v25-title{font-size:1rem;font-weight:720;letter-spacing:-.028em;margin-top:5px}.v25-copy{font-size:.55rem;color:#687873;line-height:1.55;margin-top:3px}.dark .v25-copy{color:#A7BAB4}
.v25-mode{display:flex;gap:5px;align-items:center;padding:5px;background:#EDF2F0;border:1px solid #D8E1DE;border-radius:7px}.v25-mode span{font:800 .31rem "Cascadia Mono",monospace;letter-spacing:.11em;color:#71817C;padding:4px 7px}.v25-mode .on{background:#0B1C20;color:white;border-radius:5px}
.v25-portfolio{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:7px 0}.v25-leader{background:#FAFCFB;border:1px solid var(--v25-line);border-radius:9px;padding:10px 11px;position:relative;overflow:hidden}.v25-leader:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--v25-teal)}.v25-leader .k{font:800 .30rem "Cascadia Mono",monospace;color:#7A8A85;letter-spacing:.11em}.v25-leader .v{font-size:.72rem;font-weight:720;margin-top:4px}.v25-leader .s{font-size:.44rem;color:#74837E;margin-top:3px}
.v25-root{display:grid;grid-template-columns:1.25fr repeat(3,.75fr);gap:1px;background:var(--v25-line);border:1px solid var(--v25-line);border-radius:9px;overflow:hidden}.v25-root>div{background:#FAFCFB;padding:10px}.v25-root .lead{background:#071A1E;color:#fff}.v25-root .k{font:800 .3rem "Cascadia Mono",monospace;color:#81928C;letter-spacing:.1em}.v25-root .v{font-size:.72rem;font-weight:700;margin-top:4px}.v25-root .lead .s{color:#A6B8B2}.v25-root .s{font-size:.43rem;color:#75847F;margin-top:2px}
.v25-agent-run{background:linear-gradient(135deg,#07191D,#102C31);border:1px solid #29474D;border-radius:11px;padding:13px;color:#F2F8F6;margin:8px 0}.v25-agent-run .path{display:grid;grid-template-columns:repeat(5,1fr);gap:5px;margin-top:9px}.v25-agent-run .node{border:1px solid #29464B;background:#0B2328;border-radius:7px;padding:8px}.v25-agent-run .node b{display:block;font-size:.52rem}.v25-agent-run .node span{font-size:.4rem;color:#9EB2AC}.v25-agent-run .node.done{border-color:#3E9B91;box-shadow:inset 0 0 0 1px rgba(62,155,145,.15)}
.v25-digest{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--v25-line);border:1px solid var(--v25-line);border-radius:8px;overflow:hidden}.v25-digest>div{background:#FAFCFB;padding:9px 10px}.v25-digest .k{font:800 .3rem "Cascadia Mono",monospace;color:#7C8C87;letter-spacing:.1em}.v25-digest .v{font-size:.73rem;font-weight:730;margin-top:3px}.v25-digest .good .v{color:var(--v25-green)}.v25-digest .bad .v{color:var(--v25-red)}
.v25-present{background:linear-gradient(145deg,#061519,#0A2328);border:1px solid #28454B;border-radius:14px;padding:18px;color:#fff;min-height:190px;display:flex;flex-direction:column;justify-content:space-between}.v25-present .label{font:800 .34rem "Cascadia Mono",monospace;letter-spacing:.15em;color:#7CBDB5}.v25-present h2{font-size:1.55rem;margin:8px 0 4px;letter-spacing:-.04em}.v25-present p{font-size:.62rem;color:#A6B9B3;max-width:720px}.v25-present .metric{font-size:2.1rem;font-weight:760;letter-spacing:-.05em;color:#fff}
.stButton>button,.stDownloadButton>button{border-radius:6px!important;min-height:35px!important;transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease!important}.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 7px 18px rgba(10,28,32,.07)!important}
[data-testid="stMetric"]{background:transparent!important;border:none!important;padding:.2rem 0!important}[data-testid="stMetricValue"]{font-family:"Segoe UI Variable Display","Aptos Display",sans-serif!important;letter-spacing:-.035em}
@media(max-width:1200px){.v25-portfolio{grid-template-columns:1fr 1fr}.v25-agent-run .path{grid-template-columns:1fr 1fr}.v25-root{grid-template-columns:1fr 1fr}.v25-root .lead{grid-column:1/-1}}@media(max-width:760px){.v25-portfolio,.v25-digest,.v25-root,.v25-agent-run .path{grid-template-columns:1fr}}
</style>''', unsafe_allow_html=True)


def mode_badge_v25(mode: str) -> None:
    mode=str(mode).upper()
    st.markdown(f'<div class="v25-mode"><span class="{"on" if mode=="OPERATOR" else ""}">OPERATOR</span><span class="{"on" if mode=="EXECUTIVE" else ""}">EXECUTIVE</span></div>',unsafe_allow_html=True)


def portfolio_leaders(leaders: Dict[str, Dict[str, Any]]) -> None:
    specs=[('FLOW','flow','Throughput'),('SERVICE','service','SLA'),('ECONOMICS','economics','Custo/un'),('SPEED','speed','Makespan')]
    cards=[]
    for label,key,metric in specs:
        x=leaders.get(key) or {}
        if key=='flow': val=f"{x.get('throughput',0):.2f} un/h"
        elif key=='service': val=f"{x.get('sla',0):.0f}%"
        elif key=='economics': val=f"R$ {x.get('unit_cost',0):.2f}"
        else: val=f"{x.get('makespan',0):.1f} h"
        cards.append(f'<div class="v25-leader"><div class="k">BEST {label}</div><div class="v">{_e(x.get("name","—"))}</div><div class="s">{metric}: {val}</div></div>')
    st.markdown('<div class="v25-portfolio">'+''.join(cards)+'</div>',unsafe_allow_html=True)


def root_cause_panel(rc: Dict[str, Any]) -> None:
    top=rc.get('top') or {}
    st.markdown(f'''<div class="v25-root"><div class="lead"><div class="k">ROOT CAUSE EXPLORER</div><div class="v">{_e(top.get('station','—'))} · {_e(top.get('name',''))}</div><div class="s">Maior concentração de pressão no estado simulado atual.</div></div><div><div class="k">PRESSURE SHARE</div><div class="v">{top.get('share_pct',0):.0f}%</div><div class="s">participação no score de pressão</div></div><div><div class="k">WAIT</div><div class="v">{top.get('wait_min',0):.0f} min</div><div class="s">espera média</div></div><div><div class="k">QUEUE</div><div class="v">{top.get('queue',0)}</div><div class="s">fila máxima observada</div></div></div>''',unsafe_allow_html=True)


def root_cause_chart(rc: Dict[str, Any]) -> go.Figure:
    rows=rc.get('rows',[])
    fig=go.Figure()
    fig.add_trace(go.Bar(y=[x['station'] for x in rows][::-1],x=[x['pressure_score'] for x in rows][::-1],orientation='h',marker=dict(color=['#FF681B' if i==len(rows)-1 else '#8FA39D' for i in range(len(rows))]),text=[f"{x['share_pct']:.0f}%" for x in rows][::-1],textposition='outside',hovertemplate='%{y}<br>Pressure %{x:.1f}<extra></extra>'))
    fig.update_layout(height=max(240,55*len(rows)),margin=dict(l=10,r=45,t=15,b=25),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Segoe UI Variable, Aptos',size=11,color='#65756F'),showlegend=False)
    fig.update_xaxes(showgrid=False,visible=False);fig.update_yaxes(showgrid=False)
    return fig


def agent_run_header(target_sla: float, count: int) -> None:
    nodes=[('01','DIAGNOSE','restrição + risco'),('02','GENERATE','microdecisões'),('03','SIMULATE',f'{count} candidatos'),('04','RANK','trade-offs'),('05','HANDOFF',f'meta SLA {target_sla:.0f}%')]
    st.markdown('<div class="v25-agent-run"><div class="v25-ey" style="color:#77BBB2">DECISION AUTOPILOT</div><div class="v25-title">Agentes coordenados, números vindos da simulação.</div><div class="v25-copy">O Murphy AI organiza a busca; cada KPI mostrado abaixo foi produzido pelo motor DES.</div><div class="path">'+''.join(f'<div class="node done"><b>{n} · {t}</b><span>{s}</span></div>' for n,t,s in nodes)+'</div></div>',unsafe_allow_html=True)


def change_digest_ui(rows: List[Dict[str,str]]) -> None:
    st.markdown('<div class="v25-digest">'+''.join(f'<div class="{_e(x.get("tone","neutral"))}"><div class="k">{_e(x.get("metric"))}</div><div class="v">{_e(x.get("value"))}</div></div>' for x in rows)+'</div>',unsafe_allow_html=True)


def presentation_hero(base: Dict[str,Any], alt: Dict[str,Any] | None, resilience: Dict[str,Any]) -> None:
    if alt is None:
        title=f"A operação está pressionada em {base.get('bottleneck','—')}"
        copy="O Anti-Murphy transforma o estado atual em um Decision Twin: diagnostica restrições, testa contrafactuais e mede risco antes da mudança real."
        metric=f"SLA {base.get('sla_pct',0):.0f}%"
    else:
        title=f"Decisão testada: {alt.get('name','Cenário')}"
        copy=f"O cenário desloca o sistema para {alt.get('throughput_h',0):.2f} un/h, SLA {alt.get('sla_pct',0):.0f}% e gargalo {alt.get('bottleneck','—')}."
        metric=f"{alt.get('throughput_h',0):.2f} un/h"
    st.markdown(f'<div class="v25-present"><div><div class="label">ANTI-MURPHY · OPERATIONAL DIGITAL TWIN</div><h2>{_e(title)}</h2><p>{_e(copy)}</p></div><div><div class="metric">{_e(metric)}</div><div class="v25-copy" style="color:#8CA29B">Resiliência {resilience.get("score",0):.0f}/100 · evidência baseada no modelo atual</div></div></div>',unsafe_allow_html=True)
