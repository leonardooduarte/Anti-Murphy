"""Historical V30 interface regressions. Current UI flows are in test_operation_ui.py and browser_qa.js."""
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]


def app():return AppTest.from_file(str(ROOT/'app_nexus_v30.py'),default_timeout=30).run()
def assert_clean(a):assert not list(a.exception),[(x.message,x.stack_trace) for x in a.exception]


def test_primary_pages_and_shared_run_after_demo():
    a=app();assert_clean(a)
    a.button[0].click().run();assert_clean(a)
    run_id=a.session_state['v29_analysis']['run_id']
    for key in ['nav_Evidence','nav_Review','nav_Murphy AI','nav_Model','nav_Trust','nav_Pitch']:
        a.button(key=key).click().run();assert_clean(a)
        assert a.session_state['v29_analysis']['run_id']==run_id


def test_ai_budget_authorization_then_evidence_and_review():
    a=app();a.button[0].click().run();a.button(key='nav_Murphy AI').click().run()
    a.button(key='ai_example_1').click().run();assert_clean(a)
    plan=a.session_state['nx_pending'];assert plan['spec']['budget']==3000
    assert a.session_state['v29_analysis']['policy_inputs']['budget']==10000
    a.button(key='authorize_'+plan['id']).click().run();assert_clean(a)
    assert a.session_state['v29_analysis']['policy_inputs']['budget']==3000
    assert 'nx_pending' not in a.session_state
    a.button(key='ai_example_2').click().run();assert_clean(a)
    assert any(m['rows'] for m in a.session_state['nx_messages'])
    a.button(key='nav_Evidence').click().run();assert_clean(a)
    a.button(key='nav_Review').click().run();assert_clean(a)
    a.button[-1] if False else None


def test_sensitivity_authorization_in_review_and_no_rerun_on_navigation():
    a=app();a.button[0].click().run();a.button(key='nav_Review').click().run()
    next(b for b in a.button if b.label=='Preparar teste com 8 sementes').click().run();assert_clean(a)
    plan=a.session_state['nx_pending'];assert plan['kind']=='sensitivity'
    a.button(key='authorize_'+plan['id']).click().run();assert_clean(a)
    result=a.session_state['nx_sensitivity'];assert len(result['pairs'])==8
    a.button(key='nav_Trust').click().run();assert_clean(a)
    assert a.session_state['nx_sensitivity']==result


def test_original_tools_open_and_return_to_new_workspace():
    a=app()
    next(b for b in a.button if b.label=='Abrir ferramentas anteriores').click().run();assert_clean(a)
    a.button(key='nx_return_from_legacy').click().run();assert_clean(a)
    assert a.session_state['nx_legacy'] is False
