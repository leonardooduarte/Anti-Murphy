from __future__ import annotations
from html import escape as _e
from typing import Any, Dict, List
import streamlit as st


def inject_v20_css() -> None:
    st.markdown(r'''
<style>
/* ============================================================
   ANTI-MURPHY V20 · INDUSTRIAL DECISION PLATFORM
   Premium workstation: flatter canvas, sharper hierarchy,
   fewer boxes, quieter background, stronger type discipline.
   ============================================================ */
:root{
  --am20-canvas:#F3F5F3;
  --am20-paper:#FFFFFF;
  --am20-paper-2:#F8FAF8;
  --am20-ink:#0A1518;
  --am20-ink-2:#1A292C;
  --am20-muted:#6E7B77;
  --am20-soft:#98A39F;
  --am20-line:#D9E0DD;
  --am20-line-2:#C9D3CF;
  --am20-night:#071316;
  --am20-night-2:#0C1C20;
  --am20-orange:#FF5E24;
  --am20-orange-2:#D94D1B;
  --am20-teal:#2E9B91;
  --am20-teal-2:#5BC0B4;
  --am20-green:#24745D;
  --am20-red:#B84942;
  --am20-shadow:0 18px 46px rgba(11,23,26,.06);
}
html,body,[class*="css"]{
  font-family:"Segoe UI Variable Text","Segoe UI","Aptos",system-ui,sans-serif!important;
  font-feature-settings:"tnum" 1,"ss01" 1;
  font-variant-numeric:tabular-nums;
}
h1,h2,.am16-pagehead h1,.am16-top-title,.am16-context .headline,
.v20-display,.am16-metric .value,.v18-econ .v,.v18-lens .score,.v18-lens .v{
  font-family:"Segoe UI Variable Display","Aptos Display","Segoe UI",sans-serif!important;
  letter-spacing:-.032em!important;
  font-weight:680!important;
}
.v20-micro,.am16-side-sec,.am16-breadcrumb,.am16-metric .lab,.v18-econ .k,.v18-lens .ey,
.am16-side-state .k,.am16-pagehead .ey,.workspace-label{
  font-family:"Cascadia Mono","SFMono-Regular",Consolas,monospace!important;
  letter-spacing:.13em!important;
}
.stApp{
  background:
    radial-gradient(1100px 560px at 98% -10%,rgba(255,94,36,.038),transparent 58%),
    radial-gradient(760px 460px at 18% -8%,rgba(46,155,145,.032),transparent 60%),
    linear-gradient(180deg,#F7F8F7 0%,var(--am20-canvas) 52%,#EFF2F0 100%)!important;
  color:var(--am20-ink)!important;
}
/* kill the old visible grid: industrial, not blueprint wallpaper */
.stApp:before{display:none!important}
.block-container{max-width:1880px!important;padding:.55rem .85rem 3rem!important}
[data-testid="stHeader"]{height:1rem!important;background:transparent!important}
[data-testid="stToolbar"]{opacity:.04!important}

/* shell */
.st-key-am16_navrail{
  top:.48rem!important;min-height:calc(100vh - .96rem)!important;
  border-radius:10px!important;padding:8px 7px 10px!important;
  background:linear-gradient(180deg,#061216 0%,#091A1E 56%,#071519 100%)!important;
  border:1px solid #173036!important;box-shadow:0 24px 60px rgba(4,15,19,.15)!important;
}
.am16-side-brand{padding:5px 7px 10px!important}
.am16-side-brand img{width:142px!important}
.am16-side-brand .version{font-size:.40rem!important;color:#57716B!important;letter-spacing:.19em!important}
.am16-side-state{border-radius:7px!important;padding:9px!important;background:#0B1C20!important;border-color:#1A343A!important}
.am16-side-sec{font-size:.38rem!important;color:#527069!important;margin:11px 8px 3px!important}
.st-key-am16_navrail .stButton>button{min-height:34px!important;border-radius:5px!important;font-size:.67rem!important;font-weight:590!important;padding:0 9px!important;color:#82958F!important}
.st-key-am16_navrail .stButton>button:hover{background:#10252A!important;color:#F6FAF8!important;transform:translateX(1px)!important}
.st-key-am16_navrail .stButton>button[kind="primary"]{background:#122B30!important;color:#F8FBFA!important;border-color:#29474D!important;box-shadow:inset 2px 0 0 var(--am20-orange)!important}
.st-key-am16_navrail [data-testid="stExpander"]{border-radius:6px!important;background:#0B1B1F!important}

.am16-topbar{margin-bottom:5px!important;border-radius:8px!important;padding:6px 10px 6px 12px!important;background:rgba(255,255,255,.88)!important;border:1px solid var(--am20-line)!important;box-shadow:0 5px 16px rgba(10,22,25,.02)!important;backdrop-filter:blur(14px)!important}
.am16-top-title{font-size:.84rem!important}.am16-breadcrumb{font-size:.38rem!important}
.am16-pagehead{margin:12px 0 8px!important;grid-template-columns:minmax(0,1fr) minmax(230px,.28fr)!important;gap:24px!important}
.am16-pagehead:before{width:23px!important;height:2px!important;top:24px!important;background:var(--am20-orange)!important}
.am16-pagehead h1{font-size:2.02rem!important;line-height:1!important;margin-top:7px!important}
.am16-pagehead .ey{font-size:.38rem!important;color:var(--am20-orange-2)!important}
.am16-pagehead .copy{font-size:.60rem!important;color:#6E7B77!important}

/* workflow ribbon */
.v20-workflow{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--am20-line);border-radius:7px;overflow:hidden;background:#fff;margin:4px 0 10px}
.v20-stage{padding:8px 10px;position:relative;border-right:1px solid var(--am20-line);min-height:48px}
.v20-stage:last-child{border-right:0}.v20-stage.active{background:linear-gradient(180deg,#FBFDFC,#F2F7F5)}
.v20-stage.active:before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:var(--am20-orange)}
.v20-stage .n{font-family:"Cascadia Mono",monospace;font-size:.38rem;letter-spacing:.12em;color:#96A19D;text-transform:uppercase;font-weight:800}
.v20-stage .t{font-size:.68rem;color:#1A292C;font-weight:690;margin-top:3px}.v20-stage .s{font-size:.47rem;color:#84918C;margin-top:1px}

/* stronger surfaces, fewer boxes */
.am16-metric-rail,.v17-command,.v17-verdict,.v17-inspector,.am15-module-hero,.v17-quality>div,.v17-q,
.v20-station-editor,.v20-state-banner,.v20-opportunity-detail,.v20-target-warning{border-color:var(--am20-line)!important;background:#fff!important;box-shadow:none!important}
.am16-metric-rail{border-radius:7px!important}.am16-metric{min-height:62px!important;padding:8px 11px!important}
.am16-metric .lab{font-size:.36rem!important;color:#8A9691!important}.am16-metric .value{font-size:1.23rem!important}.am16-metric .meta,.am16-metric .delta{font-size:.46rem!important}
.am16-context{border-radius:9px!important;box-shadow:0 18px 44px rgba(5,18,21,.085)!important}
.am16-signal{border-radius:7px!important;padding:9px 11px!important}.am16-signal:hover{transform:translateY(-1px)!important}
.am-cinematic,.am-replay-shell,.am-opportunity-scan,.am-prop-shell,.am-copilot-shell{border-radius:9px!important;box-shadow:0 18px 44px rgba(7,19,22,.075)!important}

/* page typography */
h3{font-size:.92rem!important;font-weight:690!important;letter-spacing:-.015em!important;margin:.82rem 0 .30rem!important}
h4{font-size:.76rem!important}p{line-height:1.52!important}
label,[data-testid="stWidgetLabel"] p{font-size:.61rem!important;color:#596964!important;font-weight:570!important}
small,.stCaption,[data-testid="stCaptionContainer"]{color:#798681!important}

/* controls */
main .stButton>button,main .stDownloadButton>button{border-radius:5px!important;min-height:37px!important;font-size:.65rem!important;font-weight:630!important}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input,[data-testid="stFileUploaderDropzone"]{border-radius:5px!important;background:#fff!important;border-color:var(--am20-line)!important;min-height:39px!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border-radius:6px!important;border-color:var(--am20-line)!important;background:#fff!important}
[data-testid="stExpander"]{border-radius:6px!important;border-color:var(--am20-line)!important;background:rgba(255,255,255,.78)!important}

/* model studio */
.v20-station-editor{border:1px solid var(--am20-line);border-radius:8px;padding:11px 12px;margin:7px 0 10px}
.v20-station-editor .head{display:flex;align-items:center;justify-content:space-between;padding-bottom:8px;border-bottom:1px solid #E8ECEA}
.v20-station-editor .head b{font-size:.82rem}.v20-station-editor .head span{font-family:"Cascadia Mono",monospace;font-size:.40rem;color:var(--am20-orange-2);letter-spacing:.13em}

/* scenario freshness */
.v20-state-banner{border:1px solid var(--am20-line);border-left:3px solid var(--am20-orange);border-radius:6px;padding:10px 12px;margin:8px 0}
.v20-state-banner .k{font-family:"Cascadia Mono",monospace;font-size:.39rem;letter-spacing:.13em;color:var(--am20-orange-2);text-transform:uppercase;font-weight:800}.v20-state-banner .t{font-size:.76rem;font-weight:680;margin-top:3px}.v20-state-banner .s{font-size:.53rem;color:#71807B;margin-top:2px}

/* opportunity detail */
.v20-opportunity-detail{display:grid;grid-template-columns:1.5fr repeat(4,.7fr);gap:1px;background:var(--am20-line)!important;border:1px solid var(--am20-line);border-radius:7px;overflow:hidden;margin:7px 0 9px}
.v20-opportunity-detail>div{background:#fff;padding:9px 10px}.v20-opportunity-detail .lead{background:#0D1C20;color:#F2F6F4}.v20-opportunity-detail .k{font-family:"Cascadia Mono",monospace;font-size:.36rem;letter-spacing:.12em;text-transform:uppercase;color:#8F9B97}.v20-opportunity-detail .v{font-size:.77rem;font-weight:690;margin-top:4px}.v20-opportunity-detail .lead .v{color:#fff}.v20-opportunity-detail .good{color:var(--am20-green)}.v20-opportunity-detail .bad{color:var(--am20-red)}

/* rupture target warning */
.v20-target-warning{border:1px solid #E2D2B2;border-left:3px solid #D69A2D;background:#FFFDF7!important;border-radius:6px;padding:10px 12px;margin:6px 0 9px}.v20-target-warning b{font-size:.73rem}.v20-target-warning p{font-size:.53rem;color:#716B5E;margin:3px 0 0}

/* quality lens microbars */
.v18-lens>div{position:relative;overflow:hidden}.v18-lens>div:not(.lead):after{content:"";position:absolute;left:10px;right:10px;bottom:6px;height:2px;background:#E8EDEB}.v18-lens>div.good:before,.v18-lens>div.bad:before{content:"";position:absolute;left:10px;bottom:6px;height:2px;width:56%;z-index:2}.v18-lens>div.good:before{background:var(--am20-teal)}.v18-lens>div.bad:before{background:var(--am20-red)}

/* subtle content rhythm */
[data-testid="stVerticalBlock"]{gap:.34rem!important}[data-testid="stHorizontalBlock"]{gap:.42rem!important}
.element-container{margin-bottom:0!important}
@media(max-width:1200px){.v20-workflow{grid-template-columns:1fr 1fr}.v20-opportunity-detail{grid-template-columns:1fr 1fr}.v20-opportunity-detail .lead{grid-column:1/-1}}
@media(max-width:900px){.v20-workflow,.v20-opportunity-detail{grid-template-columns:1fr}.am16-pagehead{grid-template-columns:1fr!important}}
</style>
''', unsafe_allow_html=True)


