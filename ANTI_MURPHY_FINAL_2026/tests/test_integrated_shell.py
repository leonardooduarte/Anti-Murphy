"""Guardrails so that redesign cannot silently remove the historical product."""
import ast
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def test_only_one_streamlit_page_config():
    entries=('app.py','app_classico.py','legacy_app.py')
    found=[]
    for file in entries:
        for node in ast.walk(ast.parse((ROOT/file).read_text(encoding='utf8'))):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='set_page_config':
                found.append(file)
    assert found==['app.py']


def test_full_function_inventory_visible_in_shell():
    shell=(ROOT/'app.py').read_text(encoding='utf8')
    required=['War Room','Murphy AI','Decision Evidence','Murphy Lab','Comparar','Modelar',
              'Visão 360','Opportunity Engine','Optimization Hub','Stress Lab','Scenario Portfolio',
              'Operations Studio','Trust Center','Mission Control','Executive Room']
    assert all(repr(name) in shell for name in required)
    assert "from app_classico import main" in shell
    assert "runpy.run_path(str(ROOT/'legacy_app.py')" in shell
    assert "from ui.studio_runner import render" in shell


def test_original_logo_is_used_for_restored_splash():
    splash=(ROOT/'ui'/'brand_launch.py').read_text('utf8')
    assert "BRAND / 'icon-dark.svg'" in splash
    assert 'am_intro_seen' in splash
    assert 'prefers-reduced-motion' in splash
    assert 'pointer-events:none' in splash
    assert 'Decision Twin' not in splash


def test_legacy_navigation_is_managed_by_shared_shell():
    classic=(ROOT/'app_classico.py').read_text('utf8')
    legacy=(ROOT/'legacy_app.py').read_text('utf8')
    shell=(ROOT/'app.py').read_text('utf8')
    assert "am_unified_shell" in classic
    assert "am_unified_shell" in legacy
    assert "op_next_page" in shell
    assert "'Registros'" in shell
    assert 'initial_sidebar_state=\'expanded\'' in shell


def test_animation_only_uses_engine_station_state():
    js=(ROOT/'ui'/'operation'/'operation.js').read_text('utf8')
    assert 'stationState(p,i,t)' in js
    assert 'Math.min(9,st.queue)' in js
    assert 'st.down?' in js
    assert 'st.processing' in js
    assert 'machine-working' in js
    css=(ROOT/'ui'/'operation'/'operation.css').read_text('utf8')
    assert '.machine-working .work-wave' in css
    assert 'prefers-reduced-motion' in css


def test_core_engine_is_bitwise_preserved():
    original=Path('/mnt/data/ANTI_MURPHY_RESTAURACAO_FUNCIONAL/simulation/engine.py')
    if original.is_file():
        assert sha256((ROOT/'simulation'/'engine.py').read_bytes()).digest()==sha256(original.read_bytes()).digest()


def test_windows_launcher_no_npm_build_and_browser_auto_open():
    scripts=list(ROOT.glob('*.bat'))
    assert [p.name for p in scripts]==['INICIAR_ANTI_MURPHY.bat']
    start=(ROOT/'tools'/'start_nexus.py').read_text('utf8')
    assert 'threading.Thread(target=open_browser_when_ready' in start
    assert 'webbrowser.open(url, new=2)' in start
    assert not any(x.name=='node_modules' for x in ROOT.rglob('node_modules'))


def test_no_font_files_distributed():
    assert not any(p.suffix.lower() in {'.ttf','.otf','.woff','.woff2'} for p in ROOT.rglob('*'))
