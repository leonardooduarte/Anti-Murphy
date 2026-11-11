"""Engineering evidence tests using the original DES and isolated project storage."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from atelier.service import Studio, StudioError
from atelier.technical_audit import cost_checks, summarize_audit
from simulation.nexus import current_analysis, selected_action


def test_evidence_is_derived_from_active_des_not_guessed():
    with TemporaryDirectory() as folder:
        studio=Studio(Path(folder))
        analysis=current_analysis(studio.state)
        selected=selected_action(studio.state,analysis)
        audit=studio.technical_audit()
        assert audit['run_id']==analysis['run_id']
        assert audit['model_hash']==studio._model_hash()
        assert audit['costs']['all_reconciled']
        assert audit['diagnostic']['scored_bottleneck']==analysis['incident']['bottleneck']
        for scenario in ('normal','incident','response'):
            engine=analysis[scenario] if scenario!='response' else selected['result']
            for row in engine['orders']:
                audited=next(r for r in audit['orders'][scenario] if r['id']==row['OP'])
                assert abs(audited['slack_h'] - round(row['Prazo (h)']-row['Conclusão (h)'],3))<1e-7
        assert audit['quality']['modeled'] is False
        assert audit['maintenance']['mtbf_h'] is None
        assert audit['maintenance']['mttr_h'] is None
        assert not any(audit['constraints'].values())


def test_cost_anomalies_fail_closed():
    with TemporaryDirectory() as folder:
        studio=Studio(Path(folder))
        a=current_analysis(studio.state)
        row=selected_action(studio.state,a)
        assert all(x['ok'] for x in cost_checks(a['incident'],row['result'],row))
        tampered=dict(row)
        tampered['decision_cost']=row['decision_cost']+900
        evidence=cost_checks(a['incident'],tampered['result'],tampered)
        assert not next(c for c in evidence if c['id']=='decision_total')['ok']
        assert not next(c for c in evidence if c['id']=='projected_difference')['ok']
        assert not cost_checks({'operating_cost':None,'penalty_total':0,'total_cost':0},None,None)[0]['ok']


def test_technical_audit_does_not_change_state_or_persist_files():
    with TemporaryDirectory() as folder:
        studio=Studio(Path(folder))
        state_before=studio.info()
        files_before={str(x.relative_to(folder)) for x in Path(folder).rglob('*') if x.is_file()}
        twice=[studio.technical_audit() for _ in range(2)]
        assert twice[0]==twice[1]
        assert studio.info()==state_before
        assert {str(x.relative_to(folder)) for x in Path(folder).rglob('*') if x.is_file()}==files_before


def test_audit_tracks_selected_response_and_project():
    with TemporaryDirectory() as folder:
        studio=Studio(Path(folder))
        old=studio.technical_audit()
        choices=[x for x in studio.info()['alternatives'] if x['signature']!=old['selected_signature']]
        assert choices
        studio.select(choices[0]['signature'])
        updated=studio.technical_audit()
        assert updated['run_id']==old['run_id']
        assert updated['selected_signature']==choices[0]['signature']
        clone=studio.create_project('Teste de réplica',duplicate=True)
        clone_audit=studio.technical_audit()
        assert clone_audit['project_id']!=old['project_id']
        assert clone_audit['project_id']==clone['active_project_id']


def test_structured_decision_requires_ack_when_explicitly_declined():
    with TemporaryDirectory() as folder:
        studio=Studio(Path(folder))
        a=studio.info()['selected']
        note='Revisamos capacidade, prazos, gargalos e custos para registrar o cenário escolhido.'
        with pytest.raises(StudioError,match='reconhecer'):
            studio.decision({'signature':a,'note':note,'constraints_ack':False})
        assert not studio.history()
        result=studio.decision({'signature':a,'note':note,'risks':'Confirmar habilidades, buffers, custo evitável e equipe de manutenção.',
                                'responsible':'Equipe acadêmica de PCP','constraints_ack':True})
        record=studio.read_history(result['filename'])['record']
        assert record['constraints_ack'] is True
        assert record['physical_feasibility_verified'] is False
        assert record['model_hash']==studio._model_hash()
        assert record['responsible']=='Equipe acadêmica de PCP'
        assert 'buffers' in record['risks']
