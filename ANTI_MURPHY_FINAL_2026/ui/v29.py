"""Anti-Murphy V29 Atlas visual system. Uses official artwork without redrawing logo."""
from __future__ import annotations
import base64
from html import escape
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go

BRAND = Path(__file__).resolve().parents[1]/'assets'/'brand'
ORANGE='#FF681B'
GRAPHITE='#1D292D'
CREAM='#F7F7F3'


def _asset_data(name='logo-dark.png'):
    return 'data:image/png;base64,'+base64.b64encode((BRAND/name).read_bytes()).decode()


def _h(x): return escape(str(x),quote=True)


def inject_atlas_css():
    st.markdown('''<style>
    /* V29.1 ATLAS — official palette. Overrides legacy light skins; no logo alteration. */
    html, body, .stApp, [data-testid="stAppViewContainer"] {background:#0C1518!important;color:#F7F7F3!important;}
    [data-testid="stHeader"]{background:#0C1518!important;}
    .block-container{max-width:1850px!important;padding:1.1rem 1.5rem 4rem!important;}
    html,body,p,span,label,h1,h2,h3,h4,div{font-family:"Segoe UI Variable","Aptos","Segoe UI",system-ui,sans-serif;}
    .stMarkdown p, .stMarkdown li{color:#C9D2CF!important;font-size:.88rem!important;line-height:1.6!important;}
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4{color:#F7F7F3!important;letter-spacing:-.02em!important;}
    .stMarkdown h3{font-size:1.18rem!important;margin-top:1.4rem!important;}
    [data-testid="stCaptionContainer"] p, .stCaption p{color:#98A9A8!important;font-size:.78rem!important;}
    [data-testid="stMetric"]{background:#142126!important;border:1px solid #2A4044!important;border-radius:13px!important;box-shadow:none!important;padding:16px!important;}
    [data-testid="stMetricLabel"] p{color:#A8BCB9!important;font-size:.77rem!important;}
    [data-testid="stMetricValue"]{color:#F7F7F3!important;font-weight:780!important;}
    [data-testid="stMetricDelta"]{font-size:.8rem!important;}
    .stButton>button, .stDownloadButton>button {box-shadow:none!important;min-height:42px!important;font-size:.83rem!important;transform:none!important;border-radius:9px!important;background:#1C2A2E!important;color:#F7F7F3!important;border:1px solid #38494D!important;}
    .stButton>button:hover,.stDownloadButton>button:hover{background:#27383B!important;border-color:#FF681B!important;color:#FFFFFF!important;transform:none!important;}
    .stButton>button[kind="primary"]{background:#FF681B!important;color:#151E21!important;border-color:#FF681B!important;font-weight:800!important;}
    .stButton>button[kind="primary"]:after{display:none!important;}
    .stButton>button[kind="primary"]:hover{background:#FF813D!important;color:#131D20!important;}
    [data-testid="stForm"], [data-testid="stExpander"]{background:#142126!important;border:1px solid #2A4044!important;border-radius:12px!important;}
    [data-testid="stSelectbox"] *,[data-testid="stNumberInput"] *, [data-testid="stTextInput"] *, [data-testid="stTextArea"] * {color:#F7F7F3;}
    [data-baseweb="select"]>div, input, textarea, [data-baseweb="input"]>div{background:#19292D!important;color:#F7F7F3!important;border-color:#30464A!important;}
    [data-testid="stWidgetLabel"] p{color:#CBD5D2!important;font-size:.8rem!important;}
    .st-key-am16_navrail{background:#101C20!important;border-color:#2D4145!important;box-shadow:none!important;}
    .st-key-am16_navrail .stButton>button{font-size:.79rem!important;min-height:37px!important;color:#B6C7C3!important;}
    .st-key-am16_navrail .stButton>button[kind="primary"]{background:#213136!important;color:#F7F7F3!important;border-left:3px solid #FF681B!important;}
    .st-key-am16_navrail .am16-side-sec{font-size:.59rem!important;color:#A3B4AF!important;margin-top:18px!important;}
    .st-key-am16_navrail .am16-side-brand .version{font-size:.61rem!important;color:#A3B4AF!important;}
    .am16-topbar{background:#142227!important;color:#F7F7F3!important;border-color:#2D4346!important;box-shadow:none!important;}
    .am16-top-title,.am16-top-title span{color:#F7F7F3!important;}
    .am16-breadcrumb{color:#AAB9B6!important;}
    .am16-status-chip{background:#1B2C2F!important;color:#C8D4D1!important;border-color:#354A4E!important;}
    .am16-status-chip b{color:#F7F7F3!important;}
    .am16-pagehead h1{color:#F7F7F3!important;font-size:1.75rem!important;}
    .am16-pagehead .copy{color:#B2C2BE!important;font-size:.79rem!important;}
    .am16-pagehead .copy b{color:#F7F7F3!important;}
    [data-testid="stTabs"] [data-baseweb="tab-list"]{background:#142126!important;border-color:#2E4348!important;}
    [data-testid="stTabs"] [data-baseweb="tab"]{color:#CBD6D3!important;}
    [data-testid="stTabs"] [aria-selected="true"]{background:#FF681B!important;color:#172225!important;}
    [data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid #2A4044!important;border-radius:11px!important;}
    [data-testid="stAlert"]{border-radius:11px!important;}
    .atlas-hero{border:1px solid #304649;border-radius:20px;background:#17252A;padding:24px 26px;position:relative;overflow:hidden;margin:9px 0 18px;}
    .atlas-hero:before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:#FF681B;}
    .atlas-hero .brand{max-width:220px;width:42%;display:block;margin-bottom:19px;height:auto;}
    .atlas-eyebrow{font-size:.72rem;color:#FF9A68!important;letter-spacing:.15em;font-weight:800;margin-bottom:6px;text-transform:uppercase;}
    .atlas-hero h1{font-size:clamp(1.9rem,2.6vw,2.8rem)!important;letter-spacing:-.045em!important;color:#F7F7F3!important;line-height:1.06;margin:0 0 9px!important;}
    .atlas-hero p{font-size:.91rem!important;color:#BDCAC7!important;max-width:800px;margin:0!important;}
    .atlas-pill-row{display:flex;gap:9px;margin-top:18px;flex-wrap:wrap;}
    .atlas-pill{padding:7px 11px;border:1px solid #405256;background:#1F3034;border-radius:7px;font-size:.73rem;color:#D7E2DE!important;font-weight:720;}
    .atlas-pill.active{border-color:#FF681B;color:#FFC09E!important;}
    .atlas-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:8px 0 15px;}
    .atlas-kpi{background:#17252A;border:1px solid #2D4246;border-radius:12px;padding:17px 17px 16px;min-width:0;}
    .atlas-kpi .k{color:#B4C5C0!important;font-size:.75rem;font-weight:700;letter-spacing:.02em;}
    .atlas-kpi .v{color:#F7F7F3!important;font-size:1.7rem;font-weight:820;letter-spacing:-.04em;margin-top:6px;}
    .atlas-kpi .m{color:#849C95!important;font-size:.7rem;margin-top:6px;}
    .atlas-stage{border:1px solid #324549;border-radius:12px;background:#162429;padding:17px;margin:4px 0 8px;min-height:162px;}
    .atlas-stage .num{color:#FF8B50;font-size:.73rem;letter-spacing:.16em;font-weight:850;}
    .atlas-stage h3{color:#F7F7F3!important;font-size:1.1rem!important;margin:6px 0 10px!important;}
    .atlas-stage .desc{color:#C7D4CF!important;font-size:.82rem;line-height:1.55;}
    .atlas-status{border:1px solid #FF681B;background:#2D2724;border-radius:11px;padding:15px 18px;margin:14px 0;}
    .atlas-status .tag{color:#FFA677!important;font-size:.72rem;font-weight:850;letter-spacing:.1em;}
    .atlas-status .headline{color:#F7F7F3!important;font-size:1.12rem;font-weight:800;margin-top:6px;}
    .atlas-status .explain{color:#D7C5BB!important;font-size:.83rem;line-height:1.5;margin-top:6px;}
    .atlas-stations{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 16px;}
    .atlas-station{flex:1 1 130px;border:1px solid #33474B;border-radius:10px;padding:12px;background:#1A2A2E;min-width:112px;}
    .atlas-station.hot{border-color:#FF681B;background:#2B2926;}
    .atlas-station .sid{color:#F7F7F3!important;font-size:.79rem;font-weight:800;}
    .atlas-station .signal{color:#9FB5AF!important;font-size:.69rem;margin-top:6px;}
    .atlas-station .bar{height:5px;background:#304246;border-radius:5px;margin-top:9px;overflow:hidden;}
    .atlas-station .bar > span{display:block;height:100%;background:#FF681B;}
    @media(max-width:950px){.atlas-strip{grid-template-columns:repeat(2,minmax(0,1fr));}.atlas-hero{padding:19px;}.atlas-kpi .v{font-size:1.35rem;}}
    </style>''',unsafe_allow_html=True)


