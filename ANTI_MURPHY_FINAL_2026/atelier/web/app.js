/* Anti-Murphy workspace. No external runtime, no client-side industrial calculations.
 * Playback interpolates presentation time; all production events come from the DES.
 */
(() => {
'use strict';
const $ = id => document.getElementById(id);
const $$ = s => [...document.querySelectorAll(s)];
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// AM-11: ordinary figures retain their format; small nonzero values stay visible.
const numericText = (v,digits=2) => {
 const n=Number(v);if(!Number.isFinite(n))return '—';
 if(n!==0 && Math.abs(n)<.5*10**(-digits))return Math.abs(n)<1e-6?n.toExponential(3).replace('.',','):n.toLocaleString('pt-BR',{maximumSignificantDigits:4});
 return n.toLocaleString('pt-BR',{maximumFractionDigits:digits,minimumFractionDigits:digits});
};
const h = v => numericText(v,2);
const integer = v => Number.isFinite(Number(v)) ? Number(v).toLocaleString('pt-BR',{maximumFractionDigits:0}) : '—';
const brl = v => Number.isFinite(Number(v)) ? new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(Math.abs(Number(v))<.5?0:Number(v)) : '—';
const brlExact = v => Number.isFinite(Number(v)) ? new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',minimumFractionDigits:2,maximumFractionDigits:2}).format(Number(v)) : '—';
const time = v => Number.isFinite(Number(v)) ? `${String(Math.floor(v)).padStart(2,'0')}:${String(Math.floor((v%1)*60 + .0001)).padStart(2,'0')} h` : '—';
const icon = id => `<svg aria-hidden="true"><use href="#ico-${id}"/></svg>`;
const st = {data:null, view:'simulacao', scene:'incident', station:'CNC', order:null,
  playing:false, speed:1, pauseOnEvent:true, presentation:false, presentationStep:0, presentationOverview:false, reportOpened:false, t:0, lastFrame:0, lastPaint:0, lastInspectorPaint:0, zoom:1, wipe:50, focus:false,
  modelTab:'stations', lab:'duration', labHistory:[], labVisible:null, advanced:'diagnostic', advancedResult:null, editing:null, stageKey:'', toastTimer:null, navStack:[], savedExperiments:[], scheduleKey:'', helpTopic:'simulacao', tourStep:-1, tourOrigin:'simulacao'};
function analysisInputs(scope,mode){
 if(scope==='lab'){
  if(mode==='goal')return {min_sla:Number($('goal-value').value)};
  if(mode==='capacity')return {min_sla:Number($('goal-value').value),target_throughput:Number($('throughput-value').value)};
 }else{
  if(mode==='sensitivity')return {station:$('advanced-station').value,resource:$('advanced-resource').value};
  if(mode==='demand')return {min_sla:Number($('advanced-sla').value)};
 }
 return {};
}
const analysisHistory=window.AMAnalysisState.createStore(()=>({contexts:st.data?.analysis_contexts,inputs:analysisInputs}));
const pageHistoryNote='Histórico temporário desta página: recarregar ou fechar descarta os resultados. Exporte os arquivos para guardar. Nenhum ensaio é recalculado automaticamente.';
window.antiMurphyResultStatus=result=>analysisHistory.status(result);
function analysisOrigin(result){
 const p=result.provenance||{};
 return `Projeto: ${p.project_name||p.project_id||'?'} (${p.project_id||'?'}) · Execução: ${p.run_id||'?'} · Assinatura: ${p.signature||'?'} · ${p.calculated_at||''} · Entradas do ensaio: ${JSON.stringify(p.inputs||{})}`;
}
function analysisSample(result){
 const sample=result.sample||(result.summary?.viable_runs!==undefined?result.summary:null);
 if(!sample)return '';
 return `<p class="lab-secondary" role="status" data-analysis-sample>Execuções: ${integer(sample.runs)} · Viáveis: ${integer(sample.viable_runs)} · Inviáveis: ${integer(sample.infeasible_runs)}. Estatísticas somente das execuções viáveis; métricas dos inviáveis não são calculadas. ${sample.viable_runs===0?'Sem amostra viável para estatísticas.':''} ${result.mode==='stress'?'Taxa de resiliência usa todas as tentativas, incluindo inviáveis como não atendidas.':''}</p>`;
}
function analysisSearch(result){
 const q=result.search_space;if(!q)return '';
 return `<p class="lab-secondary" role="status" data-capacity-search>Espaço pesquisado: ${integer(q.candidates_evaluated)} candidatos avaliados · ${integer(q.returned_count)} exibidos. Limites totais: ${integer(q.max_extra_workers)} operadores e ${integer(q.max_extra_machines)} máquinas adicionais. Uma ou duas combinações posto/recurso por alternativa, incluindo máquina + operador no mesmo posto. A operação nominal é a referência. Busca limitada; não comprova ótimo global.</p>`;
}
function analysisBanner(result){
 const state=analysisHistory.status(result);
 return analysisSample(result)+analysisSearch(result)+`<div class="lab-secondary ${state.code==='desatualizado'?'am-stale-warning':''}" role="status" data-analysis-status="${state.code}"><b>${esc(state.label)}</b> · ${esc(analysisOrigin(result))}${state.code!=='atual'?'<p>Resultado anterior preservado. Confira a origem; execute novamente para obter dados da configuração vigente.</p>':''}</div>`;
}
function analysisHistoryMarkup(scope,mode,attribute){
 const entries=analysisHistory.list(scope,mode);
 return `<p class="lab-secondary">${esc(pageHistoryNote)}</p>`+(entries.length?`<details class="am-lab-history"><summary>Histórico desta página · ${entries.length} análises</summary>${entries.map(e=>`<button type="button" ${attribute}="${e.id}" class="subtle-button">${esc(analysisHistory.status(e.result).label)} · ${esc(e.result.provenance?.project_name||e.result.provenance?.project_id||'?')} · ${esc(e.result.provenance?.calculated_at||'')}</button>`).join('')}</details>`:'');
}
function refreshAnalysisViews(){
 renderLabInfo();renderAdvancedInfo();
 if(st.view==='paineis'&&dashUI.data)renderDashboards();
}
async function api(path,method='GET',body=null){
  let opts={method,headers:{}};
  if(body!==null){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(body)}
  const res=await fetch(path,opts);let data=await res.json().catch(()=>({error:`Resposta inválida (${res.status})`}));
  if(!res.ok)throw Error(data.error || `Erro ${res.status}`);
  return data;
}
function notify(message,error=false){
  const n=$('toast');n.textContent=message;n.classList.toggle('error',error);n.classList.add('show');
  clearTimeout(st.toastTimer);st.toastTimer=setTimeout(()=>n.classList.remove('show'),5000);
  $('status-message').textContent=message;
}
function busy(on,message){$('app').setAttribute('aria-busy',String(on));$('status-message').textContent=on?(message||'Calculando…'):'Pronto'}
async function perform(promise,success,refresh=true){
  try {busy(true);const result=await promise;
    if(refresh && result?.stations){applyData(result)}
    if(success)notify(success);
    return result;
  } catch(e){notify(e.message||'Não foi possível concluir a operação.',true);throw e}
  finally{busy(false)}
}
/* Presentation mode is a read-only guided camera over the SAME DES.
 * The six moments are bookmarks, not independent simulations or invented data. */
const presentationLabels=['Plano','Falha','Pedidos','Intervenção','Comparação','Evidências'];
/* The API evaluates weak Pareto dominance over three modeled indicators.
   This UI never substitutes physical availability or an optimizer for that evidence. */
function chosenRecord(){
 const d=st.data,r=d?.record;
 return r && r.run_id===d.run_id && r.signature===d.selected && r.constraints_ack ? r:null;
}
function decisionReviewMarkup(review=st.data?.decision_review,withAction=true){
 const status=review?.status||'unknown',rival=review?.dominated_by?.[0],n=review?.dominated_by?.length||0;
 const total=Number(review?.eligible_count)||0;
 const disclaimer='Somente alternativas enumeradas que atendem aos critérios modelados; não comprova ótimo global, disponibilidade de recursos nem viabilidade industrial.';
 if(status==='dominated'&&rival){
  return `<section class="decision-quality review-warning" aria-label="Comparação multicritério"><div class="review-heading"><span>ATENÇÃO À ESCOLHA</span><strong>Existe alternativa não pior em custo, prazo e SLA</strong></div><p><b>${esc(rival.action)}</b> apresenta custo de decisão de <b>${brlExact(rival.decision_cost)}</b>, conclusão de <b>${h(rival.makespan_h)} h</b> e SLA de <b>${h(rival.sla_pct)}%</b>. ${integer(n)} alternativa(s) dominam a seleção nesses três indicadores.</p><p class="review-caution">${disclaimer} Outros critérios podem justificar uma escolha diferente, mas devem ser explicados.</p>${withAction?`<button type="button" class="review-compare-action" data-review-select="${esc(rival.signature)}">Examinar alternativa concorrente →</button>`:''}</section>`;
 }
 if(status==='non_dominated')return `<section class="decision-quality review-positive" aria-label="Comparação multicritério"><div class="review-heading"><span>COMPARAÇÃO MULTICRITÉRIO</span><strong>${total===1?'Única alternativa que atende aos critérios modelados':'Seleção não dominada entre '+integer(total)+' alternativas elegíveis'}</strong></div><p>${total===1?'Não há outra alternativa elegível para uma comparação de dominância sob as metas atuais.':'Nenhuma outra alternativa elegível do experimento apresenta simultaneamente custo e makespan não maiores e SLA não menor, com melhoria estrita em algum deles.'}</p><p class="review-caution">${disclaimer}</p></section>`;
 if(status==='outside_criteria')return `<section class="decision-quality review-warning" aria-label="Critérios do modelo"><div class="review-heading"><span>CONDIÇÕES NÃO ATENDIDAS</span><strong>Esta seleção não atende integralmente aos critérios modelados</strong></div><p>Confira viabilidade, orçamento e meta de SLA antes de registrar. ${disclaimer}</p></section>`;
 return `<section class="decision-quality"><strong>Comparação multicritério indisponível</strong><p>Faltam resultados completos ou alternativa selecionada para confrontar custo, makespan e SLA.</p></section>`;
}
function bindReviewButtons(node){
 node?.querySelectorAll('[data-review-select]').forEach(button=>button.addEventListener('click',async()=>{
  await selectAlternative(button.dataset.reviewSelect);
  if(st.view==='decisoes')navigate('decisoes',{skipStack:true});
  else if(st.view==='analise')navigate('analise',{skipStack:true});
 }));
}
/* A presentation reveals only observations justified at the current stage.
 * Hidden values are still available in ordinary dashboards, never erased. */
function presentationEvidence(){
 const d=st.data||{},step=st.presentationStep;
 const nominal=metricFor('normal')||{},incident=metricFor('incident')||{},response=metricFor('response')||{};
 const action=d.alternatives?.find(row=>row.signature===d.selected)||{};
 const spec=d.spec||{},rec=chosenRecord();
 const tile=(label,value,foot,tone='')=>`<div class="presentation-fact ${tone}"><span>${esc(label)}</span><strong>${esc(value)}</strong><small>${esc(foot)}</small></div>`;
 if(step===0)return tile('CARTEIRA PROGRAMADA',`${integer(d.orders?.length||0)} pedidos`,'Condições originais da simulação')+
   tile('ENTREGAS NO PRAZO',`${h(nominal.sla_pct)}%`,'Referência sem ocorrência')+
   tile('CONCLUSÃO NOMINAL',`${h(nominal.makespan_h)} h`,'Tempo da programação inicial');
 if(step===1)return tile('INCIDENTE',spec.station||'—','Posto atingido pela parada modelada','fact-alert')+
   tile('INÍCIO DO EVENTO',time(spec.start_h),'Relógio da simulação')+
   tile('DURAÇÃO CONSIDERADA',`${h(spec.duration_h)} h`,'Impactos analisados na próxima etapa');
 if(step===2){
   const impacted=(action.order_impacts||[]).filter(o=>o.late_before).map(o=>o.id);
   return tile('PEDIDOS ATRASADOS',integer(incident.late_orders),'Sem qualquer intervenção','fact-alert')+
     tile('CUMPRIMENTO DE PRAZOS',`${h(incident.sla_pct)}%`,'Cenário A · ocorrência sem resposta')+
     tile('PEDIDOS AFETADOS',impacted.length?impacted.slice(0,3).join(' · '):'Nenhum',impacted.length>3?`E mais ${impacted.length-3} pedido(s)`:'Identificados nos cálculos do motor');
 }
 if(step===3)return tile('RESPOSTA CONSIDERADA',action.action||'—','Alternativa enumerada, não aplicada à fábrica real')+
   tile('INVESTIMENTO MODELADO',brlExact(action.investment),'Custos adicionais declarados')+
   tile('EFEITO A PARTIR DE',action.effective_h!=null?time(action.effective_h):'Ver simulação','Efetividade registrada no modelo');
 if(step===4)return tile('A · SEM INTERVENÇÃO',`${integer(incident.late_orders)} atraso(s)`,`SLA ${h(incident.sla_pct)}% · custo ${brlExact(incident.total_cost)}`,'fact-alert')+
   tile(action.action==='Não intervir'?'B · NÃO INTERVIR':'B · RESPOSTA MODELADA',`${integer(response.late_orders)} atraso(s)`,`SLA ${h(response.sla_pct)}% · decisão ${brlExact(action.decision_cost)}`,'fact-good')+
   tile('DIFERENÇA ECONÔMICA',brlExact(action.savings),'A frente a B; diferença do modelo, não caixa comprovado','fact-delta');
 return tile('ESTADO DO REGISTRO',rec?'Registrado':'Pendente',rec?'Justificativa preservada no histórico':'Revisar a escolha antes de salvar',rec?'fact-good':'fact-alert')+
   tile('RESPOSTA SELECIONADA',action.action||'—','A seleção permanece sob responsabilidade da equipe')+
   tile('PRÓXIMO PASSO',rec?'Abrir relatório':'Registrar evidências',rec?'Relatório com justificativa e limitações':'Descrever motivo, riscos e confirmar premissas');
}

function renderPresentationGuide(){
 const box=$('presentation-guide'),button=$('presentation-toggle');if(!box||!button)return;
 box.hidden=!st.presentation;
 document.body.classList.toggle('presentation-mode',st.presentation);
 button.setAttribute('aria-pressed',String(st.presentation));
 button.textContent=st.presentation?'Encerrar modo banca':'Modo banca';
 if(!st.presentation||!st.data)return;
 const step=st.presentationStep, spec=st.data.spec||{},selected=st.data.alternatives?.find(x=>x.signature===st.data.selected)||{};
 const impact=selected.order_impacts||[],risk=impact.filter(r=>r.late_before).map(r=>r.id);
 const descriptions=[
  'Referência nominal: filas, equipamentos e carteira conforme o cenário original.',
  `Parada modelada no posto ${spec.station||'—'}, a partir de ${time(spec.start_h)} durante ${h(spec.duration_h)} h.`,
  `${integer(metricFor('incident')?.late_orders)} pedido(s) com atraso no cenário sem resposta${risk.length?' · '+risk.slice(0,3).join(', '):''}.`,
  `${selected.action||'Resposta selecionada'} · ação hipotética sujeita a condições não verificadas em fábrica.`,
  'Dois futuros calculados no mesmo modelo; o custo da decisão inclui o investimento declarado.',
  chosenRecord()?'Decisão registrada. Consulte o registro e emita o relatório com justificativa, riscos e resultados.':'Conclua a justificativa e registre a decisão. Depois gere o relatório com evidências e limitações.'
 ];
 $('presentation-title').textContent=`${String(step+1).padStart(2,'0')} / 06 · ${presentationLabels[step]}`;
 $('presentation-description').textContent=descriptions[step];
 $('presentation-evidence').innerHTML=presentationEvidence();
 $('presentation-guide').dataset.phase=String(step);
 $('presentation-restart').hidden=!(step===5&&!!chosenRecord());
 $('presentation-guide').dataset.finalized=String(!!chosenRecord());
 $('presentation-steps').innerHTML=presentationLabels.map((name,i)=>`<button type="button" data-presentation-step="${i}" class="${i===step?'active':''}" aria-current="${i===step?'step':'false'}"><b>${String(i+1).padStart(2,'0')}</b><span>${name}</span></button>`).join('');
 $('presentation-prev').disabled=step===0;
 $('presentation-next').textContent=step===presentationLabels.length-1?(chosenRecord()?'Abrir relatório final ↗':'Concluir registro →'):'Próxima etapa →';
}
function goPresentationStep(step){
 if(!st.data)return;
 st.presentationStep=Math.max(0,Math.min(5,step));st.playing=false;st.focus=false;st.presentationOverview=false;
 const spec=st.data.spec||{};
 const start=Math.max(0,Number(spec.start_h)||0), duration=Math.max(0,Number(spec.duration_h)||0);
 const iv=replayFor('response')?.intervention||{};
 const effective=Number(iv.effective_h??iv.requested_h??start);
 const phase=st.presentationStep;
 if(phase===0){st.scene='normal';st.t=Math.min(horizon(),Math.max(0,start*.35));st.order=null;}
 if(phase===1){st.scene='incident';st.t=Math.min(horizon(),start+.001);st.station=spec.station||st.station;st.order=null;}
 if(phase===2){st.scene='incident';st.t=Math.min(horizon(),start+duration*.55);const impacts=st.data.alternatives?.find(x=>x.signature===st.data.selected)?.order_impacts||[];st.order=impacts.find(x=>x.late_before)?.id||st.data.orders?.[0]?.id||null;}
 if(phase===3){st.scene='response';st.t=Math.min(horizon(),Math.max(start,effective)+.002);st.order=null;}
 if(phase===4){st.scene='split';st.t=informativeComparisonTime();st.order=null;st.station=spec.station||st.station;}
 if(phase===5){st.scene='split';st.t=informativeComparisonTime();navigate('decisoes',{skipStack:true});updateDecisionValidation();}
 else if(st.view!=='simulacao')navigate('simulacao',{skipStack:true});
 renderScene(true);renderPresentationGuide();
 window.scrollTo({top:0,behavior:'instant'});
}
function togglePresentation(){
 st.presentation=!st.presentation;
 if(st.presentation){st.presentationStep=0;st.reportOpened=false;goPresentationStep(0);}
 else{renderPresentationGuide();notify('Modo banca encerrado. Todas as áreas permanecem disponíveis.');}
}
function navigate(name, options={}){
  const allowed=['simulacao','modelo','analise','paineis','laboratorio','avancadas','decisoes','historico'];
  if(!allowed.includes(name))name='simulacao';
  if(name!==st.view && !options.skipStack && !options.fromBrowser){st.navStack.push(st.view);}
  st.view=name;st.playing=false;
  $$('.view').forEach(el=>el.hidden=el.dataset.view!==name);
  $$('.rail-item').forEach(el=>{const active=el.dataset.nav===name;el.classList.toggle('active',active);el.setAttribute('aria-current',active?'page':'false')});
  $('top-context').textContent=({simulacao:'Simulação',modelo:'Modelo produtivo',analise:'Análise de impacto',paineis:'Painéis',laboratorio:'Laboratório',avancadas:'Análises avançadas',decisoes:'Decisões',historico:'Registros'})[name];
  if(!$('guide-panel').hidden && st.helpTopic!=='metric' && st.helpTopic!=='order' && st.helpTopic!=='impact')openHelp(name);
  $('back-home').disabled=name==='simulacao';
  $('back-previous').disabled=st.navStack.length===0 && name==='simulacao';
  $('back-previous').setAttribute('aria-label',st.navStack.length?'Voltar à área anterior':'Voltar à página inicial');
  if(name==='historico')loadHistory();
  if(name==='analise')loadExperiments();
  if(name==='modelo')renderModel();
  if(name==='simulacao')renderScene(true);
  if(st.presentation)renderPresentationGuide();
  if(name==='analise')renderAnalysis();
  if(name==='laboratorio')renderLabInfo();
  if(name==='paineis')openDashboards();
  if(name==='decisoes')renderDecisions();
  if(name==='avancadas')renderAdvancedInfo();
  if(!options.fromBrowser && window.location.hash!=='#'+name){
    window.history.pushState({amView:name},'', '#'+name);
  }
  window.scrollTo({top:0,behavior:'instant'});
}
function goBack(){
  const previous=st.navStack.pop()||'simulacao';
  navigate(previous,{skipStack:true});
}

const metrics = (label,value,foot,cls='') => `<div class="metric-unit ${cls}"><div class="metric-label">${esc(label)} <button class="metric-explain" type="button" data-metric="${esc(label)}" title="Como interpretar ${esc(label)}" aria-label="Explicar ${esc(label)}">?</button></div><strong class="metric-value">${esc(value)}</strong><div class="metric-foot">${esc(foot)}</div></div>`;
function applyData(data){
  // Snapshot panels refresh lazily; experiment histories remain inspectable.
  if(dashUI.data && (dashUI.data.run_id!==data.run_id || dashUI.data.selected!==data.selected || dashUI.data.project_id!==data.active_project_id)){dashUI.data=null;dashUI.audit=null;}
  st.data=data;
  if(data.recovery_warning && data.recovery_warning!==st.lastRecoveryWarning){st.lastRecoveryWarning=data.recovery_warning;notify(data.recovery_warning,true);}
  if(!data.stations[st.station])st.station=Object.keys(data.stations)[0];
  if(st.order && !data.orders.find(o=>o.id===st.order))st.order=null;
  $('project-source').textContent=data.active_project_name||'Projeto principal';
  $('status-run').textContent='Experimento '+(data.run_id||'—');
  fillParameters();
  renderAll();
}
function renderAll(){renderMetrics();renderScene(true);renderAnalysis();renderDecisions();renderLabInfo();renderAdvancedInfo();if(st.view==='modelo')renderModel();}
function currentReplay(){
  if(!st.data)return null;
  return st.data.replay[st.scene==='split'?'incident':st.scene] || st.data.replay.incident || st.data.replay.normal;
}
function replayFor(which){return st.data?.replay?.[which]||null}
function horizon(){
  if(!st.data)return 1;
  if(st.scene==='split')return Math.max(1,Number(replayFor('incident')?.horizon)||0,Number(replayFor('response')?.horizon)||0);
  return Math.max(1,Number(replayFor(st.scene)?.horizon)||0);
}
// At 1×, a simulated minute is 100 ms of real playback (10 simulated minutes/second).
// This ratio is independent of the experiment's total horizon.
const BASE_REPLAY_HOURS_PER_SECOND=10/60;
function playbackAdvance(deltaSeconds,speed=st.speed){return Math.max(0,deltaSeconds)*BASE_REPLAY_HOURS_PER_SECOND*speed;}
function pauseMarkers(){
  const p=st.scene==='normal'?null:replayFor(st.scene==='response'?'response':'incident');
  const markers=[];
  if(p?.outage?.start!=null)markers.push({t:Number(p.outage.start),label:'Início da parada · '+p.outage.station});
  const iv=replayFor('response')?.intervention;
  if(st.scene!=='normal'&&st.scene!=='incident'&&iv?.effective_h!=null)markers.push({t:Number(iv.effective_h),label:'Intervenção aplicada'});
  return markers.filter(m=>Number.isFinite(m.t)&&m.t>=0).sort((a,b)=>a.t-b.t);
}
function metricFor(which){return st.data?.metrics?.[which]||null}
/* One definition of cost across Simulação, Análise, Painéis and Decisões.
 * The DES total_cost does not include the separate intervention investment.
 * This is a display reconciliation, not a new industrial calculation. */
function costReconciliation(a, incident, response){
 if(!a||!response||a.decision_cost==null)return '<div class="cost-note">Selecione uma resposta com resultado calculado para examinar a composição do custo.</div>';
 const operation=Number(response.operating_cost),penalty=Number(response.penalty_total),scenario=Number(response.total_cost);
 const investment=Number(a.investment),decision=Number(a.decision_cost);
 const baseline=Number(incident?.total_cost),saving=Number(a.savings);
 if(![operation,penalty,scenario,investment,decision,baseline,saving].every(Number.isFinite))return '<div class="cost-note">Faltam indicadores calculados para reconciliar os custos desta resposta.</div>';
 const reconciled=Math.abs((operation+penalty)-scenario)<.031&&Math.abs((scenario+investment)-decision)<.031&&Math.abs((baseline-decision)-saving)<.031;
 return `<div class="cost-reconcile-head"><div><span>COMPOSIÇÃO ECONÔMICA DA RESPOSTA</span><strong>${esc(a.action)}</strong></div><span class="cost-status ${reconciled?'ok':'warn'}">${reconciled?'Valores reconciliados':'Conferir valores'}</span></div>
 <div class="cost-math"><div><small>Operação</small><b>${brl(operation)}</b></div><i>+</i><div><small>Penalidades</small><b>${brl(penalty)}</b></div><i>+</i><div><small>Investimento</small><b>${brl(investment)}</b></div><i>=</i><div class="final"><small>Custo da decisão</small><b>${brl(decision)}</b></div></div>
 <div class="cost-foot"><span>Falha sem resposta: <strong>${brl(baseline)}</strong></span><span>Diferença líquida estimada: <strong>${brl(saving)}</strong></span></div>
 <p>Os valores são projeções do modelo. A viabilidade industrial depende de restrições ainda não integralmente verificadas.</p></div>`;
}
function renderCostReconciliation(){
 const a=st.data?.alternatives?.find(x=>x.signature===st.data.selected);
 const html=costReconciliation(a,metricFor('incident'),metricFor('response'));
 if($('cost-reconciliation'))$('cost-reconciliation').innerHTML=html;
 if($('decision-cost-reconciliation'))$('decision-cost-reconciliation').innerHTML=html;
}
function renderMetrics(){
  const incident=metricFor('incident'),response=metricFor('response'),base=metricFor('normal');
  if(!incident)return;
  const ref=st.scene==='normal'?base:st.scene==='response'?response:incident;
  const label=st.scene==='normal'?'Plano original':st.scene==='response'?'Com intervenção':st.scene==='split'?'Cenário A · sem intervenção':'Sem intervenção';
  $('sim-metrics').innerHTML=[
    metrics('Pedidos com atraso',integer(ref?.late_orders),'Cenário: '+label,ref?.late_orders?'warn':'good'),
    metrics('Cumprimento de prazos',h(ref?.sla_pct)+'%',integer(st.data.orders.length)+' pedidos no modelo',ref?.sla_pct>=80?'good':'warn'),
    metrics('Término previsto',h(ref?.makespan_h)+' h','Tempo simulado'),
    metrics('Custo do cenário',brl(ref?.total_cost),'Operação e penalidades · sem investimento')].join('');
  const split=$('compare-scoreboard');
  split.hidden=st.scene!=='split';
  if(st.scene==='split'){
   const x=metricFor('incident')||{},y=metricFor('response')||{};
   const selected=st.data.alternatives?.find(row=>row.signature===st.data.selected);
   split.innerHTML=`<div class="compare-score a"><span>A · SEM INTERVENÇÃO</span><strong>${integer(x.late_orders)} atraso(s) · ${h(x.makespan_h)} h</strong><small>Custo operacional + multas ${brl(x.total_cost)}</small></div><div class="compare-score b"><span>B · COM INTERVENÇÃO</span><strong>${integer(y.late_orders)} atraso(s) · ${h(y.makespan_h)} h</strong><small>Custo de decisão ${brl(selected?.decision_cost)} · investimento ${brl(selected?.investment)} incluso</small></div>`;
  }
  const a=metricFor('incident'),b=metricFor('response');
  $('impact-metrics').innerHTML=[
    metrics('Pedidos com atraso · Sem resposta',integer(a?.late_orders),'Referência do incidente',a?.late_orders?'warn':''),
    metrics('Pedidos com atraso · Resposta',integer(b?.late_orders),'Alternativa selecionada',b?.late_orders?'warn':'good'),
    metrics('Variação de término',a&&b?(h(a.makespan_h-b.makespan_h)+' h'):'—','Redução projetada'),
    metrics('Diferença de custo bruto',a&&b?brl(a.total_cost-b.total_cost):'—','Sem descontar investimentos')].join('');
  renderImpactInterpretation();
  renderIncidentWorkflow();
  renderCostReconciliation();
}


/* Incident workstation: one investigated model and actionable links, not a separate dashboard. */
function renderIncidentWorkflow(){
 const d=st.data,el=$('incident-workflow');if(!d||!el)return;
 const incident=metricFor('incident')||{};
 const selected=d.alternatives?.find(a=>a.signature===d.selected)||null;
 const impacts=selected?.order_impacts||[];
 const exposed=impacts.filter(o=>o.late_before).map(o=>o.id);
 const overdue=Number(incident.late_orders)||0;
 const when=d.spec?.start_h,post=d.spec?.station||'—';
 el.innerHTML=`<div class="incident-workflow-main"><span class="incident-led" aria-hidden="true"></span><div><span class="incident-eyebrow">INCIDENTE EM ANÁLISE · CENÁRIO SIMULADO</span><strong>${esc(post)} · parada de ${h(d.spec?.duration_h)} h</strong><small>Início em ${time(when)} · ${integer(overdue)} pedido(s) com atraso previsto sem intervenção${exposed.length?' · '+esc(exposed.slice(0,3).join(', ')):''}</small></div></div><div class="incident-workflow-actions"><button type="button" data-incident-go="scene">Localizar no mapa</button><button type="button" data-incident-go="orders">Examinar pedidos</button><button type="button" data-incident-go="compare" class="incident-workflow-cta">Comparar respostas →</button></div>`;
}

/* Choose an informative comparison instant from REAL event-driven states.
 * Scores are solely for navigation, never for cost or industrial recommendations. */
function informativeComparisonTime(){
 const a=replayFor('incident'),b=replayFor('response');
 if(!a||!b)return Math.max(0,Number(st.data?.spec?.start_h)||0);
 const start=Math.max(0,Number(st.data?.spec?.start_h)||0);
 const finish=Math.max(start,horizon());
 let best=start,bestScore=0;
 const step=Math.max(.045,(finish-start)/230);
 for(let t=start;t<=finish;t+=step){
  let score=0;
  for(let i=0;i<a.stations.length;i++){
   const j=b.stations.findIndex(x=>x.id===a.stations[i].id);if(j<0)continue;
   const x=machineState(a,i,t),y=machineState(b,j,t);
   if(x.down!==y.down)score+=9;
   if((x.processing>0)!==(y.processing>0))score+=4;
   score+=Math.min(6,Math.abs(x.queued-y.queued)*.2);
   score+=Math.min(3,Math.abs(x.paused-y.paused));
  }
  if(score>bestScore+.001){bestScore=score;best=t;}
 }
 return bestScore>0?Math.min(finish,best):start;
}
function _binaryCount(arr,t){let l=0,r=arr.length;while(l<r){const m=(l+r)>>1;if(arr[m]<=t)l=m+1;else r=m;}return l;}
const replayIndexes=new WeakMap();
function intervalIndex(entries,start,end){
 const sorted=entries.slice().sort((a,b)=>a.op[start]-b.op[start]||a.order-b.order);
 const starts=[],maxEnds=[];let max=-Infinity;
 for(const entry of sorted){starts.push(entry.op[start]);max=Math.max(max,entry.op[end]);maxEnds.push(max);}
 return {sorted,starts,maxEnds,end};
}
function intervalsAt(index,t){
 const found=[];
 for(let i=_binaryCount(index.starts,t)-1;i>=0&&index.maxEnds[i]>t;i--){
  const entry=index.sorted[i];if(entry.op[index.end]>t)found.push(entry);
 }
 return found.sort((a,b)=>a.order-b.order).map(x=>x.op);
}
function replayIndex(payload){
 let index=replayIndexes.get(payload);if(index)return index;
 const groups=payload.stations.map(()=>[]),events=[];
 (payload.operations||[]).forEach((op,order)=>{
  if(groups[op[0]])groups[op[0]].push({op,order});
  const station=payload.stations[Number(op[0])]?.id||'POSTO';
  for(const [field,kind] of [[2,'Início'],[3,'Conclusão']])events.push({t:Number(op[field]),kind,station,order:String(op[4]||'—'),unit:String(op[5]||'')});
 });
 if(payload.outage){const o=payload.outage;
  events.push({t:Number(o.start),kind:'Parada',station:o.station,order:'—',unit:''},
              {t:Number(o.end),kind:'Fim da parada',station:o.station,order:'—',unit:''});
 }
 events.sort((a,b)=>a.t-b.t||a.kind.localeCompare(b.kind,'pt-BR'));
 index={stations:groups.map(g=>({active:intervalIndex(g,2,3),waiting:intervalIndex(g,1,2)})),events,eventTimes:events.map(e=>e.t)};
 replayIndexes.set(payload,index);return index;
}
function recentReplayEvents(payload,t){
 const index=replayIndex(payload),end=_binaryCount(index.eventTimes,t+1e-9);
 return index.events.slice(Math.max(0,end-6),end).reverse();
}
function machineState(p,idx,t){
  const s=p.stations[idx]; const a=_binaryCount(s.arrivals,t),b=_binaryCount(s.starts,t),c=_binaryCount(s.ends,t);
  let workers=s.workers,machines=s.machines;
  for(const change of s.changes||[]){if(change.time<=t){workers=change.workers_after;machines=change.machines_after}}
  const outage=p.outage && p.outage.station===s.id && t>=p.outage.start && t<p.outage.end;
  const index=replayIndex(p).stations[idx];
  const ops=intervalsAt(index.active,t);
  const live=ops.filter(op=>((op[8]||[[op[2],op[3]]]).some(seg=>seg[0]<=t&&t<seg[1])));
  const waiting=intervalsAt(index.waiting,t);
  const reduced=p.details_omitted===true;
  const processing=reduced&&s.processing_starts&&s.processing_ends?
    Math.max(0,_binaryCount(s.processing_starts,t)-_binaryCount(s.processing_ends,t)):live.length;
  return {id:s.id,name:s.name,queued:Math.max(0,a-b),active:Math.max(0,b-c),processing,
    paused:reduced?Math.max(0,b-c-processing):ops.length-live.length,finished:c,down:!!outage,workers,machines,
    queue:waiting.map(op=>`${op[4]} · ${op[5]}`),working:live.map(op=>`${op[4]} · ${op[5]}`),
    operations:ops,raw:s};
}
const positions = n => {
  if(n<=3)return Array.from({length:n},(_,i)=>({x:(i+.5)*1200/n,y:275}));
  if(n===4)return [{x:230,y:190},{x:610,y:170},{x:980,y:190},{x:610,y:420}];
  if(n===5)return [{x:200,y:190},{x:600,y:168},{x:1000,y:190},{x:410,y:416},{x:838,y:420}];
  const rows=Math.ceil(n/4);const pts=[];
  for(let r=0;r<rows;r++){const count=Math.min(4,n-r*4);for(let c=0;c<count;c++)pts.push({x:(c+.5)*1200/count,y:(r+.5)*560/rows});}
  return pts;
};
function equipment(name,active){
 const nameUpper=name.toUpperCase(),running=active?'':' paused';
 const monitor='<rect x="44" y="-23" width="25" height="23" rx="2" fill="#0C262E" stroke="#85A9A8"/><path d="M48-13h17M48-8h11" stroke="#73B1A6" stroke-width="2"/>';
 if(/CORTE|LASER/.test(nameUpper))return `<g><path d="M-75 45 L-96 28 V-40 H49 L75-23 V45 Z" fill="#5D7779" stroke="#ABC1B9"/><path d="M49-40 75-23V45H49Z" fill="#294850"/><rect x="-80" y="-33" width="122" height="67" fill="#15313A" stroke="#7C9A9C"/><path d="M-70-20H31M-70-7H31M-70 6H31M-70 19H31" stroke="#325660"/><rect x="-53" y="-19" width="67" height="38" fill="#31535C" stroke="#77A29C"/><path d="M-42 14L-21-11H-1" stroke="#CFDDD3" fill="none"/><g class="machine-spindle${running}"><rect x="-16" y="-39" width="12" height="53" fill="#ACBDB3"/><path d="M-10 14v13" stroke="#FFAB72" stroke-width="2"/></g><path d="M-90 47H77" stroke="#31494C" stroke-width="11"/>${monitor}</g>`;
 if(/CNC|USIN/.test(nameUpper))return `<g><path d="M-79-58H61L83-38V56H-79Z" fill="#819494" stroke="#CFD9C7"/><path d="M61-58 83-38V56H61Z" fill="#324F54"/><rect x="-70" y="-49" width="107" height="87" fill="#24424A" stroke="#A8C4BD"/><rect x="-61" y="-43" width="65" height="73" fill="#0B2933" stroke="#7B9999"/><path d="M-52 18H-3" stroke="#9AB7B1" stroke-width="8"/><rect x="-35" y="8" width="28" height="10" fill="#D7DFD2"/><g class="machine-spindle${running}"><path d="M-26-38v36" stroke="#D7E2D5" stroke-width="7"/><path d="M-26-2v8" stroke="#FFB482" stroke-width="3"/></g><path d="M18-42v72" stroke="#87A6A5" stroke-width="2"/><rect x="43" y="-41" width="14" height="44" fill="#14343C"/><circle cx="50" cy="-30" r="3.1" fill="#83C4A9"/><circle cx="50" cy="-19" r="3.1" fill="#FFAC79"/><path d="M-77 56H78" stroke="#243E45" stroke-width="12"/></g>`;
 if(/SOLDA|ROBO/.test(nameUpper))return `<g><path d="M-90 35 60 35 77 53-71 53Z" fill="#6A8586"/><path d="M-77 54V66M66 54V66" stroke="#314F53" stroke-width="8"/><rect x="-15" y="22" width="63" height="15" fill="#29454A"/><path d="M-42 30 -31-16 2-35 31 3" fill="none" stroke="#AFC5B9" stroke-width="16" stroke-linejoin="round"/><circle cx="-31" cy="-16" r="11" fill="#526D72" stroke="#DBE3D8"/><circle cx="2" cy="-35" r="10" fill="#6F8987" stroke="#D8E4DA"/><path class="machine-spindle${running}" d="M31 3 44 14" stroke="#FFBD86" stroke-width="5"/><path class="machine-spark${running}" d="M45 19l12-6m-12 6 6 11m-6-11-11 8" stroke="#FFC18D" stroke-width="2.3"/><rect x="-55" y="31" width="30" height="9" fill="#3C5D61"/><rect x="7" y="9" width="40" height="12" fill="#D7E1D3"/></g>`;
 if(/PINT|CURA/.test(nameUpper))return `<g><path d="M-87-45H63L81-27V57H-87Z" fill="#627E7D" stroke="#CDDBD1"/><path d="M63-45 81-27V57H63Z" fill="#31545D"/><rect x="-78" y="-36" width="132" height="78" fill="#17313A" stroke="#9CB8B1"/><rect x="-39" y="8" width="53" height="22" rx="3" fill="#A1BBAE"/><path d="M-64-36v37M-20-36V1M25-36V1" stroke="#D2DCD0" stroke-width="3"/><g class="machine-activity${running}" stroke="#98C7B9" stroke-dasharray="2 5"><path d="M-64 1-76 25M-64 1-48 25M-20 1-34 25M-20 1-7 25M25 1 11 25M25 1 40 25"/></g><path d="M-89 55H73" stroke="#314D52" stroke-width="11"/></g>`;
 return `<g><path d="M-93 0H73L87 18H-93Z" fill="#879A96" stroke="#CAD9CE"/><rect x="-91" y="18" width="174" height="18" fill="#435F64"/><path d="M-77 36v30M65 36v30" stroke="#546D70" stroke-width="10"/><path d="M-85 8H77" stroke="#D2DED4" stroke-width="2"/><rect x="-29" y="-28" width="62" height="29" rx="3" fill="#ADC5B9" stroke="#E2E9DC"/><g class="machine-activity${running}"><path d="M-4-29v-22h28M24-51v22" stroke="#A7C3BA" stroke-width="7"/><rect x="20" y="-33" width="13" height="10" fill="#E1E8DC"/></g><path d="M-55 8v14M-34 8v14M-13 8v14M8 8v14M29 8v14M50 8v14" stroke="#B9CFC2" stroke-width="3"/></g>`;
}
function buildFactory(svg,p,suffix){
 if(!p){svg.innerHTML='';return;}
 svg.setAttribute('viewBox','0 0 1200 600');
 const pos=positions(p.stations.length), selectedOrder=st.data.orders.find(o=>o.id===st.order);
 const selectedRoute=(selectedOrder?.route||[]).map(r=>r[0]);
 const edges=(p.edges||[]).map(([ia,ib],idx)=>{const a=pos[ia],b=pos[ib];if(!a||!b)return '';
 const curve=`M ${a.x} ${a.y} C ${a.x+(b.x-a.x)*.15} ${a.y+(b.y-a.y)*.75}, ${b.x-(b.x-a.x)*.15} ${b.y-(b.y-a.y)*.75}, ${b.x} ${b.y}`;
 const chosen=selectedRoute.some((s,i)=>i>0&&s===p.stations[ib].id&&selectedRoute[i-1]===p.stations[ia].id);
 return `<path id="${suffix}-edge-${idx}" class="flow-stroke ${chosen?'flow-selected':''}" d="${curve}"/><circle cx="${a.x}" cy="${a.y}" r="3" fill="#7DBAB0"/>`;}).join('');
 const grid=`<defs><pattern id="g-${suffix}" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#5C8287" stroke-width=".65" opacity=".34"/></pattern><linearGradient id="surface-${suffix}" x1="0" x2=".7" y1="0" y2="1"><stop offset="0" stop-color="#25424A"/><stop offset="1" stop-color="#142B34"/></linearGradient></defs>`;
 const floor=`<g transform="translate(0 17) skewY(-2)"><rect x="-40" y="50" width="1280" height="550" fill="url(#g-${suffix})" opacity=".35"/></g>
 <path d="M22 540H1178M40 563H1160" stroke="#40666E" stroke-width="1" opacity=".7"/>
 <path d="M28 66v-18h18M1172 66v-18h-18M28 524v18h18M1172 524v18h-18" stroke="#63878D" stroke-width="2" opacity=".55" fill="none"/>
 <text x="38" y="566" class="factory-label">LAYOUT LÓGICO · EQUIPAMENTOS E FILAS</text>
 <text x="1160" y="566" text-anchor="end" class="factory-label">TEMPOS DEFINIDOS PELO SIMULADOR</text>`;
 const equipmentSvg=p.stations.map((s,i)=>{
  const {x,y}=pos[i];const working=true;
  return `<g class="station-group" data-station="${esc(s.id)}" id="${suffix}-station-${i}" transform="translate(${x} ${y})" tabindex="0" role="button" aria-label="Inspecionar ${esc(s.name)}">
   <rect class="selection-halo" x="-155" y="-116" width="310" height="224" rx="8"/>
   <path class="workcell-shadow" d="M-140 66 -105 93 120 93 147 68 117 53 -109 53Z"/>
   <path class="workcell-deck" d="M-140 52 -108 74 114 74 140 52 109 37 -108 37Z"/>
   <path class="workcell-edge" d="M-140 52 -108 74 114 74 140 52 V67 L114 91 H-108 L-140 67 Z"/>
   <path class="workcell-safety" d="M-119 62H110"/>
   <rect class="station-base" x="-140" y="-113" width="280" height="214" rx="4"/>
   <path class="station-face" d="M-127 -73 H127"/>
   <path class="machine-operating-glow" d="M-87 32 Q0 63 88 32" stroke-width="3" fill="none"/>
   <text x="-122" y="-88" class="station-name">${esc(s.id)}</text><text x="122" y="-88" text-anchor="end" class="station-status" data-k="status">—</text>
   <circle class="state-light" cx="-124" cy="-65" r="4.6"/><text x="-112" y="-61" class="machine-telemetry">POSTO DE PRODUÇÃO</text>
   <g class="station-machine" transform="translate(0 -5) scale(1.10)">${equipment(s.id,working)}</g>
   <g class="workcell-activity" aria-hidden="true"><path d="M-98 40L-76 48H80L101 40" fill="none" stroke-width="1.8"/><circle cx="101" cy="40" r="3.8"/></g>
   <text x="-122" y="52" class="station-caption station-description">${esc(s.name.length>30?s.name.slice(0,29)+'…':s.name)}</text>
   <rect x="-122" y="61" width="244" height="5" class="station-track"/>
   <rect x="-122" y="61" width="0" height="5" class="processing-bar" data-k="load"/>
   <text x="-122" y="85" class="station-caption" data-k="queue">Fila · 0</text><text x="122" y="85" text-anchor="end" class="station-caption" data-k="workers">0 oper.</text>
   <g data-k="queue-units"></g>
   <g class="station-job-line"><text x="-120" y="-47" data-k="job">—</text><text x="120" y="-47" text-anchor="end" data-k="progress">—</text></g>
   <g class="station-outage-badge" aria-hidden="true"><rect x="-133" y="-114" width="266" height="21" rx="3"/><text x="0" y="-99" text-anchor="middle">PARADA SIMULADA · POSTO INDISPONÍVEL</text></g>
   </g>`;
 }).join('');
 svg.innerHTML=`${grid}${floor}<g opacity=".66">${edges}</g>${equipmentSvg}`;
 svg.querySelectorAll('.station-group').forEach(g=>{
  const sid=g.dataset.station;
  g.addEventListener('click',()=>{st.station=sid;st.focus=false;st.lastInspectorPaint=0;updateScene();renderStationInspector()});
  g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();st.station=sid;updateScene();renderStationInspector()}});
 });
}
function operationDisplay(ops,t){
 const live=(ops||[]).find(op => (op[8] || [[op[2],op[3]]]).some(seg=>seg[0]<=t&&t<seg[1]));
 if(!live)return null;
 const started=Number(live[2]),finished=Number(live[3]);
 return {id:String(live[4]||'—'),step:String(live[5]||''),
   elapsed:Math.max(0,t-started),duration:Math.max(0,finished-started),
   fraction:Math.max(0,Math.min(1,(t-started)/Math.max(.0001,finished-started)))};
}
/* Risk emphasis uses per-order predicted delays from the selected DES alternative.
 * It does NOT infer late orders solely from queue length or elapsed time. */
