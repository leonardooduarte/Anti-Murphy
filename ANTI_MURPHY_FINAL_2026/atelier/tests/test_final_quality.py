"""Finalization checks: same DES, transparent decision accounting, read-only explanations."""
from pathlib import Path
from tempfile import TemporaryDirectory
from math import isclose

from atelier.service import Studio
from simulation.nexus import current_analysis, selected_action


def studio_fixture():
    temp=TemporaryDirectory()
    return temp,Studio(Path(temp.name))


def test_cost_components_reconcile_with_selected_decision():
    temp,s=studio_fixture()
    try:
        info=s.info();analysis=current_analysis(s.state)
        selected=selected_action(s.state,analysis)
        sim=selected['result']
        assert isclose(sim['operating_cost']+sim['penalty_total'],sim['total_cost'],abs_tol=.031)
        assert isclose(sim['total_cost']+selected['investment'],selected['decision_cost'],abs_tol=.031)
        assert isclose(analysis['incident']['total_cost']-selected['decision_cost'],selected['savings'],abs_tol=.031)
        assert s.info()['run_id']==info['run_id']
    finally: temp.cleanup()


def test_assistant_cost_detail_uses_current_engine_data_and_does_not_modify_selection():
    temp,s=studio_fixture()
    try:
        before=s.info()
        resp=s.assistant('Explique operação, multas, investimento e custo da decisão')
        after=s.info()
        assert 'COMPOSIÇÃO DE CUSTOS' in resp['label']
        assert 'Operação:' in resp['text'] and 'Investimento modelado' in resp['text']
        assert 'não é economia real' in resp['text'].lower()
        assert before['run_id']==after['run_id']
        assert before['selected']==after['selected']
        assert before['metrics']==after['metrics']
    finally:temp.cleanup()


def test_unmodeled_constraints_not_certified_by_assistant():
    temp,s=studio_fixture()
    try:
        resp=s.assistant('É viável realocar um operador com habilitação e buffer finito?')
        assert 'NÃO confirma viabilidade física' in resp['text']
        assert 'buffers' in resp['text']
    finally:temp.cleanup()


def test_order_specific_answer_does_not_invent_missing_order():
    temp,s=studio_fixture()
    try:
        present=s.info()['orders'][0]['id']
        resp=s.assistant(f'Por que o pedido {present} está atrasado?')
        assert present in resp['text'] and 'prazo' in resp['text'].lower()
        missing=s.assistant('Por que o pedido OP-9999 atrasou?')
        assert 'não existe no modelo atual' in missing['text']
    finally:temp.cleanup()


def test_dashboard_costs_are_read_only_and_consistent():
    temp,s=studio_fixture()
    try:
        before=s.info()
        d=s.dashboards()
        action=d['selected_action'];respond=d['scenarios']['response']['metrics']
        assert isclose(float(action['decision_cost']),float(respond['total_cost'])+float(action['investment']),abs_tol=.031)
        assert before['run_id']==s.info()['run_id']
    finally:temp.cleanup()
