from __future__ import annotations
from html import escape
from typing import Any, Dict, List
import streamlit as st
import plotly.graph_objects as go


def _e(x: Any) -> str:
    return escape(str(x))


def inject_v26_css() -> None:
    st.markdown(r'''<style>
:root{--am26-bg:#F1F5F4;--am26-paper:#FCFDFC;--am26-ink:#0A171A;--am26-muted:#64736F;--am26-line:#D4DFDC;--am26-dark:#07171B;--am26-dark2:#10252A;--am26-orange:#FF681B;--am26-teal:#45A89D;--am26-red:#C84A43;--am26-green:#26785F}
.stApp{background:radial-gradient(circle at 92% 4%,rgba(69,168,157,.07),transparent 26%),linear-gradient(180deg,#F7FAF9 0,#F1F5F4 42%,#EDF2F0 100%)!important;color:var(--am26-ink)}
[data-testid="stAppViewContainer"]>.main .block-container{padding-top:.8rem!important;padding-bottom:3rem!important;max-width:1680px!important}
html,body,[class*="css"]{font-family:"Segoe UI Variable","Segoe UI",Aptos,Arial,sans-serif!important}
h1,h2,h3{letter-spacing:-.025em!important;color:#0A171A!important} h1{font-size:2.15rem!important} h2{font-size:1.6rem!important}
p,li,label,[data-testid="stCaptionContainer"]{font-size:.91rem!important;line-height:1.48!important}
[data-testid="stMetricValue"]{font-weight:720!important;letter-spacing:-.035em!important}
/* enterprise surfaces */
[data-testid="stVerticalBlockBorderWrapper"]{border-color:rgba(129,151,144,.24)!important;box-shadow:none!important}
.am16-topbar,.am16-page-head,.v20-workflow{box-shadow:none!important}
.v20-workflow{min-height:44px!important}
.v20-stage{padding:7px 12px!important}
.am16-page-head{margin-bottom:10px!important}
/* rail polish */
div[data-testid="column"]:first-child [data-testid="stVerticalBlock"]{scrollbar-width:none}
.am16-side-sec{margin-top:16px!important;margin-bottom:4px!important;font-size:8px!important;letter-spacing:.20em!important;opacity:.56!important}
div[data-testid="column"]:first-child .stButton>button{min-height:37px!important;border-radius:8px!important;font-size:12px!important}
/* form ergonomics */
.stTextInput input,.stNumberInput input,.stSelectbox [data-baseweb="select"]>div{min-height:42px!important;border-radius:8px!important}
.stButton>button{border-radius:8px!important;transition:transform .14s ease,border-color .14s ease,box-shadow .14s ease!important}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 7px 20px rgba(16,37,42,.07)!important}
[data-testid="stDataFrame"]{border-radius:9px!important;overflow:hidden!important;border:1px solid var(--am26-line)!important}
/* v26 building blocks */
.am26-strip{display:grid;grid-template-columns:repeat(4,1fr);background:rgba(252,253,252,.82);border:1px solid var(--am26-line);border-radius:10px;overflow:hidden;margin:8px 0 14px}.am26-strip>div{padding:13px 15px;border-right:1px solid var(--am26-line)}.am26-strip>div:last-child{border-right:0}.am26-strip .k,.am26-card .k,.am26-inspector .k,.am26-scene .k{font:700 9px/1.2 "Cascadia Mono","Segoe UI",sans-serif;letter-spacing:.13em;color:#7A8A85;text-transform:uppercase}.am26-strip .v{font-weight:750;font-size:18px;margin-top:6px;letter-spacing:-.025em}.am26-strip .s{font-size:11px;color:var(--am26-muted);margin-top:3px}
.am26-inspector{background:linear-gradient(145deg,#07171B,#10252A);border:1px solid #254248;border-radius:12px;padding:16px;color:#DCE9E5;box-shadow:0 18px 42px rgba(7,23,27,.13)}.am26-inspector h3{color:white!important;margin:5px 0 12px!important;font-size:18px!important}.am26-inspector .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:#274047;border:1px solid #274047;border-radius:8px;overflow:hidden}.am26-inspector .cell{background:#102126;padding:10px}.am26-inspector .cell b{display:block;color:#fff;font-size:16px;margin-top:3px}.am26-inspector .signal{margin-top:11px;border-left:3px solid var(--am26-orange);background:rgba(255,104,27,.07);padding:9px 10px;font-size:12px;color:#C9D8D4}
.am26-ai{display:flex;align-items:center;justify-content:space-between;gap:16px;border:1px solid rgba(69,168,157,.38);background:linear-gradient(90deg,rgba(69,168,157,.08),rgba(255,255,255,.68));border-radius:9px;padding:10px 13px;margin:10px 0}.am26-ai b{font-size:12px}.am26-ai span{font-size:11px;color:var(--am26-muted)}
.am26-cardgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:9px 0 16px}.am26-card{background:rgba(252,253,252,.9);border:1px solid var(--am26-line);border-radius:10px;padding:13px;min-height:116px;transition:.15s ease}.am26-card:hover{transform:translateY(-2px);border-color:#AFC3BD;box-shadow:0 9px 24px rgba(18,45,47,.06)}.am26-card.favorite{border-color:rgba(255,104,27,.5)}.am26-card h4{margin:6px 0 8px;font-size:15px}.am26-card .metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:5px}.am26-card .metrics span{font-size:11px;color:#687872}.am26-card .metrics b{font-size:13px;color:#102126}.am26-tags{margin-top:9px}.am26-tag{display:inline-block;padding:3px 7px;border:1px solid #D8E1DE;border-radius:99px;font-size:9px;margin-right:4px;color:#667670}
.am26-trust{display:grid;grid-template-columns:180px 1fr;gap:12px;align-items:stretch}.am26-trustscore{background:#07171B;color:#fff;border-radius:10px;padding:16px}.am26-trustscore .score{font-size:38px;font-weight:800;letter-spacing:-.06em}.am26-trustscore .score small{font-size:13px;color:#8BA19A}.am26-trustdims{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--am26-line);border-radius:10px;overflow:hidden}.am26-trustdims>div{background:#FCFDFC;padding:13px;border-right:1px solid var(--am26-line)}.am26-trustdims>div:last-child{border-right:0}.am26-trustdims b{display:block;font-size:18px;margin:5px 0}.am26-bar{height:3px;background:#E5ECE9;border-radius:99px;overflow:hidden}.am26-bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--am26-teal),var(--am26-orange))}
.am26-target{background:linear-gradient(140deg,#07171B,#10252A);border:1px solid #28454A;border-radius:12px;padding:16px;color:white;display:grid;grid-template-columns:1.4fr repeat(4,.65fr);gap:1px}.am26-target>div{padding:5px 13px;border-left:1px solid #294348}.am26-target>div:first-child{border-left:0}.am26-target .big{font-size:24px;font-weight:790;color:white}.am26-target .good{color:#62C5B7}.am26-target .accent{color:#FF7B39}
.am26-story{background:#07171B;border:1px solid #29454A;border-radius:14px;padding:22px;color:#DDE9E6}.am26-storytop{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.am26-storytop b{font-size:22px;color:#fff}.am26-scenes{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.am26-scene{background:#10252A;border:1px solid #28454A;border-radius:9px;padding:12px;min-height:112px}.am26-scene.active{border-color:#FF681B;box-shadow:inset 0 -2px #FF681B}.am26-scene h4{font-size:13px;color:white;margin:7px 0}.am26-scene p{font-size:10px!important;color:#9FB1AB;margin:0}
@media(max-width:1100px){.am26-cardgrid,.am26-scenes{grid-template-columns:1fr 1fr}.am26-strip,.am26-trustdims{grid-template-columns:1fr 1fr}.am26-target{grid-template-columns:1fr 1fr}.am26-trust{grid-template-columns:1fr}}
</style>''', unsafe_allow_html=True)


