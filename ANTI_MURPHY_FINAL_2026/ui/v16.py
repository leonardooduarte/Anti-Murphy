from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any, Dict, List

import plotly.graph_objects as go
import streamlit as st

BRAND_DIR = Path(__file__).resolve().parents[1] / "assets" / "brand"


def _e(v: Any) -> str:
    return html.escape(str(v))


def _data_uri(filename: str, mime: str = "image/png") -> str:
    raw = (BRAND_DIR / filename).read_bytes()
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def inject_v16_css() -> None:
    st.markdown(r"""
<style>
/* =====================================================================
   ANTI-MURPHY V16.3 · CONTROL ROOM DESIGN SYSTEM
   A workstation, not a dashboard. Dense, quiet, technical, deliberate.
   ===================================================================== */
:root{
  --am16-bg:#F1F3F0;
  --am16-panel:#FBFCFA;
  --am16-panel-2:#F6F8F5;
  --am16-ink:#0D181B;
  --am16-ink-2:#162428;
  --am16-rail:#0D171A;
  --am16-rail-2:#142226;
  --am16-muted:#687571;
  --am16-soft:#93A09B;
  --am16-line:#D9DFDB;
  --am16-line-2:#C8D0CB;
  --am16-orange:#FF6426;
  --am16-orange-soft:#FFF0E9;
  --am16-teal:#4DA99E;
  --am16-teal-soft:#E7F5F2;
  --am16-green:#2F7D68;
  --am16-red:#B64B43;
  --am16-amber:#B67A2D;
  --am16-r8:8px;
  --am16-r12:12px;
  --am16-r16:16px;
  --am16-shadow:0 10px 30px rgba(13,24,27,.055);
}
html,body,[class*="css"]{font-family:"Segoe UI Variable","Aptos",Inter,"Segoe UI",system-ui,sans-serif!important}
.stApp{background:var(--am16-bg)!important;color:var(--am16-ink)!important}
.block-container{max-width:1760px!important;padding:1.05rem 1.45rem 4rem 1.45rem!important}
[data-testid="stHeader"]{background:transparent!important;height:2.2rem!important}
[data-testid="stToolbar"]{opacity:.18!important;transition:.2s ease}[data-testid="stToolbar"]:hover{opacity:.85!important}

/* V16.2 PRODUCT NAVIGATION RAIL — rendered inside the canvas, not native sidebar */
section[data-testid="stSidebar"]{display:none!important}
[data-testid="collapsedControl"]{display:none!important}
.st-key-am16_navrail{
  position:sticky;top:1rem;
  background:linear-gradient(180deg,#0C1619 0%,#101D21 70%,#0B1518 100%);
  border:1px solid #213035;border-radius:14px;padding:10px 9px 12px;
  box-shadow:0 18px 45px rgba(13,24,27,.12);min-height:calc(100vh - 2rem)
}
.st-key-am16_navrail [data-testid="stVerticalBlock"]{gap:.3rem!important}
.st-key-am16_navrail .stButton>button{
  width:100%!important;min-height:39px!important;border-radius:8px!important;
  border:1px solid transparent!important;background:transparent!important;color:#8FA09B!important;
  box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;
  font-size:.74rem!important;font-weight:650!important;padding:0 10px!important;letter-spacing:.003em!important
}
.st-key-am16_navrail .stButton>button:hover{background:#17272B!important;color:#F4F7F5!important;border-color:#22363B!important;transform:none!important}
.st-key-am16_navrail .stButton>button[kind="primary"]{background:linear-gradient(90deg,#192A2E,#162529)!important;color:#F4F7F5!important;border-color:#2A3D42!important;box-shadow:inset 3px 0 0 var(--am16-orange)!important}
.st-key-am16_navrail .stButton>button[kind="primary"]:after{display:none!important}
.st-key-am16_navrail [data-testid="stExpander"]{background:#101D21!important;border:1px solid #26383D!important;border-radius:9px!important;color:#C9D2CF!important}
.st-key-am16_navrail [data-testid="stExpander"] summary{color:#AAB8B4!important;font-size:.68rem!important}
.st-key-am16_navrail hr{border-color:#24353A!important;margin:.55rem 0!important}
.am16-side-brand{padding:8px 7px 14px}.am16-side-brand img{width:176px;max-width:100%;display:block}.am16-side-brand .version{font-size:.47rem;letter-spacing:.19em;text-transform:uppercase;color:#60736E;margin:9px 0 0 3px;font-weight:800}.am16-side-sec{font-size:.47rem;letter-spacing:.19em;text-transform:uppercase;color:#566A65;font-weight:850;margin:11px 9px 4px}.am16-side-state{margin:9px 4px 4px;border:1px solid #273A3E;background:#101D21;border-radius:10px;padding:9px}.am16-side-state .k{font-size:.46rem;text-transform:uppercase;letter-spacing:.15em;color:#5F7570;font-weight:800}.am16-side-state .v{font-size:.68rem;color:#DDE6E2;margin-top:5px;font-weight:700}.am16-side-state .v i{display:inline-block;width:6px;height:6px;background:#55B79F;border-radius:50%;margin-right:7px;box-shadow:0 0 0 4px rgba(85,183,159,.08)}.am16-side-metrics{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:8px}.am16-side-metrics div{border-top:1px solid #283A3E;padding-top:6px;font-size:.49rem;color:#60736E}.am16-side-metrics b{display:block;color:#BCC9C5;font-size:.64rem;margin-top:1px}.am16-side-footer{font-size:.47rem;line-height:1.45;color:#526762;margin:13px 7px 2px}
@media(max-width:1050px){.st-key-am16_navrail{position:relative;min-height:auto}.am16-side-brand img{width:150px}}

/* TOP COMMAND BAR */
.am16-topbar{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:center;background:rgba(251,252,250,.9);backdrop-filter:blur(16px);border:1px solid var(--am16-line);border-radius:12px;padding:10px 13px 10px 16px;box-shadow:0 7px 24px rgba(13,24,27,.035);margin:0 0 12px}.am16-breadcrumb{font-size:.53rem;letter-spacing:.14em;text-transform:uppercase;color:#85928D;font-weight:780}.am16-top-title{font-size:.96rem;color:#172427;font-weight:760;margin-top:3px;letter-spacing:-.02em}.am16-top-title span{color:#8A9691;font-weight:560}.am16-top-actions{display:flex;gap:6px;align-items:center}.am16-status-chip{font-size:.58rem;border:1px solid var(--am16-line);border-radius:999px;padding:5px 9px;color:#66736F;background:#F6F8F5;white-space:nowrap}.am16-status-chip b{color:#172427}.am16-status-chip.live:before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:#42A98E;margin-right:6px;box-shadow:0 0 0 4px rgba(66,169,142,.08)}

/* PAGE INTRO - editorial, not hero-card */
.am16-pagehead{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,.42fr);gap:30px;align-items:end;margin:23px 0 17px}.am16-pagehead .ey{font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:var(--am16-orange);font-weight:850}.am16-pagehead h1{font-size:2.22rem!important;line-height:.98!important;letter-spacing:-.061em!important;font-weight:790!important;color:var(--am16-ink)!important;margin:6px 0 0!important}.am16-pagehead .copy{text-align:right;font-size:.68rem;line-height:1.5;color:#71807A;padding-bottom:2px}.am16-pagehead .copy b{color:#33423E;font-weight:700}

/* KPI COMMAND STRIP */
.am16-metric-rail{display:grid;grid-template-columns:1.08fr 1fr 1fr 1fr .95fr;gap:1px;border:1px solid var(--am16-line);background:var(--am16-line);border-radius:12px;overflow:hidden;margin:0 0 12px;box-shadow:0 6px 22px rgba(13,24,27,.025)}.am16-metric{position:relative;background:var(--am16-panel);padding:11px 13px 10px;min-height:82px}.am16-metric .lab{font-size:.47rem;letter-spacing:.16em;text-transform:uppercase;color:#86928E;font-weight:830}.am16-metric .value{font-size:1.42rem;letter-spacing:-.045em;font-weight:780;color:#152225;margin-top:7px}.am16-metric .meta{font-size:.55rem;color:#929C98;margin-top:4px}.am16-metric .delta{position:absolute;right:11px;top:10px;font-size:.52rem;font-weight:720;color:#64726D}.am16-metric.risk:before,.am16-metric.good:before{content:"";position:absolute;left:0;right:0;top:0;height:2px}.am16-metric.risk:before{background:var(--am16-orange)}.am16-metric.good:before{background:var(--am16-teal)}.am16-metric.risk .value{color:#C54D1D}.am16-metric.good .value{color:#307E75}

/* CENTRAL WORKSPACE / RIGHT CONTEXT */
.am16-workspace-label{display:flex;align-items:center;justify-content:space-between;margin:13px 0 8px}.am16-workspace-label .left{font-size:.56rem;letter-spacing:.15em;text-transform:uppercase;color:#77847F;font-weight:820}.am16-workspace-label .right{font-size:.56rem;color:#98A29E}.am16-workspace-label .pulse{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--am16-teal);box-shadow:0 0 0 5px rgba(77,169,158,.08);margin-right:7px}
.am16-context{background:linear-gradient(180deg,#111E22,#0F1B1E);border:1px solid #25383D;border-radius:14px;padding:14px;color:#E9EFEC;min-height:100%;box-shadow:0 15px 35px rgba(13,24,27,.1)}.am16-context .ey{font-size:.48rem;letter-spacing:.17em;text-transform:uppercase;color:#6D817C;font-weight:850}.am16-context .headline{font-size:1.18rem;line-height:1.14;letter-spacing:-.035em;font-weight:740;margin:8px 0 12px}.am16-context .headline span{color:#FF7A42}.am16-context-row{padding:10px 0;border-top:1px solid #26383C}.am16-context-row .k{font-size:.47rem;text-transform:uppercase;letter-spacing:.13em;color:#647873;font-weight:780}.am16-context-row .v{font-size:.78rem;color:#DCE5E1;font-weight:680;margin-top:4px}.am16-context-row p{font-size:.57rem!important;line-height:1.45!important;color:#81938E!important;margin:4px 0 0!important}.am16-rec{margin-top:10px;border:1px solid #3A4140;background:linear-gradient(135deg,rgba(255,100,38,.10),rgba(255,100,38,.025));border-radius:10px;padding:10px}.am16-rec .k{color:#FF8552}.am16-rec .v{font-size:.77rem;color:white;margin-top:4px;font-weight:720}.am16-rec p{font-size:.56rem!important;color:#9AA9A4!important;margin:4px 0 0!important}.am16-confidence{display:flex;align-items:center;gap:8px;margin-top:11px;padding-top:10px;border-top:1px solid #26383C}.am16-confidence .ring{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--am16-teal) var(--p),#26373B 0);position:relative}.am16-confidence .ring:after{content:"";position:absolute;inset:5px;border-radius:50%;background:#111E22}.am16-confidence .ring b{position:relative;z-index:1;font-size:.62rem}.am16-confidence .txt{font-size:.54rem;color:#7C8F89;line-height:1.4}.am16-confidence .txt b{display:block;color:#DDE6E2;font-size:.64rem}

/* SIGNAL CARDS */
.am16-signals{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0 15px}.am16-signal{background:var(--am16-panel);border:1px solid var(--am16-line);border-radius:11px;padding:12px 13px;min-height:98px}.am16-signal .ey{font-size:.47rem;text-transform:uppercase;letter-spacing:.16em;color:#8B9692;font-weight:820}.am16-signal b{display:block;font-size:.84rem;color:#1B292C;margin-top:7px;letter-spacing:-.018em}.am16-signal p{font-size:.58rem!important;line-height:1.48!important;color:#7F8B87!important;margin:5px 0 0!important}.am16-signal.risk{border-left:3px solid var(--am16-orange)}.am16-signal.good{border-left:3px solid var(--am16-teal)}

/* CAUSAL CHAIN */
.am16-causal{background:#111D20;border:1px solid #26383C;border-radius:14px;padding:14px 16px;margin:10px 0;color:#ECF1EF;overflow:hidden}.am16-causal .head{display:flex;justify-content:space-between;align-items:center}.am16-causal .ey{font-size:.48rem;letter-spacing:.17em;text-transform:uppercase;color:#FF8250;font-weight:840}.am16-causal .note{font-size:.51rem;color:#657A74}.am16-chain{display:grid;grid-template-columns:repeat(5,1fr);gap:22px;margin-top:17px;position:relative}.am16-chain:before{content:"";position:absolute;top:29px;left:7%;right:7%;height:1px;background:linear-gradient(90deg,#FF6426,#BF774F,#647C75,#4DA99E)}.am16-node{position:relative;z-index:1;text-align:center}.am16-node .dot{width:58px;height:58px;margin:auto;border-radius:50%;display:grid;place-items:center;background:#132327;border:1px solid #3B4B4F;box-shadow:0 0 0 6px #111D20;color:white;font-weight:780;font-size:.72rem}.am16-node.hot .dot{border-color:#FF6426;box-shadow:0 0 0 6px #111D20,0 0 24px rgba(255,100,38,.18)}.am16-node.good .dot{border-color:#4DA99E}.am16-node .k{font-size:.47rem;letter-spacing:.1em;text-transform:uppercase;color:#738681;margin-top:9px}.am16-node .v{font-size:.58rem;color:#C9D5D1;margin-top:3px;line-height:1.3}

/* BEFORE / AFTER REVIEW */
.am16-review-grid{display:grid;grid-template-columns:1fr 46px 1fr;gap:8px;align-items:stretch;margin:8px 0 10px}.am16-review-card{background:var(--am16-panel);border:1px solid var(--am16-line);border-radius:12px;padding:14px}.am16-review-card.after{border-color:#A8CEC7;background:linear-gradient(180deg,#FBFCFA,#F4FAF8)}.am16-review-card .ey{font-size:.48rem;letter-spacing:.15em;text-transform:uppercase;color:#88938F;font-weight:820}.am16-review-card h3{font-size:.94rem!important;margin:6px 0 11px!important}.am16-review-metrics{display:grid;grid-template-columns:1fr 1fr;gap:8px}.am16-review-metrics div{border-top:1px solid #E2E6E3;padding-top:7px}.am16-review-metrics span{display:block;font-size:.47rem;letter-spacing:.08em;text-transform:uppercase;color:#929D99}.am16-review-metrics b{display:block;font-size:.88rem;margin-top:2px;color:#1A282B}.am16-review-arrow{display:grid;place-items:center;color:#899591;font-size:1.35rem}.am16-delta-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:8px 0 12px}.am16-delta{border:1px solid var(--am16-line);background:var(--am16-panel);border-radius:10px;padding:10px 11px}.am16-delta .k{font-size:.46rem;letter-spacing:.13em;text-transform:uppercase;color:#89948F}.am16-delta .v{font-size:1.02rem;font-weight:760;letter-spacing:-.03em;margin-top:5px}.am16-delta.pos .v{color:#2F7D68}.am16-delta.neg .v{color:#B64B43}.am16-delta.neutral .v{color:#6C7773}

/* FORM / COMPONENT RE-SKIN */
.stButton>button,.stDownloadButton>button{font-family:inherit!important;transition:.16s ease!important}
main .stButton>button,main .stDownloadButton>button{min-height:39px!important;border-radius:8px!important;border:1px solid var(--am16-line-2)!important;background:#FAFBF9!important;color:#52605C!important;font-size:.71rem!important;font-weight:650!important;box-shadow:none!important}
main .stButton>button:hover,main .stDownloadButton>button:hover{border-color:#AAB5B0!important;background:white!important;color:#162326!important;transform:translateY(-1px)!important;box-shadow:0 7px 18px rgba(13,24,27,.05)!important}
main .stButton>button[kind="primary"]{background:#122126!important;border-color:#122126!important;color:#F4F7F5!important;box-shadow:0 8px 20px rgba(13,24,27,.10)!important}
main .stButton>button[kind="primary"]:after{display:none!important}
main .stButton>button[kind="primary"]:hover{background:#1A2C31!important;border-color:#1A2C31!important}
[data-testid="stExpander"]{background:var(--am16-panel)!important;border:1px solid var(--am16-line)!important;border-radius:10px!important;box-shadow:none!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid var(--am16-line)!important;border-radius:10px!important;overflow:hidden!important;background:white!important;box-shadow:none!important}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{border-radius:8px!important;background:#FAFBF9!important;border-color:#D3DAD6!important;min-height:40px!important}
[data-testid="stFileUploader"]{background:#FAFBF9!important;border:1px dashed #BEC8C3!important;border-radius:10px!important}
[data-testid="stAlert"]{border-radius:9px!important;border-width:1px!important}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:18px!important;background:transparent!important;border-bottom:1px solid var(--am16-line)!important;padding:0!important;border-radius:0!important}
[data-testid="stTabs"] [data-baseweb="tab"]{height:39px!important;padding:0 2px!important;border-radius:0!important;color:#7D8984!important;font-weight:660!important;font-size:.68rem!important;flex:0 0 auto!important}
[data-testid="stTabs"] [aria-selected="true"]{background:transparent!important;color:#152225!important;box-shadow:inset 0 -2px 0 var(--am16-orange)!important}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{display:none!important}
div[data-testid="stMetric"]{background:var(--am16-panel)!important;border:1px solid var(--am16-line)!important;padding:10px 12px!important;border-radius:9px!important;box-shadow:none!important}div[data-testid="stMetric"] label{font-size:.59rem!important;color:#7B8883!important}div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-size:1.18rem!important;letter-spacing:-.035em!important;color:#182629!important}
[data-testid="stVerticalBlock"]{gap:.50rem!important}[data-testid="stHorizontalBlock"]{gap:.55rem!important}.element-container{margin-bottom:.03rem!important}
h1,h2,h3,h4{color:#142124!important}h3{font-size:1.05rem!important;letter-spacing:-.03em!important;margin:1.05rem 0 .40rem!important}p{color:#687571!important}

/* Override legacy V15 masthead/navigation if accidentally rendered */
.am15-masthead,.am15-nav-caption{display:none!important}.am15-pagebar{display:none!important}.am15-module-hero{border-radius:10px!important;box-shadow:none!important;background:#F8FAF7!important;border-color:var(--am16-line)!important;padding:14px 16px!important}.am15-module-hero:after{display:none!important}.am15-module-hero h2{font-size:1.08rem!important;letter-spacing:-.03em!important}.am15-module-hero p{font-size:.65rem!important;max-width:920px!important}.am15-station{border-radius:10px!important;box-shadow:none!important;background:#FBFCFA!important}.am15-deck-card{border-radius:10px!important;box-shadow:none!important}.am15-verdict{border-radius:10px!important}.am15-compare-story{display:none!important}

/* Dark simulation blocks visually nest into V16 */
.am-cinematic,.am-replay-shell,.am-opportunity-scan,.am-prop-shell,.am-copilot-shell{border-radius:13px!important;box-shadow:none!important}

@media(max-width:1100px){section[data-testid="stSidebar"]{min-width:230px!important;max-width:230px!important}.am16-pagehead{grid-template-columns:1fr}.am16-pagehead .copy{text-align:left}.am16-metric-rail{grid-template-columns:1fr 1fr}.am16-signals{grid-template-columns:1fr}.am16-chain{grid-template-columns:1fr 1fr}.am16-chain:before{display:none}.am16-review-grid{grid-template-columns:1fr}.am16-review-arrow{transform:rotate(90deg)}.am16-delta-grid{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.block-container{padding:.75rem .72rem 3rem!important}.am16-topbar{grid-template-columns:1fr}.am16-top-actions{flex-wrap:wrap}.am16-pagehead h1{font-size:1.78rem!important}.am16-metric-rail,.am16-delta-grid{grid-template-columns:1fr}.am16-chain{grid-template-columns:1fr}.am16-review-metrics{grid-template-columns:1fr}}
</style>
""", unsafe_allow_html=True)


