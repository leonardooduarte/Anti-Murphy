from __future__ import annotations

import html
from typing import Any, Dict, List

import plotly.graph_objects as go
from ui.stat_values import stat_value
import streamlit as st


def _e(v: Any) -> str:
    return html.escape(str(v))


def inject_v21_css() -> None:
    st.markdown(r'''
<style>
/* =====================================================================
   ANTI-MURPHY V21 · OPERATIONAL COMMAND
   Premium industrial workstation: calm canvas, precise hierarchy, motion
   only where it communicates system state.
   ===================================================================== */
:root{
 --v21-bg:#F2F4F2; --v21-paper:#FCFDFC; --v21-paper2:#F7F9F7;
 --v21-ink:#102024; --v21-muted:#66756F; --v21-line:#D6DEDA;
 --v21-dark:#0A181C; --v21-dark2:#102126; --v21-orange:#FF6426;
 --v21-teal:#3FA79B; --v21-green:#26775F; --v21-red:#B64842; --v21-amber:#A96F28;
}
html,body,[class*="css"]{font-family:"Aptos","Segoe UI Variable","Segoe UI",system-ui,sans-serif!important}
.stApp{background:
 radial-gradient(1000px 520px at 100% -10%,rgba(255,100,38,.035),transparent 58%),
 radial-gradient(800px 420px at 28% 0%,rgba(63,167,155,.025),transparent 65%),
 var(--v21-bg)!important;color:var(--v21-ink)!important}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{visibility:hidden!important;height:0!important}
[data-testid="stAppDeployButton"]{display:none!important}
.block-container{max-width:1840px!important;padding:1rem 1.25rem 4rem!important}
h1,h2,h3,h4{font-family:"Aptos Display","Segoe UI Variable Display","Segoe UI",sans-serif!important;color:var(--v21-ink)!important}
.am16-pagehead h1{font-family:"Aptos Display","Segoe UI Variable Display",sans-serif!important;font-weight:720!important;letter-spacing:-.045em!important}
.am16-topbar{background:rgba(252,253,252,.94)!important;border-color:var(--v21-line)!important;backdrop-filter:blur(14px);border-radius:8px!important}
.am16-side-brand .version{color:#80908A!important}.am16-side-state{background:#0E2024!important;border-color:#274148!important}
.am16-nav-active,.am16_navrail [data-testid="stBaseButton-primary"]{box-shadow:inset 2px 0 0 var(--v21-orange)!important}
/* quieter canvas and fewer outlines */
.am15-module-hero,.v17-command,.v17-verdict,.v17-inspector,.v20-station-editor,.v20-state-banner,
.v20-opportunity-detail,.v20-target-warning,.v18-pulse>div,.v18-econ>div,.v18-lens>div{
 background:var(--v21-paper)!important;border-color:var(--v21-line)!important;box-shadow:none!important}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{background:var(--v21-paper)!important;border-color:var(--v21-line)!important}
/* deliberate typography */
.am16-breadcrumb,.am16-pagehead .ey,.am16-workspace-label,.am16-metric .lab,.am16-context .ey,
.v20-stage .n,.am15-module-hero .ey,.v21-ey{font-family:"Cascadia Mono","Consolas",monospace!important;letter-spacing:.13em!important}
.am16-pagehead .copy,.am15-module-hero p,p{font-size:.64rem!important;line-height:1.55!important}
/* workflow ribbon becomes an understated process rail */
.v20-workflow{border-radius:6px!important;background:rgba(252,253,252,.76)!important;margin-bottom:14px!important}
.v20-stage{min-height:43px!important;padding:7px 10px!important}.v20-stage .t{font-size:.63rem!important}.v20-stage .s{font-size:.43rem!important}
/* controls */
main .stButton>button,main .stDownloadButton>button{border-radius:5px!important;transition:transform .16s ease,border-color .16s ease,box-shadow .16s ease!important}
main .stButton>button:hover,main .stDownloadButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 18px rgba(12,30,34,.055)!important}
/* new V21 components */
.v21-confidence{display:grid;grid-template-columns:132px 1fr 1fr 1fr;gap:1px;background:var(--v21-line);border:1px solid var(--v21-line);border-radius:8px;overflow:hidden;margin:7px 0 11px}
.v21-confidence>div{background:var(--v21-paper);padding:11px 12px}.v21-confidence .score{background:var(--v21-dark);color:#F4F7F6}.v21-confidence .ey{font:800 .38rem "Cascadia Mono",monospace;letter-spacing:.12em;color:#8F9D98}.v21-confidence .score .ey{color:#78928B}.v21-confidence .big{font:720 1.28rem "Aptos Display",sans-serif;margin-top:4px}.v21-confidence .score .big{color:#fff}.v21-confidence .meta{font-size:.50rem;color:#77857F;margin-top:3px;line-height:1.35}
.v21-intervention{background:linear-gradient(145deg,#0A181C,#102529);border:1px solid #284248;border-radius:9px;padding:13px;color:#EAF0EE;margin-top:8px;box-shadow:0 16px 34px rgba(5,18,21,.08)}
.v21-intervention .ey{font:800 .38rem "Cascadia Mono",monospace;letter-spacing:.13em;color:#77928B}.v21-intervention .title{font:720 1rem "Aptos Display",sans-serif;margin:5px 0 10px;color:#fff}.v21-intervention .flow{display:grid;grid-template-columns:1fr 48px 1fr;align-items:center;gap:6px}.v21-node{border:1px solid #314A50;border-radius:7px;padding:10px;background:#102126}.v21-node.after{border-color:#CE5B2B;background:#172126}.v21-node .k{font-size:.43rem;color:#82938D;text-transform:uppercase;letter-spacing:.09em}.v21-node b{display:block;margin-top:4px;color:#F2F6F4;font-size:.70rem}.v21-arrow{text-align:center;color:var(--v21-orange);font-size:1.1rem}.v21-tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px}.v21-tag{border:1px solid #385159;border-radius:99px;padding:4px 7px;font-size:.44rem;color:#AFC0BA}.v21-tag.hot{border-color:#B64D27;color:#FF9A72}
.v21-verdict{display:grid;grid-template-columns:1.25fr repeat(3,.75fr);gap:1px;background:var(--v21-line);border:1px solid var(--v21-line);border-radius:8px;overflow:hidden;margin:8px 0 12px}.v21-verdict>div{padding:11px 12px;background:var(--v21-paper)}.v21-verdict .lead{background:var(--v21-dark);color:#fff}.v21-verdict .ey{font:800 .37rem "Cascadia Mono",monospace;letter-spacing:.12em;color:#8A9994}.v21-verdict .headline{font:720 .86rem "Aptos Display",sans-serif;margin-top:4px}.v21-verdict .lead .headline{color:#fff}.v21-verdict .copy{font-size:.49rem;color:#77857F;margin-top:3px}.v21-verdict .lead .copy{color:#AAB7B3}.v21-verdict .good{color:var(--v21-green)}.v21-verdict .bad{color:var(--v21-red)}
.v21-mc{display:grid;grid-template-columns:1.05fr repeat(4,1fr);gap:1px;background:var(--v21-line);border:1px solid var(--v21-line);border-radius:8px;overflow:hidden;margin:7px 0 10px}.v21-mc>div{background:var(--v21-paper);padding:10px 11px}.v21-mc .lead{background:#102126;color:#F5F8F7}.v21-mc .k{font:800 .36rem "Cascadia Mono",monospace;letter-spacing:.12em;color:#8B9994}.v21-mc .v{font-weight:720;font-size:.79rem;margin-top:4px}.v21-mc .s{font-size:.45rem;color:#788680;margin-top:2px}.v21-mc .lead .s{color:#9DACA7}
.v21-frontier{border:1px solid var(--v21-line);border-radius:8px;background:var(--v21-paper);padding:11px 12px;margin-top:8px}.v21-frontier .head{display:flex;justify-content:space-between;align-items:end;margin-bottom:5px}.v21-frontier .head b{font-size:.76rem}.v21-frontier .head span{font-size:.47rem;color:#71807B}
.v21-section-divider{height:1px;background:linear-gradient(90deg,var(--v21-orange) 0 42px,var(--v21-line) 42px 100%);margin:13px 0}
@media(max-width:1200px){.v21-confidence,.v21-verdict,.v21-mc{grid-template-columns:1fr 1fr}.v21-confidence .score,.v21-verdict .lead,.v21-mc .lead{grid-column:1/-1}}
@media(max-width:760px){.v21-confidence,.v21-verdict,.v21-mc{grid-template-columns:1fr}.v21-intervention .flow{grid-template-columns:1fr}.v21-arrow{transform:rotate(90deg)}}
</style>
''', unsafe_allow_html=True)


