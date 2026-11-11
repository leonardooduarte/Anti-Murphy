"""Single workspace for the complete Anti-Murphy. No information-only landing page."""
from pathlib import Path
import runpy
import streamlit as st
from ui.brand_launch import reveal_once

ROOT=Path(__file__).resolve().parent
AREAS=('Operação','Modelo','Análises','Decisões','Registros','Mapa comparativo')
TOOLS={
 'Análise operacional': ('War Room','Visão 360','Executive Room','Operations Studio'),
 'Investigação e cenários': ('Murphy AI','Murphy Lab','Decision Evidence','Comparar','Scenario Portfolio'),
 'Otimização e robustez': ('Opportunity Engine','Optimization Hub','Stress Lab','Mission Control'),
 'Modelo e confiança': ('Modelar','Trust Center'),
}

def route_area(area):
    st.session_state['am_area']=area
    st.session_state['am_unified_shell']=True
    st.session_state.pop('op_historical',None)
    st.session_state['nx_legacy']=False
    if area=='Operação':st.session_state['op_page']='Decisão'
    elif area=='Modelo':st.session_state['op_page']='Modelo'
    elif area=='Registros':st.session_state['op_page']='Registros'
    elif area=='Decisões':st.session_state['active_page']='Decision Evidence'
    elif area=='Análises':st.session_state.setdefault('active_page','War Room')

def route_tool(tool):
    st.session_state['active_page']=tool
    st.session_state['am_area']='Análises'
    st.session_state['am_unified_shell']=True
    st.session_state.pop('op_historical',None)
    st.session_state['nx_legacy']=False

st.set_page_config(page_title='Anti-Murphy | Produção e decisões',
 page_icon=str(ROOT/'assets'/'brand'/'icon-32.png'),layout='wide',initial_sidebar_state='expanded')
# Import the same locally saved industrial model into the preserved classical UI.
# The active experiment itself is not silently imported: it must be recalculated.
if 'am_local_model_once' not in st.session_state:
    st.session_state['am_local_model_once']=True
    shared=ROOT/'workspace'/'projeto.json'
    if shared.is_file():
        try:
            import json as _json
            from simulation.validation import validate_model as _validate_model
            _model=_json.loads(shared.read_text(encoding='utf-8'))
            if not _validate_model(_model['stations'],_model['orders']):
                st.session_state['stations']=_model['stations']
                st.session_state['orders']=_model['orders']
                st.session_state['nx_rule']=_model.get('dispatch_rule','EDD')
                st.session_state['nx_source']='Modelo local compartilhado'
        except (OSError,KeyError,TypeError,ValueError):
            pass

# A navigation event originating in the operational canvas must also update
# the global shell, otherwise its destination is overwritten on the next rerun.
if st.session_state.get('op_next_page') in ('Decisão','Modelo','Registros'):
    destination=st.session_state.pop('op_next_page')
    st.session_state['am_area']={'Decisão':'Operação','Modelo':'Modelo','Registros':'Registros'}[destination]
st.session_state.setdefault('am_area','Operação')
st.session_state['am_unified_shell']=True
st.session_state.setdefault('active_page','War Room')

# The shell remains the same in all work areas.
st.markdown('<style>'+ (ROOT/'ui'/'unified_shell.css').read_text(encoding='utf8') + '</style>',unsafe_allow_html=True)
reveal_once()

with st.sidebar:
    st.image(str(ROOT/'assets'/'brand'/'logo-light.svg'),width=185)
    st.button('⌂  Voltar ao início',use_container_width=True,key='am_home',type='primary' if st.session_state.am_area=='Operação' else 'secondary',on_click=route_area,args=('Operação',))
    st.caption('Planejamento e controle da produção')
    st.markdown('<div class="am-side-heading">ÁREAS DE TRABALHO</div>',unsafe_allow_html=True)
    for area in AREAS:
        st.button(area,use_container_width=True,key='am_area_'+area,
                  type='primary' if st.session_state.am_area==area else 'secondary',
                  on_click=route_area,args=(area,))
    st.divider()
    st.markdown('<div class="am-side-heading">FERRAMENTAS</div>',unsafe_allow_html=True)
    for category,items in TOOLS.items():
        with st.expander(category,expanded=(st.session_state.am_area=='Análises' and st.session_state.get('active_page') in items)):
            for tool in items:
                st.button(tool,key='am_tool_'+tool,use_container_width=True,
                          on_click=route_tool,args=(tool,),
                          type='primary' if st.session_state.am_area=='Análises' and st.session_state.active_page==tool else 'secondary')
    st.divider()
    if st.button('Reproduzir animação da marca',use_container_width=True,key='am_intro_again'):
        reveal_once(force=True)
    if st.button('Configuração e API opcional',use_container_width=True,key='am_conf'):
        from app_classico import settings
        settings()
    st.caption('Experimentos locais · Nenhuma decisão é aplicada à fábrica física.')

area=st.session_state.am_area
# Persistent context header in every workspace.
active=st.session_state.get('active_page','War Room')
context={
 'Operação':('Operação','Acompanhe os pedidos e avalie interrupções.'),
 'Modelo':('Modelo produtivo','Cadastre recursos, roteiros, prazos e custos.'),
 'Análises':(active,'Experimentos e análises sobre o modelo atual.'),
 'Decisões':('Evidências da decisão','Compare alternativas e suas restrições.'),
 'Registros':('Registros','Consulte decisões e exporte resultados.'),
 'Mapa comparativo':('Mapa comparativo','Replay de dois cenários com a mesma referência temporal.'),
}
name,sub=context[area]
st.markdown(f'<div class="am-app-header"><span class="am-app-eyebrow">ANTI-MURPHY / ÁREA DE TRABALHO</span><div class="am-app-title">{name}</div><div class="am-app-subtitle">{sub}</div></div>',unsafe_allow_html=True)

if area in ('Operação','Modelo','Registros'):
    from app_classico import main
    st.session_state['op_page']={'Operação':'Decisão','Modelo':'Modelo','Registros':'Registros'}[area]
    main()
elif area in ('Análises','Decisões'):
    if area=='Decisões':st.session_state['active_page']='Decision Evidence'
    runpy.run_path(str(ROOT/'legacy_app.py'),run_name='__main__')
    # Applied LAST: historical dark skins cannot make text invisible on the light shell.
    st.markdown('<style>'+ (ROOT/'ui'/'classic_readability.css').read_text('utf8') + '</style>',unsafe_allow_html=True)
else:
    from ui.studio_runner import render
    render()