def sidebar_brand() -> None:
    logo = _data_uri("logo-dark.png")
    st.markdown(f'<div class="am16-side-brand"><img src="{logo}" alt="ANTI-MURPHY"><div class="version">V29.1 · War Room</div></div>', unsafe_allow_html=True)


def sidebar_state(status: str, stations: int, workers: int, orders: int) -> None:
    st.markdown(
        f'''<div class="am16-side-state"><div class="k">Estado do modelo</div><div class="v"><i></i>{_e(status)}</div>
        <div class="am16-side-metrics"><div>postos<b>{stations}</b></div><div>operadores<b>{workers}</b></div><div>ordens<b>{orders}</b></div><div>workspace<b>local</b></div></div></div>''',
        unsafe_allow_html=True,
    )


def topbar(section: str, page: str, status: str, model_name: str = "Factory Model · Base") -> None:
    st.markdown(
        f'''<div class="am16-topbar"><div><div class="am16-breadcrumb">ANTI-MURPHY / {_e(section.upper())}</div><div class="am16-top-title">{_e(page)} <span>· {_e(model_name)}</span></div></div>
        <div class="am16-top-actions"><span class="am16-status-chip live"><b>{_e(status)}</b></span><span class="am16-status-chip">V29.1 · WR</span></div></div>''',
        unsafe_allow_html=True,
    )


