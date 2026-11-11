"""Post-incident experiments: shared past, timed response, paired uncertainty."""
from dataclasses import asdict, replace
from hashlib import sha256
import json
import math
import statistics
from simulation.factory import TimedAction
from simulation.engine import run_simulation
from simulation.numeric import metric, finite
from simulation.atlas import DecisionPolicy, scenario_from_incident, _status
from simulation.decision_lab import config_signature, pareto_flags
from simulation.decision_council import enrich_decision_rows


def timed_candidates(cfg, at_h, policy):
    actions=[]
    for rule in ('EDD','FIFO','SPT'):
        if rule!=cfg.dispatch_rule:
            actions.append((TimedAction(at_h,f'Mudar despacho para {rule}',dispatch_rule=rule),0.,'Reordena apenas as operações ainda na fila.'))
    used={sid for order in cfg.orders for sid,_ in order['route']}
    for sid,s in cfg.stations.items():
        if sid not in used:continue
        actions.extend([
            (TimedAction(at_h,f'+1 operador · {sid}',workers_delta={sid:1}),policy.cost_worker,'Reforço habilitado disponível no instante da resposta; custo adicional contado a partir da entrada.'),
            (TimedAction(at_h,f'+1 máquina · {sid}',machines_delta={sid:1}),policy.cost_machine,'Capacidade reserva disponível no instante da resposta; equipe continua limitando a capacidade.')])
    for src,s in cfg.stations.items():
        available=int(s['operadores'])-int((cfg.absent_workers or {}).get(src,0))
        minimum=0 if s.get('automatizada',False) else math.ceil(float(s.get('operadores_por_maquina',1)))
        if available<=minimum:continue
        for dst in used:
            if dst==src:continue
            actions.append((TimedAction(at_h,f'Realocar operador · {src} → {dst}',workers_delta={src:-1,dst:1}),0.,'Reserva um operador no posto de origem e aguarda terminar o serviço em curso. Pressupõe habilitação para o destino.'))
    if cfg.chaos_station and cfg.chaos_duration_h:
        actions.append((TimedAction(at_h,f'Manutenção expressa · {cfg.chaos_station}',repair_remaining_factor=.5),policy.cost_express,'Reduz pela metade o reparo restante a partir da decisão. O tempo de parada já ocorrido é preservado.'))
    return actions


