"""Application commands and serializable data for the single operation workspace."""
from dataclasses import asdict,replace
from datetime import datetime,timezone
from hashlib import sha256
from html import escape
import json
import os
from uuid import uuid4
from simulation.nexus import (initialize,nominal,current_analysis,current_spec,base_config,execute,
    selected_action,ExperimentSpec,audit,use_demo,invalidate_model)
from simulation.nexus_ai import local_answer,generative_answer,execute_proposal,make_proposal,plain,brl,fmt
from simulation.replay import replay_payload
from simulation.response import timing_frontier
from simulation.decision_lab import config_signature
from simulation.atlas import safe_summary


def initialize_operation(state):
    initialize(state)
    state['op_enabled']=True
    state.setdefault('op_token',uuid4().hex)
    state.setdefault('op_seen',[])
    state.setdefault('op_delay',2.)
    state.setdefault('op_notice',None)


def message(state,role,text,label='',rows=None):
    data=current_analysis(state)
    state['nx_messages']=(state.get('nx_messages',[])+[{'role':role,'text':text,'label':label,
        'rows':rows or [],'run_id':data['run_id'] if data else None}])[-30:]


def ask(state,question):
    question=str(question).strip()
    if not question or len(question)>4000:raise ValueError('Escreva uma pergunta de até 4.000 caracteres.')
    message(state,'user',question)
    key=state.get('nx_api_key') or os.environ.get('OPENAI_API_KEY')
    if state.get('nx_ai_mode')=='Generativo · OpenAI' and key:
        try:answer=generative_answer(question,state,key,state.get('nx_ai_model','gpt-4.1-mini'))
        except Exception:
            answer=decision_answer(question,state)
            answer['text']='O provedor não respondeu; análise local a seguir.\n\n'+answer['text']
    else:answer=decision_answer(question,state)
    message(state,'assistant',answer['text'],answer['label'],answer.get('rows'))
    if answer.get('proposal'):state['nx_pending']=answer['proposal']


def decision_answer(question,state):
    """Short readout of the examined response; retain the sealed tool proposal."""
    answer=local_answer(question,state);data=current_analysis(state)
    if not data:return answer
    selected=selected_action(state,data);q=plain(question)
    before=data['incident']
    if any(w in q for w in ('atras','pedido','risco')) and not answer.get('proposal'):
        orders=selected['order_impacts'] if selected else [{'id':o['OP'],'due_h':o['Prazo (h)'],'before_h':o['Conclusão (h)'],'after_h':o['Conclusão (h)'],'late_before':o['Status']=='Atrasada'} for o in before['orders']]
        affected=[o for o in orders if o['late_before']]
        answer['text']='\n'.join(f"**{o['id']}** · prazo {fmt(o['due_h'])} h; sem resposta {fmt(o['before_h'])} h; resposta examinada {fmt(o['after_h'])} h." for o in affected) or 'Nenhum pedido está previsto em atraso no experimento atual.'
        answer['rows']=[]
    elif any(w in q for w in ('compar','alternativ')) and not answer.get('proposal'):
        answer['text']=f"Referência sem resposta: **{brl(before['total_cost'])}**, **{before['sla_pct']:g}%** dos pedidos no prazo. As opções abaixo usam a mesma falha e o mesmo histórico."
        answer['rows']=answer.get('rows',[])[:3]
    elif selected:
        recovered=', '.join(selected.get('recovered_orders',[])) or 'nenhum pedido'
        issues='; '.join(selected.get('restriction_reasons',[]))
        answer['text']=(f"**Em exame: {selected['action']}**\n"
            f"Economia líquida **{brl(selected['savings'])}**; entregas no prazo **{selected['sla_pct']:g}%**; conclusão **{fmt(selected['makespan_h'])} h**.\n"
            f"Recupera o prazo de {recovered}.\n"+
            (f"**Restrição:** {issues}." if issues else data.get('selection_reason','')))
        if any(w in q for w in ('esper','quando','tempo')):
            answer['text']+='\nUse “Custo de esperar” para recalcular esta resposta em outros momentos.'
        answer['rows']=[]
    if answer.get('proposal'):
        answer['text']+='\n**Novo teste preparado.** Revise os parâmetros abaixo e execute para atualizar os resultados.'
    return answer


