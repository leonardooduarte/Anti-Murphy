"""Regressão de acesso: evita nova ocultação de funções e looping de navegação."""
import ast
from pathlib import Path
from unittest.mock import Mock
import socket
from tools import start_nexus

ROOT=Path(__file__).resolve().parents[1]


def test_inicio_prioriza_o_workspace_original_e_nao_o_mapa():
    src=(ROOT/'app.py').read_text(encoding='utf-8')
    assert 'CORE = "Operação e decisões"' in src
    assert 'SECTIONS = [CORE, TOOLS, MAP]' in src
    assert 'initial_sidebar_state="expanded"' in src
    assert 'from app_classico import main' in src
    assert 'runpy.run_path(str(ROOT / "legacy_app.py")' in src
    assert 'from ui.studio_runner import render' in src


def test_modulos_importantes_tem_atendimento_direto():
    src=(ROOT/'app.py').read_text(encoding='utf-8')
    for page in ['War Room','Murphy AI','Decision Evidence','Murphy Lab',
                 'Optimization Hub','Stress Lab','Opportunity Engine',
                 'Scenario Portfolio','Operations Studio','Trust Center']:
        assert '"'+page+'"' in src


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
    original=Path('/mnt/data/ANTI_MURPHY_V31_OPERACAO/simulation/engine.py')
    restored=ROOT/'simulation/engine.py'
    if original.is_file():
        assert sha256(original.read_bytes()).digest()==sha256(restored.read_bytes()).digest()


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
