"""AM-05: experiment-specific dependencies, without running an experiment.

Timestamps and execution IDs document provenance but are never configuration
identity. Constants are explicit so algorithm changes can invalidate old results.
"""
from dataclasses import asdict
import hashlib
import json

SCHEMA = 'am05-v2'
LAB_MODES = ('duration', 'dispatch', 'robustness', 'stress', 'capacity', 'goal')
ADVANCED_MODES = ('diagnostic', 'opportunities', 'sensitivity', 'demand', 'uncertainty', 'recovery')


def canonical(value):
    """JSON form: equal numeric controls 80/80.0 produce the same signature."""
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [canonical(v) for v in value]
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def signature(value):
    encoded=json.dumps(canonical(value), sort_keys=True, ensure_ascii=False,
                       separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()[:24]


def contexts(state, project_id, selected=None):
    """Map all supported tools to their current calculation dependencies.

    Model dictionaries retain an explicit station order: scenario generators use
    station iteration for seeded choices and finite candidate enumeration.
    """
    model={'stations':state['stations'], 'station_order':list(state['stations']),
           'orders':state['orders']}
    rule=state.get('nx_rule','EDD');seed=state.get('nx_seed',42)
    spec=state.get('nx_spec') or {}
    incident={k:spec.get(k) for k in ('station','start_h','duration_h')}
    nominal={**model,'dispatch_rule':rule,'seed':seed}
    crisis={**nominal,'incident':incident}
    delay=state.get('op_delay',2.)
    timed=(selected or {}).get('timed_action')
    response={'action':asdict(timed) if timed is not None else None,
              'investment':(selected or {}).get('investment')}
    deps={
        'lab:duration':{**nominal,'incident':{k:incident[k] for k in ('station','start_h')},
                        'durations_h':[0,1,2,4,6,8,12]},
        'lab:dispatch':{**model,'seed':seed,'incident':incident,'rules':['EDD','SPT','FIFO']},
        'lab:robustness':{**model,'dispatch_rule':rule,'incident':incident,
                          'response':response,'seeds':list(range(700,706))},
        'lab:stress':{**model,'dispatch_rule':rule,'runs':16,'max_absent':1,
                      'demand_low':.9,'demand_high':1.2,'durations_h':[2,4,8],'seed':2026},
        'lab:capacity':{**nominal,'max_extra_workers':2,'max_extra_machines':1,'max_results':12},
        # Goal reads the finite alternatives calculated using the full policy.
        # Selection itself is not an input; it only changes the examined row.
        'lab:goal':{**crisis,'policy':spec,'delay_h':delay},
        'advanced:diagnostic':crisis,
        'advanced:opportunities':{**nominal,'max_candidates':28},
        'advanced:sensitivity':{**nominal,'max_add':3},
        'advanced:demand':{**nominal,'demand_start':1,'demand_stop':1.6,'step':.1},
        'advanced:uncertainty':{**model,'dispatch_rule':rule,'incident':incident,
                                'runs':12,'seed_start':2100},
        'advanced:recovery':{**crisis,'delay_h':delay,'max_results':8},
    }
    for key in ('lab:stress','advanced:uncertainty'):
        deps[key]['statistics_policy']='am09-viable-only-v1'
    return {key:{'context_signature':signature({'schema':SCHEMA,'project_id':project_id,
                                                'context_key':key,'dependencies':value}),
                 'dependencies':canonical(value)} for key,value in deps.items()}


def inputs(scope, mode, payload, state):
    """Only controls actually read by the selected tool, including defaults."""
    key=scope+':'+mode
    if key in ('lab:goal','lab:capacity'):
        result={'min_sla':float(payload.get('min_sla',80))}
        if mode=='capacity':result['target_throughput']=float(payload.get('target_throughput',5.5))
    elif key=='advanced:sensitivity':
        result={'station':str(payload.get('station') or state['nx_spec']['station']),
                'resource':str(payload.get('resource') or 'operadores')}
    elif key=='advanced:demand':result={'min_sla':float(payload.get('min_sla',80))}
    else:result={}
    return canonical(result)