def hero(title, subtitle, mode='SIMULAÇÃO · AMBIENTE ACADÊMICO'):
    markup=f'''<section class="atlas-hero">
      <img class="brand" src="{_asset_data()}" alt="Anti-Murphy — identidade oficial" />
      <div class="atlas-eyebrow">{_h(mode)} / V29.1 ATLAS</div>
      <h1>{_h(title)}</h1><p>{_h(subtitle)}</p>
      <div class="atlas-pill-row"><span class="atlas-pill">01 · OPERAÇÃO</span><span class="atlas-pill active">02 · INCIDENTE</span><span class="atlas-pill">03 · RECUPERAÇÃO</span></div>
    </section>'''
    st.markdown(markup,unsafe_allow_html=True)


def kpi_strip(items):
    html=''.join(f'<div class="atlas-kpi"><div class="k">{_h(k)}</div><div class="v">{_h(v)}</div><div class="m">{_h(note)}</div></div>' for k,v,note in items)
    st.markdown(f'<div class="atlas-strip">{html}</div>',unsafe_allow_html=True)


def stage(number, title, description):
    st.markdown(f'<div class="atlas-stage"><div class="num">ETAPA {number}</div><h3>{_h(title)}</h3><div class="desc">{_h(description)}</div></div>',unsafe_allow_html=True)


