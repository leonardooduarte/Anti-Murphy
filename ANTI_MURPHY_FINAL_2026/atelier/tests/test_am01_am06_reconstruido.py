"""Regression cases rebuilt against original AM-01..AM-06 audit descriptions.
These are *new* independent tests; not the unavailable Codex test suite.
"""
from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from atelier.service import Studio, StudioError
from atelier.decision_quality import review_alternatives
from simulation.advanced import recovery_plan
from simulation.atlas import scenario_from_incident
from simulation.engine import run_simulation
from simulation.factory import build_scenario
from data.scenarios import STATIONS_BASE, ORDERS_BASE


@pytest.fixture
def studio():
    with TemporaryDirectory() as folder:
        yield Studio(Path(folder))


def test_nominal_and_banca_reference(studio):
    view=studio.info()
    assert view['spec']['duration_h']==8
    assert view['metrics']['normal']['total_cost']==8076.37
    assert view['metrics']['incident']['total_cost']==16216.67
    assert view['metrics']['incident']['late_orders']==3
    assert view['metrics']['incident']['sla_pct']==40
    assert view['metrics']['response']['total_cost']==10313.0


def test_am01_reject_invalid_priority_input_without_state_change(studio):
    old=studio.info()
    with pytest.raises(StudioError):
        studio.calculate({'rule':'INVALIDA'})
    assert studio.info()['run_id']==old['run_id']
    assert studio.info()['rule']==old['rule']


def test_am01_renamed_critical_order_does_not_leave_dangling_id(studio):
    oid=studio.info()['orders'][0]['id']
    studio.calculate({'objective':'critical','critical_order':oid})
    model={'stations':deepcopy(studio.info()['stations']),'orders':deepcopy(studio.info()['orders'])}
    model['orders'][0]['id']='OP-RENOMEADA'
    changed=studio.set_model(model)
    assert changed['spec']['objective']=='cost'
    assert changed['spec']['critical_order']==''
    again=Studio(studio.storage).info()
    assert again['orders'][0]['id']=='OP-RENOMEADA'


def test_am01_reject_missing_operators_and_keep_project(studio):
    model={'stations':deepcopy(studio.info()['stations']),'orders':deepcopy(studio.info()['orders'])}
    model['stations']['CNC']['operadores']=0
    before=studio.info()['run_id']
    with pytest.raises(StudioError, match='CNC'):
        studio.set_model(model)
    assert studio.info()['run_id']==before
    assert Studio(studio.storage).info()['stations']['CNC']['operadores']==1


def test_am01_bad_dispatch_in_existing_storage_recovers_startup(studio):
    # Corrupt the active project's rule; confirmed checkpoint is still valid.
    path=studio.storage/'projetos'/'principal.json'
    body=json.loads(path.read_text('utf-8'));body['dispatch_rule']='ABC'
    path.write_text(json.dumps(body),encoding='utf-8')
    reloaded=Studio(studio.storage).info()
    assert reloaded['rule']=='EDD'
    assert reloaded['recovery_warning']


def test_am01_transaction_rollback_preserves_files_and_memory(studio):
    import atelier.persistence as persistence
    model={'stations':deepcopy(studio.info()['stations']),'orders':deepcopy(studio.info()['orders'])}
    model['orders'][0]['quantidade']+=1
    paths=[studio.storage/'projeto.json',studio.storage/'projeto_ativo.json',
           studio.storage/'projeto_confirmado.json',studio.storage/'projetos'/'principal.json']
    originals={p:p.read_bytes() for p in paths}
    old=studio.info()['run_id']
    real_replace=persistence.os.replace
    calls=[0]
    def fail_second(src,dst):
        calls[0]+=1
        if calls[0]==2:raise OSError('simulated disk failure')
        return real_replace(src,dst)
    with patch.object(persistence.os,'replace',side_effect=fail_second):
        with pytest.raises(StudioError, match='Falha ao gravar'):
            studio.set_model(model)
    assert all(p.read_bytes()==b for p,b in originals.items())
    assert studio.info()['run_id']==old
    assert Studio(studio.storage).info()['run_id']==old


def test_am03_record_is_not_published_when_disk_write_fails(studio):
    before=studio.info()
    with patch('atelier.service.save_record',side_effect=OSError('disk full')):
        with pytest.raises(StudioError,match='não foi registrada'):
            studio.decision({'note':'Justificativa coerente com custos e prazos.'})
    after=studio.info()
    assert after['record']==before['record']==None
    assert after['selected']==before['selected']
    assert studio.history()==[]


def test_am03_prior_record_survives_subsequent_failure(studio):
    row=studio.decision({'note':'Avaliar antes de liberar a produção.'})
    first=studio.info()['record']
    with patch('atelier.service.save_record',side_effect=OSError('disk full')):
        with pytest.raises(StudioError):
            studio.decision({'note':'Uma decisão posterior que falhará ao gravar.'})
    assert studio.info()['record']==first
    assert len(studio.history())==1
    assert studio.history()[0]['filename']==row['filename']