def model_confidence_panel(info: Dict[str, Any]) -> None:
    score=int(info.get('score',0)); band=str(info.get('band','-')); missing=info.get('missing',[])
    missing_txt='Nenhuma lacuna estrutural detectada.' if not missing else 'Falta: ' + ', '.join(map(str,missing[:3]))
    st.markdown(f'''<div class="v21-confidence">
      <div class="score"><div class="ey">MODEL CONFIDENCE</div><div class="big">{score}/100</div><div class="meta">{_e(band)} · completude heurística</div></div>
      <div><div class="ey">DATA FOUNDATION</div><div class="big">{_e('READY' if score>=85 else 'REVIEW')}</div><div class="meta">{_e(missing_txt)}</div></div>
      <div><div class="ey">STRUCTURE</div><div class="big">{sum(1 for _,ok,_ in info.get('checks',[]) if ok)}/{len(info.get('checks',[]))}</div><div class="meta">checagens de consistência atendidas</div></div>
      <div><div class="ey">MODEL USE</div><div class="big">Decision Twin</div><div class="meta">score mede o cadastro; não valida aderência ao chão de fábrica.</div></div>
    </div>''',unsafe_allow_html=True)


def scenario_intervention_map(station: str, name: str, base_station: Dict[str, Any], workers_delta: int, machines_delta: int, demand: float, rule: str, event: str, absent: int) -> None:
    bw=int(base_station.get('operadores',0)); bm=int(base_station.get('maquinas',1))
    aw=max(0,bw+int(workers_delta)); am=max(1,bm+int(machines_delta))
    tags=[f'Demanda {demand:.1f}×', f'Dispatch {rule}']
    if event and event.lower() not in {'sem perturbação','none'}: tags.append(event)
    if absent: tags.append(f'{absent} ausência(s)')
    if workers_delta: tags.append(f'{workers_delta:+d} operador(es)')
    if machines_delta: tags.append(f'{machines_delta:+d} máquina(s)')
    tags_html=''.join(f'<span class="v21-tag {"hot" if ("ausência" in t.lower() or "pertur" in t.lower()) else ""}">{_e(t)}</span>' for t in tags)
    st.markdown(f'''<div class="v21-intervention"><div class="ey">INTERVENTION PREVIEW · {_e(station)}</div><div class="title">Veja a mudança antes de simular.</div>
      <div class="flow"><div class="v21-node"><div class="k">BASELINE</div><b>{bm} máq. · {bw} op.</b></div><div class="v21-arrow">→</div><div class="v21-node after"><div class="k">DECISION WORLD</div><b>{am} máq. · {aw} op.</b></div></div><div class="v21-tags">{tags_html}</div></div>''',unsafe_allow_html=True)


