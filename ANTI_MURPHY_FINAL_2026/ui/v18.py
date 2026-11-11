from __future__ import annotations
import html
from typing import Any, Dict, List
from ui.stat_values import stat_value
import streamlit as st


def _e(v: Any) -> str:
    return html.escape(str(v))


def inject_v18_css() -> None:
    st.markdown(r'''
<style>
/* ============================================================
   ANTI-MURPHY V18 · OPERATIONAL INTELLIGENCE
   Premium system pass: calmer canvas, stronger type, denser hierarchy.
   ============================================================ */
:root{
  --am18-canvas:#F6F7F5;
  --am18-paper:#FFFFFF;
  --am18-paper-2:#F1F4F2;
  --am18-ink:#0A1518;
  --am18-ink-2:#18272B;
  --am18-muted:#6D7A76;
  --am18-muted-2:#94A09C;
  --am18-line:#DCE2DE;
  --am18-line-strong:#CBD4CF;
  --am18-night:#071316;
  --am18-night-2:#102126;
  --am18-orange:#FF6633;
  --am18-orange-deep:#D94D1B;
  --am18-teal:#2F9288;
  --am18-teal-bright:#52B5A8;
  --am18-green:#25745F;
  --am18-red:#B84A42;
  --am18-r:8px;
}
html,body,[class*="css"]{
  font-family:"Segoe UI Variable Text","Aptos","Segoe UI",system-ui,sans-serif!important;
  font-optical-sizing:auto;font-variant-numeric:tabular-nums lining-nums;
}
h1,h2,h3,h4,.am16-pagehead h1,.am16-top-title,.am16-context .headline,
.v17-command .main,.v17-inspector h3,.v17-verdict .title{
  font-family:"Segoe UI Variable Display","Aptos Display","Segoe UI Variable Text","Aptos","Segoe UI",system-ui,sans-serif!important;
}
.stApp{
  background:
    radial-gradient(900px 420px at 94% -8%,rgba(255,102,51,.045),transparent 56%),
    radial-gradient(760px 420px at 27% -12%,rgba(47,146,136,.032),transparent 60%),
    linear-gradient(180deg,#F8F9F7 0%,var(--am18-canvas) 42%,#F3F5F3 100%)!important;
  color:var(--am18-ink)!important;
}
.block-container{max-width:1880px!important;padding:.72rem 1.15rem 3.5rem!important}
[data-testid="stHeader"]{height:1.55rem!important;background:transparent!important}
[data-testid="stToolbar"]{opacity:.12!important}
/* navigation becomes a real product rail */
.st-key-am16_navrail{
  top:.72rem!important;min-height:calc(100vh - 1.44rem)!important;
  border-radius:10px!important;padding:8px 7px 10px!important;
  background:linear-gradient(180deg,#071216 0%,#0A181C 52%,#081519 100%)!important;
  border:1px solid #1C3035!important;
  box-shadow:0 26px 60px rgba(5,17,20,.14)!important;
}
.am16-side-brand{padding:7px 8px 12px!important}.am16-side-brand img{width:158px!important}.am16-side-brand .version{font-size:.44rem!important;letter-spacing:.2em!important;color:#5E7670!important;margin-top:8px!important}
.am16-side-state{background:#0C1C20!important;border-color:#21363A!important;border-radius:8px!important;padding:9px!important}
.am16-side-state .k,.am16-side-sec{font-size:.43rem!important;letter-spacing:.18em!important}
.am16-side-sec{margin:12px 9px 3px!important;color:#4E6862!important}
.am16-side-state .v{font-size:.66rem!important}.am16-side-metrics div{font-size:.45rem!important}.am16-side-metrics b{font-size:.61rem!important}
.st-key-am16_navrail .stButton>button{min-height:37px!important;border-radius:6px!important;font-size:.70rem!important;font-weight:610!important;color:#82958F!important;padding:0 9px!important}
.st-key-am16_navrail .stButton>button:hover{background:#12272C!important;color:#F2F6F4!important;border-color:#203A3F!important}
.st-key-am16_navrail .stButton>button[kind="primary"]{background:#13272C!important;color:#F7FAF8!important;border-color:#284047!important;box-shadow:inset 2px 0 0 var(--am18-orange)!important}
.st-key-am16_navrail [data-testid="stExpander"]{border-radius:7px!important;background:#0D1C20!important;border-color:#20353A!important}
.am16-side-footer{font-size:.43rem!important;color:#405D56!important}
/* top command bar */
.am16-topbar{margin-bottom:8px!important;border-radius:8px!important;padding:8px 11px 8px 13px!important;background:rgba(255,255,255,.86)!important;border-color:var(--am18-line)!important;box-shadow:0 5px 20px rgba(10,21,24,.025)!important;backdrop-filter:blur(18px) saturate(120%)!important}
.am16-breadcrumb{font-size:.45rem!important;color:#899690!important;letter-spacing:.17em!important}.am16-top-title{font-size:.88rem!important;font-weight:690!important}.am16-status-chip{font-size:.50rem!important;padding:4px 8px!important;background:#F8FAF8!important}
/* page title */
.am16-pagehead{margin:17px 0 12px!important;grid-template-columns:minmax(0,1fr) minmax(260px,.34fr)!important;gap:24px!important}
.am16-pagehead .ey{font-size:.46rem!important;letter-spacing:.19em!important}.am16-pagehead h1{font-size:2.05rem!important;line-height:1!important;letter-spacing:-.052em!important;font-weight:710!important}.am16-pagehead .copy{font-size:.61rem!important;color:#75817D!important;line-height:1.45!important}
/* surfaces */
.am16-metric-rail,.v17-command,.v17-verdict,.v17-inspector,.am15-module-hero,.v17-model-card,.v17-quality>div,.v17-q{border-color:var(--am18-line)!important;background:var(--am18-paper)!important;box-shadow:none!important}
.am16-metric-rail{border-radius:7px!important;margin-bottom:9px!important}.am16-metric{min-height:70px!important;padding:9px 11px!important}.am16-metric .lab{font-size:.43rem!important}.am16-metric .value{font-size:1.26rem!important;font-weight:710!important}.am16-metric .meta,.am16-metric .delta{font-size:.50rem!important}
.am16-context{border-radius:9px!important;background:linear-gradient(180deg,#0D1C20,#0A171A)!important;border-color:#22363B!important;box-shadow:0 18px 45px rgba(6,18,21,.09)!important;padding:13px!important}
.am16-context .headline{font-size:1.08rem!important;font-weight:680!important}.am16-context-row{padding:9px 0!important}.am16-rec{border-radius:7px!important}.am16-confidence .ring{width:38px!important;height:38px!important}
.am16-signals{gap:6px!important}.am16-signal{border-radius:7px!important;background:#FFF!important;border-color:var(--am18-line)!important;padding:9px 11px!important}.am16-signal b{font-size:.68rem!important}.am16-signal p{font-size:.50rem!important}
/* dark theatre becomes flatter, more product-like */
.am-cinematic,.am-replay-shell,.am-opportunity-scan,.am-prop-shell,.am-copilot-shell{border-radius:9px!important;box-shadow:0 18px 38px rgba(8,20,23,.07)!important}
/* typography + controls */
h3{font-size:.93rem!important;font-weight:680!important;letter-spacing:-.02em!important;margin:1rem 0 .36rem!important}
p{line-height:1.46!important}
label,[data-testid="stWidgetLabel"] p{font-size:.62rem!important;color:#65736E!important;font-weight:590!important}
main .stButton>button,main .stDownloadButton>button{border-radius:6px!important;min-height:36px!important;font-size:.66rem!important;font-weight:620!important}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input,[data-testid="stFileUploaderDropzone"]{border-radius:6px!important;background:#FFF!important;border-color:var(--am18-line)!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border-radius:7px!important;border:1px solid var(--am18-line)!important;overflow:hidden}
[data-testid="stExpander"]{border-radius:7px!important;border-color:var(--am18-line)!important;background:rgba(255,255,255,.58)!important}
[data-testid="stTabs"] [data-baseweb="tab"]{font-size:.64rem!important;height:36px!important}
div[data-testid="stMetric"]{border-radius:7px!important;background:#FFF!important;border-color:var(--am18-line)!important}
/* Plotly: visually embedded */
[data-testid="stPlotlyChart"]{background:#FFF!important;border:1px solid var(--am18-line)!important;border-radius:8px!important;padding:3px!important}
/* V18 executive pulse */
.v18-pulse{display:grid;grid-template-columns:1.28fr .82fr .82fr .92fr;gap:1px;background:var(--am18-line);border:1px solid var(--am18-line);border-radius:7px;overflow:hidden;margin:0 0 9px}
.v18-pulse>div{background:#FFF;padding:10px 12px;min-height:63px;position:relative}.v18-pulse>div:first-child:before{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;background:var(--am18-orange)}
.v18-pulse .ey{font-size:.41rem;letter-spacing:.17em;text-transform:uppercase;color:#929E99;font-weight:820}.v18-pulse .big{font-family:"Segoe UI Variable Display","Aptos Display","Segoe UI",sans-serif;font-size:.88rem;font-weight:680;color:#142226;margin-top:5px;letter-spacing:-.022em}.v18-pulse .big em{font-style:normal;color:var(--am18-orange-deep)}.v18-pulse .sub{font-size:.49rem;color:#899590;margin-top:3px;line-height:1.38}
/* V18 risk economics band */
.v18-econ{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:7px 0 11px}.v18-econ>div{background:#FFF;border:1px solid var(--am18-line);border-radius:7px;padding:9px 10px}.v18-econ .k{font-size:.40rem;text-transform:uppercase;letter-spacing:.15em;color:#929E99;font-weight:820}.v18-econ .v{font-size:.82rem;color:#172629;font-weight:700;margin-top:4px}.v18-econ .m{font-size:.49rem;color:#8A9691;margin-top:2px}.v18-econ .risk .v{color:var(--am18-orange-deep)}.v18-econ .good .v{color:var(--am18-green)}
/* model flow canvas */
.v18-flow{display:flex;align-items:stretch;gap:0;margin:8px 0 12px;overflow-x:auto;padding-bottom:2px}.v18-node{min-width:172px;flex:1;background:#FFF;border:1px solid var(--am18-line);border-radius:7px;padding:10px 11px;position:relative}.v18-node.hot{border-color:#E7A58B;box-shadow:inset 0 2px 0 var(--am18-orange)}.v18-node .id{font-size:.41rem;letter-spacing:.16em;text-transform:uppercase;color:var(--am18-orange);font-weight:850}.v18-node .name{font-size:.70rem;font-weight:680;color:#152427;margin-top:4px}.v18-node .stats{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px}.v18-node .stats span{font-size:.46rem;color:#8D9994}.v18-node .stats b{display:block;font-size:.61rem;color:#34443F;margin-top:1px}.v18-arrow{display:grid;place-items:center;width:26px;min-width:26px;color:#9EAAA5;font-size:.9rem}
/* decision lens */
.v18-lens{display:grid;grid-template-columns:1.15fr repeat(4,.72fr);gap:1px;background:var(--am18-line);border:1px solid var(--am18-line);border-radius:7px;overflow:hidden;margin:8px 0 12px}.v18-lens>div{background:#FFF;padding:10px 11px}.v18-lens .lead{background:#0D1B1F;color:#EDF3F0}.v18-lens .ey{font-size:.40rem;letter-spacing:.15em;text-transform:uppercase;color:#8B9893;font-weight:820}.v18-lens .lead .ey{color:#71847E}.v18-lens .score{font-size:1.55rem;font-weight:720;letter-spacing:-.05em;margin-top:4px}.v18-lens .lead .score span{font-size:.57rem;color:#82938D}.v18-lens .v{font-size:.82rem;font-weight:700;color:#19282B;margin-top:5px}.v18-lens .m{font-size:.47rem;color:#8B9792;margin-top:2px}.v18-lens .good .v{color:var(--am18-green)}.v18-lens .bad .v{color:var(--am18-red)}
/* opportunity quadrants cleaner */
.v17-quadrants{gap:6px!important}.v17-q{border-radius:7px!important;padding:8px 10px!important}.v17-q b{font-size:.58rem!important}.v17-q span{font-size:.47rem!important}
/* section chrome */
.v17-section-note{margin:13px 0 7px!important;padding-bottom:6px!important;border-color:var(--am18-line)!important}.v17-section-note b{font-size:.72rem!important}.v17-section-note span{font-size:.49rem!important}
.v17-inspector{border-radius:7px!important;padding:11px 12px!important}.v17-inspector-grid{border-radius:5px!important}.v17-verdict{border-radius:7px!important;padding:11px 12px!important}.v17-model-cards{display:none!important} /* replaced by richer V18 flow canvas */
/* strong whitespace discipline */
[data-testid="stVerticalBlock"]{gap:.40rem!important}[data-testid="stHorizontalBlock"]{gap:.45rem!important}.element-container{margin-bottom:0!important}
@media(max-width:1280px){.v18-pulse{grid-template-columns:1fr 1fr}.v18-econ{grid-template-columns:1fr 1fr}.v18-lens{grid-template-columns:1fr 1fr 1fr}.v18-lens .lead{grid-column:1/-1}}
@media(max-width:900px){.v18-pulse,.v18-econ,.v18-lens{grid-template-columns:1fr}.v18-flow{flex-direction:column}.v18-arrow{width:100%;height:20px}.am16-pagehead{grid-template-columns:1fr!important}.am16-pagehead .copy{text-align:left!important}}
</style>
''', unsafe_allow_html=True)


