from __future__ import annotations

from typing import Any, Dict, List
from simulation.decisions import generate_opportunities
from simulation.metrics import compare_results
from simulation.advanced import operating_alerts


def root_cause_explorer(result: Dict[str, Any]) -> Dict[str, Any]:
    """Transparent pressure decomposition from station-level simulation outputs."""
    rows=[]
    raw=[]
    for r in result.get('stations',[]):
        util=float(r.get('Utilização máquina (%)',0) or 0)
        wait=float(r.get('Espera média (min)',0) or 0)
        queue=float(r.get('Fila máx.',0) or 0)
        # Bounded components so one extreme dimension cannot dominate forever.
        util_c=min(100.0, util)
        wait_c=min(100.0, wait/2.4)
        queue_c=min(100.0, queue*3.0)
        score=.34*util_c+.36*wait_c+.30*queue_c
        raw.append((r,score,util_c,wait_c,queue_c))
    total=sum(x[1] for x in raw) or 1.0
    for r,score,uc,wc,qc in sorted(raw,key=lambda x:x[1],reverse=True):
        rows.append({
            'station':str(r.get('Posto','-')),'name':str(r.get('Nome','-')),
            'pressure_score':round(score,1),'share_pct':round(score/total*100,1),
            'util_component':round(uc,1),'wait_component':round(wc,1),'queue_component':round(qc,1),
            'utilization':float(r.get('Utilização máquina (%)',0) or 0),
            'wait_min':float(r.get('Espera média (min)',0) or 0),'queue':int(r.get('Fila máx.',0) or 0),
        })
    top=rows[0] if rows else None
    return {'rows':rows,'top':top,'sla':float(result.get('sla_pct',0) or 0),'late_orders':int(result.get('late_orders',0) or 0)}


def decision_autopilot(base_config, base_result: Dict[str, Any], target_sla: float = 90.0, max_results: int = 5) -> List[Dict[str, Any]]:
    """Controlled agentic exploration using Anti-Murphy's own counterfactual engine.

    It never asks an LLM to fabricate KPIs: candidates are simulated, ranked and returned
    with an explicit objective score.
    """
    opportunities=generate_opportunities(base_config, base_result)
    rows=[]
    for o in opportunities:
        r=o.get('result') or {}
        d=compare_results(base_result,r)
        sla=float(r.get('sla_pct',0) or 0)
        gap=max(0.0,float(target_sla)-sla)
        # Service-first score with flow/economics and a penalty for longer lead-time.
        score=(float(d.get('sla_pp',0))*2.6 + float(d.get('throughput_pct',0))*1.0
               - max(0.0,float(d.get('unit_cost_pct',0)))*.45
               - max(0.0,float(d.get('makespan_pct',0)))*.65
               - gap*.20)
        rows.append({
            'action':o.get('Ação','Oportunidade'),'score':round(score,1),'target_sla':float(target_sla),
            'sla':sla,'throughput':float(r.get('throughput_h',0) or 0),'unit_cost':float(r.get('unit_cost',0) or 0),
            'makespan':float(r.get('makespan_h',0) or 0),'bottleneck':str(r.get('bottleneck','-')),
            'sla_delta_pp':round(float(d.get('sla_pp',0)),1),'throughput_delta_pct':round(float(d.get('throughput_pct',0)),1),
            'cost_delta_pct':round(float(d.get('unit_cost_pct',0)),1),'makespan_delta_pct':round(float(d.get('makespan_pct',0)),1),
            'result':r,'config':o.get('config'),'source':o,
        })
    rows.sort(key=lambda x:(-x['score'],-x['sla'],x['unit_cost']))
    return rows[:max(1,int(max_results))]


def scenario_portfolio(history: List[Dict[str, Any]], base_result: Dict[str, Any] | None = None) -> Dict[str, Any]:
    items=[]
    if base_result is not None:
        items.append({'name':'Cenário Base','source':'Baseline','throughput':float(base_result.get('throughput_h',0)),
                      'sla':float(base_result.get('sla_pct',0)),'unit_cost':float(base_result.get('unit_cost',0)),
                      'makespan':float(base_result.get('makespan_h',0)),'bottleneck':str(base_result.get('bottleneck','-')),
                      'result':base_result,'pinned':True})
    for i,h in enumerate(history):
        items.append({'name':h.get('name',f'Cenário {i+1}'),'source':h.get('source','Experiment'),
                      'throughput':float(h.get('throughput',0)),'sla':float(h.get('sla',0)),
                      'unit_cost':float(h.get('unit_cost',0)),'makespan':float(h.get('makespan',0)),
                      'bottleneck':str(h.get('bottleneck','-')),'result':h.get('result'),'pinned':False,'history_index':i})
    if not items:
        return {'items':[],'leaders':{}}
    leaders={
        'flow':max(items,key=lambda x:x['throughput']),
        'service':max(items,key=lambda x:x['sla']),
        'economics':min(items,key=lambda x:x['unit_cost']),
        'speed':min(items,key=lambda x:x['makespan']),
    }
    return {'items':items,'leaders':leaders}


def change_digest(base: Dict[str, Any], alt: Dict[str, Any]) -> List[Dict[str, str]]:
    d=compare_results(base,alt)
    return [
        {'metric':'Throughput','value':f"{d.get('throughput_pct',0):+.1f}%",'tone':'good' if d.get('throughput_pct',0)>0 else 'bad' if d.get('throughput_pct',0)<0 else 'neutral'},
        {'metric':'SLA','value':f"{d.get('sla_pp',0):+.1f} p.p.",'tone':'good' if d.get('sla_pp',0)>0 else 'bad' if d.get('sla_pp',0)<0 else 'neutral'},
        {'metric':'Custo/un','value':f"{d.get('unit_cost_pct',0):+.1f}%",'tone':'good' if d.get('unit_cost_pct',0)<0 else 'bad' if d.get('unit_cost_pct',0)>0 else 'neutral'},
        {'metric':'Makespan','value':f"{d.get('makespan_pct',0):+.1f}%",'tone':'good' if d.get('makespan_pct',0)<0 else 'bad' if d.get('makespan_pct',0)>0 else 'neutral'},
    ]


def audit_entry(kind: str, title: str, detail: str) -> Dict[str, str]:
    return {'kind':str(kind),'title':str(title),'detail':str(detail)}