def handle_command(state,command):
    """User actions are idempotent and bound to the current model workspace."""
    if not isinstance(command,dict):return False
    cid=command.get('id')
    if not isinstance(cid,str) or not cid or cid in state.get('op_seen',[]):return False
    state['op_seen']=(state.get('op_seen',[])+[cid])[-80:]
    state['op_ack']=cid;state['op_notice']=None
    try:
        if command.get('token')!=state['op_token']:
            raise ValueError('O modelo foi alterado. Atualize a tela antes de executar a ação.')
        kind=command.get('kind');body=command.get('body') or {}
        if not isinstance(body,dict):raise ValueError('Os parâmetros do comando precisam ser um objeto.')
        if kind=='simulate':
            original_delay=state['op_delay']
            delay=float(body.get('delay_h',original_delay))
            spec=replace(current_spec(state),**{k:body[k] for k in ('station','start_h','duration_h','budget','min_sla','cost_worker','cost_machine','cost_express','objective','critical_order','budget_is_limit') if k in body})
            state['op_delay']=delay
            try:
                result=execute(state,spec,source='Ensaio de decisão',authorization=cid)
                if body.get('focus_action'):
                    focused=next((r for r in result['rows'] if r['action']==body['focus_action']),None)
                    if focused:state['nx_selected']=focused['signature']
            except Exception:state['op_delay']=original_delay;raise
            state.pop('nx_pending',None)
        elif kind=='demo':
            old_delay=state['op_delay'];new_backup='nx_model_backup' not in state
            state['op_delay']=2.;use_demo(state)
            if new_backup:state['nx_model_backup']['op_delay']=old_delay
            state['op_token']=uuid4().hex
        elif kind=='select':
            data=current_analysis(state)
            row=next((r for r in data['rows'] if r['signature']==body.get('signature')),None) if data else None
            if not row:raise ValueError('A resposta selecionada não pertence ao experimento atual.')
            state['nx_selected']=row['signature'];state.pop('op_timing',None)
        elif kind=='timing':
            data=current_analysis(state);row=selected_action(state,data)
            if not data or not row:raise ValueError('Calcule e selecione uma resposta primeiro.')
            state['op_timing']={'run_id':data['run_id'],'signature':row['signature'],'points':timing_frontier(data,row),'action':row['action']}
            audit(state,'timing',row['action'],authorization=cid,run_id=data['run_id'])
        elif kind=='sensitivity':
            data=current_analysis(state);row=selected_action(state,data)
            if not data or not row or not row.get('timed_action'):raise ValueError('Selecione uma intervenção para testar.')
            state['nx_pending']=make_proposal(state,current_spec(state),kind='sensitivity',action_signature=row['signature'])
        elif kind=='ask':ask(state,body.get('question',''))
        elif kind=='authorize':
            plan=state.get('nx_pending')
            if not plan or plan['id']!=body.get('proposal_id'):raise ValueError('O plano não está mais disponível.')
            kind=plan['kind'];execute_proposal(state,plan)
            if kind=='compare':
                answer=decision_answer('Explique essa decisão para um gerente industrial',state)
                message(state,'assistant',answer['text'],answer['label'])
            else:message(state,'assistant','As oito replicações pareadas foram concluídas. Confira a faixa de economia na aba Respostas.','RESULTADO SIMULADO')
        elif kind=='discard':state.pop('nx_pending',None)
        elif kind=='navigate':
            if body.get('page') not in ('Decisão','Modelo','Registros'):
                raise ValueError('Área indisponível.')
            state['op_next_page']=body['page']
        elif kind=='record':
            data=current_analysis(state);row=selected_action(state,data)
            if not data or not row:raise ValueError('Selecione uma resposta atual para registrar.')
            previous_record=state.get('op_record')
            state['op_record']={'run_id':data['run_id'],'signature':row['signature'],'action':row['action'],
                'utc':datetime.now(timezone.utc).isoformat(),'requested_h':row.get('requested_h'),'effective_h':row.get('effective_h'),
                'objective':current_spec(state).objective,'critical_order':current_spec(state).critical_order,
                'note':str(body.get('note',''))[:1000],'restriction_reasons':row.get('restriction_reasons',[])}
            if state.get('op_store_dir'):
                try:
                    from simulation.decision_store import save_record
                    save_record(state['op_store_dir'],memo(state))
                except (OSError,ValueError) as exc:
                    if previous_record:state['op_record']=previous_record
                    else:state.pop('op_record',None)
                    raise ValueError('Não foi possível gravar o registro no computador. Verifique a pasta registros e tente novamente.') from exc
            audit(state,'decision_recorded',row['action'],run_id=data['run_id'])
            state['op_notice']='Decisão registrada para este experimento. O relatório está disponível em Registros.'
        else:raise ValueError('Comando não reconhecido.')
    except (ValueError,TypeError,KeyError,OverflowError) as exc:
        state['op_notice']=str(exc)
    return True