def analyze_response(base, station, start_h, duration_h, policy=None, *, delay_h=0., objective='cost', critical_order='', strict_budget=False):
    policy=policy or DecisionPolicy();policy.validate()
    if not math.isfinite(delay_h) or not 0<=delay_h<=168:
        raise ValueError('O tempo até responder deve estar entre zero e 168 h.')
    if objective not in ('cost','delivery','critical'):
        raise ValueError('Prioridade de decisão inválida.')
    if objective=='critical' and critical_order not in {o['id'] for o in base.orders}:
        raise ValueError('O pedido prioritário precisa pertencer à carteira atual.')
    cfg=scenario_from_incident(base,station,start_h,duration_h)
    at=start_h+delay_h
    nominal=run_simulation(base);incident=run_simulation(cfg)
    options=[(None,0.,'Aguardar o reparo original; referência da comparação.')]+timed_candidates(cfg,at,policy)
    rows=[]
    for action,investment,why in options:
        result=incident if action is None else run_simulation(cfg,action)
        label=action.label if action else 'Não intervir'
        feasible=result['feasible'] and incident['feasible']
        raw_cost=finite(metric(result,'total_cost')+investment, 'Custo da decisão') if feasible else None
        cost=round(raw_cost,2) if feasible else None
        identity=json.dumps({'model':config_signature(cfg),'response':asdict(action) if action else None},sort_keys=True)
        rows.append({'action':label,'rationale':why,'investment':float(investment),'config':cfg,'result':result,
            'timed_action':action,'signature':sha256(identity.encode()).hexdigest()[:16],
            'feasible':bool(feasible),'within_budget':investment<=policy.budget if strict_budget else policy.budget<=0 or investment<=policy.budget,
            'meets_sla':bool(feasible and metric(result,'sla_pct')>=policy.min_sla),'decision_cost':cost,
            'savings':round(metric(incident,'total_cost')-raw_cost,2) if cost is not None else None,
            'precise': {**result.get('precise',{}), 'decision_cost':raw_cost,
                        'savings':metric(incident,'total_cost')-raw_cost if raw_cost is not None else None},
            'sla_pct':metric(result,'sla_pct'),'makespan_h':metric(result,'makespan_h'),'throughput_h':metric(result,'throughput_h'),
            'late_orders':result['late_orders'],'penalty_total':result['penalty_total'],
            'requested_h':at if action else None,'effective_h':(result.get('intervention') or {}).get('effective_h'),
            'feasibility_note':'Capacidade viável no modelo' if feasible else 'Modelo bloqueado'})
    for row,flag in zip(rows,pareto_flags(rows)):row['pareto']=flag
    rows=enrich_decision_rows(rows,incident,nominal,sla_floor=policy.min_sla)
    reference_orders={o['OP']:o for o in incident['orders']}
    for r in rows:
        r['total_lateness_h']=(sum(float(o.get('lateness_h', o.get('Atraso (h)')) or 0) for o in r['result']['orders']))
        r['order_impacts']=[{'id':o['OP'],'due_h':float(o['Prazo (h)']),
            'before_h':float(reference_orders[o['OP']].get('completion_h',reference_orders[o['OP']]['Conclusão (h)'])),
            'after_h':float(o.get('completion_h',o['Conclusão (h)'])),
            'late_before':reference_orders[o['OP']]['Status']=='Atrasada','late_after':o['Status']=='Atrasada'} for o in r['result']['orders']]
        focus=next((o for o in r['order_impacts'] if o['id']==critical_order),None)
        r['critical_finish_h']=focus['after_h'] if focus else None
        r['critical_lateness_h']=max(0,focus['after_h']-focus['due_h']) if focus else None
        r['recovered_orders']=[o['id'] for o in r['order_impacts'] if o['late_before'] and not o['late_after']]
        r['restriction_reasons']=(['Capacidade insuficiente'] if not r['feasible'] else [])+(['Supera o investimento disponível'] if not r['within_budget'] else [])+(['Entregas abaixo do mínimo exigido'] if not r['meets_sla'] else [])
    valid=[r for r in rows if r['timed_action'] and r['feasible'] and r['within_budget'] and r['meets_sla']]
    eligible=[r for r in valid if
        (metric(r,'savings') if r['savings'] is not None else 0)>.005 and r['sla_pct']>=metric(incident,'sla_pct') and r['makespan_h']<=metric(incident,'makespan_h')]
    if objective=='delivery':
        eligible=[r for r in valid if r['sla_pct']>=metric(incident,'sla_pct') and (r['sla_pct']>metric(incident,'sla_pct') or r['makespan_h']<metric(incident,'makespan_h')-.005 or (metric(r,'savings') if r['savings'] is not None else 0)>.005)]
        rank=lambda r:(-r['sla_pct'],r['total_lateness_h'],r['makespan_h'],metric(r,'decision_cost'))
        reason='Prioriza mais pedidos no prazo, depois menos horas de atraso e menor conclusão da carteira; respeita orçamento e entrega mínima.'
    elif objective=='critical':
        ref=reference_orders[critical_order];before=float(ref.get('completion_h',ref['Conclusão (h)']))
        eligible=[r for r in valid if r['critical_finish_h']<before-.005]
        rank=lambda r:(r['critical_lateness_h'],r['critical_finish_h'],-r['sla_pct'],metric(r,'decision_cost'))
        reason=f'Prioriza o atraso e a conclusão de {critical_order} entre as respostas simuladas; respeita orçamento e entrega mínima. Os demais pedidos podem ter perdas.'
    else:
        rank=lambda r:(metric(r,'decision_cost'),-r['sla_pct'],r['makespan_h'])
        reason='Menor custo total entre as respostas que geram economia sem piorar entregas e conclusão, dentro do orçamento e da entrega mínima.'
    leader=min(eligible,key=rank) if eligible else None
    rows.sort(key=lambda r:(r is not leader,not (r['feasible'] and r['within_budget'] and r['meets_sla']),
                            metric(r,'decision_cost') if r['decision_cost'] is not None else float('inf')))
    status,explanation=_status(incident,nominal,leader,rows)
    if leader and objective!='cost':status='RESPOSTA PROMISSORA';explanation=reason
    if not leader and status=='RESPOSTA PROMISSORA':
        status='SEM MELHORIA VIÁVEL'
        explanation='Nenhuma resposta admissível demonstrou melhoria para a prioridade escolhida.'
    assumptions=[
        'Comparações preservam o histórico anterior à resposta; operações em andamento não são reiniciadas.',
        'A realocação aguarda um operador livre no posto de origem e pressupõe habilitação para o destino.',
        'Reforços pressupõem capacidade reserva já disponível, sem prazo de contratação ou compra.',
        'Manutenção expressa reduz 50% do tempo restante de reparo; é uma premissa configurada, sem calibração industrial.',
        'Custos de capacidade são integrados antes e depois da entrada dos recursos; implantação é cobrada separadamente.',
        'Transporte instantâneo, parada no posto inteiro, sem turnos ou atuação física. Alternativas enumeradas; não há prova de ótimo global.']
    return {'normal':nominal,'incident':incident,'rows':rows,'leader':leader,'recommended':leader,
        'model_signature':config_signature(cfg),'baseline_signature':config_signature(base),'timed_response':True,
        'decision_h':at,'delay_h':delay_h,'budget':policy.budget,'sla_floor':policy.min_sla,
        'objective':objective,'critical_order':critical_order,'strict_budget':strict_budget,'selection_reason':reason,
        'incident_parameters':{'station':station,'start_h':start_h,'duration_h':duration_h},'policy_inputs':asdict(policy),
        'policy_status':status,'policy_explanation':explanation,'eligible_count':len(eligible),'intervention_count':len(rows)-1,
        'evaluation_assumptions':assumptions,'assumptions':assumptions}


