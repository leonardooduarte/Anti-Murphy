from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from atelier.service import Studio, WorkloadLimitError
from atelier.workload import operations, profile, response_scenarios
from simulation.factory import build_scenario
from simulation.response import timed_candidates
from simulation.atlas import DecisionPolicy, scenario_from_incident


def model(quantity=10, stages=1):
    station = {'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,
               'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,
               'custo_operador_h':10,'setup_min':0}
    return {'stations':{'P':station},'orders':[{'id':'A','quantidade':quantity,
            'prazo_h':100,'multa_hora':10,'route':[['P',1]]*stages}]}


def files(folder):
    return {str(p.relative_to(folder)):p.read_bytes() for p in folder.rglob('*.json')}


@pytest.mark.parametrize('quantity,multiplier,expected', [(1,.1,2),(5,1.3,12),(5,1.5,16),(4,1.6,12)])
def test_count_uses_per_order_des_rounding(quantity, multiplier, expected):
    assert operations(model(quantity,2)['orders'],multiplier)==expected


@pytest.mark.parametrize('automated,spare', [(False,False),(False,True),(True,False),(True,True)])
def test_main_scenario_count_matches_real_candidate_enumeration(automated, spare):
    m=model()
    m['stations']['Q']=deepcopy(m['stations']['P'])
    m['stations']['Q'].update(operadores=2 if spare else 1,automatizada=automated)
    m['orders'][0]['route'].append(['Q',1])
    cfg=build_scenario('N',m['stations'],m['orders'])
    crisis=scenario_from_incident(cfg,'P',1,2)
    assert response_scenarios(m['stations'],m['orders'])==2+len(timed_candidates(crisis,2,DecisionPolicy()))


def test_scenario_and_analysis_limits_are_inclusive_and_independent():
    m=model(2500,10)
    assert profile(**m)['within_limits']
    assert not profile(**model(2500,11))['within_limits']
    m=model(2000,10)
    p=profile(**m,scope='advanced',mode='uncertainty')
    assert p['max_scenario_operations']==20000 and p['operation_upper_bound']==260000
    assert not p['within_limits']
    assert profile(**m,scope='lab',mode='goal')['within_limits']


def test_excessive_import_is_rejected_before_engine_or_disk_change(tmp_path):
    s=Studio(tmp_path);before=files(tmp_path);run=s.info()['run_id']
    with patch('atelier.service.execute') as execute:
        with pytest.raises(WorkloadLimitError,match='Nenhum resultado foi substituído'):
            s.set_model(model(2500,10000))
    execute.assert_not_called()
    assert files(tmp_path)==before and s.info()['run_id']==run


@pytest.mark.parametrize('mode', ['duration','dispatch','robustness','stress','capacity'])
def test_all_simulating_labs_check_budget_before_cloning_or_running(tmp_path,mode):
    s=Studio(tmp_path);s.state.update(model(2500,11))
    with patch('atelier.service.current_analysis',return_value={'rows':[]}),patch('atelier.service.base_config') as cfg:
        with pytest.raises(WorkloadLimitError):s.lab({'mode':mode})
    cfg.assert_not_called()


@pytest.mark.parametrize('mode', ['diagnostic','opportunities','sensitivity','demand','uncertainty','recovery'])
def test_all_advanced_tools_check_budget_before_nominal_calculation(tmp_path,mode):
    s=Studio(tmp_path);s.state.update(model(2500,11))
    with patch('atelier.service.current_analysis',return_value={'rows':[]}),patch('atelier.service.nominal') as nominal:
        with pytest.raises(WorkloadLimitError):s.advanced({'mode':mode})
    nominal.assert_not_called()


def test_demand_growth_and_capacity_candidates_are_included():
    m=model(2000,8)
    assert not profile(**m,scope='advanced',mode='demand')['within_limits']  # 1.6 × demand
    p=profile(**m,scope='lab',mode='stress')
    assert p['max_scenario_operations']==20800 and p['scenario_upper_bound']==16
    assert not p['within_limits']
    capacity=profile(**m,scope='lab',mode='capacity')
    assert capacity['scenario_upper_bound']==6  # five candidates + optional nominal


def test_large_saved_project_opens_for_editing_without_rewrite_then_recovers(tmp_path):
    s=Studio(tmp_path)
    path=tmp_path/'projetos/principal.json'
    data=json.loads(path.read_text());data.update(model(2500,11));data['spec']['station']='P';path.write_text(json.dumps(data))
    before=files(tmp_path)
    with patch('atelier.service.execute') as execute:
        reopened=Studio(tmp_path)
    assert execute.call_count==0
    info=reopened.info()
    assert info['calculation_blocked'] and info['run_id'] is None and info['metrics'] is None
    assert info['orders']==data['orders'] and info['replay']=={}
    assert 'aberto para edição' in info['recovery_warning']
    assert files(tmp_path)==before
    reduced=reopened.set_model(model(10,2))
    assert not reduced['calculation_blocked'] and reduced['run_id'] and reduced['recovery_warning'] is None


def test_switch_to_large_project_preserves_its_archived_bytes(tmp_path):
    s=Studio(tmp_path);data=json.loads((tmp_path/'projetos/principal.json').read_text())
    data.update(model(2500,11));data.update(id='grande',name='Grande');data['spec']['station']='P'
    path=tmp_path/'projetos/grande.json';path.write_text(json.dumps(data))
    s=Studio(tmp_path);before=files(tmp_path)
    with patch('atelier.service.execute') as execute:info=s.open_project('grande')
    execute.assert_not_called()
    assert info['active_project_id']=='grande' and info['calculation_blocked']
    assert files(tmp_path)==before


def test_opportunities_do_not_clone_discarded_candidates():
    from simulation.decisions import generate_opportunities
    m=model();cfg=build_scenario('N',m['stations'],m['orders'])
    original=cfg.clone
    with patch.object(cfg,'clone',wraps=original) as clone,patch('simulation.decisions.run_simulation',return_value={'feasible':False}):
        assert generate_opportunities(cfg,{},max_candidates=1)==[]
    assert clone.call_count==1
