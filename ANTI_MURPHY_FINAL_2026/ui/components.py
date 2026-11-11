from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st

BRAND_DIR = Path(__file__).resolve().parents[1] / "assets" / "brand"


def _data_uri(filename: str, mime: str) -> str:
    data = (BRAND_DIR / filename).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def inject_css():
    st.markdown(r'''
<style>
:root{
  --bg:#ECE8DF;--paper:#F8F6F0;--paper2:#F2EEE6;--ink:#1D292D;--ink2:#263438;
  --muted:#707876;--line:#D5CEC2;--line2:#C4BCB0;--orange:#FF681B;--orange2:#C94A0A;
  --teal:#3F8E89;--green:#2B7A5A;--red:#C74B3B;--shadow:0 18px 52px rgba(29,41,45,.07);
}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
.stApp{
  color:var(--ink);
  background:
    radial-gradient(circle at 78% -8%,rgba(255,104,27,.08),transparent 30%),
    radial-gradient(circle at 12% 12%,rgba(63,142,137,.05),transparent 27%),
    linear-gradient(rgba(29,41,45,.014) 1px,transparent 1px),
    linear-gradient(90deg,rgba(29,41,45,.014) 1px,transparent 1px),
    var(--bg);
  background-size:auto,auto,52px 52px,52px 52px,auto;
  animation:ambientShift 16s ease-in-out infinite alternate;
}
@keyframes ambientShift{0%{background-position:0 0,0 0,0 0,0 0,0 0}100%{background-position:4% 0,-4% 3%,0 0,0 0,0 0}}
[data-testid="stHeader"]{height:.6rem;background:transparent!important;box-shadow:none!important;}
#MainMenu{visibility:hidden}.stDeployButton{display:none}
/* V16+ uses the native Streamlit sidebar as the product navigation rail. */
.block-container{max-width:1480px;padding:2.2rem 2.2rem 4rem!important;}
h1,h2,h3,h4{color:var(--ink)!important;letter-spacing:-.038em;font-weight:790!important;}
p,.stCaption{color:var(--muted);}

/* splash */
.am-splash{position:fixed;inset:0;z-index:99999;background:#172125;display:flex;align-items:center;justify-content:center;overflow:hidden}
.am-splash:before{content:"";position:absolute;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,rgba(255,104,27,.16),transparent 64%);animation:pulseGlow 1.7s ease-in-out infinite}
.am-splash:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent 0 48%,rgba(255,255,255,.035) 50%,transparent 52% 100%);transform:translateX(-100%);animation:scanScreen 1.4s ease-in-out 1}
.am-splash-inner{position:relative;text-align:center;animation:splashIn .7s cubic-bezier(.2,.8,.2,1) both}
.am-splash-logo{width:120px;height:120px;margin:0 auto 18px;filter:drop-shadow(0 18px 30px rgba(0,0,0,.25));animation:logoFloat 1.5s ease-in-out infinite alternate}
.am-splash-name{color:#F7F7F3;font-size:1.85rem;letter-spacing:.08em;font-weight:760}.am-splash-sub{color:#9EAAA8;font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;margin-top:7px}
.am-loadline{width:180px;height:2px;background:#314045;margin:28px auto 0;overflow:hidden;border-radius:999px}.am-loadline:after{content:"";display:block;height:100%;width:58%;background:var(--orange);animation:loadMove 1.25s ease-in-out infinite}
@keyframes splashIn{from{opacity:0;transform:translateY(14px) scale(.97)}to{opacity:1;transform:none}}
@keyframes pulseGlow{50%{transform:scale(1.08);opacity:.75}}
@keyframes logoFloat{to{transform:translateY(-5px)}}
@keyframes loadMove{0%{transform:translateX(-120%)}100%{transform:translateX(220%)}}
@keyframes scanScreen{to{transform:translateX(100%)}}

/* top bar */
.am-shell{position:relative;background:rgba(248,246,240,.82);border:1px solid rgba(197,188,176,.84);border-radius:24px;box-shadow:0 20px 60px rgba(29,41,45,.055);backdrop-filter:blur(12px);margin-bottom:12px;overflow:hidden}
.am-shell:before{content:"";position:absolute;left:-30%;top:0;width:22%;height:2px;background:linear-gradient(90deg,transparent,var(--orange),transparent);animation:shellScan 7s ease-in-out infinite}
@keyframes shellScan{0%,70%{left:-30%}100%{left:110%}}
.am-topbar{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:30px;padding:17px 20px 14px}
.am-topbar-logo{width:236px;max-width:30vw;display:block}.am-topbar-copy{padding-left:26px;border-left:1px solid var(--line2)}
.am-kicker{color:var(--orange2);font-size:.61rem;letter-spacing:.19em;text-transform:uppercase;font-weight:850}.am-sub{color:#5D6764;font-size:.83rem;line-height:1.52;margin-top:5px;max-width:650px}
.am-status{text-align:right;white-space:nowrap}.am-status .top{color:#848C89;text-transform:uppercase;letter-spacing:.15em;font-size:.56rem;font-weight:800}.am-status .value{margin-top:6px;color:var(--ink);font-size:.8rem;font-weight:760}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--green);margin-right:7px;box-shadow:0 0 0 4px rgba(43,122,90,.08);animation:statusPulse 1.7s ease-in-out infinite}
@keyframes statusPulse{50%{box-shadow:0 0 0 8px rgba(43,122,90,0)}}
.am-context{display:flex;justify-content:flex-end;gap:7px;padding:0 20px 15px}.am-chip{border:1px solid #D8D1C5;background:rgba(255,255,255,.42);border-radius:999px;padding:4px 9px;color:#69716F;font-size:.63rem}.am-chip b{color:var(--ink)}

/* horizontal nav */
div[data-testid="stRadio"]{margin:-2px 0 18px;width:100%}
div[data-testid="stRadio"]>label{display:none!important}
div[data-testid="stRadio"] div[role="radiogroup"]{display:flex!important;gap:8px;background:rgba(248,246,240,.84);border:1px solid var(--line);border-radius:18px;padding:6px;box-shadow:0 14px 34px rgba(29,41,45,.05);width:100%;max-width:100%;overflow-x:auto;justify-content:stretch;align-items:stretch}
div[data-testid="stRadio"] div[role="radiogroup"] label{margin:0!important;padding:11px 12px!important;border-radius:13px;cursor:pointer;transition:.26s cubic-bezier(.2,.8,.2,1);white-space:nowrap;position:relative;flex:1 1 0;min-width:0;display:flex!important;align-items:center;justify-content:center;text-align:center;background:rgba(255,255,255,.34);border:1px solid rgba(213,206,194,.45);overflow:hidden}
div[data-testid="stRadio"] div[role="radiogroup"] label:before{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 0 42%,rgba(255,255,255,.52) 50%,transparent 58% 100%);transform:translateX(-120%);transition:transform .65s ease;pointer-events:none}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover{background:#F3EFE7;transform:translateY(-2px);box-shadow:0 10px 22px rgba(29,41,45,.07)}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover:before{transform:translateX(130%)}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked){background:linear-gradient(180deg,#243236,#182427);border-color:#1C282B;box-shadow:0 12px 26px rgba(29,41,45,.16), inset 0 1px 0 rgba(255,255,255,.03)}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked):after{content:"";position:absolute;left:14px;right:14px;bottom:4px;height:3px;background:linear-gradient(90deg,var(--orange),#FF9A5E);border-radius:999px;box-shadow:0 0 14px rgba(255,104,27,.35)}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p{color:#F7F7F3!important}
div[data-testid="stRadio"] div[role="radiogroup"] input{display:none!important}
div[data-testid="stRadio"] div[role="radiogroup"] p{font-size:.78rem!important;font-weight:760!important;color:#5E6865!important;margin:0!important;overflow:hidden;text-overflow:ellipsis}

.am-page-title{margin:8px 0 4px;font-size:2.0rem;letter-spacing:-.045em;font-weight:820;color:var(--ink);animation:rise .42s cubic-bezier(.2,.7,.2,1) both}.am-page-sub{color:#66706D;font-size:.86rem;margin-bottom:22px;animation:rise .52s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:none}}

.am-card{background:rgba(248,246,240,.97);border:1px solid var(--line);border-radius:18px;padding:15px 17px 14px;min-height:102px;box-shadow:var(--shadow);transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease;animation:rise .5s ease both}
.am-card:hover{transform:translateY(-4px);border-color:#C2B9AC;box-shadow:0 24px 58px rgba(29,41,45,.11)}
.am-card .lab{color:#777F7D;text-transform:uppercase;font-size:.59rem;letter-spacing:.15em;font-weight:850}.am-card .val{font-size:1.52rem;line-height:1.05;font-weight:850;margin-top:10px;color:var(--ink)}.am-card .hint{color:#8C9491;font-size:.68rem;margin-top:8px}.am-card.accent{position:relative}.am-card.accent:before{content:"";position:absolute;left:15px;right:15px;top:-1px;height:3px;border-radius:0 0 3px 3px;background:linear-gradient(90deg,var(--orange) 0 43%,transparent 43% 57%,var(--orange) 57% 100%)}

/* live twin */
.flow-shell{position:relative;background:rgba(248,246,240,.9);border:1px solid var(--line);border-radius:24px;padding:22px 20px 22px;box-shadow:var(--shadow);margin-top:7px;overflow:hidden}
.flow-shell:after{content:"";position:absolute;inset:auto -10% -45% auto;width:420px;height:240px;background:radial-gradient(circle,rgba(63,142,137,.07),transparent 68%);pointer-events:none}
.flow-topline{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.flow-label{font-size:.63rem;letter-spacing:.16em;text-transform:uppercase;color:#777F7D;font-weight:850}.flow-legend{font-size:.68rem;color:#8A918F}.flow-legend b{color:var(--orange2)}
.live-badge{display:inline-flex;align-items:center;gap:7px;margin-left:10px;border:1px solid #D6D1C7;background:#FBFAF6;border-radius:999px;padding:4px 8px;font-size:.61rem;color:#65706D}.live-badge i{display:block;width:6px;height:6px;border-radius:50%;background:var(--teal);box-shadow:0 0 0 0 rgba(63,142,137,.35);animation:livePulse 1.5s infinite}@keyframes livePulse{70%{box-shadow:0 0 0 7px rgba(63,142,137,0)}}
.flow-wrap{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;position:relative}.flow-wrap:before{content:"";position:absolute;left:7%;right:7%;top:46px;height:2px;background:linear-gradient(90deg,#CFC9BE,#BEB8AD,#CFC9BE);z-index:0}
.flow-runner{position:absolute;top:42px;left:7%;width:10px;height:10px;border-radius:50%;background:var(--teal);box-shadow:0 0 0 4px #ECE8DF,0 0 20px rgba(63,142,137,.65);z-index:2;animation:runner 7.5s cubic-bezier(.4,0,.2,1) infinite}
@keyframes runner{0%{left:7%;opacity:0}5%{opacity:1}23%{left:27%}43%{left:47%}63%{left:67%}83%{left:87%;opacity:1}100%{left:87%;opacity:0}}
.flow-node{position:relative;z-index:1}.flow-card{position:relative;background:#FBFAF6;border:1px solid #D6D1C7;border-radius:16px;padding:14px 14px 13px;min-height:154px;box-shadow:0 7px 18px rgba(29,41,45,.035);transition:.22s cubic-bezier(.2,.8,.2,1);animation:nodeIn .45s ease both}.flow-node:nth-child(2) .flow-card{animation-delay:.06s}.flow-node:nth-child(3) .flow-card{animation-delay:.12s}.flow-node:nth-child(4) .flow-card{animation-delay:.18s}.flow-node:nth-child(5) .flow-card{animation-delay:.24s}@keyframes nodeIn{from{opacity:0;transform:translateY(8px) scale(.985)}to{opacity:1;transform:none}}
.flow-card:hover{transform:translateY(-5px) scale(1.012);box-shadow:0 16px 34px rgba(29,41,45,.085)}.flow-card:after{content:"";position:absolute;width:9px;height:9px;border-radius:50%;background:#B7B2A9;border:3px solid #F7F5EF;top:41px;left:50%;transform:translateX(-50%)}.flow-card.bottleneck{border-color:#FFAB80;box-shadow:0 0 0 3px rgba(255,104,27,.07),0 8px 20px rgba(29,41,45,.04);animation:bottleneckPulse 2.2s ease-in-out infinite}@keyframes bottleneckPulse{50%{box-shadow:0 0 0 7px rgba(255,104,27,.035),0 12px 30px rgba(29,41,45,.06)}}
.flow-card.bottleneck:before{content:"";position:absolute;left:14px;right:14px;top:-2px;height:4px;background:linear-gradient(90deg,var(--orange) 0 43%,transparent 43% 57%,var(--orange) 57% 100%);border-radius:4px}.flow-card.bottleneck:after{background:var(--orange)}
.flow-id{font-size:.58rem;letter-spacing:.16em;text-transform:uppercase;color:#808886;font-weight:850}.flow-name{font-size:.87rem;font-weight:760;color:var(--ink);margin-top:4px;min-height:34px}.flow-util{font-size:1.43rem;font-weight:860;margin-top:10px}.flow-meta{margin-top:6px}.pill{display:inline-block;border:1px solid #D8D3C9;background:#F3F0E9;color:#68716F;border-radius:999px;padding:3px 7px;font-size:.61rem;margin-right:4px}.flow-note{color:#858D8A;font-size:.64rem;margin-top:8px;line-height:1.35}.bottleneck-tag{display:inline-block;margin-top:7px;color:#A73D08;background:#FFF0E7;border-radius:999px;padding:3px 8px;font-size:.58rem;font-weight:850;letter-spacing:.05em}
.pressure{margin-top:9px}.pressure-top{display:flex;justify-content:space-between;font-size:.56rem;color:#919895;text-transform:uppercase;letter-spacing:.08em}.pressure-bar{height:4px;background:#E4DFD5;border-radius:999px;overflow:hidden;margin-top:4px}.pressure-fill{height:100%;border-radius:999px;background:var(--teal);transform-origin:left;animation:barGrow .9s cubic-bezier(.2,.7,.2,1) both}.flow-card.bottleneck .pressure-fill{background:var(--orange)}@keyframes barGrow{from{transform:scaleX(0)}to{transform:scaleX(1)}}

.insight{background:#F8F4EC;border:1px solid #DDD6CA;border-left:3px solid var(--orange);padding:16px 17px;border-radius:0 15px 15px 0;color:#46504D;line-height:1.52;animation:rise .45s ease both}.insight b{color:var(--ink)}.section-rule{height:1px;background:linear-gradient(90deg,#CAC5BB,transparent);margin:18px 0 22px}
.am-empty{background:rgba(248,246,240,.9);border:1px solid var(--line);border-radius:22px;padding:32px;box-shadow:var(--shadow);margin-top:8px}.am-empty-eyebrow{color:var(--orange2);font-size:.62rem;letter-spacing:.16em;text-transform:uppercase;font-weight:850}.am-empty-title{font-size:1.55rem;font-weight:820;margin-top:8px;letter-spacing:-.035em}.am-empty-copy{color:#66706D;max-width:720px;margin-top:8px;line-height:1.55}.am-empty-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:20px}.am-empty-item{background:#F2EEE6;border:1px solid #DDD6CA;border-radius:14px;padding:12px;color:#5C6663;font-size:.75rem}.am-empty-item b{display:block;color:var(--ink);margin-bottom:3px}

div[data-testid="stMetric"]{background:#F8F6F0;border:1px solid var(--line);padding:13px 15px;border-radius:16px;box-shadow:0 8px 20px rgba(29,41,45,.035)}div[data-testid="stMetric"] label{color:#747C79!important}
div[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#F8F6F0}.stButton{width:100%}.stButton>button{width:100%;min-height:46px;border-radius:14px;border:1px solid #C9C3B8;background:linear-gradient(180deg,#FBF9F4,#F2EEE7);color:var(--ink);font-weight:780;letter-spacing:-.01em;transition:.24s cubic-bezier(.2,.8,.2,1);position:relative;overflow:hidden;box-shadow:0 10px 22px rgba(29,41,45,.05)}.stButton>button:before{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 0 40%,rgba(255,255,255,.48) 50%,transparent 60% 100%);transform:translateX(-130%);transition:transform .75s ease;pointer-events:none}.stButton>button:hover{border-color:var(--orange);color:#A73D08;background:linear-gradient(180deg,#FFF8F2,#F8F0E8);transform:translateY(-2px);box-shadow:0 14px 28px rgba(29,41,45,.10)}.stButton>button:hover:before{transform:translateX(135%)}.stButton>button:active{transform:translateY(0) scale(.995)}.stButton>button[kind="primary"]{background:linear-gradient(180deg,#233136,#182427);color:#F7F7F3;border:1px solid #1A272A;box-shadow:0 12px 24px rgba(29,41,45,.14)}.stButton>button[kind="primary"]:after{content:"";position:absolute;left:12px;right:12px;bottom:4px;height:3px;background:linear-gradient(90deg,var(--orange),#FFA061);border-radius:999px;opacity:.95}.stButton>button[kind="primary"]:hover{background:linear-gradient(180deg,#2A393D,#1D2A2D);color:white}.stSelectbox div[data-baseweb="select"]>div,.stNumberInput input,.stTextInput input{border-color:#CEC8BD!important;background:#F8F6F0!important;color:var(--ink)!important;min-height:46px!important;box-shadow:0 6px 16px rgba(29,41,45,.03)}
[data-testid="stDataEditor"]{box-shadow:0 8px 26px rgba(29,41,45,.035)}[data-testid="stDataEditor"] button{border-radius:10px!important}[data-testid="stDataEditor"] [role="grid"]{min-height:180px}

/* cinematic tabs + briefing */
[data-testid="stTabs"] [data-baseweb="tab-list"]{display:flex;gap:6px;background:rgba(248,246,240,.72);border:1px solid var(--line);padding:5px;border-radius:14px;width:100%;max-width:100%;box-shadow:0 8px 24px rgba(29,41,45,.035)}
[data-testid="stTabs"] [data-baseweb="tab"]{height:auto;padding:8px 12px;border-radius:10px;color:#66706D;font-weight:760;font-size:.76rem;flex:1;justify-content:center}
[data-testid="stTabs"] [aria-selected="true"]{background:var(--ink);color:#F7F7F3!important}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{display:none}
.am-brief-hero{position:relative;overflow:hidden;background:#162124;border:1px solid #2D3A3E;border-radius:22px;padding:26px 28px;color:#F7F7F3;box-shadow:0 24px 60px rgba(29,41,45,.14);margin:8px 0 14px}
.am-brief-hero:after{content:"";position:absolute;right:-80px;top:-100px;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(255,104,27,.18),transparent 66%);animation:briefGlow 5s ease-in-out infinite alternate}
@keyframes briefGlow{to{transform:translate(-35px,25px) scale(1.14)}}
.am-brief-kicker{font-size:.61rem;letter-spacing:.18em;text-transform:uppercase;color:#FF8A4C;font-weight:850}.am-brief-title{font-size:2rem;line-height:1.05;font-weight:850;letter-spacing:-.045em;margin-top:9px;max-width:760px}.am-brief-title span{color:#FF8A4C}.am-brief-copy{position:relative;z-index:1;margin-top:12px;color:#BFCBC8;max-width:860px;line-height:1.58;font-size:.86rem}.am-brief-copy b{color:white}
/* top navigation can host more modules without feeling cramped */
div[data-testid="stRadio"] div[role="radiogroup"] label{padding:10px 10px!important}
div[data-testid="stRadio"] div[role="radiogroup"] p{font-size:.74rem!important}

/* experience update */
[data-testid="stFileUploader"]{background:rgba(248,246,240,.72);border:1px dashed #C7BFB3;border-radius:16px;padding:8px}
[data-testid="stExpander"]{background:rgba(248,246,240,.7);border:1px solid var(--line)!important;border-radius:17px!important;overflow:hidden;box-shadow:0 8px 22px rgba(29,41,45,.025)}
[data-testid="stStatusWidget"]{border-radius:17px!important;border:1px solid #D8D0C4!important;background:#F8F6F0!important}
[data-testid="stDownloadButton"] button{min-height:44px;border-radius:13px;border:1px solid #C9C3B8;background:#F8F6F0;color:var(--ink);font-weight:760}
[data-testid="stDownloadButton"] button:hover{border-color:var(--orange);color:#A73D08}
[data-testid="stTabs"] [data-baseweb="tab-list"]{backdrop-filter:blur(10px);position:sticky;top:.7rem;z-index:20}

/* V13 · product polish */
.block-container{max-width:1540px!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stToolbar"]{opacity:.35;transition:opacity .2s ease}[data-testid="stToolbar"]:hover{opacity:1}
.am-shell{transition:transform .25s ease,box-shadow .25s ease}.am-shell:hover{transform:translateY(-1px)}
.am-context{gap:7px}.am-chip{backdrop-filter:blur(8px)}
[data-testid="stHorizontalBlock"]{row-gap:.55rem}
.stButton>button[kind="secondary"]{background:rgba(248,246,240,.82);backdrop-filter:blur(8px)}
[data-testid="stExpander"] summary{font-weight:760;color:#48524f}
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 0 4px rgba(255,104,27,.08)}
[data-testid="stNumberInput"] button{border-color:#d5cec2!important}
[data-testid="stAlert"]{border-radius:15px!important}
/* stronger editorial rhythm */
h3{letter-spacing:-.025em!important;margin-top:1.55rem!important}.section-rule{margin:25px 0 27px}
/* data surfaces */
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{box-shadow:0 12px 30px rgba(29,41,45,.045)}
/* make empty / insight surfaces feel related */
.insight,.am-empty,.am-brief-hero{transition:transform .22s ease,box-shadow .22s ease}.insight:hover{transform:translateY(-2px);box-shadow:0 14px 32px rgba(29,41,45,.06)}
/* subtle ambient scan for primary simulation surfaces */
.am-brief-hero:before{content:"";position:absolute;left:-20%;top:0;width:18%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.025),transparent);animation:amScan 7s linear infinite;pointer-events:none}@keyframes amScan{to{left:120%}}

@media(max-width:1050px){.am-topbar{grid-template-columns:1fr}.am-status{text-align:left}.am-topbar-logo{max-width:65vw}.flow-wrap{grid-template-columns:1fr}.flow-wrap:before,.flow-runner{display:none}.flow-card:after{display:none}.am-empty-grid{grid-template-columns:1fr}.block-container{padding:1.35rem .9rem 3rem!important}.am-brief-title{font-size:1.55rem}div[data-testid="stRadio"] div[role="radiogroup"]{min-width:720px}}
</style>
''', unsafe_allow_html=True)


