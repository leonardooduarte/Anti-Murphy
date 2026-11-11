from pathlib import Path
from streamlit.testing.v1 import AppTest
from simulation.operation import handle_command
from simulation.operation import initialize_operation

ROOT=Path(__file__).resolve().parents[1]


def app():return AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()


def test_current_primary_views_render_without_exceptions():
    a=app();assert not list(a.exception)
    for page in ['Modelo','Registros','Decisão']:
        a.session_state['op_page']=page;a.run()
        assert not list(a.exception)


def test_blocked_resources_show_an_error_instead_of_a_production_forecast():
    a=app();stations=dict(a.session_state['stations']);stations['CNC']=dict(stations['CNC'],operadores=0)
    a.session_state['stations']=stations;a.run()
    assert not list(a.exception)
    assert any('Modelo bloqueado' in x.value for x in a.error)


def test_evidence_exports_the_current_timed_experiment(tmp_path):
    a=app();state={};initialize_operation(state)
    # AppTest cannot operate an iframe; execute the same serialized user command
    # tested in Chromium, then verify the native export view.
    handle_command(state,{'id':'ui-demo','token':state['op_token'],'kind':'demo','body':{}})
    for key,value in state.items():a.session_state[key]=value
    a.session_state['op_store_dir']=str(tmp_path)
    a.session_state['op_page']='Registros';a.run()
    assert not list(a.exception)
    assert len(a.get('download_button'))==3
    assert any('6,00 h' in x.value for x in a.caption)
