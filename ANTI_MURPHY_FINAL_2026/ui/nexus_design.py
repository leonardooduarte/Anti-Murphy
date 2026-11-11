"""V30 single-source design system; the original artwork is embedded unmodified."""
from html import escape
from pathlib import Path
import base64
import streamlit as st
import plotly.graph_objects as go
ROOT=Path(__file__).resolve().parents[1]


def h(s):return escape(str(s),quote=True)
def money(x,decimals=0):return 'R$ '+f'{float(x):,.{decimals}f}'.replace(',','_').replace('.',',').replace('_','.')
def number(x,decimals=1):return f'{float(x):.{decimals}f}'.replace('.',',')


def inject():
    st.markdown('<style>'+(ROOT/'ui/nexus.css').read_text()+'</style>',unsafe_allow_html=True)


def brand():
    data=base64.b64encode((ROOT/'assets/brand/logo-dark.svg').read_bytes()).decode()
    st.markdown(f'<div class="nx-brand"><img src="data:image/svg+xml;base64,{data}" alt="Anti-Murphy"><small>V30 / NEXUS · INTELIGÊNCIA OPERACIONAL</small></div>',unsafe_allow_html=True)


def top_line(page,run_id=None):
    st.markdown(f'<div class="nx-topline"><span>WORKSPACE / {h(page.upper())}</span><span class="tag"><i class="dot"></i>SIMULAÇÃO · DADOS DO MODELO</span><span>{h("RUN "+run_id if run_id else "MODELO PRONTO")}</span></div>',unsafe_allow_html=True)


def hero(kicker,title,copy):
    st.markdown(f'<div class="nx-hero"><div><div class="eyebrow">{h(kicker)}</div><h1>{title}</h1></div><p>{h(copy)}</p></div>',unsafe_allow_html=True)


def section(index,title):st.markdown(f'<div class="nx-section"><span>{h(index)}</span> / {h(title.upper())}</div>',unsafe_allow_html=True)


def rail(items):
    html=''.join(f'<div class="nx-kpi"><div class="label">{h(k)}</div><div class="value {"accent" if i==0 else ""}">{h(v)}</div><div class="detail">{h(d)}</div></div>' for i,(k,v,d) in enumerate(items))
    st.markdown('<div class="nx-metric-rail">'+html+'</div>',unsafe_allow_html=True)


def verdict(label,title,body):
    st.markdown(f'<div class="nx-verdict"><div class="label">{h(label)}</div><strong>{h(title)}</strong><p>{h(body)}</p></div>',unsafe_allow_html=True)


def evidence(label,title,body):
    st.markdown(f'<div class="nx-evidence"><div class="type">{h(label)}</div><h3>{h(title)}</h3><p>{h(body)}</p></div>',unsafe_allow_html=True)


def empty(title,body):st.markdown(f'<div class="nx-empty"><b>{h(title)}</b><p>{h(body)}</p></div>',unsafe_allow_html=True)


def timeline(data=None):
    if data:
        s=data['incident_parameters'];steps=[('01','Operação nominal','Carteira, recursos e roteiros preservados.'),('02',f"Parada em {s['station']}",f"Início {number(s['start_h'])} h · duração {number(s['duration_h'])} h."),('03','Comparar respostas',f"{len(data['rows'])-1} intervenções, mesmo incidente e semente."),('04','Escolher com evidência',data['leader']['action'] if data.get('leader') else 'Nenhuma resposta selecionada.')]
    else:steps=[('01','Observar','Conheça o fluxo e a restrição atual.'),('02','Definir o incidente','Posto, início, duração e orçamento.'),('03','Testar alternativas','Compare o efeito de cada resposta.'),('04','Revisar a decisão','Examine evidências e limites.')]
    html=''.join(f'<div class="nx-step {"active" if data else ""}"><span class="index">{i}</span><b>{h(t)}</b><p>{h(d)}</p></div>' for i,t,d in steps)
    st.markdown('<div class="nx-timeline">'+html+'</div>',unsafe_allow_html=True)


