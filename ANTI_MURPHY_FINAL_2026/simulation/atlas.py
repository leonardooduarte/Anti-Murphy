"""V29 · decision policy and audit view. Pure Python; no Streamlit dependency.

Synthetic DES results, not predictions of industrial outcomes. No automatic actuation.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

from simulation.numeric import metric
from simulation.decision_lab import evaluate_decisions, config_signature
from simulation.factory import ScenarioConfig


@dataclass(frozen=True)
class DecisionPolicy:
    budget: float = 10000.0
    min_sla: float = 80.0
    cost_worker: float = 1200.0
    cost_machine: float = 6500.0
    cost_express: float = 1800.0

    def validate(self):
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError('A política deve conter apenas números finitos.')
        if self.budget < 0 or not 0 <= self.min_sla <= 100:
            raise ValueError('Orçamento ou SLA fora do intervalo permitido.')
        if min(self.cost_worker, self.cost_machine, self.cost_express) < 0:
            raise ValueError('Os custos de intervenção devem ser não negativos.')


def scenario_from_incident(base_config: ScenarioConfig, station: str, start_h: float, duration_h: float) -> ScenarioConfig:
    if station not in base_config.stations:
        raise ValueError(f"Posto desconhecido: {station}")
    if not math.isfinite(start_h) or not math.isfinite(duration_h) or not 0 <= start_h <= 500 or not 0 < duration_h <= 168:
        raise ValueError('Início ou duração de parada inválidos.')
    cfg = base_config.clone('Incidente sob análise')
    cfg.chaos_station = station
    cfg.chaos_start_h = float(start_h)
    cfg.chaos_duration_h = float(duration_h)
    return cfg


def _status(incident: dict, normal: dict, best: dict | None, rows: list[dict]) -> tuple[str, str]:
    if not incident.get('feasible', True):
        return 'MODELO BLOQUEADO', 'A operação com o incidente não é simulável. Corrija recursos antes de comparar ganhos.'
    if not rows:
        return 'SEM ALTERNATIVAS', 'Nenhuma alternativa foi gerada pelo mecanismo atual.'
    if (metric(incident,'total_cost') == metric(normal,'total_cost')
            and metric(incident,'sla_pct') == metric(normal,'sla_pct')
            and metric(incident,'makespan_h') == metric(normal,'makespan_h')):
        return 'SEM IMPACTO MENSURÁVEL', 'O incidente configurado não alterou custo, prazo ou SLA desta carteira; pode ocorrer fora do horizonte efetivo.'
    valid = [r for r in rows if r.get('feasible') and r.get('within_budget') and r.get('meets_sla')]
    if not valid:
        return 'RESTRIÇÕES NÃO ATENDIDAS', 'Nenhuma resposta testada satisfaz simultaneamente capacidade, orçamento e SLA mínimo.'
    candidates = [r for r in valid if r.get('action') != 'Não intervir' and r.get('decision_cost') is not None]
    if not candidates:
        return 'SEM MELHORIA VIÁVEL', 'Nenhuma intervenção testada atende às restrições; mantenha o incidente como referência e reveja o modelo.'
    improved = [r for r in candidates if (float(r.get('savings') or 0) > 0.005
            and r['sla_pct'] >= metric(incident,'sla_pct') - 1e-8
            and r['makespan_h'] <= metric(incident,'makespan_h') + 1e-8)]
    if improved:
        return 'RESPOSTA PROMISSORA', 'Há ao menos uma intervenção simulada que reduz o custo sem deteriorar SLA ou makespan frente à crise.'
    return 'TRADE-OFF NECESSÁRIO', 'Há opções admissíveis, mas nenhuma demonstra melhoria simultânea de custo, serviço e tempo.'


def analyze_incident(base_config: ScenarioConfig, station: str, start_h: float, duration_h: float,
                     policy: DecisionPolicy | None = None) -> dict[str, Any]:
    policy = policy or DecisionPolicy()
    policy.validate()
    incident_cfg = scenario_from_incident(base_config, station, start_h, duration_h)
    result = evaluate_decisions(
        incident_cfg, budget=policy.budget, sla_floor=policy.min_sla,
        cost_worker=policy.cost_worker, cost_machine=policy.cost_machine,
        cost_express=policy.cost_express,
    )
    rows = result['rows']
    admissible = [r for r in rows if r.get('feasible') and r.get('within_budget') and r.get('meets_sla')]
    candidates = [r for r in admissible if r['action'] != 'Não intervir']
    status, explanation = _status(result['incident'], result['normal'], result.get('recommended'), rows)

    # Prefer a material, non-worsening alternative. Otherwise do not imply a unique best action.
    improvement = [r for r in candidates if (
        float(r.get('savings') or 0) > 0.005
        and float(r['sla_pct']) >= metric(result['incident'],'sla_pct') - 1e-8
        and float(r['makespan_h']) <= metric(result['incident'],'makespan_h') + 1e-8
    )]
    leader = min(improvement, key=lambda x:(metric(x,'decision_cost'),-metric(x,'sla_pct'),metric(x,'makespan_h'))) if improvement else None
    if leader is None and candidates and status == 'TRADE-OFF NECESSÁRIO':
        # Only surface an option if it offers some measurable improvement.
        # A cheaper option that worsens every operational metric is not a leader.
        conditional=[r for r in candidates if r.get('verdict') in {'RECOMENDADA','PROMISSORA','CONDICIONAL'} and (float(r.get('savings') or 0)>0.005
                     or float(r['sla_pct'])>metric(result['incident'],'sla_pct')+1e-8
                     or float(r['makespan_h'])<metric(result['incident'],'makespan_h')-1e-8)]
        leader = min(conditional, key=lambda x:(metric(x,'decision_cost'),-metric(x,'sla_pct'),metric(x,'makespan_h'))) if conditional else None
    if status in ('MODELO BLOQUEADO','SEM IMPACTO MENSURÁVEL','RESTRIÇÕES NÃO ATENDIDAS','SEM MELHORIA VIÁVEL'):
        leader = None
    if leader is None and status == 'TRADE-OFF NECESSÁRIO':
        status = 'SEM MELHORIA VIÁVEL'
        explanation = 'Nenhuma intervenção admissível produziu benefício mensurável frente ao incidente.'
    # One authoritative selection across War Room, Evidence, AI and exported memos.
    result['recommended'] = leader
    result['policy_status'] = status
    result['policy_explanation'] = explanation
    result['leader'] = leader
    result['eligible_count'] = len(admissible)
    result['intervention_count'] = len(candidates)
    result['baseline_signature'] = config_signature(base_config)
    result['incident_parameters'] = {'station':station,'start_h':float(start_h),'duration_h':float(duration_h)}
    result['policy_inputs'] = asdict(policy)
    result['evaluation_assumptions'] = ['Custos informados pelo usuário são premissas, não preços reais.',
        'Realocação exige capacitação e disponibilidade; não é validada automaticamente pela simulação.',
        'A indisponibilidade considera o posto inteiro e não uma máquina individual.',
        'O ranking testa alternativas enumeradas, não prova ótimo global.',
        'Não houve integração com chão de fábrica nem aplicação física de decisões.']
    return result


def safe_summary(data: dict) -> dict:
    """Sanitized data packet; excludes live scenario objects and customer names."""
    leader = data.get('leader')
    out = {'status':data['policy_status'],'status_reason':data['policy_explanation'],
           'signature':data['model_signature'],'baseline_signature':data.get('baseline_signature'),
           'incident':data['incident_parameters'],
           'summary':{name:{key:data[name].get(key) for key in ('total_cost','sla_pct','makespan_h','throughput_h','penalty_total','bottleneck','feasible')}
                      for name in ('normal','incident')},
           'actions_evaluated':len(data['rows']), 'eligible_actions':data.get('eligible_count',0),
           'alternatives':[{k:r.get(k) for k in ('action','verdict','verdict_reason','savings','sla_pct','makespan_h','investment','decision_cost','meets_sla','within_budget','feasible')} for r in data['rows']],
           'recommended_action': {k:leader.get(k) for k in ('action','rationale','savings','sla_pct','makespan_h','decision_cost','investment','verdict','verdict_reason')} if leader else None,
           'assumptions':data.get('evaluation_assumptions',[])}
    if data.get('timed_response'):
        out['response_requested_h']=data['decision_h']
        out['response_delay_h']=data['delay_h']
    return out


def decision_memo(data: dict, selected: dict | None = None) -> bytes:
    body = safe_summary(data)
    if selected is not None:
        if not any(r['signature']==selected.get('signature') for r in data['rows']):
            raise ValueError('A alternativa examinada não pertence a esta análise.')
        body['examined_action']={k:selected.get(k) for k in ('action','signature','verdict','investment','decision_cost','savings','sla_pct','makespan_h','within_budget','meets_sla','feasible')}
    body['artifact'] = 'ANTI-MURPHY V30 NEXUS · Auditável · Resultado do modelo'
    body['generated_utc'] = datetime.now(timezone.utc).isoformat()
    canonical = json.dumps(body,sort_keys=True,ensure_ascii=False,default=str).encode('utf-8')
    body['content_sha256'] = sha256(canonical).hexdigest()
    return json.dumps(body,ensure_ascii=False,indent=2,default=str).encode('utf-8')