def workflow_ribbon(active: str) -> None:
    stages = [
        ("OBSERVE", "Observe", "estado atual"),
        ("DIAGNOSE", "Diagnose", "causa e restrição"),
        ("EXPERIMENT", "Experiment", "mundo alternativo"),
        ("DECIDE", "Decide", "trade-off e ação"),
    ]
    html=[]
    for key,title,sub in stages:
        cls=' active' if key==active else ''
        html.append(f'<div class="v20-stage{cls}"><div class="n">{key}</div><div class="t">{title}</div><div class="s">{sub}</div></div>')
    st.markdown('<div class="v20-workflow">'+''.join(html)+'</div>', unsafe_allow_html=True)


def stale_scenario_notice() -> None:
    st.markdown('''<div class="v20-state-banner"><div class="k">UNSIMULATED CHANGES</div><div class="t">A configuração atual ainda não foi simulada.</div><div class="s">Os resultados anteriores foram preservados no histórico, mas não representam os controles que estão na tela agora. Execute o mundo alternativo para sincronizar análise e configuração.</div></div>''', unsafe_allow_html=True)


def opportunity_detail(opp: Dict[str, Any]) -> None:
    action=_e(str(opp.get('Ação','Oportunidade')))
    tp=float(opp.get('Throughput Δ (%)',0)); sla=float(opp.get('SLA Δ (p.p.)',0)); cost=float(opp.get('Custo/un Δ (%)',0)); mk=float(opp.get('Makespan Δ (%)',0))
    def cls(v, inverse=False):
        good = v < 0 if inverse else v > 0
        bad = v > 0 if inverse else v < 0
        return 'good' if good else ('bad' if bad else '')
    st.markdown(f'''<div class="v20-opportunity-detail">
      <div class="lead"><div class="k">SELECTED OPPORTUNITY</div><div class="v">{action}</div></div>
      <div><div class="k">Throughput</div><div class="v {cls(tp)}">{tp:+.1f}%</div></div>
      <div><div class="k">SLA</div><div class="v {cls(sla)}">{sla:+.1f} p.p.</div></div>
      <div><div class="k">Cost / unit</div><div class="v {cls(cost, True)}">{cost:+.1f}%</div></div>
      <div><div class="k">Makespan</div><div class="v {cls(mk, True)}">{mk:+.1f}%</div></div>
    </div>''', unsafe_allow_html=True)


