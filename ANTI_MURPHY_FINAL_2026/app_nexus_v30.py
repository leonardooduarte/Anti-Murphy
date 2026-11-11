"""ANTI-MURPHY V30 NEXUS — unified workspace over the retained V29 DES engine."""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
from copy import deepcopy
import json
import os
import runpy
import math
import zipfile
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from data.scenarios import STATIONS_BASE, ORDERS_BASE
from data.importer import make_template, read_client_workbook
from simulation.nexus import (initialize, base_config, current_spec, current_analysis, nominal, execute,
    selected_action, invalidate_model, use_demo, restore_model, ExperimentSpec, audit)
from simulation.nexus_ai import local_answer, generative_answer, execute_proposal, make_proposal
from simulation.model_io import frames_to_model, route_to_text
from simulation.validation import validate_model
from simulation.decision_lab import config_signature
from simulation.atlas import decision_memo
from simulation.report import executive_html
from ui import nexus_design as d
from ui.motion import render_twin

ROOT=Path(__file__).resolve().parent


def model_frames():
    ss=[]
    for sid,s in st.session_state.stations.items():
        ss.append({'ID':sid,'Posto':s.get('nome',sid),'Máquinas':s['maquinas'],'Operadores':s['operadores'],
            'Operadores/máquina':s.get('operadores_por_maquina',1),'Eficiência operador':s['eficiencia_operador'],
            'Disponibilidade':s['disponibilidade'],'Setup (min)':s.get('setup_min',0),
            'Custo operador/h':s['custo_operador_h'],'Custo máquina/h':s['custo_maquina_h']})
    oo=[{'ID':o['id'],'Cliente':o.get('cliente',''),'Produto':o.get('produto',''),'Quantidade':o['quantidade'],
        'Prazo (h)':o['prazo_h'],'Multa/h (R$)':o['multa_hora'],'Prioridade':o.get('prioridade',3),'Roteiro':route_to_text(o['route'])} for o in st.session_state.orders]
    return pd.DataFrame(ss),pd.DataFrame(oo)


def go(page):st.session_state.nx_page=page;st.rerun()


def draw_sidebar():
    with st.sidebar:
        d.brand()
        st.markdown('<div class="nx-nav-label">CENTRAL DE INTELIGÊNCIA</div>',unsafe_allow_html=True)
        pages=[('War Room','◉  War Room'),('Murphy AI','✦  Murphy AI'),('Evidence','⇄  Comparar respostas'),('Review','◇  Revisar decisão'),('Factory Command','▣  Fábrica animada')]
        for page,label in pages:
            if st.button(label,key='nav_'+page,type='primary' if st.session_state.nx_page==page else 'secondary',width='stretch'):go(page)
        st.markdown('<div class="nx-nav-label">OPERAÇÃO E APRESENTAÇÃO</div>',unsafe_allow_html=True)
        for page,label in [('Model','▦  Modelo industrial'),('Trust','◎  Evidências e limites'),('Pitch','▶  Pitch · 2 minutos')]:
            if st.button(label,key='nav_'+page,type='primary' if st.session_state.nx_page==page else 'secondary',width='stretch'):go(page)
        st.markdown('<div class="nx-nav-label">PREFERÊNCIAS</div>',unsafe_allow_html=True)
        st.toggle('Reduzir movimento',key='nx_reduced_motion',help='O replay inicia pausado; reduz a frequência dos desenhos e mantém os controles manuais.')
        with st.expander('Ferramentas V29 preservadas'):
            st.caption('Laboratório, otimização, resiliência, portfólio, metas, operações e demais módulos originais.')
            if st.button('Abrir ferramentas anteriores',width='stretch'):
                st.session_state.nx_legacy=True;st.rerun()
        st.markdown(f'<div class="nx-side-foot"><b>{len(st.session_state.stations)} postos · {len(st.session_state.orders)} ordens</b><br>{d.h(st.session_state.nx_source)}<br>Motor DES / processamento local</div>',unsafe_allow_html=True)


