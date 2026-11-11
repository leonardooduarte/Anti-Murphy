"""Prevent monetary claims copied from an old run entering the current ledger.
The invariant belongs to the service, not just a browser validator.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest

from atelier.record_integrity import parse_brl_amounts, audit_decision_note
from atelier.service import Studio, StudioError


def test_parse_brazilian_currency_not_plain_numbers():
    assert [x['cents'] for x in parse_brl_amounts('R$ 4.223,17, R$4103,67 e 40% SLA')]==[422317,410367]
    assert parse_brl_amounts('Economia 4223,17, custo 4103,67') == []
    assert [v['cents'] for v in parse_brl_amounts('R$ -2.100,50 e -R$ 3,10')]==[-210050,-310]


def test_current_result_reference_and_old_run_rejected():
    with TemporaryDirectory() as temp:
        app=Studio(Path(temp));state=app.info()
        selected=state['selected']
        action=next(x for x in state['alternatives'] if x['signature']==selected)
        assert action['savings'] is not None
        note=f"Custo modelado da decisão: R$ {action['decision_cost']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
        # API contract: reference validation uses current_analysis, independent of UI.
        from simulation.nexus import current_analysis
        analysis=current_analysis(app.state)
        chosen=next(r for r in analysis['rows'] if r['signature']==selected)
        checked=audit_decision_note(note,analysis,chosen)
        assert checked['status']=='matched',checked
        good=app.decision({'signature':selected,'note':note,'constraints_ack':True,
                           'risks':'Verificar custos evitáveis e disponibilidade antes de agir.',
                           'expected_run_id':state['run_id']})
        assert good['record']['monetary_audit']['status']=='matched'
        assert good['record']['cost_snapshot']['run_id']==state['run_id']
        with pytest.raises(StudioError,match='simulação mudou'):
            app.decision({'signature':selected,'note':note,'constraints_ack':True,
                          'expected_run_id':'run-anterior'})


def test_unmatched_amount_requires_ack_but_not_prescribed_risks():
    with TemporaryDirectory() as temp:
        app=Studio(Path(temp));state=app.info()
        action=next(x for x in state['alternatives'] if x['signature']==state['selected'])
        # Intentionally not present in the model.
        note='No experimento anterior, a diferença era R$ 987.654,32; confirmar se continua válida.'
        payload={'signature':action['signature'],'note':note,'constraints_ack':True,
                 'expected_run_id':state['run_id']}
        with pytest.raises(StudioError,match='Quantia não identificada'):
            app.decision(payload)
        saved=app.decision({**payload,'finance_ack':True})
        assert saved['record']['monetary_audit']['status']=='requires_confirmation'
        assert saved['record']['external_amounts_acknowledged'] is True
        assert saved['record']['risks']==''
        assert len(app.history())==1