def executive_pulse(base: Dict[str, Any], resilience: Dict[str, Any], recs: List[Dict[str, Any]]) -> None:
    bn=str(base.get('bottleneck','—'))
    late=int(base.get('late_orders',0)); total=max(1,len(base.get('orders',[])))
    penalty=float(base.get('penalty_total',0)); score=float(resilience.get('score',0))
    rec=(recs[0].get('title') if recs else None) or f'Testar capacidade em {bn}'
    status='CRÍTICO' if score<45 else ('ATENÇÃO' if score<70 else 'CONTROLADO')
    st.markdown(f'''<div class="v18-pulse">
      <div><div class="ey">Operational state</div><div class="big">Restrição ativa em <em>{_e(bn)}</em></div><div class="sub">O sistema concentra a leitura no ponto que limita o fluxo agora.</div></div>
      <div><div class="ey">Service exposure</div><div class="big">{late}/{total} OPs atrasadas</div><div class="sub">R$ {penalty:,.2f} de penalidade no lote simulado.</div></div>
      <div><div class="ey">Resilience posture</div><div class="big">{score:.0f}/100 · {status}</div><div class="sub">Robustez combinada de prazo, fila, pressão e recuperação.</div></div>
      <div><div class="ey">Next experiment</div><div class="big">{_e(rec)}</div><div class="sub">Próximo teste explicável antes de comprometer recurso real.</div></div>
    </div>''', unsafe_allow_html=True)


