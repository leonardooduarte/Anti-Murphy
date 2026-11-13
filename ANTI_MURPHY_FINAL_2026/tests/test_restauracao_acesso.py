"""Regressão de acesso: evita nova ocultação de funções e looping de navegação."""
import ast
from pathlib import Path
from unittest.mock import Mock
import socket
from tools import start_nexus

ROOT=Path(__file__).resolve().parents[1]


def test_inicio_prioriza_o_workspace_original_e_nao_o_mapa():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    assert not list(app.exception)
    assert app.session_state['am_area']=='Operação'
    for area in ('Modelo','Registros','Mapa comparativo','Operação'):
        app.button(key='am_area_'+area).click().run()
        assert not list(app.exception)
        assert app.session_state['am_area']==area
    app.button(key='am_home').click().run()
    assert app.session_state['am_area']=='Operação'


def test_modulos_importantes_tem_atendimento_direto():
    from streamlit.testing.v1 import AppTest
    for page in ['War Room','Murphy AI','Decision Evidence','Murphy Lab',
                 'Optimization Hub','Stress Lab','Opportunity Engine',
                 'Scenario Portfolio','Operations Studio','Trust Center']:
        # Each tool must be reachable directly from a fresh public home.
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
        app.button(key='am_tool_'+page).click().run()
        assert not list(app.exception),page
        assert app.session_state['active_page']==page
        assert app.session_state['am_area']=='Análises'


def test_caminho_de_recarregamento_infinito_foi_retirado():
    src=(ROOT/'app_classico.py').read_text(encoding='utf-8')
    assert 'fc_nav_requested' not in src
    assert "['Decisão','Modelo','Registros']" in src
    assert 'on_click=_open_previous_tools' in src


def test_app_define_configuracao_uma_unica_vez():
    roots=[ROOT/'app.py',ROOT/'legacy_app.py',ROOT/'app_classico.py']
    calls=[]
    for p in roots:
        tree=ast.parse(p.read_text('utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='set_page_config':
                calls.append(p.name)
    assert calls==['app.py']


def test_retorno_de_legacy_nao_reentra_em_legacy():
    src=(ROOT/'legacy_app.py').read_text('utf-8')
    assert 'on_click=_return_to_operation' in src
    assert "st.session_state['op_historical'] = False" in src


def test_engine_inalterado_no_pacote_de_restauracao():
    from hashlib import sha256
    import json
    expected=json.loads((ROOT/'docs/AM19/base-reference.json').read_text('utf-8'))['sha256']['simulation/engine.py']
    assert sha256((ROOT/'simulation/engine.py').read_bytes()).hexdigest()==expected



def test_launcher_abre_navegador_sem_npm():
    code=(ROOT/'tools/start_nexus.py').read_text('utf-8')
    assert 'threading.Thread(target=open_browser_when_ready' in code
    assert 'webbrowser.open(url, new=2)' in code
    assert '--server.headless=true' in code
    assert not (ROOT/'node_modules').exists()


def test_choose_port_skips_porta_ocupada():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0))
        busy=s.getsockname()[1]
        assert start_nexus.available_port(busy, attempts=2)==busy+1