function delayedOrderIds(scene){
 const a=st.data?.alternatives?.find(x=>x.signature===st.data.selected);
 if(!a||scene==='normal')return new Set();
 const key=scene==='response'?'late_after':'late_before';
 return new Set((a.order_impacts||[]).filter(row=>row[key]).map(row=>String(row.id)));
}
function frameStation(svg,p,t,drawQueue=true){
 if(!p||!svg.firstChild)return;
 p.stations.forEach((s,i)=>{
  const obj=machineState(p,i,t);const g=svg.querySelector(`#${svg.id}-station-${i}`);if(!g)return;
  g.classList.toggle('down',obj.down);g.classList.toggle('selected',obj.id===st.station);g.classList.toggle('is-processing',obj.processing>0);
  g.dataset.currentOperation=obj.working?.[0]||'';
  g.classList.toggle('has-queue',obj.queued>0);
  g.dataset.state=obj.down?'down':obj.processing?'processing':obj.paused?'paused':'idle';
  g.classList.toggle('is-paused',obj.paused>0&&!obj.down);
  g.querySelectorAll('.machine-activity,.machine-spindle,.machine-spark').forEach(item=>item.classList.toggle('paused',!obj.processing));
  const status=obj.down?'PARADO':obj.processing?`${obj.processing} ATIVO${obj.processing>1?'S':''}`:obj.paused?'SUSPENSO':'DISPONÍVEL';
  g.querySelector('[data-k=status]').textContent=status;
  g.querySelector('[data-k=queue]').textContent=`Fila · ${obj.queued}`;
  g.querySelector('[data-k=workers]').textContent=`${obj.workers} oper.`;
  g.setAttribute('aria-label',`${obj.name}: ${status.toLowerCase()}, ${obj.queued} unidades em fila, ${obj.processing} processando. Selecionar para inspecionar.`);
  g.querySelector('[data-k=load]').setAttribute('width', String(Math.min(232,232*obj.processing/Math.max(1,obj.machines))));
  g.querySelector('[data-k=load]').classList.toggle('down',obj.down);
  const job=operationDisplay(obj.operations,t);
  g.querySelector('[data-k=job]').textContent=job?job.id:(obj.down?'CICLO INTERROMPIDO':obj.paused?'OPERAÇÃO SUSPENSA':(p.details_omitted?'DETALHES POR PEÇA OMITIDOS':'SEM OPERAÇÃO ATIVA'));
  g.querySelector('[data-k=progress]').textContent=job?`${Math.round(job.elapsed*60)} min decorridos`:' ';
  g.querySelector('[data-k=load]').setAttribute('width',String(job?244*job.fraction:Math.min(244,244*obj.processing/Math.max(1,obj.machines))));
  if(drawQueue){
    const signature=st.scene+'|'+svg.id+'|'+obj.queue.join('|');
    if(g.dataset.queueSignature!==signature){
      g.dataset.queueSignature=signature;
      const branch=st.scene==='split'?(svg.id==='factory-b'?'response':'incident'):st.scene;
      const delayed=delayedOrderIds(branch);
      const chunk=obj.queue.slice(0,8).map((label,j)=>{
        const oid=String(label).split(' · ')[0];const risk=delayed.has(oid);
        return `<rect x="${-122+j*20}" y="97" width="15" height="10" rx="1.5" class="queue-unit ${risk?'at-risk':''}"><title>${esc(label)}${risk?' · pedido com atraso previsto':''}</title></rect>`;
      }).join('');
      g.querySelector('[data-k=queue-units]').innerHTML=chunk+(obj.queue.length>8?`<text x="50" y="105" class="queue-extra">+${obj.queue.length-8}</text>`:'');
    }
  }
 });
}
function presentationCompareEnabled(){return st.presentation&&st.presentationStep===4&&st.scene==='split'}
function comparisonStationStatus(replay,stationId){
 const idx=replay?.stations?.findIndex(s=>s.id===stationId)??-1;
 if(idx<0)return {text:'Posto não encontrado',label:'—',queued:null,processing:null,down:false};
 const state=machineState(replay,idx,st.t);
 const label=state.down?'PARADO':state.processing>0?'PROCESSANDO':state.paused>0?'OPERAÇÃO PAUSADA':'SEM PROCESSAMENTO';
 return {text:`${integer(state.processing)} operação(ões) ativa(s) · ${integer(state.queued)} un. em fila`,label,queued:state.queued,processing:state.processing,down:state.down};
}
function renderPresentationCompare(){
 const panel=$('presentation-compare-insights'),button=$('presentation-compare-view');
 const show=presentationCompareEnabled();
 panel.hidden=!show;button.hidden=!show;
 if(!show)return;
 button.textContent=st.presentationOverview?'Ampliar posto afetado':'Ver layout completo';
 button.setAttribute('aria-pressed',String(!st.presentationOverview));
 const station=st.data?.spec?.station||st.station;
 const a=comparisonStationStatus(replayFor('incident'),station),b=comparisonStationStatus(replayFor('response'),station);
 const chip=(letter,name,x)=>`<div class="presentation-live-scenario ${x.down?'live-down':'live-available'}"><span>${letter} · ${esc(name)} · ${esc(station)}</span><strong>${esc(x.label)}</strong><small>${esc(x.text)}</small></div>`;
 const selected=st.data?.alternatives?.find(row=>row.signature===st.data.selected);
 panel.innerHTML=chip('A','SEM INTERVENÇÃO',a)+`<div class="presentation-live-time"><span>MESMO INSTANTE</span><strong>${time(st.t)}</strong><small>Estados extraídos dos replays</small></div>`+chip('B',selected?.action==='Não intervir'?'NÃO INTERVIR':'COM RESPOSTA',b);
}
function presentationCompareViewBox(replay){
 if(!presentationCompareEnabled()||st.presentationOverview||!replay)return '0 0 1200 600';
 const idx=replay.stations?.findIndex(x=>x.id===(st.data?.spec?.station||st.station))??-1;
 const position=positions(replay.stations?.length||0)[Math.max(0,idx)]||{x:600,y:300};
 const w=530,h=370;
 return `${Math.max(0,Math.min(1200-w,position.x-w/2))} ${Math.max(0,Math.min(600-h,position.y-h/2))} ${w} ${h}`;
}
function renderScene(force=false){
 const d=st.data;if(!d)return;
 st.t=Math.min(st.t,horizon());
 if(force)st.lastInspectorPaint=0;
 const mode=st.scene, a=mode==='split'?'incident':mode,
   b='response',p1=replayFor(a)||replayFor('incident')||replayFor('normal'),p2=replayFor(b);
 const key=`${d.run_id}:${mode}:${st.order}:${Object.keys(d.stations).join(',')}`;
 if(force||key!==st.stageKey){
  st.stageKey=key;
  buildFactory($('factory-a'),p1,'factory-a');
  buildFactory($('factory-b'),mode==='split'?p2:null,'factory-b');
 }
 $('scene-b').style.display=mode==='split'?'block':'none';
 $('factory-viewport').dataset.scene=mode;
 const comparePanels=presentationCompareEnabled();
 $('factory-viewport').dataset.presentationCompare=String(comparePanels);
 $('factory-viewport').dataset.compareOverview=String(!!st.presentationOverview);
 $('split-divider').hidden=mode!=='split'||comparePanels;
 $('split-divider').style.left=`${st.wipe}%`;
 $('scene-a').style.clipPath=mode==='split'&&!comparePanels?`inset(0 ${100-st.wipe}% 0 0)`:'none';
 $('scene-b').style.clipPath=mode==='split'&&!comparePanels?`inset(0 0 0 ${st.wipe}%)`:'none';
 $('factory-a').setAttribute('viewBox',comparePanels?presentationCompareViewBox(p1):'0 0 1200 600');
 $('factory-b').setAttribute('viewBox',comparePanels?presentationCompareViewBox(p2):'0 0 1200 600');
 $('chip-left').textContent=mode==='split'?'A · SEM INTERVENÇÃO':mode==='normal'?'PLANO ORIGINAL':mode==='response'?'COM INTERVENÇÃO':'SEM INTERVENÇÃO';
 $('chip-right').hidden=mode!=='split';$('chip-right').textContent=st.data?.alternatives?.find(row=>row.signature===st.data.selected)?.action==='Não intervir'?'B · NÃO INTERVIR':'B · COM RESPOSTA';$('split-control').hidden=mode!=='split'||comparePanels;
 $$('#scene-tabs button').forEach(button=>{button.classList.toggle('active',button.dataset.scene===mode);
    button.disabled=(button.dataset.scene==='response'||button.dataset.scene==='split')&&!replayFor('response');
    button.title=button.disabled?'Selecione uma alternativa com simulação disponível.':'';
 });
 $('stage-subtitle').textContent=mode==='split'?(st.presentation?`Mesmo instante ${time(st.t)} · cenários A e B`:'Mesmo instante · dois cenários'):'Fluxo lógico por posto';
 const point=(p1?.stations||[]).findIndex(x=>x.id===st.station);
 const center=positions(p1?.stations.length||0)[Math.max(0,point)]||{x:600,y:300};
 const origin=st.focus&&!comparePanels?`${center.x/12}% ${center.y/6}%`:'50% 50%';
 for(const svg of [$('factory-a'),$('factory-b')]){
  svg.style.transformOrigin=origin;
  svg.style.transform=comparePanels?'none':`scale(${st.focus?Math.max(1.38,st.zoom):st.zoom})`;
 }
 $('factory-viewport').classList.toggle('focus-active',st.focus);
 renderEventBookmarks();
 updateScene();renderMetrics();renderSchedule(true);
 renderPresentationGuide();renderPresentationCompare();
}