def page_head(code: str, title: str, copy: str, context: str = "") -> None:
    st.markdown(
        f'''<div class="am16-pagehead"><div><div class="ey">{_e(code)}</div><h1>{_e(title)}</h1></div><div class="copy">{_e(copy)}{('<br><b>'+_e(context)+'</b>') if context else ''}</div></div>''',
        unsafe_allow_html=True,
    )


def metric_rail(base: Dict[str, Any], resilience: Dict[str, Any], exposure: float, alt: Dict[str, Any] | None = None) -> None:
    def d_pct(new: float, old: float) -> str:
        if abs(old) < 1e-9: return "—"
        return f"{((new-old)/old)*100:+.1f}%"
    def d_pp(new: float, old: float) -> str:
        return f"{new-old:+.1f} p.p."
    a = alt or base
    sla=float(a.get("sla_pct",0)); score=float(resilience.get("score",0))
    entries=[
        ("Throughput",f"{a.get('throughput_h',0):.2f} un/h",f"{a.get('total_units',0)} unidades", d_pct(float(a.get('throughput_h',0)),float(base.get('throughput_h',0))) if alt else "fluxo", "good" if alt and a.get('throughput_h',0)>base.get('throughput_h',0) else ""),
        ("SLA",f"{sla:.0f}%",f"{a.get('late_orders',0)} OPs atrasadas", d_pp(sla,float(base.get('sla_pct',0))) if alt else "prazo", "good" if sla>=80 else "risk"),
        ("Makespan",f"{a.get('makespan_h',0):.1f} h","tempo até a última OP", d_pct(float(a.get('makespan_h',0)),float(base.get('makespan_h',0))) if alt else "tempo", ""),
        ("Custo / un.",f"R$ {a.get('unit_cost',0):.2f}","custo operacional", d_pct(float(a.get('unit_cost',0)),float(base.get('unit_cost',0))) if alt else "economia", ""),
        ("Resiliência",f"{score:.0f}/100",str(resilience.get('band','')), f"exposição {exposure:.0f}", "good" if score>=70 else "risk"),
    ]
    blocks=[]
    for lab,val,meta,delta,klass in entries:
        blocks.append(f'<div class="am16-metric {klass}"><div class="lab">{_e(lab)}</div><div class="value">{_e(val)}</div><div class="meta">{_e(meta)}</div><div class="delta">{_e(delta)}</div></div>')
    st.markdown('<div class="am16-metric-rail">'+''.join(blocks)+'</div>',unsafe_allow_html=True)