def incident_controls():
    spec=current_spec(st.session_state);sids=list(st.session_state.stations)
    if spec.station not in sids:spec=ExperimentSpec(station=sids[0])
    with st.expander('Configurar incidente e condições',expanded=False):
        with st.form('incident_form'):
            a,b,c=st.columns([1.2,1,1])
            with a:sid=st.selectbox('Posto afetado',sids,index=sids.index(spec.station))
            with b:start=st.number_input('Início da parada (h)',0.,500.,float(spec.start_h),.5)
            with c:duration=st.number_input('Duração da parada (h)',.05,168.,float(spec.duration_h),.5)
            a,b=st.columns(2)
            with a:budget=st.number_input('Teto de investimento (R$) · 0 = sem teto',0.,100000000.,float(spec.budget),500.)
            with b:sla=st.slider('SLA mínimo (%)',0,100,int(spec.min_sla),5)
            a,b,c=st.columns(3)
            with a:cw=st.number_input('Implantação / operador (R$)',0.,100000000.,float(spec.cost_worker),100.)
            with b:cm=st.number_input('Implantação / máquina (R$)',0.,100000000.,float(spec.cost_machine),500.)
            with c:ce=st.number_input('Manutenção expressa (R$)',0.,100000000.,float(spec.cost_express),100.)
            st.caption('Valores são premissas por carteira. Manutenção expressa reduz pela metade a duração da parada. Realocação pressupõe competências e disponibilidade. As alterações valem ao executar o formulário.')
            submit=st.form_submit_button('Simular incidente e comparar respostas',type='primary',width='stretch')
        if submit:
            try:
                with st.spinner('Simulando o incidente e comparando alternativas sob a mesma semente…'):
                    execute(st.session_state,ExperimentSpec(sid,start,duration,budget,float(sla),cw,cm,ce))
                st.rerun()
            except (ValueError,TypeError) as exc:st.error(str(exc))


def summary_rail(data,b):
    if data:
        i=data['incident'];n=data['normal'];a=data.get('leader')
        d.rail([('CUSTO DO INCIDENTE',d.money(i['total_cost']),f"{d.money(i['total_cost']-n['total_cost'])} vs nominal"),
            ('CONCLUSÃO DA CARTEIRA',d.number(i['makespan_h'])+' h',f"Nominal: {d.number(n['makespan_h'])} h"),
            ('SLA COM INCIDENTE',d.number(i['sla_pct'],0)+'%',f"{i['late_orders']} de {len(i['orders'])} ordens atrasadas"),
            ('ECONOMIA LÍQUIDA',d.money(a['savings']) if a else 'Sem resposta',a['action'] if a else data['policy_status'])])
    else:
        d.rail([('THROUGHPUT NOMINAL',d.number(b['throughput_h'],2)+' un/h','Produção média da carteira'),('CONCLUSÃO NOMINAL',d.number(b['makespan_h'])+' h','Até a última peça'),
            ('SLA NOMINAL',d.number(b['sla_pct'],0)+'%','Ordens concluídas até o prazo'),('RESTRIÇÃO INDICADA',b['bottleneck'],'Diagnóstico interno do modelo')])


def downloads(data,action=None,prefix='war'):
    a,b,c=st.columns(3)
    with a:st.download_button('↓ Memorando JSON',decision_memo(data,action),'anti_murphy_v30_memorando.json','application/json',width='stretch',key=prefix+'_json')
    fields=('action','verdict','investment','decision_cost','savings','sla_pct','makespan_h','throughput_h','within_budget','meets_sla','feasible','rationale')
    csv=pd.DataFrame([{k:r.get(k) for k in fields} for r in data['rows']]).to_csv(index=False,sep=';').encode('utf-8-sig')
    with b:st.download_button('↓ Matriz de alternativas',csv,'anti_murphy_v30_alternativas.csv','text/csv',width='stretch',key=prefix+'_csv')
    with c:st.download_button('↓ Relatório executivo',executive_html(data,action),'anti_murphy_v30_relatorio.html','text/html',width='stretch',key=prefix+'_html')


def war_room():
    b=nominal(st.session_state);data=current_analysis(st.session_state)
    d.hero('01 / WAR ROOM','Toda ruptura tem<br>uma <em>resposta.</em>','Veja o que parou, acompanhe o efeito na linha e compare decisões com evidências do mesmo modelo.')
    summary_rail(data,b)
    bar1,bar2,bar3=st.columns([1.3,1,1])
    with bar1:
        if st.button('▶ Preparar demonstração CNC',type='primary',width='stretch'):
            try:
                with st.spinner('Preparando a carteira sintética reproduzível…'):use_demo(st.session_state)
                st.rerun()
            except ValueError as exc:st.error(str(exc))
    with bar2:
        if st.button('✦ Investigar com Murphy AI',width='stretch'):go('Murphy AI')
    with bar3:
        if st.button('↗ Abrir pitch de 2 minutos',width='stretch'):go('Pitch')
    incident_controls()
    data=current_analysis(st.session_state);b=nominal(st.session_state)
    d.section('01','Operação em movimento')
    render_twin(b,data,data.get('leader') if data else None,reduced=st.session_state.nx_reduced_motion)
    d.timeline(data)
    if not data:
        d.empty('O próximo passo é definir a ruptura.','Configure um incidente ou prepare a demonstração CNC. A War Room calculará as alternativas; os controles do replay permitem examinar a operação nominal agora.')
        return
    a=data.get('leader')
    d.section('02','O que mudou e como responder')
    d.verdict(data['policy_status'],a['action'] if a else 'Nenhuma intervenção selecionada',
        f"Economia líquida simulada {d.money(a['savings'],2)}, já descontando {d.money(a['investment'])} de implantação. "+a.get('verdict_reason','') if a else data['policy_explanation'])
    left,right=st.columns(2)
    with left:st.plotly_chart(d.cost_chart(data,a),width='stretch',config={'displayModeBar':False})
    with right:st.plotly_chart(d.completion_chart(data,a),width='stretch',config={'displayModeBar':False})
    st.caption('A resposta é uma alternativa aplicada desde o início do cenário, exceto a manutenção, que altera a duração do reparo. O replay compara cenários contrafactuais completos; ele não simula despacho de recursos decidido após detectar a falha.')
    c1,c2=st.columns(2)
    with c1:
        if st.button('Comparar todas as respostas →',width='stretch'):go('Evidence')
    with c2:
        if st.button('Revisar evidências da decisão →',width='stretch'):go('Review')
    downloads(data)