@pytest.mark.parametrize('rule', ['EDD','SPT'])
@pytest.mark.parametrize('reversed_rows', [True, False])
def test_am02_simultaneous_order_permutation_uses_priority(rule,reversed_rows):
    station={'P':{'nome':'P','maquinas':1,'operadores':1,
                'operadores_por_maquina':1,'eficiencia_operador':1.,
                'disponibilidade':1.,'setup_min':0.,
                'custo_maquina_h':1.,'custo_operador_h':1.}}
    long={'id':'LONG','quantidade':1,'prazo_h':3.0,'multa_hora':100.,
          'release_h':0,'route':[['P',120.]]}
    short={'id':'SHORT','quantidade':1,'prazo_h':.5,'multa_hora':100.,
           'release_h':0,'route':[['P',6.]]}
    orders=[long,short] if not reversed_rows else [short,long]
    cfg=build_scenario('priority',station,orders,dispatch_rule=rule,seed=42)
    output=run_simulation(cfg)
    assert output['sla_pct']==100.0
    first=min(output['operations'],key=lambda x:x['start_h'])
    assert first['OP']=='SHORT'


def test_am02_fifo_maintains_id_tie_breaker():
    station={'P':{'maquinas':1,'operadores':1,'operadores_por_maquina':1,
                'eficiencia_operador':1,'disponibilidade':1,
                'custo_maquina_h':1,'custo_operador_h':1}}
    orders=[{'id':ident,'quantidade':1,'prazo_h':5,'multa_hora':0,'route':[['P',6]]}
            for ident in ('Z','A')]
    cfg=build_scenario('fifo',station,orders,dispatch_rule='FIFO')
    out=run_simulation(cfg)
    assert min(out['operations'],key=lambda x:x['start_h'])['OP']=='A'


def test_am04_modelled_eligibility_is_independent_of_pareto(studio):
    rows=studio.info()['alternatives']
    failing=next(x for x in rows if x['feasible'] and x['within_budget'] and not x['meets_sla'])
    decision=review_alternatives(rows,failing['signature'])
    assert decision['status']=='outside_criteria'
    # Deliberate selection below target is still supported.
    selected=studio.select(failing['signature'])
    assert selected['selected']==failing['signature']
    assert selected['decision_review']['status']=='outside_criteria'


def test_am05_stamps_change_with_scenario(studio):
    before=studio.lab({'mode':'duration'})
    assert before['provenance']['analysis_signature']==studio.info()['analysis_signature']
    studio.calculate({'duration_h':1})
    after=studio.lab({'mode':'duration'})
    assert after['provenance']['analysis_signature']==studio.info()['analysis_signature']
    assert after['provenance']['analysis_signature']!=before['provenance']['analysis_signature']
    assert len(before['points'])==7


def test_am05_stamps_change_with_selected_action(studio):
    before=studio.lab({'mode':'goal','min_sla':80})
    other=next(x['signature'] for x in studio.info()['alternatives'] if x['action']=='Não intervir')
    studio.select(other)
    after=studio.lab({'mode':'goal','min_sla':80})
    assert after['provenance']['analysis_signature']!=before['provenance']['analysis_signature']


def test_am05_stamps_change_with_lab_inputs(studio):
    before=studio.lab({'mode':'capacity','min_sla':80,'target_throughput':5.5})
    after=studio.lab({'mode':'capacity','min_sla':90,'target_throughput':5.5})
    assert before['provenance']['signature']!=after['provenance']['signature']
    assert before['provenance']['run_id']==after['provenance']['run_id']


def test_am06_operator_recovery_only_after_action(studio):
    cfg=build_scenario('base',STATIONS_BASE,ORDERS_BASE)
    crisis=scenario_from_incident(cfg,'CNC',4,8)
    before=run_simulation(crisis)
    enhanced=recovery_plan(crisis,before,max_results=8,action_at_h=6)
    row=next(x for x in enhanced if x['Ação']=='+1 operador em CNC')
    after=row['result']
    assert row['Solicitação (h)']==6
    assert after['intervention']['effective_h']==6
    assert after['makespan_h']==19.97
    assert after['sla_pct']==60.0
    prefix=lambda r:[(x['OP'],x['Unidade'],x['Etapa'],x['start_h'],x['end_h'])
                    for x in r['operations'] if x['end_h']<=6]
    assert prefix(before)==prefix(after)
    assert before['makespan_h']==24.58
    assert before['sla_pct']==40


def test_am06_recovery_does_not_mutate_initial_capacity(studio):
    cfg=build_scenario('base',STATIONS_BASE,ORDERS_BASE)
    crisis=scenario_from_incident(cfg,'CNC',4,8)
    before=json.dumps(crisis.stations,sort_keys=True)
    recovery_plan(crisis,run_simulation(crisis),action_at_h=6)
    assert json.dumps(crisis.stations,sort_keys=True)==before
    assert crisis.stations['CNC']['operadores']==1


def test_am06_advanced_includes_effective_time_and_cost_basis(studio):
    res=studio.advanced({'mode':'recovery'})
    rows=res['rows']
    cnc=next(x for x in rows if x['Ação']=='+1 operador em CNC')
    assert cnc['Solicitação (h)']==6
    assert cnc['Efetivação (h)']==6
    assert cnc['Makespan']==19.97
    assert cnc['SLA']==60
    assert cnc['Investimento adicional (R$)'] is None
