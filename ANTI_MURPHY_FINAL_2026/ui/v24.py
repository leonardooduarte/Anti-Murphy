from __future__ import annotations
from html import escape
from typing import Any, Dict, List
import streamlit as st
import plotly.graph_objects as go


def _e(v: Any) -> str: return escape(str(v))


def inject_v24_css() -> None:
    st.markdown(r'''<style>
:root{--v24-canvas:#F2F5F4;--v24-paper:#FCFDFC;--v24-ink:#0B191D;--v24-muted:#687773;--v24-line:#D7E0DD;--v24-dark:#07171B;--v24-dark2:#10282D;--v24-orange:#FF681B;--v24-teal:#48A99E;--v24-red:#C5524A;--v24-green:#2D7B65}
.stApp{background:linear-gradient(180deg,#F7F9F8 0,#F1F4F3 18%,#EDF2F0 100%)!important}
.block-container{max-width:1900px!important;padding:.72rem 1rem 4rem!important}
.am16_navrail{background:linear-gradient(180deg,#06161A,#091D21)!important;border:1px solid #1E373D!important;border-radius:12px!important;padding:12px 10px!important;box-shadow:0 22px 60px rgba(7,23,27,.12)!important}
.am16-topbar{background:rgba(252,253,252,.95)!important;backdrop-filter:blur(16px);border:1px solid var(--v24-line)!important;box-shadow:0 8px 24px rgba(10,27,31,.04)!important}
.v20-workflow{margin:3px 0 7px!important;background:transparent!important;border-color:#DDE5E2!important}.v20-stage{min-height:39px!important;padding:6px 9px!important}.v20-stage .t{font-size:.60rem!important}.v20-stage .s{display:none!important}
.am16-pagehead{margin:4px 0 7px!important}.am16-pagehead h1{font-size:1.9rem!important;letter-spacing:-.045em!important}.am16-pagehead .copy{max-width:720px!important;font-size:.62rem!important}
[data-testid="stVerticalBlock"]{gap:.28rem!important}[data-testid="stHorizontalBlock"]{gap:.38rem!important}
.v24-section{border:1px solid var(--v24-line);background:rgba(252,253,252,.92);border-radius:9px;padding:13px 14px;margin:7px 0 9px}.v24-section.dark{background:linear-gradient(145deg,#07171B,#10272C);color:#EDF4F2;border-color:#274248}.v24-ey{font:800 .35rem "Cascadia Mono",Consolas,monospace;letter-spacing:.14em;color:#80928C;text-transform:uppercase}.v24-title{font-weight:740;font-size:.95rem;letter-spacing:-.02em;margin-top:5px}.v24-copy{font-size:.53rem;color:#72817C;margin-top:4px;line-height:1.5}.dark .v24-title{color:#fff}.dark .v24-copy{color:#AABBB6}
.v24-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--v24-line);border:1px solid var(--v24-line);border-radius:8px;overflow:hidden;margin:7px 0}.v24-kpi{background:var(--v24-paper);padding:10px 11px}.v24-kpi .k{font:800 .32rem "Cascadia Mono",monospace;letter-spacing:.12em;color:#8B9893}.v24-kpi .v{font-size:.92rem;font-weight:720;margin-top:4px;color:var(--v24-ink)}.v24-kpi .s{font-size:.45rem;color:#7A8984;margin-top:2px}.v24-kpi.critical .v{color:var(--v24-orange)}.v24-kpi.good .v{color:var(--v24-green)}
.v24-trust-grid{display:grid;grid-template-columns:1.1fr repeat(3,1fr);gap:1px;background:var(--v24-line);border:1px solid var(--v24-line);border-radius:8px;overflow:hidden}.v24-trust-grid>div{background:var(--v24-paper);padding:11px}.v24-trust-grid .lead{background:var(--v24-dark);color:#fff}.v24-trust-grid .k{font:800 .31rem "Cascadia Mono",monospace;letter-spacing:.11em;color:#85958F}.v24-trust-grid .v{font-size:.84rem;font-weight:720;margin-top:4px}.v24-trust-grid .s{font-size:.44rem;color:#7D8B86;margin-top:2px}.v24-trust-grid .lead .s{color:#9DB0AA}
.v24-agent{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin:7px 0}.v24-agent>div{border:1px solid var(--v24-line);background:#fff;border-radius:8px;padding:9px 10px}.v24-agent .n{font:800 .31rem "Cascadia Mono",monospace;color:var(--v24-orange);letter-spacing:.1em}.v24-agent .t{font-size:.63rem;font-weight:700;margin-top:4px}.v24-agent .s{font-size:.43rem;color:#788680;margin-top:2px}
.v24-rule{display:grid;grid-template-columns:1.2fr repeat(5,.8fr);gap:1px;background:var(--v24-line);border:1px solid var(--v24-line);border-radius:8px;overflow:hidden;margin:7px 0}.v24-rule>div{background:#fff;padding:9px}.v24-rule .lead{background:var(--v24-dark);color:#fff}.v24-rule .k{font:800 .3rem "Cascadia Mono",monospace;letter-spacing:.1em;color:#84948E}.v24-rule .v{font-size:.67rem;font-weight:700;margin-top:3px}
.v24-maint{display:grid;grid-template-columns:1.1fr repeat(4,1fr);gap:1px;background:var(--v24-line);border:1px solid var(--v24-line);border-radius:8px;overflow:hidden}.v24-maint>div{padding:9px 10px;background:#fff}.v24-maint .lead{background:var(--v24-dark);color:#fff}.v24-maint .k{font:800 .3rem "Cascadia Mono",monospace;color:#899793;letter-spacing:.1em}.v24-maint .v{font-size:.69rem;font-weight:700;margin-top:3px}
main .stButton>button,main .stDownloadButton>button{border-radius:6px!important;min-height:36px!important}.v23-callout{border-radius:7px!important}
@media(max-width:1200px){.v24-agent{grid-template-columns:1fr 1fr}.v24-kpi-grid,.v24-trust-grid{grid-template-columns:1fr 1fr}.v24-rule{grid-template-columns:1fr 1fr}.v24-rule .lead{grid-column:1/-1}}@media(max-width:760px){.v24-agent,.v24-kpi-grid,.v24-trust-grid,.v24-rule,.v24-maint{grid-template-columns:1fr}}
</style>''', unsafe_allow_html=True)