def signal(status, reason, headline='PARECER DO MODELO'):
    st.markdown(f'<div class="atlas-status"><div class="tag">{_h(headline)}</div><div class="headline">{_h(status)}</div><div class="explain">{_h(reason)}</div></div>',unsafe_allow_html=True)


def plant_flow(stations, bottleneck, affected=None):
    bits=[]
    for row in stations:
        sid=str(row.get('Posto','?'))
        util=max(0,min(100,float(row.get('Utilização máquina (%)',0))))
        queue=int(row.get('Fila máx.',0))
        hot=(sid == bottleneck or sid==affected)
        cls=' hot' if hot else ''
        bits.append(f'<div class="atlas-station{cls}"><div class="sid">{_h(sid)}</div><div class="signal">Uso: {util:.0f}% · Fila: {queue}</div><div class="bar"><span style="width:{util:.1f}%"></span></div></div>')
    st.markdown('<div class="atlas-stations">'+''.join(bits)+'</div>',unsafe_allow_html=True)


def comparison_chart(normal,incident,leader=None):
    labels=['Operação','Incidente']+(['Resposta'] if leader else [])
    vals=[float(normal['total_cost']),float(incident['total_cost'])]+([float(leader['decision_cost'])] if leader else [])
    colors=['#A8BFC0','#FF681B']+(['#5EB6A2'] if leader else [])
    fig=go.Figure(go.Bar(x=labels,y=vals,marker_color=colors,text=[f'R$ {v:,.0f}' for v in vals],textposition='outside',cliponaxis=False))
    fig.update_layout(title='Custo da carteira + implantação (R$)',height=310,margin=dict(l=15,r=15,t=60,b=10),
        paper_bgcolor='#142126',plot_bgcolor='#142126',font=dict(color='#F7F7F3',size=12),
        xaxis=dict(showgrid=False),yaxis=dict(gridcolor='#2A3E43',zeroline=False),showlegend=False)
    return fig


def frontier_chart(rows):
    valid=[r for r in rows if r.get('feasible') and r.get('within_budget') and r.get('decision_cost') is not None]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[r['decision_cost'] for r in valid],y=[r['sla_pct'] for r in valid],mode='markers',
        marker=dict(color=['#FF681B' if r.get('pareto') else '#78979A' for r in valid],size=[13 if r.get('pareto') else 9 for r in valid],line=dict(width=1,color='#F7F7F3')),
        customdata=[[r['action'],r['makespan_h']] for r in valid],
        hovertemplate='<b>%{customdata[0]}</b><br>Custo: R$ %{x:,.2f}<br>SLA: %{y:.1f}%<br>Prazo: %{customdata[1]:.2f}h<extra></extra>'))
    fig.update_layout(title='Fronteira de decisão · custo × SLA',height=320,margin=dict(l=10,r=10,t=54,b=5),
        paper_bgcolor='#142126',plot_bgcolor='#142126',font=dict(color='#F7F7F3',size=12),
        xaxis=dict(title='Custo total da decisão (R$)',gridcolor='#293E40'),yaxis=dict(title='SLA (%)',gridcolor='#293E40'),showlegend=False)
    return fig