function renderEventBookmarks(){
 if(!st.data)return;
 const current=currentReplay();if(!current)return;
 const marks=[{label:'Início',t:0,type:'start'}];
 if(current.outage)marks.push({label:'Parada · '+current.outage.station,t:current.outage.start,type:'incident'});
 const response=replayFor('response');
 if(response?.intervention){
  const iv=response.intervention;
  if(Number.isFinite(Number(iv.requested_h)))marks.push({label:'Resposta solicitada',t:Number(iv.requested_h),type:'action'});
  if(iv.effective_h!=null && Number(iv.effective_h)!==Number(iv.requested_h))marks.push({label:'Resposta efetiva',t:Number(iv.effective_h),type:'action'});
 }
 if(st.scene==='split'){
  if(current.outage)marks.push({label:'Fim da parada · A',t:current.outage.end,type:'incident'});
  if(response?.outage)marks.push({label:'Fim da parada · B',t:response.outage.end,type:'action'});
 } else if(current.outage)marks.push({label:'Fim da parada',t:current.outage.end,type:'action'});
 marks.push({label:'Fim da programação',t:horizon(),type:'finish'});
 marks.sort((a,b)=>a.t-b.t);
 $('event-bookmarks').innerHTML=marks.map(m=>`<button type="button" class="event-mark ${m.type}" data-seek="${m.t}" title="Ir para ${time(m.t)}"><span class="event-mark-dot"></span>${esc(m.label)} <strong>${time(m.t)}</strong></button>`).join('');
 $$('#event-bookmarks [data-seek]').forEach(b=>b.addEventListener('click',()=>{
  st.playing=false;st.t=Math.min(horizon(),Math.max(0,Number(b.dataset.seek)));updateScene();
 }));
}
/* Navigation from recorded operation boundaries, not fabricated physical movement.
 * Only completed/started operations already known to the DES are listed. */
function renderEventLog(){
 const payload=currentReplay(), el=$('event-log');if(!payload||!el)return;
 if(payload.details_omitted){el.dataset.signature='';el.innerHTML='<p class="event-log-empty">Modo reduzido: eventos por peça omitidos. Estados agregados e linha do tempo preservados.</p>';return;}
 const recent=recentReplayEvents(payload,st.t);
 const signature=st.scene+'|'+recent.map(x=>[x.t,x.kind,x.station,x.order,x.unit].join(':')).join('|');
 if(el.dataset.signature===signature)return;
 el.dataset.signature=signature;
 el.innerHTML=recent.length?recent.map(e=>`<button class="event-log-item" type="button" data-event-time="${e.t}" data-event-station="${esc(e.station)}"><time>${time(e.t)}</time><strong>${esc(e.kind)} · ${esc(e.station)}</strong><span>${e.order==='—'?'Parada registrada no cenário':esc(e.order+' · unidade '+e.unit)}</span></button>`).join(''):
 '<p class="event-log-empty">Ainda não há operações iniciadas neste instante simulado. Avance a linha do tempo.</p>';
}
function updateScene(){
 const p1=replayFor(st.scene==='split'?'incident':st.scene)||replayFor('incident')||replayFor('normal'),p2=replayFor('response');
 if(!p1)return;
 frameStation($('factory-a'),p1,st.t);
 if(st.scene==='split')frameStation($('factory-b'),p2,st.t);
 $('factory-viewport').dataset.playing=String(st.playing);
 // Connections indicate process precedence, not material transit: do not animate them as real transport.
 const operational=p1.stations.map((station,index)=>machineState(p1,index,st.t));
 const activeStations=operational.filter(x=>x.processing>0).length;
 const stoppedStations=operational.filter(x=>x.down).length;
 const inQueue=operational.reduce((acc,x)=>acc+x.queued,0);
 $('stage-activity-summary').textContent=`${activeStations} posto(s) processando · ${inQueue} em fila${stoppedStations?' · '+stoppedStations+' parado(s)':''} · fluxo lógico, sem transporte modelado`;
 $('factory-viewport').dataset.incident=String(stoppedStations>0);
 const alert=$('stage-event-alert');
 const iv=st.scene==='response'?p1.intervention:null;
 const effective=iv?.effective_h == null?null:Number(iv.effective_h);
 if(st.scene==='split'){alert.hidden=true;alert.textContent='';}
 else if(effective!==null&&Number.isFinite(effective)&&st.t>=effective&&st.t<effective+.2){
  alert.hidden=false;alert.dataset.tone='response';
  alert.textContent=`RESPOSTA MODELADA · efetiva em ${time(effective)}${stoppedStations?' · posto ainda parado':''}`;
 }
 else if(stoppedStations){alert.hidden=false;alert.dataset.tone='incident';alert.textContent=`FALHA MODELADA · ${p1.outage?.station||'POSTO'} · início ${time(p1.outage?.start)}`;}
 else {alert.hidden=true;alert.textContent='';}

 $('stage-time-label').textContent=time(st.t);
 $('stage-mode-indicator').textContent=st.playing?'REPRODUÇÃO ATIVA':'REPRODUÇÃO PAUSADA';
 $('operational-hud').innerHTML=`<div><span>POSTOS EM ATIVIDADE</span><strong>${integer(activeStations)}</strong></div><div><span>UNIDADES EM FILA</span><strong>${integer(inQueue)}</strong></div><div class="${stoppedStations?'hud-alert':''}"><span>POSTOS PARADOS</span><strong>${integer(stoppedStations)}</strong></div>`;
 $('clock-label').textContent=time(st.t);
 $('horizon-label').textContent=time(horizon());
 $('time-conversion').textContent=`${String(st.speed).replace('.',',')}× = ${h(10*st.speed)} min simulados/s · ${st.pauseOnEvent?'pausa em eventos ativa':'reprodução contínua'}`;
 $('timeline-range').value=String(Math.round(10000*st.t/horizon()));
 const outage=p1.outage;
 const status=outage&&st.t>=outage.start&&st.t<outage.end?'PARADA / '+outage.station:
  st.scene==='split'?'COMPARAÇÃO TEMPORAL':'PRODUÇÃO SIMULADA';
 $('event-status').textContent=status;
 $('timeline-marks').innerHTML=`<span>0 h</span><span class="incident-mark">Falha ${time(st.data.spec.start_h)}</span><span>Fim ${time(horizon())}</span>`;
 $('play-button').innerHTML=icon(st.playing?'pause':'play');
 const now=performance.now();
 // Avoid replacing interactive inspector buttons at every animation tick.
 // Replay geometry keeps its higher refresh rate; contextual panels update less often.
 if(!st.playing || now-st.lastInspectorPaint>340){
  renderStationInspector();renderOrders();renderEventLog();st.lastInspectorPaint=now;
 }
 updateScheduleCursor();
 if(presentationCompareEnabled())renderPresentationCompare();
}
function renderOrders(){
 const d=st.data,p=currentReplay();if(!p)return;
 $('orders-row').innerHTML=d.orders.map(o=>{
  const done=_binaryCount(p.order_completions[o.id]||[],st.t);
  const progress=100*done/Math.max(1,Number(o.quantidade));
  const predicted=st.scene==='response'?metricFor('response'):metricFor('incident');
  const orderRow=(st.scene==='response'?st.data.alternatives.find(a=>a.signature===st.data.selected)?.order_impacts||[]:[]).find(x=>x.id===o.id);
  const impact=(st.data.alternatives.find(a=>a.signature===st.data.selected)?.order_impacts||[]).find(x=>x.id===o.id);
  const recovered=st.scene==='split'&&impact?.late_before&&!impact?.late_after;
  const late=(st.scene==='split'||st.scene==='incident'?impact?.late_before:st.scene==='response'?impact?.late_after:false)||false;
  const response=st.scene==='split'?replayFor('response'):null;
  const doneB=response?_binaryCount(response.order_completions[o.id]||[],st.t):0;
  const progressB=100*doneB/Math.max(1,Number(o.quantidade));
  const comparison=st.scene==='split'&&response?
    `<div class="orders-compare-labels"><span>A · ${done}</span><span>B · ${doneB}</span></div><div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,progress)}%"></div></div><div class="bar-track bar-response"><div class="bar-fill" style="width:${Math.min(100,progressB)}%"></div></div>`:
    `<small>${done}/${integer(o.quantidade)} unidades</small><div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,progress)}%"></div></div>`;
  return `<div class="order-mini ${st.order===o.id?'selected':''} ${late?'delayed':''}" data-order="${esc(o.id)}" tabindex="0" role="button"><div class="order-mini-title"><strong>${esc(o.id)}</strong>${recovered?'<span class="order-recovered">Prazo recuperado</span>':''}</div><small>${esc(o.produto)}</small>${comparison}</div>`;
 }).join('');
 $$('.order-mini').forEach(el=>{el.onclick=()=>{st.order=st.order===el.dataset.order?null:el.dataset.order;renderScene(true)};el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.click()}}});
}
function renderStationInspector(){
 const d=st.data;if(!d)return;
 const p=currentReplay(),idx=p?.stations.findIndex(s=>s.id===st.station)??-1;
 const raw=d.stations[st.station]||{};
 if(idx<0)return;
 const s=machineState(p,idx,st.t);
 const pB=st.scene==='split'?replayFor('response'):null;
 const indexB=pB?.stations?.findIndex(x=>x.id===st.station)??-1;
 const sb=pB&&indexB>=0?machineState(pB,indexB,st.t):null;
 const status=s.down?'Parado':s.processing?'Em processamento':s.paused?'Operação suspensa':'Disponível';
 $('inspect-status').textContent=status.toUpperCase();$('inspect-status').classList.toggle('alert',s.down);
 $('station-inspector').innerHTML=`<h2>${esc(s.id)}</h2><p>${esc(raw.nome||s.name)}</p><div class="inspect-status-line"><span class="status-pill ${s.down?'down':''}"></span>${esc(status)}</div>
 <div class="inspect-machine-preview ${s.down?'is-down':s.processing&&st.playing?'is-running':'is-idle'}" aria-label="Representação ilustrativa do equipamento ${esc(s.id)}">
  <div class="inspect-machine-head"><span>VISUALIZAÇÃO DO POSTO</span><span>${esc(s.id)}</span></div>
  <svg viewBox="-130 -95 260 190" role="img" aria-label="Equipamento ${esc(s.id)}">
    <defs><linearGradient id="inspector-floor" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#304B53"/><stop offset="1" stop-color="#172D36"/></linearGradient></defs>
    <path d="M-117 54L-72 82H76L115 55L73 36H-69Z" fill="url(#inspector-floor)" stroke="#789197" stroke-width="1"/>
    <g transform="translate(0 -2) scale(1.0)">${equipment(s.id,true)}</g>
    <circle cx="94" cy="-69" r="5" fill="${s.down?'#FF681B':s.processing?'#7BCFB0':'#718E95'}"/>
  </svg><div class="inspect-machine-footer">${s.down?'PARADA REGISTRADA':s.processing?'EM PROCESSAMENTO':'SEM PROCESSAMENTO NO INSTANTE'}</div>
</div>
<div class="inspector-quick-actions"><button type="button" class="inspect-focus-button" data-inspect-focus="1">${st.focus?'Exibir planta inteira':'Focar neste posto'}</button><button type="button" class="inspect-inspect-button" data-open-schedule="1">Ver programação</button><button type="button" class="inspect-inspect-button" data-inspect-murphy="1">Consultar Murphy</button></div>
 ${sb?`<div class="inspect-compare"><div class="inspect-compare-head">COMPARAÇÃO NO INSTANTE ${time(st.t)}</div><div class="inspect-compare-columns"><div><small>SEM RESPOSTA · A</small><strong>${s.down?'Parado':s.processing?'Processando':'Disponível'}</strong><span>Fila: ${integer(s.queued)} un.</span></div><div><small>COM RESPOSTA · B</small><strong>${sb.down?'Parado':sb.processing?'Processando':'Disponível'}</strong><span>Fila: ${integer(sb.queued)} un.</span></div></div><p>Diferença de fila (B − A): <b>${sb.queued-s.queued>0?'+':''}${integer(sb.queued-s.queued)}</b> unidade(s).</p></div>`:''}
 <div class="inspect-data"><div class="inspect-row"><span>Máquinas</span><b>${integer(s.machines)}</b></div><div class="inspect-row"><span>Operadores</span><b>${integer(s.workers)}</b></div><div class="inspect-row"><span>Fila no instante</span><b>${integer(s.queued)}</b></div><div class="inspect-row"><span>Processando</span><b>${integer(s.processing)}</b></div><div class="inspect-row"><span>Suspensas</span><b>${integer(s.paused)}</b></div></div><p class="inspector-foot">${s.working.length?esc(s.working.slice(0,4).join(' · ')):(p.details_omitted?'Modo reduzido: estados agregados exatos; identificação por peça omitida.':'Nenhuma operação em processamento neste instante.')}</p>
 ${s.queue.length?`<div class="inspection-queue"><strong>Unidades aguardando</strong><div>${s.queue.slice(0,5).map(label=>{
   const orderId=String(label).split(' · ')[0];const usable=d.orders.some(o=>o.id===orderId);
   return `<button type="button" class="queue-pick" ${usable?`data-inspect-order="${esc(orderId)}"`:'disabled'} title="${esc(label)}">${esc(label)}</button>`;
 }).join('')}</div></div>`:''}`;
 if(st.order){
  const order=d.orders.find(o=>o.id===st.order);
  const trace=(p.operations||[]).filter(op=>op[4]===st.order).sort((a,b)=>a[2]-b[2]).slice(0,12);
  const completion=p.order_completions?.[st.order]||[];
  const due=Number(order?.prazo_h);
  const finalTime=completion.length?Math.max(...completion):null;
  const delay=finalTime!==null&&Number.isFinite(due)?Math.max(0,finalTime-due):null;
  const orderDetail=`<section class="order-trace" aria-label="Rastreio da ordem selecionada"><h3>Ordem ${esc(st.order)}</h3>
    <p>Roteiro registrado na simulação. Selecione uma etapa na programação para localizar a operação.</p>
    <div class="inspect-data"><div class="inspect-row"><span>Prazo</span><b>${time(due)}</b></div>
    <div class="inspect-row"><span>Conclusão prevista</span><b>${finalTime===null?'Não concluída':time(finalTime)}</b></div>
    <div class="inspect-row"><span>Atraso previsto</span><b>${delay===null?'Em cálculo':h(delay)+' h'}</b></div></div>
    <div class="order-trace-lines">${trace.map(op=>{const wait=Math.max(0,Number(op[2])-Number(op[1]));const station=p.stations[op[0]];return `<button type="button" class="order-trace-line trace-interactive" data-trace-time="${Number(op[2])}" data-trace-station="${esc(station?.id||'')}"><strong>${esc(station?.name||station?.id||'Posto')}</strong><span>Início ${time(op[2])} · Fim ${time(op[3])}</span><small>Espera registrada ${h(wait*60)} min · selecionar na linha do tempo ↗</small></button>`;}).join('')||'<p>Sem operações registradas para esta ordem.</p>'}</div></section>`;
  $('station-inspector').insertAdjacentHTML('beforeend',orderDetail+`<button type="button" class="explain-order-button" id="explain-order-button">Por que este resultado? ${icon('arrow')}</button>`);
  $('explain-order-button').onclick=()=>openHelp('order');
 }
 const sp=d.spec||{};
 $('incident-inspector').innerHTML=`<h3>${esc(sp.station||'—')}</h3><p>Parada programada de ${h(sp.duration_h)} h, iniciada em ${time(sp.start_h)}.</p><div class="inspect-data"><div class="inspect-row"><span>Resposta após</span><b>${h(d.delay_h)} h</b></div><div class="inspect-row"><span>Pedidos atrasados</span><b>${integer(metricFor('incident')?.late_orders)}</b></div></div><p class="inspector-foot">Hipóteses sintéticas: nenhuma atuação física. Restrições de habilitação não verificadas automaticamente.</p>`;
}
/* Analytical dashboards — read-only views of the same DES experiment.
   No forecast, utilization, risk or cost is calculated from visual animation. */
