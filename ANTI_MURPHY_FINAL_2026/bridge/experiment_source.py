"""Converts an active V30.2 workspace into a real, hypothetical A/B DES trace.

This is explicitly NOT the complete NEXUS decision optimizer. It is a single
express-maintenance hypothesis, with feasibility still unverified.
"""
from dataclasses import replace
from simulation.factory import TimedAction
from simulation.nexus import base_config, current_spec
from simulation.trace_export import generate_comparison
from simulation_contract import validate_reconstruction


def bundle_from_workspace(session_state):
    cfg = base_config(session_state)
    spec = current_spec(session_state)
    if spec.station not in cfg.stations or spec.duration_h <= 0:
        raise ValueError('Selecione um incidente válido antes de comparar futuros.')
    cfg.chaos_station=spec.station
    cfg.chaos_start_h=float(spec.start_h)
    cfg.chaos_duration_h=float(spec.duration_h)
    requested=cfg.chaos_start_h + min(0.5,cfg.chaos_duration_h/2)
    action=TimedAction(at_h=requested,label='Manutenção expressa (hipótese: 50% do reparo restante)',
                       repair_remaining_factor=0.5)
    total_units=sum(int(order['quantidade']) for order in cfg.orders)
    if total_units > 250:
        raise ValueError('Demonstração limitada a 250 unidades para evitar travar a interface.')
    bundle,baseline,reply=generate_comparison(cfg,action,keyframe_every=30,
        experiment_id='FC-WORKSPACE-'+str(cfg.seed)+'-'+spec.station)
    validate_reconstruction(bundle)
    return bundle.model_dump(mode='json',by_alias=True),baseline,reply
