from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any, Dict, Iterable, List

import streamlit as st

BRAND_DIR = Path(__file__).resolve().parents[1] / "assets" / "brand"


def _e(value: Any) -> str:
    return html.escape(str(value))


def _data_uri(filename: str, mime: str) -> str:
    raw = (BRAND_DIR / filename).read_bytes()
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def inject_v15_css() -> None:
    """V15 visual system: compact enterprise shell + editorial operational surfaces."""
    st.markdown(
        r"""
<style>
/* ──────────────────────────────────────────────────────────────
   ANTI-MURPHY V15 · PRODUCT REDESIGN
   Quiet industrial luxury: graphite / porcelain / signal orange
   ────────────────────────────────────────────────────────────── */
:root{
  --am15-bg:#EDEBE6;
  --am15-paper:#F7F5F0;
  --am15-paper-2:#F1EEE8;
  --am15-ink:#142126;
  --am15-ink-2:#1B2A2F;
  --am15-ink-3:#24363B;
  --am15-muted:#68736F;
  --am15-muted-2:#8C9491;
  --am15-line:#D3CEC5;
  --am15-line-dark:#304146;
  --am15-orange:#FF6523;
  --am15-orange-2:#FF8853;
  --am15-teal:#4CA9A0;
  --am15-green:#2F7D68;
  --am15-red:#B94F43;
  --am15-shadow:0 16px 42px rgba(20,33,38,.065);
  --am15-shadow-deep:0 24px 70px rgba(20,33,38,.16);
}
html,body,[class*="css"]{font-family:Inter,Manrope,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important}
.stApp{
  color:var(--am15-ink)!important;
  background:
    radial-gradient(circle at 82% -10%,rgba(255,101,35,.06),transparent 30%),
    radial-gradient(circle at 6% 25%,rgba(76,169,160,.035),transparent 28%),
    linear-gradient(rgba(20,33,38,.015) 1px,transparent 1px),
    linear-gradient(90deg,rgba(20,33,38,.015) 1px,transparent 1px),
    var(--am15-bg)!important;
  background-size:auto,auto,64px 64px,64px 64px,auto!important;
}
.block-container{max-width:1600px!important;padding:1rem 1.35rem 4rem!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stToolbar"]{opacity:.25;transition:.2s ease}[data-testid="stToolbar"]:hover{opacity:1}

/* enterprise masthead */
.am15-masthead{position:relative;overflow:hidden;background:linear-gradient(122deg,#111D21 0%,#18272B 65%,#1C2C30 100%);border:1px solid #2A3A3E;border-radius:22px;padding:0;box-shadow:var(--am15-shadow-deep);margin:0 0 12px;color:#F4F5F1}
.am15-masthead:before{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 0 44%,rgba(255,255,255,.025) 50%,transparent 56% 100%);transform:translateX(-80%);animation:am15Scan 11s linear infinite;pointer-events:none}
.am15-masthead:after{content:"";position:absolute;width:420px;height:420px;border-radius:50%;right:-160px;top:-220px;background:radial-gradient(circle,rgba(255,101,35,.17),transparent 67%);pointer-events:none}
@keyframes am15Scan{to{transform:translateX(100%)}}
.am15-head-main{display:grid;grid-template-columns:230px 1fr auto;align-items:center;gap:24px;min-height:82px;padding:14px 18px 11px;position:relative;z-index:1}
.am15-logo{width:215px;height:auto;display:block}.am15-product{border-left:1px solid #3B4A4E;padding-left:24px;min-width:0}.am15-eyebrow{font-size:.58rem;letter-spacing:.19em;text-transform:uppercase;font-weight:850;color:#FF8B58}.am15-title{font-size:1.07rem;letter-spacing:-.025em;font-weight:760;margin-top:4px;color:#F3F5F1}.am15-sub{font-size:.66rem;color:#8EA09B;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.am15-modelstate{text-align:right;min-width:210px}.am15-modelstate .k{font-size:.52rem;text-transform:uppercase;letter-spacing:.16em;color:#71837E;font-weight:800}.am15-modelstate .v{margin-top:5px;font-size:.72rem;font-weight:750;color:#EAF0ED}.am15-dot{width:7px;height:7px;border-radius:50%;background:#53BA9F;box-shadow:0 0 0 5px rgba(83,186,159,.08);display:inline-block;margin-right:7px}
.am15-head-meta{display:flex;align-items:center;gap:7px;border-top:1px solid #28383C;padding:8px 18px 10px;position:relative;z-index:1}.am15-meta-chip{font-size:.56rem;color:#91A19D;border:1px solid #34464A;background:#18272B;border-radius:999px;padding:4px 9px}.am15-meta-chip b{color:#EAF0ED}.am15-meta-note{margin-left:auto;font-size:.55rem;letter-spacing:.08em;text-transform:uppercase;color:#61746F}

/* workspace navigation: flatter, denser, not pill-dashboard-ish */
.am15-nav-caption{font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#8B918E;font-weight:850;margin:10px 3px 6px}
.stButton>button,.stDownloadButton>button{font-family:inherit!important;transition:.18s ease!important}
/* first horizontal nav rows inherit this more restrained product style */
.stButton>button{min-height:41px!important;border-radius:10px!important;border:1px solid var(--am15-line)!important;background:rgba(247,245,240,.86)!important;color:#5E6865!important;font-weight:650!important;box-shadow:0 5px 16px rgba(20,33,38,.025)!important}
.stButton>button:hover{transform:translateY(-1px)!important;border-color:#B9B2A8!important;color:var(--am15-ink)!important;background:#FBFAF7!important;box-shadow:0 9px 22px rgba(20,33,38,.06)!important}
.stButton>button[kind="primary"]{background:linear-gradient(180deg,#1C2B30,#142126)!important;border-color:#142126!important;color:#F3F5F2!important;box-shadow:0 10px 25px rgba(20,33,38,.13)!important;position:relative;overflow:hidden}
.stButton>button[kind="primary"]:after{content:"";position:absolute;left:10px;right:10px;bottom:3px;height:2px;background:var(--am15-orange);border-radius:999px}
.stButton>button[kind="primary"]:hover{background:linear-gradient(180deg,#223439,#18262B)!important;color:white!important}

/* page title system */
.am-page-title{font-size:2rem!important;line-height:1.05!important;letter-spacing:-.052em!important;font-weight:820!important;color:var(--am15-ink)!important;margin:22px 0 5px!important}.am-page-sub{font-size:.76rem!important;color:#74807C!important;max-width:860px!important;margin-bottom:16px!important}
.am15-pagebar{display:flex;align-items:end;justify-content:space-between;gap:20px;margin:18px 0 13px}.am15-pagebar .left .ey{font-size:.55rem;text-transform:uppercase;letter-spacing:.16em;color:var(--am15-orange);font-weight:850}.am15-pagebar h1{font-size:2rem;line-height:1.05;letter-spacing:-.055em;margin:4px 0 0;font-weight:820}.am15-pagebar .right{text-align:right;font-size:.62rem;color:#7B8581;max-width:420px}

/* cockpit KPIs: custom compact strip */
.am15-kpis{display:grid;grid-template-columns:1.08fr 1fr 1fr 1.08fr .95fr;gap:8px;margin:8px 0 13px}.am15-kpi{position:relative;background:rgba(248,247,243,.94);border:1px solid var(--am15-line);border-radius:13px;padding:12px 14px 11px;min-height:92px;overflow:hidden;box-shadow:0 7px 22px rgba(20,33,38,.035);transition:.2s ease}.am15-kpi:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(20,33,38,.065)}.am15-kpi .lab{font-size:.51rem;letter-spacing:.16em;text-transform:uppercase;font-weight:850;color:#89918E}.am15-kpi .value{font-size:1.52rem;font-weight:800;letter-spacing:-.045em;color:var(--am15-ink);margin-top:8px}.am15-kpi .sub{font-size:.6rem;color:#8A9390;margin-top:5px}.am15-kpi .signal{position:absolute;right:10px;top:10px;font-size:.54rem;font-weight:800;padding:3px 7px;border-radius:999px;background:#ECE8E1;color:#737D79}.am15-kpi.risk{border-top:2px solid var(--am15-orange)}.am15-kpi.risk .value{color:#C94C18}.am15-kpi.good{border-top:2px solid var(--am15-teal)}.am15-kpi.good .value{color:#33877F}

/* hero / editorial panels */
.am15-module-hero{position:relative;overflow:hidden;border:1px solid var(--am15-line);border-radius:19px;background:linear-gradient(135deg,#FAF9F5,#F3F0E9);padding:20px 22px;margin:9px 0 15px;box-shadow:var(--am15-shadow)}.am15-module-hero:after{content:"";position:absolute;right:-100px;top:-120px;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(255,101,35,.075),transparent 68%)}.am15-module-hero .ey{font-size:.54rem;letter-spacing:.17em;text-transform:uppercase;color:#C54B18;font-weight:850}.am15-module-hero h2{font-size:1.48rem!important;line-height:1.08!important;letter-spacing:-.042em!important;margin:8px 0 5px!important}.am15-module-hero p{font-size:.72rem!important;max-width:780px!important;color:#707A76!important;line-height:1.48!important;margin:0!important}.am15-hero-pills{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}.am15-hero-pill{font-size:.57rem;font-weight:700;color:#56615D;background:#EBE7DF;border:1px solid #D8D1C7;border-radius:999px;padding:5px 8px}

/* twin stage treatment */
.am15-stage-label{display:flex;align-items:center;justify-content:space-between;margin:18px 2px 8px}.am15-stage-label .a{font-size:.56rem;letter-spacing:.17em;text-transform:uppercase;font-weight:850;color:#7C8581}.am15-stage-label .b{font-size:.59rem;color:#9AA09E}.am15-stage-label .live{display:inline-flex;align-items:center;gap:6px;color:#4B8F84;font-weight:750}.am15-stage-label .live:before{content:"";width:6px;height:6px;border-radius:50%;background:#55B49E;box-shadow:0 0 0 4px rgba(85,180,158,.08)}

/* decision deck */
.am15-deck{display:grid;grid-template-columns:1.15fr 1fr 1fr 1fr;gap:8px;margin:10px 0 16px}.am15-deck-card{background:#172529;color:#EAF0ED;border:1px solid #2B3D42;border-radius:13px;padding:13px 14px;min-height:112px;position:relative;overflow:hidden}.am15-deck-card:after{content:"";position:absolute;width:140px;height:140px;border-radius:50%;right:-75px;bottom:-95px;background:radial-gradient(circle,rgba(76,169,160,.09),transparent 68%)}.am15-deck-card.primary:after{background:radial-gradient(circle,rgba(255,101,35,.17),transparent 68%)}.am15-deck-card .ey{font-size:.5rem;letter-spacing:.14em;text-transform:uppercase;color:#71847F;font-weight:850}.am15-deck-card.primary .ey{color:#FF8B58}.am15-deck-card b{display:block;font-size:.98rem;line-height:1.22;letter-spacing:-.02em;margin:8px 0 5px;color:#F5F7F3}.am15-deck-card p{font-size:.61rem;line-height:1.45;color:#8EA09B!important;margin:0!important}.am15-deck-card .mini{position:absolute;right:12px;top:12px;font-size:.55rem;color:#8FA19C;background:#213237;border:1px solid #33474C;border-radius:999px;padding:3px 7px}

/* station gallery for Model */
.am15-station-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:8px;margin:8px 0 13px}.am15-station{background:#F8F7F3;border:1px solid var(--am15-line);border-radius:13px;padding:12px 13px;min-height:108px;position:relative}.am15-station .id{font-size:.49rem;letter-spacing:.14em;text-transform:uppercase;color:#C5501D;font-weight:850}.am15-station .name{font-size:.86rem;font-weight:760;color:var(--am15-ink);margin-top:6px}.am15-station .meta{font-size:.58rem;color:#818A87;margin-top:8px;line-height:1.55}.am15-station .cap{height:3px;background:#E4E0D8;border-radius:99px;overflow:hidden;margin-top:9px}.am15-station .cap i{display:block;height:100%;background:linear-gradient(90deg,var(--am15-teal),#72C5BB);border-radius:99px}.am15-station .tag{position:absolute;right:9px;top:9px;font-size:.47rem;color:#7C8582;border:1px solid #DDD7CE;border-radius:999px;padding:2px 6px}

/* compare: executive before/after */
.am15-compare-story{display:grid;grid-template-columns:1fr 42px 1fr;gap:10px;align-items:stretch;margin:11px 0 14px}.am15-state{background:#F8F7F3;border:1px solid var(--am15-line);border-radius:16px;padding:16px}.am15-state.after{border-top:2px solid var(--am15-teal)}.am15-state.before{border-top:2px solid #AAB3AF}.am15-state .ey{font-size:.52rem;letter-spacing:.16em;text-transform:uppercase;color:#86908C;font-weight:850}.am15-state h3{font-size:1rem!important;margin:6px 0 11px!important}.am15-state-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px}.am15-state-metric{border-top:1px solid #E0DBD2;padding-top:7px}.am15-state-metric span{font-size:.5rem;text-transform:uppercase;letter-spacing:.1em;color:#969D9A}.am15-state-metric b{display:block;font-size:.88rem;margin-top:3px}.am15-arrow{display:flex;align-items:center;justify-content:center;font-size:1.45rem;color:#A2AAA7}.am15-verdict{background:#152327;border:1px solid #2B3C40;border-radius:16px;padding:15px 17px;color:#EFF3F0;margin:9px 0 15px}.am15-verdict .ey{font-size:.5rem;letter-spacing:.16em;text-transform:uppercase;color:#FF8B58;font-weight:850}.am15-verdict b{font-size:.95rem;display:block;margin-top:7px}.am15-verdict p{font-size:.63rem;line-height:1.48;color:#91A29D!important;margin:5px 0 0!important}

/* form surfaces and tables */
[data-testid="stExpander"]{background:rgba(248,247,243,.85)!important;border:1px solid var(--am15-line)!important;border-radius:13px!important;overflow:hidden!important;box-shadow:none!important}[data-testid="stExpander"] summary{font-weight:720!important;color:#4D5854!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid var(--am15-line)!important;border-radius:13px!important;overflow:hidden!important;background:#F8F7F3!important;box-shadow:0 7px 20px rgba(20,33,38,.025)!important}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{border-radius:9px!important;background:#FAF9F5!important;border-color:#D4CEC5!important;min-height:42px!important}
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 0 4px rgba(255,101,35,.09)!important}
[data-testid="stFileUploader"]{background:#F7F5F0!important;border:1px dashed #C9C2B8!important;border-radius:13px!important;padding:7px!important}
[data-testid="stAlert"]{border-radius:12px!important}

/* tabs become a slim tool switcher */
[data-testid="stTabs"] [data-baseweb="tab-list"]{display:flex!important;gap:2px!important;background:#E5E1D9!important;border:1px solid #D5CFC6!important;padding:4px!important;border-radius:11px!important;width:100%!important;box-shadow:none!important;position:static!important}
[data-testid="stTabs"] [data-baseweb="tab"]{height:34px!important;padding:0 10px!important;border-radius:7px!important;color:#69736F!important;font-weight:680!important;font-size:.68rem!important;flex:1!important;justify-content:center!important}
[data-testid="stTabs"] [aria-selected="true"]{background:#172529!important;color:#F3F5F2!important;box-shadow:0 5px 14px rgba(20,33,38,.12)!important}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{display:none!important}

/* Streamlit metrics become secondary, not dominant */
div[data-testid="stMetric"]{background:#F8F7F3!important;border:1px solid var(--am15-line)!important;padding:11px 13px!important;border-radius:12px!important;box-shadow:none!important}div[data-testid="stMetric"] label{font-size:.62rem!important;color:#727D79!important}div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-size:1.25rem!important;letter-spacing:-.035em!important}

/* tighter rhythm, no giant blank bands */
.element-container{margin-bottom:.08rem!important}[data-testid="stVerticalBlock"]{gap:.55rem!important}[data-testid="stHorizontalBlock"]{gap:.55rem!important;row-gap:.55rem!important}.section-rule{margin:15px 0!important}h3{font-size:1.18rem!important;letter-spacing:-.035em!important;margin:1.2rem 0 .45rem!important}h4{letter-spacing:-.02em!important}

/* responsive */
@media(max-width:1100px){
 .am15-head-main{grid-template-columns:190px 1fr}.am15-modelstate{grid-column:1/-1;text-align:left}.am15-logo{width:180px}.am15-kpis{grid-template-columns:1fr 1fr}.am15-deck{grid-template-columns:1fr 1fr}.am15-compare-story{grid-template-columns:1fr}.am15-arrow{transform:rotate(90deg)}.am15-sub{white-space:normal}.block-container{padding:.7rem .75rem 3rem!important}
}
@media(max-width:650px){.am15-head-main{grid-template-columns:1fr}.am15-product{border-left:0;padding-left:0}.am15-head-meta{flex-wrap:wrap}.am15-meta-note{width:100%;margin-left:0}.am15-kpis,.am15-deck{grid-template-columns:1fr}.am15-pagebar{display:block}.am15-pagebar .right{text-align:left;margin-top:8px}}
</style>
""",
        unsafe_allow_html=True,
    )


