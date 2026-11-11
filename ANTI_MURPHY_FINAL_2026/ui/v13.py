from __future__ import annotations

import html
from typing import Any, Dict, List
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


def _e(x): return html.escape(str(x))


def render_alert_center(alerts: List[Dict[str, Any]], height: int = 280):
    if not alerts:
        st.success("Nenhum alerta operacional relevante no cenário atual.")
        return
    rows=[]
    for a in alerts[:6]:
        level=a.get("level","ATENÇÃO")
        cls={"CRÍTICO":"crit","ATENÇÃO":"warn","OPORTUNIDADE":"opp"}.get(level,"warn")
        rows.append(f'<div class="row {cls}"><div class="sig"></div><div><b>{_e(a.get("title"))}</b><span>{_e(a.get("detail"))}</span></div><i>{_e(level)}</i></div>')
    doc=f'''<style>*{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:Aptos,"Segoe UI",sans-serif}}.box{{background:#162124;color:#edf2ef;border:1px solid #2d3a3e;border-radius:10px;padding:16px 18px}}.head{{font-size:9px;color:#ff8245;letter-spacing:.15em;font-weight:850;text-transform:uppercase;margin-bottom:6px}}.row{{display:grid;grid-template-columns:10px 1fr auto;gap:10px;align-items:center;padding:10px 0;border-top:1px solid #29373a}}.row:first-of-type{{border-top:0}}.sig{{width:8px;height:8px;border-radius:50%;background:#e3a05d}}.crit .sig{{background:#ff681b;box-shadow:0 0 12px rgba(255,104,27,.5)}}.opp .sig{{background:#59b7aa}}.row b{{display:block;font-size:11px}}.row span{{display:block;color:#869592;font-size:8px;margin-top:3px}}.row i{{font-style:normal;font-size:7px;letter-spacing:.1em;color:#9eaaa7;border:1px solid #344548;border-radius:99px;padding:4px 7px}}.crit i{{color:#ff9b68;border-color:#5e3b2d}}</style><div class="box"><div class="head">Operational Intelligence · alert center</div>{''.join(rows)}</div>'''
    components.html(doc,height=height,scrolling=False)


def sensitivity_chart(rows: List[Dict[str, Any]], resource_label: str):
    df=pd.DataFrame([{k:v for k,v in r.items() if k!="result"} for r in rows])
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["Adição"],y=df["Throughput"],mode="lines+markers+text",text=[f"{v:.2f}" for v in df["Throughput"]],textposition="top center",name="Throughput"))
    fig.add_trace(go.Scatter(x=df["Adição"],y=df["SLA"],mode="lines+markers",name="SLA (%)",yaxis="y2"))
    fig.update_layout(height=360,margin=dict(l=20,r=20,t=35,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Aptos, Segoe UI, sans-serif",color="#66736E",size=11),xaxis=dict(title=f"{resource_label} adicionais",gridcolor="#DDE3DF",zeroline=False),yaxis=dict(title="Throughput",gridcolor="#DDE3DF",zeroline=False),yaxis2=dict(title="SLA %",overlaying="y",side="right",range=[0,105],showgrid=False),legend=dict(orientation="h",y=1.15,font=dict(size=10)),hovermode="x unified")
    return fig


def rupture_chart(scan: Dict[str, Any]):
    pts=scan.get("points",[])
    df=pd.DataFrame([{k:v for k,v in x.items() if k!="result"} for x in pts])
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["Demanda x"],y=df["SLA"],mode="lines+markers",name="SLA"))
    floor=float(scan.get("sla_floor",80))
    fig.add_hline(y=floor,line_dash="dash",annotation_text=f"piso SLA {floor:.0f}%")
    fb=scan.get("first_break")
    if fb:
        fig.add_vline(x=fb["Demanda x"],line_dash="dot",annotation_text=f"ruptura {fb['Demanda x']:.2f}×")
    fig.update_layout(height=330,margin=dict(l=20,r=20,t=35,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Aptos, Segoe UI, sans-serif",color="#66736E",size=11),xaxis=dict(title="Multiplicador de demanda",gridcolor="#DDE3DF",zeroline=False),yaxis=dict(title="SLA (%)",range=[0,105],gridcolor="#DDE3DF",zeroline=False))
    return fig


def render_portfolio(history: List[Dict[str, Any]], summary: Dict[str, Any]):
    if not history:
        st.info("Rode e salve cenários para formar o portfólio de decisões.")
        return
    cols=st.columns(4)
    defs=[("Maior throughput","throughput","throughput","un/h"),("Maior SLA","sla","sla","%"),("Menor custo/un","cost","unit_cost","R$"),("Menor makespan","makespan","makespan","h")]
    for c,(title,key,metric,suffix) in zip(cols,defs):
        item=summary.get(key,{})
        value=float(item.get(metric,0))
        val=f"R$ {value:.2f}" if suffix=="R$" else f"{value:.1f}{suffix if suffix=='%' else ' '+suffix}"
        with c:
            st.markdown(f"<div class='am-card'><div class='lab'>{title}</div><div class='val'>{val}</div><div class='hint'>{_e(item.get('name','Cenário'))}</div></div>",unsafe_allow_html=True)
    df=pd.DataFrame(history)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["unit_cost"],y=df["throughput"],mode="markers+text",text=df["name"],textposition="top center",marker=dict(size=[max(12,float(x)/5) for x in df["sla"]]),customdata=df[["sla","makespan","source"]],hovertemplate="%{text}<br>Custo/un R$ %{x:.2f}<br>Throughput %{y:.2f}<br>SLA %{customdata[0]:.0f}%<br>Makespan %{customdata[1]:.1f}h<extra></extra>"))
    fig.update_layout(height=400,margin=dict(l=20,r=20,t=35,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Aptos, Segoe UI, sans-serif",color="#66736E",size=11),xaxis=dict(title="Custo por unidade",gridcolor="#DDE3DF",zeroline=False),yaxis=dict(title="Throughput",gridcolor="#DDE3DF",zeroline=False),title=dict(text="Fronteira visual de decisões",font=dict(size=14,color="#172528")))
    st.plotly_chart(fig,use_container_width=True)


def render_migration(base_bn: str, history: List[Dict[str, Any]]):
    if not history: return
    chain=[base_bn]+[str(h.get("bottleneck","-")) for h in history[-5:]]
    labels=[]
    for i,x in enumerate(chain): labels.append(f"<div class='node'><b>{_e(x)}</b><span>{'BASE' if i==0 else f'C{i}'}</span></div>")
    doc=f'''<style>*{{box-sizing:border-box}}body{{margin:0;font-family:Aptos,"Segoe UI",sans-serif;background:transparent}}.wrap{{border-radius:18px;background:#162124;border:1px solid #2e3d40;padding:15px;color:white}}.head{{font-size:9px;color:#ff8245;letter-spacing:.15em;font-weight:850;text-transform:uppercase;margin-bottom:14px}}.chain{{display:flex;align-items:center;gap:8px}}.node{{flex:1;text-align:center;border:1px solid #344548;background:#1b292c;border-radius:12px;padding:11px 6px;position:relative}}.node:not(:last-child):after{{content:'→';position:absolute;right:-13px;top:13px;color:#637672;z-index:5}}.node b{{display:block;font-size:12px;color:#eef2ef}}.node span{{font-size:7px;color:#7f918c;letter-spacing:.12em}}</style><div class='wrap'><div class='head'>Bottleneck Migration · como a restrição se move</div><div class='chain'>{''.join(labels)}</div></div>'''
    components.html(doc,height=112,scrolling=False)
