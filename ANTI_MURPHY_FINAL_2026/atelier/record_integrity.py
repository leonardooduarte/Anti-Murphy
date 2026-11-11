"""Conservative, deterministic audit of Brazilian-real amounts quoted in decisions.

This does NOT verify free-form financial claims in general. It detects explicitly
prefixed R$ values that fail to match the current synthetic run's known outputs.
No LLM, external API, modification to simulation economics, or silent rewriting.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

MONEY = re.compile(r'(?<!\w)([-−]?\s*R\$\s*[-−]?\s*)((?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d{1,2})?)(?!\d|[.,]\d)', re.IGNORECASE)
CENT = Decimal('0.01')


def cents(value):
    try:
        return int((Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)) * 100)
    except (ValueError, TypeError, InvalidOperation):
        return None


def parse_brl_amounts(note):
    found = []
    for match in MONEY.finditer(str(note or '')):
        normalized = match.group(2).replace('.', '').replace(',', '.')
        sign = -1 if '-' in match.group(1) or '−' in match.group(1) else 1
        value = cents(Decimal(normalized) * sign)
        if value is not None:
            found.append({'written': match.group(0).strip(), 'cents': value})
    return found


def money_reference_values(analysis, selection):
    """Only numbers genuinely computed by the active experiment.

    Include components to avoid flagging a legitimately discussed fine or
    investment. The presence of an amount on this list is not proof that its
    interpretation in a narrative is correct.
    """
    sources = {}
    for label, run in (
        ('Operação nominal', analysis.get('normal') or {}),
        ('Falha sem intervenção', analysis.get('incident') or {}),
        ('Resposta selecionada', selection.get('result') or {}),
    ):
        for key, description in (
            ('total_cost', 'custo total'),
            ('operating_cost', 'custo operacional'),
            ('penalty_total', 'multas por atraso'),
        ):
            val = cents(run.get(key))
            if val is not None:
                sources.setdefault(val, []).append(f'{label} · {description}')
    for key, description in (
        ('decision_cost', 'custo da decisão'),
        ('investment', 'investimento modelado'),
        ('savings', 'diferença econômica modelada'),
    ):
        val = cents(selection.get(key))
        if val is not None:
            sources.setdefault(val, []).append(description)
    return sources


def audit_decision_note(note, analysis, selection):
    known = money_reference_values(analysis, selection)
    amounts = parse_brl_amounts(note)
    unknown = [x for x in amounts if x['cents'] not in known]
    matched = [{**x, 'sources': known[x['cents']]} for x in amounts if x['cents'] in known]
    return {
        'status': 'requires_confirmation' if unknown else ('matched' if amounts else 'no_explicit_amounts'),
        'found_count': len(amounts),
        'matched': matched,
        'unmatched': unknown,
        'scope': 'Somente valores explicitamente escritos com R$; a coerência textual, outras unidades e custos externos não são certificados.',
    }


def cost_snapshot(analysis, selection):
    response = selection.get('result') or {}
    incident = analysis.get('incident') or {}
    return {
        'run_id': analysis.get('run_id'),
        'action': selection.get('action'),
        'incident_total_cost': incident.get('total_cost'),
        'response_total_cost': response.get('total_cost'),
        'response_operating_cost': response.get('operating_cost'),
        'response_penalty_total': response.get('penalty_total'),
        'investment': selection.get('investment'),
        'decision_cost': selection.get('decision_cost'),
        'savings': selection.get('savings'),
        'units': 'BRL; valores do modelo sintético',
    }
