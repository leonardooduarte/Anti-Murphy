"""Application services: one project, one DES model, shared experiments and records.
No Streamlit or frontend dependencies. Predictions are synthetic planning results.
"""
from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any
import hashlib, json, os, re, tempfile, uuid

from data.scenarios import STATIONS_BASE, ORDERS_BASE
from simulation.nexus import (initialize, execute, ExperimentSpec, current_analysis,
    selected_action, invalidate_model, nominal, base_config, audit)
from simulation.engine import run_simulation
from simulation.numeric import metric
from simulation.factory import TimedAction
from simulation.atlas import scenario_from_incident
from simulation.replay import replay_payload
from simulation.response import paired_response
from simulation.innovation import stress_test, goal_seek
from simulation.advanced import (operating_alerts, sensitivity_analysis, demand_breakpoint,
    monte_carlo_analysis, recovery_plan, model_confidence)
from simulation.decisions import generate_opportunities
from simulation.intelligence import explain_comparison
from simulation.validation import validate_model
from simulation.operation import decision_answer, memo
from atelier.decision_explainer import explain
from simulation.decision_store import save_record, archived_records


from .technical_audit import summarize_audit
from .decision_quality import review_alternatives
from .record_integrity import audit_decision_note, cost_snapshot
from .persistence import atomic_bundle
from .workspace_guard import workspace_lock, project_revision
from .analysis_provenance import contexts as experiment_contexts, inputs as experiment_inputs, signature as experiment_signature

class StudioError(Exception):
    pass


def _operability_errors(stations, orders):
    """Live project must be operable; low-staff scenarios remain valid in DES."""
    used={step[0] for o in orders for step in o.get('route',[])
          if isinstance(step,(tuple,list)) and len(step)==2}
    issues=[]
    for sid in used:
        s=stations.get(sid)
        if not s or s.get('automatizada',False): continue
        try:
            if int(s['operadores']) < float(s['operadores_por_maquina']):
                issues.append(f'Posto {sid}: equipe insuficiente para executar os pedidos.')
        except (ValueError,TypeError,KeyError,OverflowError): pass
    return issues


def _json_safe(value):
    return json.loads(json.dumps(value, ensure_ascii=False, default=str, allow_nan=False))


def _summary(result):
    if not result: return None
    return {k: result.get(k) for k in ('name','feasible','makespan_h','sla_pct','late_orders',
        'total_cost','operating_cost','penalty_total','throughput_h','bottleneck','planned_units','total_units','warnings','precise')}


def _candidate(row):
    return {k: row.get(k) for k in ('action','signature','verdict','verdict_reason','rationale',
        'investment','decision_cost','savings','sla_pct','makespan_h','late_orders','total_lateness_h',
        'feasible','within_budget','meets_sla','requested_h','effective_h',
        'restriction_reasons','recovered_orders','order_impacts','pareto','precise')}


def _atomic_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=None
    try:
        with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix='.save_', suffix='.tmp',
                                         encoding='utf-8', delete=False) as f:
            tmp=Path(f.name);json.dump(payload,f,ensure_ascii=False,indent=2)
            f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if tmp and tmp.exists():tmp.unlink()


