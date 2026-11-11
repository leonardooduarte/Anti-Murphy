from __future__ import annotations
import html
from typing import Any, Dict, List
import streamlit as st


def _e(v: Any) -> str:
    return html.escape(str(v))


def inject_v17_css() -> None:
    st.markdown(r'''
<style>
/* ============================================================
   ANTI-MURPHY V17 · DECISION COMMAND
   Refinement layer: premium density, clearer hierarchy, quieter UI.
   ============================================================ */
:root{
  --v17-bg:#EEF1EE; --v17-surface:#FCFDFB; --v17-ink:#0C171A;
  --v17-muted:#66736E; --v17-line:#D6DDD8; --v17-line2:#C7D0CA;
  --v17-rail:#091417; --v17-rail2:#102025; --v17-orange:#F5662C;
  --v17-teal:#3D9D92; --v17-green:#2E7865; --v17-red:#B94C43;
  --v17-radius:10px;
}
html,body,[class*="css"]{font-family:"Aptos","Segoe UI Variable",Inter,"Segoe UI",system-ui,sans-serif!important;font-feature-settings:"tnum" 1,"ss01" 1}
.stApp{background:
 radial-gradient(circle at 88% -5%,rgba(245,102,44,.055),transparent 24%),
 radial-gradient(circle at 18% 0%,rgba(61,157,146,.04),transparent 22%),
 var(--v17-bg)!important}
.block-container{max-width:1840px!important;padding:1rem 1.35rem 3.2rem!important}
/* tighter product rail */
.st-key-am16_navrail{background:linear-gradient(180deg,#081316,#0D1B1F 58%,#091518)!important;border-color:#1C3035!important;border-radius:12px!important;padding:9px 8px 12px!important;box-shadow:0 22px 55px rgba(7,18,21,.16)!important}
.st-key-am16_navrail .stButton>button{font-size:.75rem!important;min-height:40px!important;border-radius:7px!important;padding:0 11px!important}
.st-key-am16_navrail .stButton>button[kind="primary"]{background:#13262B!important;box-shadow:inset 2px 0 0 var(--v17-orange)!important}
.am16-side-brand img{width:164px!important}.am16-side-brand .version{color:#647A74!important}.am16-side-sec{color:#536A65!important;font-size:.46rem!important}
.am16-side-state{background:#0E1C20!important;border-color:#23363B!important}.am16-side-footer{color:#435B56!important}
/* product top line */
.am16-topbar{border-radius:9px!important;padding:9px 12px 9px 14px!important;margin-bottom:10px!important;background:rgba(252,253,251,.92)!important;box-shadow:0 5px 18px rgba(12,23,26,.028)!important}
.am16-top-title{font-size:.92rem!important}.am16-breadcrumb{font-size:.49rem!important}.am16-status-chip{font-size:.54rem!important;padding:4px 8px!important}
/* stronger editorial heads */
.am16-pagehead{margin:18px 0 13px!important;grid-template-columns:minmax(0,1fr) minmax(260px,.36fr)!important}.am16-pagehead h1{font-size:2.08rem!important;letter-spacing:-.058em!important}.am16-pagehead .copy{font-size:.65rem!important}.am16-pagehead .ey{font-size:.49rem!important}
/* cards less rounded, less template-like */
.am16-metric-rail{border-radius:9px!important;box-shadow:none!important}.am16-metric{min-height:76px!important;padding:10px 12px 9px!important}.am16-metric .value{font-size:1.34rem!important}.am16-context{border-radius:10px!important;box-shadow:0 18px 44px rgba(10,22,25,.10)!important}
.am16-signals{gap:7px!important}.am16-signal{border-radius:9px!important}
.am-cinematic,.am-replay-shell,.am-opportunity-scan,.am-prop-shell,.am-copilot-shell{border-radius:10px!important}
/* section typography */
h3{font-size:1rem!important;font-weight:760!important;margin:1.15rem 0 .42rem!important}p{line-height:1.5!important}
/* form polish */
main .stButton>button,main .stDownloadButton>button{border-radius:7px!important;min-height:38px!important;font-size:.70rem!important}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{border-radius:7px!important;background:#FCFDFB!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border-radius:8px!important}
[data-testid="stExpander"]{border-radius:8px!important}
/* native labels slightly stronger */
label,[data-testid="stWidgetLabel"] p{font-size:.68rem!important;color:#687570!important;font-weight:610!important}
/* plotly containers look embedded */
[data-testid="stPlotlyChart"]{background:rgba(252,253,251,.42);border-radius:9px}
/* new V17 surfaces */
.v17-command{display:grid;grid-template-columns:1.4fr .82fr .82fr;gap:1px;background:var(--v17-line);border:1px solid var(--v17-line);border-radius:9px;overflow:hidden;margin:0 0 10px}
.v17-command>div{background:#FCFDFB;padding:11px 13px;min-height:65px}.v17-command .ey{font-size:.45rem;letter-spacing:.16em;text-transform:uppercase;color:#89948F;font-weight:850}.v17-command .main{font-size:.91rem;color:#142225;font-weight:760;margin-top:5px;letter-spacing:-.025em}.v17-command .sub{font-size:.55rem;color:#8B9692;margin-top:3px;line-height:1.4}.v17-command .accent{color:var(--v17-orange)}
.v17-inspector{background:#FCFDFB;border:1px solid var(--v17-line);border-radius:9px;padding:13px 14px}.v17-inspector-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}.v17-inspector .ey{font-size:.46rem;text-transform:uppercase;letter-spacing:.16em;color:#87938E;font-weight:850}.v17-inspector h3{font-size:1rem!important;margin:5px 0 2px!important}.v17-state{font-size:.48rem;text-transform:uppercase;letter-spacing:.1em;border:1px solid #D9DFDB;border-radius:999px;padding:4px 7px;color:#63716C}.v17-state.hot{color:#C45425;border-color:#E7B29A;background:#FFF5F0}.v17-inspector-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#E0E5E1;border:1px solid #E0E5E1;border-radius:7px;overflow:hidden;margin-top:10px}.v17-inspector-grid div{background:#F8FAF7;padding:9px}.v17-inspector-grid span{display:block;font-size:.43rem;text-transform:uppercase;letter-spacing:.11em;color:#8A9591}.v17-inspector-grid b{display:block;font-size:.82rem;color:#1A282B;margin-top:3px}.v17-inspector-note{font-size:.58rem;color:#74817C;margin-top:9px;line-height:1.45}
.v17-verdict{border:1px solid var(--v17-line);background:#FCFDFB;border-radius:9px;padding:14px 15px;margin:7px 0 12px}.v17-verdict-grid{display:grid;grid-template-columns:.8fr 1.2fr 1fr;gap:14px;align-items:center}.v17-verdict .score{font-size:2rem;font-weight:790;letter-spacing:-.06em;color:#172528}.v17-verdict .score span{font-size:.7rem;color:#8A9691;font-weight:650}.v17-verdict .ey{font-size:.45rem;letter-spacing:.15em;text-transform:uppercase;color:#8A9691;font-weight:850}.v17-verdict .title{font-size:.92rem;font-weight:760;color:#172528;margin-top:4px}.v17-verdict .copy{font-size:.59rem;color:#72807B;line-height:1.5;margin-top:4px}.v17-verdict .bar{height:5px;border-radius:999px;background:#E2E7E3;overflow:hidden;margin-top:7px}.v17-verdict .bar i{display:block;height:100%;background:linear-gradient(90deg,var(--v17-teal),var(--v17-orange));border-radius:999px}
.v17-quality{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:8px 0 12px}.v17-quality>div{background:#FCFDFB;border:1px solid var(--v17-line);border-radius:8px;padding:10px 11px}.v17-quality .k{font-size:.44rem;letter-spacing:.13em;text-transform:uppercase;color:#8A9691;font-weight:820}.v17-quality .v{font-size:.86rem;font-weight:740;color:#182629;margin-top:4px}.v17-quality .m{font-size:.52rem;color:#8B9692;margin-top:2px}
.v17-quadrants{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:6px 0 10px}.v17-q{border:1px solid var(--v17-line);border-radius:8px;padding:9px 10px;background:#FCFDFB}.v17-q b{font-size:.62rem;color:#1B292C}.v17-q span{display:block;font-size:.51rem;color:#8A9691;margin-top:2px}.v17-q.quick{border-top:2px solid var(--v17-teal)}.v17-q.strategic{border-top:2px solid #6C7C78}.v17-q.low{border-top:2px solid #C3CBC7}.v17-q.avoid{border-top:2px solid var(--v17-orange)}
.v17-model-cards{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin:8px 0 12px}.v17-model-card{background:#FCFDFB;border:1px solid var(--v17-line);border-radius:8px;padding:11px;position:relative}.v17-model-card.hot{border-color:#E7A98F}.v17-model-card .id{font-size:.44rem;letter-spacing:.14em;text-transform:uppercase;color:var(--v17-orange);font-weight:850}.v17-model-card .name{font-size:.73rem;font-weight:740;color:#172528;margin-top:5px}.v17-model-card .meta{font-size:.52rem;color:#7A8782;margin-top:5px;line-height:1.45}.v17-model-card .line{height:3px;background:#E2E7E3;border-radius:999px;margin-top:9px;overflow:hidden}.v17-model-card .line i{display:block;height:100%;background:var(--v17-teal)}
.v17-section-note{display:flex;align-items:center;justify-content:space-between;gap:12px;border-bottom:1px solid var(--v17-line);padding:0 0 7px;margin:16px 0 8px}.v17-section-note b{font-size:.79rem;color:#172528}.v17-section-note span{font-size:.54rem;color:#8B9692}
@media(max-width:1200px){.v17-command{grid-template-columns:1fr}.v17-model-cards{grid-template-columns:repeat(2,1fr)}.v17-verdict-grid{grid-template-columns:1fr}.v17-quality,.v17-quadrants{grid-template-columns:1fr 1fr}}
</style>
''', unsafe_allow_html=True)


