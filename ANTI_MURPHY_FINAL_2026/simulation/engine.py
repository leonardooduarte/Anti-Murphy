"""Anti-Murphy V27: motor de eventos discretos verificável e reproduzível.

Implementação com Python padrão (sem dependência operacional de SimPy).
Mantém o formato de saída da V26 para compatibilidade com as telas existentes.
Hipóteses: operadores_por_maquina determina a capacidade simultânea do posto; eventos de parada
indisponibilizam um posto inteiro; operação interrompida segura os recursos,
mas o tempo parado NÃO é contado como processamento/ocupação produtiva.
Disponibilidade/eficiência são fatores de ciclo; custos dos ativos são cobrados
pelo horizonte integral do cenário (modelo de custo de capacidade contratada).
Essas hipóteses não substituem calibração industrial.
"""
from __future__ import annotations

import hashlib
import heapq
import math
import random
from collections import defaultdict
from copy import deepcopy
from itertools import count
from typing import Any, Protocol

from simulation.factory import ScenarioConfig, TimedAction
from simulation.validation import validate_model
from simulation.numeric import finite, present, product_ratio


class SimulationResult(dict):
    """Resultado em formato dicionário com suporte ao acesso por atributo."""
    def __getattr__(self, name):
        try: return self[name]
        except KeyError as exc: raise AttributeError(name) from exc


def _noise(seed: int, order_id: str, unit: int, step: int) -> float:
    """Randomização comum entre alternativas: não depende da ordem de despacho."""
    payload = f"{seed}|{order_id}|{unit}|{step}".encode('utf-8')
    n = int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), 'big')
    return random.Random(n).triangular(.96, 1.05, 1.0)


def _priority(order: dict, cycle_min: float, rule: str, arrival: float, unit: int):
    if rule == 'SPT':
        return (float(cycle_min), float(order['prazo_h']), arrival, str(order['id']), unit)
    if rule == 'FIFO':
        return (arrival, str(order['id']), unit)
    return (float(order['prazo_h']), int(order.get('prioridade', 9)), arrival, str(order['id']), unit)


def _infeasible(config: ScenarioConfig, stations: dict, orders: list, blocked: list[str]):
    """Não fabrica produção/conclusões quando faltam recursos obrigatórios."""
    order_rows = []
    for order in orders:
        order_rows.append({'OP':order['id'], 'Cliente':order.get('cliente',''),
            'Produto':order.get('produto',''), 'Quantidade':int(order['quantidade_sim']),
            'Prazo (h)':float(order['prazo_h']), 'Conclusão (h)':None, 'Atraso (h)':None,
            'Multa (R$)':None, 'Status':'Bloqueada'})
    station_rows = []
    for sid, s in stations.items():
        station_rows.append({'Posto':sid,'Nome':s.get('nome',sid),
            'Máquinas':int(s['maquinas']),'Operadores':int(s['available_workers']),
            'Utilização máquina (%)':0.0,'Utilização mão de obra (%)':0.0,
            'Espera média (min)':0.0, 'Fila máx.':0, 'Custo cenário (R$)':0.0})
    return SimulationResult({'name':config.name, 'dispatch_rule':config.dispatch_rule,
        'feasible':False,'blocked_stations':blocked,
        'warnings':[f"Sem operadores disponíveis em: {', '.join(blocked)}. A operação é inviável; não foi calculado resultado econômico."],
        'makespan_h':0.0,'total_units':0,'planned_units':sum(x['quantidade_sim'] for x in orders),
        'throughput_h':0.0,'sla_pct':0.0,'late_orders':len(orders),
        'penalty_total':0.0,'operating_cost':0.0,'total_cost':0.0,'unit_cost':0.0,
        'bottleneck':blocked[0], 'balance_loss_pp':0.0,'orders':order_rows,
        'stations':station_rows,'events':[{'time':0.0,'type':'blocked','message':f"Posto(s) sem equipe: {', '.join(blocked)}"}],
        'operations':[], 'cost_breakdown':{}, 'config':config})


