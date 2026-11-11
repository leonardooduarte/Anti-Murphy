from __future__ import annotations
import html
from typing import Any, Dict, List
import streamlit as st
import streamlit.components.v1 as components


def _e(x): return html.escape(str(x))

def inject_v14_css():
    st.markdown(r'''
<style>
:root{
 --am-bg:#F1EEE7;--am-surface:#FBFAF6;--am-surface2:#F6F3EC;--am-ink:#172327;--am-muted:#687370;
 --am-line:#D8D1C6;--am-line-strong:#C8BFB2;--am-orange:#FF641E;--am-orange-soft:#FFF0E7;
 --am-teal:#45A39A;--am-green:#2F806A;--am-red:#BD4E41;--am-dark:#142024;--am-dark2:#1A292D;
 --am-radius-sm:10px;--am-radius:14px;--am-radius-lg:20px;
}
.stApp{background:
 radial-gradient(circle at 78% -12%,rgba(255,100,30,.055),transparent 31%),
 linear-gradient(rgba(23,35,39,.012) 1px,transparent 1px),linear-gradient(90deg,rgba(23,35,39,.012) 1px,transparent 1px),var(--am-bg)!important;
 background-size:auto,56px 56px,56px 56px,auto!important;}
.block-container{max-width:1540px!important;padding:1.15rem 1.6rem 4rem!important}
.am-shell{border-radius:18px!important;margin-bottom:10px!important;box-shadow:0 8px 26px rgba(23,35,39,.045)!important;background:rgba(251,250,246,.9)!important}
.am-topbar{grid-template-columns:220px 1fr auto!important;padding:12px 16px 7px!important;gap:22px!important;min-height:68px}
.am-topbar-logo{width:205px!important}.am-topbar-copy{padding-left:22px!important}.am-sub{font-size:.75rem!important;margin-top:3px!important;line-height:1.35!important}.am-kicker{font-size:.56rem!important}.am-context{padding:0 16px 10px!important;gap:6px!important}.am-chip{font-size:.58rem!important;padding:3px 8px!important}
.am-page-title{font-size:1.72rem!important;margin:15px 0 3px!important}.am-page-sub{font-size:.78rem!important;margin-bottom:16px!important}
.am-card{border-radius:14px!important;min-height:88px!important;padding:13px 15px!important;box-shadow:0 8px 24px rgba(23,35,39,.04)!important;background:rgba(251,250,246,.96)!important}
.am-card:hover{transform:translateY(-2px)!important;box-shadow:0 12px 28px rgba(23,35,39,.07)!important}.am-card .val{font-size:1.42rem!important;margin-top:8px!important}.am-card .hint{font-size:.63rem!important;margin-top:6px!important}
/* Make Streamlit controls feel like a product shell */
.stButton>button,.stDownloadButton>button{min-height:40px!important;border-radius:11px!important;font-weight:650!important;box-shadow:none!important;transition:.18s ease!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px)!important;border-color:#BEB4A6!important}
.stButton>button[kind="primary"]{background:linear-gradient(180deg,#1B2B2F,#142024)!important;border:1px solid #142024!important;color:#F7F7F3!important;position:relative;overflow:hidden}
.stButton>button[kind="primary"]:after{content:"";position:absolute;left:10px;right:10px;bottom:3px;height:2px;background:linear-gradient(90deg,var(--am-orange),#FF9B68);border-radius:999px}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{border-radius:10px!important;background:rgba(251,250,246,.96)!important}
[data-testid="stDataFrame"]{border:1px solid var(--am-line)!important;border-radius:14px!important;overflow:hidden!important}
/* primary grouped navigation */
.am-nav-label{font-size:.55rem;letter-spacing:.13em;text-transform:uppercase;color:#8A928F;font-weight:800;margin:5px 2px 6px}
.am-subnav{display:flex;align-items:center;gap:7px;margin:-1px 0 14px;padding:7px;border:1px solid var(--am-line);background:rgba(251,250,246,.72);border-radius:13px}
.am-subnav-note{margin-left:auto;font-size:.64rem;color:#87908D;padding-right:8px}
/* compact tabs */
.stTabs [data-baseweb="tab-list"]{gap:3px!important;border-bottom:1px solid var(--am-line)!important}.stTabs [data-baseweb="tab"]{height:37px!important;padding:0 11px!important;font-size:.72rem!important;border-radius:9px 9px 0 0!important}.stTabs [aria-selected="true"]{background:#19282C!important;color:#F7F7F3!important}
/* overview composition */
.am-overview-hero{display:grid;grid-template-columns:minmax(0,2.25fr) minmax(300px,.75fr);gap:14px;align-items:stretch;margin-top:12px}
.am-rail{background:linear-gradient(145deg,#162326,#1B2A2E);border:1px solid #2C3B3E;border-radius:20px;padding:18px;color:#EAF0ED;position:relative;overflow:hidden;min-height:100%}
.am-rail:after{content:"";position:absolute;width:220px;height:220px;border-radius:50%;right:-80px;bottom:-100px;background:radial-gradient(circle,rgba(255,100,30,.12),transparent 68%)}
.am-rail-k{font-size:.56rem;letter-spacing:.16em;text-transform:uppercase;color:#FF8B52;font-weight:850}.am-rail h3{font-size:1.2rem!important;color:#F4F6F3!important;margin:8px 0 4px!important;letter-spacing:-.025em}.am-rail p{font-size:.72rem!important;line-height:1.5;color:#8EA09B!important;margin:0 0 14px!important}
.am-rail-item{border-top:1px solid #2C3B3E;padding:11px 0;position:relative;z-index:1}.am-rail-item span{display:block;font-size:.54rem;color:#71837E;letter-spacing:.11em;text-transform:uppercase;font-weight:800}.am-rail-item b{display:block;font-size:.88rem;color:#EDF2EF;margin-top:4px}.am-rail-item em{display:block;font-style:normal;font-size:.62rem;color:#8EA09B;margin-top:3px}.am-rail-action{margin-top:12px;border:1px solid #3A4B4F;border-radius:11px;padding:10px 11px;background:#1D2D31;font-size:.68rem;color:#C8D3D0;position:relative;z-index:1}.am-rail-action strong{color:#FF8B52}
/* insight strip */
.am-insight-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:13px 0 6px}.am-insight-card{background:rgba(251,250,246,.88);border:1px solid var(--am-line);border-radius:14px;padding:13px 14px;min-height:95px}.am-insight-card .ey{font-size:.54rem;letter-spacing:.14em;text-transform:uppercase;font-weight:850;color:#8A928F}.am-insight-card b{display:block;font-size:.88rem;color:var(--am-ink);margin:7px 0 4px}.am-insight-card p{font-size:.67rem;line-height:1.42;margin:0!important;color:#78827F!important}
/* compare */
.am-compare-head{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:8px 0 16px}.am-delta-card{border:1px solid var(--am-line);border-radius:14px;background:var(--am-surface);padding:13px}.am-delta-card span{font-size:.54rem;letter-spacing:.12em;text-transform:uppercase;color:#89918F;font-weight:800}.am-delta-values{display:flex;align-items:baseline;gap:8px;margin-top:8px}.am-delta-values .from{color:#8B9491;font-size:.8rem}.am-delta-values .arrow{color:#B4BBB8}.am-delta-values .to{font-size:1.25rem;font-weight:800;color:var(--am-ink)}.am-delta-card small{display:block;margin-top:6px;font-size:.62rem}.pos{color:var(--am-green)!important}.neg{color:var(--am-red)!important}.neutral{color:#7C8683!important}
.am-neutral-state{border:1px solid var(--am-line);border-radius:18px;background:linear-gradient(135deg,#FBFAF6,#F5F1E9);padding:28px;display:grid;grid-template-columns:auto 1fr;gap:17px;align-items:center;margin:12px 0 16px}.am-neutral-icon{width:52px;height:52px;border-radius:14px;background:#E9E5DC;display:flex;align-items:center;justify-content:center;font-size:1.5rem;color:#61706C}.am-neutral-state h3{font-size:1.2rem!important;margin:0 0 5px!important}.am-neutral-state p{font-size:.75rem!important;margin:0!important;max-width:720px}
/* section heading */
.am-section-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin:20px 0 9px}.am-section-head h3{font-size:1.18rem!important;margin:0!important}.am-section-head p{font-size:.67rem!important;margin:0!important;color:#88908D!important}
/* reduce empty vertical gaps */
.element-container{margin-bottom:.15rem!important}.section-rule{margin:14px 0!important}
@media(max-width:1050px){.am-overview-hero{grid-template-columns:1fr}.am-insight-grid{grid-template-columns:1fr}.am-compare-head{grid-template-columns:1fr 1fr}.am-topbar{grid-template-columns:1fr!important}.am-topbar-copy{border-left:0!important;padding-left:0!important}}
</style>
''', unsafe_allow_html=True)