def plot_style(fig,title=None,height=310):
    fig.update_layout(template='plotly_dark',title=dict(text=title,font=dict(size=15,color='#e8ece6')) if title else None,
        paper_bgcolor='#111b1f',plot_bgcolor='#111b1f',font=dict(family='Segoe UI, sans-serif',color='#cbd9d7',size=12),
        margin=dict(l=15,r=20,t=48 if title else 15,b=30),height=height,
        colorway=['#FF681B','#a6c7b9','#89a9b4','#d4cec1'],legend=dict(orientation='h',y=1.12,x=0,font=dict(size=11)),
        hoverlabel=dict(bgcolor='#23343b',font_color='#F7F7F3'),transition_duration=300)
    fig.update_xaxes(gridcolor='#31454d',zeroline=False)
    fig.update_yaxes(gridcolor='#31454d',zeroline=False)
    return fig


def cost_chart(data,action):
    n=data['normal'];i=data['incident'];labels=['Nominal','Incidente']+(['Resposta'] if action else [])
    results=[n,i]+([action['result']] if action else [])
    fig=go.Figure()
    fig.add_bar(name='Capacidade contratada',x=labels,y=[r['operating_cost'] for r in results],marker_color='#8babad')
    fig.add_bar(name='Multas por atraso',x=labels,y=[r['penalty_total'] for r in results],marker_color='#FF681B')
    fig.add_bar(name='Implantação',x=labels,y=[0,0]+([action['investment']] if action else []),marker_color='#d3ba9b')
    fig.update_layout(barmode='stack',yaxis_title='R$ / carteira',bargap=.52)
    return plot_style(fig,'De onde vem o custo?',330)


def completion_chart(data,action):
    fig=go.Figure()
    for name,r,color in [('Nominal',data['normal'],'#8fabb3'),('Incidente',data['incident'],'#FF681B')]+([('Resposta',action['result'],'#a6c7b9')] if action else []):
        from simulation.replay import replay_payload
        p=replay_payload(r);ts=p['completion_times']
        fig.add_trace(go.Scatter(x=[0]+ts,y=list(range(len(ts)+1)),name=name,mode='lines',line=dict(color=color,width=2.5,shape='hv')))
    fig.update_layout(xaxis_title='Tempo do modelo (h)',yaxis_title='Peças concluídas')
    return plot_style(fig,'Quando a produção se recupera?',330)


def frontier(data):
    rows=[r for r in data['rows'] if r['feasible'] and r['decision_cost'] is not None]
    fig=go.Figure()
    for label,group,color in [('Atende às restrições',[r for r in rows if r['within_budget'] and r['meets_sla'] and r['action']!='Não intervir'],'#a6c7b9'),
        ('Restrita',[r for r in rows if not(r['within_budget'] and r['meets_sla'])],'#718b93'),
        ('Não intervir',[r for r in rows if r['action']=='Não intervir'],'#FF681B')]:
        fig.add_trace(go.Scatter(x=[r['decision_cost'] for r in group],y=[r['makespan_h'] for r in group],mode='markers',name=label,
            marker=dict(size=[15 if r.get('pareto') else 9 for r in group],color=color,line=dict(width=1,color='#e1e9df')),
            customdata=[[r['action'],r['sla_pct'],r['investment']] for r in group],
            hovertemplate='<b>%{customdata[0]}</b><br>Custo total: R$ %{x:.2f}<br>Prazo: %{y:.2f} h<br>SLA: %{customdata[1]}%<br>Implantação: R$ %{customdata[2]:.2f}<extra></extra>'))
    fig.update_layout(xaxis_title='Custo total com implantação (R$)',yaxis_title='Conclusão da carteira (h)')
    return plot_style(fig,'Custo × prazo · tamanho maior = não dominada',380)
