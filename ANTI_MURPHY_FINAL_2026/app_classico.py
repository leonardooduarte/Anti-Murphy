"""Anti-Murphy: one operational workspace connected to the retained DES."""
from pathlib import Path
from copy import deepcopy
from dataclasses import replace,asdict
import json
import os
import runpy
from uuid import uuid4
import pandas as pd
import streamlit as st
from data.importer import read_client_workbook,make_template
from simulation.nexus import current_analysis,current_spec,selected_action,invalidate_model,restore_model,audit,nominal
from simulation.operation import initialize_operation,payload,handle_command,memo,report
from simulation.validation import validate_model
from simulation.model_io import frames_to_model
from simulation.nexus_ai import brl,fmt
from ui.operation_component import render_operation
from app_nexus_v30 import model_frames
ROOT=Path(__file__).resolve().parent


def commit_model(stations,orders,source):
    errors=validate_model(stations,orders)
    if errors:raise ValueError(' | '.join(errors[:8]))
    invalidate_model(st.session_state)
    st.session_state.pop('nx_model_backup',None)
    st.session_state.stations=deepcopy(stations);st.session_state.orders=deepcopy(orders)
    st.session_state.nx_source=source;st.session_state.op_token=uuid4().hex
    if current_spec(st.session_state).station not in stations:
        st.session_state.nx_spec=asdict(replace(current_spec(st.session_state),station=next(iter(stations))))
    if current_spec(st.session_state).critical_order not in {o['id'] for o in orders}:
        st.session_state.nx_spec=asdict(replace(current_spec(st.session_state),critical_order='',objective='cost'))
    audit(st.session_state,'model',source)


@st.dialog('Configuração',width='medium')
def settings():
    st.subheader('Murphy')
    st.selectbox('Modo de análise',['Local · sem API','Generativo · OpenAI'],key='nx_ai_mode')
    for key,default in [('nx_api_key',''),('nx_ai_model','gpt-4.1-mini')]:
        st.session_state[key]=st.session_state.get(key,default)
    if st.session_state.nx_ai_mode=='Generativo · OpenAI':
        st.text_input('Chave da API · somente nesta sessão',type='password',key='nx_api_key')
        st.text_input('Modelo OpenAI',key='nx_ai_model')
        import importlib.util
        if importlib.util.find_spec('openai') is None:
            st.info('Execute INSTALAR_IA_OPCIONAL.bat para instalar o provedor opcional.')
        st.caption('A conversa e os indicadores resumidos são enviados ao provedor. Disponibilidade e custos dependem da sua conta. O modo local permanece disponível.')
    else:
        st.caption('Interpretação por regras e dados calculados pelo simulador. Funciona sem chave e sem internet após a instalação.')
    st.divider()
    st.subheader('Ferramentas técnicas preservadas')
    st.caption('Otimização, laboratório e portfólio da versão anterior. Mantêm a interface histórica e comparam cenários integrais.')
    def _open_previous_tools():
        st.session_state['am_area'] = 'Análises'
        st.session_state['active_page'] = 'War Room'
        st.session_state['op_historical'] = False
        st.session_state['nx_legacy'] = False
    st.button('Abrir ferramentas anteriores',width='stretch',on_click=_open_previous_tools)
    if 'nx_model_backup' in st.session_state:
        if st.button('Restaurar modelo anterior à demonstração',width='stretch'):
            restore_model(st.session_state);st.session_state.op_token=uuid4().hex;st.rerun()