def require_analysis():
    data=current_analysis(st.session_state)
    if not data:
        d.empty('Ainda não há uma análise vigente.','Execute um incidente na War Room. Comparação, revisão e IA usam esse mesmo experimento e invalidam os resultados quando o modelo muda.')
        if st.button('Ir para War Room',type='primary'):go('War Room')
    return data


def evidence_page():
    d.hero('02 / DECISION EVIDENCE','Escolhas diferentes.<br><em>A mesma referência.</em>','Cada alternativa parte do mesmo incidente, carteira e semente. Examine ganhos, restrições e o custo de recuperar a operação.')
    data=require_analysis()
    if not data:return
    d.verdict('POLÍTICA DE DECISÃO',data['policy_status'],data['policy_explanation'])
    st.plotly_chart(d.frontier(data),width='stretch',config={'displaylogo':False})
    st.caption('Menor custo e menor prazo são preferíveis, respeitando o SLA mínimo. Pareto é relativo apenas ao conjunto de alternativas enumeradas. A referência “Não intervir” está identificada separadamente.')
    view=[]
    for r in data['rows']:
        view.append({'Alternativa':r['action'],'Veredito':r['verdict'],'Implantação (R$)':r['investment'],'Custo final (R$)':r['decision_cost'],
            'Economia líquida (R$)':r['savings'],'SLA (%)':r['sla_pct'],'Conclusão (h)':r['makespan_h'],
            'Orçamento OK':r['within_budget'],'SLA OK':r['meets_sla'],'Viável':r['feasible']})
    st.dataframe(pd.DataFrame(view),width='stretch',hide_index=True,height=430)
    names=[r['action'] for r in data['rows']];picked=selected_action(st.session_state,data)
    selection=st.selectbox('Alternativa a examinar',names,index=names.index(picked['action']) if picked else 0,key='nx_evidence_selection_'+data['run_id'])
    row=next(r for r in data['rows'] if r['action']==selection)
    st.session_state.nx_selected=row['signature']
    d.evidence(row['verdict'],row['action'],row.get('verdict_reason',''))
    st.markdown('**Hipótese:** '+row['rationale'])
    st.caption('Selecionar uma alternativa a examina no modelo; isso não a aprova nem a executa na operação.')
    if st.button('Abrir revisão desta alternativa',type='primary'):go('Review')
    downloads(data,row,prefix='evidence')