class Studio:
    def __init__(self, storage: Path):
        storage=Path(storage).resolve()
        self._initializing=True
        try:
            with workspace_lock(storage):
                self._storage_revision=project_revision(storage)
                self._initialize(storage)
        except OSError as exc:
            raise StudioError('Não foi possível abrir o projeto: '+str(exc)) from exc
        finally:
            self._initializing=False

    def _initialize(self, storage: Path):
        self.storage=storage
        self.lock=RLock()
        self.state={}
        initialize(self.state)
        self.state.update(op_enabled=True,op_delay=2.,op_token=uuid.uuid4().hex,
            op_store_dir=str(storage/'registros'),nx_source='Exemplo sintético · PCP')
        self.state.setdefault('nx_ai_mode','Local · sem API')
        self.state.setdefault('nx_messages',[])
        self.state.setdefault('nx_rule','EDD')
        self.state.setdefault('nx_seed',42)
        self._replays={}
        self._lab={}
        self._last_config=None
        self._recovery_warning=None
        p=storage/'projeto.json'
        if p.exists():
            try:
                data=json.loads(p.read_text('utf-8'))
                if not validate_model(data['stations'],data['orders']):
                    self.state['stations']=data['stations']; self.state['orders']=data['orders']
                    self.state['nx_source']='Projeto local recuperado'
                    self.state['nx_rule']=data.get('dispatch_rule','EDD')
            except (OSError,ValueError,KeyError,TypeError):pass
        self.project_id='principal'
        self.projects_dir=self.storage/'projetos'
        self.experiments_dir=self.storage/'experimentos'
        self.projects_dir.mkdir(parents=True,exist_ok=True)
        self.experiments_dir.mkdir(parents=True,exist_ok=True)
        active=self.storage/'projeto_ativo.json'
        startup_spec={'station':'CNC' if 'CNC' in self.state['stations'] else next(iter(self.state['stations'])),
                      'start_h':4,'duration_h':8,'budget':10000,'min_sla':80,'delay_h':2}
        if active.exists():
            try:
                selected=json.loads(active.read_text('utf-8')).get('id','')
                project=self._project_file(selected)
                if project.is_file():
                    data=json.loads(project.read_text('utf-8'))
                    if not validate_model(data['stations'],data['orders']):
                        self.project_id=selected
                        self.state['stations']=data['stations']
                        self.state['orders']=data['orders']
                        self.state['nx_rule']=data.get('dispatch_rule','EDD')
                        startup_spec.update(data.get('spec') or {})
                        startup_spec['delay_h']=data.get('delay_h',startup_spec['delay_h'])
            except (OSError,ValueError,TypeError,KeyError):pass
        # Recover a previously confirmed model if the current active pointer or
        # project carries a stale/invalid priority or an incomplete write.
        try:
            ExperimentSpec(**{**asdict(ExperimentSpec()), **{k:v for k,v in startup_spec.items() if k in asdict(ExperimentSpec())}}).validate(self.state['stations'])
            if _operability_errors(self.state['stations'],self.state['orders']):
                raise ValueError('Projeto contém posto sem equipe para os pedidos.')
            if self.state.get('nx_rule') not in ('EDD','SPT','FIFO'):
                raise ValueError('Regra de despacho persistida inválida.')
            if (startup_spec.get('objective')=='critical' and startup_spec.get('critical_order') not in {o['id'] for o in self.state['orders']}):
                raise ValueError('Prioridade persistida faz referência a pedido inexistente.')
        except (ValueError,TypeError,KeyError) as exc:
            checkpoint=self.storage/'projeto_confirmado.json'
            recovered=False
            if checkpoint.exists():
                try:
                    saved=json.loads(checkpoint.read_text('utf-8'))
                    if not (validate_model(saved['stations'],saved['orders'])+_operability_errors(saved['stations'],saved['orders'])):
                        candidate_spec={**asdict(ExperimentSpec()),**(saved.get('spec') or {})}
                        ExperimentSpec(**candidate_spec).validate(saved['stations'])
                        self.state['stations']=saved['stations'];self.state['orders']=saved['orders']
                        self.state['nx_rule']=saved.get('dispatch_rule','EDD')
                        startup_spec=candidate_spec;self.project_id=saved.get('id','principal')
                        recovered=True
                except (OSError,ValueError,TypeError,KeyError):pass
            if not recovered:
                self.state['stations']=deepcopy(STATIONS_BASE)
                self.state['orders']=deepcopy(ORDERS_BASE)
                self.state['nx_rule']='EDD';self.project_id='principal'
                startup_spec=asdict(ExperimentSpec())
            self._recovery_warning='Configuração inválida na abertura; recuperada a última versão confirmada ou o exemplo padrão.'
        startup_spec['station']=startup_spec['station'] if startup_spec['station'] in self.state['stations'] else next(iter(self.state['stations']))
        self.calculate(startup_spec,initial=True)

    def _project_file(self, project_id):
        if not isinstance(project_id,str) or not re.fullmatch(r'[a-z0-9_-]{1,48}',project_id):
            raise StudioError('Identificador de projeto inválido.')
        return self.projects_dir/(project_id+'.json')

    @staticmethod
    def _project_name(name):
        raw=str(name or '')
        if any(ord(ch)<32 for ch in raw):
            raise StudioError('Nome do projeto contém caracteres de controle.')
        name=raw.strip()
        if not (3<=len(name)<=70):
            raise StudioError('Nome do projeto: informe entre 3 e 70 caracteres.')
        return name

    @contextmanager
    def _writing_workspace(self):
        try:
            with workspace_lock(self.storage):
                if project_revision(self.storage)!=self._storage_revision:
                    raise StudioError('O projeto foi alterado por outra instância ou fora deste programa. '
                                      'Esta gravação foi bloqueada para preservar os dados. '
                                      'Feche e reabra o Anti-Murphy nesta pasta antes de tentar novamente.')
                yield
        except OSError as exc:
            raise StudioError('Gravação indisponível: '+str(exc)) from exc

    def _persist_model(self, state=None, project_id=None, name=None):
        with self._writing_workspace():
            pid=project_id or self.project_id
            paths=[self.storage/'projeto.json',self._project_file(pid),
                   self.storage/'projeto_ativo.json',self.storage/'projeto_confirmado.json']
            # A second reader must not change revisions merely by starting.
            if self._initializing and not self._recovery_warning and all(p.is_file() for p in paths):
                return
            self._persist_model_locked(state,project_id,name)
            self._storage_revision=project_revision(self.storage)

    def _persist_model_locked(self, state=None, project_id=None, name=None):
        """Stage all local model files; publish no memory until disk confirms."""
        state = state if state is not None else self.state
        pid = project_id or self.project_id
        basic = {'stations':state['stations'], 'orders':state['orders'],
                 'dispatch_rule':state.get('nx_rule','EDD')}
        validation = validate_model(basic['stations'], basic['orders']) + _operability_errors(basic['stations'],basic['orders'])
        if validation:
            raise StudioError('Modelo não salvo: ' + ' | '.join(validation[:5]))
        if basic['dispatch_rule'] not in ('EDD', 'FIFO', 'SPT'):
            raise StudioError('Regra de despacho inválida.')
        path = self._project_file(pid)
        previous = {}
        if path.is_file():
            try: previous=json.loads(path.read_text('utf-8'))
            except (OSError,ValueError,TypeError): pass
        now = datetime.now(timezone.utc).isoformat()
        document = {**basic, 'id':pid, 'name':name or previous.get('name','Projeto principal'),
            'created_at':previous.get('created_at',now),'updated_at':now,
            'spec':asdict(ExperimentSpec(**state['nx_spec'])),
            'delay_h':state.get('op_delay',2.)}
        # Checkpoint records the last *complete* model/spec to assist startup.
        files={self.storage/'projeto.json':basic,
               path:document,
               self.storage/'projeto_ativo.json':{'id':pid},
               self.storage/'projeto_confirmado.json':document}
        try:
            atomic_bundle(files)
        except (OSError,ValueError,TypeError) as exc:
            raise StudioError('Falha ao gravar projeto. Estado anterior preservado sempre que possível: '+str(exc)) from exc

    def projects(self):
        """Project chooser; no duplicate workspaces and no network dependency."""
        out=[]
        for path in sorted(self.projects_dir.glob('*.json')):
            try:
                data=json.loads(path.read_text('utf-8'))
                out.append({'id':data['id'],'name':data['name'],
                    'updated_at':data.get('updated_at'),
                    'stations':len(data.get('stations',{})),
                    'orders':len(data.get('orders',[])),
                    'active':data['id']==self.project_id})
            except (OSError,ValueError,TypeError,KeyError):continue
        return sorted(out,key=lambda x:x.get('updated_at') or '',reverse=True)

    def create_project(self,name,duplicate=True):
        with self.lock:
            name=self._project_name(name)
            if len(self.projects())>=40:raise StudioError('Limite de 40 projetos locais atingido.')
            candidate=deepcopy(self.state)
            if not duplicate:
                candidate['stations']=deepcopy(STATIONS_BASE)
                candidate['orders']=deepcopy(ORDERS_BASE)
                candidate['nx_rule']='EDD'
                invalidate_model(candidate)
            candidate['nx_source']='Projeto local · '+name
            pid=uuid.uuid4().hex[:12]
            station='CNC' if 'CNC' in candidate['stations'] else next(iter(candidate['stations']))
            self._commit_calculation(candidate,{'station':station,'start_h':4,'duration_h':8},
                                     project_id=pid, project_name=name)
            return self.info()

    def open_project(self,project_id):
        with self.lock:
            path=self._project_file(project_id)
            if not path.is_file():raise StudioError('Projeto não encontrado.')
            try: data=json.loads(path.read_text('utf-8'))
            except (OSError,ValueError,TypeError) as exc:raise StudioError('Não foi possível ler o projeto.') from exc
            errors=validate_model(data['stations'],data['orders'])+_operability_errors(data['stations'],data['orders'])
            if errors:raise StudioError('Projeto inválido: '+'; '.join(errors[:3]))
            candidate=deepcopy(self.state)
            candidate.update(stations=deepcopy(data['stations']),orders=deepcopy(data['orders']),
                             nx_rule=data.get('dispatch_rule','EDD'),nx_source='Projeto local · '+data['name'])
            invalidate_model(candidate)
            payload=dict(data.get('spec') or {})
            payload['station']=payload.get('station') if payload.get('station') in candidate['stations'] else next(iter(candidate['stations']))
            payload['delay_h']=data.get('delay_h',2.)
            self._commit_calculation(candidate,payload,project_id=project_id,project_name=data['name'])
            return self.info()

    def rename_project(self,name):
        with self.lock:
            name=self._project_name(name)
            self._persist_model(name=name)
            self.state['nx_source']='Projeto local · '+name
            return self.info()

    def _model_hash(self):
        raw=json.dumps({'stations':self.state['stations'],'orders':self.state['orders'],
            'rule':self.state.get('nx_rule')},sort_keys=True,ensure_ascii=False)
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def experiment_list(self):
        with self.lock:
            out=[]
            for path in self.experiments_dir.glob('*.json'):
                try:
                    d=json.loads(path.read_text('utf-8'))
                    if d.get('project_id')==self.project_id:
                        out.append({k:d.get(k) for k in ('id','name','created_at','model_hash',
                            'project_id','run_id','spec','metrics','selected_action','selected_signature')})
                except (OSError,TypeError,ValueError):continue
            return sorted(out,key=lambda x:x.get('created_at') or '',reverse=True)

    def save_experiment(self,name):
        with self.lock, self._writing_workspace():
            name=self._project_name(name)
            if len(self.experiment_list())>=100:raise StudioError('Limite de 100 experimentos por projeto atingido.')
            a=current_analysis(self.state)
            if not a:raise StudioError('Execute uma simulação antes de guardar o experimento.')
            selected=selected_action(self.state,a)
            data={'id':uuid.uuid4().hex[:16], 'name':name,
                'created_at':datetime.now(timezone.utc).isoformat(),
                'project_id':self.project_id,'run_id':a['run_id'],
                'model_hash':self._model_hash(),
                'spec':asdict(ExperimentSpec(**self.state['nx_spec'])),
                'dispatch_rule':self.state['nx_rule'],
                'delay_h':self.state.get('op_delay'),
                'metrics':{'incident':_summary(a['incident']),
                           'response':_summary(selected.get('result')) if selected else None},
                'selected_signature':selected.get('signature') if selected else None,
                'selected_action':selected.get('action') if selected else None,
                'assumptions':a.get('evaluation_assumptions',[]),
                'basis':'Experimento sintético; restrições físicas não integralmente validadas.'}
            _atomic_json(self.experiments_dir/(data['id']+'.json'),data)
            return data

    def compare_experiments(self,first,second):
        with self.lock:
            allowed={r['id'] for r in self.experiment_list()}
            if first not in allowed or second not in allowed or first==second:
                raise StudioError('Selecione dois experimentos distintos do projeto atual.')
            one=json.loads((self.experiments_dir/(first+'.json')).read_text('utf-8'))
            two=json.loads((self.experiments_dir/(second+'.json')).read_text('utf-8'))
            k=('late_orders','sla_pct','makespan_h','total_cost')
            a=one['metrics']['response'] or one['metrics']['incident'] or {}
            b=two['metrics']['response'] or two['metrics']['incident'] or {}
            return _json_safe({'first':one,'second':two,
                'same_model':one['model_hash']==two['model_hash'],
                'delta':{x:(metric(b,x)-metric(a,x)) if isinstance(a.get(x),(int,float)) and isinstance(b.get(x),(int,float)) else None for x in k},
                'note':'Comparação retrospectiva. Custos de ações somente quando modelados; modelos distintos não isolam o efeito da intervenção.'})

    @staticmethod
    def _prepared_replays(state):
        a=current_analysis(state)
        if not a:
            return {'normal':replay_payload(nominal(state))}
        row=selected_action(state,a)
        replays={'normal':replay_payload(a['normal']),
                 'incident':replay_payload(a['incident'])}
        if row and row.get('result'):
            replays['response']=replay_payload(row['result'])
        return replays

    def _rebuild_replays(self):
        self._replays=self._prepared_replays(self.state)

    def _commit_calculation(self, candidate, payload, *, project_id=None, project_name=None, initial=False):
        """Compute and persist candidate before replacing the visible state."""
        old=ExperimentSpec(**candidate['nx_spec'])
        params={k:v for k,v in payload.items() if k in asdict(old)}
        spec=replace(old,**params)
        if 'delay_h' in payload:
            try: d=float(payload['delay_h'])
            except (ValueError,TypeError,OverflowError) as exc:
                raise StudioError('Espera da intervenção inválida.') from exc
            if not 0<=d<=168:raise StudioError('Espera da intervenção fora do intervalo permitido.')
            candidate['op_delay']=d
        if 'rule' in payload:
            rule=str(payload['rule'])
            if rule not in ('EDD','FIFO','SPT'):raise StudioError('Regra de despacho inválida.')
            candidate['nx_rule']=rule
        if candidate.get('nx_rule') not in ('EDD','FIFO','SPT'):
            raise StudioError('Regra de despacho inválida.')
        errors=validate_model(candidate['stations'],candidate['orders']) + _operability_errors(candidate['stations'],candidate['orders'])
        if errors:raise StudioError('Modelo inválido: '+' | '.join(errors[:8]))
        # The priority must name a current order, never a stale ID from a rename.
        if spec.objective=='critical' and spec.critical_order not in {o['id'] for o in candidate['orders']}:
            raise StudioError('O pedido prioritário não existe no modelo atual. Escolha um pedido válido.')
        try:
            execute(candidate,spec,source='Interface integrada')
            replays=self._prepared_replays(candidate)
        except (ValueError,OverflowError,TypeError,KeyError,IndexError) as exc:
            raise StudioError('Simulação não concluída: '+str(exc)) from exc
        try:
            self._persist_model(candidate,project_id,project_name)
        except StudioError:
            if not initial: raise
            # A read-only disk on startup must not prevent inspection of the
            # last model that could be loaded; warn instead of pretending saved.
            self._recovery_warning='Abertura somente leitura: não foi possível confirmar a gravação local.'
        self.state=candidate
        self._replays=replays
        self.project_id=project_id or self.project_id
        self._last_config=_json_safe({'spec':asdict(spec),'delay_h':candidate['op_delay']})
        return self.info()

    def _analysis_signature(self):
        analysis=current_analysis(self.state)
        if not analysis:
            return None
        context={'run_id':analysis['run_id'],'project_id':self.project_id,
            'model_hash':self._model_hash(), 'selected':self.state.get('nx_selected'),
            'delay_h':self.state.get('op_delay')}
        return hashlib.sha256(json.dumps(context,sort_keys=True,allow_nan=False).encode()).hexdigest()[:24]

    def _analysis_contexts(self):
        analysis=current_analysis(self.state)
        selected=selected_action(self.state,analysis) if analysis else None
        return experiment_contexts(self.state,self.project_id,selected)

    def _stamp_result(self, result, mode, payload, scope='lab'):
        """Immutable origin and deterministic, tool-specific configuration."""
        analysis=current_analysis(self.state)
        key=scope+':'+mode
        calculation_context=self._analysis_contexts()[key]
        context_signature=calculation_context['context_signature']
        actual_inputs=experiment_inputs(scope,mode,payload,self.state)
        project_name=next((x['name'] for x in self.projects() if x['active']),'Projeto principal')
        context={'schema':'am05-v2','scope':scope,'mode':mode,'context_key':key,
                 'project_id':self.project_id,'project_name':project_name,
                 'source':self.state.get('nx_source'),
                 'run_id':analysis['run_id'] if analysis else None,
                 'analysis_signature':self._analysis_signature(),
                 'context_signature':context_signature,'inputs':actual_inputs,
                 'dependencies':calculation_context['dependencies'],
                 'calculated_at':datetime.now(timezone.utc).isoformat()}
        context['signature']=experiment_signature({'context_signature':context_signature,
                                                   'inputs':actual_inputs})
        return _json_safe({**result,'provenance':context})

    def info(self):
        with self.lock:
            a=current_analysis(self.state)
            sel=selected_action(self.state,a) if a else None
            return _json_safe({'source':self.state.get('nx_source'),
                'active_project_id':self.project_id,
                'active_project_name':next((x['name'] for x in self.projects() if x['active']),'Projeto principal'),
                'projects':self.projects(),
                'experiment_count':len(self.experiment_list()),
                'stations':self.state['stations'],'orders':self.state['orders'],
                'rule':self.state.get('nx_rule','EDD'),
                'run_id':a.get('run_id') if a else None,
                'analysis_signature':self._analysis_signature(),
                'analysis_contexts':{k:{'context_signature':v['context_signature']}
                                     for k,v in self._analysis_contexts().items()},
                'spec':asdict(ExperimentSpec(**self.state['nx_spec'])),
                'delay_h':self.state.get('op_delay',2.),
                'policy':{'status':a.get('policy_status'),'reason':a.get('policy_explanation'),
                          'selection_reason':a.get('selection_reason')} if a else None,
                'metrics':{'normal':_summary(a['normal']),'incident':_summary(a['incident']),
                           'response':_summary(sel.get('result')) if sel else None} if a else None,
                'alternatives':[_candidate(r) for r in a['rows']] if a else [],
                'decision_review':review_alternatives([_candidate(r) for r in a['rows']],sel['signature'] if sel else None) if a else None,
                'selected':sel['signature'] if sel else None,
                'recommendation':a['leader']['signature'] if a and a.get('leader') else None,
                'assumptions':a.get('evaluation_assumptions',[]) if a else [],
                'replay':self._replays,
                'record':self.state.get('op_record'),
                'recovery_warning':self._recovery_warning,
                'history_count':len(archived_records(self.storage/'registros'))})

    def technical_audit(self):
        """Read-only, model-scoped engineering evidence for the active experiment."""
        with self.lock:
            analysis = current_analysis(self.state)
            if not analysis: raise StudioError('Não existe experimento calculado.')
            selected = selected_action(self.state, analysis)
            snapshot=summarize_audit(analysis, selected, self.state['orders'],
                self.state['nx_spec'], self.project_id, self._model_hash())
            snapshot['analysis_signature']=self._analysis_signature()
            return _json_safe(snapshot)

    def dashboards(self):
        """Read-only analytical snapshot for the current project and selected response.

        No simulation is executed here. All displayed values are copied from the
        cached DES result; alternatives retain their eligibility/assumption flags.
        """
        with self.lock:
            analysis = current_analysis(self.state)
            if not analysis:
                raise StudioError('Execute uma simulação antes de consultar os painéis.')
            selected = selected_action(self.state, analysis)
            scenarios = {}
            for key, result in (
                ('normal', analysis.get('normal')),
                ('incident', analysis.get('incident')),
                ('response', selected.get('result') if selected else None),
            ):
                if result is None:
                    continue
                scenarios[key] = {
                    'metrics': _summary(result),
                    'stations': [dict(row) for row in result.get('stations', [])],
                    'orders': [dict(row) for row in result.get('orders', [])],
                    'cost_breakdown': dict(result.get('cost_breakdown') or {}),
                }
            return _json_safe({
                'schema_version': '1.0',
                'analysis_signature': self._analysis_signature(),
                'run_id': analysis['run_id'],
                'project_id': self.project_id,
                'model_hash': self._model_hash(),
                'incident': asdict(ExperimentSpec(**self.state['nx_spec'])),
                'selected': selected.get('signature') if selected else None,
                'selected_action': _candidate(selected) if selected else None,
                'decision_review': review_alternatives([_candidate(row) for row in analysis['rows']],selected.get('signature') if selected else None),
                'scenarios': scenarios,
                'alternatives': [_candidate(row) for row in analysis['rows']],
                'assumptions': list(analysis.get('evaluation_assumptions') or analysis.get('assumptions') or []),
                'limitations': [
                    'Resultados derivados de um modelo de simulação; não são medições de chão de fábrica.',
                    'Competências individuais, buffers finitos e certas intervenções não têm verificação industrial completa.',
                    'Custo operacional e penalidades não equivalem ao custo da decisão; confira o investimento da intervenção selecionada.',
                    'A busca de alternativas enumeradas não demonstra ótimo global.',
                ],
            })

    def calculate(self, payload:dict, initial=False):
        with self.lock:
            candidate=deepcopy(self.state)
            return self._commit_calculation(candidate,payload,initial=initial)

    def select(self, signature:str):
        with self.lock:
            a=current_analysis(self.state)
            if not a: raise StudioError('Execute um experimento antes de selecionar a resposta.')
            row=next((r for r in a['rows'] if r['signature']==signature),None)
            if not row: raise StudioError('Alternativa não pertence ao experimento atual.')
            self.state['nx_selected']=signature
            self._rebuild_replays()
            return self.info()

    def set_model(self, payload:dict):
        with self.lock:
            stations=payload.get('stations'); orders=payload.get('orders')
            if not isinstance(stations,dict) or not isinstance(orders,list):
                raise StudioError('Modelo: informe postos e ordens.')
            errors=validate_model(stations,orders)+_operability_errors(stations,orders)
            if errors:raise StudioError(' | '.join(errors[:10]))
            if len(stations)>50 or len(orders)>200 or sum(int(o['quantidade']) for o in orders)>2500:
                raise StudioError('Modelo excede os limites desta estação (50 postos, 200 ordens, 2.500 unidades).')
            candidate=deepcopy(self.state)
            candidate.update(stations=deepcopy(stations),orders=deepcopy(orders),
                             nx_source='Modelo editado pelo usuário')
            invalidate_model(candidate)
            current=ExperimentSpec(**candidate['nx_spec'])
            updates={'station':current.station if current.station in stations else next(iter(stations))}
            if current.objective=='critical' and current.critical_order not in {o['id'] for o in orders}:
                # The user has renamed/deleted their priority. Clear a dangling
                # reference rather than persisting an unreopenable project.
                updates.update(objective='cost',critical_order='')
            return self._commit_calculation(candidate,updates)

    def reset(self):
        with self.lock:
            candidate=deepcopy(self.state)
            candidate.update(stations=deepcopy(STATIONS_BASE),orders=deepcopy(ORDERS_BASE),
                             nx_source='Exemplo sintético · PCP',nx_rule='EDD')
            invalidate_model(candidate)
            return self._commit_calculation(candidate,
                       {'station':'CNC','start_h':4,'duration_h':8,
                        'objective':'cost','critical_order':''})

    def decision(self,payload:dict):
        with self.lock, self._writing_workspace():
            a=current_analysis(self.state)
            if not a:raise StudioError('É necessário executar uma simulação.')
            signature=str(payload.get('signature') or self.state.get('nx_selected') or '')
            row=next((r for r in a['rows'] if r['signature']==signature),None)
            if not row:raise StudioError('Selecione uma alternativa válida.')
            if payload.get('expected_run_id') is not None and str(payload['expected_run_id'])!=str(a['run_id']):
                raise StudioError('A simulação mudou desde a elaboração da justificativa. Atualize os dados antes de registrar.')
            if row['action']!='Não intervir' and (not row.get('feasible') or not row.get('within_budget')):
                raise StudioError('Alternativa não atende à viabilidade ou ao limite de orçamento configurado.')
            note=str(payload.get('note') or '').strip()
            if len(note)<12:raise StudioError('Informe uma justificativa de pelo menos 12 caracteres.')
            if payload.get('constraints_ack') is False:
                raise StudioError('É necessário reconhecer as limitações do modelo antes de registrar.')
            responsible=str(payload.get('responsible') or '').strip()[:90]
            risks=str(payload.get('risks') or '').strip()[:650]
            money_audit=audit_decision_note(note,a,row)
            finance_ack=payload.get('finance_ack') is True
            if money_audit['unmatched'] and not finance_ack:
                written=', '.join(x['written'] for x in money_audit['unmatched'][:3])
                raise StudioError('Quantia não identificada nesta execução ('+written+'). Confira ou confirme que deseja registrá-la como não verificada.')
            candidate=deepcopy(self.state)
            candidate['nx_selected']=signature
            candidate['op_record']={'project_id':self.project_id,'run_id':a['run_id'],'signature':signature,'action':row['action'],
                'utc':datetime.now(timezone.utc).isoformat(),'requested_h':row.get('requested_h'),
                'effective_h':row.get('effective_h'),'objective':self.state['nx_spec']['objective'],
                'note':note[:1000], 'responsible':responsible, 'risks':risks,
                'constraints_ack':bool(payload.get('constraints_ack',False)),
                'physical_feasibility_verified':False,
                'model_hash':self._model_hash(),
                'monetary_audit':money_audit,
                'external_amounts_acknowledged':finance_ack if money_audit['unmatched'] else False,
                'cost_snapshot':cost_snapshot(a,row),
                'decision_review':review_alternatives([_candidate(r) for r in a['rows']],signature),
                'restriction_reasons':row.get('restriction_reasons') or []}
            raw=memo(candidate)
            prepared_replays=self._prepared_replays(candidate)
            try:
                path=save_record(self.storage/'registros',raw)
            except (OSError,ValueError,TypeError) as exc:
                raise StudioError('A decisão não foi registrada. Verifique as permissões da pasta e tente novamente.') from exc
            self.state=candidate
            self._replays=prepared_replays
            audit(self.state,'decision_recorded',row['action'],run_id=a['run_id'])
            return {'filename':path.name,'record':self.state['op_record']}

    def history(self):
        with self.lock:
            out=[]
            for item in archived_records(self.storage/'registros'):
                d=item['data'];r=d.get('record') or {}; ex=d.get('examined_action') or {}
                out.append({'filename':item['filename'],'utc':r.get('utc'), 'action':r.get('action'),
                    'note':r.get('note'),'run_id':r.get('run_id'),
                    'savings':ex.get('savings'),'sla_pct':ex.get('sla_pct'), 'makespan_h':ex.get('makespan_h')})
            return out

    def read_history(self, filename):
        items=archived_records(self.storage/'registros')
        item=next((i for i in items if i['filename']==filename),None)
        if item is None:raise StudioError('Registro não encontrado.')
        return item['data']

    def assistant(self,question):
        with self.lock:
            question=str(question or '').strip()
            if not 1<=len(question)<=1500:raise StudioError('Escreva uma pergunta de até 1.500 caracteres.')
            analysis=current_analysis(self.state)
            selected=selected_action(self.state,analysis) if analysis else None
            a=explain(question,analysis,selected,[o['id'] for o in self.state['orders']])
            if a is None:
                a=decision_answer(question,self.state)
            # Read-only: proposals do not execute automatically.
            return {'text':a.get('text'),'label':a.get('label'),'rows':a.get('rows') or [],
                'proposal_available':bool(a.get('proposal'))}

    def lab(self,payload):
        with self.lock:
            a=current_analysis(self.state)
            if not a:raise StudioError('Execute uma simulação antes de abrir o laboratório.')
            mode=str(payload.get('mode') or '')
            cfg=base_config(self.state)
            spec=ExperimentSpec(**self.state['nx_spec'])
            points=[];notes=[]
            if mode=='duration':
                for hours in [0,1,2,4,6,8,12]:
                    if hours==0:r=run_simulation(cfg)
                    else:r=run_simulation(scenario_from_incident(cfg,spec.station,spec.start_h,hours))
                    points.append({'label':f'{hours} h','duration_h':hours,
                        'total_cost':r['total_cost'],'makespan_h':r['makespan_h'],
                        'sla_pct':r['sla_pct'],'late_orders':r['late_orders']})
                notes.append('Variação isolada da duração da parada; demais entradas mantidas.')
            elif mode=='dispatch':
                for rule in ('EDD','SPT','FIFO'):
                    alt=cfg.clone();alt.dispatch_rule=rule
                    r=run_simulation(scenario_from_incident(alt,spec.station,spec.start_h,spec.duration_h))
                    points.append({'label':rule,'total_cost':r['total_cost'], 'makespan_h':r['makespan_h'],
                        'sla_pct':r['sla_pct'],'late_orders':r['late_orders']})
                notes.append('As três regras são avaliadas no mesmo incidente e na mesma semente.')
            elif mode=='robustness':
                row=selected_action(self.state,a)
                if not row or not row.get('timed_action'):
                    raise StudioError('Selecione uma intervenção temporal para executar o teste pareado.')
                res=paired_response(row,range(700,706))
                return self._stamp_result({'mode':mode,'pairs':res['pairs'],'mean_net_saving':res['mean_net_saving'],
                        'min_net_saving':res['min_net_saving'],'max_net_saving':res['max_net_saving'],
                        'notes':['Seis sementes sintéticas pareadas; não é intervalo de confiança industrial.']},mode,payload)
            elif mode=='stress':
                result=stress_test(cfg, runs=16, max_absent=1, demand_low=.9,
                                   demand_high=1.2, durations=(2.,4.,8.),seed=2026)
                points=[{'label':f"#{r['Run']:02d} · {r['Posto afetado']}",'sla_pct':r['SLA'],
                         'makespan_h':r['Makespan'],'unit_cost':r['Custo/un'],
                         'throughput_h':r['Throughput']} for r in result['runs']]
                return self._stamp_result({'mode':mode,'points':points,'summary':result['summary'],
                    'notes':['16 perturbações sintéticas reproduzíveis. Fragilidade relativa do modelo; não são frequências de falhas medidas na indústria.']},mode,payload)
            elif mode=='capacity':
                target=float(payload.get('min_sla',80))
                throughput=float(payload.get('target_throughput',5.5))
                if not 0<=target<=100 or not 0<throughput<=100000:
                    raise StudioError('Meta de serviço ou throughput fora do intervalo permitido.')
                base=nominal(self.state)
                rows=goal_seek(cfg,base,target_throughput=throughput,target_sla=target,
                               max_extra_workers=2,max_extra_machines=1,max_results=12)
                points=[{'label':r['Cenário'],'sla_pct':r['SLA'],
                        'makespan_h':r['Makespan'],'unit_cost':r['Custo/un'],
                        'throughput_h':r['Throughput'],'goal_met':r['Atinge meta']=='Sim',
                        'added_workers':r['Operadores +'],'added_machines':r['Máquinas +']}
                        for r in rows]
                return self._stamp_result({'mode':mode,'points':points,'notes':[
                     'Busca discreta de capacidade sobre operação nominal, sem indisponibilidade; não inclui custos de contratação ou compra e não prova ótimo global.']},mode,payload)
            elif mode=='goal':
                target=float(payload.get('min_sla',80))
                if not 0<=target<=100:raise StudioError('Meta de SLA fora do intervalo permitido.')
                for row in a['rows']:
                    if row.get('feasible') and row.get('within_budget') and row.get('sla_pct',0)>=target:
                        points.append({'label':row['action'],'sla_pct':row['sla_pct'],
                            'total_cost':row.get('decision_cost'), 'makespan_h':row['makespan_h'],
                            'savings':row.get('savings')})
                points.sort(key=lambda x:(x['total_cost'] is None,x['total_cost'] or 0))
                notes.append('Busca restrita às alternativas enumeradas. Não demonstra ótimo global.')
            else:raise StudioError('Experimento de laboratório não reconhecido.')
            return self._stamp_result({'mode':mode,'points':points,'notes':notes},mode,payload)

    def advanced(self, payload:dict):
        """Advanced tools from the historical engine, exposed in the SAME local workspace.

        All tests are read-only experiments. They never alter the selected response,
        project model, decision record, or simulation run ID.
        """
        with self.lock:
            mode=str(payload.get('mode') or 'diagnostic')
            allowed={'diagnostic','opportunities','sensitivity','demand','uncertainty','recovery'}
            if mode not in allowed:
                raise StudioError('Análise avançada não reconhecida.')
            a=current_analysis(self.state)
            if not a:
                raise StudioError('Execute uma simulação antes de usar esta análise.')
            cfg=base_config(self.state)
            nominal_result=nominal(self.state)
            incident=a['incident']
            base_note=('Dados sintéticos. Experimentos de apoio à análise; '
                'não garantem a viabilidade física nem demonstram ótimo global.')
            if mode=='diagnostic':
                result={
                    'run_id':a['run_id'],
                    'quality':model_confidence(self.state['stations'],self.state['orders']),
                    'bottleneck':incident.get('bottleneck'),
                    'alerts':operating_alerts(incident),
                    'comparison':explain_comparison(nominal_result, incident),
                    'stations':[{k:r.get(k) for k in ('Posto','Nome','Utilização máquina (%)',
                        'Espera média (min)','Fila máx.')} for r in incident.get('stations',[])],
                    'notes':[base_note,'A completude cadastral não comprova calibração industrial.']}
            elif mode=='opportunities':
                rows=generate_opportunities(cfg,nominal_result,max_candidates=28)
                result={'rows':[{k:r.get(k) for k in ('Ação','Throughput Δ (%)',
                    'SLA Δ (p.p.)','Custo/un Δ (%)','Makespan Δ (%)',
                    'Score de oportunidade')} for r in rows],
                    'basis':'Operação nominal, sem a parada configurada.',
                    'notes':[base_note,'Acréscimos de máquinas e operadores não incluem custos de aquisição/contratação, skills ou limites de buffers.']}
            elif mode=='sensitivity':
                station=str(payload.get('station') or self.state['nx_spec']['station'])
                if station not in cfg.stations:raise StudioError('Posto não encontrado no modelo.')
                resource=str(payload.get('resource') or 'operadores')
                if resource not in ('operadores','maquinas'):
                    raise StudioError('Selecione máquinas ou operadores.')
                rows=sensitivity_analysis(cfg,nominal_result,station,resource,max_add=3)
                result={'station':station,'resource':resource,
                    'rows':[{k:r.get(k) for k in ('Adição','Throughput','SLA','Custo/un',
                        'Makespan','Ganho marginal TP','Throughput Δ (%)','Gargalo')} for r in rows],
                    'notes':[base_note,'Experimentos sobre operação nominal. Investimento, habilitação e disponibilidade adicional não verificados.']}
            elif mode=='demand':
                floor=float(payload.get('min_sla',80))
                if not 0<=floor<=100:raise StudioError('Meta de SLA fora do intervalo.')
                r=demand_breakpoint(cfg,sla_floor=floor,demand_start=1.,demand_stop=1.6,step=.1)
                result={'rows':[{k:x.get(k) for k in ('Demanda x','SLA','Throughput','Makespan','Gargalo')}
                       for x in r['points']],
                    'first_break':r['first_break'].get('Demanda x') if r['first_break'] else None,
                    'last_safe':r['last_safe'].get('Demanda x') if r['last_safe'] else None,
                    'min_sla':floor,'notes':[base_note,'Variação sintética entre 1,0 e 1,6 vezes a demanda.']}
            elif mode=='uncertainty':
                spec=ExperimentSpec(**self.state['nx_spec'])
                crisis=scenario_from_incident(cfg,spec.station,spec.start_h,spec.duration_h)
                r=monte_carlo_analysis(crisis,runs=12,seed_start=2100)
                result={'rows':r['runs'],'summary':r['summary'],
                    'dominant_bottleneck':r['dominant_bottleneck'],
                    'bottleneck_share':r['bottleneck_share'],
                    'notes':[base_note,'12 sementes diferentes da mesma falha; dispersão interna do modelo, não probabilidade empírica de falha.']}
            else:  # recovery
                crisis=incident['config']
                rows=recovery_plan(crisis,incident,max_results=8,
                                   action_at_h=float(self.state['nx_spec']['start_h'])+float(self.state.get('op_delay',2.)))
                result={'rows':[{k:r.get(k) for k in ('Ação','SLA','SLA Δ (p.p.)',
                    'Throughput','Throughput Δ (%)','Makespan','Custo/un','Gargalo',
                    'Solicitação (h)','Efetivação (h)','Custo cenário (R$)','Investimento adicional (R$)')}
                    for r in rows], 'basis':'Intervenções de capacidade sobre o cenário com falha.',
                    'notes':[base_note,'Reforços são aplicados somente no instante de resposta (falha + espera configurada); histórico anterior é compartilhado.','Custo de cenário inclui capacidade após a ação e multas, mas não inclui investimento adicional em pessoal/equipamentos, que depende de orçamento externo.']}
            return self._stamp_result({'mode':mode,'experiment_id':a['run_id'],**result},mode,payload,scope='advanced')

    def export_model(self):
        return json.dumps({'stations':self.state['stations'],'orders':self.state['orders'],
            'dispatch_rule':self.state.get('nx_rule','EDD')},ensure_ascii=False,indent=2).encode('utf-8')

    def export_decision(self):
        if not current_analysis(self.state):raise StudioError('Execute primeiro uma simulação.')
        return memo(self.state)