def model_page():
    st.header('Modelo industrial')
    st.caption('Recursos, carteira e roteiros dos experimentos. Aplicar alterações invalida resultados e autorizações anteriores.')
    if st.session_state.pop('op_model_saved',False):st.success('Modelo aplicado. As análises e autorizações anteriores foram invalidadas.')
    station_df,order_df=model_frames()
    station_df['Automatizada']=[s.get('automatizada',False) for s in st.session_state.stations.values()]
    order_df['Liberação (h)']=[o.get('release_h',0.) for o in st.session_state.orders]
    edit,imp=st.tabs(['Editar recursos e pedidos','Importar ou exportar'])
    with edit:
        st.subheader('Postos e recursos')
        ss=st.data_editor(station_df,num_rows='dynamic',hide_index=True,width='stretch',key='op_station_editor_'+st.session_state.op_token)
        st.subheader('Ordens de produção')
        st.caption('Roteiro: ID_DO_POSTO:minutos; ID_DO_POSTO:minutos.')
        oo=st.data_editor(order_df,num_rows='dynamic',hide_index=True,width='stretch',key='op_order_editor_'+st.session_state.op_token)
        if st.button('Aplicar modelo e invalidar análises anteriores',type='primary'):
            try:
                stations,orders=frames_to_model(ss,oo)
                for _,r in ss.iterrows():
                    sid=str(r['ID']).strip().upper()
                    if sid in stations:
                        stations[sid]={**st.session_state.stations.get(sid,{}),**stations[sid]}
                release={str(r['ID']).strip().upper():float(r.get('Liberação (h)',0)) for _,r in oo.iterrows()}
                for order in orders:order['release_h']=release[order['id']]
                commit_model(stations,orders,'Modelo editado pelo usuário')
                st.session_state.op_model_saved=True;st.rerun()
            except (ValueError,TypeError,KeyError) as exc:st.error(str(exc))
    with imp:
        a,b=st.columns(2)
        with a:st.download_button('Baixar modelo Excel',make_template(station_df,order_df),'anti_murphy_modelo.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',width='stretch')
        with b:st.download_button('Baixar modelo JSON',json.dumps({'stations':st.session_state.stations,'orders':st.session_state.orders},ensure_ascii=False,indent=2).encode(),'anti_murphy_modelo.json','application/json',width='stretch')
        uploaded=st.file_uploader('Importar JSON, Excel ou CSV',type=['json','xlsx','csv'])
        if uploaded:
            try:
                if uploaded.name.lower().endswith('.json'):
                    model=json.loads(uploaded.getvalue());stations,orders=model['stations'],model['orders'];warnings=[]
                else:
                    si,oi,warnings=read_client_workbook(uploaded)
                    if si is None:si=station_df
                    if oi is None:oi=order_df
                    stations,orders=frames_to_model(si,oi)
                errors=validate_model(stations,orders)
                if errors:raise ValueError(' | '.join(errors[:8]))
                st.write(f'{len(stations)} postos · {len(orders)} ordens')
                for warning in warnings:st.warning(warning)
                if st.button('Aplicar arquivo importado',type='primary'):
                    commit_model(stations,orders,'Modelo importado · '+uploaded.name)
                    st.session_state.op_model_saved=True;st.rerun()
            except (ValueError,TypeError,KeyError) as exc:st.error(str(exc))


def archived_section():
    from simulation.decision_store import archived_records
    saved=archived_records(st.session_state['op_store_dir'])
    if not saved:return
    with st.expander(f"Decisões arquivadas neste computador ({len(saved)})"):
        st.caption('Os arquivos preservam a análise original. Consultar um arquivo não altera o modelo em uso.')
        labels={item['filename']:item['data']['record']['utc'][:19].replace('T',' ')+' UTC · '+item['data']['record']['action'] for item in saved}
        selected=st.selectbox('Registro arquivado',list(labels),format_func=lambda name:labels[name],key='op_archive_choice')
        item=next(i for i in saved if i['filename']==selected)
        record=item['data']['record'];examined=item['data']['examined_action']
        st.write(record.get('note') or 'Sem observação adicional.')
        st.caption('Economia líquida '+brl(examined['savings'])+' · '+fmt(examined['sla_pct'])+'% dos pedidos no prazo · experimento '+item['data']['run_id'])
        st.download_button('Baixar registro arquivado',item['raw'],item['filename'],'application/json')