def review_page():
    d.hero('03 / DECISION REVIEW','Uma decisão que você<br>consegue <em>explicar.</em>','Acompanhe o raciocínio da escolha, confronte as premissas e teste se o benefício persiste sob outras sementes.')
    data=require_analysis()
    if not data:return
    row=selected_action(st.session_state,data)
    if not row:
        d.empty('Nenhuma resposta está selecionada.',data['policy_explanation'])
        if st.button('Explorar alternativas calculadas'):go('Evidence')
        downloads(data,prefix='review_none');return
    d.verdict(row['verdict'],row['action'],row.get('verdict_reason',''))
    d.rail([('INVESTIMENTO',d.money(row['investment']),'Premissa de implantação'),('CUSTO DA DECISÃO',d.money(row['decision_cost']) if row['decision_cost'] is not None else 'Não calculado','Operação + multas + implantação'),
        ('ECONOMIA LÍQUIDA',d.money(row['savings']) if row['savings'] is not None else 'Não calculada','Comparada ao incidente sem ação'),('CONCLUSÃO',d.number(row['makespan_h'])+' h',f"SLA {d.number(row['sla_pct'],0)}%")])
    a,b=st.columns([1.1,1])
    with a:
        d.section('01','Razões e condições')
        st.markdown('**Intervenção modelada:** '+row['rationale'])
        st.markdown(('**Efeito calculado:** '+row.get('tradeoff_note','')).replace('R$',r'R\$'))
        for ok,caption in [(row['feasible'],'Capacidade viável no motor'),(row['within_budget'],'Dentro do teto de investimento'),(row['meets_sla'],'SLA mínimo atendido')]:
            st.markdown(('✓ ' if ok else '× ')+caption)
    with b:
        d.evidence('VALIDAÇÃO OPERACIONAL NECESSÁRIA','Antes de considerar a execução','Confirmar capacitação, disponibilidade, contratação, custos, segurança e aderência do modelo. A realocação assume operadores habilitados; o motor limita a quantidade por posto, sem escala ou matriz individual de competências.')
    render_twin(data['normal'],data,row,reduced=st.session_state.nx_reduced_motion)
    d.section('02','Sensibilidade pareada')
    st.caption('8 pares de simulações, sementes 700–707. Mesma realização por peça em cada par. Economia líquida desconta a implantação em todas as replicações.')
    if row['feasible'] and row['action']!='Não intervir':
        if st.button('Preparar teste com 8 sementes',width='stretch'):
            st.session_state.nx_pending=make_proposal(st.session_state,current_spec(st.session_state),kind='sensitivity',action_signature=row['signature'])
    render_pending()
    sense=st.session_state.get('nx_sensitivity')
    if sense and sense.get('run_id')==data['run_id'] and sense.get('action')==row['action']:
        if sense['feasible']:
            d.rail([('ECONOMIA LÍQUIDA MÉDIA',d.money(sense['mean_net_saving'],2),'8 replicações sintéticas'),('MENOR ECONOMIA',d.money(sense['min_net_saving'],2),'Pior amostra observada'),('MAIOR ECONOMIA',d.money(sense['max_net_saving'],2),'Melhor amostra observada'),('SEMENTES','700–707','Não é probabilidade industrial')])
            table=pd.DataFrame(sense['pairs']);table['net_saving']=table['cost_saving']-row['investment']
            st.dataframe(table.rename(columns={'seed':'Semente','cost_saving':'Economia antes da implantação (R$)','sla_gain_pp':'Ganho de SLA (p.p.)','makespan_gain_h':'Redução de prazo (h)','net_saving':'Economia líquida (R$)'}),width='stretch',hide_index=True)
        else:st.warning(sense['message'])
    downloads(data,row,prefix='review')


def render_pending():
    prop=st.session_state.get('nx_pending')
    if not prop:return
    spec=ExperimentSpec(**prop['spec'])
    stale=prop['model_signature']!=config_signature(base_config(st.session_state)) or prop['workspace_signature']!=current_spec(st.session_state).signature()
    with st.container(border=True):
        d.evidence('FERRAMENTA PENDENTE · AUTORIZAÇÃO HUMANA',
            'Teste pareado de sensibilidade' if prop['kind']=='sensitivity' else 'Simular incidente e comparar respostas',
            f"Posto {spec.station} · início {d.number(spec.start_h)} h · parada {d.number(spec.duration_h)} h · teto {d.money(spec.budget) if spec.budget else 'sem teto'} · SLA mínimo {spec.min_sla:g}%. Custos: operador {d.money(spec.cost_worker)}, máquina {d.money(spec.cost_machine)}, manutenção {d.money(spec.cost_express)}.")
        if prop['kind']=='sensitivity':
            data=current_analysis(st.session_state)
            target=next((r for r in data['rows'] if r['signature']==prop['action_signature']),None) if data else None
            st.markdown('**Alternativa a testar:** '+(target['action'] if target else 'Análise desatualizada')+' · 8 pares, sementes 700–707.')
        st.caption('O teste só altera resultados de simulação deste workspace. Não aciona máquinas ou sistemas externos. Plano '+prop['id'])
        if stale:st.warning('Este plano venceu porque o modelo ou as restrições mudaram. Descarte e prepare outro.')
        a,b=st.columns([1.4,1])
        with a:
            if st.button('✓ Autorizar e executar experimento',type='primary',width='stretch',disabled=stale,key='authorize_'+prop['id']):
                try:
                    with st.spinner('Executando a ferramenta autorizada…'):result=execute_proposal(st.session_state,prop)
                    if prop['kind']=='compare':
                        answer=local_answer('Explique essa decisão para um gerente industrial',st.session_state)
                        append_message('assistant',answer['text'],answer['label'],run_id=result['run_id'])
                    else:
                        append_message('assistant','Teste pareado concluído. Os resultados líquidos de implantação estão na revisão da alternativa.','RESULTADO SIMULADO',run_id=result['run_id'])
                    st.rerun()
                except ValueError as exc:st.error(str(exc))
        with b:
            if st.button('Descartar plano',width='stretch',key='discard_'+prop['id']):
                st.session_state.pop('nx_pending',None);st.rerun()


def append_message(role,text,label='',rows=None,run_id=None):
    st.session_state.nx_messages=(st.session_state.nx_messages+[{'role':role,'text':text,'label':label,'rows':rows or [],'run_id':run_id,
        'model_signature':config_signature(base_config(st.session_state))}])[-40:]


