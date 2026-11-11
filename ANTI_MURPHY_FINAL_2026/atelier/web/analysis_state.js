/* AM-05: page-local experiment history and one validity rule for UI/exports. */
(function(root){'use strict';
function canonical(value){
 if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
 if(value && typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
 return JSON.stringify(value);
}
function createStore(current){
 let sequence=0;const entries=[];
 const list=(scope,mode)=>entries.filter(e=>e.scope===scope&&e.result.mode===mode).sort((a,b)=>b.id-a.id);
 const find=result=>entries.find(e=>e.result===result);
 function status(result){
  const p=result?.provenance;
  if(!p?.context_key||!p.context_signature)return {code:'desconhecido',label:'Histórico sem origem verificável'};
  const now=current(),token=now.contexts?.[p.context_key]?.context_signature;
  if(!token||token!==p.context_signature||canonical(p.inputs||{})!==canonical(now.inputs(p.scope,result.mode)))return {code:'desatualizado',label:'Desatualizado · outra configuração'};
  const entry=find(result);
  return entry&&list(entry.scope,result.mode).some(e=>e.id>entry.id)?{code:'historico',label:'Histórico · corresponde à configuração atual'}:{code:'atual',label:'Atual'};
 }
 return {entries,list,status,find,begin:()=>++sequence,add(result,scope,id){
  const entry={result,scope,id:id??++sequence};sequence=Math.max(sequence,entry.id);entries.push(entry);return entry;
 }};
}
const api={canonical,createStore};if(typeof module==='object'&&module.exports)module.exports=api;root.AMAnalysisState=api;
})(typeof window==='object'?window:globalThis);
