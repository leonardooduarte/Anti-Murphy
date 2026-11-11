from __future__ import annotations

from html import escape
from typing import Any, Dict, List
import streamlit as st
import plotly.graph_objects as go


def _e(v: Any) -> str:
    return escape(str(v))


def inject_v23_css() -> None:
    st.markdown(r'''<style>
:root{--v23-bg:#EDF1F0;--v23-paper:#FBFCFB;--v23-paper2:#F5F7F6;--v23-ink:#0D1B1F;--v23-muted:#667570;--v23-line:#D3DDDA;--v23-dark:#07171B;--v23-dark2:#10262B;--v23-orange:#FF681B;--v23-teal:#47A89D;--v23-green:#2D7B65;--v23-red:#B94A43;--v23-amber:#B37A32}
html,body,[class*="css"]{font-family:"Segoe UI Variable","Aptos","Segoe UI",system-ui,sans-serif!important}
.stApp{background:radial-gradient(900px 420px at 102% -8%,rgba(255,104,27,.045),transparent 62%),radial-gradient(900px 480px at 18% -14%,rgba(71,168,157,.05),transparent 68%),var(--v23-bg)!important}
.block-container{max-width:1880px!important;padding:1rem 1.2rem 5rem!important}
h1,h2,h3,h4,.am16-pagehead h1{font-family:"Segoe UI Variable Display","Aptos Display","Segoe UI",sans-serif!important;letter-spacing:-.035em!important}
p,.stCaption{font-size:.68rem!important;line-height:1.58!important}
.am16_navrail{position:sticky;top:12px}.am16-side-brand{padding-top:2px!important}.am16-side-footer{opacity:.62!important;font-size:.43rem!important}
.am16-topbar{border-radius:7px!important;background:rgba(251,252,251,.92)!important;border-color:var(--v23-line)!important;box-shadow:0 10px 32px rgba(13,27,31,.035)!important}
.am16-pagehead{margin-bottom:10px!important}.am16-pagehead h1{font-size:1.75rem!important;font-weight:680!important}.am16-pagehead .copy{font-size:.69rem!important;max-width:850px!important}
.v20-workflow{border-color:var(--v23-line)!important;background:rgba(251,252,251,.72)!important;box-shadow:none!important}
main .stButton>button,main .stDownloadButton>button{border-radius:6px!important;min-height:38px!important;font-weight:620!important}
main .stButton>button:hover,main .stDownloadButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 20px rgba(7,23,27,.055)!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border-radius:7px!important;border-color:var(--v23-line)!important;background:var(--v23-paper)!important}
.v23-hero{display:grid;grid-template-columns:1.35fr .65fr;gap:10px;margin:9px 0 12px}.v23-hero-main{background:linear-gradient(145deg,#07171B,#10272C);border:1px solid #29444A;border-radius:11px;padding:20px;color:#EFF5F3;position:relative;overflow:hidden}.v23-hero-main:after{content:"";position:absolute;right:-90px;top:-130px;width:310px;height:310px;border-radius:50%;border:1px solid rgba(71,168,157,.14);box-shadow:0 0 0 45px rgba(71,168,157,.026),0 0 0 90px rgba(255,104,27,.018)}.v23-ey{font:800 .39rem "Cascadia Mono",Consolas,monospace;letter-spacing:.14em;color:#7E9A94}.v23-hero-main h2{color:#fff!important;font-size:1.34rem!important;margin:6px 0 5px!important}.v23-hero-main p{color:#AFC0BB!important;max-width:720px;margin:0}.v23-hero-side{display:grid;grid-template-columns:1fr 1fr;gap:8px}.v23-stat{background:var(--v23-paper);border:1px solid var(--v23-line);border-radius:8px;padding:12px}.v23-stat .k{font:800 .34rem "Cascadia Mono",monospace;letter-spacing:.11em;color:#87958F}.v23-stat .v{font:700 .88rem "Segoe UI Variable Display",sans-serif;margin-top:4px;color:var(--v23-ink)}.v23-stat .s{font-size:.47rem;color:#7A8883;margin-top:3px}.v23-exec-grid{display:grid;grid-template-columns:1.15fr repeat(3,1fr);gap:1px;background:var(--v23-line);border:1px solid var(--v23-line);border-radius:8px;overflow:hidden;margin:8px 0 12px}.v23-exec-grid>div{background:var(--v23-paper);padding:11px 12px}.v23-exec-grid .lead{background:var(--v23-dark);color:#fff}.v23-exec-grid .k{font:800 .34rem "Cascadia Mono",monospace;letter-spacing:.11em;color:#82918C}.v23-exec-grid .v{font:700 .82rem "Segoe UI Variable Display",sans-serif;margin-top:4px}.v23-exec-grid .lead .v{color:#fff}.v23-exec-grid .s{font-size:.45rem;color:#7B8984;margin-top:2px}.v23-exec-grid .lead .s{color:#A3B2AD}.v23-score{display:grid;grid-template-columns:130px repeat(4,1fr);gap:1px;background:var(--v23-line);border:1px solid var(--v23-line);border-radius:8px;overflow:hidden;margin:8px 0 11px}.v23-score>div{background:var(--v23-paper);padding:10px 11px}.v23-score .overall{background:var(--v23-dark);color:#fff}.v23-score .k{font:800 .33rem "Cascadia Mono",monospace;letter-spacing:.11em;color:#87958F}.v23-score .v{font-weight:720;font-size:.82rem;margin-top:4px}.v23-score .overall .v{font-size:1.18rem;color:#fff}.v23-score .bar{height:3px;background:#E5ECE9;border-radius:5px;margin-top:6px;overflow:hidden}.v23-score .bar i{display:block;height:100%;background:linear-gradient(90deg,var(--v23-teal),var(--v23-orange));border-radius:5px}.v23-thread{display:flex;gap:7px;overflow-x:auto;padding:3px 1px 8px}.v23-thread-card{min-width:170px;border:1px solid var(--v23-line);background:var(--v23-paper);border-radius:8px;padding:10px}.v23-thread-card .k{font:800 .32rem "Cascadia Mono",monospace;letter-spacing:.1em;color:#8A9792}.v23-thread-card .v{font-weight:680;font-size:.66rem;margin-top:4px}.v23-thread-card .s{font-size:.44rem;color:#7C8A85;margin-top:3px}.v23-callout{border:1px solid var(--v23-line);border-left:3px solid var(--v23-orange);background:var(--v23-paper);border-radius:7px;padding:10px 12px;margin:7px 0;font-size:.58rem;color:#5E6D68;line-height:1.5}.v23-ai-plan{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:8px 0}.v23-ai-plan>div{border:1px solid var(--v23-line);background:var(--v23-paper);border-radius:8px;padding:11px}.v23-ai-plan .n{font:800 .34rem "Cascadia Mono",monospace;color:var(--v23-orange);letter-spacing:.1em}.v23-ai-plan .t{font-weight:700;font-size:.67rem;margin-top:4px}.v23-ai-plan .s{font-size:.47rem;color:#74827D;margin-top:3px;line-height:1.4}
@media(max-width:1150px){.v23-hero{grid-template-columns:1fr}.v23-score{grid-template-columns:1fr 1fr}.v23-score .overall{grid-column:1/-1}.v23-exec-grid{grid-template-columns:1fr 1fr}.v23-exec-grid .lead{grid-column:1/-1}}@media(max-width:760px){.v23-hero-side,.v23-ai-plan,.v23-score,.v23-exec-grid{grid-template-columns:1fr}}
</style>''', unsafe_allow_html=True)