def answer_question(question):
    try:
        mode=st.session_state.get('nx_ai_mode','Local · sem API')
        if mode=='Generativo · OpenAI' and (st.session_state.get('nx_api_key') or os.environ.get('OPENAI_API_KEY')):
            with st.spinner('Interpretando o pacote de evidências…'):
                out=generative_answer(question,st.session_state,st.session_state.get('nx_api_key') or os.environ['OPENAI_API_KEY'],st.session_state.get('nx_ai_model','gpt-4.1-mini'))
        else:out=local_answer(question,st.session_state)
        append_message('user',question)
        data=current_analysis(st.session_state)
        append_message('assistant',out['text'],out['label'],out['rows'],data['run_id'] if data else None)
        if out.get('proposal'):st.session_state.nx_pending=out['proposal']
    except ValueError as exc:
        append_message('user',question);append_message('assistant',str(exc),'PEDIDO INCOMPLETO · REVISAR')
    except Exception:
        # Do not echo exception bodies: SDK/network errors can contain request metadata.
        out=local_answer(question,st.session_state)
        append_message('user',question)
        append_message('assistant','O provedor generativo não respondeu. Continuei com a análise local.\n\n'+out['text'],out['label'],out['rows'])
        if out.get('proposal'):st.session_state.nx_pending=out['proposal']


def ai_page():
    d.hero('04 / MURPHY AI','Pergunte à operação.<br><em>Investigue a resposta.</em>','Um analista integrado ao modelo: diagnostique, compare hipóteses e autorize experimentos com parâmetros que você pode conferir.')
    data=current_analysis(st.session_state);b=nominal(st.session_state)
    st.markdown('<span class="nx-badge">CÁLCULO / MOTOR DES</span><span class="nx-badge orange">HIPÓTESES / REGRAS LOCAIS</span><span class="nx-badge">INTERPRETAÇÃO / GENERATIVA OPCIONAL</span>',unsafe_allow_html=True)
    with st.expander('Modo de IA e conexão opcional'):
        st.selectbox('Modo de análise',['Local · sem API','Generativo · OpenAI'],key='nx_ai_mode')
        # Retain session-only settings when their widgets are hidden in local mode.
        for key,default in [('nx_api_key',''),('nx_ai_model','gpt-4.1-mini')]:
            st.session_state[key]=st.session_state.get(key,default)
        if st.session_state.nx_ai_mode=='Generativo · OpenAI':
            st.text_input('Chave da API (somente nesta sessão)',type='password',key='nx_api_key',help='Alternativa: variável OPENAI_API_KEY. Não será salva nos relatórios ou no modelo.')
            st.text_input('Identificador do modelo OpenAI',key='nx_ai_model')
            import importlib.util
            if importlib.util.find_spec('openai') is None:
                st.info('Para habilitar o modo generativo, feche o aplicativo e execute INSTALAR_IA_OPCIONAL.bat. O modo local já está disponível.')
            st.caption('O modo generativo envia indicadores e alternativas sem nomes de clientes ao provedor, além das últimas mensagens da conversa. A cobrança e a disponibilidade dependem da sua conta API. Sem chave ou em caso de erro, o modo local continua funcionando.')
        else:
            st.caption('Modo local ativo: interpretação por regras e resultados do simulador, sem chave de API. Use as perguntas abaixo ou escreva no campo de conversa.')
    d.evidence('CONTEXTO VIGENTE',f"Experimento {data['run_id']}" if data else 'Operação nominal · nenhum incidente executado',
        f"Gargalo {data['incident']['bottleneck'] if data else b['bottleneck']} · {len(st.session_state.stations)} postos · {len(st.session_state.orders)} ordens. O botão de autorização controla cada ferramenta; o chat não executa testes automaticamente.")
    examples=['Minha CNC quebrou por 5 horas. O que devo fazer?','Tenho apenas R$ 3.000 para resolver o problema.','Compare realocar operadores com manutenção expressa.','Qual alternativa reduz os atrasos sem aumentar os custos?']
    a,b=st.columns(2)
    for j,col in enumerate([a,b]):
        with col:
            for idx in range(j,len(examples),2):
                if st.button(examples[idx],width='stretch',key='ai_example_'+str(idx)):
                    answer_question(examples[idx]);st.rerun()
    for msg in st.session_state.nx_messages:
        with st.chat_message(msg['role'],avatar=str(ROOT/'assets/brand/icon-dark.svg') if msg['role']=='assistant' else '👤'):
            if msg['label']:st.caption(msg['label']+(' · RUN '+msg['run_id'] if msg.get('run_id') else ''))
            if msg.get('run_id') and (not data or msg['run_id']!=data['run_id']):st.caption('Histórico de experimento anterior; os valores não descrevem a análise vigente.')
            st.markdown(msg['text'].replace('R$',r'R\$'))
            if msg.get('rows'):
                table=pd.DataFrame(msg['rows']).rename(columns={'action':'Alternativa','investment':'Implantação (R$)','decision_cost':'Custo final (R$)','savings':'Economia líquida (R$)','sla_pct':'SLA (%)','makespan_h':'Conclusão (h)','verdict':'Veredito','within_budget':'Orçamento OK','meets_sla':'SLA OK'})
                st.dataframe(table.rename(columns={'seed':'Semente','cost_saving':'Economia antes da implantação (R$)','sla_gain_pp':'Ganho de SLA (p.p.)','makespan_gain_h':'Redução de prazo (h)','net_saving':'Economia líquida (R$)'}),width='stretch',hide_index=True)
    render_pending()
    if st.button('Limpar conversa e plano pendente'):
        st.session_state.nx_messages=[];st.session_state.pop('nx_pending',None);st.rerun()
    q=st.chat_input('Ex.: investigue a CNC com orçamento de R$ 3.000…',max_chars=4000)
    if q:answer_question(q);st.rerun()


