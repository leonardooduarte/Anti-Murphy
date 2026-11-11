"""Regressões de segurança de decisão e contraste; não substituem teste GUI Streamlit."""
from copy import deepcopy
from pathlib import Path
import ast
import pytest
from data.scenarios import STATIONS_BASE, ORDERS_BASE
from simulation.factory import build_scenario
from simulation.engine import run_simulation
from simulation.atlas import analyze_incident, DecisionPolicy
from simulation.murphy_agent import propose_simulation
from simulation.ai_copilot import build_ai_context, local_copilot_answer
from simulation.decision_lab import config_signature
from ui.design_system import CSS

ROOT=Path(__file__).resolve().parents[1]


def scenario():
    return build_scenario('Controle', deepcopy(STATIONS_BASE), deepcopy(ORDERS_BASE), dispatch_rule='EDD',seed=42)


def test_no_chat_background_conflict_from_v22():
    legacy=(ROOT/'ui/v22.py').read_text()
    assert 'rgba(255,255,255,.78)' not in legacy
    assert 'background:var(--am-panel)!important' in CSS
    assert 'stChatMessage' in CSS and 'stChatInput' in CSS
    assert '0.92rem' in CSS


def test_css_is_injected_last():
    source=(ROOT/'legacy_app.py').read_text()
    assert source.index('inject_design_system()') > source.index('inject_atlas_css()')
    assert source.index('inject_atlas_css()') > source.index('inject_v22_css()')


def test_trust_does_not_render_aggregate_score():
    src=(ROOT/'ui/v26.py').read_text()
    f=src[src.index('def trust_dashboard('):src.index('def skill_heatmap(')]
    assert 'Pendente' in f and 'CALIBRAÇÃO' in f and 'VERIFICAÇÃO' in f
    assert 'score:.0f' not in f


def test_stale_ai_data_uses_only_signed_analysis():
    source=(ROOT/'legacy_app.py').read_text()
    assert 'decision_data=current_atlas_analysis(),' in source
    assert 'decision_data=current_atlas_analysis() or ' not in source
    assert 'base_result_signature' in source


def test_recovery_not_invented_when_deadline_impossible():
    cfg=scenario()
    for order in cfg.orders:
        order['prazo_h']=0.5
    analysis=analyze_incident(cfg,'CNC',4,5,DecisionPolicy(budget=100,min_sla=100))
    assert analysis['leader'] is None
    assert analysis['policy_status']=='RESTRIÇÕES NÃO ATENDIDAS'


def test_normal_baseline_is_reproducible_and_no_stale_signature():
    a=scenario()
    baseline=run_simulation(a)
    b=a.clone('Outro nome')
    assert run_simulation(b)['operations']==baseline['operations']
    a.stations['CNC']['operadores'] += 1
    assert config_signature(a) != config_signature(b)


def test_local_ai_cannot_claim_performance_without_scenario():
    cfg=scenario()
    ctx=build_ai_context(run_simulation(cfg),cfg.stations)
    answer=local_copilot_answer('Compare as decisões',ctx).lower()
    assert ('não existe' in answer or 'ainda não' in answer or 'cenário' in answer)


def test_explicit_confirmation_for_simulation_proposal():
    proposal=propose_simulation('Simule uma falha de 3 horas na CNC',STATIONS_BASE)
    assert proposal and proposal.as_dict()['requires_confirmation']
    assert propose_simulation('Qual o gargalo?',STATIONS_BASE) is None


def test_economic_cost_decomposes_capacity_and_penalty():
    cfg=scenario(); result=run_simulation(cfg)
    assert result['total_cost']==pytest.approx(result['operating_cost']+result['penalty_total'],abs=.02)
    assert result['total_units']==sum(x['quantidade'] for x in cfg.orders)


def test_no_blanket_claim_of_100_percent_model_validation():
    text=(ROOT/'legacy_app.py').read_text()
    assert 'Evidence score {trust' not in text
    assert 'Validação com dados reais: PENDENTE' in text


def test_local_ai_creates_real_brief_without_decision_run():
    cfg=scenario(); ctx=build_ai_context(run_simulation(cfg),cfg.stations)
    response=local_copilot_answer('Faça um briefing executivo',ctx)
    assert 'CNC' in response or 'CORTE' in response
    assert 'Ainda não há briefing' not in response
    assert 'R$' in response


def test_local_ai_reads_atlas_leader_instead_of_legacy_field():
    cfg=scenario(); result=analyze_incident(cfg,'CNC',4,5)
    ctx=build_ai_context(run_simulation(cfg),cfg.stations,decision_data=result)
    assert ctx['decision_evidence']['policy_status']==result['policy_status']
    assert ctx['decision_evidence']['recommended']['action']==result['leader']['action']
    response=local_copilot_answer('qual a decisão recomendada?',ctx)
    assert result['leader']['action'] in response


def test_no_recommendation_when_atlas_rejects_all():
    cfg=scenario()
    for order in cfg.orders:order['prazo_h']=0.5
    result=analyze_incident(cfg,'CNC',4,5,DecisionPolicy(budget=100,min_sla=100))
    ctx=build_ai_context(run_simulation(cfg),cfg.stations,decision_data=result)
    text=local_copilot_answer('Qual sua recomendação?',ctx)
    assert 'Nenhuma recomendação automática' in text