def executive_strip(items: List[tuple[str,str,str,str]]) -> None:
    html=''.join(f'<div><div class="k">{_e(k)}</div><div class="v" style="color:{_e(c)}">{_e(v)}</div><div class="s">{_e(s)}</div></div>' for k,v,s,c in items)
    st.markdown(f'<div class="am26-strip">{html}</div>',unsafe_allow_html=True)


def station_inspector(station_row: Dict[str,Any], pressure_share: float=0.0) -> None:
    st.markdown(f'''<div class="am26-inspector"><div class="k">CONTEXT INSPECTOR · {_e(station_row.get('Posto','—'))}</div><h3>{_e(station_row.get('Nome',''))}</h3><div class="grid">
    <div class="cell"><div class="k">MACHINE LOAD</div><b>{float(station_row.get('Utilização máquina (%)',0)):.1f}%</b></div>
    <div class="cell"><div class="k">AVG WAIT</div><b>{float(station_row.get('Espera média (min)',0)):.0f} min</b></div>
    <div class="cell"><div class="k">MAX QUEUE</div><b>{int(station_row.get('Fila máx.',0))}</b></div>
    <div class="cell"><div class="k">PRESSURE SHARE</div><b>{pressure_share:.0f}%</b></div></div>
    <div class="signal">Use este posto como contexto para testar capacidade, mão de obra, risco, manutenção ou perguntar ao Murphy AI.</div></div>''',unsafe_allow_html=True)