def workspace_label(label: str, note: str = "telemetria derivada da simulação") -> None:
    st.markdown(f'<div class="am16-workspace-label"><div class="left">{_e(label)}</div><div class="right"><span class="pulse"></span>{_e(note)}</div></div>',unsafe_allow_html=True)


def intelligence_panel(base: Dict[str, Any], resilience: Dict[str, Any], recommendations: List[Dict[str, Any]], alerts: List[Dict[str, Any]], confidence: int = 82) -> None:
    bn=str(base.get("bottleneck","-")); row=next((r for r in base.get("stations",[]) if str(r.get("Posto"))==bn),{})
    rec=recommendations[0] if recommendations else {}
    title=rec.get("title") or rec.get("action") or f"Testar capacidade em {bn}"
    why=rec.get("why") or rec.get("reason") or "Use um experimento controlado para validar a alavanca antes da implementação."
    alert=alerts[0] if alerts else None
    alert_txt=alert.get("detail") if alert else "Nenhum alerta dominante além da restrição atual."
    st.markdown(f'''<aside class="am16-context"><div class="ey">Decision intelligence</div><div class="headline">A operação pede atenção em <span>{_e(bn)}</span>.</div>
    <div class="am16-context-row"><div class="k">Restrição dominante</div><div class="v">{_e(row.get('Nome',bn))}</div><p>Fila {int(row.get('Fila máx.',0))} · espera {float(row.get('Espera média (min)',0)):.1f} min · utilização {float(row.get('Utilização máquina (%)',0)):.1f}%.</p></div>
    <div class="am16-context-row"><div class="k">Sinal prioritário</div><div class="v">{_e(alert.get('title') if alert else 'Pressão sistêmica')}</div><p>{_e(alert_txt)}</p></div>
    <div class="am16-rec"><div class="k">Próximo experimento sugerido</div><div class="v">{_e(title)}</div><p>{_e(why)}</p></div>
    <div class="am16-confidence"><div class="ring" style="--p:{max(0,min(100,confidence))}%"><b>{confidence}%</b></div><div class="txt"><b>Confiança heurística</b>Consistência dos sinais do modelo; não é probabilidade do mundo real.</div></div></aside>''',unsafe_allow_html=True)


