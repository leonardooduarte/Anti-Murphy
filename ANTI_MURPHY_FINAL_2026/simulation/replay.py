"""Replay of exact DES traces. No artificial transport times or random motion."""
from __future__ import annotations
from bisect import bisect_right
from collections import defaultdict


def replay_payload(result):
    cfg=result['config']
    stations=list(cfg.stations)
    last={}
    rows=[]
    for op in result.get('operations',[]):
        start=op.get('start_h',op['Início (h)']);end=op.get('end_h',op['Fim (h)'])
        arrival=op.get('arrival_h',start-op['Espera (h)'])
        key=(op['OP'],op['Unidade'])
        if key not in last or op['Etapa']>last[key][0]:last[key]=(op['Etapa'],end)
        rows.append([stations.index(op['Posto']),arrival,start,end,op['OP'],op['Unidade'],
                     op['Etapa'],op.get('machine_slot',0),op.get('process_segments',[[start,end]])])
    final_times=sorted(x[1] for x in last.values())
    per_order=defaultdict(list)
    for (oid,_),(_,end) in last.items():per_order[oid].append(end)
    by_station=[]
    for idx,sid in enumerate(stations):
        group=[r for r in rows if r[0]==idx];s=cfg.stations[sid]
        by_station.append({'id':sid,'name':s.get('nome',sid),'machines':s['maquinas'],
            'workers':max(0,s['operadores']-(cfg.absent_workers or {}).get(sid,0)),
            'arrivals':sorted(r[1] for r in group),'starts':sorted(r[2] for r in group),
            'ends':sorted(r[3] for r in group),
            'processing_starts':sorted(a for r in group for a,b in r[8] if b>a),
            'processing_ends':sorted(b for r in group for a,b in r[8] if b>a),
            'changes':[c for c in result.get('resource_changes',[]) if c['station']==sid]})
    # All event arrays remain exact. Only per-piece details are capped for a bounded iframe.
    return {'stations':by_station,'operations':rows if len(rows)<=12000 else [],
        'details_omitted':len(rows)>12000, 'operation_count':len(rows),
        'completion_times':final_times,'horizon':max((r[3] for r in rows),default=0),
        'order_completions':{oid:sorted(times) for oid,times in per_order.items()},
        'planned':result.get('planned_units',0),'feasible':result.get('feasible',True),
        'outage':{'station':cfg.chaos_station,'start':cfg.chaos_start_h,
                  'end':cfg.chaos_start_h+cfg.chaos_duration_h} if cfg.chaos_station and cfg.chaos_duration_h>0 else None,
        'bottleneck':result.get('bottleneck'),'intervention':result.get('intervention'),
        'edges':sorted({(stations.index(a[0]),stations.index(b[0])) for o in cfg.orders for a,b in zip(o['route'],o['route'][1:])}),
        'metrics':{k:result.get(k) for k in ('total_cost','sla_pct','makespan_h','throughput_h','late_orders')}}


def snapshot(payload, time_h):
    t=max(0.,float(time_h));stations=[]
    for s in payload['stations']:
        a=bisect_right(s['arrivals'],t);b=bisect_right(s['starts'],t);c=bisect_right(s['ends'],t)
        down=bool(payload['outage'] and payload['outage']['station']==s['id'] and payload['outage']['start']<=t<payload['outage']['end'])
        stations.append({'id':s['id'],'queue':a-b,'active':b-c,
            'processing':(bisect_right(s['processing_starts'],t)-bisect_right(s['processing_ends'],t)) if 'processing_starts' in s else None,
            'completed_operations':c,'down':down})
    return {'time':t,'stations':stations,'completed':bisect_right(payload['completion_times'],t)}