def model_page():
    d.hero('05 / MODELO INDUSTRIAL','O modelo é a base<br>de <em>cada decisão.</em>','Edite recursos e roteiros ou importe uma carteira. Aplicar um novo modelo invalida análises, propostas e conversas para evitar evidências antigas.')
    sdf,odf=model_frames()
    imp,edit=st.tabs(['Importar e exportar','Editar o modelo'])
    with imp:
        st.download_button('↓ Baixar modelo Excel preenchido',make_template(sdf,odf),'anti_murphy_modelo.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',width='stretch')
        uploaded=st.file_uploader('Importar modelo JSON, Excel (Postos / Ordens) ou CSV',type=['json','xlsx','csv'])
        if uploaded:
            try:
                if uploaded.name.lower().endswith('.json'):
                    payload=json.loads(uploaded.getvalue())
                    if not isinstance(payload,dict):raise ValueError('O JSON deve ser um objeto de modelo.')
                    ns,no=payload.get('stations'),payload.get('orders')
                    oi=None;warnings=[]
                    if not isinstance(ns,dict) or not isinstance(no,list):raise ValueError('JSON requer stations (objeto) e orders (lista).')
                else:
                    si,oi,warnings=read_client_workbook(uploaded)
                    ns,no=frames_to_model(si if si is not None else sdf,oi if oi is not None else odf)
                for warning in warnings:st.info(warning)
                errors=validate_model(ns,no)
                if errors:st.error(' | '.join(errors))
                else:
                    st.caption(f'Prévia: {len(ns)} postos e {len(no)} ordens. Nada foi aplicado ainda.')
                    st.dataframe(pd.DataFrame([{'ID':o['id'],'Produto':o.get('produto',''),'Quantidade':o['quantidade'],'Prazo (h)':o['prazo_h'],'Roteiro':route_to_text(o['route'])} for o in no]),hide_index=True,width='stretch')
                    if st.button('Aplicar arquivo ao workspace',type='primary'):
                        invalidate_model(st.session_state);st.session_state.stations=ns;st.session_state.orders=no
                        st.session_state.nx_source='Modelo importado pelo usuário';audit(st.session_state,'model','Importação de arquivo');st.rerun()
            except (ValueError,TypeError,KeyError,OverflowError,OSError,zipfile.BadZipFile) as exc:st.error('Não foi possível importar: '+str(exc))
        save=json.dumps({'schema':'anti-murphy-model-v30','stations':st.session_state.stations,'orders':st.session_state.orders},ensure_ascii=False,indent=2).encode()
        st.download_button('↓ Exportar modelo JSON',save,'anti_murphy_modelo.json','application/json',width='stretch')
    with edit:
        with st.form('model_edit'):
            st.markdown('**Postos de trabalho**')
            se=st.data_editor(sdf,num_rows='dynamic',width='stretch',hide_index=True,key='nx_stations_editor_'+config_signature(base_config(st.session_state)))
            st.markdown('**Ordens e roteiros**')
            st.caption('Roteiro: CORTE:4; CNC:9; MONTAGEM:6. Os tempos são minutos por peça; prazo é medido em horas desde o início do cenário.')
            oe=st.data_editor(odf,num_rows='dynamic',width='stretch',hide_index=True,key='nx_orders_editor_'+config_signature(base_config(st.session_state)))
            rule=st.selectbox('Regra de despacho',['EDD','SPT','FIFO'],index=['EDD','SPT','FIFO'].index(st.session_state.get('nx_rule','EDD')))
            seed=st.number_input('Semente de processo',0,1000000,int(st.session_state.get('nx_seed',42)),1)
            save_button=st.form_submit_button('Validar e aplicar modelo',type='primary',width='stretch')
        if save_button:
            try:
                ns,no=frames_to_model(se,oe);errors=validate_model(ns,no)
                if errors:raise ValueError(' | '.join(errors))
                invalidate_model(st.session_state);st.session_state.stations=ns;st.session_state.orders=no
                st.session_state.nx_rule=rule;st.session_state.nx_seed=int(seed);st.session_state.nx_source='Modelo editado pelo usuário'
                audit(st.session_state,'model','Modelo editado e aplicado');st.rerun()
            except (ValueError,TypeError,OverflowError) as exc:st.error(str(exc))
    with st.expander('Restaurar dados de demonstração'):
        st.caption('Troca o workspace pela carteira sintética. O modelo atual será guardado temporariamente para restauração após o pitch.')
        if st.button('Carregar carteira demonstrativa CNC'):
            use_demo(st.session_state);st.rerun()
    if 'nx_model_backup' in st.session_state and st.button('Restaurar o modelo anterior ao pitch'):
        restore_model(st.session_state);st.rerun()