def baseline_target_warning(current_sla: float, target_sla: float) -> None:
    st.markdown(f'''<div class="v20-target-warning"><b>O cenário-base já viola o alvo escolhido.</b><p>SLA atual: {current_sla:.0f}% · piso configurado: {target_sla:.0f}%. Nesse caso, o Rupture Lab não mede “quando quebra”; ele confirma que a operação já parte fora do limite. Use um piso ≤ SLA atual para medir deterioração ou Mission Control para buscar recuperação.</p></div>''', unsafe_allow_html=True)


def station_edit_header(sid: str, name: str) -> None:
    st.markdown(f'<div class="v20-station-editor"><div class="head"><span>VISUAL MODEL EDITOR · {_e(sid)}</span><b>{_e(name)}</b></div></div>', unsafe_allow_html=True)


def decision_economics(base: Dict[str, Any], alt: Dict[str, Any]) -> None:
    base_pen=float(base.get('penalty_total',0)); alt_pen=float(alt.get('penalty_total',0))
    base_cost=float(base.get('total_cost',0)); alt_cost=float(alt.get('total_cost',0))
    pen_delta=alt_pen-base_pen; cost_delta=alt_cost-base_cost
    verdict='reduz' if pen_delta < 0 else ('aumenta' if pen_delta > 0 else 'mantém')
    cls='good' if pen_delta < 0 else ('bad' if pen_delta > 0 else '')
    st.markdown(f'''<div class="v20-opportunity-detail">
      <div class="lead"><div class="k">COST OF DOING NOTHING</div><div class="v">Base: R$ {base_pen:,.2f} em penalidades</div></div>
      <div><div class="k">Scenario penalty</div><div class="v {cls}">R$ {alt_pen:,.2f}</div></div>
      <div><div class="k">Penalty delta</div><div class="v {cls}">R$ {pen_delta:+,.2f}</div></div>
      <div><div class="k">Total cost delta</div><div class="v {'good' if cost_delta<0 else ('bad' if cost_delta>0 else '')}">R$ {cost_delta:+,.2f}</div></div>
      <div><div class="k">Interpretation</div><div class="v">Cenário {verdict} exposição</div></div>
    </div>''', unsafe_allow_html=True)