def splash():
    icon = _data_uri("icon-dark.svg", "image/svg+xml")
    st.markdown(f'<div class="am-splash"><div class="am-splash-inner"><img class="am-splash-logo" src="{icon}" alt="Anti-Murphy"><div class="am-splash-name">ANTI-MURPHY</div><div class="am-splash-sub">Decision Twin</div><div class="am-loadline"></div></div></div>', unsafe_allow_html=True)


def topbar(stations_count: int, workers_count: int, orders_count: int, status_text: str = "Cenário-base ativo"):
    logo = _data_uri("logo-light.png", "image/png")
    html = (
        f'<div class="am-shell"><div class="am-topbar">'
        f'<img class="am-topbar-logo" src="{logo}" alt="Anti-Murphy">'
        '<div class="am-topbar-copy"><div class="am-kicker">Decision Twin · PCP + DES + What-if</div>'
        '<div class="am-sub">Teste decisões antes de aplicá-las. Capacidade, pessoas, filas, custo e prazo respondem à mesma simulação.</div></div>'
        f'<div class="am-status"><div class="top">Estado do modelo</div><div class="value"><span class="dot"></span>{status_text}</div></div>'
        f'</div><div class="am-context"><span class="am-chip"><b>{stations_count}</b> postos</span>'
        f'<span class="am-chip"><b>{workers_count}</b> operadores</span><span class="am-chip"><b>{orders_count}</b> OPs</span></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def page_intro(title: str, subtitle: str):
    st.markdown(f'<div class="am-page-title">{title}</div><div class="am-page-sub">{subtitle}</div>', unsafe_allow_html=True)


def metric_card(label, value, hint="", accent="#1D292D", emphasis=False):
    klass = "am-card accent" if emphasis else "am-card"
    st.markdown(f'<div class="{klass}"><div class="lab">{label}</div><div class="val" style="color:{accent}">{value}</div><div class="hint">{hint}</div></div>', unsafe_allow_html=True)