def decision_narrative(base: Dict[str, Any], alt: Dict[str, Any], d: Dict[str, Any]) -> None:
    tp=float(d.get('throughput_pct',0)); sla=float(d.get('sla_pp',0)); cost=float(d.get('unit_cost_pct',0)); mk=float(d.get('makespan_pct',0))
    positives=sum([tp>1, sla>1, cost<-1, mk<-1]); negatives=sum([tp<-1, sla<-1, cost>1, mk>1])
    if negatives>=2 and negatives>positives:
        title='Trade-off desfavorável no conjunto de métricas'
        copy='A alternativa cria perdas relevantes em mais de uma dimensão; trate-a como evidência para refinar a intervenção, não como resultado final.'
    elif positives>=2 and positives>negatives:
        title='Ganho multidimensional no cenário simulado'
        copy='Mais de uma dimensão melhora ao mesmo tempo. Ainda vale verificar robustez, dispersão e custo de implantação antes da decisão real.'
    else:
        title='Resultado misto: o cenário troca ganhos por perdas'
        copy='A leitura correta é de trade-off. Use os vetores abaixo para entender o que melhora, o que piora e onde o gargalo permanece.'
    def cell(k,v,good):
        return f'<div><div class="ey">{k}</div><div class="headline {"good" if good else "bad"}">{v}</div></div>'
    st.markdown(f'''<div class="v21-verdict"><div class="lead"><div class="ey">DECISION NARRATIVE</div><div class="headline">{_e(title)}</div><div class="copy">{_e(copy)}</div></div>
      {cell('FLOW',f'{tp:+.1f}%',tp>=0)}{cell('SERVICE',f'{sla:+.1f} p.p.',sla>=0)}{cell('TIME',f'{mk:+.1f}%',mk<=0)}</div>''',unsafe_allow_html=True)