def pack_result(result):
    p=replay_payload(result)
    p['orders']=result['orders']
    return p


def payload(state,presentation=False):
    data=current_analysis(state);normal=nominal(state);row=selected_action(state,data)
    fields=('action','signature','investment','decision_cost','savings','sla_pct','makespan_h','late_orders','rationale','verdict','within_budget','meets_sla','feasible','requested_h','effective_h','pareto','total_lateness_h','order_impacts','recovered_orders','restriction_reasons','critical_finish_h','critical_lateness_h')
    rows=[{k:r.get(k) for k in fields} for r in data['rows']] if data else []
    spec=asdict(current_spec(state));spec['delay_h']=float(state.get('op_delay',2.))
    return {'token':state['op_token'],'ack':state.get('op_ack'),'notice':state.get('op_notice'),
        'source':state.get('nx_source'),'model_signature':config_signature(base_config(state)),
        'run_id':data['run_id'] if data else None,'presentation':bool(presentation),
        'normal':pack_result(normal),'incident':pack_result(data['incident']) if data else None,
        'response':pack_result(row['result']) if row else None,'selected':row['signature'] if row else None,
        'recommended':data['leader']['signature'] if data and data.get('leader') else None,
        'rows':rows,'spec':spec,'status':data['policy_status'] if data else 'OPERAÇÃO SEM INCIDENTE',
        'selection_reason':data.get('selection_reason') if data else None,
        'assumptions':data.get('evaluation_assumptions',[]) if data else [],
        'messages':state.get('nx_messages',[]),'proposal':state.get('nx_pending'),
        'ai_mode':state.get('nx_ai_mode','Local · sem API'),'timing':state.get('op_timing'),
        'sensitivity':state.get('nx_sensitivity'),'record':state.get('op_record'),
        'orders':[{k:o.get(k) for k in ('id','produto','quantidade','prazo_h','route')} for o in state['orders']]}


def memo(state):
    data=current_analysis(state)
    if not data:raise ValueError('Calcule um experimento antes de exportar.')
    body=safe_summary(data);row=selected_action(state,data)
    body.update({'artifact':'ANTI-MURPHY / Resposta após a falha','run_id':data['run_id'],
        'examined_action':{k:row.get(k) for k in ('action','signature','requested_h','effective_h','investment','decision_cost','savings','sla_pct','makespan_h')} if row else None,
        'decision_criteria':{k:getattr(current_spec(state),k) for k in ('objective','critical_order','budget','budget_is_limit','min_sla')},
        'selection_reason':data.get('selection_reason'),
        'order_impacts':row.get('order_impacts',[]) if row else [],
        'timing':state.get('op_timing'),'sensitivity':state.get('nx_sensitivity'),'record':state.get('op_record'),
        'generated_utc':datetime.now(timezone.utc).isoformat()})
    body['sha256']=sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return json.dumps(body,ensure_ascii=False,indent=2).encode('utf-8')


