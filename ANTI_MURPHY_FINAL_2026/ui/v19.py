from __future__ import annotations
import streamlit as st


def inject_v19_css() -> None:
    st.markdown(r'''
<style>
/* ============================================================
   ANTI-MURPHY V19 · PRODUCT POLISH
   Industrial editorial system: colder canvas, stronger hierarchy,
   technical display type, compact spacing, richer interaction.
   ============================================================ */
:root{
  --am19-canvas:#EEF2F0;
  --am19-canvas-2:#E8EEEB;
  --am19-paper:#FCFDFC;
  --am19-paper-2:#F5F8F6;
  --am19-ink:#0C171A;
  --am19-ink-2:#192A2E;
  --am19-muted:#6B7B76;
  --am19-soft:#93A09B;
  --am19-line:#D7E0DC;
  --am19-line-2:#C6D2CD;
  --am19-night:#071316;
  --am19-night-2:#0C1D21;
  --am19-orange:#FF642E;
  --am19-orange-dark:#D64F20;
  --am19-teal:#318F87;
  --am19-teal-2:#54B4A8;
  --am19-green:#24735D;
  --am19-red:#B84A42;
  --am19-shadow:0 10px 30px rgba(10,22,25,.055);
}
html,body,[class*="css"]{
  font-family:"Segoe UI Variable Text","Segoe UI",system-ui,sans-serif!important;
  font-feature-settings:"tnum" 1,"ss01" 1;
  font-variant-numeric:tabular-nums;
}
h1,h2,h3,h4,.am16-pagehead h1,.am16-top-title,.am16-context .headline,
.v17-command .main,.v17-inspector h3,.v17-verdict .title,.v18-pulse .big,
.am16-metric .value,.v18-econ .v,.v18-lens .score,.v18-lens .v{
  font-family:"Bahnschrift SemiBold","Bahnschrift","Segoe UI Variable Display","Segoe UI",sans-serif!important;
  font-stretch:semi-condensed;
}
.stApp{
  background:
    linear-gradient(rgba(35,77,69,.022) 1px,transparent 1px),
    linear-gradient(90deg,rgba(35,77,69,.022) 1px,transparent 1px),
    radial-gradient(900px 520px at 86% -8%,rgba(255,100,46,.055),transparent 55%),
    radial-gradient(760px 500px at 24% -10%,rgba(49,143,135,.045),transparent 58%),
    linear-gradient(180deg,#F4F7F5 0%,var(--am19-canvas) 48%,#EAF0ED 100%)!important;
  background-size:48px 48px,48px 48px,auto,auto,auto!important;
  color:var(--am19-ink)!important;
}
.block-container{max-width:1920px!important;padding:.65rem 1rem 3rem!important}
[data-testid="stHeader"]{height:1.25rem!important;background:transparent!important}
[data-testid="stToolbar"]{opacity:.08!important}

/* NAV RAIL */
.st-key-am16_navrail{
  top:.6rem!important;min-height:calc(100vh - 1.2rem)!important;
  border-radius:12px!important;padding:8px 8px 11px!important;
  background:linear-gradient(180deg,#061115 0%,#0A191D 54%,#08161A 100%)!important;
  border:1px solid #183038!important;
  box-shadow:0 24px 60px rgba(5,16,20,.16)!important;
  position:sticky!important;
}
.am16-side-brand{padding:6px 8px 12px!important;border-bottom:1px solid rgba(255,255,255,.055)!important}
.am16-side-brand img{width:148px!important;filter:brightness(1.04)}
.am16-side-brand .version{font-size:.42rem!important;letter-spacing:.22em!important;color:#668079!important;margin-top:8px!important}
.am16-side-state{background:linear-gradient(180deg,#0D1F24,#0A191D)!important;border:1px solid #203A40!important;border-radius:9px!important;padding:10px!important;margin-top:9px!important}
.am16-side-state .k,.am16-side-sec{font-size:.41rem!important;letter-spacing:.20em!important;text-transform:uppercase!important;color:#55716A!important;font-weight:800!important}
.am16-side-sec{margin:13px 9px 4px!important}
.am16-side-state .v{font-size:.64rem!important;color:#ECF4F1!important}.am16-side-metrics div{font-size:.43rem!important;color:#718B84!important}.am16-side-metrics b{font-size:.59rem!important;color:#E6EFEC!important}
.st-key-am16_navrail .stButton>button{min-height:36px!important;border-radius:6px!important;font-size:.68rem!important;font-weight:600!important;color:#839791!important;padding:0 10px!important;transition:all .18s ease!important;border:1px solid transparent!important;background:transparent!important}
.st-key-am16_navrail .stButton>button:hover{background:#10262B!important;color:#F3F8F6!important;border-color:#1E3A40!important;transform:translateX(2px)!important}
.st-key-am16_navrail .stButton>button[kind="primary"]{background:linear-gradient(90deg,#142D33,#10252A)!important;color:#F8FBFA!important;border-color:#27454B!important;box-shadow:inset 2px 0 0 var(--am19-orange)!important}
.st-key-am16_navrail [data-testid="stExpander"]{border-radius:7px!important;background:#0C1B1F!important;border-color:#1D343A!important}
.am16-side-footer{font-size:.40rem!important;color:#3E5D56!important;line-height:1.45!important}

/* TOPBAR + PAGE TITLE */
.am16-topbar{margin-bottom:7px!important;border-radius:9px!important;padding:7px 11px 7px 13px!important;background:rgba(252,253,252,.90)!important;border:1px solid var(--am19-line)!important;box-shadow:0 6px 22px rgba(10,22,25,.025)!important;backdrop-filter:blur(16px) saturate(130%)!important}
.am16-breadcrumb{font-size:.42rem!important;color:#899792!important;letter-spacing:.18em!important}.am16-top-title{font-size:.86rem!important;font-weight:650!important;color:#152427!important}.am16-status-chip{font-size:.48rem!important;padding:4px 8px!important;background:#F7FAF8!important;border-color:var(--am19-line)!important}
.am16-pagehead{margin:15px 0 11px!important;grid-template-columns:minmax(0,1fr) minmax(250px,.30fr)!important;gap:28px!important;position:relative!important}
.am16-pagehead:before{content:"";position:absolute;left:0;top:26px;width:26px;height:2px;background:var(--am19-orange)}
.am16-pagehead .ey{font-size:.43rem!important;letter-spacing:.21em!important;color:var(--am19-orange-dark)!important}.am16-pagehead h1{font-size:2.15rem!important;line-height:.98!important;letter-spacing:-.035em!important;font-weight:650!important;margin-top:8px!important}.am16-pagehead .copy{font-size:.60rem!important;color:#75827D!important;line-height:1.5!important}

/* CARDS + METRICS */
.am16-metric-rail,.v17-command,.v17-verdict,.v17-inspector,.am15-module-hero,.v17-model-card,.v17-quality>div,.v17-q{border-color:var(--am19-line)!important;background:rgba(252,253,252,.94)!important;box-shadow:none!important}
.am16-metric-rail{border-radius:8px!important;margin-bottom:8px!important;overflow:hidden!important}
.am16-metric{min-height:67px!important;padding:9px 12px!important;position:relative!important}
.am16-metric:after{content:"";position:absolute;left:12px;right:12px;bottom:0;height:1px;background:linear-gradient(90deg,transparent,rgba(49,143,135,.15),transparent)}
.am16-metric .lab{font-size:.40rem!important;letter-spacing:.17em!important;color:#8C9994!important}.am16-metric .value{font-size:1.28rem!important;font-weight:650!important;letter-spacing:-.025em!important}.am16-metric .meta,.am16-metric .delta{font-size:.48rem!important;color:#8A9691!important}
.am16-context{border-radius:10px!important;background:linear-gradient(180deg,#0D1D21 0%,#09171A 100%)!important;border:1px solid #223B41!important;box-shadow:0 20px 48px rgba(6,18,21,.10)!important;padding:14px!important}
.am16-context .headline{font-size:1.10rem!important;font-weight:650!important}.am16-context-row{padding:9px 0!important}.am16-rec{border-radius:7px!important;background:rgba(255,255,255,.025)!important}.am16-confidence .ring{width:38px!important;height:38px!important}
.am16-signals{gap:7px!important}.am16-signal{border-radius:8px!important;background:#FCFDFC!important;border:1px solid var(--am19-line)!important;padding:10px 12px!important;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease!important}.am16-signal:hover{transform:translateY(-2px)!important;border-color:var(--am19-line-2)!important;box-shadow:var(--am19-shadow)!important}.am16-signal b{font-size:.68rem!important}.am16-signal p{font-size:.49rem!important;color:#82908A!important}

/* CINEMATIC SURFACES */
.am-cinematic,.am-replay-shell,.am-opportunity-scan,.am-prop-shell,.am-copilot-shell{border-radius:10px!important;box-shadow:0 20px 44px rgba(8,20,23,.08)!important;border-color:#20373D!important}
.am-station,.am16-context,.am-opportunity-scan{transition:transform .18s ease,border-color .18s ease!important}
.am-station:hover{transform:translateY(-2px)!important;border-color:#39555B!important}

/* GENERAL TYPOGRAPHY */
h3{font-size:.95rem!important;font-weight:650!important;letter-spacing:-.015em!important;margin:.95rem 0 .34rem!important;color:#152427!important}
h4{font-size:.78rem!important;font-weight:650!important}
p{line-height:1.50!important}
label,[data-testid="stWidgetLabel"] p{font-size:.61rem!important;color:#65736E!important;font-weight:560!important}
small,.stCaption,[data-testid="stCaptionContainer"]{color:#7E8C87!important}

/* CONTROLS */
main .stButton>button,main .stDownloadButton>button{border-radius:6px!important;min-height:37px!important;font-size:.66rem!important;font-weight:620!important;transition:all .16s ease!important}
main .stButton>button:hover,main .stDownloadButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 7px 18px rgba(10,22,25,.07)!important}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input,[data-testid="stFileUploaderDropzone"]{border-radius:6px!important;background:#FCFDFC!important;border-color:var(--am19-line)!important;min-height:39px!important}
[data-testid="stSelectbox"]>div>div:focus-within,[data-testid="stNumberInput"] input:focus,[data-testid="stTextInput"] input:focus{border-color:#85AAA2!important;box-shadow:0 0 0 2px rgba(49,143,135,.10)!important}
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 0 4px rgba(255,100,46,.10)!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border-radius:8px!important;border:1px solid var(--am19-line)!important;overflow:hidden!important;background:#FCFDFC!important}
[data-testid="stDataFrame"] thead,[data-testid="stDataEditor"] thead{background:#EEF3F0!important}
[data-testid="stExpander"]{border-radius:7px!important;border-color:var(--am19-line)!important;background:rgba(252,253,252,.72)!important}
[data-testid="stTabs"] [data-baseweb="tab"]{font-size:.63rem!important;height:35px!important;font-weight:600!important}
div[data-testid="stMetric"]{border-radius:7px!important;background:#FCFDFC!important;border-color:var(--am19-line)!important}

/* PLOTLY + DATA VISUALIZATION */
[data-testid="stPlotlyChart"]{background:#FCFDFC!important;border:1px solid var(--am19-line)!important;border-radius:9px!important;padding:5px!important;box-shadow:none!important}

/* EXECUTIVE PULSE */
.v18-pulse{gap:1px!important;background:var(--am19-line)!important;border:1px solid var(--am19-line)!important;border-radius:8px!important;overflow:hidden!important;margin:0 0 8px!important;box-shadow:0 5px 16px rgba(9,22,25,.025)!important}
.v18-pulse>div{background:#FCFDFC!important;padding:10px 12px!important;min-height:62px!important}.v18-pulse>div:first-child:before{width:2px!important;background:var(--am19-orange)!important}.v18-pulse .ey{font-size:.39rem!important;letter-spacing:.18em!important;color:#8B9893!important}.v18-pulse .big{font-size:.88rem!important;font-weight:650!important;color:#142326!important}.v18-pulse .big em{color:var(--am19-orange-dark)!important}.v18-pulse .sub{font-size:.47rem!important;color:#899590!important}

/* ECONOMICS BAND */
.v18-econ{gap:7px!important;margin:7px 0 10px!important}.v18-econ>div{background:#FCFDFC!important;border:1px solid var(--am19-line)!important;border-radius:8px!important;padding:9px 11px!important;transition:all .18s ease!important}.v18-econ>div:hover{transform:translateY(-2px)!important;box-shadow:var(--am19-shadow)!important}.v18-econ .k{font-size:.38rem!important;letter-spacing:.16em!important;color:#909D98!important}.v18-econ .v{font-size:.82rem!important;font-weight:650!important}.v18-econ .m{font-size:.47rem!important;color:#899590!important}

/* MODEL FLOW */
.v18-flow{gap:0!important;margin:8px 0 11px!important}.v18-node{min-width:170px!important;background:#FCFDFC!important;border:1px solid var(--am19-line)!important;border-radius:8px!important;padding:10px 11px!important;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease!important}.v18-node:hover{transform:translateY(-3px)!important;border-color:#B8C7C1!important;box-shadow:var(--am19-shadow)!important}.v18-node.hot{border-color:#E09B80!important;box-shadow:inset 0 2px 0 var(--am19-orange)!important}.v18-node .id{font-size:.39rem!important;letter-spacing:.17em!important}.v18-node .name{font-size:.68rem!important;font-weight:650!important}.v18-node .stats span{font-size:.44rem!important}.v18-node .stats b{font-size:.59rem!important}.v18-arrow{color:#92A09B!important}

/* DECISION LENS */
.v18-lens{border-radius:8px!important;background:var(--am19-line)!important;border:1px solid var(--am19-line)!important;overflow:hidden!important}.v18-lens>div{background:#FCFDFC!important;position:relative!important}.v18-lens>div:not(.lead):after{content:"";position:absolute;left:10px;right:10px;bottom:8px;height:2px;background:#E7EDE9}.v18-lens>div.good:after{background:linear-gradient(90deg,var(--am19-teal),#9ED4CB)}.v18-lens>div.bad:after{background:linear-gradient(90deg,var(--am19-red),#E3A8A2)}

/* SURFACE DENSITY / EMPTY SPACE */
.am15-module-hero{border-radius:8px!important;padding:14px 15px!important}
.am-empty{border-radius:9px!important;border-color:var(--am19-line)!important;background:#FCFDFC!important}
.insight{border-radius:7px!important;background:#FCFDFC!important;border-color:var(--am19-line)!important}
hr{border-color:var(--am19-line)!important}

/* RESPONSIVE */
@media(max-width:1180px){
  .am16-pagehead{grid-template-columns:1fr!important}.v18-pulse{grid-template-columns:1fr 1fr!important}.v18-econ{grid-template-columns:1fr 1fr!important}
}
</style>
''', unsafe_allow_html=True)
