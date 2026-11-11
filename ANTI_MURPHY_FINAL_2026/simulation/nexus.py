"""Versioned decision workspace shared by every V30 screen; no UI dependency."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from data.scenarios import STATIONS_BASE, ORDERS_BASE, DEFAULT_RULE, DEFAULT_SEED
from simulation.factory import build_scenario
from simulation.engine import run_simulation
from simulation.atlas import analyze_incident, DecisionPolicy
from simulation.decision_lab import config_signature


@dataclass(frozen=True)
class ExperimentSpec:
    station: str = 'CNC'
    start_h: float = 4.0
    duration_h: float = 5.0
    budget: float = 10000.0
    min_sla: float = 80.0
    cost_worker: float = 1200.0
    cost_machine: float = 6500.0
    cost_express: float = 1800.0
    objective: str = 'cost'
    critical_order: str = ''
    budget_is_limit: bool = False

    def policy(self):
        return DecisionPolicy(**{k: v for k, v in asdict(self).items() if k not in ('station','start_h','duration_h','objective','critical_order','budget_is_limit')})

    def signature(self):
        return hashlib.sha256(json.dumps(asdict(self),sort_keys=True).encode()).hexdigest()[:16]

    def validate(self, stations):
        self.policy().validate()
        if self.objective not in ('cost','delivery','critical'):
            raise ValueError('Escolha uma prioridade válida para a decisão.')
        if not isinstance(self.budget_is_limit,bool):
            raise ValueError('Informe se o orçamento é um limite.')
        if self.objective=='critical' and not self.critical_order:
            raise ValueError('Selecione o pedido que precisa ser protegido.')
        if self.station not in stations:
            raise ValueError('Selecione um posto cadastrado no modelo.')
        if not all(math.isfinite(v) for v in (self.start_h,self.duration_h)) or not 0<=self.start_h<=500 or not 0<self.duration_h<=168:
            raise ValueError('Início entre 0 e 500 h; duração maior que zero e até 168 h.')


def initialize(state):
    for k,v in {'stations':STATIONS_BASE,'orders':ORDERS_BASE,'nx_spec':asdict(ExperimentSpec()),
                'nx_page':'War Room','nx_messages':[], 'audit_log':[], 'decision_history':[],
                'nx_reduced_motion':False,'nx_source':'Carteira demonstrativa · sintética'}.items():
        if k not in state:
            state[k]=deepcopy(v)


def base_config(state):
    return build_scenario('Operação nominal',state['stations'],state['orders'],
                          dispatch_rule=state.get('nx_rule',DEFAULT_RULE),seed=state.get('nx_seed',DEFAULT_SEED))


def current_spec(state):
    return ExperimentSpec(**state['nx_spec'])


def audit(state, kind, detail, **fields):
    state['audit_log'] = (state.get('audit_log',[])+[{'utc':datetime.now(timezone.utc).isoformat(),
        'kind':kind,'detail':detail,**fields}])[-120:]


def current_analysis(state):
    data=state.get('v29_analysis')
    if not data or data.get('baseline_signature')!=config_signature(base_config(state)):
        return None
    if data.get('spec_signature') != current_spec(state).signature():
        return None
    return data


def nominal(state):
    cfg=base_config(state); signature=config_signature(cfg)
    if state.get('base_result_signature') != signature or not state.get('base_result'):
        state['base_result']=run_simulation(cfg)
        state['base_result_signature']=signature
    return state['base_result']


def execute(state, spec: ExperimentSpec, *, source='War Room', authorization=None):
    """Publish only after all calculations succeed, so errors never half-commit state."""
    spec.validate(state['stations'])
    cfg=base_config(state)
    if state.get('op_enabled'):
        from simulation.response import analyze_response
        result=analyze_response(cfg,spec.station,spec.start_h,spec.duration_h,spec.policy(),delay_h=float(state.get('op_delay',0.)),objective=spec.objective,critical_order=spec.critical_order,strict_budget=spec.budget_is_limit)
    else:
        result=analyze_incident(cfg,spec.station,spec.start_h,spec.duration_h,spec.policy())
    result['spec_signature']=spec.signature()
    result['run_id']=hashlib.sha256((config_signature(cfg)+spec.signature()+str(result.get('decision_h',''))).encode()).hexdigest()[:12]
    result['source']=source
    state['nx_spec']=asdict(spec)
    state['v29_analysis']=result
    # Compatibility aliases for existing V29 modules, all referencing the same run.
    state['v27_decisions']=result
    state['v27_incident']=result['incident']['config']
    state['nx_selected']=result['leader']['signature'] if result['leader'] else None
    state.pop('nx_sensitivity',None)
    state.pop('op_timing',None)
    state.pop('op_record',None)
    audit(state,'simulation',f'{source}: {spec.station}, {spec.duration_h:g} h',
          run_id=result['run_id'], model=result['baseline_signature'], authorization=authorization)
    return result


def selected_action(state, data=None):
    data=data or current_analysis(state)
    if not data:return None
    return next((r for r in data['rows'] if r['signature']==state.get('nx_selected')),data.get('leader'))


def invalidate_model(state):
    for k in list(state.keys()):
        if k.startswith(('nx_pending','nx_sensitivity','v21_','v23_','v24_','v25_','v27_','v29_')) or k in {
            'base_result','base_result_signature','scenario_result','scenario_config','opportunities','goal_results','stress_results'}:
            state.pop(k,None)
    state['nx_messages']=[]
    state['decision_history']=[]
    state.pop('nx_selected',None)
    state.pop('nx_model_editor',None)
    state.pop('op_timing',None)
    state.pop('op_record',None)


def use_demo(state):
    """Explicit reset requested by a demo button; preserves the user's model for restore."""
    if 'nx_model_backup' not in state:
        state['nx_model_backup']={k:deepcopy(state.get(k)) for k in ('stations','orders','nx_spec','nx_source','nx_rule','nx_seed')}
    invalidate_model(state)
    state['stations']=deepcopy(STATIONS_BASE);state['orders']=deepcopy(ORDERS_BASE)
    state['nx_source']='Carteira demonstrativa · sintética';state['nx_rule']='EDD';state['nx_seed']=42
    execute(state,ExperimentSpec(duration_h=8.0,budget_is_limit=bool(state.get('op_enabled'))),source='Caso CNC reproduzível')


def restore_model(state):
    backup=state.pop('nx_model_backup',None)
    if backup:
        invalidate_model(state)
        for k,v in backup.items():
            if v is not None:state[k]=v
            else:state.pop(k,None)
        audit(state,'model','Modelo anterior restaurado após o pitch')