const dashUI = {tab:'operacao',scenario:'incident',data:null,robustness:null,audit:null,riskMinutes:30,loading:false};
const dashVal = (value,digits=1)=>Number.isFinite(Number(value))&&value!==null&&value!==undefined?numericText(value,digits):'—';
const dashMoney = value=>value===null||value===undefined?'—':brl(value);
const dashH = value=>value===null||value===undefined?'—':`${dashVal(value,2)} h`;
const dashPct = value=>value===null||value===undefined?'—':`${dashVal(value,1)}%`;
const dashScenarioLabels={normal:'Plano original',incident:'Sem intervenção',response:'Com intervenção'};
function dashScenario(){return dashUI.data?.scenarios?.[dashUI.scenario]||null;}
function dashScenarioSelectOptions(){
 const keys=Object.keys(dashUI.data?.scenarios||{});
 $('dash-scenario').innerHTML=keys.map(k=>`<option value="${esc(k)}">${esc(dashScenarioLabels[k]||k)}</option>`).join('');
 if(!keys.includes(dashUI.scenario))dashUI.scenario=keys.includes('incident')?'incident':keys[0];
 $('dash-scenario').value=dashUI.scenario;
}
async function openDashboards(force=false){
 if(!st.data)return;
 if(dashUI.loading)return;
 if(!force && dashUI.data?.analysis_signature===st.data.analysis_signature && dashUI.data?.project_id===st.data.active_project_id){if(dashUI.tab==='auditoria')loadAudit();else renderDashboards();return;}
 const expected=st.data.analysis_signature;
 dashUI.loading=true;
 $('dash-body').innerHTML='<div class="dash-loading" role="status">Atualizando indicadores do experimento…</div>';
 try{
  const result=await api('/api/dashboards');
  if(expected!==st.data?.analysis_signature || result.analysis_signature!==expected || result.project_id!==st.data?.active_project_id || result.selected!==st.data?.selected)throw Error('O projeto ou a seleção mudou durante a consulta. Atualize os painéis.');
  dashUI.data=result;
  $('dash-project').textContent=st.data.active_project_name||'Projeto principal';
  $('dash-experiment').textContent=`Execução ${result.run_id} · ${Object.keys(st.data.stations).length} postos · ${st.data.orders.length} pedidos`;
  dashScenarioSelectOptions();if(dashUI.tab==='auditoria')await loadAudit(true);else renderDashboards();
 }catch(err){$('dash-body').innerHTML=`<div class="dash-error" role="alert">Não foi possível consultar os painéis: ${esc(err.message||String(err))}. <button class="subtle-button" data-dash-retry>Repetir</button></div>`;}
 finally{dashUI.loading=false;}
}
function dashStat(label,val,foot='',tone=''){
 return `<div class="dash-stat ${tone}"><span>${esc(label)}</span><strong>${esc(val)}</strong><small>${esc(foot)}</small></div>`;
}
function dashScenarioMetrics(scenario){
 const m=scenario?.metrics||{};
 return `<div class="dash-stat-strip">${dashStat('Entregas no prazo',dashPct(m.sla_pct),'Dos pedidos cadastrados',m.sla_pct<80?'dash-warn':'')}${dashStat('Término previsto',dashH(m.makespan_h),'Horário de conclusão')}${dashStat('Pedidos com atraso',integer(m.late_orders),'Em relação aos prazos',m.late_orders>0?'dash-warn':'')}${dashStat('Custo operacional + multas',dashMoney(m.total_cost),'Investimento de intervenção à parte')}</div>`;
}
function dashBar(v,limit=100,type='util'){
 const n=Math.max(0,Math.min(100,Number(v)||0));return `<span class="dash-track ${esc(type)}"><span style="width:${n}%"></span></span>`;
}
function dashUtilization(){
 const rows=dashScenario()?.stations||[];
 const widest=Math.max(1,...rows.map(r=>Number(r['Fila máx.'])||0));
 const name=dashScenarioLabels[dashUI.scenario];
 return `${dashScenarioMetrics(dashScenario())}<div class="dash-panel-layout"><article class="dash-panel dash-primary-panel"><header><div><h2>Utilização e filas por posto</h2><p>${esc(name)} · valores calculados pelo motor</p></div><span class="dash-hint">Selecionar posto para inspecionar</span></header>
  <div class="dash-scroll"><table class="dash-table dash-stations"><thead><tr><th>Posto</th><th>Utilização de máquina</th><th>Equipe</th><th>Fila máx.</th><th>Espera média</th></tr></thead><tbody>${rows.map(r=>{
   const id=r['Posto'];const vm=r['Utilização máquina (%)'],vw=r['Utilização mão de obra (%)'],queue=r['Fila máx.'];
   return `<tr><td><button class="dash-table-link" data-dash-station="${esc(id)}"><strong>${esc(id)}</strong><small>${esc(r['Nome'])}</small></button></td><td><div class="dash-bar-cell">${dashBar(vm)}<span>${dashPct(vm)}</span></div></td><td><div class="dash-bar-cell">${dashBar(vw)}<span>${dashPct(vw)}</span></div></td><td><div class="dash-bar-cell">${dashBar(100*(Number(queue)||0)/widest,100,'queue')}<span>${integer(queue)}</span></div></td><td>${dashVal(r['Espera média (min)'])} min</td></tr>`;
  }).join('')}</tbody></table></div></article>
  <aside class="dash-panel dash-side-panel"><header><div><h2>Investigação operacional</h2><p>Do indicador à ocorrência</p></div></header><div class="dash-insight"><span class="dash-insight-label">Incidente configurado</span><strong>${esc(dashUI.data.incident.station||'—')}</strong><p>Início: ${dashH(dashUI.data.incident.start_h)} · duração: ${dashH(dashUI.data.incident.duration_h)}</p></div><div class="dash-actions"><button class="dash-cta" data-dash-go="simulacao">Inspecionar na fábrica →</button><button data-dash-advanced="diagnostic">Abrir diagnóstico de gargalos →</button><button data-dash-go="modelo">Revisar recursos do modelo →</button></div><p class="dash-footnote">Utilização elevada não comprova gargalo isoladamente. Considere espera, fila, restrições e ritmo de chegada.</p></aside></div>`;
}
function dashCostBar(key,scenario){
 const a=Number(scenario?.metrics?.operating_cost)||0,b=Number(scenario?.metrics?.penalty_total)||0;
 const max=Math.max(1,...Object.values(dashUI.data.scenarios).map(s=>Number(s.metrics?.total_cost)||0));
 const w=100*(a+b)/max;const ap=(a+b)>0?100*a/(a+b):100;
 return `<div class="dash-cost-row"><div class="dash-cost-top"><strong>${esc(dashScenarioLabels[key]||key)}</strong><span>${dashMoney(a+b)}</span></div><div class="dash-cost-track" title="Operação: ${dashMoney(a)}; multas: ${dashMoney(b)}"><span class="dash-cost-scaled" style="width:${w}%"><span style="width:${ap}%" class="dash-cost-operating"></span><span style="width:${100-ap}%" class="dash-cost-penalty"></span></span></div><div class="dash-cost-details"><span>Operação ${dashMoney(a)}</span><span>Multas ${dashMoney(b)}</span></div></div>`;
}
function dashOrders(){
 const sc=dashScenario();if(!sc)return '';
 const rows=sc.orders||[];
 return `<article class="dash-panel"><header><div><h2>Carteira de pedidos</h2><p>Prazo, conclusão e folga por pedido · alerta com folga ≤ ${dashUI.riskMinutes} minutos</p></div><button class="dash-text-button" data-dash-go="analise">Comparar por pedido →</button></header><div class="dash-scroll"><table class="dash-table"><thead><tr><th>Pedido</th><th>Prazo</th><th>Conclusão</th><th>Folga</th><th>Multa estimada</th><th>Situação</th></tr></thead><tbody>${rows.map(o=>`<tr><td><button class="dash-table-link" data-dash-order="${esc(o['OP'])}"><strong>${esc(o['OP'])}</strong><small>${esc(o['Cliente']||'')}</small></button></td><td>${dashH(o['Prazo (h)'])}</td><td>${dashH(o['Conclusão (h)'])}</td><td class="${Number(o['Prazo (h)'])<Number(o['Conclusão (h)'])?'dash-negative':''}">${dashH(Number(o['Prazo (h)'])-Number(o['Conclusão (h)']))}</td><td>${dashMoney(o['Multa (R$)'])}</td><td><span class="dash-status ${Number(o['Atraso (h)'])>0?'late':Number(o['Prazo (h)'])-Number(o['Conclusão (h)'])<=dashUI.riskMinutes/60?'risk':'ok'}">${Number(o['Atraso (h)'])>0?'Atraso previsto':Number(o['Prazo (h)'])-Number(o['Conclusão (h)'])<=dashUI.riskMinutes/60?'Folga reduzida':'No prazo'}</span></td></tr>`).join('')}</tbody></table></div></article>`;
}
function dashCostReconciliation(){
 const a=dashUI.data?.selected_action;const incident=dashUI.data?.scenarios?.incident?.metrics;
 const response=dashUI.data?.scenarios?.response?.metrics;
 return `<section class="dash-panel dash-reconciliation">${costReconciliation(a,incident,response)}</section>`;
}
function dashPerformance(){
 const sc=dashScenario();const variants=Object.entries(dashUI.data.scenarios);
 return `${dashScenarioMetrics(sc)}${dashCostReconciliation()}<div class="dash-panel-layout"><article class="dash-panel dash-primary-panel"><header><div><h2>Composição de custos</h2><p>Custos operacionais e multas de atraso, por cenário</p></div></header><div class="dash-cost-chart">${variants.map(([k,v])=>dashCostBar(k,v)).join('')}</div><div class="dash-cost-legend"><span><i class="operating"></i> Operação</span><span><i class="penalty"></i> Penalidades</span></div><p class="dash-footnote">A comparação acima não inclui necessariamente o investimento da intervenção. Consulte a análise de alternativas para custo de decisão.</p></article><aside class="dash-panel dash-side-panel"><header><div><h2>Diferenças de programação</h2><p>Sem intervenção → resposta selecionada</p></div></header>${(()=>{const a=dashUI.data.scenarios.incident?.metrics||{},b=dashUI.data.scenarios.response?.metrics||{};return `<div class="dash-delta"><span>Variação do término</span><strong>${dashH(Number(a.makespan_h)-Number(b.makespan_h))}</strong><small>Positivo indica antecipação prevista</small></div><div class="dash-delta"><span>Pedidos recuperados</span><strong>${Number.isFinite(Number(a.late_orders)-Number(b.late_orders))?integer(Number(a.late_orders)-Number(b.late_orders)):'—'}</strong><small>Diferença entre as projeções</small></div>`})()}<div class="dash-actions"><button data-dash-go="analise" class="dash-cta">Examinar custos da decisão →</button></div></aside></div>${dashOrders()}`;
}
// Independent flags: a non-dominated alternative may still fail its SLA target.
const modeledEligible = a => a?.feasible===true && a?.within_budget===true && a?.meets_sla===true;
function modeledRestrictions(a){
 const fail=[];
 if(a?.feasible!==true)fail.push('viabilidade');
 if(a?.within_budget!==true)fail.push('orçamento');
 if(a?.meets_sla!==true)fail.push('meta de SLA');
 return fail.length ? 'Não atende: '+fail.join(', ') : 'Atende às metas modeladas';
}
function costSlaFrontier(alternatives){
 // Two objectives only: decision cost decreases, SLA increases. The decision
 // record separately reviews cost, makespan and SLA; do not conflate the sets.
 // Exact equivalents remain alternatives; strict dominance uses full precision.
 const candidates=alternatives.filter(a=>modeledEligible(a)&&Number.isFinite(Number(a.decision_cost))&&Number.isFinite(Number(a.sla_pct)));
 return candidates.filter(a=>!candidates.some(b=>
  Number(b.decision_cost)<=Number(a.decision_cost)&&Number(b.sla_pct)>=Number(a.sla_pct)&&
  (Number(b.decision_cost)<Number(a.decision_cost)||Number(b.sla_pct)>Number(a.sla_pct))
 )).sort((a,b)=>Number(a.decision_cost)-Number(b.decision_cost)||Number(b.sla_pct)-Number(a.sla_pct)||String(a.signature).localeCompare(String(b.signature)));
}
function dashScenarios(){
 const scs=dashUI.data.scenarios;
 const options=Object.entries(scs);
 const current=dashUI.data.selected_action;
 return `<article class="dash-panel"><header><div><h2>Comparação dos três cenários</h2><p>Resultados da operação nominal, incidente e intervenção selecionada</p></div><button data-dash-scene="split" class="dash-text-button">Abrir comparação A/B →</button></header><div class="dash-scenario-grid">${options.map(([key,v])=>`<div class="dash-scenario-card ${key==='response'?'response':''}"><span>${esc(dashScenarioLabels[key])}</span><strong>${dashPct(v.metrics?.sla_pct)} <small>entregas no prazo</small></strong><div><span>Término</span><b>${dashH(v.metrics?.makespan_h)}</b></div><div><span>Pedidos atrasados</span><b>${integer(v.metrics?.late_orders)}</b></div><div><span>Operação + multas</span><b>${dashMoney(v.metrics?.total_cost)}</b></div><button data-dash-scene="${esc(key)}">Ver na simulação →</button></div>`).join('')}</div></article><div class="dash-panel-layout"><article class="dash-panel dash-primary-panel"><header><div><h2>Alternativas calculadas</h2><p>${dashUI.data.alternatives.length} respostas enumeradas · seleção atual destacada</p></div></header><div class="dash-scroll"><table class="dash-table"><thead><tr><th>Alternativa</th><th>Entregas</th><th>Término</th><th>Custo da decisão</th><th>Condição no modelo</th></tr></thead><tbody>${dashUI.data.alternatives.map(a=>`<tr class="${a.signature===dashUI.data.selected?'is-selected':''}"><td><button class="dash-table-link" data-dash-select="${esc(a.signature)}"><strong>${esc(a.action)}</strong></button></td><td>${dashPct(a.sla_pct)}</td><td>${dashH(a.makespan_h)}</td><td>${dashMoney(a.decision_cost)}</td><td><span class="dash-status ${modeledEligible(a)?'ok':'late'}">${esc(modeledRestrictions(a))}</span></td></tr>`).join('')}</tbody></table></div></article><aside class="dash-panel dash-side-panel"><header><div><h2>Resposta selecionada</h2><p>Projeção baseada nas premissas cadastradas</p></div></header><div class="dash-insight"><strong>${esc(current?.action||'Nenhuma resposta selecionada')}</strong><p>${esc(current?.rationale||'Consulte a análise para avaliar a intervenção.')}</p></div><div class="dash-delta"><span>Investimento declarado</span><strong>${dashMoney(current?.investment)}</strong></div><div class="dash-actions"><button class="dash-cta" data-dash-go="decisoes">Revisar a decisão →</button></div><p class="dash-footnote">A viabilidade física pode depender de habilitações, reservas de recursos e capacidades não verificadas.</p></aside></div>`;
}
function dashTradeoffPlot(){
 const options=dashUI.data.alternatives.filter(a=>Number.isFinite(Number(a.decision_cost))&&Number.isFinite(Number(a.sla_pct)));
 if(!options.length)return '<div class="empty-state">Nenhuma alternativa quantitativa disponível.</div>';
 const width=920,height=320,left=84,right=38,top=27,bottom=59;
 const raw=options.map(x=>Number(x.decision_cost));const low=Math.min(...raw),high=Math.max(...raw);
 const min=Math.max(0,low-(high-low)*.08),max=high+Math.max(1,(high-low)*.08);
 const x=v=>left+(Number(v)-min)/Math.max(1,max-min)*(width-left-right);
 const y=v=>top+(100-Number(v))/100*(height-top-bottom);
 const grid=[0,25,50,75,100].map(v=>`<line x1="${left}" y1="${y(v)}" x2="${width-right}" y2="${y(v)}" class="dash-svg-grid"/><text x="${left-13}" y="${y(v)+4}" text-anchor="end" class="dash-svg-label">${v}%</text>`).join('');
 const ticks=Array.from({length:5},(_,i)=>min+(max-min)*i/4).map(v=>`<text x="${x(v)}" y="${height-28}" text-anchor="middle" class="dash-svg-label">${dashMoney(v)}</text>`).join('');
 // Only alternatives satisfying modeled criteria participate in this descriptive non-dominated set.
 // This is NOT a guarantee of global optimality or real industrial feasibility.
 const modeled=options.filter(modeledEligible);
 const frontier=costSlaFrontier(options);
 const pareto=new Set(frontier.map(a=>a.signature));
 const line=frontier.length>1?`<polyline class="dash-pareto-line" points="${frontier.map(a=>`${x(a.decision_cost)},${y(a.sla_pct)}`).join(' ')}"/>`:'';
 const dots=options.map(a=>`<g data-dash-select="${esc(a.signature)}" role="button" tabindex="0" class="dash-chart-option ${a.signature===dashUI.data.selected?'chosen':''} ${pareto.has(a.signature)?'pareto':''}" aria-label="${esc(a.action)}; custo ${dashMoney(a.decision_cost)}; SLA ${dashPct(a.sla_pct)}"><circle cx="${x(a.decision_cost)}" cy="${y(a.sla_pct)}" r="${a.signature===dashUI.data.selected?8.5:pareto.has(a.signature)?7.2:5.9}"/><title>${esc(a.action)} | ${dashMoney(a.decision_cost)} | SLA ${dashPct(a.sla_pct)}${pareto.has(a.signature)?' | não dominada na amostra':''}</title></g>`).join('');
 return `<svg class="dash-scatter" viewBox="0 0 ${width} ${height}" role="img" aria-label="Alternativas por custo e entregas no prazo. Linha tracejada representa as opções não dominadas do conjunto enumerado.">${grid}${ticks}${line}${dots}<text x="${left}" y="14" class="dash-svg-title">Entregas no prazo (%)</text><text x="${width-right}" y="${height-5}" text-anchor="end" class="dash-svg-title">Custo da decisão (R$)</text></svg><div class="dash-plot-note"><strong>${frontier.length} alternativa(s) não dominada(s)</strong> em custo e SLA entre ${modeled.length} que atendem à viabilidade, orçamento e SLA. Empates nas duas métricas são equivalentes. A linha indica apenas o conjunto enumerado; não comprova viabilidade física nem ótimo global.</div>`;
}
function dashOptimize(){
 const arr=dashUI.data.alternatives;
 const good=arr.filter(modeledEligible).slice().sort((a,b)=>(Number(a.decision_cost)||Infinity)-(Number(b.decision_cost)||Infinity));
 const selected=dashUI.data.selected_action;
 return `<div class="dash-panel-layout"><article class="dash-panel dash-primary-panel"><header><div><h2>Alternativas: custo × cumprimento de prazos</h2><p>Selecione um ponto para recalcular a resposta exibida no projeto</p></div></header>${dashTradeoffPlot()}<p class="dash-footnote">Os pontos representam alternativas enumeradas, não uma fronteira ótima global. Habilitações e buffers podem alterar a viabilidade real.</p></article><aside class="dash-panel dash-side-panel"><header><div><h2>Busca e sensibilidade</h2><p>Ferramentas do motor original</p></div></header><div class="dash-stat-mini"><span>Alternativas enumeradas</span><strong>${integer(arr.length)}</strong></div><div class="dash-stat-mini"><span>Atendem critérios modelados</span><strong>${integer(good.length)}</strong></div><div class="dash-stat-mini"><span>Menor custo entre essas respostas</span><strong>${dashMoney(good[0]?.decision_cost)}</strong></div><div class="dash-actions"><button class="dash-cta" data-dash-lab="goal">Executar Goal Seek →</button><button data-dash-advanced="sensitivity">Sensibilidade de recursos →</button><button data-dash-advanced="opportunities">Opportunity Engine →</button><button data-dash-go="modelo">Ajustar capacidade →</button></div></aside></div><article class="dash-panel"><header><div><h2>Resposta atual</h2><p>Premissas, resultado e próximos passos</p></div></header><div class="dash-response-line"><strong>${esc(selected?.action||'Nenhuma selecionada')}</strong><span>Investimento ${dashMoney(selected?.investment)}</span><span>Custo total de decisão ${dashMoney(selected?.decision_cost)}</span><button class="dash-text-button" data-dash-go="decisoes">Abrir evidências e registro →</button></div></article>`;
}
function dashRobust(){
 const r=dashUI.robustness||analysisHistory.list('advanced','uncertainty')[0]?.result;
 if(!r){return analysisHistoryMarkup('advanced','uncertainty','data-dash-history')+`<div class="dash-panel dash-robust-empty"><div class="dash-robust-icon">∿</div><h2>Resultados sob variações do modelo</h2><p>Execute 12 simulações com sementes diferentes sobre o incidente selecionado. A análise não altera o projeto nem a resposta escolhida.</p><button class="dash-cta" data-dash-robust-run>Executar Monte Carlo (12 execuções)</button><p class="dash-footnote">As sementes são uma análise de sensibilidade interna. Não representam frequências reais de falhas industriais nem um intervalo de confiança calibrado com dados de fábrica.</p></div><div class="dash-actions-inline"><button data-dash-lab="stress" class="subtle-button">Abrir Stress Lab</button><button data-dash-advanced="demand" class="subtle-button">Limite de demanda</button></div>`;}
 const rows=r.rows||[],m=r.summary?.makespan||{},sla=r.summary?.sla||{};
 const slas=rows.filter(x=>x.feasible!==false&&x.sla!==null&&x.sla!==undefined).map(x=>Number(x.sla)).filter(Number.isFinite);
 const constantSla=slas.length>1&&slas.every(v=>Math.abs(v-slas[0])<.005);
 const consistencyNote=constantSla?`<div class="dash-robust-constant"><strong>SLA sem variação entre as ${integer(slas.length)} execuções (${h(slas[0])}%).</strong> O experimento não demonstrou sensibilidade desse indicador às perturbações consideradas; isso não significa risco de atraso nulo nem modelo calibrado.</div>`:'';

 return analysisBanner(r)+analysisHistoryMarkup('advanced','uncertainty','data-dash-history')+`<div class="dash-stat-strip">${dashStat('Execuções',integer(rows.length),'Sementes sintéticas')}${dashStat('Makespan médio',dashH(m.mean),'Não é prazo garantido')}${dashStat('P10 / P90',`${dashVal(m.p10,2)} / ${dashVal(m.p90,2)} h`,'Faixa descritiva')}${dashStat('SLA médio',dashPct(sla.mean),'Sobre as execuções')}</div><article class="dash-panel"><header><div><h2>Dispersão do término previsto</h2><p>Uma coluna por execução · a posição vertical não representa probabilidade</p></div><button data-dash-robust-run class="dash-text-button">Executar novamente</button></header>${window.AMCharts.render(r,'dash')}${consistencyNote}<div class="dash-robust-note">Gargalo mais frequente: <strong>${esc(r.dominant_bottleneck||'—')}</strong>. As execuções podem compartilhar a mesma estrutura e não caracterizam incerteza industrial real.</div></article><div class="dash-actions-inline"><button data-dash-lab="stress" class="subtle-button">Stress Lab →</button><button data-dash-advanced="demand" class="subtle-button">Limite de demanda →</button></div>`;
}
/* Evidence read from the same DES run. Honest about unmodeled industrial dimensions. */
async function loadAudit(force=false){
 const data=st.data;if(!data)return;
 if(!force&&dashUI.audit?.analysis_signature===data.analysis_signature&&dashUI.audit?.run_id===data.run_id&&dashUI.audit?.project_id===data.active_project_id&&dashUI.audit?.selected_signature===data.selected){renderDashboards();return;}
 $('dash-body').innerHTML='<div class="dash-loading" role="status">Conferindo evidências do experimento…</div>';
 try{
  const result=await api('/api/technical-audit');
  if(result.analysis_signature!==st.data?.analysis_signature||result.run_id!==st.data?.run_id||result.project_id!==st.data?.active_project_id||result.selected_signature!==st.data?.selected){throw Error('A análise mudou. Atualize o painel para consultar o experimento ativo.');}
  dashUI.audit=result;renderDashboards();
 }catch(e){$('dash-body').innerHTML=`<div class="dash-error" role="alert">Não foi possível abrir a auditoria técnica: ${esc(e.message)} <button class="subtle-button" data-audit-refresh>Repetir</button></div>`;}
}
function auditSlackStatus(slack,threshold){return slack<0?['Atrasado','late']:slack<=threshold?['Folga reduzida','risk']:['No prazo','ok'];}
function dashAudit(){
 const a=dashUI.audit;
 if(!a)return '<div class="dash-loading">Consultando evidências calculadas…</div>';
 const orders=a.orders[dashUI.scenario]||[];
 const threshold=dashUI.riskMinutes/60;
 const near=orders.filter(o=>o.slack_h>=0&&o.slack_h<=threshold).length;
 const late=orders.filter(o=>o.slack_h<0).length;
 const diag=a.diagnostic,m=a.maintenance;
 const auditRows=orders.map(o=>{const [label,tone]=auditSlackStatus(o.slack_h,threshold);return `<tr><td><button class="dash-table-link" data-dash-order="${esc(o.id)}"><strong>${esc(o.id)}</strong><small>${esc(o.client||'')}</small></button></td><td>${dashH(o.due_h)}</td><td>${dashH(o.finish_h)}</td><td class="${o.slack_h<0?'dash-negative':''}">${dashH(o.slack_h)}</td><td><span class="dash-status ${tone}">${label}</span></td></tr>`}).join('');
 return `<div class="audit-heading"><div><span>AUDITORIA DE ENGENHARIA / EXPERIMENTO ${esc(a.run_id)}</span><h2>Rastreabilidade e limites da decisão</h2><p>Verificações determinísticas e informações que o modelo ainda não representa.</p></div><button class="subtle-button" data-audit-refresh>Revalidar</button></div>
 <div class="dash-stat-strip">${dashStat('Pedidos atrasados',integer(late),'Folga negativa')}${dashStat('Entregas com pouca folga',integer(near),'Dentro do limite configurado')}${dashStat('Indicador de gargalo',String(diag.scored_bottleneck||'—'),'Pontuação do motor')}${dashStat('Posto de maior espera',String(diag.highest_mean_wait||'—'),dashVal(diag.highest_mean_wait_min,1)+' min')}</div>
 <article class="dash-panel"><header><div><h2>Folga por pedido · ${esc(dashScenarioLabels[dashUI.scenario])}</h2><p>Folga = prazo cadastrado − conclusão calculada; não equivale à probabilidade de atraso.</p></div><label class="audit-threshold">Limite de alerta <select id="dash-risk-limit">${[15,30,60,120].map(v=>`<option value="${v}" ${dashUI.riskMinutes===v?'selected':''}>${v} min</option>`).join('')}</select></label></header><div class="dash-scroll"><table class="dash-table"><thead><tr><th>Pedido</th><th>Prazo</th><th>Conclusão</th><th>Folga</th><th>Classificação</th></tr></thead><tbody>${auditRows||'<tr><td colspan="5">Sem resultados por pedido.</td></tr>'}</tbody></table></div></article>
 <div class="audit-grid"><article class="dash-panel"><header><div><h2>Diagnóstico da capacidade</h2><p>Três evidências diferentes do mesmo cenário</p></div></header><div class="audit-evidence"><div><span>Índice composto do motor</span><strong>${esc(diag.scored_bottleneck||'—')}</strong></div><div><span>Maior espera média</span><strong>${esc(diag.highest_mean_wait||'—')}</strong><small>${dashVal(diag.highest_mean_wait_min,1)} min</small></div><div><span>Maior fila registrada</span><strong>${esc(diag.largest_queue_station||'—')}</strong><small>${integer(diag.largest_queue_units)} un.</small></div></div><p class="audit-foot">${esc(diag.methodology)} ${esc(diag.validation)}</p><div class="audit-actions"><button data-dash-advanced="sensitivity">Testar sensibilidade de recursos →</button><button data-dash-go="simulacao">Inspecionar fábrica →</button></div></article>
 <article class="dash-panel"><header><div><h2>Confiabilidade dos custos</h2><p>Identidades contábeis verificadas automaticamente</p></div></header><div class="audit-checks">${a.costs.checks.map(x=>`<div class="${x.ok?'passed':'failed'}"><span>${x.ok?'✓':'!'}</span>${esc(x.description)}</div>`).join('')}</div><p class="audit-foot">${esc(a.costs.basis)}</p></article></div>
 <div class="audit-grid"><article class="dash-panel"><header><div><h2>Manutenção e disponibilidade</h2><p>Limites do experimento de parada</p></div></header><div class="audit-evidence"><div><span>Posto da parada</span><strong>${esc(m.station||'—')}</strong></div><div><span>Início programado</span><strong>${dashH(m.start_h)}</strong></div><div><span>Duração programada</span><strong>${dashH(m.scheduled_duration_h)}</strong></div></div><p class="audit-foot">Sem histórico de falhas e reparos: MTBF e MTTR estatísticos não são estimáveis. Redução do reparo expressa é uma hipótese, não comprovação de recursos de manutenção disponíveis.</p></article>
 <article class="dash-panel"><header><div><h2>Qualidade e restrições</h2><p>Não confundir indicadores ausentes com desempenho perfeito</p></div></header><div class="audit-limits"><p><b>Qualidade:</b> refugo, retrabalho, inspeção e primeira passagem não estão modelados. Não é possível informar OEE/FPY verificado.</p><p><b>Restrição industrial:</b> habilitações individuais, buffers finitos, setups dependentes da sequência e recursos físicos de manutenção ainda exigem validação.</p><p><b>Origem:</b> dados sintéticos; simulação local, sem instrumentação física.</p></div><div class="audit-actions"><button data-dash-go="decisoes">Registrar ressalvas na decisão →</button></div></article></div>`;
}
function renderDashboards(){
 if(!dashUI.data)return;
 if(dashUI.data.analysis_signature!==st.data?.analysis_signature||dashUI.data.project_id!==st.data?.active_project_id){$('dash-body').innerHTML='<p role="status">Painel de outra configuração. <button data-dash-retry>Atualizar indicadores</button></p>';return;}
 $$('#dash-tabs button').forEach(btn=>{const active=btn.dataset.dashTab===dashUI.tab;btn.classList.toggle('active',active);btn.setAttribute('aria-selected',String(active));});
 $('dash-scenario').value=dashUI.scenario;
 const body={operacao:dashUtilization,desempenho:dashPerformance,cenarios:dashScenarios,otimizacao:dashOptimize,robustez:dashRobust,auditoria:dashAudit};
 $('dash-body').innerHTML=body[dashUI.tab]();
}
async function dashRunRobustness(){
 const id=analysisHistory.begin();
 try{
  const result=await api('/api/advanced','POST',{mode:'uncertainty'});
  analysisHistory.add(result,'advanced',id);
  const visible=analysisHistory.find(dashUI.robustness);
  if(!visible||id>visible.id)dashUI.robustness=result;
  if(st.view==='paineis'&&dashUI.data)renderDashboards();
  notify('Monte Carlo preservado com projeto e configuração de origem.');
 }catch(e){notify(e.message||'Erro no experimento.',true);if(st.view==='paineis'&&dashUI.data)renderDashboards();}
}
function dashBindEvents(){
 $$('#dash-tabs button').forEach(b=>b.onclick=()=>{dashUI.tab=b.dataset.dashTab;if(dashUI.tab==='auditoria')loadAudit();else renderDashboards();});
 $('dash-scenario').onchange=e=>{dashUI.scenario=e.target.value;if(dashUI.tab==='auditoria')loadAudit();else renderDashboards();};
 $('dash-refresh').onclick=()=>openDashboards(true);
 $('dash-open-simulation').onclick=()=>navigate('simulacao');
 $('dash-open-analysis').onclick=()=>navigate('analise');
 $('dash-report').onclick=generateReport;
 $('dash-body').addEventListener('click',async e=>{
  const node=e.target.closest('[data-dash-station],[data-dash-order],[data-dash-go],[data-dash-scene],[data-dash-select],[data-dash-lab],[data-dash-advanced],[data-dash-robust-run],[data-dash-history],[data-dash-retry],[data-audit-refresh]');if(!node)return;
  if(node.hasAttribute('data-dash-history')){dashUI.robustness=analysisHistory.entries.find(x=>x.id===Number(node.dataset.dashHistory))?.result;renderDashboards();return;}
  if(node.hasAttribute('data-dash-retry'))return openDashboards(true);
  if(node.hasAttribute('data-audit-refresh'))return loadAudit(true);
  if(node.hasAttribute('data-dash-robust-run'))return dashRunRobustness();
  if(node.dataset.dashStation){st.station=node.dataset.dashStation;st.focus=true;st.t=Number(st.data.spec.start_h)||0;navigate('simulacao');return;}
  if(node.dataset.dashOrder){st.order=node.dataset.dashOrder;st.focus=true;navigate('simulacao');return;}
  if(node.dataset.dashGo){navigate(node.dataset.dashGo);return;}
  if(node.dataset.dashScene){st.scene=node.dataset.dashScene;st.t=Number(st.data.spec.start_h)||0;navigate('simulacao');return;}
  if(node.dataset.dashSelect){await selectAlternative(node.dataset.dashSelect);if(st.data){dashUI.data=null;await openDashboards(true);}return;}
  if(node.dataset.dashLab){st.lab=node.dataset.dashLab;st.labIntent=(st.labIntent||0)+1;navigate('laboratorio');return;}
  if(node.dataset.dashAdvanced){st.advanced=node.dataset.dashAdvanced;st.advancedIntent=(st.advancedIntent||0)+1;navigate('avancadas');return;}
 });
 $('dash-body').addEventListener('change',e=>{if(e.target.id==='dash-risk-limit'){dashUI.riskMinutes=Number(e.target.value)||30;renderDashboards();}});
 $('dash-body').addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('[data-dash-select]')){e.preventDefault();e.target.click();}});
}

function renderAnalysis(){
 const d=st.data;if(!d)return;
 $('alternative-count').textContent=`${d.alternatives.length} respostas avaliadas`;
 $('alternatives-table').innerHTML=`<table class="data-table"><thead><tr><th>Intervenção</th><th>Viabilidade</th><th>No prazo</th><th>Conclusão</th><th>Custo total</th><th>Economia líquida</th></tr></thead><tbody>${d.alternatives.map(a=>{
 const chosen=a.signature===d.selected,eligible=a.feasible&&a.within_budget&&a.meets_sla;
 return `<tr class="pickable ${chosen?'selected':''}" data-signature="${esc(a.signature)}"><td>${esc(a.action)}</td><td><span class="tiny-tag ${eligible?'':a.feasible?'caution':'none'}">${eligible?'Atende modelo':a.feasible?'Não atende meta':'Inviável'}</span></td><td>${h(a.sla_pct)}%</td><td>${h(a.makespan_h)} h</td><td>${brl(a.decision_cost)}</td><td class="${a.savings>0?'positive':a.savings<0?'negative':'neutral'}">${brl(a.savings)}</td></tr>`
 }).join('')}</tbody></table>`;
 $$('#alternatives-table tr[data-signature]').forEach(tr=>tr.onclick=()=>selectAlternative(tr.dataset.signature));
 const chosen=d.alternatives.find(a=>a.signature===d.selected) || d.alternatives[0];
 if(!chosen){$('alternative-detail').innerHTML='Nenhuma alternativa disponível.';return}
 const issue=chosen.restriction_reasons?.length?chosen.restriction_reasons.join(' · '):'Competências individuais e capacidade de buffers ainda não têm verificação completa no modelo.';
 $('alternative-detail').innerHTML=`${decisionReviewMarkup()}<h3 class="alt-name">${esc(chosen.action)}</h3><span class="tiny-tag ${chosen.feasible?'':'caution'}">${chosen.feasible?'Simulada':'Não simulável'}</span><p class="alt-description">${esc(chosen.rationale||chosen.verdict_reason||'Resposta enumerada pelo motor.')}</p>
 <div class="alt-metrics"><div><small>Pedidos no prazo</small><strong>${h(chosen.sla_pct)}%</strong></div><div><small>Término previsto</small><strong>${h(chosen.makespan_h)} h</strong></div><div><small>Investimento</small><strong>${brl(chosen.investment)}</strong></div><div><small>Economia líquida</small><strong>${brl(chosen.savings)}</strong></div></div>
 <div class="alt-warning">${esc(issue)}</div><div class="alt-buttons"><button class="primary-button full" id="alt-see-factory">Ver na simulação ${icon('arrow')}</button><button class="subtle-button" id="alt-choose">Registrar esta alternativa</button></div>`;
 $('alt-see-factory').onclick=()=>{st.scene='split';st.t=Number(d.spec.start_h)||0;navigate('simulacao')};
 $('alt-choose').onclick=()=>navigate('decisoes');
 bindReviewButtons($('alternative-detail'));
 renderFrontier();
 $('impact-orders').innerHTML=`<table class="data-table"><thead><tr><th>Pedido</th><th>Prazo</th><th>Sem resposta</th><th>Com resposta</th><th>Condição</th></tr></thead><tbody>${(chosen.order_impacts||[]).map(o=>`<tr><td>${esc(o.id)}</td><td>${h(o.due_h)} h</td><td>${h(o.before_h)} h</td><td>${h(o.after_h)} h</td><td><span class="tiny-tag ${o.late_after?'caution':''}">${o.late_after?'Atraso previsto':'No prazo'}</span></td></tr>`).join('')}</tbody></table>`;
 $('impact-orders').insertAdjacentHTML('beforeend','<button id="explain-impact" class="subtle-button explanation-action">Entender os atrasos e diferenças</button>');
 $('explain-impact').onclick=()=>openHelp('impact');
}