def section_header(title: str, helper: str = ""):
    st.markdown(f'<div class="am-section-head"><h3>{_e(title)}</h3><p>{_e(helper)}</p></div>', unsafe_allow_html=True)


def decision_rail(base: Dict[str, Any], resilience: Dict[str, Any], recommendations: List[Dict[str, Any]]):
    bn = base.get("bottleneck", "-")
    row = next((x for x in base.get("stations", []) if x.get("Posto") == bn), {})
    rec = recommendations[0] if recommendations else {}
    title = rec.get("title") or rec.get("Título") or rec.get("recommendation") or rec.get("action") or "Explorar capacidade no gargalo"
    reason = rec.get("reason") or rec.get("detail") or rec.get("why") or "Use o Murphy Lab para validar a intervenção antes de alterar a operação."
    html_doc = f'''
    <div class="am-rail">
      <div class="am-rail-k">Decision Intelligence</div>
      <h3>O que merece atenção agora</h3>
      <p>Diagnóstico compacto do cenário-base e próximo experimento sugerido.</p>
      <div class="am-rail-item"><span>Restrição atual</span><b>{_e(bn)} · {_e(row.get('Nome',''))}</b><em>fila máx. {row.get('Fila máx.',0)} · espera {float(row.get('Espera média (min)',0)):.1f} min</em></div>
      <div class="am-rail-item"><span>Resiliência</span><b>{float(resilience.get('score',0)):.0f}/100 · {_e(resilience.get('band',''))}</b><em>sensibilidade operacional do modelo</em></div>
      <div class="am-rail-item"><span>Próximo teste sugerido</span><b>{_e(title)}</b><em>{_e(reason)}</em></div>
      <div class="am-rail-action"><strong>Princípio:</strong> diagnosticar → experimentar → comparar → decidir.</div>
    </div>'''
    st.markdown(html_doc, unsafe_allow_html=True)