def ai_context_bar(text: str) -> None:
    st.markdown(f'<div class="am26-ai"><div><b>✦ MURPHY AI · CONTEXTUAL</b><br><span>{_e(text)}</span></div><span>explain · challenge · recommend</span></div>',unsafe_allow_html=True)


def trust_dashboard(score: float, verification: float, validation: float|None, uncertainty: float|None, data_quality: float=100.0) -> None:
    """Separate evidence dimensions: never average unlike scores into one 'trust' KPI."""
    dims = [
        ('CADASTRO',data_quality,'Verificação estrutural; não implica aderência ao mundo real.'),
        ('VERIFICAÇÃO',verification,'Consistência computacional e completude dos dados informados.'),
        ('CALIBRAÇÃO',validation,'Requer observações reais independentes.'),
        ('INCERTEZA',uncertainty,'Estabilidade em replicações sintéticas; não é probabilidade de acerto.'),
    ]
    parts = ''.join(
        '<div><span class="k">'+_e(title)+'</span><b>'+(f'{float(value):.0f}/100' if value is not None else 'Pendente')+'</b>'
        '<div class="am26-bar"><i style="width:'+(f'{max(0,min(100,float(value))):.0f}' if value is not None else '0')+'%"></i></div>'
        '<span class="am26-trust-hint">'+_e(note)+'</span></div>'
        for title,value,note in dims
    )
    st.markdown('<div class="am26-trust-dims-only"><div class="am26-trust-intro"><b>EVIDÊNCIAS DO MODELO</b><small>Dimensões independentes · não representam homologação industrial</small></div>'
        '<div class="am26-trustdims">'+parts+'</div></div>',unsafe_allow_html=True)