def timing_frontier(data,row):
    if not row or not row.get('timed_action'):raise ValueError('Selecione uma intervenção para comparar momentos.')
    start=data['incident_parameters']['start_h'];points=[]
    for delay in sorted({0.,1.,2.,4.,8.,float(data['delay_h'])}):
        cfg=row['config'];action=replace(row['timed_action'],at_h=start+delay)
        r=run_simulation(cfg,action)
        cost=metric(r,'total_cost')+row['investment']
        points.append({'delay_h':delay,'requested_h':action.at_h,'effective_h':r['intervention']['effective_h'],
            'net_saving':round(metric(data['incident'],'total_cost')-cost,2),'sla_pct':metric(r,'sla_pct'),
            'makespan_h':metric(r,'makespan_h'),'late_orders':r['late_orders']})
    return points


def paired_response(row, seeds=range(700,708)):
    if not row or not row.get('timed_action'):raise ValueError('Selecione uma intervenção para testar a sensibilidade.')
    pairs=[]
    for seed in seeds:
        cfg=row['config'].clone();cfg.seed=int(seed)
        incident=run_simulation(cfg);response=run_simulation(cfg,row['timed_action'])
        pairs.append({'seed':seed,'cost_saving':round(metric(incident,'total_cost')-metric(response,'total_cost'),2),
            'net_saving':round(metric(incident,'total_cost')-metric(response,'total_cost')-row['investment'],2),
            'sla_gain_pp':round(metric(response,'sla_pct')-metric(incident,'sla_pct'),2),
            'makespan_gain_h':round(metric(incident,'makespan_h')-metric(response,'makespan_h'),2)})
    return {'pairs':pairs,'mean_net_saving':statistics.mean(p['net_saving'] for p in pairs),
        'min_net_saving':min(p['net_saving'] for p in pairs),'max_net_saving':max(p['net_saving'] for p in pairs)}