/* Decision frontier: interactive multi-criteria comparison from the actual engine.
   Pareto calculation only ranks the finite enumerated options; it is not a global optimum. */
function renderFrontier(){
 const svg=$('frontier-chart');if(!svg||!st.data)return;
 const points=st.data.alternatives.filter(a=>Number.isFinite(Number(a.decision_cost)) && Number.isFinite(Number(a.sla_pct)));
 if(!points.length){svg.innerHTML='<text x="30" y="100" fill="#647D73">Não há alternativas quantificadas.</text>';return;}
 const W=1120,H=255,L=84,R=35,T=30,B=42;
 const raw=points.map(x=>Number(x.decision_cost)),lo=Math.min(...raw),hi=Math.max(...raw),span=Math.max(1,hi-lo);
 const min=Math.max(0,lo-span*.06),max=hi+span*.06;
 const xx=v=>L+(Number(v)-min)/Math.max(.001,max-min)*(W-L-R);
 const yy=v=>T+(100-Number(v))/100*(H-T-B);
 const frontier=costSlaFrontier(points);
 const grid=[0,25,50,75,100].map(y=>`<line class="frontier-grid" x1="${L}" y1="${yy(y)}" x2="${W-R}" y2="${yy(y)}"/><text class="frontier-axis" x="${L-10}" y="${yy(y)+4}" text-anchor="end">${y}%</text>`).join('');
 const ticks=Array.from({length:5},(_,i)=>min+(max-min)*i/4).map(v=>`<text class="frontier-axis" x="${xx(v)}" y="${H-15}" text-anchor="middle">${brl(v)}</text>`).join('');
 const path=frontier.length>1?`<polyline class="frontier-line" points="${frontier.map(a=>`${xx(a.decision_cost)},${yy(a.sla_pct)}`).join(' ')}"/>`:'';
 const dots=points.map(a=>{
   const selected=a.signature===st.data.selected,viable=modeledEligible(a);
   return `<g class="frontier-point ${selected?'selected':''} ${viable?'viable':'unverified'}" data-signature="${esc(a.signature)}" tabindex="0" role="button" aria-label="Selecionar ${esc(a.action)}"><circle cx="${xx(a.decision_cost)}" cy="${yy(a.sla_pct)}" r="${selected?8:5.8}"/><title>${esc(a.action)} · custo ${brl(a.decision_cost)} · entregas no prazo ${h(a.sla_pct)}% · ${esc(modeledRestrictions(a))}</title></g>`;
 }).join('');
 svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
 svg.innerHTML=`${grid}<text x="${L}" y="15" class="frontier-title">Entregas no prazo (%)</text>${ticks}<text x="${W-R}" y="${H-2}" text-anchor="end" class="frontier-title">Custo simulado com decisão (R$)</text>${path}${dots}`;
 svg.querySelectorAll('.frontier-point').forEach(g=>{
   g.addEventListener('click',()=>selectAlternative(g.dataset.signature));
   g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();g.dispatchEvent(new MouseEvent('click',{bubbles:true}))}});
 });
 $('frontier-description').textContent=`${points.length} alternativas · ${frontier.length} não dominada(s) em custo e SLA entre as que atendem às metas modeladas. Empates nas duas métricas são equivalentes. Habilitações e buffers ainda exigem verificação; não há garantia de ótimo global.`;
}

async function selectAlternative(signature){
 try{const data=await perform(api('/api/select','POST',{signature}),null,true); st.scene='split';renderScene(true)}catch(_e){}
}
function fillParameters(){
 const d=st.data;if(!d)return;
 const current=$('form-station').value;
 $('form-station').innerHTML=Object.keys(d.stations).map(s=>`<option value="${esc(s)}">${esc(s)}</option>`).join('');
 $('form-station').value=d.spec.station;
 const p=d.spec;
 for(const [id,value] of [['form-start',p.start_h],['form-duration',p.duration_h],['form-delay',d.delay_h],
  ['form-budget',p.budget],['form-sla',p.min_sla]])$(id).value=value;
 $('form-objective').value=p.objective;
 $('form-critical').innerHTML=`<option value="">Nenhum</option>`+d.orders.map(o=>`<option value="${esc(o.id)}">${esc(o.id)}</option>`).join('');
 $('form-critical').value=p.critical_order||'';
}
async function calculate(){
 const req={station:$('form-station').value,start_h:Number($('form-start').value),
  duration_h:Number($('form-duration').value),delay_h:Number($('form-delay').value),
  budget:Number($('form-budget').value),min_sla:Number($('form-sla').value),
  objective:$('form-objective').value,critical_order:$('form-critical').value};
 if(req.objective==='critical' && !req.critical_order){notify('Selecione o pedido prioritário.',true);return}
 try{st.playing=false;await perform(api('/api/run','POST',req),'Novas alternativas calculadas.');st.t=Math.min(horizon(),req.start_h);st.scene='split';navigate('analise')}
 catch(_e){}
}
/* Model editing: all inputs are editable; original schemas preserved on commit. */

/* Structured route editor: avoids syntax errors in production order paths. */
let routeEditorIndex=-1,routeEditorSteps=[];
function routeFromModel(raw){
 if(Array.isArray(raw))return raw.map(r=>[String(r[0]||''),Number(r[1])]);
 return String(raw||'').split(';').map(x=>x.trim()).filter(Boolean).map(x=>{const [id,min]=x.split(':');return [String(id||'').trim().toUpperCase(),Number(min)]});
}
function routePreview(raw){return routeFromModel(raw).map(([sid,min])=>`${sid} · ${h(min)} min`).join(' → ')||'Nenhuma operação';}
function renderRouteSteps(){
 const box=$('route-steps'),valid=Object.entries(st.editing.stations);
 box.innerHTML=routeEditorSteps.map(([sid,min],i)=>`<div class="route-step" data-step="${i}"><span class="route-step-num">${i+1}</span><label>Posto<select class="route-step-station" data-step-station="${i}">${valid.map(([id,station])=>`<option value="${esc(id)}" ${id===sid?'selected':''}>${esc(station.nome||id)} (${esc(id)})</option>`).join('')}</select></label><label>Tempo por unidade (min)<input type="number" min="0.01" max="100000" step="any" value="${Number.isFinite(min)?min:0}" data-step-min="${i}"/></label><div class="route-step-actions"><button type="button" data-route-up="${i}" ${i===0?'disabled':''} aria-label="Subir operação ${i+1}">↑</button><button type="button" data-route-down="${i}" ${i===routeEditorSteps.length-1?'disabled':''} aria-label="Descer operação ${i+1}">↓</button><button type="button" data-route-remove="${i}" aria-label="Remover operação ${i+1}">×</button></div></div>`).join('')||'<p class="route-empty">Sem operações. Adicione ao menos uma etapa ao roteiro.</p>';
 box.querySelectorAll('[data-step-station]').forEach(el=>el.onchange=()=>{routeEditorSteps[Number(el.dataset.stepStation)][0]=el.value});
 box.querySelectorAll('[data-step-min]').forEach(el=>el.oninput=()=>{routeEditorSteps[Number(el.dataset.stepMin)][1]=Number(el.value)});
 box.querySelectorAll('[data-route-up],[data-route-down],[data-route-remove]').forEach(el=>el.onclick=()=>{
  const i=Number(el.dataset.routeUp??el.dataset.routeDown??el.dataset.routeRemove);
  if(el.hasAttribute('data-route-remove'))routeEditorSteps.splice(i,1);
  else {const j=i+(el.hasAttribute('data-route-up')?-1:1);[routeEditorSteps[i],routeEditorSteps[j]]=[routeEditorSteps[j],routeEditorSteps[i]];}
  renderRouteSteps();
 });
}
function openRouteEditor(index){
 routeEditorIndex=index;
 const order=st.editing?.orders[index];if(!order)return;
 routeEditorSteps=routeFromModel(order.route);
 $('route-dialog-title').textContent=`Roteiro · ${order.id}`;
 $('route-error').hidden=true;
 renderRouteSteps();$('route-dialog').showModal();
}
function commitRouteEditor(){
 const err=$('route-error');
 if(!routeEditorSteps.length){err.textContent='Inclua pelo menos uma operação.';err.hidden=false;return;}
 for(const [sid,min] of routeEditorSteps){
  if(!st.editing.stations[sid]||!Number.isFinite(min)||min<=0){err.textContent='Selecione postos existentes e tempos maiores que zero.';err.hidden=false;return;}
 }
 st.editing.orders[routeEditorIndex].route=routeEditorSteps.map(([sid,min])=>[sid,min]);
 $('route-dialog').close();renderModel();notify('Roteiro atualizado no editor. Aplique as alterações para recalcular.');
}

function renderModel(){
 const d=st.data;if(!d)return;
 if(!st.editing)st.editing={stations:structuredClone(d.stations),orders:structuredClone(d.orders)};
 const m=st.editing;
 $('count-stations').textContent=Object.keys(m.stations).length;
 $('count-orders').textContent=m.orders.length;
 renderModelWorkload();
 $$('#model-tabs button').forEach(b=>b.classList.toggle('active',b.dataset.modelTab===st.modelTab));
 const body=st.modelTab==='stations'?renderStationsTable(m.stations):renderOrdersTable(m.orders);
 $('model-table').innerHTML=body;
 $$('#model-table input').forEach(inp=>{
  inp.addEventListener('input',()=>{
   const field=inp.dataset.field,idx=inp.dataset.idx;
   const original=st.modelTab==='stations'?m.stations[idx]:m.orders[Number(idx)];
   if(!original)return;
   if(field==='route'){
    original.route=inp.value;renderModelWorkload();return;
   }
   original[field]=inp.dataset.numeric==='1'? Number(inp.value):inp.value;
   renderModelWorkload();
  });
 });
 $$('#model-table button[data-route-edit]').forEach(btn=>btn.onclick=()=>openRouteEditor(Number(btn.dataset.routeEdit)));
 $$('#model-table button[data-remove]').forEach(btn=>btn.onclick=()=>{
  if(st.modelTab==='stations')delete m.stations[btn.dataset.remove];
  else m.orders.splice(Number(btn.dataset.remove),1);
  renderModel();
 });
}
function renderModelWorkload(){
 const el=$('model-workload'),m=st.editing;if(!el||!m)return;
 const limit=st.data?.workload?.limits;if(!limit){el.hidden=true;return;}
 el.hidden=false;
 let units=0,operations=0,valid=true;
 for(const o of m.orders){const q=Number(o.quantidade);let route=o.route;
  if(typeof route==='string')route=route.split(';').map(s=>s.trim()).filter(Boolean);
  if(!Number.isSafeInteger(q)||q<=0||!Array.isArray(route)||!route.length){valid=false;continue;}
  units+=q;operations+=q*route.length;
 }
 const over=valid&&operations>limit.per_scenario;
 el.classList.toggle('workload-over',over);
 const posts=Object.keys(m.stations).length;
 el.innerHTML=`<div><span class="eyebrow">DIMENSÃO DO MODELO</span><strong>${valid?integer(operations):'—'} <small>operações por cenário</small></strong><span>${valid?integer(units):'—'} ${units===1?'unidade':'unidades'} · ${integer(posts)} ${posts===1?'posto':'postos'}</span></div><p role="status">${!valid?'Complete quantidades e roteiros para conferir o volume.':over?`Volume acima do limite de ${integer(limit.per_scenario)} operações por cenário. Reduza quantidades ou etapas antes de aplicar; o projeto salvo permanece preservado.`:`Limites: ${integer(limit.per_scenario)} operações por cenário e ${integer(limit.per_analysis)} por análise. A conferência considera todos os cenários do ensaio antes de simular.`}</p>`;
}
function renderStationsTable(stations){
 const cols=[['nome','Posto','text'],['maquinas','Máquinas','number'],['operadores','Operadores','number'],
  ['operadores_por_maquina','Op./máquina','number'],['eficiencia_operador','Eficiência','number'],
  ['disponibilidade','Disponibilidade','number'],['setup_min','Setup min','number'],
  ['custo_operador_h','Operador R$/h','number'],['custo_maquina_h','Máquina R$/h','number']];
 return `<table class="data-table"><thead><tr><th>ID</th>${cols.map(c=>`<th>${c[1]}</th>`).join('')}<th></th></tr></thead><tbody>${Object.entries(stations).map(([sid,s])=>`<tr><td>${esc(sid)}</td>${cols.map(([key,_,type])=>`<td><input aria-label="${esc(key)} de ${esc(sid)}" data-idx="${esc(sid)}" data-field="${key}" data-numeric="${type==='number'?'1':'0'}" type="${type}" ${type==='number'?'step="any"':''} value="${esc(s[key]??'')}"></td>`).join('')}<td><button class="row-remove" aria-label="Remover ${esc(sid)}" data-remove="${esc(sid)}">×</button></td></tr>`).join('')}</tbody></table>`;
}
function renderOrdersTable(orders){
 const cols=[['id','Pedido','text'],['cliente','Cliente','text'],['produto','Produto','text'],['quantidade','Unidades','number'],['prazo_h','Prazo h','number'],['multa_hora','Multa R$/h','number'],['prioridade','Prioridade','number'],['release_h','Liberação h','number'],['route','Roteiro','text']];
 return `<table class="data-table"><thead><tr>${cols.map(c=>`<th>${c[1]}</th>`).join('')}<th></th></tr></thead><tbody>${orders.map((o,i)=>`<tr>${cols.map(([key,_,type])=>key==='route'?`<td class="route-cell"><button type="button" class="route-edit" data-route-edit="${i}" aria-label="Editar roteiro do pedido ${esc(o.id)}"><span>Editar etapas</span><small>${esc(routePreview(o.route))}</small></button></td>`:`<td><input aria-label="${esc(key)} de ${esc(o.id)}" data-idx="${i}" data-field="${key}" data-numeric="${type==='number'?'1':'0'}" type="${type}" ${type==='number'?'step="any"':''} value="${esc(o[key]??'')}"></td>`).join('')}<td><button class="row-remove" data-remove="${i}" aria-label="Remover pedido">×</button></td></tr>`).join('')}</tbody></table>`;
}
function normalizedModel(){
 const m=structuredClone(st.editing);
 const stations={},orders=[];
 for(const [key,raw] of Object.entries(m.stations)){
  const sid=key.trim().toUpperCase();if(!sid)throw Error('ID do posto não informado.');
  if(stations[sid])throw Error('ID de posto duplicado: '+sid);
  stations[sid]={...raw,maquinas:Number(raw.maquinas),operadores:Number(raw.operadores),
    operadores_por_maquina:Number(raw.operadores_por_maquina),eficiencia_operador:Number(raw.eficiencia_operador),
    disponibilidade:Number(raw.disponibilidade),setup_min:Number(raw.setup_min),
    custo_operador_h:Number(raw.custo_operador_h),custo_maquina_h:Number(raw.custo_maquina_h)};
 }
 for(const raw of m.orders){
  const order={...raw,id:String(raw.id||'').trim().toUpperCase(),quantidade:Number(raw.quantidade),
    prazo_h:Number(raw.prazo_h),multa_hora:Number(raw.multa_hora),prioridade:Number(raw.prioridade),release_h:Number(raw.release_h)||0};
  if(typeof raw.route==='string')order.route=raw.route.split(';').map(s=>s.trim()).filter(Boolean).map(step=>{
   const [id,minutes]=step.split(':');if(!id||!minutes)throw Error('Roteiro inválido em '+order.id);return [id.trim().toUpperCase(),Number(minutes)];
  });
  else order.route=raw.route;
  orders.push(order);
 }
 return {stations,orders};
}
async function saveModel(){
 try{const data=normalizedModel();await perform(api('/api/model','POST',data),'Modelo atualizado. Simulações recalculadas.');st.editing=null;st.t=0;st.scene='incident';navigate('simulacao')}
 catch(e){if(!e.message?.startsWith('Modelo'))notify(e.message,true)}
}
/* Laboratory uses engine results, never invented data. */
const labInfo={duration:['Sensibilidade da parada','Avalia sete durações mantendo o modelo e a semente.','Tempo de parada'],
 dispatch:['Regras de despacho','Compara EDD, SPT e FIFO diante do mesmo incidente.','Custo da operação'],
 robustness:['Robustez da intervenção','Teste pareado da intervenção selecionada em seis sementes sintéticas.','Economia líquida'],
 goal:['Meta de entregas','Filtra as alternativas já simuladas por percentual de pedidos no prazo.','Custo total'],
 stress:['Estresse da carteira','Variação sintética de demanda, paradas e ausências em 16 cenários.','SLA por execução'],
 capacity:['Otimização de capacidade','Busca incrementos discretos de máquinas e operadores para uma meta.','Custo unitário']};