def economics_strip(base: Dict[str, Any]) -> None:
    orders=base.get('orders',[])
    total=max(1,len(orders)); late=int(base.get('late_orders',0)); late_share=late/total*100
    penalty=float(base.get('penalty_total',0)); cost=float(base.get('total_cost',0)); unit=float(base.get('unit_cost',0))
    worst=max((float(o.get('Multa (R$)',0)) for o in orders), default=0.0)
    st.markdown(f'''<div class="v18-econ">
      <div class="risk"><div class="k">Cost of delay</div><div class="v">R$ {penalty:,.2f}</div><div class="m">penalidade acumulada no lote simulado</div></div>
      <div class="risk"><div class="k">Late-order ratio</div><div class="v">{late_share:.0f}%</div><div class="m">{late} de {total} ordens fora do prazo</div></div>
      <div><div class="k">Total scenario cost</div><div class="v">R$ {cost:,.2f}</div><div class="m">custo operacional + penalidades</div></div>
      <div><div class="k">Largest order penalty</div><div class="v">R$ {worst:,.2f}</div><div class="m">maior exposição individual observada</div></div>
    </div>''', unsafe_allow_html=True)


def model_flow(stations: Dict[str, Dict[str, Any]], bottleneck: str|None=None) -> None:
    pieces=[]; items=list(stations.items())
    for i,(sid,s) in enumerate(items):
        avail=float(s.get('disponibilidade',1))*100; eff=float(s.get('eficiencia_operador',1))*100
        cls=' hot' if sid==bottleneck else ''
        pieces.append(f'''<div class="v18-node{cls}"><div class="id">{_e(sid)}</div><div class="name">{_e(s.get('nome',sid))}</div><div class="stats"><span>capacidade<b>{int(s.get('maquinas',0))} maq.</b></span><span>mão de obra<b>{int(s.get('operadores',0))} op.</b></span><span>disponibilidade<b>{avail:.0f}%</b></span><span>eficiência<b>{eff:.0f}%</b></span></div></div>''')
        if i<len(items)-1: pieces.append('<div class="v18-arrow">→</div>')
    st.markdown('<div class="v18-flow">'+''.join(pieces)+'</div>',unsafe_allow_html=True)