class EventObserver(Protocol):
    """Optional read-only trace sink; raises on errors rather than faking provenance."""
    def on_initial(self, *, config: ScenarioConfig, action: TimedAction | None,
                   stations: dict, orders: list) -> None: ...
    def on_transition(self, *, kind: str, now_h: float, entity_id: str | None,
                      stations: dict, orders: list, queue: dict, active: dict,
                      running: dict, units: dict, order_completed: dict,
                      outage_active: bool) -> None: ...


def run_simulation(config: ScenarioConfig, action: TimedAction | None = None,
                   observer: EventObserver | None = None) -> SimulationResult:
    errors = validate_model(config.stations, config.orders, demand_multiplier=config.demand_multiplier)
    if errors:
        raise ValueError('Modelo inválido: ' + ' | '.join(errors[:12]))
    if config.dispatch_rule not in {'EDD', 'SPT', 'FIFO'}:
        raise ValueError('Regra de despacho deve ser EDD, SPT ou FIFO.')
    finite(config.chaos_duration_h, 'Duração da parada')
    finite(config.chaos_start_h, 'Início da parada')
    finite(config.chaos_start_h + config.chaos_duration_h, 'Fim da parada')
    if config.chaos_duration_h < 0 or config.chaos_start_h < 0:
        raise ValueError('Início e duração de parada devem ser não negativos.')
    stations = deepcopy(config.stations)
    orders = deepcopy(config.orders)
    absent = config.absent_workers or {}
    for sid in absent:
        if sid not in stations:
            raise ValueError(f"Ausência atribuída a posto inexistente: {sid}.")
        if int(absent[sid]) < 0:
            raise ValueError('Quantidade de ausências não pode ser negativa.')
    for sid, s in stations.items():
        s['available_workers'] = max(0, int(s['operadores']) - int(absent.get(sid, 0)))
    initial_resources={sid:(int(s['maquinas']),int(s['available_workers'])) for sid,s in stations.items()}
    if action:
        if not math.isfinite(action.at_h) or action.at_h<0:
            raise ValueError('O instante da resposta deve ser finito e não negativo.')
        if action.dispatch_rule and action.dispatch_rule not in {'EDD','FIFO','SPT'}:
            raise ValueError('Regra de resposta inválida.')
        if action.repair_remaining_factor is not None:
            if not math.isfinite(action.repair_remaining_factor) or not 0<action.repair_remaining_factor<=1:
                raise ValueError('O fator de reparo deve estar entre zero (exclusivo) e um.')
            if not config.chaos_station or action.at_h<config.chaos_start_h:
                raise ValueError('O reparo só pode ser solicitado após o início da falha.')
        for changes,field,minimum in [(action.workers_delta or {},'available_workers',0),(action.machines_delta or {},'maquinas',1)]:
            for sid,delta in changes.items():
                if sid not in stations or not isinstance(delta,int) or isinstance(delta,bool) or stations[sid][field]+delta<minimum:
                    raise ValueError('Alteração de recursos inválida.')
                if field=='maquinas' and delta<0:
                    raise ValueError('A resposta não pode remover máquinas em operação.')
                if field=='available_workers' and not stations[sid].get('automatizada',False) and sid in {a for o in orders for a,_ in o['route']} and stations[sid][field]+delta<float(stations[sid].get('operadores_por_maquina',1)):
                    raise ValueError('A resposta não pode deixar um posto usado sem equipe mínima.')
    for o in orders:
        quantity = finite(int(o['quantidade']) * float(config.demand_multiplier), 'Quantidade escalada')
        o['quantidade_sim'] = max(1, int(round(quantity)))
    used = {sid for o in orders for sid, _ in o['route']}
    blocked = [sid for sid in stations if sid in used and not stations[sid].get('automatizada', False)
               and stations[sid]['available_workers'] < float(stations[sid].get('operadores_por_maquina',1))]
    if blocked:
        return _infeasible(config, stations, orders, blocked)

    order_by_id = {o['id']:o for o in orders}
    event_heap: list = []
    queue: dict = {sid: [] for sid in stations}
    counter = count()
    active = {sid:0 for sid in stations}
    slots = {sid:set() for sid in stations}
    busy = defaultdict(float)
    held_down = defaultdict(float)
    work_wait = defaultdict(float)
    performed = defaultdict(int)
    queue_max = defaultdict(int)
    all_completion = defaultdict(list)
    order_completion: dict[str,float] = {}
    op_log = []
    event_log = []
    # Trace-only entities: no effect on dispatch, timing or accounting.
    observed_units = ({f"{o['id']}#{u+1}": {
        'order_id': o['id'], 'route_step': 0, 'station_id': None,
        'machine_id': None, 'phase': 'unreleased'
    } for o in orders for u in range(o['quantidade_sim'])} if observer else {})
    observed_running = {}  # (oid, unit) -> (sid, slot)
    observed_completed = defaultdict(int)
    observed_outage_active = False

    current_rule=config.dispatch_rule
    reserved_workers=defaultdict(int)
    resource_changes=[]
    effective_h=None
    response_reserved=False
    outage_start = float(config.chaos_start_h)
    outage_end = outage_start + float(config.chaos_duration_h)
    disrupted = (config.chaos_station in stations and outage_end > outage_start)
    if config.chaos_station and config.chaos_station not in stations:
        raise ValueError('Posto de falha não existe no modelo.')

    if observer:
        observer.on_initial(config=config, action=action, stations=stations, orders=orders)

    def observe(kind, now, entity=None):
        if observer is not None:
            observer.on_transition(
                kind=kind, now_h=float(now), entity_id=entity,
                stations=stations, orders=orders, queue=queue, active=active,
                running=observed_running, units=observed_units,
                order_completed=observed_completed,
                outage_active=observed_outage_active,
            )

    def add_event(t, kind, payload):
        heapq.heappush(event_heap, (finite(t, 'Instante do evento'), next(counter), kind, payload))

    for order in orders:
        for unit in range(order['quantidade_sim']):
            add_event(float(order.get('release_h', 0)), 'arrive', (order['id'],unit,0))
    if action:
        add_event(action.at_h,'intervene',None)

    defer_start = False

    def enqueue(oid, unit, step, now):
        sid, minutes = order_by_id[oid]['route'][step]
        p = _priority(order_by_id[oid], minutes, current_rule, now, unit)
        heapq.heappush(queue[sid], (p,next(counter),float(now),oid,unit,step))
        if observer:
            observed_units[f"{oid}#{unit+1}"].update(
                route_step=step, station_id=sid, machine_id=None, phase='queued')
            observe('queue_enter', now, f"{oid}#{unit+1}")
        queue_max[sid] = max(queue_max[sid],len(queue[sid]))
        try_start(sid,now)

    def try_start(sid, now):
        # Dispatch only after *all* same-time releases/completions/responses.
        if defer_start:
            return
        if disrupted and sid == config.chaos_station and outage_start <= now < outage_end:
            # Schedule a wake-up only once; any queued operations remain blocked until recovery.
            return
        s=stations[sid]
        workers_per_machine=float(s.get('operadores_por_maquina',1))
        available_workers = max(0, int(s['available_workers']) - reserved_workers[sid])
        machines = int(s['maquinas'])
        cap = (machines if s.get('automatizada', False) or
               available_workers >= machines * workers_per_machine else
               int(available_workers / workers_per_machine))
        while queue[sid] and active[sid] < cap:
            _p,_counter, arrival, oid, unit, step = heapq.heappop(queue[sid])
            active[sid] += 1
            slot = next(i for i in range(cap) if i not in slots[sid])
            slots[sid].add(slot)
            if observer:
                uid = f"{oid}#{unit+1}"
                observed_running[(oid, unit)] = (sid, slot)
                observed_units[uid].update(station_id=sid, machine_id=f"{sid}:slot:{slot}",
                                           phase='processing', route_step=step)
                observe('operation_start', now, uid)
            work_wait[sid] += max(0,now-arrival)
            _,base_cycle = order_by_id[oid]['route'][step]
            # Explicit one operator + one machine; staffing shortage constrains parallel capacity
            # instead of also multiplying the processing time (double penalty).
            eff=float(s.get('eficiencia_operador',1))
            availability=float(s.get('disponibilidade',1))
            setup_h=float(s.get('setup_min',0))/60 if unit==0 else 0.0
            process_h = product_ratio(
                (base_cycle, _noise(config.seed,oid,unit,step)),
                (60, eff, availability), 'Tempo de processamento') + setup_h
            finite(process_h, 'Tempo de processamento')
            down_h=0.0
            end=now+process_h
            if disrupted and sid==config.chaos_station and now < outage_start < end:
                down_h=outage_end-outage_start
                end+=down_h
            if not math.isfinite(end) or end <= now:
                raise ValueError('Fim da operação fora da precisão temporal representável.')
            busy[sid]+=process_h
            held_down[sid]+=down_h
            performed[sid]+=1
            add_event(end,'finish',(oid,unit,step,sid,now,process_h,down_h,arrival,slot))

    if disrupted:
        # Only trace-enabled runs need an extra boundary marker.
        # Ordinary V30.2 runs keep the original heap exactly unchanged.
        if observer:
            add_event(outage_start, 'outage_start', config.chaos_station)
        add_event(outage_end, 'wake', config.chaos_station)
        event_log += [
            {'time':outage_start,'type':'murphy','message':f"Parada de {config.chaos_station} iniciada ({config.chaos_duration_h:g} h)."},
            {'time':outage_end,'type':'recovery','message':f"Posto {config.chaos_station} recuperado."},
        ]
    for sid,n in absent.items():
        if int(n)>0:
            event_log.append({'time':0.0,'type':'workforce','message':f"{sid}: {int(n)} ausência(s) no cenário."})

    last_time=0.0
    while event_heap:
        now = event_heap[0][0]
        defer_start = True
        # An event can enqueue further transitions at the same timestamp.
        # All of them form one dispatch boundary, regardless of input row order.
        while event_heap and event_heap[0][0] == now:
            now, _seq, kind, payload = heapq.heappop(event_heap)
            if kind in {'arrive','finish'}:
                last_time=max(last_time,now)
            if kind=='arrive':
                enqueue(*payload,now)
            elif kind=='outage_start':
                observed_outage_active = True
                if observer:
                    for (oid, unit), (sid, slot) in observed_running.items():
                        if sid == payload:
                            observed_units[f"{oid}#{unit+1}"]['phase'] = 'paused'
                    observe('outage_start', now, payload)
            elif kind=='wake':
                observed_outage_active = False
                if observer:
                    for (oid, unit), (sid, slot) in observed_running.items():
                        if sid == payload:
                            observed_units[f"{oid}#{unit+1}"]['phase'] = 'processing'
                    observe('outage_end', now, payload)
                try_start(payload,now)
            elif kind=='intervene':
                # Reserve outgoing workers at the requested time. Existing work finishes;
                # the transfer becomes effective only when every donor has a free worker.
                if not response_reserved:
                    for sid,delta in (action.workers_delta or {}).items():
                        if delta<0:reserved_workers[sid]=-delta
                    response_reserved=True
                waiting=[]
                for sid,delta in (action.workers_delta or {}).items():
                    if delta>=0:continue
                    demand=0 if stations[sid].get('automatizada',False) else math.ceil(active[sid]*float(stations[sid].get('operadores_por_maquina',1)))
                    if stations[sid]['available_workers']-demand < -delta:
                        finishes=[e[0] for e in event_heap if e[2]=='finish' and e[3][3]==sid and e[0]>=now]
                        if finishes:waiting.append(min(finishes))
                if waiting:
                    add_event(min(waiting),'intervene',None)
                    continue
                effective_h=now
                for sid,s in stations.items():
                    before=(int(s['maquinas']),int(s['available_workers']))
                    s['maquinas']+=int((action.machines_delta or {}).get(sid,0))
                    s['available_workers']+=int((action.workers_delta or {}).get(sid,0))
                    reserved_workers[sid]=0
                    after=(int(s['maquinas']),int(s['available_workers']))
                    if before!=after:resource_changes.append({'time':now,'station':sid,'machines_before':before[0],'workers_before':before[1],'machines_after':after[0],'workers_after':after[1]})
                if action.dispatch_rule:
                    current_rule=action.dispatch_rule
                    for sid,q in queue.items():
                        queue[sid]=[(_priority(order_by_id[oid],order_by_id[oid]['route'][step][1],current_rule,arrival,unit),seq,arrival,oid,unit,step) for _,seq,arrival,oid,unit,step in q]
                        heapq.heapify(queue[sid])
                if action.repair_remaining_factor is not None and disrupted and now<outage_end:
                    previous_end=outage_end
                    outage_end=now+(previous_end-now)*action.repair_remaining_factor
                    advance=previous_end-outage_end
                    updated=[]
                    for t,seq,event,item in event_heap:
                        if event=='wake' and item==config.chaos_station:
                            t=outage_end
                        elif event=='finish' and item[3]==config.chaos_station and item[6]>0 and item[4]<outage_start:
                            values=list(item);values[6]-=advance;item=tuple(values);t-=advance
                            held_down[config.chaos_station]-=advance
                        updated.append((t,seq,event,item))
                    event_heap[:]=updated;heapq.heapify(event_heap)
                    for event in event_log:
                        if event['type']=='recovery':event['time']=outage_end
                event_log.append({'time':now,'type':'decision','message':action.label,'requested_h':action.at_h})
                observe('action_applied', now, action.label)
                for sid in stations:try_start(sid,now)
            else:
                oid,unit,step,sid,start,process_h,down_h,arrival,slot = payload
                active[sid]-=1
                slots[sid].remove(slot)
                if observer:
                    observed_running.pop((oid, unit))
                    uid = f"{oid}#{unit+1}"
                    last_step = step + 1 >= len(order_by_id[oid]['route'])
                    observed_units[uid].update(
                        phase='completed' if last_step else 'unreleased',
                        route_step=step + (0 if last_step else 1),
                        station_id=None, machine_id=None,
                    )
                    if last_step:
                        observed_completed[oid] += 1
                    observe('operation_finish', now, uid)
                segments = [[start, now]] if down_h <= 0 else [[start, outage_start], [outage_end, now]]
                op_log.append({'OP':oid,'Unidade':unit+1,'Etapa':step+1,'Posto':sid,
                    'Início (h)':round(start,4),'Fim (h)':round(now,4),
                    'Processando (h)':round(process_h,4),'Parada (h)':round(down_h,4),
                    'Espera (h)':round(start-arrival,4),
                    'arrival_h':arrival,'start_h':start,'end_h':now,
                    'machine_slot':slot, 'process_segments':segments})
                if unit==0:
                    event_log.append({'time':now,'type':'flow','message':f"{oid} liberou a 1ª peça de {stations[sid].get('nome',sid)}."})
                order = order_by_id[oid]
                if step+1<len(order['route']):
                    enqueue(oid,unit,step+1,now)
                else:
                    all_completion[oid].append(now)
                    if len(all_completion[oid])==order['quantidade_sim']:
                        order_completion[oid]=max(all_completion[oid])
                        observe('order_completed', now, oid)
                try_start(sid,now)
        defer_start = False
        for station_id in stations:
            try_start(station_id, now)
    makespan=last_time
    total_units=sum(o['quantidade_sim'] for o in orders)
    rows=[]; penalty_total=0.0; late_orders=0
    for o in orders:
        finish=float(order_completion[o['id']])
        lateness=max(0.0,finish-float(o['prazo_h']))
        penalty=product_ratio((lateness, o['multa_hora']), (), 'Multa por atraso')
        late_orders+=int(lateness>1e-9)
        penalty_total+=penalty
        rows.append({'OP':o['id'],'Cliente':o.get('cliente',''),'Produto':o.get('produto',''),
            'Quantidade':o['quantidade_sim'],'Prazo (h)':float(o['prazo_h']),
            'Conclusão (h)':round(finish,2),'Atraso (h)':round(lateness,2),
            'Multa (R$)':round(penalty,2),'Status':'Atrasada' if lateness>1e-9 else 'No prazo',
            'completion_h':finish, 'lateness_h':lateness, 'penalty':penalty})
    station_rows=[]; operating_cost=0.0; bn='-'; top_score=-1
    precise_utils=[]
    for sid,s in stations.items():
        machines=int(s['maquinas']); workers=int(s['available_workers'])
        original_machines,original_workers=initial_resources[sid]
        before_h=min(makespan,effective_h) if effective_h is not None else makespan
        after_h=max(0,makespan-before_h)
        machine_hours=before_h*original_machines+after_h*machines
        worker_hours=before_h*original_workers+after_h*workers
        machine_util=min(100.0, 100 * product_ratio(
            (busy[sid],), (machine_hours,), 'Utilização de máquinas', zero_over_zero=True))
        labor_demand=0 if s.get('automatizada',False) else float(s.get('operadores_por_maquina',1))
        worker_util=min(100.0, 100 * product_ratio(
            (busy[sid], labor_demand), (worker_hours,), 'Utilização de equipe', zero_over_zero=True))
        precise_utils.append(machine_util)
        avg_wait=work_wait[sid]/max(1,performed[sid])*60
        # Fixed capacity cost across the total plan horizon; NOT activity-based cost.
        cost=(product_ratio((machine_hours, s['custo_maquina_h']), (), 'Custo de máquinas') +
              product_ratio((worker_hours, s['custo_operador_h']), (), 'Custo de equipe'))
        operating_cost+=cost
        score=machine_util+min(50,avg_wait/2)+queue_max[sid]*2
        if score>top_score:
            top_score=score;bn=sid
        station_rows.append({'Posto':sid,'Nome':s.get('nome',sid),'Máquinas':machines,
            'Operadores':workers,'Utilização máquina (%)':round(machine_util,1),
            'Utilização mão de obra (%)':round(worker_util,1),
            'Espera média (min)':round(avg_wait,1),'Fila máx.':queue_max[sid],
            'Custo cenário (R$)':round(cost,2), 'Parada de operações (h)':round(held_down[sid],2),
            'precise': {'machine_util_pct':machine_util, 'worker_util_pct':worker_util,
                        'mean_wait_min':avg_wait, 'cost':finite(cost, 'Custo do posto')}})
    result_config=config
    if action and action.repair_remaining_factor is not None:
        result_config=config.clone();result_config.chaos_duration_h=outage_end-outage_start
    precise = {
        'makespan_h':finite(makespan, 'Makespan'),
        'throughput_h':product_ratio((total_units,), (makespan,), 'Throughput'),
        'sla_pct':100*(len(orders)-late_orders)/len(orders),
        'penalty_total':finite(penalty_total, 'Multas'),
        'operating_cost':finite(operating_cost, 'Custo operacional'),
        'total_cost':finite(operating_cost+penalty_total, 'Custo total'),
        'unit_cost':product_ratio((operating_cost,), (total_units,), 'Custo unitário'),
        'balance_loss_pp':max(precise_utils)-min(precise_utils),
    }
    return SimulationResult({'name':config.name,'dispatch_rule':current_rule,
        'feasible':True,'blocked_stations':[],'warnings':[], 'makespan_h':present(makespan,2),
        'total_units':total_units,'planned_units':total_units,
        'throughput_h':present(precise['throughput_h'],3),
        'sla_pct':round(100*(len(orders)-late_orders)/len(orders),1),'late_orders':late_orders,
        'penalty_total':round(penalty_total,2),'operating_cost':round(operating_cost,2),
        'total_cost':round(operating_cost+penalty_total,2),
        'unit_cost':round(operating_cost/max(1,total_units),2),
        'bottleneck':bn,'balance_loss_pp':round(precise['balance_loss_pp'],1),
        'orders':rows,'stations':station_rows,'events':sorted((event for event in event_log if event['time'] <= makespan+1e-9),key=lambda x:x['time']),
        'operations':op_log,
        'cost_breakdown':{'capacidade_contratada':round(operating_cost,2),
                          'multas_atraso':round(penalty_total,2)},
        'precise':precise, 'config':result_config,'resource_changes':resource_changes,
        'intervention':{'requested_h':action.at_h,'effective_h':effective_h,'label':action.label} if action else None})