def command_summary(base: Dict[str, Any], resilience: Dict[str, Any], recs: List[Dict[str, Any]]) -> None:
    bn = base.get('bottleneck','—')
    rec = recs[0].get('title') if recs else 'Executar nova exploração contrafactual'
    late = int(base.get('late_orders',0))
    risk = f"{late} OPs atrasadas · resiliência {float(resilience.get('score',0)):.0f}/100"
    st.markdown(f'''<div class="v17-command">
      <div><div class="ey">Current constraint</div><div class="main">Pressão concentrada em <span class="accent">{_e(bn)}</span></div><div class="sub">O cockpit prioriza a principal restrição do modelo neste instante.</div></div>
      <div><div class="ey">Risk posture</div><div class="main">{_e(risk)}</div><div class="sub">Prazo, filas e robustez combinados numa leitura curta.</div></div>
      <div><div class="ey">Next best test</div><div class="main">{_e(rec)}</div><div class="sub">Sugestão heurística; a decisão permanece com o usuário.</div></div>
    </div>''', unsafe_allow_html=True)


def station_inspector(row: Dict[str, Any], is_bottleneck: bool=False) -> None:
    name=row.get('Nome',row.get('Posto','Posto')); sid=row.get('Posto','—')
    util=float(row.get('Utilização máquina (%)',0)); q=row.get('Fila máx.',0); wait=float(row.get('Espera média (min)',0)); labor=float(row.get('Utilização mão de obra (%)',0))
    state='CONSTRAINT' if is_bottleneck else ('LOADED' if max(util,labor)>=80 else 'STABLE')
    cls='hot' if is_bottleneck else ''
    st.markdown(f'''<div class="v17-inspector"><div class="v17-inspector-head"><div><div class="ey">Station focus · { _e(sid) }</div><h3>{_e(name)}</h3></div><span class="v17-state {cls}">{state}</span></div>
      <div class="v17-inspector-grid"><div><span>machine load</span><b>{util:.1f}%</b></div><div><span>labor load</span><b>{labor:.1f}%</b></div><div><span>max queue</span><b>{q}</b></div><div><span>avg wait</span><b>{wait:.1f} min</b></div></div>
      <div class="v17-inspector-note">Leitura operacional do posto selecionado. Use o Scenario Studio para testar capacidade, mão de obra, despacho ou perturbações sobre este ponto.</div></div>''', unsafe_allow_html=True)