def executive_hero(base: Dict[str, Any], resilience: Dict[str, Any], confidence: Dict[str, Any]) -> None:
    bn=base.get('bottleneck','-'); sla=float(base.get('sla_pct',0)); tp=float(base.get('throughput_h',0)); ri=float(resilience.get('score',0)); mc=int(confidence.get('score',0))
    posture='CRITICAL' if sla<60 else ('WATCH' if sla<85 else 'STABLE')
    st.markdown(f'''<div class="v23-hero"><div class="v23-hero-main"><div class="v23-ey">EXECUTIVE ROOM · DECISION INTELLIGENCE</div><h2>A operação em uma frase: { _e(posture) }</h2><p>O Anti-Murphy consolida estado operacional, restrição, risco e decisões testadas em uma leitura executiva. A simulação continua sendo a fonte quantitativa; esta sala organiza evidência para decisão.</p></div><div class="v23-hero-side"><div class="v23-stat"><div class="k">THROUGHPUT</div><div class="v">{tp:.2f} un/h</div><div class="s">cenário-base</div></div><div class="v23-stat"><div class="k">SLA</div><div class="v">{sla:.0f}%</div><div class="s">nível de serviço</div></div><div class="v23-stat"><div class="k">RESILIENCE</div><div class="v">{ri:.0f}/100</div><div class="s">índice interno</div></div><div class="v23-stat"><div class="k">MODEL READY</div><div class="v">{mc}/100</div><div class="s">completude do cadastro</div></div></div></div>''',unsafe_allow_html=True)


def executive_snapshot(base: Dict[str, Any], value: Dict[str, Any], history_count: int) -> None:
    st.markdown(f'''<div class="v23-exec-grid"><div class="lead"><div class="k">CURRENT CONSTRAINT</div><div class="v">{_e(base.get('bottleneck','-'))}</div><div class="s">restrição identificada no cenário-base</div></div><div><div class="k">LATE ORDERS</div><div class="v">{int(value.get('late_orders',0))}/{int(value.get('total_orders',0))}</div><div class="s">{float(value.get('late_share',0)):.0f}% da carteira</div></div><div><div class="k">PENALTY EXPOSURE</div><div class="v">R$ {float(value.get('base_penalties',0)):,.0f}</div><div class="s">no lote simulado</div></div><div><div class="k">DECISION EVIDENCE</div><div class="v">{history_count} cenário(s)</div><div class="s">histórico comparável desta sessão</div></div></div>''',unsafe_allow_html=True)