def trust_header(model_score: float, calibration: Dict[str, Any] | None, mc: Dict[str, Any] | None, data_label: str) -> None:
    cal_score = calibration.get('score') if calibration else None
    mc_runs = len(mc.get('runs', [])) if mc else 0
    stability = float(mc.get('bottleneck_share',0)) if mc else 0.0
    cal_txt='—' if cal_score is None else f'{cal_score:.0f}/100'
    st.markdown(f'''<div class="v24-trust-grid"><div class="lead"><div class="k">EVIDÊNCIAS DO MODELO</div><div class="v">Dados consistentes não equivalem a modelo validado.</div><div class="s">Separates structural completeness, real-world calibration and simulated uncertainty.</div></div><div><div class="k">VERIFICAÇÃO CADASTRAL</div><div class="v">{model_score:.0f}/100</div><div class="s">completude e consistência</div></div><div><div class="k">CALIBRATION</div><div class="v">{cal_txt}</div><div class="s">aderência a observações reais</div></div><div><div class="k">SIMULATION EVIDENCE</div><div class="v">{mc_runs} runs</div><div class="s">gargalo dominante {stability:.0f}%</div></div></div>''',unsafe_allow_html=True)


def agent_architecture() -> None:
    items=[('01','Diagnosis Agent','lê gargalo, fila, SLA e risco'),('02','Experiment Agent','transforma hipótese em cenário'),('03','Optimization Agent','compara rotas e fronteiras'),('04','Risk Agent','estressa e procura ruptura'),('05','Executive Agent','resume evidência e trade-offs')]
    st.markdown('<div class="v24-agent">'+''.join(f'<div><div class="n">{n}</div><div class="t">{t}</div><div class="s">{s}</div></div>' for n,t,s in items)+'</div>',unsafe_allow_html=True)