def decision_verdict(base: Dict[str, Any], alt: Dict[str, Any], delta: Dict[str, Any]) -> None:
    tp=float(delta.get('throughput_pct',0)); sla=float(delta.get('sla_pp',0)); cost=float(delta.get('unit_cost_pct',0)); mk=float(delta.get('makespan_pct',0))
    # 0–100 descriptive decision-quality heuristic; rewards service/flow and lower cost/time.
    score=max(0,min(100,50 + tp*1.0 + sla*.65 - cost*.55 - mk*.45))
    positives=sum([tp>0.3,sla>0.5,cost<-0.3,mk<-0.3]); negatives=sum([tp<-0.3,sla<-0.5,cost>0.3,mk>0.3])
    if positives>=2 and negatives==0: title='Ganho sistêmico consistente'; copy='A intervenção melhora múltiplas dimensões sem trade-off relevante no conjunto observado.'
    elif positives>negatives: title='Trade-off favorável'; copy='Há ganho dominante, mas pelo menos uma dimensão deve ser acompanhada antes de implementar.'
    elif negatives>positives: title='Trade-off desfavorável'; copy='O cenário cria pressão relevante em desempenho, prazo ou custo; vale revisar a intervenção.'
    else: title='Mudança de baixo contraste'; copy='O cenário pouco altera o equilíbrio global ou distribui ganhos e perdas de forma semelhante.'
    st.markdown(f'''<div class="v17-verdict"><div class="v17-verdict-grid"><div><div class="ey">Decision signal</div><div class="score">{score:.0f}<span>/100</span></div><div class="bar"><i style="width:{score:.0f}%"></i></div></div><div><div class="ey">Interpretation</div><div class="title">{_e(title)}</div><div class="copy">{_e(copy)}</div></div><div><div class="ey">Constraint migration</div><div class="title">{_e(base.get('bottleneck','—'))} → {_e(alt.get('bottleneck','—'))}</div><div class="copy">A nota é uma heurística transparente de leitura do cenário, não uma recomendação automática.</div></div></div></div>''', unsafe_allow_html=True)