def signal_strip(base: Dict[str, Any], resilience: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> None:
    bn=str(base.get("bottleneck","-")); score=float(resilience.get("score",0)); rec=recommendations[0] if recommendations else {}
    penalty=float(base.get("penalty_total",0)); late=int(base.get("late_orders",0))
    rec_title=rec.get("title") or "Rodar experimento focalizado"
    html_s=f'''<div class="am16-signals">
      <div class="am16-signal risk"><div class="ey">Risk signal</div><b>{_e(bn)} concentra a pressão</b><p>{late} OP(s) atrasadas e R$ {penalty:,.2f} de penalidade no lote simulado.</p></div>
      <div class="am16-signal {'good' if score>=70 else 'risk'}"><div class="ey">Resilience</div><b>{score:.0f}/100 · {_e(resilience.get('band',''))}</b><p>Use Stress Lab e Rupture Finder para descobrir a fronteira segura do modelo.</p></div>
      <div class="am16-signal good"><div class="ey">Next move</div><b>{_e(rec_title)}</b><p>Transforme o diagnóstico em um cenário comparável antes de comprometer recurso real.</p></div>
    </div>'''
    st.markdown(html_s,unsafe_allow_html=True)


def causal_chain(base: Dict[str, Any], alt: Dict[str, Any] | None = None, explanation: Dict[str, Any] | None = None) -> None:
    src=alt or base
    bn=str(src.get("bottleneck","-")); row=next((r for r in src.get("stations",[]) if str(r.get("Posto"))==bn),{})
    queue=int(row.get("Fila máx.",0)); wait=float(row.get("Espera média (min)",0)); sla=float(src.get("sla_pct",0)); cost=float(src.get("unit_cost",0))
    nodes=[
        (bn,"Restrição", "hot"),
        (str(queue),"Fila máx.", "hot" if queue>10 else ""),
        (f"{wait:.0f}m","Espera média", ""),
        (f"{sla:.0f}%","SLA", "good" if sla>=80 else "hot"),
        (f"R${cost:.0f}","Custo / un.", "good" if alt and alt.get('unit_cost',0)<base.get('unit_cost',0) else ""),
    ]
    blocks=''.join(f'<div class="am16-node {klass}"><div class="dot">{_e(val)}</div><div class="k">{_e(lbl)}</div><div class="v">{_e("causa" if i==0 else "efeito sistêmico")}</div></div>' for i,(val,lbl,klass) in enumerate(nodes))
    note=(explanation or {}).get("headline","Leitura causal construída a partir das métricas do cenário.")
    st.markdown(f'<div class="am16-causal"><div class="head"><div class="ey">Causal trace</div><div class="note">{_e(note)}</div></div><div class="am16-chain">{blocks}</div></div>',unsafe_allow_html=True)


def review_cards(base: Dict[str, Any], alt: Dict[str, Any], delta: Dict[str, Any]) -> None:
    def card(cls:str,ey:str,name:str,x:Dict[str,Any])->str:
        return f'''<div class="am16-review-card {cls}"><div class="ey">{_e(ey)}</div><h3>{_e(name)}</h3><div class="am16-review-metrics">
          <div><span>Throughput</span><b>{float(x.get('throughput_h',0)):.2f} un/h</b></div><div><span>SLA</span><b>{float(x.get('sla_pct',0)):.0f}%</b></div>
          <div><span>Custo / un.</span><b>R$ {float(x.get('unit_cost',0)):.2f}</b></div><div><span>Makespan</span><b>{float(x.get('makespan_h',0)):.1f} h</b></div></div></div>'''
    st.markdown('<div class="am16-review-grid">'+card("before","Baseline","Cenário-base",base)+'<div class="am16-review-arrow">→</div>'+card("after","Decision world",alt.get("name","Cenário"),alt)+'</div>',unsafe_allow_html=True)
    vals=[("Throughput",float(delta.get("throughput_pct",0)),"%",True),("SLA",float(delta.get("sla_pp",0))," p.p.",True),("Custo / un.",float(delta.get("unit_cost_pct",0)),"%",False),("Makespan",float(delta.get("makespan_pct",0)),"%",False)]
    parts=[]
    for lab,v,suf,higher_better in vals:
        good=(v>0 if higher_better else v<0); neutral=abs(v)<.05
        klass="neutral" if neutral else ("pos" if good else "neg")
        parts.append(f'<div class="am16-delta {klass}"><div class="k">Δ {_e(lab)}</div><div class="v">{v:+.1f}{suf}</div></div>')
    st.markdown('<div class="am16-delta-grid">'+''.join(parts)+'</div>',unsafe_allow_html=True)


def decision_confidence(base: Dict[str, Any], alt: Dict[str, Any], history_count: int = 0) -> Dict[str, Any]:
    # Transparent heuristic: rewards measurable separation, repeatable evidence/history and a clear bottleneck response.
    tp = abs((float(alt.get("throughput_h",0))-float(base.get("throughput_h",0))) / max(float(base.get("throughput_h",0)),.01) * 100)
    sla = abs(float(alt.get("sla_pct",0))-float(base.get("sla_pct",0)))
    cost = abs((float(alt.get("unit_cost",0))-float(base.get("unit_cost",0))) / max(float(base.get("unit_cost",0)),.01) * 100)
    separation=min(35, tp*1.2 + sla*.55 + cost*.35)
    evidence=min(25, 10 + history_count*3)
    migration=12 if base.get("bottleneck") != alt.get("bottleneck") else 6
    score=int(max(25,min(92,28+separation+evidence+migration)))
    band="ALTA" if score>=78 else ("MÉDIA" if score>=58 else "EXPLORATÓRIA")
    return {"score":score,"band":band,"note":"Heurística transparente baseada em separação de resultados, evidência acumulada e resposta do gargalo."}


def confidence_card(info: Dict[str, Any]) -> None:
    score=int(info.get("score",0))
    st.markdown(f'''<div class="am16-signal good"><div class="ey">Decision confidence</div><b>{score}% · {_e(info.get('band',''))}</b><p>{_e(info.get('note',''))}</p></div>''',unsafe_allow_html=True)


def scenario_canvas(target: str, station_name: str, workers: int, machines: int, demand: float, rule: str, event: str, absent: int) -> None:
    changes=[]
    if workers: changes.append(f"{workers:+d} operador(es)")
    if machines: changes.append(f"{machines:+d} máquina(s)")
    if abs(demand-1)>1e-9: changes.append(f"demanda {demand:.1f}×")
    if rule!="EDD": changes.append(f"despacho {rule}")
    if event.lower() not in {"sem perturbação","nenhuma","none"}: changes.append(event)
    if absent: changes.append(f"{absent} ausência(s)")
    body=' · '.join(changes) if changes else "Nenhuma intervenção configurada"
    mode="READY TO SIMULATE" if changes else "NEUTRAL SCENARIO"
    st.markdown(f'''<div class="am16-context"><div class="ey">Scenario canvas</div><div class="headline"><span>{_e(target)}</span> · {_e(station_name)}</div>
      <div class="am16-context-row"><div class="k">Intervenções</div><div class="v">{_e(body)}</div><p>O cenário-base permanece intacto; apenas a cópia contrafactual é alterada.</p></div>
      <div class="am16-context-row"><div class="k">Dispatch rule</div><div class="v">{_e(rule)}</div><p>Demanda {_e(f'{demand:.1f}×')} · ponto-alvo {_e(target)}.</p></div>
      <div class="am16-rec"><div class="k">{_e(mode)}</div><div class="v">{'Execute o mundo alternativo.' if changes else 'Configure ao menos uma mudança.'}</div><p>O motor recalculará filas, gargalo, prazo, custo e eventos.</p></div></div>''',unsafe_allow_html=True)


def opportunity_leaderboard(opps: List[Dict[str, Any]], limit: int = 3) -> None:
    if not opps: return
    top=sorted(opps,key=lambda x:float(x.get("Score de oportunidade",0)),reverse=True)[:limit]
    parts=[]
    for i,x in enumerate(top,1):
        parts.append(f'''<div class="am16-signal {'good' if i==1 else ''}"><div class="ey">Opportunity {i:02d}</div><b>{_e(x.get('Ação','Alternativa'))}</b><p>Score {float(x.get('Score de oportunidade',0)):.1f} · Δ throughput {float(x.get('Throughput Δ (%)',0)):+.1f}% · Δ SLA {float(x.get('SLA Δ (p.p.)',0)):+.1f} p.p.</p></div>''')
    st.markdown('<div class="am16-signals">'+''.join(parts)+'</div>',unsafe_allow_html=True)


def stress_summary_panel(summary: Dict[str, Any]) -> None:
    st.markdown(f'''<div class="am16-signals">
      <div class="am16-signal {'good' if float(summary.get('resilience_rate',0))>=80 else 'risk'}"><div class="ey">Survival rate</div><b>{float(summary.get('resilience_rate',0)):.0f}% dos futuros</b><p>Cenários que mantiveram SLA ≥ 80%.</p></div>
      <div class="am16-signal risk"><div class="ey">Weakest link</div><b>{_e(summary.get('most_fragile','-'))}</b><p>Posto mais sensível à bateria de perturbações.</p></div>
      <div class="am16-signal"><div class="ey">Tail risk</div><b>P90 {float(summary.get('makespan_p90',0)):.1f} h</b><p>Cauda superior do tempo de conclusão sob estresse.</p></div>
    </div>''',unsafe_allow_html=True)


def goal_route_strip(rows: List[Dict[str, Any]], target_tp: float, target_sla: float) -> None:
    if not rows: return
    top=rows[:3]
    parts=[]
    for i,r in enumerate(top,1):
        hit=str(r.get("Atinge meta",""))=="Sim"
        parts.append(f'''<div class="am16-signal {'good' if hit else ''}"><div class="ey">Route {i:02d} · {'target hit' if hit else 'closest path'}</div><b>{_e(r.get('Cenário','Rota'))}</b><p>{float(r.get('Throughput',0)):.2f} un/h · SLA {float(r.get('SLA',0)):.0f}% · implantação R$ {float(r.get('Investimento estimado',0)):,.0f}</p></div>''')
    st.markdown('<div class="am16-signals">'+''.join(parts)+'</div>',unsafe_allow_html=True)


def scenario_delta_chart(base: Dict[str, Any], alt: Dict[str, Any]):
    vals=[
        ("Throughput", (float(alt.get('throughput_h',0))/max(float(base.get('throughput_h',0)),.01)-1)*100, True),
        ("SLA", float(alt.get('sla_pct',0))-float(base.get('sla_pct',0)), True),
        ("Custo/un", (float(alt.get('unit_cost',0))/max(float(base.get('unit_cost',0)),.01)-1)*100, False),
        ("Makespan", (float(alt.get('makespan_h',0))/max(float(base.get('makespan_h',0)),.01)-1)*100, False),
    ]
    y=[x[0] for x in vals]; raw=[x[1] for x in vals]
    quality=[v if hb else -v for (_,v,hb) in vals]
    labels=[f"{v:+.1f}{' p.p.' if name=='SLA' else '%'}" for name,v,_ in vals]
    colors=["#4DA99E" if q>0.05 else ("#B64B43" if q<-0.05 else "#A2ADA8") for q in quality]
    fig=go.Figure(go.Bar(x=quality,y=y,orientation='h',marker_color=colors,text=labels,textposition='outside',cliponaxis=False,customdata=raw,hovertemplate="<b>%{y}</b><br>impacto direcional %{x:+.1f}<br>delta bruto %{customdata:+.1f}<extra></extra>"))
    fig.add_vline(x=0,line_width=1,line_color="#AAB5B0")
    fig.update_layout(height=285,margin=dict(l=12,r=56,t=15,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(title="Impacto na direção desejável →",gridcolor="#E3E7E4",zeroline=False),yaxis=dict(autorange="reversed"),showlegend=False,font=dict(family="Segoe UI, sans-serif",color="#64726D",size=11))
    return fig


def recovery_cards(rows: List[Dict[str, Any]]) -> None:
    if not rows: return
    parts=[]
    for i,r in enumerate(rows[:3],1):
        parts.append(f'<div class="am16-signal {"good" if i==1 else ""}"><div class="ey">Recovery option {i:02d}</div><b>{_e(r.get("Ação","Resposta"))}</b><p>SLA {float(r.get("SLA",0)):.0f}% ({float(r.get("SLA Δ (p.p.)",0)):+.1f} p.p.) · TP {float(r.get("Throughput Δ (%)",0)):+.1f}% · score {float(r.get("Recovery score",0)):.1f}</p></div>')
    st.markdown('<div class="am16-signals">'+''.join(parts)+'</div>',unsafe_allow_html=True)


def model_quality_strip(stations: Dict[str, Dict[str, Any]], orders: List[Dict[str, Any]]) -> None:
    nst=max(1,len(stations)); nord=max(1,len(orders))
    complete_cost=sum(1 for x in stations.values() if float(x.get("custo_maquina_h",0))>0 and float(x.get("custo_operador_h",0))>=0)
    complete_av=sum(1 for x in stations.values() if .5 <= float(x.get("disponibilidade",0)) <= 1)
    valid_routes=sum(1 for o in orders if o.get("route"))
    score=round(100*(.35*complete_cost/nst + .30*complete_av/nst + .35*valid_routes/nord))
    band="READY" if score>=90 else ("REVIEW" if score>=70 else "INCOMPLETE")
    st.markdown(f'<div class="am16-signals"><div class="am16-signal good"><div class="ey">Model readiness</div><b>{score}% · {band}</b><p>Completude estrutural para executar cenários comparáveis.</p></div><div class="am16-signal"><div class="ey">Structure</div><b>{len(stations)} postos · {sum(int(x.get("maquinas",0)) for x in stations.values())} máquinas</b><p>{sum(int(x.get("operadores",0)) for x in stations.values())} operadores configurados.</p></div><div class="am16-signal"><div class="ey">Demand model</div><b>{len(orders)} ordens ativas</b><p>{valid_routes}/{len(orders) if orders else 0} roteiros completos e prontos para simulação.</p></div></div>',unsafe_allow_html=True)
