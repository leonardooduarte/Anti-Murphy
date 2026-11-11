"""Release-gate checks for grounded Murphy responses, costs and decision persistence."""
from pathlib import Path
from tempfile import TemporaryDirectory
from math import isclose
import pytest
from atelier.service import Studio, StudioError
from simulation.nexus import current_analysis, selected_action


def test_murphy_separates_bottleneck_from_longest_wait_and_reports_orders():
    with TemporaryDirectory() as temp:
        studio=Studio(Path(temp)); analysis=current_analysis(studio.state)
        before=studio.info()
        response=studio.assistant('Qual o gargalo da operação e quais pedidos estão em risco? Posto selecionado CNC')
        text=response['text']
        assert 'GARGALOS E PEDIDOS' in response['label']
        assert f"Gargalo identificado pelo motor no cenário de parada: {analysis['incident']['bottleneck']}" in text
        station_rows=analysis['incident']['stations']
        longest=max(station_rows,key=lambda r:r['Espera média (min)'])
        assert f"Maior espera média registrada: {longest['Posto']}" in text
        actual={r['OP'] for r in analysis['incident']['orders'] if r['Atraso (h)']>0}
        assert actual and all(x in text for x in actual)
        assert 'não comprova execução física' in text
        after=studio.info()
        assert before['run_id']==after['run_id'] and before['selected']==after['selected']
        assert before['metrics']==after['metrics']


def test_murphy_answer_for_capacity_is_not_an_unexecuted_simulation():
    with TemporaryDirectory() as temp:
        studio=Studio(Path(temp))
        response=studio.assistant('E se eu aumentar a capacidade da CNC?')
        assert 'não alterei o modelo nem calculei um cenário novo' in response['text'].lower()
        assert 'Otimização de capacidade' in response['text']


def test_costs_and_operator_intervention_only_claim_modeled_feasibility():
    with TemporaryDirectory() as temp:
        studio=Studio(Path(temp)); analysis=current_analysis(studio.state)
        actions=analysis['rows']
        assert actions
        for row in actions:
            sim=row.get('result')
            if not sim or row.get('decision_cost') is None:continue
            assert isclose(sim['operating_cost']+sim['penalty_total'],sim['total_cost'],abs_tol=.05)
            assert isclose(sim['total_cost']+row['investment'],row['decision_cost'],abs_tol=.05)
            assert isclose(analysis['incident']['total_cost']-row['decision_cost'],row['savings'],abs_tol=.05)
        response=studio.assistant('A realocação de operador para a CNC é fisicamente viável?')
        assert 'NÃO confirma viabilidade física' in response['text']


def test_decision_validation_persistence_and_readback():
    with TemporaryDirectory() as temp:
        folder=Path(temp); studio=Studio(folder)
        before=studio.info(); selected=selected_action(studio.state,current_analysis(studio.state))
        with pytest.raises(StudioError,match='12 caracteres'):
            studio.decision({'signature':selected['signature'],'note':'curto'})
        assert studio.history()==[]
        note='Escolhida para comparação porque reduz atrasos no modelo; validar habilidades e custos reais.'
        record=studio.decision({'signature':selected['signature'],'note':note})
        assert record['record']['note']==note
        assert len(studio.history())==1
        result=studio.read_history(record['filename'])
        assert result['record']['note']==note
        assert studio.info()['run_id']==before['run_id']
        assert studio.info()['selected']==before['selected']
        restarted=Studio(folder)
        assert restarted.history()[0]['note']==note