def trust_page():
    d.hero('06 / EVIDÊNCIAS E LIMITES','Confiança se constrói<br>com <em>rastreabilidade.</em>','Uma simulação verificável ainda precisa de calibração. Veja o que foi testado, o que é hipótese e o que exige evidência industrial.')
    errors=validate_model(st.session_state.stations,st.session_state.orders)
    a,b=st.columns(2)
    with a:
        d.evidence('CADASTRO',f'{len(errors)} inconsistências estruturais', ' | '.join(errors) if errors else 'Postos, roteiros, números finitos, capacidade e ordens passaram na validação de entrada.')
        d.evidence('CALIBRAÇÃO','Validação com dados reais: PENDENTE','Não há homologação com uma fábrica. Tempos, custos e disponibilidade precisam de observações independentes.')
    with b:
        d.evidence('VERIFICAÇÃO','Testes incluídos no pacote','Verificam motor, custos, decisões sem benefício, estados antigos, aprovação de ferramentas e contadores do replay. O relatório técnico registra os resultados desta entrega.')
        sense=st.session_state.get('nx_sensitivity');data=current_analysis(st.session_state)
        d.evidence('INCERTEZA','8 pares calculados' if sense and data and sense.get('run_id')==data['run_id'] else 'Ainda não avaliada nesta análise','Replicações variam o ruído sintético de ciclo; não estimam a probabilidade real de sucesso de uma intervenção.')
    st.markdown('**Premissas do motor**')
    for s in ['Uma falha para o posto inteiro; não uma máquina individual. Recursos em operação ficam retidos durante a parada.',
        'Capacidade simultânea = mínimo entre máquinas e equipes possíveis por operadores/máquina. Sem turnos, horas extras ou competências individuais no DES.',
        'Transferência entre postos é instantânea. As conexões do desenho mostram dependências, não tempos de transporte.',
        'Custos de capacidade são cobrados sobre todo o horizonte de cada cenário; somam-se multas e implantação. Economia é por carteira, sem projeção anual.',
        'Intervenções de recursos e despacho valem desde o início da simulação. Não são decisões dinâmicas disparadas depois da falha.',
        'A manutenção expressa pressupõe reduzir o reparo à metade. Não modela um técnico, estoque de peças ou logística.',
        'As alternativas são enumeradas; o ranking não prova ótimo global. Nenhuma decisão física ou conexão com chão de fábrica é realizada.']:
        st.markdown('• '+s)
    st.caption('Modelo vigente: '+config_signature(base_config(st.session_state)))
    if st.session_state.audit_log:
        st.dataframe(pd.DataFrame(st.session_state.audit_log),hide_index=True,width='stretch')
        st.download_button('↓ Exportar trilha de auditoria',json.dumps(st.session_state.audit_log,ensure_ascii=False,indent=2).encode(),'anti_murphy_auditoria.json','application/json')


