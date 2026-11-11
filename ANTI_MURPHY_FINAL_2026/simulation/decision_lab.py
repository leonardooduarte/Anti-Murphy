"""Decision Evidence Studio: experimento causal, opções, dominância e evidências.

Todas as ações partem de um MESMO incidente-base, mesmo conjunto de ordens,
mesma semente e mesma condição inicial. Não é otimização global nem conselho
financeiro. Custos de implantação são hipóteses explicitamente configuráveis.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
import statistics
from typing import Any

from simulation.engine import run_simulation
from simulation.numeric import metric, finite
from simulation.factory import ScenarioConfig
from simulation.decision_council import enrich_decision_rows, select_recommended_action


def config_signature(config: ScenarioConfig) -> str:
    d=asdict(config)
    d.pop('name',None)
    d['absent_workers'] = d.get('absent_workers') or {}  # None e {} significam sem ausências.
    return sha256(json.dumps(d,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()[:16]


def _option(config: ScenarioConfig, label: str, investment: float, why: str):
    return {'name':label,'config':config,'investment':float(investment),'why':why}


def candidate_actions(incident: ScenarioConfig, *, cost_worker: float = 1200.0,
                      cost_machine: float = 6500.0, cost_express: float = 1800.0,
                      include_transfers: bool = True) -> list[dict]:
    if min(cost_worker,cost_machine,cost_express)<0:
        raise ValueError('Custos de intervenção não podem ser negativos.')
    candidates=[]
    for rule in ('EDD','SPT','FIFO'):
        if rule != incident.dispatch_rule:
            c=incident.clone(f'Mudar despacho para {rule}')
            c.dispatch_rule=rule
            candidates.append(_option(c,c.name,0,'Mudança de prioridade sem compra de equipamento.'))
    for sid,s in incident.stations.items():
        if sid not in {step[0] for o in incident.orders for step in o['route']}:
            continue
        c=incident.clone(f'+1 operador · {sid}')
        c.stations[sid]['operadores']=int(s['operadores'])+1
        candidates.append(_option(c,c.name,cost_worker,'Testa capacidade da equipe, sem assumir ganho automático.'))
        c=incident.clone(f'+1 máquina · {sid}')
        c.stations[sid]['maquinas']=int(s['maquinas'])+1
        candidates.append(_option(c,c.name,cost_machine,'Testa capacidade adicional e possíveis gargalos posteriores.'))
        setup=float(s.get('setup_min',0))
        if setup>0:
            c=incident.clone(f'SMED · -30% setup · {sid}')
            c.stations[sid]['setup_min']=setup*.7
            candidates.append(_option(c,c.name,0,'Melhoria de método sem aquisição simulada.'))
    if include_transfers:
        for src,st in incident.stations.items():
            if int(st['operadores'])<=1:
                continue
            for dst in incident.stations:
                if dst == src:
                    continue
                c=incident.clone(f'Realocar operador · {src} → {dst}')
                c.stations[src]['operadores']-=1
                c.stations[dst]['operadores']+=1
                candidates.append(_option(c,c.name,0,'Transferência exige capacitação e autorização operacional.'))
    if incident.chaos_station and incident.chaos_duration_h>0:
        c=incident.clone(f'Manutenção expressa · {incident.chaos_station}')
        c.chaos_duration_h*=.5
        candidates.append(_option(c,c.name,cost_express,'Mesmo incidente iniciador, tempo de reparo reduzido pela intervenção.'))
    return candidates


def pareto_flags(rows: list[dict]) -> list[bool]:
    """Pareto: custo total + implantação ↓, SLA ↑, makespan ↓; só opções válidas."""
    result=[]
    for a in rows:
        if not a['feasible'] or not a['within_budget'] or not a.get('meets_sla',True):
            result.append(False)
            continue
        dominated=False
        for b in rows:
            if a is b or not b['feasible'] or not b['within_budget'] or not b.get('meets_sla',True):
                continue
            akey=(metric(a,'decision_cost'), -metric(a,'sla_pct'), metric(a,'makespan_h'))
            bkey=(metric(b,'decision_cost'), -metric(b,'sla_pct'), metric(b,'makespan_h'))
            if all(y<=x+1e-8 for x,y in zip(akey,bkey)) and any(y<x-1e-8 for x,y in zip(akey,bkey)):
                dominated=True
                break
        result.append(not dominated)
    return result


def evaluate_decisions(incident: ScenarioConfig, *, budget: float = 0.0,
                       sla_floor: float = 0.0, cost_worker: float = 1200.0,
                       cost_machine: float = 6500.0, cost_express: float = 1800.0,
                       max_actions: int = 90) -> dict:
    """0 de orçamento significa sem teto. Custo é para UMA carteira/horizonte.

    Mesmo seed para variação de processo por unidade, evitando viés entre opções.
    O incidente sem ação é o baseline decisório, NÃO operação sem falha.
    """
    if budget<0 or not 0<=sla_floor<=100:
        raise ValueError('Orçamento ou SLA mínimo inválidos.')
    baseline=run_simulation(incident)
    normal_cfg=incident.clone('Operação sem incidente')
    normal_cfg.chaos_station=None
    normal_cfg.chaos_duration_h=0
    normal_cfg.absent_workers={}
    normal=run_simulation(normal_cfg)
    rows=[]
    opt_baseline=_option(incident.clone('Não intervir'), 'Não intervir',0,'Aguardar a recuperação normal da operação.')
    options=[opt_baseline]+candidate_actions(incident,cost_worker=cost_worker,cost_machine=cost_machine,cost_express=cost_express)
    for item in options[:max_actions]:
        cfg=item['config']
        r=baseline if item['name']=='Não intervir' else run_simulation(cfg)
        feasible=bool(r.get('feasible', True))
        valid_cost=feasible and bool(baseline.get('feasible',True))
        cost=metric(r,'total_cost') if feasible else 0
        decision_cost=cost+item['investment'] if feasible else 0
        savings=metric(baseline,'total_cost')-decision_cost if valid_cost else None
        row={'action':item['name'],'rationale':item['why'],
            'investment':item['investment'],'feasible':feasible,
            'within_budget':budget<=0 or item['investment']<=budget,
            'meets_sla':feasible and metric(r,'sla_pct')>=sla_floor,
            'decision_cost':round(decision_cost,2) if feasible else None,
            'savings':round(savings,2) if savings is not None else None,
            'precise': {**r.get('precise',{}), 'decision_cost':finite(decision_cost) if feasible else None, 'savings':savings},
            'sla_pct':metric(r,'sla_pct'),'makespan_h':metric(r,'makespan_h'),
            'throughput_h':metric(r,'throughput_h'),
            'late_orders':int(r['late_orders']),
            'penalty_total':float(r['penalty_total']),
            'feasibility_note':'Viável no modelo' if feasible else '; '.join(r.get('warnings',[])),
            'signature':config_signature(cfg), 'config':cfg,'result':r}
        rows.append(row)
    flags=pareto_flags(rows)
    for row,flag in zip(rows,flags):
        row['pareto']=flag
    rows = enrich_decision_rows(rows, baseline, normal, sla_floor=sla_floor)
    # Política de ordenação: primeiro veredito/ restrições, depois custo por horizonte, SLA,
    # tempo. Sem score arbitrário nem pretensão de ótimo global.
    verdict_order={'RECOMENDADA':0,'PROMISSORA':1,'CONDICIONAL':2,'SEM BENEFÍCIO':3,'NÃO RECOMENDADA':4,'RESTRITA':5,'REFERÊNCIA':6}
    rows.sort(key=lambda r:(verdict_order.get(str(r.get('verdict','RESTRITA')),9),
                              not(r['feasible'] and r['within_budget'] and r['meets_sla']),
                              not r['feasible'],not r['within_budget'],
                              float('inf') if r['decision_cost'] is None else metric(r,'decision_cost'),
                              -r['sla_pct'],r['makespan_h']))
    recommended=select_recommended_action(rows)
    return {'model_signature':config_signature(incident), 'normal':normal,
            'incident':baseline, 'rows':rows,'budget':budget,'sla_floor':sla_floor,
            'recommended':recommended,
            'assumptions':[
                'Todos os custos são estimativas configuráveis para uma carteira de ordens; não incluem impostos, riscos contratuais ou NPV.',
                'Custo operacional é cobrado sobre o horizonte do cenário; imobilização de recursos durante falhas não gera operação produtiva.',
                'Alocação respeita operadores_por_maquina (salvo posto explicitamente automatizado).',
                'Resultados numéricos são internos ao modelo; não são validação ou previsão fabril.',
                'O ranking explora alternativas predeterminadas, não comprova ótimo global.'
            ]}


def paired_stress_test(incident: ScenarioConfig, action_config: ScenarioConfig,
                       *, runs: int = 8, seed_start: int = 700) -> dict:
    """Compara a MESMA realização estocástica em cada par de simulações."""
    if runs<2 or runs>60:
        raise ValueError('Use 2 a 60 replicações.')
    pairs=[]
    for k in range(runs):
        a=incident.clone(); b=action_config.clone()
        a.seed=seed_start+k; b.seed=seed_start+k
        ra=run_simulation(a); rb=run_simulation(b)
        if not ra['feasible'] or not rb['feasible']:
            return {'feasible':False,'pairs':[],'message':'Uma opção não é simulável por indisponibilidade de recursos.'}
        pairs.append({'seed':a.seed,
                      'cost_saving':round(float(ra['total_cost'])-float(rb['total_cost']),2),
                      'sla_gain_pp':round(float(rb['sla_pct'])-float(ra['sla_pct']),1),
                      'makespan_gain_h':round(float(ra['makespan_h'])-float(rb['makespan_h']),2)})
    return {'feasible':True,'pairs':pairs,
            'mean_cost_saving_before_investment':round(statistics.fmean(p['cost_saving'] for p in pairs),2),
            'min_cost_saving_before_investment':min(p['cost_saving'] for p in pairs),
            'max_cost_saving_before_investment':max(p['cost_saving'] for p in pairs),
            'fraction_positive_cost_saving':round(sum(p['cost_saving']>0 for p in pairs)/len(pairs),3),
            'interpretation':'Dispersão interna de amostras sintéticas. Não é probabilidade real de sucesso.'}


def decision_report(data: dict, row: dict) -> str:
    """JSON auditável, sem dados pessoais nem código executável embutido."""
    return json.dumps({
        'produto':'Anti-Murphy V28 · War Room / Decision Evidence Studio',
        'modelo_sha256_16':data['model_signature'],
        'cenario_sem_acao':{k:data['incident'].get(k) for k in ('feasible','sla_pct','throughput_h','makespan_h','total_cost','late_orders','bottleneck')},
        'acao':row['action'], 'assinatura_acao':row['signature'],
        'indicadores_acao':{k:row[k] for k in ('feasible','decision_cost','savings','investment','sla_pct','makespan_h','throughput_h','penalty_total','pareto','within_budget','meets_sla')},
        'premissas':data['assumptions'],
        'aviso':'Ferramenta acadêmica. Simulação não homologada em dados de fábrica real.'
    },ensure_ascii=False,indent=2)