def insight_strip(base: Dict[str, Any], recommendations: List[Dict[str, Any]], resilience: Dict[str, Any]):
    bn = base.get("bottleneck", "-")
    row = next((x for x in base.get("stations", []) if x.get("Posto") == bn), {})
    rec = recommendations[0] if recommendations else {}
    rec_title = rec.get("title") or rec.get("Título") or rec.get("action") or "Teste capacidade no gargalo"
    sla=float(base.get('sla_pct',0))
    cost=float(base.get('unit_cost',0))
    st.markdown(f'''
    <div class="am-insight-grid">
      <div class="am-insight-card"><div class="ey">Risco dominante</div><b>{_e(bn)} concentra a pressão</b><p>Fila máxima de {row.get('Fila máx.',0)} e espera média de {float(row.get('Espera média (min)',0)):.1f} min.</p></div>
      <div class="am-insight-card"><div class="ey">Próximo experimento</div><b>{_e(rec_title)}</b><p>Valide a intervenção no Murphy Lab e acompanhe a migração da restrição.</p></div>
      <div class="am-insight-card"><div class="ey">Leitura executiva</div><b>SLA {sla:.0f}% · R$ {cost:.2f}/un</b><p>Resiliência {float(resilience.get('score',0)):.0f}/100. Priorize decisões que melhorem prazo sem deteriorar custo.</p></div>
    </div>''', unsafe_allow_html=True)


def compare_summary(base: Dict[str, Any], alt: Dict[str, Any], delta: Dict[str, Any]):
    defs=[
        ("Throughput",f"{base.get('throughput_h',0):.2f}",f"{alt.get('throughput_h',0):.2f}",float(delta.get('throughput_pct',0)),"%"),
        ("SLA",f"{base.get('sla_pct',0):.0f}%",f"{alt.get('sla_pct',0):.0f}%",float(delta.get('sla_pp',0))," p.p."),
        ("Custo / un",f"R$ {base.get('unit_cost',0):.2f}",f"R$ {alt.get('unit_cost',0):.2f}",float(delta.get('unit_cost_pct',0)),"%"),
        ("Makespan",f"{base.get('makespan_h',0):.1f}h",f"{alt.get('makespan_h',0):.1f}h",float(delta.get('makespan_pct',0)),"%"),
    ]
    cards=[]
    for i,(lab,fr,to,d,suff) in enumerate(defs):
        beneficial = d>0 if lab in ("Throughput","SLA") else d<0
        cls = "pos" if abs(d)>.01 and beneficial else ("neg" if abs(d)>.01 else "neutral")
        cards.append(f'<div class="am-delta-card"><span>{lab}</span><div class="am-delta-values"><div class="from">{fr}</div><div class="arrow">→</div><div class="to">{to}</div></div><small class="{cls}">{d:+.1f}{suff}</small></div>')
    st.markdown('<div class="am-compare-head">'+''.join(cards)+'</div>', unsafe_allow_html=True)


def neutral_compare_state():
    st.markdown('''<div class="am-neutral-state"><div class="am-neutral-icon">↔</div><div><h3>Nenhum impacto detectado</h3><p>O experimento reproduz o cenário-base. Altere capacidade, demanda, regra de despacho, ausência ou perturbação para gerar uma comparação útil.</p></div></div>''', unsafe_allow_html=True)