def report(state):
    from pathlib import Path
    import base64
    data=json.loads(memo(state));a=data.get('examined_action') or {};record=data.get('record') or {}
    if not a:
        return ('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Anti-Murphy · Análise sem seleção</title>'
            '<style>body{font:16px/1.7 Segoe UI,Arial,sans-serif;background:#f7f7f3;color:#1d292d;max-width:960px;margin:40px auto;padding:24px}h1{border-left:4px solid #ff681b;padding-left:18px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}</style>'
            '<h1>Anti-Murphy · Análise sem seleção</h1><p>Nenhuma resposta está em exame. Selecione uma alternativa no aplicativo para exportar seu efeito nas entregas. Os resultados calculados e as restrições estão no memorando abaixo.</p><p>'
            +escape(data.get('status_reason',''))+'</p><details><summary>Memorando do experimento '+escape(data['run_id'])+'</summary><pre>'
            +escape(json.dumps(data,ensure_ascii=False,indent=2))+'</pre></details></html>').encode('utf-8')
    safe=lambda value:escape(str(value or ''))
    logo=base64.b64encode((Path(__file__).resolve().parents[1]/'assets/brand/logo-light.svg').read_bytes()).decode()
    reason=data.get('selection_reason','')
    rows=''.join('<tr><td>'+safe(o['id'])+'</td><td>'+fmt(o['due_h'])+' h</td><td>'+fmt(o['before_h'])+' h</td><td>'+fmt(o['after_h'])+' h</td><td>'+('Atrasa' if o['late_after'] else 'No prazo')+'</td></tr>' for o in data.get('order_impacts',[]))
    limits=''.join('<li>'+safe(s)+'</li>' for s in data.get('assumptions',[]))
    chosen=('<section><h2>Decisão registrada</h2><h3>'+safe(record.get('action'))+'</h3><p>'+safe(record.get('note') or 'Sem observação adicional.')+'</p><p class="small">Registro UTC '+safe(record.get('utc'))+'</p></section>') if record else '<p class="callout">Prévia de análise. Esta resposta ainda não foi registrada como decisão.</p>'
    if record and record.get('signature')!=a.get('signature'):
        chosen+='<p class="callout">A resposta examinada abaixo difere da decisão registrada acima.</p>'
    cards=''.join('<div><span>'+label+'</span><strong>'+safe(value)+'</strong></div>' for label,value in [
        ('Economia líquida prevista',brl(a.get('savings') or 0)),('Investimento de implantação',brl(a.get('investment') or 0)),
        ('Pedidos no prazo',fmt(a.get('sla_pct') or 0)+'%'),('Conclusão da carteira',fmt(a.get('makespan_h') or 0)+' h')])
    html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Anti-Murphy · Registro da decisão</title><style>
    *{box-sizing:border-box}body{font:15px/1.7 'Segoe UI',Arial,sans-serif;background:#f7f7f3;color:#1d292d;max-width:1120px;margin:35px auto;padding:25px}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #cbd4c4;padding-bottom:22px}header img{width:230px}header span,.small{font-size:12px;color:#61735a}h1{font-size:36px;line-height:1.2;letter-spacing:-1px;margin:35px 0 10px}h2{font-size:23px;margin:25px 0 10px}h3{font-size:18px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin:25px 0}.cards>div{border-left:2px solid #ff681b;padding-left:15px}.cards span{font-size:12px;display:block;color:#61735a}.cards strong{font-size:23px;display:block}section{background:#fff;border:1px solid #d8dfd2;border-radius:7px;padding:20px;margin:25px 0}.callout{border-left:3px solid #ff681b;padding:12px 18px;background:#fff0e3}table{width:100%;border-collapse:collapse;background:#fff}th,td{padding:13px 12px;text-align:left;border-bottom:1px solid #d8dfd2}th{font-size:12px;color:#61735a}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:11px}li{margin-bottom:9px}.table-scroll{overflow:auto}@media(max-width:650px){.cards{grid-template-columns:1fr 1fr}header{gap:20px}header img{width:160px}h1{font-size:28px}}@media print{body{background:#fff;margin:0;padding:10px}details{display:none}section{break-inside:avoid}.cards{break-inside:avoid}}
    </style><header><img alt="Anti-Murphy" src="data:image/svg+xml;base64,'''+logo+'''"><span>APOIO À DECISÃO / PCP<br>Resultados calculados por simulação</span></header><h1>Uma decisão com seus motivos.</h1><p class="small">Experimento '''+safe(data['run_id'])+' · '+safe(state.get('nx_source','Modelo do usuário'))+'</p>'+chosen+'<h2>Resposta examinada: '+safe(a.get('action'))+'</h2><div class="cards">'+cards+'</div><p>'+safe(reason)+'</p>'
    if a.get('requested_h') is not None:
        html+='<p>Solicitação em '+fmt(a['requested_h'])+' h · entrada efetiva em '+fmt(a['effective_h'])+' h.</p>'
    html+='<h2>O efeito nas entregas</h2><div class="table-scroll"><table><tr><th>Pedido</th><th>Prazo</th><th>Sem resposta</th><th>Resposta examinada</th><th>Condição final</th></tr>'+rows+'</table></div><h2>Hipóteses e limites</h2><ul>'+limits+'</ul><p class="small">Prioridades e orçamento: '+safe(json.dumps(data.get('decision_criteria',{}),ensure_ascii=False))+'. Dados do caso CNC são sintéticos; nenhuma máquina é acionada pelo aplicativo.</p><details><summary>Memorando completo e rastreabilidade</summary><pre>'+escape(json.dumps(data,ensure_ascii=False,indent=2))+'</pre></details><p class="small">SHA-256 do memorando: '+safe(data['sha256'])+'</p></body></html>'
    return html.encode('utf-8')
