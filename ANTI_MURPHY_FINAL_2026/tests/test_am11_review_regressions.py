"""Independent AM-11 review references for float range and legacy JSON."""
from decimal import Decimal, localcontext
import pytest

from simulation.numeric import metric, product_ratio
from simulation.decision_council import _safe_pct


def test_nonzero_subnormal_intermediate_product_uses_representable_reference():
    a, denominator = 1e-160, 1e-320
    with localcontext() as context:
        context.prec = 80
        expected = float(Decimal.from_float(a) * Decimal.from_float(a)
                         / Decimal.from_float(denominator))
    assert product_ratio((a, a), (denominator,), 'Referência') == pytest.approx(expected, rel=1e-14)


@pytest.mark.parametrize('sign', [1, -1])
def test_recovery_percentage_avoids_intermediate_overflow(sign):
    assert _safe_pct(sign * 1e308, 1e308) == pytest.approx(sign * 100)


def test_unrepresentable_percentage_is_explicit_error():
    with pytest.raises(ValueError):
        _safe_pct(1.0, float.fromhex('0x0.0000000000001p-1022'))


def test_null_precise_legacy_summary_falls_back_to_rounded_metric():
    assert metric({'makespan_h': 3.25, 'precise': None}, 'makespan_h') == 3.25


def test_cost_component_underflow_is_explicit_not_free_production():
    from unittest.mock import patch
    from simulation.engine import run_simulation
    from simulation.factory import ScenarioConfig
    cfg=ScenarioConfig('underflow', {'P': {'nome':'P','maquinas':1,'operadores':1,
        'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,
        'custo_maquina_h':1e-320,'custo_operador_h':0,'setup_min':0}},
        [{'id':'A','quantidade':1,'prazo_h':1,'multa_hora':0,'route':[('P',6e-9)]}])
    with patch('simulation.engine._noise',return_value=1), pytest.raises(ValueError,match='representação'):
        run_simulation(cfg)


def test_zero_cost_and_automated_zero_labor_remain_valid():
    from unittest.mock import patch
    from simulation.engine import run_simulation
    from simulation.factory import ScenarioConfig
    cfg=ScenarioConfig('free', {'P': {'nome':'P','maquinas':1,'operadores':0,'automatizada':True,
        'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,
        'custo_maquina_h':0,'custo_operador_h':0,'setup_min':0}},
        [{'id':'A','quantidade':1,'prazo_h':1,'multa_hora':0,'route':[('P',.06)]}])
    with patch('simulation.engine._noise',return_value=1):
        result=run_simulation(cfg)
    assert result['precise']['total_cost']==0
    assert result['stations'][0]['precise']['worker_util_pct']==0