def decision_lens(base: Dict[str, Any], alt: Dict[str, Any], delta: Dict[str, Any]) -> None:
    tp=float(delta.get('throughput_pct',0)); sla=float(delta.get('sla_pp',0)); cost=float(delta.get('unit_cost_pct',0)); mk=float(delta.get('makespan_pct',0))
    # Transparent descriptive score. Positive = more flow/service and less cost/time.
    flow=max(0,min(100,50+tp*3.0))
    service=max(0,min(100,50+sla*1.2))
    economics=max(0,min(100,50-cost*2.2))
    speed=max(0,min(100,50-mk*1.25))
    total=max(0,min(100,.28*flow+.28*service+.22*economics+.22*speed))
    def cls(v): return 'good' if v>=55 else ('bad' if v<45 else '')
    st.markdown(f'''<div class="v18-lens">
      <div class="lead"><div class="ey">Decision quality lens</div><div class="score">{total:.0f}<span>/100</span></div><div class="m">heurística transparente de equilíbrio entre fluxo, serviço, economia e tempo</div></div>
      <div class="{cls(flow)}"><div class="ey">Flow</div><div class="v">{flow:.0f}/100</div><div class="m">throughput {tp:+.1f}%</div></div>
      <div class="{cls(service)}"><div class="ey">Service</div><div class="v">{service:.0f}/100</div><div class="m">SLA {sla:+.1f} p.p.</div></div>
      <div class="{cls(economics)}"><div class="ey">Economics</div><div class="v">{economics:.0f}/100</div><div class="m">custo/un {cost:+.1f}%</div></div>
      <div class="{cls(speed)}"><div class="ey">Speed</div><div class="v">{speed:.0f}/100</div><div class="m">makespan {mk:+.1f}%</div></div>
    </div>''',unsafe_allow_html=True)


def resilience_callout(summary: Dict[str, Any]) -> None:
    score=float(summary.get('resilience_pct',summary.get('score',0)))
    fragile=summary.get('fragile_station',summary.get('most_fragile','—'))
    p90=summary.get('makespan_p90',summary.get('p90_makespan',0))
    st.markdown(f'''<div class="v18-pulse">
      <div><div class="ey">Resilience verdict</div><div class="big">{score:.0f}% dos futuros preservam o critério</div><div class="sub">A leitura agrega a bateria de cenários, não um único caso extremo.</div></div>
      <div><div class="ey">Weakest link</div><div class="big"><em>{_e(fragile)}</em></div><div class="sub">posto com maior sensibilidade no conjunto perturbado</div></div>
      <div><div class="ey">Tail completion</div><div class="big">P90 {stat_value(p90,1,' h')}</div><div class="sub">cauda superior do tempo de conclusão</div></div>
      <div><div class="ey">Interpretation</div><div class="big">Teste a fronteira, não a média</div><div class="sub">Use Rupture Lab para localizar o primeiro ponto de falha.</div></div>
    </div>''',unsafe_allow_html=True)