def decision_scorecard_ui(score: Dict[str, Any]) -> None:
    def c(k,v):
        return f'<div><div class="k">{k}</div><div class="v">{float(v):.0f}/100</div><div class="bar"><i style="width:{max(0,min(100,float(v))):.0f}%"></i></div></div>'
    st.markdown(f'''<div class="v23-score"><div class="overall"><div class="k">DECISION QUALITY</div><div class="v">{float(score.get('overall',0)):.0f}/100</div><div style="font-size:.44rem;color:#A4B3AE;margin-top:3px">{_e(score.get('band','-'))}</div></div>{c('FLOW',score.get('flow',0))}{c('SERVICE',score.get('service',0))}{c('ECONOMICS',score.get('economics',0))}{c('SPEED',score.get('speed',0))}</div>''',unsafe_allow_html=True)
    st.markdown(f'<div class="v23-callout"><b>{_e(score.get("verdict",""))}</b> · score heurístico transparente; não é probabilidade de sucesso.</div>',unsafe_allow_html=True)


def decision_thread(history: List[Dict[str, Any]]) -> None:
    if not history:
        st.markdown('<div class="v23-callout"><b>Decision Thread vazio.</b> Rode experimentos para construir uma trilha comparável de decisões.</div>',unsafe_allow_html=True); return
    cards=[]
    for i,h in enumerate(history[-8:],1):
        cards.append(f'<div class="v23-thread-card"><div class="k">{i:02d} · {_e(h.get("source","TEST"))}</div><div class="v">{_e(h.get("name","Scenario"))}</div><div class="s">TP {float(h.get("throughput",0)):.2f} · SLA {float(h.get("sla",0)):.0f}% · BN {_e(h.get("bottleneck","-"))}</div></div>')
    st.markdown('<div class="v23-thread">'+''.join(cards)+'</div>',unsafe_allow_html=True)


def ai_action_plan(rec: Dict[str, Any] | None, base: Dict[str, Any]) -> None:
    title = rec.get('title','Investigar a restrição') if rec else f'Investigar {base.get("bottleneck","-")}'
    why = rec.get('why','Priorizar o sinal de maior pressão do cenário-base.') if rec else 'Use o gargalo e as filas como ponto de partida.'
    st.markdown(f'''<div class="v23-ai-plan"><div><div class="n">01 · DIAGNOSE</div><div class="t">Confirmar a causa</div><div class="s">{_e(why)}</div></div><div><div class="n">02 · EXPERIMENT</div><div class="t">{_e(title)}</div><div class="s">Simular antes de implementar; comparar serviço, custo, fluxo e tempo.</div></div><div><div class="n">03 · DECIDE</div><div class="t">Promover só com evidência</div><div class="s">Revisar trade-offs, confiança da simulação e custo de não agir.</div></div></div>''',unsafe_allow_html=True)


def portfolio_scatter(frontier: List[Dict[str, Any]], all_history: List[Dict[str, Any]]) -> go.Figure:
    fig=go.Figure()
    if all_history:
        fig.add_trace(go.Scatter(x=[float(x.get('unit_cost',0)) for x in all_history],y=[float(x.get('sla',0)) for x in all_history],mode='markers',name='Testados',text=[x.get('name','') for x in all_history],marker=dict(size=10,color='#AAB7B3',opacity=.45),hovertemplate='%{text}<br>Custo/un R$ %{x:.2f}<br>SLA %{y:.0f}%<extra></extra>'))
    if frontier:
        fig.add_trace(go.Scatter(x=[x['unit_cost'] for x in frontier],y=[x['sla'] for x in frontier],mode='markers+text',name='Fronteira',text=[x['name'] for x in frontier],textposition='top center',marker=dict(size=14,color='#FF681B',line=dict(width=1,color='#fff')),hovertemplate='%{text}<br>Custo/un R$ %{x:.2f}<br>SLA %{y:.0f}%<extra></extra>'))
    fig.update_layout(height=350,margin=dict(l=20,r=20,t=25,b=45),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#142227',font=dict(family='Segoe UI Variable, Aptos',color='#53625D',size=11),xaxis_title='Custo por unidade (menor é melhor)',yaxis_title='SLA (maior é melhor)',legend=dict(orientation='h',y=1.08,x=0))
    fig.update_xaxes(gridcolor='#E4EAE8'); fig.update_yaxes(gridcolor='#E4EAE8',range=[0,105])
    return fig

def pressure_strip(rows: List[Dict[str, Any]]) -> None:
    top=(rows or [])[:4]
    if not top: return
    cells=[]
    for r in top:
        s=float(r.get('score',0)); tone='#FF681B' if s>=65 else ('#B37A32' if s>=40 else '#47A89D')
        cells.append(f'''<div class="v23-stat"><div class="k">{_e(r.get('station','-'))} · PRESSURE</div><div class="v" style="color:{tone}">{s:.0f}/100</div><div class="s">fila {int(r.get('queue',0))} · espera {float(r.get('wait',0)):.0f} min · util {float(r.get('util',0)):.0f}%</div></div>''')
    st.markdown('<div class="v23-hero-side" style="grid-template-columns:repeat('+str(len(cells))+',1fr);margin:7px 0 11px">'+''.join(cells)+'</div>',unsafe_allow_html=True)
