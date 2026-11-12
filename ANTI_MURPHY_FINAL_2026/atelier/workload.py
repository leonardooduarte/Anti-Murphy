"""Deterministic, conservative work estimates for the local Studio only.

Resource policy, not a numerical approximation of production performance.
The standalone DES remains unrestricted and its formulas are unchanged.
"""
import math

from simulation.innovation import _capacity_plans

MAX_SCENARIO_OPERATIONS = 25_000
MAX_ANALYSIS_OPERATIONS = 250_000


def operations(orders, multiplier=1.0):
    # Same per-order demand rounding as the DES, including the minimum one unit.
    return sum(max(1, int(round(int(o['quantidade']) * multiplier))) * len(o['route']) for o in orders)


def response_scenarios(stations, orders):
    used = {sid for o in orders for sid, _ in o['route']}
    transfers = sum(len(used - {sid}) for sid, s in stations.items()
                    if int(s['operadores']) > (0 if s.get('automatizada', False)
                                               else math.ceil(float(s['operadores_por_maquina']))))
    # Nominal + incident + two other rules + two additions per used post + repair.
    return 5 + 2 * len(used) + transfers


def profile(stations, orders, scope='model', mode=''):
    nominal = operations(orders)
    multiplier = 1.0
    if scope == 'model':
        scenarios = response_scenarios(stations, orders)
    elif scope == 'lab':
        if mode == 'capacity':
            scenarios = len(_capacity_plans(stations, 2, 1)) + 1  # optional nominal cache miss
        else:
            scenarios = {'duration': 7, 'dispatch': 3, 'robustness': 12, 'stress': 16, 'goal': 0}.get(mode, 0)
        if mode == 'stress':
            multiplier = 1.2
    else:
        # Advanced tools can fill the nominal cache once before their own runs.
        # Conservative upper bounds include that run, even if already cached.
        scenarios = {'diagnostic': 1, 'opportunities': 29, 'sensitivity': 4,
                     'demand': 8, 'uncertainty': 13, 'recovery': 6}.get(mode, 0)
        if mode == 'demand':
            multiplier = 1.6
    largest = operations(orders, multiplier)
    upper = largest * scenarios
    allowed = not scenarios or (largest <= MAX_SCENARIO_OPERATIONS and upper <= MAX_ANALYSIS_OPERATIONS)
    return {'nominal_operations': nominal, 'max_scenario_operations': largest,
            'scenario_upper_bound': scenarios, 'operation_upper_bound': upper,
            'limits': {'per_scenario': MAX_SCENARIO_OPERATIONS, 'per_analysis': MAX_ANALYSIS_OPERATIONS},
            'within_limits': allowed, 'estimate_kind': 'upper_bound',
            'units': sum(int(o['quantidade']) for o in orders)}


def limit_message(p):
    def n(value): return f'{value:,}'.replace(',', '.')
    return (f'Este cálculo pode exigir até {n(p["operation_upper_bound"])} operações em '
            f'{n(p["scenario_upper_bound"])} cenários ({n(p["max_scenario_operations"])} por cenário). '
            f'O limite desta versão é {n(MAX_SCENARIO_OPERATIONS)} por cenário e '
            f'{n(MAX_ANALYSIS_OPERATIONS)} por análise. Reduza quantidades ou etapas do roteiro, '
            'ou divida o estudo em lotes. Nenhum resultado foi substituído e nenhum cenário foi iniciado.')
