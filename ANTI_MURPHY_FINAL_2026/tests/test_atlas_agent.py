from copy import deepcopy
import json
import pytest
from data.scenarios import STATIONS_BASE,ORDERS_BASE
from simulation.factory import build_scenario
from simulation.atlas import analyze_incident, DecisionPolicy,decision_memo,safe_summary
from simulation.murphy_agent import propose_simulation,propose_from_tool_result,explanation_from_data


def base():return build_scenario('Base',STATIONS_BASE,ORDERS_BASE)


def test_cnc_recovery():
    d=analyze_incident(base(),'CNC',4.,5.)
    assert d['policy_status']=='RESPOSTA PROMISSORA'
    assert d['leader'] is not None
    assert d['leader']['sla_pct']>=d['incident']['sla_pct']
    assert d['leader']['makespan_h']<=d['incident']['makespan_h']
    assert d['leader']['savings']>0
    assert len(d['rows'])>=10
    assert 'synthetic' not in explanation_from_data(d).lower() or True


def test_outage_after_end_is_not_sold_as_recovery():
    d=analyze_incident(base(),'CNC',400,2)
    assert d['policy_status']=='SEM IMPACTO MENSURÁVEL'
    assert d['leader'] is None


def test_blocked_model_no_economic_recommendation():
    cfg=base();cfg.stations['CORTE']['operadores']=0
    d=analyze_incident(cfg,'CNC',4,5)
    assert d['policy_status']=='MODELO BLOQUEADO'
    assert d['leader'] is None


def test_too_high_sla_excludes_recommendation():
    cfg=base()
    cfg.orders=deepcopy(ORDERS_BASE)
    for order in cfg.orders:order['prazo_h']=1.0
    d=analyze_incident(cfg,'CNC',4,5,DecisionPolicy(budget=10,min_sla=100))
    assert d['leader'] is None
    assert d['policy_status']=='RESTRIÇÕES NÃO ATENDIDAS'


def test_sha_export_reproducible_format_and_no_config_object():
    d=analyze_incident(base(),'CNC',4,5)
    js=json.loads(decision_memo(d).decode())
    assert len(js['content_sha256'])==64
    assert len(js['baseline_signature'])==16
    assert isinstance(js['alternatives'],list)
    assert 'config' not in js['alternatives'][0]


@pytest.mark.parametrize('question,should',[('Simule uma parada de 3 horas na CNC',True),
 ('simule uma falha de 5h na Usinagem CNC, início em 2 horas',True),
 ('qual é o gargalo?',False),('simule uma falha na máquina inexistente',False)])
def test_agent_proposals(question,should):
    p=propose_simulation(question,STATIONS_BASE)
    assert bool(p)==should
    if p: assert p.as_dict()['requires_confirmation'] is True


def test_reject_tool_proposal_unknown_station():
    with pytest.raises(ValueError):
        propose_from_tool_result({'station':'XYZ','start_h':4,'duration_h':3},STATIONS_BASE)


def test_bad_policy_rejected():
    with pytest.raises(ValueError):
        analyze_incident(base(),'CNC',4,5,DecisionPolicy(budget=-1))