def model_cards(stations: Dict[str, Dict[str, Any]], bottleneck: str|None=None) -> None:
    cards=[]
    for sid,s in stations.items():
        avail=float(s.get('disponibilidade',1))*100; eff=float(s.get('eficiencia_operador',1))*100
        cls=' hot' if sid==bottleneck else ''
        width=max(8,min(100,avail))
        cards.append(f'''<div class="v17-model-card{cls}"><div class="id">{_e(sid)}</div><div class="name">{_e(s.get('nome',sid))}</div><div class="meta">{int(s.get('maquinas',0))} maq. · {int(s.get('operadores',0))} op.<br>disp. {avail:.0f}% · eficiência {eff:.0f}%</div><div class="line"><i style="width:{width:.0f}%"></i></div></div>''')
    st.markdown('<div class="v17-model-cards">'+''.join(cards)+'</div>',unsafe_allow_html=True)


def opportunity_quadrants() -> None:
    st.markdown('''<div class="v17-quadrants"><div class="v17-q quick"><b>Quick wins</b><span>alto impacto · baixo custo</span></div><div class="v17-q strategic"><b>Strategic bets</b><span>alto impacto · maior investimento</span></div><div class="v17-q low"><b>Low leverage</b><span>baixo retorno marginal</span></div><div class="v17-q avoid"><b>Avoid</b><span>custo alto · impacto desfavorável</span></div></div>''', unsafe_allow_html=True)


def section_note(title: str, note: str) -> None:
    st.markdown(f'<div class="v17-section-note"><b>{_e(title)}</b><span>{_e(note)}</span></div>',unsafe_allow_html=True)