def skill_heatmap(skill_df, station_ids: List[str]) -> go.Figure:
    workers=[]; z=[]
    for _,r in skill_df.iterrows():
        worker=str(r.get('Operador','')).strip() or '—'; workers.append(worker)
        prof=float(r.get('Proficiência média (%)',100) or 100)
        skills=[x.strip().upper() for x in str(r.get('Competências','')).replace(';',',').split(',') if x.strip()]
        z.append([prof if sid.upper() in skills else 0 for sid in station_ids])
    fig=go.Figure(go.Heatmap(z=z,x=station_ids,y=workers,zmin=0,zmax=100,colorscale=[[0,'#EDF2F0'],[.01,'#BFD8D2'],[.75,'#45A89D'],[1,'#FF681B']],showscale=True,colorbar=dict(title='Prof.%',thickness=10)))
    fig.update_layout(height=max(240,42*max(1,len(workers))+70),margin=dict(l=10,r=20,t=15,b=25),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Segoe UI Variable, Segoe UI',size=11,color='#CBD8D3'))
    fig.update_xaxes(side='top',showgrid=False);fig.update_yaxes(showgrid=False,autorange='reversed')
    return fig


def portfolio_cards(items: List[Dict[str,Any]], notes: Dict[str,Any], limit: int=6) -> None:
    cards=[]
    for x in items[:limit]:
        key=f"{x.get('name')}::{x.get('source')}"; meta=notes.get(key,{})
        fav=' favorite' if meta.get('favorite') else ''
        tags=[t.strip() for t in str(meta.get('tags','')).split(',') if t.strip()][:3]
        tag_html=''.join(f'<span class="am26-tag">#{_e(t)}</span>' for t in tags)
        cards.append(f'''<div class="am26-card{fav}"><div class="k">{_e(x.get('source','SCENARIO'))}{' · ★' if fav else ''}</div><h4>{_e(x.get('name','—'))}</h4><div class="metrics"><span>Throughput<br><b>{float(x.get('throughput',0)):.2f}</b></span><span>SLA<br><b>{float(x.get('sla',0)):.0f}%</b></span><span>Custo/un<br><b>R$ {float(x.get('unit_cost',0)):.0f}</b></span><span>Makespan<br><b>{float(x.get('makespan',0)):.1f}h</b></span></div><div class="am26-tags">{tag_html}</div></div>''')
    st.markdown('<div class="am26-cardgrid">'+''.join(cards)+'</div>',unsafe_allow_html=True)


def mission_target_hero(best: Dict[str,Any], target_tp: float, target_sla: float) -> None:
    hit=str(best.get('Atinge meta','')).lower()=='sim'
    st.markdown(f'''<div class="am26-target"><div><div class="k">{'TARGET REACHED' if hit else 'CLOSEST ROUTE'}</div><div class="big">{_e(best.get('Cenário','Rota operacional'))}</div><div style="font-size:11px;color:#90A49E;margin-top:4px">meta {target_tp:.2f} un/h · SLA {target_sla:.0f}%</div></div>
    <div><div class="k">THROUGHPUT</div><div class="big good">{float(best.get('Throughput',0)):.2f}</div></div><div><div class="k">SLA</div><div class="big good">{float(best.get('SLA',0)):.0f}%</div></div><div><div class="k">CUSTO/UN</div><div class="big">R$ {float(best.get('Custo/un',0)):.0f}</div></div><div><div class="k">IMPLANTAÇÃO</div><div class="big accent">R$ {float(best.get('Investimento estimado',0)):,.0f}</div></div></div>''',unsafe_allow_html=True)


def presentation_story(base: Dict[str,Any], alt: Dict[str,Any]|None, value: Dict[str,Any]|None=None) -> None:
    alt=alt or base
    late=int(base.get('late_orders',0)); orders=int(base.get('orders_count',0) or max(late,1))
    scenes=[
        ('01 · OBSERVE','The operation',f'{late} of {orders} orders are late; SLA is {base.get("sla_pct",0):.0f}%.'),
        ('02 · DIAGNOSE','The constraint',f'{base.get("bottleneck","—")} concentrates system pressure.'),
        ('03 · EXPERIMENT','The counterfactual',f'{alt.get("name","Current decision")} is tested without touching the real operation.'),
        ('04 · EVIDENCE','The result',f'{alt.get("throughput_h",0):.2f} un/h · SLA {alt.get("sla_pct",0):.0f}% · R$ {alt.get("unit_cost",0):.0f}/un.'),
        ('05 · DECIDE','The handoff',f'Decide with simulation evidence, risk and economic exposure visible.')]
    html=''.join(f'<div class="am26-scene {"active" if i==4 else ""}"><div class="k">{_e(k)}</div><h4>{_e(t)}</h4><p>{_e(p)}</p></div>' for i,(k,t,p) in enumerate(scenes))
    st.markdown(f'<div class="am26-story"><div class="am26-storytop"><div><div class="k">ANTI-MURPHY · PRESENTATION MODE</div><b>From operational pressure to evidence-backed decision.</b></div><div style="color:#FF7B39;font-weight:800">V28</div></div><div class="am26-scenes">{html}</div></div>',unsafe_allow_html=True)