def monte_carlo_panel(mc: Dict[str, Any], label: str='Scenario') -> None:
    s=mc.get('summary',{}); n=len(mc.get('runs',[])); bn=mc.get('dominant_bottleneck','-'); share=mc.get('bottleneck_share')
    def block(key,title,fmt):
        x=s.get(key,{}); mean=x.get('mean');lo=x.get('ci_low');hi=x.get('ci_high'); fmt_original=fmt;fmt=lambda v:'Não calculado' if v is None else fmt_original(v)
        return f'<div><div class="k">{title}</div><div class="v">{fmt(mean)}</div><div class="s">95% CI {fmt(lo)} – {fmt(hi)}</div></div>'
    st.markdown('<div class="v21-mc"><div class="lead"><div class="k">SIMULATION CONFIDENCE</div><div class="v">'+_e(label)+'</div><div class="s">'+str(n)+' replicações · gargalo '+_e(str(bn))+' em '+stat_value(share,0,'% dos viáveis')+'</div></div>'+block('throughput','Throughput',lambda v:f'{v:.2f}')+block('sla','SLA',lambda v:f'{v:.0f}%')+block('makespan','Makespan',lambda v:f'{v:.1f}h')+block('unit_cost','Cost / unit',lambda v:f'R$ {v:.0f}')+'</div>',unsafe_allow_html=True)


def resilience_surface_chart(surface: Dict[str, Any]) -> go.Figure:
    pts=surface.get('points',[])
    demands=sorted({float(p['demand']) for p in pts}); absences=sorted({int(p['absent']) for p in pts})
    z=[]; text=[]
    for a in absences:
        row=[]; tr=[]
        for d in demands:
            p=next((x for x in pts if int(x['absent'])==a and abs(float(x['demand'])-d)<1e-9),None)
            row.append(float(p['sla']) if p else None)
            tr.append((f"SLA {p['sla']:.0f}%<br>TP {p['throughput']:.2f}<br>MK {p['makespan']:.1f}h<br>BN {p['bottleneck']}") if p else '')
        z.append(row); text.append(tr)
    fig=go.Figure(go.Heatmap(z=z,x=demands,y=absences,text=text,hovertemplate='Demanda %{x:.2f}×<br>Ausências %{y}<br>%{text}<extra></extra>',
        colorscale=[[0,'#B64842'],[.35,'#D98B55'],[.65,'#E8D9B9'],[.80,'#8EC8BC'],[1,'#2D7864']],zmin=0,zmax=100,colorbar=dict(title='SLA')))
    floor=float(surface.get('sla_floor',80))
    fig.update_layout(height=390,margin=dict(l=20,r=20,t=22,b=42),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#142227',font=dict(family='Aptos, Segoe UI',color='#53625D',size=11),xaxis_title='Multiplicador de demanda',yaxis_title='Ausências no posto')
    fig.add_annotation(x=demands[-1] if demands else 1,y=absences[-1] if absences else 0,text=f'Piso SLA {floor:.0f}%',showarrow=False,xanchor='right',font=dict(size=10,color='#687671'))
    return fig


def frontier_summary(surface: Dict[str, Any]) -> None:
    safe=int(surface.get('safe_count',0)); total=int(surface.get('total',0)); pct=100*safe/max(1,total); station=surface.get('station','-')
    st.markdown(f'''<div class="v21-frontier"><div class="head"><b>Operational survival map</b><span>{_e(station)} · {safe}/{total} combinações dentro do piso</span></div><div style="font-size:.58rem;color:#6E7D78">A superfície cruza demanda e ausência para mostrar onde o modelo ainda sustenta o SLA definido. Cobertura segura do grid: <b>{pct:.0f}%</b>.</div></div>''',unsafe_allow_html=True)
