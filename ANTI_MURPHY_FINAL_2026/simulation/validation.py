"""Validação do modelo fabril. Sem dependências externas.

Distingue erro cadastral de calibração: um modelo íntegro não está necessariamente
validado contra uma fábrica real.
"""
from __future__ import annotations

import math
from typing import Any


def _number(value: Any, label: str, errors: list[str], *, min_value: float = 0, strict: bool = False) -> None:
    try:
        v = float(value)
        if not math.isfinite(v) or (v <= min_value if strict else v < min_value):
            errors.append(f"{label}: número inválido (esperado {'>' if strict else '>='} {min_value}).")
    except (ValueError, TypeError, OverflowError):
        errors.append(f"{label}: informe um número válido.")


def validate_model(stations: dict, orders: list, *, demand_multiplier: float = 1.0) -> list[str]:
    errors: list[str] = []
    if not isinstance(stations, dict) or not stations:
        return ["Cadastre pelo menos um posto de trabalho."]
    if not isinstance(orders, list) or not orders:
        return ["Cadastre pelo menos uma ordem de produção."]
    _number(demand_multiplier, "Multiplicador de demanda", errors, min_value=0, strict=True)
    for sid, s in stations.items():
        if not isinstance(s, dict):
            errors.append(f"Posto {sid}: dados inválidos.")
            continue
        if 'automatizada' in s and not isinstance(s['automatizada'],bool):
            errors.append(f'Posto {sid}: automatizada deve ser true ou false no JSON.')
        for key, strict in [("maquinas", True), ("operadores", False)]:
            _number(s.get(key), f"Posto {sid} / {key}", errors, strict=strict)
            try:
                if float(s.get(key, 0)) != int(float(s.get(key, 0))):
                    errors.append(f"Posto {sid} / {key}: precisa ser inteiro.")
            except (TypeError, ValueError, OverflowError):
                pass
        for key, strict in [("operadores_por_maquina", True), ("eficiencia_operador", True),
                            ("disponibilidade", True), ("custo_maquina_h", False),
                            ("custo_operador_h", False), ("setup_min", False)]:
            _number(s.get(key, 0 if key.startswith('custo') or key == 'setup_min' else None),
                    f"Posto {sid} / {key}", errors, strict=strict)
        for key in ('disponibilidade', 'eficiencia_operador'):
            try:
                if key == 'disponibilidade' and float(s[key]) > 1:
                    errors.append(f"Posto {sid}: disponibilidade deve ser <= 1.")
            except (ValueError, TypeError, KeyError):
                pass
    ids: set[str] = set()
    for i, o in enumerate(orders, 1):
        if not isinstance(o, dict):
            errors.append(f"Ordem {i}: dados inválidos.")
            continue
        if not isinstance(o.get('id'), str) or not o.get('id', '').strip():
            errors.append(f"Ordem {i}: ID deve ser texto não vazio.")
        oid = str(o.get('id') or '').strip()
        if not oid:
            errors.append(f"Ordem {i}: ID obrigatório.")
        if oid in ids:
            errors.append(f"Ordem {oid}: ID duplicado.")
        ids.add(oid)
        for key, strict in [('quantidade', True), ('prazo_h', True), ('multa_hora', False)]:
            _number(o.get(key), f"Ordem {oid} / {key}", errors, strict=strict)
        try:
            if float(o.get('quantidade', 0)) != int(float(o.get('quantidade', 0))):
                errors.append(f"Ordem {oid}: quantidade precisa ser inteira.")
        except (TypeError, ValueError, OverflowError):
            pass
        _number(o.get('release_h', 0), f"Ordem {oid} / liberação", errors)
        if 'prioridade' in o:
            try:
                priority = float(o['prioridade'])
                if not priority.is_integer() or not math.isfinite(priority):
                    errors.append(f"Ordem {oid}: prioridade deve ser um número inteiro finito.")
            except (ValueError, TypeError, OverflowError):
                errors.append(f"Ordem {oid}: prioridade inválida.")
        route = o.get('route')
        if not isinstance(route, (list, tuple)) or not route:
            errors.append(f"Ordem {oid}: roteiro vazio ou inválido.")
            continue
        for n, step in enumerate(route, 1):
            if not isinstance(step, (list, tuple)) or len(step) != 2:
                errors.append(f"Ordem {oid}, etapa {n}: use (POSTO, minutos).")
                continue
            sid, minutes = step
            if sid not in stations:
                errors.append(f"Ordem {oid}, etapa {n}: posto '{sid}' não cadastrado.")
            _number(minutes, f"Ordem {oid}, etapa {n} / tempo (min)", errors, strict=True)
    return errors