def product_header(stations_count: int, workers_count: int, orders_count: int, status_text: str) -> None:
    logo = _data_uri("logo-dark.png", "image/png")
    status_detail = "modelo pronto para experimentação" if "base" in status_text.lower() else "cenário disponível para comparação"
    st.markdown(
        f"""
        <header class="am15-masthead">
          <div class="am15-head-main">
            <img class="am15-logo" src="{logo}" alt="ANTI-MURPHY">
            <div class="am15-product">
              <div class="am15-eyebrow">Decision Intelligence · Production Systems</div>
              <div class="am15-title">Workspace operacional</div>
              <div class="am15-sub">Simule. Entenda a restrição. Teste a decisão antes de transformar a operação real.</div>
            </div>
            <div class="am15-modelstate">
              <div class="k">Estado do modelo</div>
              <div class="v"><span class="am15-dot"></span>{_e(status_text)}</div>
            </div>
          </div>
          <div class="am15-head-meta">
            <span class="am15-meta-chip"><b>{stations_count}</b> postos</span>
            <span class="am15-meta-chip"><b>{workers_count}</b> operadores</span>
            <span class="am15-meta-chip"><b>{orders_count}</b> OPs</span>
            <span class="am15-meta-note">{_e(status_detail)}</span>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def pagebar(index: str, title: str, subtitle: str, context: str = "") -> None:
    st.markdown(
        f"""
        <div class="am15-pagebar">
          <div class="left"><div class="ey">{_e(index)}</div><h1>{_e(title)}</h1></div>
          <div class="right">{_e(subtitle)}{('<br><b>'+_e(context)+'</b>') if context else ''}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def module_hero(kicker: str, title: str, copy: str, pills: Iterable[str] = ()) -> None:
    pill_html = "".join(f'<span class="am15-hero-pill">{_e(x)}</span>' for x in pills)
    st.markdown(
        f'<section class="am15-module-hero"><div class="ey">{_e(kicker)}</div><h2>{_e(title)}</h2><p>{_e(copy)}</p><div class="am15-hero-pills">{pill_html}</div></section>',
        unsafe_allow_html=True,
    )


def cockpit_kpis(base: Dict[str, Any], exposure: float, resilience: Dict[str, Any]) -> None:
    sla = float(base.get("sla_pct", 0))
    risk_class = "risk" if exposure >= 60 or sla < 70 else "good"
    kpis = [
        ("Throughput", f"{base.get('throughput_h',0):.2f} un/h", f"{base.get('total_units',0)} unidades simuladas", "Fluxo", ""),
        ("SLA", f"{sla:.0f}%", f"{base.get('late_orders',0)} OPs atrasadas", "Prazo", "good" if sla >= 80 else "risk"),
        ("Makespan", f"{base.get('makespan_h',0):.1f} h", "tempo até a última OP", "Tempo", ""),
        ("Custo / un.", f"R$ {base.get('unit_cost',0):.2f}", "custo operacional simulado", "Economia", ""),
        ("Resiliência", f"{float(resilience.get('score',0)):.0f}/100", str(resilience.get('band','')), "Murphy", risk_class),
    ]
    blocks=[]
    for lab,val,sub,signal,klass in kpis:
        blocks.append(f'<div class="am15-kpi {klass}"><div class="signal">{_e(signal)}</div><div class="lab">{_e(lab)}</div><div class="value">{_e(val)}</div><div class="sub">{_e(sub)}</div></div>')
    st.markdown('<div class="am15-kpis">'+''.join(blocks)+'</div>', unsafe_allow_html=True)


def stage_label(label: str = "Live Decision Twin", note: str = "telemetria derivada da simulação") -> None:
    st.markdown(f'<div class="am15-stage-label"><div class="a">{_e(label)}</div><div class="b"><span class="live">modelo ativo</span> · {_e(note)}</div></div>', unsafe_allow_html=True)


def decision_deck(base: Dict[str, Any], resilience: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> None:
    bn = base.get("bottleneck", "-")
    row = next((r for r in base.get("stations", []) if r.get("Posto") == bn), {})
    rec = recommendations[0] if recommendations else {}
    rec_title = rec.get("title") or rec.get("Título") or rec.get("action") or rec.get("recommendation") or f"Testar capacidade em {bn}"
    rec_reason = rec.get("reason") or rec.get("detail") or rec.get("why") or "Valide a intervenção no Murphy Lab antes de alterar a operação real."
    wait = float(row.get("Espera média (min)", 0))
    queue = int(row.get("Fila máx.", 0))
    sla = float(base.get("sla_pct", 0))
    cost = float(base.get("unit_cost", 0))
    cards = f"""
      <div class="am15-deck-card primary"><div class="mini">restrição</div><div class="ey">Onde agir</div><b>{_e(bn)} · {_e(row.get('Nome',''))}</b><p>Fila máxima {queue} · espera média {wait:.1f} min. Este é o ponto que concentra a pressão sistêmica do cenário atual.</p></div>
      <div class="am15-deck-card"><div class="mini">{float(resilience.get('score',0)):.0f}/100</div><div class="ey">Robustez</div><b>{_e(resilience.get('band','Resiliência'))}</b><p>O índice combina pressão, prazo e sensibilidade operacional. Use o Stress Lab para enxergar a faixa de ruptura.</p></div>
      <div class="am15-deck-card"><div class="mini">próximo teste</div><div class="ey">Decisão sugerida</div><b>{_e(rec_title)}</b><p>{_e(rec_reason)}</p></div>
      <div class="am15-deck-card"><div class="mini">economia</div><div class="ey">Contexto executivo</div><b>SLA {sla:.0f}% · R$ {cost:.2f}/un.</b><p>Não otimize um KPI isolado: compare fluxo, prazo, custo e risco antes de escolher a intervenção.</p></div>
    """
    st.markdown(f'<div class="am15-deck">{cards}</div>', unsafe_allow_html=True)


def station_gallery(stations: Dict[str, Dict[str, Any]]) -> None:
    blocks=[]
    for sid, s in stations.items():
        machines=max(1,int(s.get("maquinas",1)))
        workers=max(0,int(s.get("operadores",0)))
        coverage=min(100, (workers/max(machines,1))*100)
        blocks.append(
            f'<div class="am15-station"><div class="tag">{machines} maq.</div><div class="id">{_e(sid)}</div><div class="name">{_e(s.get("nome",sid))}</div><div class="meta">{workers} operador(es) · setup {float(s.get("setup_min",0)):.0f} min<br>disp. {float(s.get("disponibilidade",1))*100:.0f}% · ef. {float(s.get("eficiencia_operador",1))*100:.0f}%</div><div class="cap"><i style="width:{coverage:.0f}%"></i></div></div>'
        )
    st.markdown('<div class="am15-station-grid">'+''.join(blocks)+'</div>', unsafe_allow_html=True)


def compare_story(base: Dict[str, Any], alt: Dict[str, Any], delta: Dict[str, Any], explanation: Dict[str, Any]) -> None:
    def state_card(cls: str, ey: str, name: str, x: Dict[str, Any]) -> str:
        return f'''<div class="am15-state {cls}"><div class="ey">{_e(ey)}</div><h3>{_e(name)}</h3><div class="am15-state-grid">
          <div class="am15-state-metric"><span>Throughput</span><b>{float(x.get('throughput_h',0)):.2f} un/h</b></div>
          <div class="am15-state-metric"><span>SLA</span><b>{float(x.get('sla_pct',0)):.0f}%</b></div>
          <div class="am15-state-metric"><span>Custo / un.</span><b>R$ {float(x.get('unit_cost',0)):.2f}</b></div>
          <div class="am15-state-metric"><span>Makespan</span><b>{float(x.get('makespan_h',0)):.1f} h</b></div>
        </div></div>'''
    story = state_card("before","Antes","Cenário-base",base) + '<div class="am15-arrow">→</div>' + state_card("after","Depois",alt.get("name","Cenário"),alt)
    headline = explanation.get("headline", "A simulação mostra o efeito sistêmico da decisão.")
    causes = explanation.get("causes", [])
    cause = " ".join(causes[:2]) if causes else "Compare a mudança de gargalo e os deltas antes de implementar."
    bottleneck = f"{base.get('bottleneck','-')} → {alt.get('bottleneck','-')}"
    st.markdown(f'<div class="am15-compare-story">{story}</div><div class="am15-verdict"><div class="ey">Decision readout · gargalo { _e(bottleneck) }</div><b>{_e(headline)}</b><p>{_e(cause)}</p></div>', unsafe_allow_html=True)


def scenario_preview(target: str, delta_workers: int, delta_machines: int, demand: float, rule: str, event_name: str, absent: int, base_rule: str = "EDD") -> None:
    changes=[]
    if delta_workers: changes.append(("Mão de obra", f"{delta_workers:+d} operador(es) · {target}"))
    if delta_machines: changes.append(("Capacidade", f"{delta_machines:+d} máquina(s) · {target}"))
    if abs(float(demand)-1.0) > 1e-9: changes.append(("Demanda", f"{demand:.1f}×"))
    if rule != base_rule: changes.append(("Despacho", rule))
    if event_name.lower() not in {"sem perturbação", "nenhuma", "none"}: changes.append(("Murphy Event", event_name))
    if absent: changes.append(("Ausência", f"{absent} operador(es) · {target}"))
    if not changes:
        st.markdown('<div class="am15-verdict"><div class="ey">SCENARIO PREVIEW · NEUTRO</div><b>Nenhuma intervenção configurada.</b><p>O cenário atual reproduz exatamente a base. Altere ao menos um recurso, demanda, regra ou perturbação para gerar um experimento útil.</p></div>', unsafe_allow_html=True)
        return
    chips=''.join(f'<span class="am15-hero-pill"><b>{_e(k)}:</b>&nbsp; {_e(v)}</span>' for k,v in changes)
    st.markdown(f'<div class="am15-module-hero"><div class="ey">SCENARIO PREVIEW</div><h2>O mundo alternativo está configurado.</h2><p>{len(changes)} mudança(s) serão aplicadas à cópia do cenário-base. A operação original permanece intacta.</p><div class="am15-hero-pills">{chips}</div></div>', unsafe_allow_html=True)


def opportunity_matrix(opps: List[Dict[str, Any]]):
    if not opps:
        return None
    import plotly.graph_objects as go
    xs=[float(x.get("Custo/un Δ (%)",0)) for x in opps]
    ys=[float(x.get("Throughput Δ (%)",0)) for x in opps]
    sla=[float(x.get("SLA Δ (p.p.)",0)) for x in opps]
    scores=[float(x.get("Score de oportunidade",0)) for x in opps]
    sizes=[max(12, min(34, 13 + max(0,s)*.16)) for s in scores]
    labels=[x.get("Ação","") for x in opps]
    fig=go.Figure(go.Scatter(
        x=xs,y=ys,mode="markers",text=labels,
        marker=dict(size=sizes,color=sla,colorscale=[[0,"#9AA6A2"],[.5,"#4CA9A0"],[1,"#FF6523"]],showscale=True,colorbar=dict(title="Δ SLA",thickness=10),line=dict(width=1,color="#F7F5F0")),
        customdata=list(zip(scores,sla)),
        hovertemplate="<b>%{text}</b><br>Δ custo/un %{x:+.1f}%<br>Δ throughput %{y:+.1f}%<br>Score %{customdata[0]:.1f}<br>Δ SLA %{customdata[1]:+.1f} p.p.<extra></extra>"
    ))
    xmin=min(xs+[0]); xmax=max(xs+[0]); ymin=min(ys+[0]); ymax=max(ys+[0])
    pad_x=max(3,(xmax-xmin)*.08); pad_y=max(3,(ymax-ymin)*.08)
    # Decision quadrants: visually encode the management interpretation instead of leaving a generic scatter.
    fig.add_shape(type="rect",x0=xmin-pad_x,x1=0,y0=0,y1=ymax+pad_y,fillcolor="rgba(61,157,146,.065)",line_width=0,layer="below")
    fig.add_shape(type="rect",x0=0,x1=xmax+pad_x,y0=0,y1=ymax+pad_y,fillcolor="rgba(108,124,120,.035)",line_width=0,layer="below")
    fig.add_shape(type="rect",x0=xmin-pad_x,x1=0,y0=ymin-pad_y,y1=0,fillcolor="rgba(187,197,192,.035)",line_width=0,layer="below")
    fig.add_shape(type="rect",x0=0,x1=xmax+pad_x,y0=ymin-pad_y,y1=0,fillcolor="rgba(245,102,44,.05)",line_width=0,layer="below")
    fig.add_hline(y=0,line_width=1,line_dash="dot",line_color="#AEB8B3")
    fig.add_vline(x=0,line_width=1,line_dash="dot",line_color="#AEB8B3")
    fig.add_annotation(x=xmin-pad_x*.6,y=ymax+pad_y*.5,text="QUICK WINS",showarrow=False,xanchor="left",font=dict(size=9,color="#2F7D68"))
    fig.add_annotation(x=xmax+pad_x*.6,y=ymax+pad_y*.5,text="STRATEGIC BETS",showarrow=False,xanchor="right",font=dict(size=9,color="#687570"))
    fig.add_annotation(x=xmax+pad_x*.6,y=ymin-pad_y*.4,text="AVOID",showarrow=False,xanchor="right",font=dict(size=9,color="#B9542B"))
    fig.update_layout(height=430,margin=dict(l=25,r=25,t=34,b=25),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#FCFDFB",xaxis=dict(title="Δ custo por unidade (%)  ← melhor",gridcolor="#E1E6E2",zeroline=False),yaxis=dict(title="Δ throughput (%)",gridcolor="#E1E6E2",zeroline=False),hovermode="closest",font=dict(family="Aptos, Segoe UI, sans-serif",color="#66736E",size=11))
    return fig


def stress_landscape(stress_result: Dict[str, Any]):
    runs=stress_result.get("runs",[])
    if not runs:
        return None
    import plotly.graph_objects as go
    x=[float(r.get("Makespan",0)) for r in runs]
    y=[float(r.get("SLA",0)) for r in runs]
    c=[float(r.get("Demanda x",1)) for r in runs]
    size=[max(10,min(28,10+float(r.get("Parada (h)",0))*2.3+float(r.get("Ausências",0))*3)) for r in runs]
    labels=[f"Run {r.get('Run','')} · {r.get('Posto afetado','')}" for r in runs]
    fig=go.Figure(go.Scatter(x=x,y=y,mode="markers",text=labels,marker=dict(size=size,color=c,colorscale=[[0,"#4CA9A0"],[.55,"#E8A55F"],[1,"#FF6523"]],showscale=True,colorbar=dict(title="Demanda ×",thickness=10),opacity=.84,line=dict(width=1,color="#F7F5F0")),hovertemplate="<b>%{text}</b><br>Makespan %{x:.1f} h<br>SLA %{y:.0f}%<extra></extra>"))
    fig.add_hrect(y0=80,y1=105,fillcolor="rgba(47,125,104,.06)",line_width=0,annotation_text="zona operacional",annotation_position="top left")
    fig.add_hrect(y0=0,y1=80,fillcolor="rgba(255,101,35,.045)",line_width=0,annotation_text="zona de ruptura",annotation_position="bottom left")
    fig.add_hline(y=80,line_dash="dash",line_color="#7C8985")
    fig.update_layout(height=420,margin=dict(l=25,r=25,t=35,b=25),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(247,245,240,.4)",xaxis_title="Makespan (h)",yaxis_title="SLA (%)",yaxis_range=[0,105],font=dict(family="Aptos, Segoe UI, sans-serif",color="#66736E",size=11),xaxis=dict(title="Makespan (h)",gridcolor="#E1E6E2",zeroline=False),yaxis=dict(title="SLA (%)",range=[0,105],gridcolor="#E1E6E2",zeroline=False))
    return fig


def route_cards(rows: List[Dict[str, Any]], limit: int = 3) -> None:
    if not rows:
        return
    blocks=[]
    for i,row in enumerate(rows[:limit],1):
        hit = str(row.get("Atinge meta","")).lower() in {"sim","yes","true"}
        blocks.append(f'''<div class="am15-deck-card {'primary' if i==1 else ''}"><div class="mini">{'META' if hit else 'ROTA'}</div><div class="ey">Rota {i:02d}</div><b>{_e(row.get('Cenário','Alternativa'))}</b><p>{float(row.get('Throughput',0)):.2f} un/h · SLA {float(row.get('SLA',0)):.0f}% · R$ {float(row.get('Custo/un',0)):.2f}/un.<br>Implantação estimada R$ {float(row.get('Investimento estimado',0)):,.0f}</p></div>''')
    st.markdown('<div class="am15-deck" style="grid-template-columns:repeat(3,1fr)">'+''.join(blocks)+'</div>', unsafe_allow_html=True)
