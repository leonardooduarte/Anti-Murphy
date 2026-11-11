"""Independent, read-only consistency checks for DES decision support.

This module deliberately does NOT call the simulation engine, change schedules,
create quality/maintenance observations or certify physical feasibility.
"""
from __future__ import annotations

from math import isfinite


def _num(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        v = float(value)
        return v if isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _near(a, b, tolerance=0.075):
    x, y = _num(a), _num(b)
    return x is not None and y is not None and abs(x-y) <= tolerance


def cost_checks(incident, response, selected):
    """Check DES cost identities at cent-level rounding tolerance."""
    checks = []
    for key, row in [('incident', incident), ('response', response)]:
        if not row:
            checks.append({'id': key, 'ok': False, 'description': 'Cenário sem dados calculados'})
            continue
        op, penalty, total = [row.get(x) for x in ('operating_cost', 'penalty_total', 'total_cost')]
        valid = _num(op) is not None and _num(penalty) is not None
        checks.append({'id': f'{key}_cost', 'ok': valid and _near(_num(op)+_num(penalty), total),
                       'description': ('Sem intervenção' if key=='incident' else 'Com intervenção')+' · custo do cenário = capacidade contratada + multas'})
    if selected and response:
        investment = _num(selected.get('investment'))
        total = _num(response.get('total_cost'))
        decision = selected.get('decision_cost')
        baseline = _num(incident.get('total_cost')) if incident else None
        checks.extend([
            {'id': 'decision_total', 'ok': investment is not None and total is not None and
             _near(investment+total, decision),
             'description': 'Custo de decisão = custo do cenário + investimento modelado'},
            {'id': 'projected_difference', 'ok': baseline is not None and _num(decision) is not None and
             _near(baseline-_num(decision), selected.get('savings')),
             'description': 'Diferença estimada = custo sem resposta − custo de decisão'},
        ])
    return checks


def summarize_audit(analysis, selected, orders, spec, project_id, model_hash):
    """Project contextual evidence; no values guessed for missing industrial data."""
    baseline = analysis['incident']
    response = selected.get('result') if selected else None
    nominal = analysis.get('normal') or {}
    by_id = {o['id']: o for o in orders}
    out = {}
    for name, result in [('normal', nominal), ('incident', baseline), ('response', response)]:
        if not result:
            continue
        detail = []
        for row in result.get('orders', []):
            due, finish = _num(row.get('Prazo (h)')), _num(row.get('Conclusão (h)'))
            if due is None or finish is None:
                continue
            slack = round(due-finish, 3)
            detail.append({'id': row.get('OP'), 'client': row.get('Cliente'),
                           'due_h': due, 'finish_h': finish, 'slack_h': slack,
                           'lateness_h': max(0, round(-slack, 3)),
                           'penalty': _num(row.get('Multa (R$)')),
                           'units': by_id.get(row.get('OP'), {}).get('quantidade')})
        out[name] = detail
    stations = baseline.get('stations') or []
    longest_wait = max(stations, key=lambda x: float(x.get('Espera média (min)') or 0)) if stations else None
    largest_queue = max(stations, key=lambda x: int(x.get('Fila máx.') or 0)) if stations else None
    bottleneck = baseline.get('bottleneck')
    checks = cost_checks(baseline, response, selected)
    outage = {'station': spec.get('station'), 'start_h': spec.get('start_h'),
              'scheduled_duration_h': spec.get('duration_h'),
              'scheduled_end_h': round(float(spec.get('start_h') or 0)+float(spec.get('duration_h') or 0), 5),
              'mtbf_h': None, 'mttr_h': None}
    return {'schema_version':'1.0', 'run_id':analysis['run_id'], 'project_id':project_id,
            'model_hash':model_hash, 'selected_signature':selected.get('signature') if selected else None,
            'orders':out,
            'diagnostic':{'scored_bottleneck':bottleneck,
                          'highest_mean_wait':longest_wait.get('Posto') if longest_wait else None,
                          'highest_mean_wait_min':longest_wait.get('Espera média (min)') if longest_wait else None,
                          'largest_queue_station':largest_queue.get('Posto') if largest_queue else None,
                          'largest_queue_units':largest_queue.get('Fila máx.') if largest_queue else None,
                          'methodology':'Indicador de criticidade: utilização de máquina + min(50, espera média [min]/2) + 2 × fila máxima. Não é prova de restrição estrutural.',
                          'validation':'Para confirmar uma restrição, execute teste de incremento marginal de capacidade e compare throughput, custo e atrasos.'},
            'maintenance':outage,
            'costs':{'checks':checks, 'all_reconciled': bool(checks) and all(c['ok'] for c in checks),
                     'basis':'Custos de capacidade contratada por máquinas e operadores ao longo do horizonte simulado; multas de atraso e investimento da ação separados. Não equivale a fluxo de caixa efetivo.'},
            'quality':{'modeled':False,
                       'note':'Refugo, retrabalho, inspeção e rendimento conforme não estão parametrizados no motor atual. Não calcular OEE, FPY ou taxa real de defeitos.'},
            'constraints':{'individual_skills_verified':False,'finite_buffers_verified':False,
                           'sequence_dependent_setups_verified':False,'physical_maintenance_resources_verified':False},
            'reference':'Todos os valores vêm do experimento sintético ativo, sem telemetria industrial.'}
