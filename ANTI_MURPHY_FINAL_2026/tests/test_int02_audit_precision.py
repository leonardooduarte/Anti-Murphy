"""Independent per-order timing references, including legacy and deadline edges."""
from copy import deepcopy
from decimal import Decimal
import json
from unittest.mock import patch
import pytest
from atelier.technical_audit import summarize_audit
from atelier.service import Studio
from simulation.nexus import current_analysis,selected_action


def snapshot(row):
    result={'orders':[deepcopy(row)],'stations':[]}
    return summarize_audit({'incident':result,'normal':result,'run_id':'unit'},None,
                           [{'id':'A','quantidade':1}],{},'P','hash')['orders']['normal'][0]


def row(**extra):
    return {'OP':'A','Prazo (h)':.0005,'Conclusão (h)':0.,'Multa (R$)':5.,**extra}


@pytest.mark.parametrize('finish',[.001,.0003,.0005,.0005000005,.000500002])
def test_precise_completion_and_deadline_difference_keep_sign(finish):
    expected=float(Decimal(str(.0005))-Decimal(str(finish)))
    late=max(0.,-expected)
    actual=snapshot(row(completion_h=finish,lateness_h=late))
    assert actual['finish_h']==finish
    assert actual['slack_h']==pytest.approx(expected,abs=1e-18)
    assert actual['lateness_h']==pytest.approx(late,abs=1e-18)
    assert actual['timing_source']=='precise'


@pytest.mark.parametrize('finish,status,is_late',[(.0005000005,'No prazo',False),(.000500002,'Atrasada',True)])
def test_engine_deadline_classification_is_preserved_without_new_tolerance(finish,status,is_late):
    actual=snapshot(row(completion_h=finish,lateness_h=finish-.0005,Status=status))
    assert actual['is_late'] is is_late
    assert actual['slack_h']<0


@pytest.mark.parametrize('finish',[0.,1.23])
def test_legacy_completion_falls_back_only_when_precise_key_is_absent(finish):
    actual=snapshot(row(**{'Conclusão (h)':finish}))
    assert actual['finish_h']==finish
    assert actual['slack_h']==.0005-finish
    assert actual['timing_source']=='legacy_rounded'
    assert actual['lateness_source']=='derived'


@pytest.mark.parametrize('invalid',[None,True,'bad',float('nan'),float('inf'),-1.])
def test_invalid_explicit_precise_completion_is_not_replaced_by_rounded_zero(invalid):
    actual=snapshot(row(completion_h=invalid,lateness_h=.1))
    assert actual['finish_h'] is None
    assert actual['slack_h'] is None
    assert actual['is_late'] is None
    assert actual['timing_source']=='unavailable'


@pytest.mark.parametrize('invalid',[None,True,'bad',float('nan'),float('inf'),-1.])
def test_invalid_explicit_lateness_remains_unknown(invalid):
    actual=snapshot(row(completion_h=.001,lateness_h=invalid))
    assert actual['lateness_h'] is None
    assert actual['is_late'] is None
    assert actual['lateness_source']=='unavailable'


def test_legacy_classification_is_retained_and_rounded_origin_is_identified():
    actual=snapshot(row(Status='Atrasada'))
    assert actual['is_late'] is True
    assert actual['timing_source']=='legacy_rounded'


def test_precise_zero_is_retained_and_not_replaced_by_nonzero_legacy_value():
    actual=snapshot(row(completion_h=0.,lateness_h=0.,**{'Conclusão (h)':7}))
    assert actual['finish_h']==0.
    assert actual['slack_h']==.0005


def test_real_short_cycle_all_scenarios_read_only_and_core_metrics_unchanged(tmp_path):
    s=Studio(tmp_path)
    station={'nome':'P','maquinas':2,'operadores':2,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':5,'setup_min':0}
    s.set_model({'stations':{'P':station},'orders':[{'id':'A','quantidade':2,'prazo_h':.0005,'multa_hora':10000,'route':[['P',.06]]}]})
    s.calculate({'station':'P','start_h':.0001,'duration_h':.001,'delay_h':0})
    chosen=next(r for r in s.info()['alternatives'] if r['action'].startswith('Manutenção expressa'))
    s.select(chosen['signature'])
    before=deepcopy(s.info());disk={p:p.read_bytes() for p in tmp_path.rglob('*.json')}
    analysis=current_analysis(s.state);selected=selected_action(s.state,analysis)
    with patch('atelier.service.execute',side_effect=AssertionError('audit must not simulate')):
        audited=s.technical_audit()
    for key,result in [('normal',analysis['normal']),('incident',analysis['incident']),('response',selected['result'])]:
        expected=result['orders'][0];actual=audited['orders'][key][0]
        assert actual['finish_h']==expected['completion_h']
        assert actual['slack_h']==expected['Prazo (h)']-expected['completion_h']
        assert actual['lateness_h']==expected['lateness_h']
        assert actual['is_late']==(expected['Status']=='Atrasada')
    assert s.info()==before
    assert all(p.read_bytes()==data for p,data in disk.items())
    assert audited['costs']['all_reconciled']