const labGuidance={
 duration:['Avaliar sensibilidade ao tempo de parada.','O motor varia a duração da interrupção e mostra o efeito nos resultados.','O gráfico compara o término previsto em horas; alteração de prazo não prova viabilidade de reparo.'],
 dispatch:['Comparar regras de despacho.','São executadas EDD, SPT e FIFO com o incidente atual.','O menor custo depende dos prazos e das regras representadas.'],
 robustness:['Testar estabilidade da resposta.','As sementes simuladas alteram a variabilidade de processamento.','Compare a dispersão da economia, não apenas a média.'],
 goal:['Verificar metas de entrega.','O motor filtra alternativas que atingem o percentual configurado.','As respostas ainda podem exigir validação operacional.'],
 stress:['Estressar a carteira.','Cenários sintéticos variam recursos, demanda e incidentes.','Resultados não correspondem a frequências observadas na fábrica.'],
 capacity:['Investigar capacidade adicional.','Testa incrementos discretos de recursos sobre o mesmo modelo.','Custos e habilitações precisam de confirmação antes de aplicar.']
};
function labEmptyState(){
 const a=labGuidance[st.lab]||labGuidance.duration;
 return `<div class="helpful-empty"><span>PREPARAÇÃO DO EXPERIMENTO</span><h3>${esc(a[0])}</h3><p>${esc(a[1])}</p><p><strong>Interpretação:</strong> ${esc(a[2])}</p><button type="button" class="subtle-button" data-run-context="lab">Executar ${esc(labInfo[st.lab]?.[0]||'ensaio')}</button></div>`;
}
window.antiMurphyAnalysisSignature=()=>st.data?.analysis_signature;
function labState(entry){return analysisHistory.status(entry?.result).label;}
function renderLabInfo(){
 const info=labInfo[st.lab];
 $('lab-name').textContent=info[0];$('lab-description').textContent=info[1];
 $('goal-label').hidden=!['goal','capacity'].includes(st.lab);$('throughput-label').hidden=st.lab!=='capacity';
 $$('#lab-tabs button').forEach(btn=>btn.classList.toggle('active',btn.dataset.lab===st.lab));
 const entries=analysisHistory.list('lab',st.lab),selected=entries.find(e=>e.id===st.labVisible)||entries[0],node=$('lab-results');
 if(!selected){$('lab-result-count').textContent='Nenhum ensaio';node.innerHTML=analysisHistoryMarkup('lab',st.lab,'data-lab-history')+labEmptyState();return;}
 const result=selected.result,points=result.points||result.pairs||[];
 $('lab-result-count').textContent=`${points.length} resultados · ${labState(selected)}`;
 node.innerHTML=analysisBanner(result)+analysisHistoryMarkup('lab',st.lab,'data-lab-history')+(points.length?`<div class="lab-secondary">${esc(result.notes?.join(' ')||'')}</div>${window.AMCharts.render(result,'lab')}`:'<div class="empty-state">Nenhuma observação atende aos filtros deste ensaio.</div>');
 node.querySelectorAll('[data-lab-history]').forEach(b=>b.onclick=()=>{st.labIntent=(st.labIntent||0)+1;st.labVisible=Number(b.dataset.labHistory);renderLabInfo();});
}
async function runLab(){
 const mode=st.lab,id=analysisHistory.begin(),intent=st.labIntent||0;
 try{
  const result=await perform(api('/api/lab','POST',{mode,...analysisInputs('lab',mode)}),null,false);
  analysisHistory.add(result,'lab',id);
  if(mode===st.lab&&intent===(st.labIntent||0)&&id>(st.labVisible||0))st.labVisible=id;
  renderLabInfo();notify('Experimento preservado no histórico com origem e estado de validade.');
 }catch(_e){}
}
/* Specialist tools reuse the verified Python simulation modules. No client-side metrics. */
const advancedInfo={
 diagnostic:['Diagnóstico operacional','Alertas por posto, filas, utilização e completude do cadastro.'],
 opportunities:['Oportunidades de melhoria','Variações de recursos, setups e regras de despacho na operação nominal.'],
 sensitivity:['Sensibilidade de capacidade','Ganho marginal de máquinas ou operadores em um posto selecionado.'],
 demand:['Limite de demanda','Identifique o primeiro multiplicador de demanda abaixo da meta de entregas.'],
 uncertainty:['Monte Carlo · tempos de processo','Repete a mesma falha com 12 sementes de tempos de processo.'],
 recovery:['Recuperação da produção','Experimenta respostas de capacidade mantendo a falha programada.']
};
const advancedGuidance={
 diagnostic:['Identifique o posto ou recurso com maior acúmulo e abra a inspeção da fábrica.','Diagnósticos são sinais do modelo, não inspeções de chão de fábrica.'],
 opportunities:['Examine variações de capacidade e despacho calculadas pelo motor.','A pontuação compara alternativas enumeradas, não garante ótimo global.'],
 sensitivity:['Selecione um posto e um tipo de recurso para estudar efeito marginal.','A disponibilidade e a habilitação de novos recursos não são verificadas integralmente.'],
 demand:['Defina o percentual mínimo de entregas antes de ampliar a demanda.','O limite encontrado depende dos parâmetros sintéticos adotados.'],
 uncertainty:['Compare execuções com sementes diferentes e observe a distribuição dos resultados.','Doze simulações são uma investigação exploratória, não uma probabilidade industrial validada.'],
 recovery:['Examine ações de recuperação de capacidade após a falha.','Compare custo e atrasos, respeitando os recursos disponíveis e as restrições.']
};
function advancedEmptyState(){
 const info=advancedInfo[st.advanced]||advancedInfo.diagnostic;
 const notes=advancedGuidance[st.advanced]||advancedGuidance.diagnostic;
 return `<div class="helpful-empty"><span>FERRAMENTA DE ANÁLISE</span><h3>${esc(info[0])}</h3><p>${esc(notes[0])}</p><p><strong>Atenção:</strong> ${esc(notes[1])}</p><button type="button" class="subtle-button" data-run-context="advanced">Executar ${esc(info[0])}</button></div>`;
}
function renderAdvancedInfo(){
 const info=advancedInfo[st.advanced];if(!info)return;
 $('advanced-title').textContent=info[0];$('advanced-description').textContent=info[1];
 $$('#advanced-tabs button').forEach(b=>b.classList.toggle('active',b.dataset.advanced===st.advanced));
 $('advanced-station-label').hidden=st.advanced!=='sensitivity';
 $('advanced-resource-label').hidden=st.advanced!=='sensitivity';
 $('advanced-sla-label').hidden=st.advanced!=='demand';
 const selected=$('advanced-station').value;
 $('advanced-station').innerHTML=Object.entries(st.data?.stations||{}).map(([id,r])=>`<option value="${esc(id)}">${esc(r.nome||id)} · ${esc(id)}</option>`).join('');
 $('advanced-station').value=st.data?.stations?.[selected]?selected:(st.data?.stations?.[st.station]?st.station:Object.keys(st.data?.stations||{})[0]||'');
 const entries=analysisHistory.list('advanced',st.advanced);
 const entry=entries.find(e=>e.id===st.advancedVisible)||entries[0];
 if(entry){renderAdvanced(entry.result);}else{st.advancedResult=null;$('advanced-export').disabled=true;$('advanced-result-count').textContent='Nenhuma análise';$('advanced-results').innerHTML=analysisHistoryMarkup('advanced',st.advanced,'data-advanced-history')+advancedEmptyState();}
}
const showVal=(v)=>v===null||v===undefined?'—':typeof v==='number'?h(Math.abs(v)<.0001?0:v):typeof v==='boolean'?(v?'Sim':'Não'):String(v);
const fieldName={
 'Ação':'Alternativa','Throughput Δ (%)':'Throughput Δ (%)','SLA Δ (p.p.)':'SLA Δ (p.p.)',
 'Custo/un Δ (%)':'Custo/un Δ (%)','Makespan Δ (%)':'Makespan Δ (%)','Score de oportunidade':'Índice comparativo',
 'Adição':'Recursos adicionais','Throughput':'Unidades/h','SLA':'Pedidos no prazo (%)','Custo/un':'Custo por unidade (R$)',
 'Makespan':'Conclusão (h)','Ganho marginal TP':'Ganho marginal (un/h)','Throughput Δ (%)':'Throughput Δ (%)',
 'Demanda x':'Multiplicador de demanda','Gargalo':'Gargalo','run':'Ensaio','seed':'Semente',
 'throughput':'Unidades/h','sla':'Pedidos no prazo (%)','makespan':'Conclusão (h)','unit_cost':'Custo/un (R$)',
 'bottleneck':'Gargalo','SLA Δ (p.p.)':'SLA Δ (p.p.)'
};
function advancedTable(rows){
 if(!rows?.length)return '<div class="empty-state">Nenhum resultado para as condições deste experimento.</div>';
 const keys=Object.keys(rows[0]);
 return `<div class="table-scroll advanced-table-scroll"><table class="data-table advanced-table"><thead><tr>${keys.map(k=>`<th>${esc(fieldName[k]||k)}</th>`).join('')}</tr></thead><tbody>${rows.map((r,i)=>`<tr>${keys.map((k,j)=>`<td ${j===0?'class="advanced-first"':''}>${esc(showVal(r[k]))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
function advancedBars(rows,valueKey,labelKey,title,unit,maxFixed=null){
 const items=(rows||[]).slice(0,12);if(!items.length)return '';
 const raw=items.map(r=>Number(r[valueKey]||0));
 const max=maxFixed||Math.max(1,...raw.map(v=>Math.max(0,v)));
 return `<div class="advanced-bars"><h3>${esc(title)}</h3><div class="advanced-bars-body">${items.map((r,i)=>{
   const v=raw[i];const pct=Math.min(100,Math.max(0,100*v/max));
   return `<div class="advanced-bar-row"><span>${esc(showVal(r[labelKey]))}</span><div class="advanced-bar-track"><div class="advanced-bar-fill" style="width:${pct}%"></div></div><strong>${esc(showVal(v))}${unit}</strong></div>`;
 }).join('')}</div></div>`;
}
function monteCarloDistribution(rows){
 const values=(rows||[]).filter(r=>r.feasible!==false&&r.sla!==null&&r.sla!==undefined).map(r=>Number(r.sla)).filter(Number.isFinite);
 if(!values.length)return '';
 const lo=0,hi=100,bins=10,count=Array(10).fill(0);
 for(const v of values)count[Math.min(9,Math.floor(Math.max(0,Math.min(99.999,v))/10))]++;
 const max=Math.max(1,...count),width=800,base=170,left=44,right=15,top=22,usable=width-left-right;
 const bars=count.map((n,i)=>{
  const w=usable/10-8,x=left+i*usable/10+4,height=n/max*120;
  return `<g><rect class="mc-bar" x="${x}" y="${base-height}" width="${w}" height="${height}" rx="2"><title>${i*10}–${(i+1)*10}%: ${n} execução(ões)</title></rect><text x="${x+w/2}" y="${base+17}" text-anchor="middle" class="mc-tick">${i*10}</text><text x="${x+w/2}" y="${Math.max(top+3,base-height-5)}" text-anchor="middle" class="mc-value">${n?n:''}</text></g>`;
 }).join('');
 const unchanged=count.filter(x=>x>0).length===1;
 const equalSla=values.length>1&&values.every(x=>Math.abs(x-values[0])<.005);
 return `<section class="mc-distribution"><div class="mc-head"><strong>Distribuição de cumprimento de prazos</strong><span>${values.length} execuções · valores da simulação</span></div>
 <svg viewBox="0 0 ${width} 220" role="img" aria-label="Histograma de percentual dos pedidos dentro do prazo"><line x1="${left}" y1="${base}" x2="${width-right}" y2="${base}" class="mc-axis"/>${bars}<text x="${width-right}" y="211" text-anchor="end" class="mc-legend">Cumprimento de prazos (%)</text></svg><p>${equalSla?'SLA igual em todas as execuções ('+h(values[0])+'%): nenhuma variação observada nesse indicador. ':unchanged?'Todas as execuções apresentaram SLA na mesma faixa de 10 pontos percentuais. ':''}Distribuição interna do modelo, sem interpretação como probabilidade observada na indústria.</p></section>`;
}
function renderAdvanced(result){
 st.advancedResult=result;$('advanced-export').disabled=false;
 const container=$('advanced-results');
 const notes=`<div class="advanced-notes">${(result.notes||[]).map(n=>`<p>${esc(n)}</p>`).join('')}</div>`;
 $('advanced-result-title').textContent=advancedInfo[result.mode]?.[0]||'Resultados';
 let head='';let rows=result.rows||[];
 if(result.mode==='diagnostic'){
  const q=result.quality||{};
  head=`<div class="advanced-report"><div><span>Completude do cadastro</span><strong>${h(q.score)} / 100</strong><small>Não mede acurácia industrial</small></div><div><span>Alertas ativos</span><strong>${integer(result.alerts?.length||0)}</strong><small>Regras do modelo</small></div><div><span>Gargalo da operação</span><strong>${esc(result.bottleneck||'—')}</strong><small>Incidente da análise de origem</small></div></div>`;
  head+=`<h3 class="advanced-subheading">Alertas do modelo</h3><div class="advanced-alerts">${(result.alerts||[]).length?result.alerts.map(a=>{const valid=!!st.data?.stations?.[a.station];return `<${valid?'button':'div'} class="advanced-alert ${valid?'advanced-focus':''}" ${valid?`data-focus="${esc(a.station)}" title="Inspecionar ${esc(a.station)} na simulação"`:''}><span class="advanced-level">${esc(a.level)}</span><div><strong>${esc(a.title)}</strong><p>${esc(a.detail)}</p></div>${valid?'<span class="advanced-open">Inspecionar posto ↗</span>':''}</${valid?'button':'div'}>`;}).join(''):'<p>Nenhum alerta pelas regras configuradas.</p>'}</div>`;
  if(q.missing?.length)head+=`<div class="advanced-notes"><strong>Pontos para revisar</strong><p>${esc(q.missing.join(' · '))}</p></div>`;
  rows=result.stations||[];
 } else if(result.mode==='uncertainty'){
  const m=result.summary||{};
  head=`<div class="advanced-report"><div><span>SLA médio simulado</span><strong>${showVal(m.sla?.mean)}%</strong><small>${rows.length} execuções</small></div><div><span>Conclusão média</span><strong>${showVal(m.makespan?.mean)} h</strong><small>Variação de tempos</small></div><div><span>Gargalo mais frequente</span><strong>${esc(result.dominant_bottleneck||'—')}</strong><small>${showVal(result.bottleneck_share)}% dos ensaios</small></div></div>`;
 } else if(result.mode==='sensitivity'){
  head='';
 } else if(result.mode==='demand'){
  head=`<div class="advanced-report"><div><span>Primeira ruptura de SLA</span><strong>${result.first_break===null?'Não identificada':h(result.first_break)+'×'}</strong><small>Faixa de 1,0× a 1,6×</small></div><div><span>Último nível que atende à meta</span><strong>${result.last_safe===null?'Nenhum':h(result.last_safe)+'×'}</strong><small>Meta de ${h(result.min_sla)}%</small></div></div>`;
 }
 // Gráficos técnicos específicos substituem as barras genéricas; tabela e notas permanecem.
 $('advanced-result-count').textContent=(result.mode==='diagnostic'?`${rows.length} postos`:`${rows.length} resultados`)+' · '+analysisHistory.status(result).label;
 container.innerHTML=analysisBanner(result)+analysisHistoryMarkup('advanced',result.mode,'data-advanced-history')+head+window.AMCharts.render(result,'advanced')+`<details class="advanced-extra-table"><summary>Tabela técnica original (consulta adicional)</summary>${advancedTable(rows)}</details>`+notes;
 container.querySelectorAll('[data-advanced-history]').forEach(b=>b.onclick=()=>{st.advancedIntent=(st.advancedIntent||0)+1;st.advancedVisible=Number(b.dataset.advancedHistory);renderAdvancedInfo();});
 container.querySelectorAll('[data-focus]').forEach(btn=>btn.addEventListener('click',()=>{
  const sid=btn.dataset.focus;if(!st.data?.stations?.[sid])return;
  st.station=sid;st.scene='incident';st.t=Math.min(horizon(),Number(st.data.spec?.start_h||0));
  navigate('simulacao');notify('Posto '+sid+' selecionado na simulação.');
 }));
}
async function runAdvanced(){
 const mode=st.advanced,id=analysisHistory.begin(),intent=st.advancedIntent||0;
 try{
  $('advanced-result-count').textContent='Calculando…';
  const result=await perform(api('/api/advanced','POST',{mode,...analysisInputs('advanced',mode)}),null,false);
  analysisHistory.add(result,'advanced',id);
  if(mode===st.advanced&&intent===(st.advancedIntent||0)&&id>(st.advancedVisible||0))st.advancedVisible=id;
  renderAdvancedInfo();notify('Análise preservada com seus parâmetros de origem.');
 }catch(e){if(mode===st.advanced)$('advanced-result-count').textContent='Erro na análise';}
}
/* Editable engineering-language suggestion derived only from the current run.
 * The operator still has to verify the reasoning and acknowledge real constraints. */
function technicalDecisionDraft(){
 const d=st.data||{},action=d.alternatives?.find(a=>a.signature===d.selected)||{};
 const initial=metricFor('incident')||{},changed=metricFor('response')||{},quality=d.decision_review||{};
 const compare=quality.status==='dominated'?'Outra resposta enumerada domina esta seleção em custo, prazo e SLA; a escolha exige justificativa adicional.':
  quality.status==='non_dominated'?'Esta escolha não é dominada nas três métricas entre as alternativas elegíveis enumeradas; isso não demonstra ótimo global.':
  'As condições de elegibilidade e a comparação de critérios devem ser verificadas antes da aplicação.';
 return {
  note:`A resposta ${action.action||'selecionada'} foi examinada no cenário sintético: sem intervenção, ${integer(initial.late_orders)} pedido(s) atrasados, SLA ${h(initial.sla_pct)}% e conclusão em ${h(initial.makespan_h)} h; com a resposta, ${integer(changed.late_orders)} pedido(s) atrasados, SLA ${h(changed.sla_pct)}% e conclusão em ${h(changed.makespan_h)} h. O custo da decisão modelado é ${brlExact(action.decision_cost)}, com diferença econômica estimada de ${brlExact(action.savings)} frente à falha sem resposta. ${compare}`,
  risks:'Antes de qualquer aplicação real, confirmar disponibilidade e habilitação de operadores, técnicos e peças, capacidade das estações, custos efetivamente evitáveis e prazos cadastrados. O experimento não equivale a homologação industrial.'
 };
}
/* Read-only financial consistency gate: compare explicit R$ amounts against
   results for the CURRENT run. Unknown amounts are not assumed fraudulent:
   they may be external, but cannot be presented as a modeled output. */
function moneyAuditCurrent(note){
 const d=st.data||{}, a=d.alternatives?.find(x=>x.signature===d.selected)||{};
 const ref=metricFor('incident')||{}, nom=metricFor('normal')||{}, res=metricFor('response')||{};
 const entries=[
  ['Falha · total',ref.total_cost],['Falha · operação',ref.operating_cost],['Falha · multas',ref.penalty_total],
  ['Nominal · total',nom.total_cost],['Nominal · operação',nom.operating_cost],['Nominal · multas',nom.penalty_total],
  ['Resposta · total',res.total_cost],['Resposta · operação',res.operating_cost],['Resposta · multas',res.penalty_total],
  ['Decisão · custo',a.decision_cost],['Intervenção · investimento',a.investment],['Diferença econômica',a.savings]
 ];
 const known=new Map();entries.forEach(([label,value])=>{
  if(value==null||!Number.isFinite(Number(value)))return;
  const key=Math.round(Number(value)*100);known.set(key,[...(known.get(key)||[]),label]);
 });
 const regex=/([-−]?\s*R\$\s*[-−]?\s*)((?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d{1,2})?)(?!\d|[.,]\d)/gi;
 const listed=[];
 for(const match of String(note||'').matchAll(regex)){
  const amount=Number(match[2].replace(/\./g,'').replace(',','.')) * (/[-−]/.test(match[1])?-1:1);
  if(Number.isFinite(amount)){
   const value=Math.round(amount*100);
   listed.push({written:match[0],cents:value,matched:known.has(value),sources:known.get(value)||[]});
  }
 }
 return {listed,unmatched:listed.filter(x=>!x.matched),known};
}
function renderMoneyAudit(){
 const audit=moneyAuditCurrent($('decision-note')?.value||'');
 const holder=$('decision-money-audit'),wrapper=$('decision-external-ack-wrap');
 if(!holder||!wrapper)return audit;
 if(audit.unmatched.length){
  const quoted=audit.unmatched.map(x=>esc(x.written)).slice(0,4).join(' · ');
  holder.hidden=false;holder.className='decision-money-audit money-alert';
  holder.innerHTML=`<div class="money-status"><strong>Confira uma quantia informada</strong><span>${quoted}</span></div><p>Ela não corresponde aos valores calculados nesta execução. Pode ser de outro cenário ou de uma fonte externa. Revise se quiser; seu texto não será alterado automaticamente.</p>`;
  // The same non-invasive safeguard applies in the normal and presentation modes.
  // A knowledgeable user may retain an outside figure with an explicit caveat.
  wrapper.hidden=false;
 }else if(audit.listed.length){
  holder.hidden=false;holder.className='decision-money-audit money-ok';
  holder.innerHTML='<div class="money-status"><strong>Quantias reconhecidas nos resultados</strong><span>'+audit.listed.length+' referência(s) conferida(s) numericamente</span></div><p>Esta comparação não garante que a interpretação escrita esteja correta.</p>';
  wrapper.hidden=true;
  $('decision-external-ack').checked=false;
 }else{
  holder.hidden=false;holder.className='decision-money-audit money-neutral';
  holder.innerHTML='<div class="money-status"><strong>Justificativa em texto livre</strong><span>Não é necessário informar valores em R$ para registrar.</span></div>';
  wrapper.hidden=true;
  $('decision-external-ack').checked=false;
 }
 return audit;
}
function similarDecisionSections(){
 const clean=v=>String(v||'').toLocaleLowerCase('pt-BR').replace(/[^a-zà-ÿ0-9]+/g,' ').trim();
 const a=clean($('decision-note')?.value),b=clean($('decision-risks')?.value);
 if(!a||!b)return false;
 if(a===b||a.includes(b)&&b.length>=60||b.includes(a)&&a.length>=60)return true;
 const wa=new Set(a.split(' ').filter(w=>w.length>=4)),wb=new Set(b.split(' ').filter(w=>w.length>=4));
 const overlap=[...wa].filter(w=>wb.has(w)).length;
 return Math.min(wa.size,wb.size)>=7&&overlap/Math.min(wa.size,wb.size)>.92;
}
function draftQuality(){
 const note=$('decision-note')?.value.trim()||'',risks=$('decision-risks')?.value.trim()||'';
 const words=note.toLocaleLowerCase('pt-BR').match(/[a-záéíóúâêôãõç]{3,}/g)||[];
 const enough=note.length>=65&&new Set(words).size>=8&&!/(.)\1{9,}/.test(note);
 return {enough,risks:risks.length>=25,distinct:!similarDecisionSections(),noteCount:note.length};
}
function insertTechnicalDraft(){
 const note=$('decision-note'),risks=$('decision-risks');if(!note||!risks)return;
 if(note.value.trim()||risks.value.trim()){
   const ok=window.confirm('Substituir os textos preenchidos por uma sugestão técnica calculada a partir deste experimento? Você poderá editar antes de registrar.');
   if(!ok)return;
 }
 const draft=technicalDecisionDraft();note.value=draft.note;risks.value=draft.risks;
 $('decision-external-ack').checked=false;updateDecisionValidation();note.focus();notify('Sugestão inserida. Confira os dados, ajuste a justificativa e valide os riscos antes de salvar.');
}
function renderDecisions(){
 const d=st.data;if(!d)return;
 const a=d.alternatives.find(x=>x.signature===d.selected);
 $('decision-selected').innerHTML=a?`${chosenRecord()?`<div class="record-completed" role="status"><div><span>REGISTRO CONFIRMADO NO COMPUTADOR</span><strong>${esc(localTimestamp(chosenRecord().utc))} · ${esc(chosenRecord().responsible||'Equipe')}</strong><small>Justificativa arquivada para o experimento e a alternativa selecionada.</small></div><button type="button" id="record-see-report">Gerar relatório →</button><button type="button" id="record-see-history">Abrir registro →</button></div>`:''}${decisionReviewMarkup()}<h3 class="alt-name">${esc(a.action)}</h3><div class="alt-metrics"><div><small>Custo total simulado</small><strong>${brl(a.decision_cost)}</strong></div><div><small>Pedidos no prazo</small><strong>${h(a.sla_pct)}%</strong></div><div><small>Economia líquida estimada</small><strong>${brl(a.savings)}</strong></div><div><small>Conclusão da carteira</small><strong>${h(a.makespan_h)} h</strong></div></div>
 <div class="evidence-pane"><h4>Condições consideradas</h4><div class="inspect-row"><span>Posto afetado</span><b>${esc(d.spec?.station||'—')}</b></div><div class="inspect-row"><span>Início da parada</span><b>${time(d.spec?.start_h)}</b></div><div class="inspect-row"><span>Duração considerada</span><b>${h(d.spec?.duration_h)} h</b></div><div class="inspect-row"><span>Investimento modelado</span><b>${brl(a.investment)}</b></div>${Number(a.investment)===0?'<p class="investment-caveat">Investimento zero no modelo não garante ausência de custos reais de realocação, treinamento ou parada.</p>':''}<div class="inspect-row"><span>Orçamento do estudo</span><b>${brl(d.spec?.budget)}</b></div><div class="inspect-row"><span>Execução da ação</span><b>${a.effective_h!=null?time(a.effective_h):'Não definida'}</b></div></div>
 <div class="evidence-pane"><h4>Pedidos avaliados</h4><div class="evidence-orders">${(a.order_impacts||[]).map(o=>`<div><span>${esc(o.id)}</span><span>${h(o.before_h)} h → ${h(o.after_h)} h</span><b class="${o.late_after?'risk-label':''}">${o.late_after?'Atraso previsto':'No prazo'}</b></div>`).join('')||'<p>Nenhum detalhamento de pedido disponível.</p>'}</div></div>
 <div class="alt-warning"><strong>Limites desta avaliação</strong><p>${esc(a.restriction_reasons?.join(' · ')||'Habilitações individuais, setups dependentes da sequência e capacidades finitas de buffers ainda não foram verificados integralmente.')}</p></div><div class="evidence-navigation"><button id="evidence-see-operation" class="subtle-button">Consultar operação</button><button id="evidence-see-analysis" class="subtle-button">Comparar respostas</button></div>`:'<div class="empty-state">Execute uma simulação para documentar uma resposta.</div>';
 if(a){bindReviewButtons($('decision-selected'));$('record-see-report')?.addEventListener('click',generateReport);$('record-see-history')?.addEventListener('click',()=>{navigate('historico');if(st.lastRecordedFilename)openHistory(st.lastRecordedFilename);});$('evidence-see-operation').onclick=()=>{st.scene='split';st.t=Number(d.spec.start_h)||0;navigate('simulacao')};$('evidence-see-analysis').onclick=()=>navigate('analise')};
 $('register-decision').textContent=chosenRecord()?'Registrar nova revisão da decisão →':'Registrar decisão →';
 $('decision-draft').disabled=!a;
 const noteKey=String(d.run_id||'')+'|'+String(d.selected||'');
 if(st.noteKey!==noteKey){const rec=chosenRecord();$('decision-note').value=rec?.note||'';$('decision-risks').value=rec?.risks||'';$('decision-owner').value=rec?.responsible||'';$('decision-ack').checked=!!rec;$('decision-external-ack').checked=!!rec?.external_amounts_acknowledged;st.noteKey=noteKey;updateDecisionValidation();}
 const welcome=$('assistant-messages')?.querySelector('.assistant-placeholder');
 if(welcome){const incident=d.metrics?.incident||{};welcome.innerHTML=`<div class="assistant-welcome"><span>LEITURA DO EXPERIMENTO</span><strong>${integer(incident.late_orders)} pedido(s) com atraso previsto sem resposta</strong><p>Seleção examinada: ${esc(a?.action||'Nenhuma')}. Consulte o Murphy para investigar as diferenças, não para executar uma ação.</p></div>`;}
}
function updateDecisionValidation(message=''){
 const note=$('decision-note');if(!note)return;
 const n=note.value.trim().length;
 const status=$('decision-validation');
 const money=renderMoneyAudit();
 const moneyOK=!money.unmatched.length||$('decision-external-ack').checked;
 // Same lightweight rules in both modes: free text, minimum context, acknowledgement.
 // Quality suggestions are informational, never an artificial word-count gate.
 const valid=n>=12&&moneyOK&&$('decision-ack').checked;
 let detail=valid?`Texto livre · ${n}/1000 caracteres · registro disponível`:
  n<12?`${n}/12 caracteres · descreva brevemente o motivo da escolha com suas palavras.`:
  !$('decision-ack').checked?'Confirme que a avaliação é uma simulação e depende de verificação física.':
  'A quantia não foi encontrada nesta execução. Confira ou confirme que deseja mantê-la sem validação automática.';
 if(valid&&similarDecisionSections())detail='Registro disponível. Dica: a seção de riscos pode trazer informações diferentes da justificativa.';
 if(valid&&!($('decision-risks')?.value||'').trim())detail='Registro disponível. Se conhecer riscos ou verificações pendentes, descrevê-los pode ajudar a auditoria.';
 status.textContent=message||detail;
 status.classList.toggle('invalid',!valid);
 note.setAttribute('aria-invalid',String(n>0&&n<12));
 $('register-decision').disabled=!valid;
 return {valid,money};
}

async function saveDecision(){
 const a=st.data?.alternatives.find(x=>x.signature===st.data.selected);
 if(!a){notify('Selecione uma alternativa primeiro.',true);return}
 if($('decision-note').value.trim().length<12){updateDecisionValidation('Descreva o motivo da escolha com suas próprias palavras (mínimo de 12 caracteres).');notify('Descreva brevemente o motivo da escolha.',true);$('decision-note').focus();return}
 if(!$('decision-ack').checked){updateDecisionValidation('Confirme que a decisão é baseada em simulação e requer verificações físicas.');notify('Reconheça as limitações do modelo antes de registrar.',true);$('decision-ack').focus();return}
 const money=moneyAuditCurrent($('decision-note').value);
 if(money.unmatched.length&&!$('decision-external-ack').checked){
  updateDecisionValidation();notify('Confira a quantia não reconhecida ou registre-a como informação não verificada.',true);$('decision-external-ack').focus();return;
 }
 try{const saved=await perform(api('/api/record','POST',{signature:a.signature,note:$('decision-note').value,risks:$('decision-risks').value,responsible:$('decision-owner').value,constraints_ack:$('decision-ack').checked,finance_ack:money.unmatched.length>0&&$('decision-external-ack').checked,expected_run_id:st.data.run_id}),'Decisão registrada. Relatório e histórico disponíveis.',false);const data=await api('/api/state');applyData(data);navigate('decisoes',{skipStack:true});$('record-see-report')?.focus();if(saved?.filename)st.lastRecordedFilename=saved.filename;}
 catch(_e){}
}
function assistantMessage(text,label='MURPHY · ANÁLISE LOCAL',question=false){
 const holder=$('assistant-messages');holder.querySelector('.assistant-placeholder')?.remove();
 const item=document.createElement('div');item.className='assistant-message'+(question?' question':'');
 const head=document.createElement('strong');head.textContent=label;
 const body=document.createElement('div');body.textContent=text;
 item.append(head,body);
 if(!question){
   const actions=document.createElement('div');actions.className='assistant-context-actions';
   const link=(caption,view)=>{const b=document.createElement('button');b.type='button';b.className='subtle-button';b.textContent=caption;b.dataset.assistantNav=view;actions.appendChild(b)};
   const name=String(label||'').toUpperCase();
   if(name.includes('CUSTO')){link('Ver composição no dashboard','paineis');link('Comparar intervenções','analise');}
   else if(name.includes('PEDIDO')){link('Investigar pedido na fábrica','simulacao');link('Comparar por pedido','analise');}
   else if(name.includes('GARGALO')){link('Inspecionar o gargalo e as filas','simulacao');link('Ver indicadores por posto','paineis');}
   else if(name.includes('LIMITES')){link('Conferir o modelo','modelo');link('Consultar alternativas','analise');}
   else{link('Examinar alternativas','analise');link('Ver simulação','simulacao');}
   item.append(actions);
 }
 holder.append(item);holder.scrollTop=holder.scrollHeight;
}
async function askAssistant(question){
 if(!question||!question.trim())return;
 assistantMessage(question,'PERGUNTA',true);
 try{const res=await perform(api('/api/assistant','POST',{question}),null,false);assistantMessage(res.text||'Sem resposta fundamentada para esta pergunta.',res.label||'MURPHY · ANÁLISE LOCAL');$('assistant-input').value=''}
 catch(_e){}
}
function localTimestamp(value){
 if(!value)return 'Data não registrada';
 const date=new Date(value);
 if(Number.isNaN(date.valueOf()))return String(value);
 return new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'short',timeZone:'America/Sao_Paulo'}).format(date)+' (Brasília)';
}
async function loadHistory(){
 try{
  const all=await api('/api/history');$('history-count').textContent=`${all.length} registros`;
  $('history-list').innerHTML=all.length?all.map(r=>`<button class="history-item" data-file="${esc(r.filename)}"><strong>${esc(r.action||'Decisão')}</strong><small>${esc(localTimestamp(r.utc))} · ${esc(r.run_id||'')}</small><small>Economia prevista: ${brl(r.savings)} · SLA ${h(r.sla_pct)}%</small></button>`).join(''):'<div class="empty-state">Nenhuma decisão registrada ainda.</div>';
  $$('#history-list .history-item').forEach(btn=>btn.onclick=()=>openHistory(btn.dataset.file));
 }catch(e){notify(e.message,true)}
}
async function openHistory(filename){
 try{
  const r=await api('/api/history/'+encodeURIComponent(filename));
  const action=r.examined_action||{},record=r.record||{};
  const audit=record.monetary_audit||{};
  const moneyAuditText=audit.status==='matched'?'Referências com R$ reconhecidas nos indicadores da execução registrada.':
    audit.status==='no_explicit_amounts'?'Justificativa sem quantias explícitas em R$.':
    audit.status==='requires_confirmation'?'Quantias não conferidas nesta execução, mantidas com ciência do responsável: '+(audit.unmatched||[]).map(x=>x.written).join(' · '):
    'Registro anterior sem conferência automatizada de valores.';
  const savedCosts=record.cost_snapshot||{};
  const economicTrace=savedCosts.run_id?`<div class="history-economic-evidence"><strong>Base monetária armazenada na decisão</strong><div><span>Falha sem resposta</span><b>${brlExact(savedCosts.incident_total_cost)}</b></div><div><span>Resposta + investimento</span><b>${brlExact(savedCosts.decision_cost)}</b></div><div><span>Diferença modelada</span><b>${brlExact(savedCosts.savings)}</b></div><small>Valores sintéticos vinculados à execução ${esc(savedCosts.run_id)}.</small></div>`:'';
  $('history-detail').innerHTML=`<div class="history-report-head"><span>FICHA DE DECISÃO</span><h3>${esc(record.action)}</h3><small>${esc(localTimestamp(record.utc))}</small></div><div class="history-meta"><div><span>Responsável</span><strong>${esc(record.responsible||'Não informado')}</strong></div><div><span>Experimento</span><strong>${esc(record.run_id||'—')}</strong></div><div><span>Viabilidade física</span><strong>Não homologada</strong></div></div><div class="inspect-data"><div class="inspect-row"><span>Economia líquida estimada</span><b>${brl(action.savings)}</b></div><div class="inspect-row"><span>Pedidos no prazo</span><b>${h(action.sla_pct)}%</b></div><div class="inspect-row"><span>Conclusão</span><b>${h(action.makespan_h)} h</b></div></div>${record.decision_review?decisionReviewMarkup(record.decision_review,false):''}<h3>Justificativa</h3><p>${esc(record.note||'Nenhuma justificativa informada.')}</p><h3>Riscos e verificações pendentes</h3><p>${esc(record.risks||'Não detalhados neste registro.')}</p><div class="history-validation">${esc(moneyAuditText)}</div>${economicTrace}<div class="history-validation">${record.constraints_ack?'Limitações reconhecidas pelo responsável no registro.':'Registro legado sem confirmação explícita das limitações.'}</div><details class="history-technical"><summary>Rastreabilidade técnica · JSON e integridade</summary><pre>${esc(JSON.stringify({run_id:r.run_id,record:record,sha256:r.sha256},null,2))}</pre></details>`;
  $$('#history-list .history-item').forEach(b=>b.classList.toggle('active',b.dataset.file===filename));
 }catch(e){notify(e.message,true)}
}
function download(content,name){const blob=new Blob([content],{type:'application/json'}),url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url)}
async function importModel(file){
 try{const obj=JSON.parse(await file.text());await perform(api('/api/model','POST',{stations:obj.stations,orders:obj.orders}),'Modelo importado e recalculado.');st.editing=null;navigate('modelo')}
 catch(e){notify('Falha ao importar: '+e.message,true)}
}

/* Schedule uses the simulator's recorded start/end intervals and exact segments.
   No physical travel animation or invented transport durations. */
function renderSchedule(force=false){
 const svg=$('schedule-chart');if(!svg||!st.data)return;
 const p=currentReplay();if(!p)return;
 if(p.details_omitted){svg.innerHTML='<text x="20" y="35">Modo reduzido: cronograma por peça omitido; estados agregados preservados.</text>';st.scheduleKey='';return;}
 const key=`${st.data.run_id}:${st.scene}:${st.data.selected}:${st.order||''}`;
 if(!force&&st.scheduleKey===key)return;
 st.scheduleKey=key;
 const hor=Math.max(1,horizon()),left=138,width=1020,height=34+47*p.stations.length+38;
 svg.setAttribute('viewBox',`0 0 ${left+width+24} ${height}`);
 const px=t=>left+Math.max(0,Math.min(hor,t))/hor*width;
 const grid=Array.from({length:9},(_,i)=>{
   const t=hor*i/8,x=px(t);return `<line class="gantt-grid" x1="${x}" y1="26" x2="${x}" y2="${height-14}"/><text class="gantt-label" x="${x}" y="16" text-anchor="middle">${h(t)} h</text>`;
 }).join('');
 const base=p.stations.map((station,i)=>{const y=34+47*i;
    return `<text class="gantt-station" x="7" y="${y+22}">${esc(station.id)}</text><rect x="${left}" y="${y}" width="${width}" height="32" class="gantt-track"/>`;
 }).join('');
 const operations=(p.operations||[]);
 const bars=operations.slice(0,2800).map(op=>{
  const [idx,arrival,start,end,oid,unit,step,slot,segments]=op;
  if(!Number.isFinite(Number(start))||!Number.isFinite(Number(end)))return '';
  const y=34+idx*47+4,soft=st.order&&st.order!==oid;
  const spans=Array.isArray(segments)&&segments.length?segments:[[start,end]];
  const shown=spans.filter(seg=>Array.isArray(seg)&&seg.length>=2).map(([a,b])=>`<rect class="gantt-operation ${soft?'dimmed':''}" x="${px(a)}" y="${y}" width="${Math.max(1.5,px(b)-px(a))}" height="24" rx="2"/>`).join('');
  return `<g class="gantt-op" data-order="${esc(oid)}" data-station="${esc(p.stations[idx]?.id||'')}" data-time="${start}">${shown}<title>${esc(oid)} · unidade ${esc(unit)} · etapa ${esc(step)} · ${time(start)}–${time(end)} · espera ${h(Math.max(0,start-arrival))} h</title></g>`;
 }).join('');
 const outageIndex=p.outage?p.stations.findIndex(q=>q.id===p.outage.station):-1;
 const outage=p.outage&&outageIndex>=0?`<rect class="gantt-outage" x="${px(p.outage.start)}" y="${34+47*outageIndex}" width="${Math.max(2,px(p.outage.end)-px(p.outage.start))}" height="32"/><title>Parada ${esc(p.outage.station)} · ${time(p.outage.start)} a ${time(p.outage.end)}</title>`:'';
 svg.innerHTML=grid+base+outage+bars+`<line id="schedule-cursor" class="gantt-cursor" x1="${left}" y1="28" x2="${left}" y2="${height-14}"/>`;
 svg.querySelectorAll('.gantt-op').forEach(g=>g.addEventListener('click',()=>{
   st.station=g.dataset.station;st.order=g.dataset.order;st.t=Number(g.dataset.time);st.playing=false;renderScene(true);
 }));
 $('schedule-label').textContent=`${operations.length} operações calculadas · ${p.stations.length} postos`+(operations.length>2800?' · 2.800 exibidas':'');
 updateScheduleCursor();
}
function updateScheduleCursor(){
 const svg=$('schedule-chart'),line=svg?.querySelector('#schedule-cursor');if(!line)return;
 const x=138+1020*Math.max(0,st.t)/Math.max(1,horizon());line.setAttribute('x1',x);line.setAttribute('x2',x);
}
async function showProjects(){
 try{const rows=await api('/api/projects');
   $('projects-list').innerHTML=rows.map(p=>`<div class="project-row"><div><strong>${esc(p.name)}</strong><small>${integer(p.stations)} postos · ${integer(p.orders)} pedidos · ${esc((p.updated_at||'').slice(0,16).replace('T',' '))}</small></div>${p.active?'<span class="active-project">Atual</span>':`<button class="subtle-button" data-open-project="${esc(p.id)}">Abrir</button>`}</div>`).join('');
   const active=rows.find(p=>p.active);$('project-rename-name').value=active?.name||'';
   $('projects-dialog').showModal();
   $('projects-list').querySelectorAll('[data-open-project]').forEach(b=>b.onclick=async()=>{
     try{st.playing=false;const data=await perform(api('/api/project/open','POST',{id:b.dataset.openProject}),'Projeto aberto.');
       st.t=0;st.scene='incident';st.stageKey='';st.scheduleKey='';st.editing=null;st.savedExperiments=[];
       $('projects-dialog').close();navigate('simulacao');}catch(_e){}
   });
 }catch(e){notify(e.message,true)}
}
async function createProject(){
 const name=$('project-new-name').value.trim();if(name.length<3){notify('Informe um nome com pelo menos 3 caracteres.',true);return;}
 try{await perform(api('/api/project/create','POST',{name,duplicate:$('project-duplicate').checked}),'Projeto criado.');
     st.t=0;st.scene='incident';st.stageKey='';st.scheduleKey='';st.editing=null;st.savedExperiments=[];
     $('projects-dialog').close();navigate('modelo');}catch(_e){}
}
async function renameProject(){
 try{await perform(api('/api/project/rename','POST',{name:$('project-rename-name').value}),'Projeto renomeado.');$('projects-dialog').close();}
 catch(_e){}
}
async function loadExperiments(){
 if(!st.data)return;
 try{
  st.savedExperiments=await api('/api/experiments');
  const items=st.savedExperiments;
  $('experiment-count').textContent=`${items.length} arquivados`;
  $('experiment-list').innerHTML=items.length?items.slice(0,30).map(x=>{
   const m=x.metrics?.response||x.metrics?.incident||{};
   return `<div class="journal-row"><div><strong>${esc(x.name)}</strong><small>${esc((x.created_at||'').replace('T',' ').slice(0,16))} · ${esc(x.selected_action||'Sem intervenção')}</small></div><div><b>${h(m.makespan_h)} h</b><span>${integer(m.late_orders)} atrasos</span></div></div>`;
  }).join(''):'<div class="journal-empty">Nenhum experimento guardado. Execute uma simulação e use “Guardar experimento” para criar sua primeira referência.</div>';
  const opts=`<option value="">Selecione</option>`+items.map(x=>`<option value="${esc(x.id)}">${esc(x.name)}</option>`).join('');
  const first=$('experiment-first').value,second=$('experiment-second').value;
  $('experiment-first').innerHTML=opts;$('experiment-second').innerHTML=opts;
  if(items.some(x=>x.id===first))$('experiment-first').value=first;
  else if(items.length)$('experiment-first').value=items[items.length-1].id;
  if(items.some(x=>x.id===second))$('experiment-second').value=second;
  else if(items.length>1)$('experiment-second').value=items[0].id;
  $('experiment-compare').disabled=items.length<2;
 }catch(e){notify('Não foi possível carregar experimentos: '+e.message,true)}
}
async function saveExperiment(){
 const name=$('experiment-name').value.trim();if(name.length<3){notify('Dê um nome ao experimento para guardá-lo.',true);return}
 try{await perform(api('/api/experiment/save','POST',{name}),'Experimento guardado na biblioteca.',false);
  $('experiment-name').value='';await loadExperiments();}catch(_e){}
}
async function compareExperiments(){
 const first=$('experiment-first').value,second=$('experiment-second').value;
 if(!first||!second||first===second){notify('Selecione dois experimentos distintos.',true);return}
 try{const r=await perform(api('/api/experiment/compare','POST',{first,second}),null,false);
  const vals=['late_orders','sla_pct','makespan_h'];
  const labels={'late_orders':'Pedidos atrasados','sla_pct':'Cumprimento de prazos','makespan_h':'Conclusão (h)','total_cost':'Custo simulado (R$)'};
  const f=r.first.metrics.response||r.first.metrics.incident||{},s=r.second.metrics.response||r.second.metrics.incident||{};
  $('experiment-comparison').innerHTML=`<div class="journal-compare-head"><strong>${esc(r.first.name)} × ${esc(r.second.name)}</strong><span>${r.same_model?'Mesmo modelo produtivo':'Modelos diferentes · não atribuir causalidade'}</span></div>
   <table class="data-table"><thead><tr><th>Indicador</th><th>Referência</th><th>Comparação</th><th>Variação B − A</th></tr></thead><tbody>${vals.map(k=>`<tr><td>${labels[k]}</td><td>${h(f[k])}</td><td>${h(s[k])}</td><td>${r.delta[k]===null?'—':`${r.delta[k]>0?'+':''}${h(r.delta[k])}`}</td></tr>`).join('')}</tbody></table>
   <h3>Composição econômica arquivada</h3>
   <table class="data-table" data-archived-economics><thead><tr><th>Componente (R$)</th><th>Referência A</th><th>Comparação B</th><th>Variação B − A</th></tr></thead><tbody>${['scenario_cost','investment','decision_cost','savings','reference_cost'].map(k=>{
    const labels={scenario_cost:'Custo do cenário · operação + multas',investment:'Investimento da intervenção',decision_cost:'Custo total da decisão',savings:'Economia líquida · frente à própria referência',reference_cost:'Custo da referência sem resposta'};
    const e=r.economics,format=v=>v===null||v===undefined?'Não registrado / não calculado':brlExact(v);
    return `<tr data-economic-component="${k}"><td>${labels[k]}</td><td>${format(e?.first?.[k])}</td><td>${format(e?.second?.[k])}</td><td>${format(e?.delta?.[k])}</td></tr>`;
   }).join('')}</tbody></table>
   ${r.economics?.first?.status!=='complete'||r.economics?.second?.status!=='complete'?'<p role="status">Comparação econômica parcial: há componentes não registrados ou não calculados. O investimento ausente não foi considerado zero.</p>':''}
   ${!r.economics?.same_reference?'<p role="status">Referências econômicas diferentes ou não identificadas. As economias líquidas usam suas próprias referências.</p>':''}
   <p>${esc(r.note)}</p>`;
 }catch(_e){}
}


/* Accessible learning layer. Every explanation remains tied to the active model;
   it never uses unverified constraints to claim industrial feasibility. */
const helpCatalog={
 simulacao:{title:'Simulação da produção',what:'O mapa representa os postos e as filas do modelo. A execução é calculada pelo motor de eventos discretos; o movimento interno das máquinas é apenas uma indicação visual de atividade.',when:'Execute o cenário de referência, acompanhe o incidente e selecione um posto ou pedido para investigar.',how:'Use a linha do tempo para avançar ou retroceder. Compare a operação sem intervenção com a resposta selecionada. Fluxos entre postos representam precedência lógica, não transporte com duração medida.',act:'Selecionar um posto na fábrica ou uma ordem na carteira.'},
 modelo:{title:'Modelo produtivo',what:'Define postos, quantidade de máquinas, operadores, roteiros, volumes, prazos e custos do estudo.',when:'Quando quiser representar outra fábrica, alterar a demanda ou avaliar a consequência de recursos diferentes.',how:'Edite os campos e clique em Aplicar alterações. O programa recalcula os cenários; experimento anterior salvo continua disponível na biblioteca. Roteiros seguem a ordem dos postos cadastrados.',act:'Editar um parâmetro, aplicar e comparar os resultados.'},
 paineis:{title:'Painéis analíticos',what:'Reúne resultados do mesmo experimento em visões por posto, pedido, cenário, custo e robustez. Os dados vêm do motor de eventos discretos.',when:'Quando precisar investigar desempenho, comparar resultados ou compartilhar evidências de um experimento.',how:'Selecione um painel e um cenário de referência. Clique em postos, pedidos ou alternativas para continuar a investigação nas ferramentas correspondentes. Monte Carlo executa novas sementes sintéticas apenas quando solicitado.',act:'Selecionar a CNC no painel Operação e abrir a inspeção na fábrica.'},
 analise:{title:'Análise de impacto',what:'Compara a operação nominal, a parada sem resposta e intervenções enumeradas pelo motor.',when:'Após definir uma falha ou quando um pedido estiver sujeito a atraso.',how:'Observe prazo e custo total, selecione uma alternativa na tabela ou no gráfico e examine o impacto por pedido. “Viável no modelo” não comprova skills, setup ou buffers industriais não verificados.',act:'Selecionar uma resposta e abrir sua comparação na simulação.'},
 laboratorio:{title:'Laboratório de cenários',what:'Permite variar hipóteses de parada, despacho, demanda e capacidade, preservando o modelo principal.',when:'Para testar a sensibilidade dos resultados antes de recomendar uma decisão.',how:'Defina um ensaio e execute. Compare o comportamento entre configurações; testes pareados e Monte Carlo neste ambiente não representam probabilidades empíricas calibradas.',act:'Executar um ensaio de duração da parada.'},
 avancadas:{title:'Análises avançadas',what:'Oferece diagnóstico, oportunidades, sensibilidade de recursos, limite de demanda, incerteza e recuperação.',when:'Quando for necessário explicar gargalos, investigar capacidade ou avaliar robustez.',how:'Cada ferramenta mostra as hipóteses e limitações do motor. Não confunda oportunidades enumeradas com uma otimização global comprovada.',act:'Abrir Diagnóstico operacional e selecionar o posto em destaque.'},
 decisoes:{title:'Decisões e evidências',what:'Reúne alternativa selecionada, custos, impacto por pedido e condições avaliadas, para registrar uma justificativa.',when:'Depois de comparar resultados e verificar as condições da resposta escolhida.',how:'A decisão registrada representa uma análise de simulação: não aciona máquinas. Escreva o motivo, as premissas e os riscos antes de salvar.',act:'Inspecionar evidências e registrar uma justificativa própria.'},
 historico:{title:'Registros de decisão',what:'Permite recuperar justificativas e resultados salvos neste computador.',when:'Para explicar uma escolha anterior ou comparar decisões de experimentos passados.',how:'Os registros são locais. Consulte as premissas associadas e evite aplicar conclusões antigas a modelos que foram alterados.',act:'Selecionar um registro para consultar as evidências.'}
};
const metricGuides={
 'Pedidos com atraso':['Número de pedidos cuja conclusão prevista excede o prazo cadastrado.','Pedido atrasado quando a hora da última conclusão supera o prazo. É uma contagem de pedidos, não de unidades.'],
 'Cumprimento de prazos':['Percentual de pedidos concluídos até o prazo previsto.','SLA (%) = (pedidos no prazo ÷ total de pedidos) × 100. A métrica reflete o cenário calculado, não desempenho observado de uma fábrica.'],
 'Término previsto':['Momento final da programação calculada.','O makespan depende da referência de início e da conclusão da última operação. Os tempos da simulação são expressos em horas.'],
 'Custo do cenário':['Estimativa de custos operacionais e penalidades do cenário.','Para analisar uma resposta, use o custo de decisão que inclui investimentos modelados. O custo operacional isolado não representa economia líquida da intervenção.'],
 'Diferença de custo bruto':['Diferença entre os custos totais dos cenários de parada e resposta, antes dos investimentos.','Não interprete como economia líquida. Consulte a coluna Economia líquida nas alternativas e verifique custos não modelados.'],
 'Variação de término':['Redução ou acréscimo do makespan entre os futuros em comparação.','A diferença é calculada em horas entre as conclusões previstas do cenário sem resposta e do cenário com intervenção.']
};
function explanationOrder(){
 if(!st.data)return '<p>Execute uma simulação primeiro.</p>';
 const d=st.data,ord=d.orders.find(o=>o.id===st.order)||d.orders[0];
 if(!ord)return '<p>Nenhum pedido cadastrado.</p>';
 const p=replayFor(st.scene==='response'?'response':'incident')||currentReplay();
 const ops=(p?.operations||[]).filter(op=>op[4]===ord.id);
 const waits=ops.map(op=>({station:p?.stations?.[op[0]]?.id||'—', wait:Math.max(0,Number(op[2])-Number(op[1]))}));
 waits.sort((a,b)=>b.wait-a.wait);
 const biggest=waits[0];
 const completions=p?.order_completions?.[ord.id]||[];
 const done=completions.length?Math.max(...completions):null;
 const late=done==null?null:Math.max(0,done-Number(ord.prazo_h));
 const alt=d.alternatives.find(a=>a.signature===d.selected);
 const impact=(alt?.order_impacts||[]).find(x=>x.id===ord.id);
 const affected=(p?.outage?.station && ops.some(op=>p.stations?.[op[0]]?.id===p.outage.station));
 return `<div class="guide-fact"><strong>${esc(ord.id)} · ${esc(ord.produto||'Pedido')}</strong><span>Prazo ${time(ord.prazo_h)} · conclusão ${done==null?'não registrada':time(done)}</span><span>${late===null?'Conclusão não disponível':late>0?'Atraso previsto: '+h(late)+' h':'Dentro do prazo neste cenário'}</span></div>
 <h3>Onde houve espera?</h3><p>${biggest?`A maior espera observada antes de uma operação deste pedido foi de <b>${h(biggest.wait)} h</b> no posto <b>${esc(biggest.station)}</b>.`:'Não há espera registrada para este pedido.'}</p>
 <p>${affected?'O roteiro do pedido passa pelo posto em que a parada foi configurada. Isso indica exposição ao incidente, mas não prova isoladamente toda a causalidade do atraso.':'O roteiro do pedido não contém o posto da falha configurada; o impacto pode decorrer da competição por outros recursos.'}</p>
 ${impact?`<h3>Comparação entre respostas</h3><p>Conclusão sem resposta: <b>${time(impact.before_h)}</b>. Com a alternativa selecionada: <b>${time(impact.after_h)}</b>.</p>`:''}
 <p class="guide-caveat">Origem: registros de operações e conclusões calculadas pelo motor. Atribuição causal completa exige análise contrafactual e verificação das restrições físicas.</p>`;
}
function explanationImpact(){
 if(!st.data)return '<p>Execute uma simulação primeiro.</p>';
 const d=st.data,a=metricFor('incident'),b=metricFor('response'),s=d.alternatives.find(x=>x.signature===d.selected);
 const n=(s?.order_impacts||[]).filter(x=>x.late_before&&!x.late_after).length;
 return `<div class="guide-fact"><strong>${esc(s?.action||'Alternativa selecionada')}</strong><span>Sem intervenção: ${integer(a?.late_orders)} pedidos atrasados · com resposta: ${integer(b?.late_orders)}.</span><span>Pedidos recuperados nos resultados: ${integer(n)}.</span></div>
 <h3>Qual foi a diferença?</h3><p>Conclusão prevista: ${h(a?.makespan_h)} h sem intervenção e ${h(b?.makespan_h)} h com a resposta. Isso corresponde a ${h((a?.makespan_h||0)-(b?.makespan_h||0))} h de diferença no cenário calculado.</p>
 <h3>E o custo?</h3><p>O custo de decisão informado pelo motor para a alternativa é ${brl(s?.decision_cost)} e o investimento modelado é ${brl(s?.investment)}. Custos não cadastrados não entram na comparação.</p><p class="guide-caveat">Estas diferenças são projeções de um modelo sintético. Skills, setups e buffers podem não estar integralmente representados.</p>`;
}
function renderImpactInterpretation(){
 const d=st.data,a=metricFor('incident'),b=metricFor('response'),s=d?.alternatives.find(x=>x.signature===d.selected);
 if(!a||!b||!$('impact-interpretation'))return;
 const improved=Math.max(0,(a.late_orders||0)-(b.late_orders||0));
 const recovered=(s?.order_impacts||[]).filter(o=>o.late_before&&!o.late_after);
 const late=(s?.order_impacts||[]).filter(o=>o.late_before);
 const changedLate=(s?.order_impacts||[]).filter(o=>!o.late_before&&o.late_after);
 $('impact-interpretation').innerHTML=`<div class="interpret-title"><span>SEQUÊNCIA DE ANÁLISE · MODELO SIMULADO</span><button type="button" id="interpret-details">Origem dos resultados ${icon('arrow')}</button></div>
 <div class="impact-path" aria-label="Etapas da avaliação de incidente e resposta">
  <button type="button" class="impact-path-node" data-impact-go="machine"><small>01 / INCIDENTE</small><strong>${esc(d.spec?.station||'—')}</strong><span>Parada ${h(d.spec?.duration_h)} h · ${time(d.spec?.start_h)}</span><em>Localizar no replay ↗</em></button>
  <span class="impact-path-separator" aria-hidden="true">→</span>
  <button type="button" class="impact-path-node" data-impact-go="orders"><small>02 / EFEITO SEM RESPOSTA</small><strong>${integer(a.late_orders)} pedido(s)</strong><span>${late.length?esc(late.slice(0,3).map(o=>o.id).join(' · ')):'Sem atraso previsto'}</span><em>Examinar pedidos ↗</em></button>
  <span class="impact-path-separator" aria-hidden="true">→</span>
  <button type="button" class="impact-path-node" data-impact-go="response"><small>03 / INTERVENÇÃO EXAMINADA</small><strong>${integer(recovered.length)} prazo(s) recuperado(s)</strong><span>${esc(s?.action||'Resposta não selecionada')}</span><em>Comparar A/B ↗</em></button>
 </div>
 <p>Na resposta selecionada, a simulação prevê <b>${integer(b.late_orders)} pedido(s) atrasado(s)</b>, ante <b>${integer(a.late_orders)}</b> sem intervenção. ${improved>0?`A redução líquida prevista é de ${integer(improved)} pedido(s) atrasado(s).`:'Não há redução líquida de pedidos atrasados.'} ${changedLate.length?`Há ${integer(changedLate.length)} pedido(s) que passam a atrasar nessa resposta.`:''}</p>
 <small>Representação dos resultados e hipóteses do motor; as setas mostram a ordem da investigação, não causalidade física comprovada. Skills, setups e buffers devem ser verificados.</small>`;
 $('interpret-details').onclick=()=>openHelp('impact');
 $('impact-interpretation').querySelectorAll('[data-impact-go]').forEach(button=>button.onclick=()=>{
   const action=button.dataset.impactGo;st.playing=false;
   if(action==='machine'){st.station=d.spec?.station||st.station;st.scene='incident';st.t=Number(d.spec?.start_h)||0;st.focus=true;}
   if(action==='orders'){st.order=late[0]?.id||d.orders[0]?.id||null;st.scene='incident';st.t=Number(d.spec?.start_h)||0;st.focus=false;}
   if(action==='response'){st.scene='split';st.t=informativeComparisonTime();st.focus=false;}
   navigate('simulacao');
 });
}
function contextHelpMarkup(topic){
 if(topic==='metric'){
  const title=st.metricName||'Indicador',data=metricGuides[title]||['Indicador calculado pelo motor.','Consulte o cenário e as hipóteses antes de usar este número como referência.'];
  return `<div class="guide-fact"><strong>${esc(title)}</strong></div><h3>O que significa</h3><p>${esc(data[0])}</p><h3>Como é interpretado</h3><p>${esc(data[1])}</p>`;
 }
 if(topic==='order')return explanationOrder();
 if(topic==='impact')return explanationImpact();
 const info=helpCatalog[topic]||helpCatalog.simulacao;
 return `<div class="guide-fact"><strong>Área: ${esc(info.title)}</strong></div><h3>O que faz</h3><p>${esc(info.what)}</p><h3>Quando utilizar</h3><p>${esc(info.when)}</p><h3>Como interpretar</h3><p>${esc(info.how)}</p><div class="guide-next"><span>PRÓXIMA AÇÃO</span><p>${esc(info.act)}</p></div>`;
}
function openHelp(topic=st.view){
 st.helpTopic=topic;
 $('guide-heading').textContent=topic==='metric'?(st.metricName||'Indicador'):topic==='order'?'Interpretação do pedido':topic==='impact'?'Interpretação de cenários':helpCatalog[topic]?.title||'Ajuda contextual';
 $('guide-content').innerHTML=contextHelpMarkup(topic);
 $('guide-panel').hidden=false;$('guide-backdrop').hidden=false;
 $('guide-close').focus();
}
function closeHelp(){ $('guide-panel').hidden=true;$('guide-backdrop').hidden=true; }
const tutorial=[
 {view:'modelo',target:'#model-tabs',title:'Confira o modelo produtivo',body:'Postos, recursos, roteiros e pedidos definem as condições de cada simulação. Você pode alterar o exemplo, mas não precisa fazer isso agora.'},
 {view:'simulacao',target:'#scene-tabs',title:'Observe a produção',body:'Alterne entre plano nominal, parada e resposta. O mapa e as filas vêm do simulador; animações internas das máquinas indicam apenas atividade.'},
 {view:'simulacao',target:'#timeline-range',title:'Investigue o tempo simulado',body:'Arraste a linha do tempo ou use reproduzir. Selecione uma máquina para consultar fila, ocupação e operações no instante escolhido.'},
 {view:'analise',target:'#alternatives-table',title:'Compare respostas ao incidente',body:'Selecione uma intervenção e observe custo, entregas no prazo e consequências por pedido. Viabilidade no modelo não garante execução física.'},
 {view:'laboratorio',target:'#lab-tabs',title:'Experimente outras hipóteses',body:'Os ensaios variam parâmetros e ajudam a compreender sensibilidade. Cada teste utiliza o modelo atual sem aplicar uma decisão na operação.'},
 {view:'decisoes',target:'#decision-selected',title:'Registre sua avaliação',body:'Examine evidências, limitações e impactos. Uma decisão só é registrada se você escrever a justificativa e confirmar.'}
];
function clearTourHighlight(){$$('.tour-highlight').forEach(e=>e.classList.remove('tour-highlight'));}
function startTour(){closeHelp();st.tourOrigin=st.view;st.tourStep=0;renderTour();}
function endTour(){const origin=st.tourOrigin;st.tourStep=-1;$('tour-panel').hidden=true;clearTourHighlight();if(origin&&origin!==st.view)navigate(origin,{skipStack:true});}
function renderTour(){
 if(st.tourStep<0)return;
 const step=tutorial[st.tourStep];
 navigate(step.view,{skipStack:true});
 clearTourHighlight();
 const target=document.querySelector(step.target);
 if(target)target.classList.add('tour-highlight');
 $('tour-panel').hidden=false;
 $('tour-progress').textContent=`ETAPA ${st.tourStep+1} DE ${tutorial.length}`;
 $('tour-title').textContent=step.title;$('tour-text').textContent=step.body;
 $('tour-previous').disabled=st.tourStep===0;
 $('tour-next').textContent=st.tourStep===tutorial.length-1?'Concluir percurso':'Próxima etapa';
 if(target){target.scrollIntoView({behavior:'instant',block:'nearest'});}
}


function generateReport(){
 const d=st.data;if(!d){notify('Execute uma simulação antes de gerar o relatório.',true);return}
 const ref=metricFor('incident'),response=metricFor('response'),base=metricFor('normal');
 const selected=d.alternatives.find(a=>a.signature===d.selected);
 if(!ref||!selected){notify('Selecione uma resposta antes de gerar o relatório.',true);return}
 const rows=(selected.order_impacts||[]).map(o=>{const slack=Number(o.due_h)-Number(o.after_h);return `<tr><td>${esc(o.id)}</td><td>${h(o.due_h)} h</td><td>${h(o.before_h)} h</td><td>${h(o.after_h)} h</td><td>${h(slack)} h</td><td>${o.late_after?'Atraso':slack<=.5?'Folga reduzida':'No prazo'}</td></tr>`;}).join('');
 const cards=(title,m)=>`<div class="comparison"><h3>${esc(title)}</h3><dl><dt>Conclusão prevista</dt><dd>${h(m?.makespan_h)} h</dd><dt>Pedidos no prazo</dt><dd>${h(m?.sla_pct)}%</dd><dt>Pedidos atrasados</dt><dd>${integer(m?.late_orders)}</dd><dt>Custo do cenário</dt><dd>${brlExact(m?.total_cost)}</dd></dl></div>`;
 const review=d.decision_review||{},record=chosenRecord();
 const reviewHtml=decisionReviewMarkup(review,false);
 const audit=record?.monetary_audit;
 const matchedAudit=audit?.status==='matched'?'Quantias explícitas com R$ conferidas numericamente contra o experimento atual.':audit?.status==='no_explicit_amounts'?'Justificativa sem valores monetários explícitos para conferência.':audit?.status==='requires_confirmation'?'Quantias não encontradas na execução, mantidas com ciência do responsável: '+(audit.unmatched||[]).map(x=>x.written).join(' · '):'Registro anterior sem conferência monetária automática.';
 const recordHtml=record?`<h2>Decisão efetivamente registrada</h2><div class="callout"><p><b>Responsável:</b> ${esc(record.responsible||'Não informado')} · <b>Registro:</b> ${esc(localTimestamp(record.utc))}</p><p><b>Justificativa:</b> ${esc(record.note)}</p><p><b>Riscos e verificações:</b> ${esc(record.risks||'Não detalhados no registro.')}</p><p><b>Integridade da justificativa:</b> ${esc(matchedAudit)} Esta conferência não avalia a interpretação dos valores.</p><p><b>Vínculo:</b> execução ${esc(record.run_id||'—')} · modelo ${esc(String(record.model_hash||'—').slice(0,16))}…</p><p>Limitações reconhecidas; viabilidade física não homologada.</p></div>`:'<p class="report-draft">RELATÓRIO DE ANÁLISE · ainda não há decisão registrada para esta alternativa e este experimento.</p>';
 const disclaimer='Cenário sintético de apoio à decisão, não monitoramento em tempo real. Restrições de habilitação individual, setups dependentes de sequência, buffers finitos e recursos de manutenção não foram integralmente verificados. O motor não simula refugo, retrabalho nem inspeção de qualidade. MTBF/MTTR exigem histórico de falhas não disponível.';
 const documentHtml=`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Anti-Murphy · Relatório ${esc(d.run_id||'')}</title><style>
 @page{size:A4;margin:17mm}*{box-sizing:border-box}body{margin:0;background:#E8ECEB;font-family:Arial,Helvetica,sans-serif;color:#1D292D;font-size:12px;line-height:1.5}main{max-width:900px;background:white;min-height:100vh;margin:0 auto;padding:36px 45px}header{display:flex;justify-content:space-between;gap:16px;border-bottom:4px solid #FF681B;padding-bottom:20px;margin-bottom:26px}.logo{font-size:20px;letter-spacing:.09em;font-weight:800}.mark{display:inline-block;border-left:5px solid #FF681B;padding-left:11px}.meta{font-size:11px;color:#59716A;text-align:right}h1{font-size:24px;margin:0 0 7px}h2{font-size:15px;border-bottom:1px solid #DCE5E0;margin:27px 0 13px;padding-bottom:8px}h3{font-size:14px;margin:0 0 9px}.lead{font-size:13px;color:#3E5750}.comparison-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:15px}.comparison{border:1px solid #D7E2DC;padding:15px}.comparison h3{font-size:12px}.comparison dl{display:grid;grid-template-columns:1fr auto;gap:6px;margin:0}.comparison dt{color:#56736A}.comparison dd{margin:0;text-align:right;font-weight:700}table{border-collapse:collapse;width:100%;font-size:11px}th,td{text-align:left;border-bottom:1px solid #DFE6E0;padding:9px 7px}th{background:#F1F4F1;color:#2A4540}p{margin:8px 0}.callout{border-left:3px solid #FF681B;background:#F4F6F2;padding:15px 18px;margin:16px 0}.print{display:flex;justify-content:end;padding:16px;background:#DDE6DF}.print button{background:#1D292D;border:0;color:white;padding:11px 18px;cursor:pointer}.decision-quality{border:1px solid #CEDAD8;background:#F4F7F5;padding:13px 17px;margin:12px 0}.review-warning{border-left:4px solid #FF681B}.review-heading span{display:block;color:#657D7D;font-size:9px;letter-spacing:.06em}.review-heading strong{display:block;margin-top:3px;color:#1D292D}.review-caution{color:#50686C;font-size:10px}.report-draft{background:#FFF2E8;padding:11px 14px;border-left:3px solid #FF681B}.executive-summary{background:#F1F5F1;border:1px solid #D7E2DC;border-left:4px solid #FF681B;padding:14px 17px;margin:14px 0 18px}.executive-summary>span{color:#526B64;font-size:9px;font-weight:700;letter-spacing:.08em}.executive-summary>div{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin:12px 0}.executive-summary strong{font-size:16px;color:#1D292D;line-height:1.2}.executive-summary small{display:block;font-size:9px;color:#56736A;font-weight:400;padding-top:5px}.executive-summary p{font-size:10px;color:#536D63}.foot{font-size:11px;color:#607970;margin-top:25px;line-height:1.6}@media print{body{background:white}main{padding:0;min-height:auto}.print{display:none}.comparison{break-inside:avoid}h2{break-after:avoid}}
 </style></head><body><div class="print"><button id="print-report">Imprimir ou salvar como PDF</button></div><main><header><div class="mark logo">ANTI-MURPHY</div><div class="meta">Estudo ${esc(d.run_id||'—')}<br>Projeto: ${esc(d.active_project_name||'Projeto local')}<br>Emissão: ${new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo'}).format(new Date())}</div></header>
 <h1>Análise de impacto na produção</h1><p class="lead">Posto: <b>${esc(d.spec?.station||'—')}</b> · Início da parada: <b>${h(d.spec?.start_h)} h</b> · Duração: <b>${h(d.spec?.duration_h)} h</b> · Resposta após: <b>${h(d.delay_h)} h</b></p>
 <section class="executive-summary"><span>RESULTADO DO EXPERIMENTO · EVIDÊNCIA SINTÉTICA</span><div><strong>${integer(ref?.late_orders)} → ${integer(response?.late_orders)}<small>pedidos atrasados (A → B)</small></strong><strong>${h(ref?.sla_pct)}% → ${h(response?.sla_pct)}%<small>SLA simulado</small></strong><strong>${brlExact(selected.savings)}<small>diferença econômica modelada</small></strong></div><p>Alternativa selecionada: ${esc(selected.action)}. Estes resultados não certificam viabilidade física nem economia de caixa.</p></section><h2>Comparação de cenários</h2><div class="comparison-grid">${cards('Operação nominal',base)}${cards('Falha sem resposta',ref)}${cards('Resposta selecionada',response)}</div>
 <h2>Intervenção avaliada</h2><div class="callout"><h3>${esc(selected.action)}</h3><p>${esc(selected.rationale||'Alternativa enumerada pelo motor.')}</p><p>Operação: <b>${brlExact(response?.operating_cost)}</b> + penalidades: <b>${brlExact(response?.penalty_total)}</b> + investimento modelado: <b>${brlExact(selected.investment)}</b> = custo da decisão: <b>${brlExact(selected.decision_cost)}</b>.</p><p>Referência sem intervenção: <b>${brlExact(ref?.total_cost)}</b> · Diferença líquida estimada: <b>${brlExact(selected.savings)}</b>.</p></div>
 <h2>Qualidade da escolha no conjunto enumerado</h2>${reviewHtml}${recordHtml}
 <h2>Impacto por pedido</h2><table><thead><tr><th>Pedido</th><th>Prazo</th><th>Sem resposta</th><th>Com resposta</th><th>Folga B</th><th>Condição</th></tr></thead><tbody>${rows||'<tr><td colspan="6">Detalhamento indisponível</td></tr>'}</tbody></table>
 <h2>Método econômico e indicadores</h2><p>Custos operacionais estimados por capacidade contratada (máquinas e operadores) durante o horizonte da programação; multas previstas por atraso em relação ao prazo cadastrado. O investimento modelado é somado separadamente no custo da decisão. Uma redução de makespan ou de custo modelado <strong>não é garantia de economia financeira efetiva</strong> sem verificar as parcelas evitáveis.</p><p>Folga = prazo − conclusão prevista. Folga negativa significa atraso; entre zero e 0,50 h indica atenção neste relatório. O indicador de gargalo do motor usa pontuação composta por utilização, espera e fila máxima; não demonstra, sozinho, a restrição estrutural de throughput.</p><h2>Hipóteses e limitações</h2><p>${esc(disclaimer)}</p><p>${esc((selected.restriction_reasons||[]).join(' · ')||'A conformidade industrial depende de validações externas e dos dados cadastrais reais.')}</p>
 <div class="foot">Experimento ${esc(d.run_id||'—')} · Dados do modelo local (${esc(d.source||'não informada')}). Fonte dos indicadores: resultados do motor de eventos discretos do Anti-Murphy. O relatório apresenta previsões de simulação e não constitui instrução para atuação física. Nenhuma ação foi aplicada em máquina real.</div></main></body></html>`;
 const popup=window.open('','_blank');
 if(!popup){const blob=new Blob([documentHtml],{type:'text/html;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='anti-murphy-relatorio-'+String(d.run_id||'estudo').replace(/[^a-z0-9_-]/gi,'_')+'.html';document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),5000);notify('Pop-up bloqueado. Relatório HTML salvo para abrir ou imprimir como PDF.');return;}
 popup.document.open();popup.document.write(documentHtml);popup.document.close();
 popup.document.getElementById('print-report')?.addEventListener('click',()=>popup.print());
 st.reportOpened=true;if(st.presentation)renderPresentationGuide();
}

function bindEvents(){
 dashBindEvents();
 $('presentation-toggle').onclick=togglePresentation;
 $('presentation-prev').onclick=()=>goPresentationStep(st.presentationStep-1);
 $('presentation-next').onclick=()=>{
  if(st.presentationStep===5 && !chosenRecord()){
   navigate('decisoes',{skipStack:true});
   if(!$('decision-note').value.trim()){$('decision-note').focus();notify('Descreva o motivo da escolha, reconheça os limites e registre antes de concluir a demonstração.');}
   else $('register-decision').focus();
   return;
  }
  if(st.presentationStep===5&&chosenRecord()){generateReport();return;}
  goPresentationStep(st.presentationStep+1);
 };
 $('presentation-restart').onclick=()=>goPresentationStep(0);
 $('presentation-fullscreen').onclick=async()=>{
   try{
    if(document.fullscreenElement)await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
   }catch(_error){notify('Não foi possível ativar tela cheia. Você pode usar F11 no navegador.',true);}
 };
 document.addEventListener('fullscreenchange',()=>{$('presentation-fullscreen').textContent=document.fullscreenElement?'Sair da tela cheia':'Tela cheia ⛶';});
 $('presentation-compare-view').onclick=()=>{st.presentationOverview=!st.presentationOverview;renderScene(true);};
 $('decision-draft').onclick=insertTechnicalDraft;
 $('decision-risks').addEventListener('input',()=>updateDecisionValidation());
 $('decision-external-ack').addEventListener('change',()=>updateDecisionValidation());
 $('decision-ack').addEventListener('change',()=>updateDecisionValidation());
 $('presentation-steps').addEventListener('click',event=>{const el=event.target.closest('[data-presentation-step]');if(el)goPresentationStep(Number(el.dataset.presentationStep));});
 document.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&st.presentation&&!document.querySelector('dialog[open]')&&!document.fullscreenElement){st.presentation=false;renderPresentationGuide();}
  if(!st.presentation||event.altKey||event.ctrlKey||event.metaKey||['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName))return;
  if(event.key==='ArrowRight'){event.preventDefault();goPresentationStep(Math.min(5,st.presentationStep+1));}
  if(event.key==='ArrowLeft'){event.preventDefault();goPresentationStep(Math.max(0,st.presentationStep-1));}
 });
 $('report-generate').addEventListener('click',generateReport);
 $('decision-report').addEventListener('click',generateReport);
 $('guide-start').addEventListener('click',startTour);
 $('help-button').addEventListener('click',()=>openHelp(st.view));
 $('guide-close').addEventListener('click',closeHelp);
 $('guide-backdrop').addEventListener('click',closeHelp);
 $('guide-tour-from-help').addEventListener('click',startTour);
 $('tour-close').addEventListener('click',endTour);
 $('tour-previous').addEventListener('click',()=>{if(st.tourStep>0){st.tourStep--;renderTour();}});
 $('tour-next').addEventListener('click',()=>{if(st.tourStep>=tutorial.length-1)endTour();else {st.tourStep++;renderTour();}});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'){if(st.tourStep>=0)endTour();if(!$('guide-panel').hidden)closeHelp();}});
 document.addEventListener('click',event=>{
  const button=event.target.closest('[data-metric]');if(button){st.metricName=button.dataset.metric;openHelp('metric');}
  const area=event.target.closest('[data-area-help]');if(area)openHelp(area.dataset.areaHelp);
 });
 $$('.section-intro').forEach(section=>{
  const view=section.closest('.view')?.dataset.view;
  if(!helpCatalog[view])return;
  const dest=section.querySelector('.intro-tools')||section;
  const b=document.createElement('button');b.type='button';b.className='context-link';b.dataset.areaHelp=view;b.textContent='Como usar esta área';
  dest.appendChild(b);
 });

 $$('.rail-item').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.nav)));
 $('go-analysis').onclick=()=>navigate('analise');
 $('go-dashboards').onclick=()=>navigate('paineis');
 $('quick-incident').onclick=()=>navigate('analise');
 $('incident-workflow').onclick=e=>{
  const b=e.target.closest('[data-incident-go]');if(!b||!st.data)return;
  if(b.dataset.incidentGo==='compare'){st.scene='split';st.t=informativeComparisonTime();st.playing=false;renderScene(true);return;}
  if(b.dataset.incidentGo==='scene'){
   st.scene='incident';st.station=st.data.spec?.station||st.station;st.t=Number(st.data.spec?.start_h)||0;st.focus=true;st.playing=false;renderScene(true);$('factory-viewport').scrollIntoView({block:'center',behavior:'smooth'});return;
  }
  if(b.dataset.incidentGo==='orders'){
   const imp=st.data.alternatives?.find(a=>a.signature===st.data.selected)?.order_impacts||[];
   st.order=imp.find(x=>x.late_before)?.id||st.data.orders[0]?.id||null;st.scene='incident';st.playing=false;renderScene(true);$('orders-row').scrollIntoView({block:'center',behavior:'smooth'});
  }
 };
 $('event-log').addEventListener('click',event=>{
  const item=event.target.closest('[data-event-time]');if(!item)return;
  const t=Number(item.dataset.eventTime);if(!Number.isFinite(t))return;
  st.playing=false;st.t=Math.min(horizon(),Math.max(0,t));
  if(st.data?.stations?.[item.dataset.eventStation])st.station=item.dataset.eventStation;
  renderScene(true);
 });
 $('inspect-alternatives').onclick=()=>navigate('analise');
 $('see-order-analysis').onclick=()=>navigate('analise');
 $('analysis-recalculate').onclick=calculate;
 $$('#advanced-tabs button').forEach(b=>b.onclick=()=>{st.advanced=b.dataset.advanced;st.advancedIntent=(st.advancedIntent||0)+1;renderAdvancedInfo();});
 $('advanced-run').onclick=runAdvanced;
 ['goal-value','throughput-value'].forEach(id=>{for(const event of ['input','change'])$(id).addEventListener(event,()=>{st.labIntent=(st.labIntent||0)+1;renderLabInfo();});});
 ['advanced-station','advanced-resource','advanced-sla'].forEach(id=>{for(const event of ['input','change'])$(id).addEventListener(event,()=>{st.advancedIntent=(st.advancedIntent||0)+1;renderAdvancedInfo();});});
 document.addEventListener('click',event=>{const button=event.target.closest('[data-run-context]');if(!button)return;if(button.dataset.runContext==='lab')runLab();if(button.dataset.runContext==='advanced')runAdvanced();});
 $('advanced-export').onclick=()=>{if(!st.advancedResult)return;download(JSON.stringify({
  produto:'Anti-Murphy',formato:'analise_avancada',versao:'1.0',
  experimento:st.advancedResult.experiment_id,proveniencia:st.advancedResult.provenance,
  status:analysisHistory.status(st.advancedResult).code,fonte:st.advancedResult.provenance?.source||'',
  horario_exportacao:new Date().toISOString(),resultado:st.advancedResult
 },null,2),`anti_murphy_${st.advancedResult.mode}_${st.advancedResult.experiment_id}.json`)};
 $('advanced-to-analysis').onclick=()=>navigate('analise');
 $('advanced-go-model').onclick=()=>navigate('modelo');
 $('advanced-go-decisions').onclick=()=>navigate('decisoes');
 $('advanced-go-lab').onclick=()=>navigate('laboratorio');
 $$('#scene-tabs button').forEach(b=>b.onclick=()=>{st.scene=b.dataset.scene;st.playing=false;renderScene(true)});
 $('play-button').onclick=()=>{if(st.t>=horizon()-.001)st.t=0;st.playing=!st.playing;updateScene()};
 $('reset-time').onclick=()=>{st.playing=false;st.t=0;updateScene()};
 $('speed-control').onchange=e=>{st.speed=Number(e.target.value)||1;updateScene()};
 $('pause-on-event').onchange=e=>{st.pauseOnEvent=e.target.checked;updateScene()};
 $('timeline-range').oninput=e=>{st.t=horizon()*Number(e.target.value)/10000;st.playing=false;updateScene()};
 $('wipe-range').oninput=e=>{st.wipe=Number(e.target.value);renderScene()};
 $('stage-fullscreen').onclick=async()=>{
 const node=document.querySelector('.canvas-workspace');
 try{
  if(document.fullscreenElement)await document.exitFullscreen();
  else await node.requestFullscreen();
 }catch(e){notify('O navegador não permitiu ampliar a visualização.',true)}
 };
 document.addEventListener('fullscreenchange',()=>{
  const on=!!document.fullscreenElement;
  $('stage-fullscreen').textContent=on?'Sair da tela ampliada':'Ampliar mapa ↗';
  renderScene();
 });
 $('station-inspector').addEventListener('click',event=>{
  const focus=event.target.closest('[data-inspect-focus]');
  if(focus){st.focus=!st.focus;st.lastInspectorPaint=0;renderScene();return;}
  const murphy=event.target.closest('[data-inspect-murphy]');
  if(murphy){
   const current=st.station;
   navigate('decisoes');
   // The local assistant reads the current experiment, not an invented station-specific forecast.
   askAssistant(`Qual é o gargalo da operação e quais pedidos estão em risco? O posto selecionado para investigação é ${current}.`);
   return;
  }
  const schedule=event.target.closest('[data-open-schedule]');
  if(schedule){$('schedule-panel').open=true;$('schedule-panel').scrollIntoView({block:'nearest',behavior:'smooth'});return;}
  const trace=event.target.closest('[data-trace-time]');
  if(trace){st.station=trace.dataset.traceStation||st.station;st.t=Math.min(horizon(),Math.max(0,Number(trace.dataset.traceTime)||0));st.playing=false;renderScene(true);return;}
  const pick=event.target.closest('[data-inspect-order]');
  if(pick){st.order=pick.dataset.inspectOrder;st.focus=true;renderScene(true);}
 });
 $('zoom-in').onclick=()=>{st.zoom=Math.min(1.7,st.zoom+.15);renderScene()};
 $('zoom-out').onclick=()=>{st.zoom=Math.max(.8,st.zoom-.15);if(st.zoom<=1)st.focus=false;renderScene()};
 $$('#model-tabs button').forEach(b=>b.onclick=()=>{st.modelTab=b.dataset.modelTab;renderModel()});
 $('add-model-row').onclick=()=>{
  if(st.modelTab==='stations'){
   let sid='NOVO_POSTO',i=1;while(st.editing.stations[sid])sid='NOVO_POSTO_'+i++;
   st.editing.stations[sid]={nome:'Novo posto',setor:'Produção',maquinas:1,operadores:1,operadores_por_maquina:1,eficiencia_operador:.95,disponibilidade:.96,custo_operador_h:25,custo_maquina_h:40,setup_min:10};
  } else {let id='OP-NOVA',i=1;while(st.editing.orders.some(o=>o.id===id))id='OP-NOVA-'+i++;
   st.editing.orders.push({id,cliente:'Cliente',produto:'Peça',quantidade:5,prazo_h:12,multa_hora:200,prioridade:2,release_h:0,route:[[Object.keys(st.editing.stations)[0],5]]});
  }renderModel();
 };
 $('route-close').onclick=()=>$('route-dialog').close();
 $('route-cancel').onclick=()=>$('route-dialog').close();
 $('route-add').onclick=()=>{routeEditorSteps.push([Object.keys(st.editing.stations)[0]||'',5]);renderRouteSteps();};
 $('route-apply').onclick=commitRouteEditor;
 $('model-save').onclick=saveModel;
 $('reset-model').onclick=async()=>{if(!confirm('Restaurar o exemplo sintético? Suas alterações locais serão substituídas.'))return;try{await perform(api('/api/reset','POST',{}),'Modelo de exemplo restaurado.');st.editing=null;st.scene='incident';st.t=0;navigate('modelo')}catch(_e){}};
 $('model-import-button').onclick=()=>$('model-file').click();
 $('model-file').onchange=e=>{if(e.target.files?.[0])importModel(e.target.files[0]);e.target.value=''};
 $('header-export').onclick=async()=>{try{const r=await fetch('/api/model/export');if(!r.ok)throw Error('Exportação indisponível');download(await r.text(),'anti_murphy_modelo.json')}catch(e){notify(e.message,true)}};
 $$('#lab-tabs button').forEach(b=>b.onclick=()=>{st.lab=b.dataset.lab;st.labIntent=(st.labIntent||0)+1;st.labVisible=null;renderLabInfo()});
 $('run-lab').onclick=runLab;
 $('register-decision').onclick=saveDecision;
 $('decision-note').addEventListener('input',()=>{$('decision-external-ack').checked=false;updateDecisionValidation();});
 $('decision-ack').addEventListener('change',()=>updateDecisionValidation());
 $('assistant-form').onsubmit=e=>{e.preventDefault();askAssistant($('assistant-input').value)};
 $$('[data-question]').forEach(b=>b.onclick=()=>askAssistant(b.dataset.question));
 $('assistant-messages').addEventListener('click',event=>{
  const button=event.target.closest('[data-assistant-nav]');if(!button)return;
  if(button.dataset.assistantNav==='paineis')dashUI.tab='desempenho';
  if(button.dataset.assistantNav==='simulacao'){
    const text=button.closest('.assistant-message')?.querySelector('div')?.textContent||'';
    const match=text.match(/\bOP-[A-Za-z0-9-]+\b/);
    if(match&&st.data?.orders?.some(o=>o.id===match[0]))st.order=match[0];
  }
  navigate(button.dataset.assistantNav);
 });
 $('refresh-history').onclick=loadHistory;
 // Contextual guidance replaces the former generic help modal; it remains in the markup as reference documentation.
 $('project-manager').onclick=showProjects;
 $('project-create').onclick=createProject;
 $('project-rename').onclick=renameProject;
 $('experiment-save').onclick=saveExperiment;
 $('experiment-compare').onclick=compareExperiments;
 $$('[data-close]').forEach(b=>b.onclick=()=>$((b.dataset.close)).close());
 $('skip-intro').onclick=()=>hideSplash();
 window.addEventListener('popstate',()=>{st.navStack=[];navigate(location.hash.slice(1),{fromBrowser:true})});
 $('back-home').onclick=()=>{st.navStack=[];navigate('simulacao',{skipStack:true})};
 $('back-previous').onclick=goBack;
}
let bootTime=performance.now();let lastRead=0;
function hideSplash(){const el=$('splash');if(!el)return;el.classList.add('hide');try{sessionStorage.setItem('am-boot','1')}catch(_e){}setTimeout(()=>el.remove(),900)}
function animate(now){
 if(st.playing&&st.data&&st.view==='simulacao'){
  const elapsed=Math.max(0,Math.min(.1,(now-st.lastFrame)/1000));
  const proposed=Math.min(horizon(),st.t+playbackAdvance(elapsed));
  const marker=st.pauseOnEvent?pauseMarkers().find(m=>m.t>st.t+1e-8&&m.t<=proposed+1e-8):null;
  if(marker){st.t=marker.t;st.playing=false;updateScene();lastRead=now;notify(`${marker.label} em ${time(marker.t)}. Reprodução pausada para inspeção.`);}
  else st.t=proposed;
  if(st.t>=horizon()-1e-9){st.playing=false;updateScene();lastRead=now;}
  if(now-lastRead>115){updateScene();lastRead=now;}
 }
 st.lastFrame=now;
 requestAnimationFrame(animate);
}
async function main(){
 bindEvents();
 try{
  busy(true,'Abrindo projeto…');
  applyData(await api('/api/state'));
  const route=location.hash.slice(1)||'simulacao';navigate(route,{fromBrowser:true});
  busy(false);
  let first=true;try{first=!sessionStorage.getItem('am-boot')}catch(_e){}
  setTimeout(hideSplash,first?Math.max(0,1550-(performance.now()-bootTime)):120);
  st.playing=false; // Make the first frame inspectable before playing.
 }catch(e){busy(false);notify('Não foi possível abrir o projeto: '+e.message,true);hideSplash()}
 requestAnimationFrame(animate);
}
main();
})();