def pitch_page():
    d.hero('07 / PITCH MODE','Quando Murphy acontece,<br><em>a decisão aparece.</em>','Demonstração de 120 segundos com seis capítulos e resultados do motor. Dados sintéticos identificados; reprodução manual, pausa e reinício a qualquer momento.')
    a,b=st.columns([1.3,1])
    with a:
        if st.button('Preparar / reiniciar carteira sintética',type='primary',width='stretch'):
            with st.spinner('Calculando o roteiro reproduzível…'):use_demo(st.session_state)
            st.session_state.nx_pitch_revision=st.session_state.get('nx_pitch_revision',0)+1;st.rerun()
    with b:
        if 'nx_model_backup' in st.session_state and st.button('Restaurar meu modelo anterior',width='stretch'):
            restore_model(st.session_state);st.rerun()
    data=current_analysis(st.session_state)
    if not data:
        d.empty('Prepare o cenário para começar.','O botão acima calcula a carteira CNC com semente 42 e guarda seu modelo atual. Depois, pressione Reproduzir no palco.')
        return
    if data['source']!='Pitch reproduzível':st.info('O palco está usando seu experimento atual. Para a demonstração acadêmica reproduzível, prepare a carteira sintética acima.')
    render_twin(data['normal'],data,data.get('leader'),pitch=True,reduced=st.session_state.nx_reduced_motion)
    with st.expander('Roteiro de fala · apresentação completa de 5 minutos'):
        for time,title,text in [('0:00–0:40','Problema','Uma quebra de máquina não termina na manutenção: ela altera filas, prazos e custos. O PCP precisa comparar respostas antes de decidir.'),
            ('0:40–1:10','Proposta','O Anti-Murphy conecta um modelo produtivo, incidentes e alternativas. A decisão fica ligada a dados e hipóteses explícitas.'),
            ('1:10–3:10','Demonstração','Pressione Reproduzir. Acompanhe nominal, falha, impacto, alternativas, decisão e recuperação estimada.'),
            ('3:10–4:15','Diferencial','Mostre a autorização do Murphy AI e a revisão da decisão. O analista propõe; o motor calcula; a pessoa autoriza.'),
            ('4:15–5:00','Limites e próximos passos','Os dados são sintéticos. A próxima etapa é calibrar tempos, custos, competências e turnos com uma operação real. O ganho mostrado é uma evidência do modelo, não uma economia fabril validada.')]:
            st.markdown(f'**{time} · {title}** — {text}')




def factory_command_page():
    from bridge.factory_command_component import read_validated_bundle, factory_command_view
    from simulation.decision_lab import config_signature
    from bridge.experiment_source import bundle_from_workspace
    st.header('Factory Command · Futuros Paralelos')
    st.caption('Canvas com eventos calculados pelo motor DES. Nenhuma ação é executada na fábrica.')
    source=st.radio('Fonte', ['Demonstração de três postos', 'Modelo atual do workspace'],horizontal=True,key='fc_source')
    if source=='Modelo atual do workspace':
        spec=current_spec(st.session_state)
        signature=config_signature(base_config(st.session_state))+str(spec.signature())
        if st.button('Simular dois futuros para meu modelo',key='fc_build_workspace'):
            try:
                with st.spinner('Gerando eventos completos para ambos os futuros…'):
                    bundle,_,_=bundle_from_workspace(st.session_state)
                    st.session_state.fc_active_bundle=bundle
                    st.session_state.fc_active_signature=signature
            except (ValueError,TypeError,KeyError) as exc:st.error(str(exc))
        bundle=st.session_state.get('fc_active_bundle') if st.session_state.get('fc_active_signature')==signature else None
        if bundle is None:
            st.info('Execute a comparação. Alterações no modelo invalidam automaticamente o resultado anterior.')
            return
    else:
        bundle=read_validated_bundle(ROOT/'simulation_snapshot.json')
    result=factory_command_view(bundle,key='factory_command_nexus')
    if result is not None and getattr(result,'selected_station',None):
        st.caption('Posto selecionado: '+str(result.selected_station))
    st.warning('Capacidade de buffers, skills individuais e setups dependentes da sequência ainda não são impostos pelo motor. Custo do reparo não incluído.')


def main():
    if st.session_state.get('nx_legacy'):
        runpy.run_path(str(ROOT/'legacy_app.py'),run_name='__main__');return
    st.set_page_config(page_title='Anti-Murphy V30 · NEXUS',page_icon=str(ROOT/'assets/brand/icon-32.png'),layout='wide',initial_sidebar_state='expanded')
    initialize(st.session_state);d.inject();draw_sidebar()
    page=st.session_state.nx_page
    if st.session_state.pop('nx_legacy_returned',False):
        invalidate_model(st.session_state)
        st.info('Workspace sincronizado após usar as ferramentas anteriores. Execute a análise para atualizar as evidências.')
    data=current_analysis(st.session_state)
    d.top_line(page,data['run_id'] if data else None)
    issues=validate_model(st.session_state.stations,st.session_state.orders)
    if issues and page not in {'Model','Trust'}:
        st.error('O modelo precisa de correção: '+' | '.join(issues[:6]))
        if st.button('Corrigir modelo'):go('Model')
        return
    pages={'War Room':war_room,'Murphy AI':ai_page,'Evidence':evidence_page,'Review':review_page,'Model':model_page,'Trust':trust_page,'Pitch':pitch_page,'Factory Command':factory_command_page}
    pages.get(page,war_room)()
    data=current_analysis(st.session_state)
    st.markdown(f'<div class="nx-footer"><span>ANTI-MURPHY / NEXUS · MOTOR DES REPRODUZÍVEL</span><span>{d.h("RUN "+data["run_id"] if data else "SEM INCIDENTE ATIVO")} · SIMULAÇÃO / VALIDAÇÃO INDUSTRIAL PENDENTE</span></div>',unsafe_allow_html=True)


if __name__=='__main__':main()