def scheduling_row(row: Dict[str, Any], best: bool=False) -> None:
    cls=' style="color:#2D7B65"' if best else ''
    st.markdown(f'''<div class="v24-rule"><div class="lead"><div class="k">DISPATCH RULE</div><div class="v">{_e(row.get('rule'))}{' · BEST' if best else ''}</div></div><div><div class="k">THROUGHPUT</div><div class="v"{cls}>{row.get('throughput',0):.2f} un/h</div></div><div><div class="k">SLA</div><div class="v"{cls}>{row.get('sla',0):.0f}%</div></div><div><div class="k">MAKESPAN</div><div class="v">{row.get('makespan',0):.1f} h</div></div><div><div class="k">COST / UNIT</div><div class="v">R$ {row.get('unit_cost',0):.2f}</div></div><div><div class="k">BOTTLENECK</div><div class="v">{_e(row.get('bottleneck','-'))}</div></div></div>''',unsafe_allow_html=True)


def reliability_strip(row: Dict[str, Any]) -> None:
    st.markdown(f'''<div class="v24-maint"><div class="lead"><div class="k">ASSET RISK</div><div class="v">{_e(row.get('station'))} · {_e(row.get('name'))}</div></div><div><div class="k">FAILURE PROB.</div><div class="v">{row.get('failure_probability',0):.1f}%</div></div><div><div class="k">EXPECTED DOWNTIME</div><div class="v">{row.get('expected_downtime_h',0):.1f} h</div></div><div><div class="k">RISK SCORE</div><div class="v">{row.get('risk_score',0):.0f}/100</div></div><div><div class="k">DOWNTIME EXPOSURE</div><div class="v">R$ {row.get('downtime_exposure',0):,.0f}</div></div></div>''',unsafe_allow_html=True)


def pareto_chart(rows: List[Dict[str, Any]], frontier: List[Dict[str, Any]]) -> go.Figure:
    ids={id(x) for x in frontier}
    fig=go.Figure()
    others=[x for x in rows if id(x) not in ids]
    if others:
        fig.add_trace(go.Scatter(x=[x['unit_cost'] for x in others],y=[x['sla'] for x in others],mode='markers',name='Dominados',text=[x.get('name',x.get('rule','Scenario')) for x in others],marker=dict(size=[max(8,min(25,7+x.get('throughput',0)*2)) for x in others],color='#AAB7B3',opacity=.45),hovertemplate='%{text}<br>Custo/un R$ %{x:.2f}<br>SLA %{y:.0f}%<extra></extra>'))
    if frontier:
        fig.add_trace(go.Scatter(x=[x['unit_cost'] for x in frontier],y=[x['sla'] for x in frontier],mode='markers+text',name='Pareto',text=[x.get('name',x.get('rule','Scenario')) for x in frontier],textposition='top center',marker=dict(size=[max(12,min(28,9+x.get('throughput',0)*2)) for x in frontier],color='#FF681B',line=dict(color='white',width=1)),hovertemplate='%{text}<br>Custo/un R$ %{x:.2f}<br>SLA %{y:.0f}%<extra></extra>'))
    fig.update_layout(height=390,margin=dict(l=25,r=15,t=25,b=45),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#142227',font=dict(family='Segoe UI Variable, Aptos',size=11,color='#CBD8D3'),xaxis_title='Custo por unidade ↓',yaxis_title='SLA ↑',legend=dict(orientation='h',y=1.07,x=0))
    fig.update_xaxes(gridcolor='#E3EAE7');fig.update_yaxes(gridcolor='#E3EAE7',range=[0,105])
    return fig