def evidence_page():
    st.header('Registro da decisão')
    st.caption('O que foi escolhido, quais entregas mudam e quais condições sustentam a decisão.')
    archived_section()
    data=current_analysis(st.session_state)
    if not data:
        st.info('Calcule uma parada na área Decisão e ensaie uma resposta para produzir o registro.')
        return
    row=selected_action(st.session_state,data);record=st.session_state.get('op_record')
    if record and record['run_id']==data['run_id']:
        st.success('Decisão registrada no computador: '+record['action'])
        if record.get('note'):st.write('Motivo registrado: '+record['note'])
        if row and record['signature']!=row['signature']:
            st.warning('Você está examinando outra resposta. Os arquivos distinguem a análise em exibição da decisão registrada.')
    else:st.info('Prévia da análise. Ensaie e registre a escolha na área Decisão para formalizar o resultado.')
    if row:
        st.subheader(row['action'])
        a,b,c=st.columns(3)
        a.metric('Economia líquida prevista',brl(row['savings']))
        b.metric('Pedidos no prazo',fmt(row['sla_pct'])+'%')
        c.metric('Conclusão da carteira',fmt(row['makespan_h'])+' h')
        if row.get('requested_h') is not None:
            st.caption(f"Solicitada em {fmt(row['requested_h'])} h · efetiva em {fmt(row['effective_h'])} h · implantação {brl(row['investment'])}")
        for restriction in row.get('restriction_reasons',[]):st.warning(restriction)
        impacts=pd.DataFrame([{'Pedido':o['id'],'Prazo':fmt(o['due_h'])+' h',
            'Aguardar reparo':fmt(o['before_h'])+' h','Resposta em exame':fmt(o['after_h'])+' h',
            'Efeito':'Recupera o prazo' if o['late_before'] and not o['late_after'] else 'Continua em atraso' if o['late_after'] else 'Mantém o prazo'} for o in row.get('order_impacts',[])])
        if not impacts.empty:st.dataframe(impacts,hide_index=True,width='stretch')
    st.caption(data.get('selection_reason',''))
    columns=['action','investment','decision_cost','savings','sla_pct','makespan_h','requested_h','effective_h','within_budget','meets_sla']
    frame=pd.DataFrame([{k:r.get(k) for k in columns} for r in data['rows']]).rename(columns={
        'action':'Resposta','investment':'Implantação (R$)','decision_cost':'Custo total (R$)',
        'savings':'Economia líquida (R$)','sla_pct':'Pedidos no prazo (%)','makespan_h':'Conclusão (h)',
        'requested_h':'Solicitação (h)','effective_h':'Entrada efetiva (h)',
        'within_budget':'Dentro do orçamento','meets_sla':'Atende à entrega mínima'})
    a,b,c=st.columns(3)
    with a:st.download_button('Memorando JSON',memo(st.session_state),'anti_murphy_decisao.json','application/json',width='stretch')
    with b:st.download_button('Relatório HTML',report(st.session_state),'anti_murphy_decisao.html','text/html',width='stretch')
    with c:st.download_button('Matriz CSV',frame.to_csv(index=False,sep=';',decimal=',').encode('utf-8-sig'),'anti_murphy_respostas.csv','text/csv',width='stretch')
    with st.expander('Todas as respostas calculadas'):st.dataframe(frame,hide_index=True,width='stretch')
    timing=st.session_state.get('op_timing')
    if timing and timing['run_id']==data['run_id']:
        with st.expander('Efeito de esperar para responder'):
            st.write(timing['action']);st.dataframe(pd.DataFrame(timing['points']).rename(columns={
                'delay_h':'Espera após a falha (h)','requested_h':'Solicitação (h)','effective_h':'Entrada efetiva (h)',
                'net_saving':'Economia líquida (R$)','sla_pct':'No prazo (%)','makespan_h':'Conclusão (h)','late_orders':'Pedidos atrasados'}),hide_index=True,width='stretch')
    sensitivity=st.session_state.get('nx_sensitivity')
    if sensitivity and sensitivity['run_id']==data['run_id']:
        with st.expander('Variação em oito pares de sementes'):
            st.write(sensitivity['action']);st.dataframe(pd.DataFrame(sensitivity['pairs']),hide_index=True,width='stretch')
    with st.expander('Dados, hipóteses e rastreabilidade'):
        st.write('Fonte: '+st.session_state.get('nx_source','Modelo do usuário'))
        st.write('Experimento: '+data['run_id'])
        st.write('Sugestão para a prioridade atual: '+(data['leader']['action'] if data['leader'] else 'Nenhuma resposta demonstra melhoria dentro das restrições.'))
        for assumption in data['evaluation_assumptions']:st.markdown('- '+assumption)
        st.caption('Caso CNC sintético. Sem calibração com dados de uma fábrica nem atuação física.')
        st.dataframe(pd.DataFrame(st.session_state.get('audit_log',[])),hide_index=True,width='stretch')


def main():
    if st.session_state.get('op_historical'):
        if st.session_state.get('nx_legacy'):
            runpy.run_path(str(ROOT/'legacy_app.py'),run_name='__main__');return
        st.session_state.pop('op_historical',None);invalidate_model(st.session_state)
        st.session_state.op_token=uuid4().hex
    # Streamlit page configuration is applied once by the new main entrypoint.
    initialize_operation(st.session_state)
    st.session_state.setdefault('op_store_dir',os.environ.get('AM_RECORD_DIR',str(ROOT/'registros')))
    for key in ('nx_ai_mode','nx_api_key','nx_ai_model'):
        if key in st.session_state:st.session_state[key]=st.session_state[key]
    st.markdown('<style>'+(ROOT/'ui/operation_shell.css').read_text(encoding='utf-8')+'</style>',unsafe_allow_html=True)
    if st.session_state.get('op_next_page'):
        st.session_state.op_page=st.session_state.pop('op_next_page')
    if st.session_state.get('op_page') not in (None,'Decisão','Modelo','Registros','Factory Command'):
        st.session_state.op_page='Decisão'
    if st.session_state.get('am_unified_shell'):
        page = st.session_state.get('op_page', 'Decisão')
        if page not in ('Decisão','Modelo','Registros'):
            page='Decisão'
    else:
        logo,nav,utility=st.columns([1.4,3.4,.8],vertical_alignment='center')
        with logo:st.image(str(ROOT/'assets/brand/logo-light.svg'),width=185)
        with nav:page=st.segmented_control('Área',['Decisão','Modelo','Registros'],default='Decisão',required=True,label_visibility='collapsed',key='op_page',width='stretch')
        with utility:
            if st.button('Configuração',width='stretch'):settings()
    if page=='Modelo':model_page()
    elif page=='Registros':evidence_page()
    else:
        errors=validate_model(st.session_state.stations,st.session_state.orders)
        if errors:st.error('Revise o modelo: '+' | '.join(errors[:6]));return
        baseline=nominal(st.session_state)
        if not baseline.get('feasible',True):
            st.error('Modelo bloqueado: '+' | '.join(baseline.get('warnings',[])))
            st.info('Revise os recursos na aba Modelo. Não foram calculadas previsões de entrega para uma operação sem capacidade mínima.')
            return
        value=render_operation(payload(st.session_state))
        if handle_command(st.session_state,value):st.rerun()


if __name__=='__main__':main()

