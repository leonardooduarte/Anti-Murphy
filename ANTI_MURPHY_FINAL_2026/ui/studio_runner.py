"""Factory Command Studio: compact, offline-first graphical surface over V30.2 DES.

The browser-only visualization intentionally does not require a Node.js build.
Its data originate exclusively from simulation.trace_export.generate_comparison.
Legacy workspace remains accessible via app_classico.py.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re

import streamlit as st

from data.scenarios import STATIONS_BASE, ORDERS_BASE
from simulation.factory import ScenarioConfig, TimedAction
from simulation.trace_export import generate_comparison, stable_model_digest
from simulation_contract import validate_reconstruction

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).with_name('factory_studio.html')


def example_config(*, station: str = 'CNC', start_h: float = 3.0,
                   duration_h: float = 12.0, quantity_scale: float = 0.60) -> ScenarioConfig:
    """Clearly labelled synthetic demo, five original production stations."""
    orders = deepcopy(ORDERS_BASE)
    for order in orders:
        order['quantidade'] = max(2, round(order['quantidade'] * quantity_scale))
    return ScenarioConfig(name='Anti-Murphy · Linha demonstrativa de cinco postos',
                          stations=deepcopy(STATIONS_BASE), orders=orders,
                          chaos_station=station, chaos_start_h=start_h,
                          chaos_duration_h=duration_h, seed=42)


def compute_bundle(cfg: ScenarioConfig, *, repair_factor: float = 0.45,
                   decision_delay_h: float = 1.0):
    decision_h = cfg.chaos_start_h + min(decision_delay_h, cfg.chaos_duration_h / 2)
    action = TimedAction(at_h=decision_h,
                         label=f'Manutenção expressa hipotética · {repair_factor:.0%} do reparo restante',
                         repair_remaining_factor=repair_factor)
    bundle, a, b = generate_comparison(cfg, action, keyframe_every=80,
                                       experiment_id='FC-STUDIO-'+hashlib.sha256((stable_model_digest(cfg)+repr((repair_factor,decision_delay_h))).encode()).hexdigest()[:12])
    validate_reconstruction(bundle)
    return bundle.model_dump(mode='json',by_alias=True), a, b


def brand_data_uri():
    import base64
    p = ROOT/'assets'/'brand'/'logo-light.svg'
    return 'data:image/svg+xml;base64,'+base64.b64encode(p.read_bytes()).decode()


def embed_html(bundle: dict) -> str:
    raw=json.dumps(bundle,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return TEMPLATE.read_text('utf8').replace('__BUNDLE_JSON__',raw).replace('__BRAND__',brand_data_uri())


def decision_summary(bundle: dict, a: dict, b: dict) -> str:
    sa, sb = bundle['branch_A']['summary'], bundle['branch_B']['summary']
    dt=(sa['makespan_us']-sb['makespan_us'])/3600000000
    dc=(sa['total_cost_cents']-sb['total_cost_cents'])/100
    return (f'O motor V30.2 calculou o makespan A de {sa["makespan_us"]/3600000000:.2f} h '
            f'e B de {sb["makespan_us"]/3600000000:.2f} h (diferença {dt:+.2f} h). '
            f'O custo operacional modelado varia R$ {dc:+,.2f}, mas exclui o custo da '
            'manutenção expressa. Buffers finitos e setups dependentes da sequência '
            'não são impostos pelo motor. Portanto, a alternativa é uma hipótese, '
            'não uma recomendação de implementação validada.')


def _decision_id(bundle:dict, choice:str)->str:
    return hashlib.sha256((bundle['experiment_id']+'|'+choice).encode()).hexdigest()[:16]


def _save_decision(bundle:dict, choice:str, rationale:str)->str:
    """Local append-only JSONL in a non-versioned folder; no physical control action."""
    target=ROOT/'registros'/'factory_command_decisions.jsonl'
    target.parent.mkdir(parents=True,exist_ok=True)
    row={'record_id':_decision_id(bundle,choice)+'-'+datetime.now(timezone.utc).strftime('%H%M%S%f'),
         'timestamp_utc':datetime.now(timezone.utc).isoformat(),
         'experiment_id':bundle['experiment_id'],'model_schema_version':bundle['schema_version'],
         'selection':choice,'rationale':rationale.strip()[:800],
         'branch_A_summary':bundle['branch_A']['summary'],
         'branch_B_summary':bundle['branch_B']['summary'],
         'qualification':'synthetic_hypothesis_not_validated_for_real_operations',
         'status':'recorded_not_applied'}
    with target.open('a',encoding='utf8') as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
    return row['record_id']



def render():
    """Interface operacional; controles de experimento em uma única barra lateral."""
    st.markdown("""<style>
    :root{color-scheme:light}
    html,body,[data-testid="stAppViewContainer"]{background:#F7F7F3!important;color:#1D292D!important}
    [data-testid="stHeader"]{background:#F7F7F3!important;height:2.75rem!important}
    [data-testid="stDecoration"]{display:none!important}
    [data-testid="block-container"]{max-width:none!important;padding:0!important;margin:0!important}
    [data-testid="stMain"]{overflow-x:hidden}
    iframe{border:0!important;display:block}
    [data-testid="stSidebar"]{background:#EDF1EC!important;border-right:1px solid #BCC9C1!important}
    [data-testid="stSidebar"] *{color:#1D292D}
    [data-testid="stSidebar"] h2{font-size:16px}
    button[kind="primary"]{background:#FF681B!important;border-color:#FF681B!important;color:#1D292D!important}
    [data-testid="stAppViewContainer"] .stAlert{border-radius:3px}
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('### Anti-Murphy')
        st.caption('Simulação de produção · V30.2')
        st.markdown('#### Configurar simulação')
        src = st.radio('Modelo', ['Demonstração de cinco postos', 'Modelo do workspace V30.2'], key='am_source')
        if src.startswith('Modelo do'):
            from simulation.operation import initialize_operation
            from simulation.nexus import base_config
            initialize_operation(st.session_state)
            default = base_config(st.session_state)
            valid = tuple(default.stations)
        else:
            default = None
            valid = tuple(STATIONS_BASE)
        with st.form('am_experiment_config'):
            station = st.selectbox('Recurso afetado', valid, index=valid.index('CNC') if 'CNC' in valid else 0)
            start = st.number_input('Início da parada (h)', min_value=0.0,max_value=1000.0,value=3.0,step=0.5)
            duration = st.number_input('Duração da parada (h)', min_value=0.5,max_value=1000.0,value=12.0,step=0.5)
            factor = st.slider('Fator de reparo hipotético',0.10,1.00,0.45,step=0.05)
            delay = st.number_input('Decisão após a parada (h)', min_value=0.0,max_value=10.0,value=1.0,step=0.5)
            submit = st.form_submit_button('Executar comparação', type='primary', use_container_width=True)
        st.caption('Alternativa B é uma hipótese. Custos de reparo adicionais não são contabilizados.')

    if submit or 'fc_studio_bundle' not in st.session_state:
        try:
            if src.startswith('Modelo do'):
                from copy import deepcopy as _deepcopy
                cfg=_deepcopy(default)
                cfg.chaos_station=station
                cfg.chaos_start_h=float(start)
                cfg.chaos_duration_h=float(duration)
                if sum(int(o['quantidade']) for o in cfg.orders)>250:
                    raise ValueError('Até 250 unidades no replay. Reduza a carteira.')
            else:
                cfg=example_config(station=station,start_h=float(start),duration_h=float(duration))
            with st.spinner('Executando simulação...'):
                bundle,a,b=compute_bundle(cfg,repair_factor=float(factor),decision_delay_h=float(delay))
            st.session_state.fc_studio_bundle=bundle
            st.session_state.fc_studio_results=(a,b)
            st.session_state.fc_studio_source=src
        except Exception as exc:
            st.error('Não foi possível concluir a simulação: '+str(exc))
            if 'fc_studio_bundle' not in st.session_state:
                return

    bundle=st.session_state.fc_studio_bundle
    a,b=st.session_state.fc_studio_results
    # O documento é compilado com os dados do DES. Nenhuma dependência npm é necessária.
    st.components.v1.html(embed_html(bundle),height=1590,scrolling=False)

    with st.sidebar:
        st.divider()
        st.markdown('#### Registrar decisão')
        with st.form('am_decision'):
            choice=st.selectbox('Alternativa',['A · Sem intervenção','B · Reparo hipotético','Nenhuma · Reavaliar'])
            rationale=st.text_area('Justificativa',height=85,
                placeholder='Documente as condições e as verificações pendentes.')
            confirm=st.form_submit_button('Registrar análise',use_container_width=True)
        if confirm:
            rec=_save_decision(bundle,choice,rationale)
            st.success('Registro local criado: '+rec)
        st.divider()
        st.markdown('#### Consulta do resultado')
        q=st.text_input('Pedido ou questão',value='A intervenção reduz os atrasos?',key='am_question')
        if st.button('Consultar cálculo',key='am_ai_answer',use_container_width=True):
            m=re.search(r'OP-\d+',q.upper())
            if m and m.group(0) in bundle['definition']['orders']:
                key=m.group(0)
                fa=bundle['branch_A']['keyframes'][-1]['orders'][key]
                fb=bundle['branch_B']['keyframes'][-1]['orders'][key]
                if fa.get('completion_us') and fb.get('completion_us'):
                    st.write(f'{key}: A = {fa["completion_us"]/3600000000:.2f} h; B = {fb["completion_us"]/3600000000:.2f} h.')
                else:
                    st.write(f'{key}: conclusão não identificada nos dois cenários.')
            st.write(decision_summary(bundle,a,b))
        st.caption('Consulta determinística; não utiliza modelo generativo nem executa ações reais.')
