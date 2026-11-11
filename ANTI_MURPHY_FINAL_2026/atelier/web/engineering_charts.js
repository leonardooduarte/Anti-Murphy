/* Anti-Murphy / Engineering charts. No dependencies, no simulated data on the client.
   Every plotted value is copied from a Python DES response; interpolation is visual only.
   SVG, keyboard-focusable points, metric selector and source table/CSV support.
*/
(function(){'use strict';
const state=new Map();
const safe=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const valid=v=>v!==null&&v!==undefined&&v!==''&&Number.isFinite(Number(v));
const N=(v)=>Number(v);
const fnum=(v,d=2)=>{
 if(!valid(v))return '—';const n=N(v);
 if(n!==0 && Math.abs(n)<.5*10**(-d))return Math.abs(n)<1e-6?n.toExponential(3).replace('.',','):n.toLocaleString('pt-BR',{maximumSignificantDigits:4});
 return n.toLocaleString('pt-BR',{maximumFractionDigits:d,minimumFractionDigits:d});
};
const fc=(v)=>valid(v)?new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:2}).format(N(v)):'—';
function fmt(v,unit){if(!valid(v))return '—';if(unit==='R$')return fc(v);if(unit==='%')return fnum(v,1)+'%';if(unit==='p.p.')return fnum(v,1)+' p.p.';if(unit==='h')return fnum(v,2)+' h';if(unit==='un/h')return fnum(v,3)+' un/h';if(unit==='un')return fnum(v,0)+' un';if(unit==='R$/un')return fc(v)+'/un';if(unit==='×')return fnum(v,2)+'×';return fnum(v,2);}
const configs={
 'lab:duration':{heading:'Sensibilidade à duração da parada',intro:'Variação isolada da duração; a trajetória mostra a resposta do modelo, não a probabilidade de falha.',x:'duration_h',xLabel:'Duração da parada (h)',kind:'line',metrics:[['makespan_h','Término previsto','h'],['sla_pct','Pedidos no prazo','%'],['total_cost','Operação + multas','R$'],['late_orders','Pedidos atrasados','un']]},
 'lab:dispatch':{heading:'Comparação de políticas de despacho',intro:'Mesma falha e mesma semente. Compare cada indicador isoladamente; não existe uma política vencedora em todas as dimensões.',x:'label',xLabel:'Regra de sequenciamento',kind:'dots',metrics:[['total_cost','Operação + multas','R$'],['makespan_h','Término previsto','h'],['sla_pct','Pedidos no prazo','%'],['late_orders','Pedidos atrasados','un']]},
 'lab:robustness':{heading:'Resultado econômico por semente',intro:'Barras à direita de zero representam economia positiva; à esquerda, perda. Seis sementes sintéticas pareadas.',x:'seed',xLabel:'Semente',kind:'diverging',metrics:[['net_saving','Economia líquida','R$'],['cost_saving','Redução bruta de custo','R$'],['sla_gain_pp','Variação de SLA','p.p.'],['makespan_gain_h','Antecipação do término','h']]},
 'lab:goal':{heading:'Alternativas que atendem à meta',intro:'Resultados filtrados entre alternativas já enumeradas. Não há garantia de ótimo global.',x:'label',xLabel:'Alternativa',kind:'dots',metrics:[['total_cost','Custo total da decisão','R$'],['sla_pct','Pedidos no prazo','%'],['makespan_h','Término previsto','h'],['savings','Economia estimada','R$']]},
 'lab:stress':{heading:'Resultados das perturbações da carteira',intro:'Cada ponto é um dos 16 cenários sintéticos; não são frequências medidas de incidentes.',x:'sla_pct',y:'unit_cost',xLabel:'Pedidos no prazo (%)',kind:'scatter',metrics:[['unit_cost','Custo por unidade','R$/un'],['makespan_h','Término previsto','h'],['throughput_h','Throughput','un/h']]},
 'lab:capacity':{heading:'Capacidade adicional e desempenho',intro:'Busca discreta sobre a operação nominal. Recursos adicionais não têm custo de contratação ou aquisição modelado.',x:'label',xLabel:'Cenário de capacidade',kind:'dots',metrics:[['throughput_h','Throughput','un/h'],['unit_cost','Custo por unidade','R$/un'],['sla_pct','Pedidos no prazo','%'],['makespan_h','Término previsto','h']]},
 'advanced:diagnostic':{heading:'Fila e espera por posto',intro:'Fila máxima e espera média são evidências diferentes; nenhum indicador isolado prova a restrição estrutural.',x:'Posto',xLabel:'Posto produtivo',kind:'dots',metrics:[['Fila máx.','Maior fila registrada','un'],['Espera média (min)','Espera média','min'],['Utilização máquina (%)','Utilização da máquina','%']]},
 'advanced:opportunities':{heading:'Efeito das oportunidades enumeradas',intro:'Os efeitos são calculados no cenário nominal. Variações negativas de custo ou makespan podem ser favoráveis.',x:'Ação',xLabel:'Alternativa de melhoria',kind:'diverging',maxBars:14,metrics:[['Throughput Δ (%)','Variação de throughput','%'],['Custo/un Δ (%)','Variação de custo/un','%',-1],['Makespan Δ (%)','Variação de término','%',-1],['SLA Δ (p.p.)','Variação de SLA','p.p.'],['Score de oportunidade','Índice comparativo','']]},
 'advanced:sensitivity':{heading:'Ganho marginal de recursos',intro:'Incrementos discretos em um único posto na operação nominal; o ganho marginal indica possível saturação.',x:'Adição',xLabel:'Recursos acrescentados (un)',kind:'line',metrics:[['Throughput','Throughput','un/h'],['Ganho marginal TP','Ganho marginal','un/h'],['Custo/un','Custo por unidade','R$/un'],['SLA','Pedidos no prazo','%'],['Makespan','Término previsto','h']]},
 'advanced:demand':{heading:'Limite de atendimento à demanda',intro:'Faixa analisada de 1,0× a 1,6×. Identifique a primeira condição abaixo da meta de SLA.',x:'Demanda x',xLabel:'Multiplicador de demanda',kind:'line',metrics:[['SLA','Pedidos no prazo','%'],['Throughput','Throughput','un/h'],['Makespan','Término previsto','h']]},
 'advanced:uncertainty':{heading:'Dispersão das execuções Monte Carlo',intro:'Exibe todas as 12 observações. A amostra é exploratória e não fornece intervalo de confiança industrial calibrado.',x:'run',xLabel:'Execução',kind:'dots',metrics:[['makespan','Término previsto','h'],['sla','Pedidos no prazo','%'],['unit_cost','Custo por unidade','R$/un'],['throughput','Throughput','un/h']]},
 'advanced:recovery':{heading:'Alternativas de recuperação',intro:'Recuperação sobre o cenário de falha. Não inclui custos de investimento nem verifica todas as restrições físicas.',x:'Ação',xLabel:'Alternativa de recuperação',kind:'dots',metrics:[['SLA','Pedidos no prazo','%'],['SLA Δ (p.p.)','Variação de SLA','p.p.'],['Throughput Δ (%)','Variação do throughput','%'],['Custo/un','Custo por unidade','R$/un'],['Makespan','Término previsto','h']]}
};
configs['dash:uncertainty']=configs['advanced:uncertainty'];
/* A dozen full scenario names cannot be read on a 920px categorical axis.
   Draw discrete numeric identifiers and expose the complete descriptions alongside.
   The identifiers are based on the actual Python result order, never on synthetic data. */
function indexedAxis(rows,cfg){return cfg.kind==='dots' && cfg.x==='label' && rows.length>=7;}
function indexedLegend(rows,cfg){
 if(!indexedAxis(rows,cfg))return '';
 const points=rows.map((r,i)=>{
  const label=String(r[cfg.x]??`Cenário ${i+1}`);
  return `<button type="button" class="eng-index-chip" data-eng-point="${i}" aria-label="Consultar cenário ${i+1}: ${safe(label)}" aria-pressed="false" title="${safe(label)}"><b>${String(i+1).padStart(2,'0')}</b><span>${safe(label)}</span></button>`;
 }).join('');
 return `<div class="eng-index-legend" role="group" aria-label="Legenda dos cenários calculados"><div class="eng-index-legend-header"><strong>Cenários do experimento</strong><small>Identificadores do eixo horizontal · selecione um cenário para consultar os resultados</small></div><div class="eng-index-grid">${points}</div></div>`;
}

function dataOf(result,scope){return scope==='lab'?result.points||result.pairs||[]:result.rows||result.stations||[];}
function ticks(low,high,n=4){const v=[];for(let i=0;i<=n;i++)v.push(low+(high-low)*i/n);return v;}
function range(values,opt={}){
 let arr=values.filter(Number.isFinite);if(valid(opt.target))arr.push(Number(opt.target));
 if(!arr.length)return [0,1];let low=Math.min(...arr),high=Math.max(...arr);
 if(opt.percent){low=Math.min(0,low);high=Math.max(100,high)}
 if(opt.diverging){low=Math.min(low,0);high=Math.max(high,0);const a=Math.max(Math.abs(low),Math.abs(high),.01);return [-a*1.12,a*1.12];}
 if(low===high){const d=Math.max(Math.abs(low)*.08,.25);low-=d;high+=d}
 const pad=(high-low)*.12;low-=pad;high+=pad;
 if(opt.zeroFloor && low>0)low=0;
 if(opt.percent){low=Math.max(0,low);high=Math.min(100,high)}
 return low>=high?[low,low+1]:[low,high];
}
function baseSvg(title,unit,xLabel,content,width=920,height=340){return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${safe(title)}, unidade ${safe(unit)}, eixo horizontal ${safe(xLabel)}" class="eng-svg"><title>${safe(title)} (${safe(unit)})</title>${content}</svg>`;}
function plot(rows,cfg,metric,result){
 const [field,title,unit,favorable=1]=metric;
 const entries=rows.map((r,i)=>({...r,__index:i,__val:valid(r[field])?N(r[field]):null})).filter(r=>r.__val!==null);
 if(!entries.length)return baseSvg(title,unit,'Sem amostra', '<text x="30" y="80" fill="#34545B">Sem observações viáveis para este indicador; consulte a tabela e os motivos.</text>');
 const kind=cfg.kind==='scatter'?'scatter':cfg.kind;
 if(kind==='diverging'||(cfg===configs['lab:goal']&&field==='savings'))return diverging(entries,cfg,metric);
 const W=920,H=350,L=86,R=35,T=38,B=65,iw=W-L-R,ih=H-T-B;
 let xs=[],plotX,lab,unitsX;
 if(kind==='line' || kind==='scatter'){
  const numeric=entries.every(r=>valid(r[cfg.x]));
  if(numeric){xs=entries.map(r=>N(r[cfg.x]));const xmin=Math.min(...xs),xmax=Math.max(...xs);plotX=r=>xmin===xmax?L+iw/2:L+(N(r[cfg.x])-xmin)/(xmax-xmin)*iw;unitsX=()=>((cfg.x==='Adição'||xmin===xmax)?[...new Set(xs)]:ticks(xmin,xmax,5)).map(x=>[xmin===xmax?L+iw/2:L+(x-xmin)/(xmax-xmin)*iw,fmt(x,cfg.kind==='scatter'?'%':cfg.x==='Demanda x'?'×':cfg.x==='duration_h'?'h':cfg.x==='Adição'?'un':'')]);}
 }
 if(!plotX){plotX=r=>L+((r.__index+.5)/rows.length)*iw;unitsX=()=>entries.map(r=>[plotX(r),String(r[cfg.x]??r.__index+1),r.__index]);}
 const target=cfg===configs['advanced:demand'] && field==='SLA'?result.min_sla: (cfg===configs['lab:capacity']&&field==='sla_pct'&&valid(result.target_sla)?result.target_sla:null);
 const vals=entries.map(r=>r.__val);const [lo,hi]=range(vals,{percent:unit==='%',target});
 const yy=v=>T+(hi-v)/(hi-lo)*ih;
 const grid=ticks(lo,hi).map(v=>`<line x1="${L}" y1="${yy(v)}" x2="${W-R}" y2="${yy(v)}" class="eng-grid"/><text class="eng-tick" text-anchor="end" x="${L-11}" y="${yy(v)+4}">${safe(fmt(v,unit))}</text>`).join('');
 const xaxis=unitsX().filter((d,i,all)=>all.length<=12 || i%Math.ceil(all.length/9)===0 || i===all.length-1).map(([x,label,sourceIndex],i)=>{
  const axisLabel=indexedAxis(rows,cfg)?String(Number(sourceIndex??i)+1).padStart(2,'0'):(String(label).length>14?String(label).slice(0,12)+'…':String(label));
  return `<text class="eng-tick eng-x-tick ${indexedAxis(rows,cfg)?'eng-x-index':''}" x="${x}" y="${H-B+22}" text-anchor="middle">${safe(axisLabel)}</text>`;
 }).join('');
 const sorted=entries.slice().sort((a,b)=>plotX(a)-plotX(b));
 const path=(kind==='line' && sorted.length>1)?`<polyline class="eng-series-line" points="${sorted.map(r=>`${plotX(r)},${yy(r.__val)}`).join(' ')}"/>`:'';
 const line=valid(target)?`<line class="eng-target" x1="${L}" y1="${yy(Number(target))}" x2="${W-R}" y2="${yy(Number(target))}"/><text class="eng-target-label" x="${W-R-4}" y="${yy(Number(target))-7}" text-anchor="end">Meta ${safe(fmt(target,'%'))}</text>`:'';
 const dots=entries.map(r=>{
  const x=plotX(r),y=yy(r.__val),bad=(valid(target) && r.__val<Number(target))||((field==='net_saving'||field==='cost_saving')&&r.__val<0);
  const label=String(r.label||r['Ação']||r['Posto']||r.run||r.__index+1);
  return `<g class="eng-point ${bad?'bad':''} ${r.goal_met===true?'goal':r.goal_met===false?'bad':''}" role="button" tabindex="0" data-eng-point="${r.__index}" aria-label="${safe(label)}, ${safe(title)} ${safe(fmt(r.__val,unit))}" transform="translate(${x} ${y})"><circle r="${kind==='scatter'?7.3:7.1}"/><title>${safe(label)} · ${safe(fmt(r.__val,unit))}${kind==='scatter'&&cfg.y?' · SLA '+safe(fmt(r.sla_pct,'%')):''}</title></g>`;
 }).join('');
 const caption=`<text class="eng-axis-title" x="${W-R}" y="${H-14}" text-anchor="end">${safe(cfg.xLabel)}</text><text class="eng-axis-title" x="${L}" y="17">${safe(title)} (${safe(unit)})</text>`;
 return baseSvg(title,unit,cfg.xLabel,grid+line+path+dots+xaxis+caption,W,H);
}
function diverging(entries,cfg,metric){
 const [field,title,unit,favorable=1]=metric;
 const visible=entries.slice(0,cfg.maxBars||24);
 const W=940,H=Math.max(240,75+visible.length*37),L=260,R=98,T=30,B=40;
 const [low,high]=range(entries.map(x=>x.__val),{diverging:true});
 const xp=v=>L+(v-low)/(high-low)*(W-L-R),xzero=xp(0);
 const lines=visible.map((r,i)=>{
  const y=T+i*37+13,x=xp(r.__val),left=Math.min(x,xzero),w=Math.max(1,Math.abs(x-xzero));
  const good=(r.__val*favorable>=0);const name=String(r.label??r['Ação']??r.seed??i+1);
  return `<g class="eng-diverge-row ${good?'good':'bad'}" role="button" tabindex="0" data-eng-point="${r.__index}" aria-label="${safe(name)}, ${safe(title)} ${safe(fmt(r.__val,unit))}"><text x="${L-13}" y="${y+4}" text-anchor="end" class="eng-bar-name">${safe(name.length>34?name.slice(0,32)+'…':name)}</text><rect class="eng-zero-backing" x="${L}" y="${y-10}" width="${W-L-R}" height="20"/><rect class="eng-diverge-bar" x="${left}" y="${y-7}" width="${w}" height="14" rx="2"/><text class="eng-bar-value" x="${r.__val>=0?x+8:x-8}" y="${y+4}" text-anchor="${r.__val>=0?'start':'end'}">${safe(fmt(r.__val,unit))}</text><title>${safe(name)} · ${safe(fmt(r.__val,unit))}</title></g>`;
 }).join('');
 const xref=`<line class="eng-zero-line" x1="${xzero}" y1="${T-13}" x2="${xzero}" y2="${H-B+8}"/><text class="eng-axis-title" x="${xzero}" y="${H-12}" text-anchor="middle">0 · referência</text>`;
 const caption=`<text class="eng-axis-title" x="${L}" y="16">${safe(title)} (${safe(unit)})</text>`;
 const note=entries.length>visible.length?`<p class="eng-truncated">Exibindo ${visible.length} de ${entries.length} alternativas. Todos os resultados continuam na tabela e no CSV.</p>`:'';
 return baseSvg(title,unit,'Valor com sinal',lines+xref+caption,W,H)+note;
}
function summary(rows,cfg,metric,result){
 const [key,title,unit]=metric;const validRows=rows.filter(r=>valid(r[key]));
 if(!validRows.length)return '';
 const values=validRows.map(r=>Number(r[key]));const min=Math.min(...values),max=Math.max(...values),avg=values.reduce((a,b)=>a+b,0)/values.length;
 const meta=(cfg===configs['advanced:demand'] && key==='SLA' && valid(result.min_sla))?`<div><span>Meta cadastrada</span><strong>${fmt(result.min_sla,'%')}</strong></div>`:'';
 return `<div class="eng-stats"><div><span>Observações</span><strong>${validRows.length}</strong></div><div><span>Mínimo</span><strong>${safe(fmt(min,unit))}</strong></div><div><span>Média aritmética</span><strong>${safe(fmt(avg,unit))}</strong></div><div><span>Máximo</span><strong>${safe(fmt(max,unit))}</strong></div>${meta}</div>`;
}
function selectedDetail(row,cfg,metric){
 const [field,title,unit]=metric;
 const label=String(row.label??row['Ação']??row['Posto']??row.run??row.seed??`Observação ${row.__index+1}`);
 const primary=valid(row[field])?fmt(row[field],unit):'—';
 const other=cfg.metrics.filter(m=>m[0]!==field&&valid(row[m[0]])).slice(0,3);
 return `<div class="eng-selection-title"><span>CENÁRIO SELECIONADO</span><strong>${safe(label)}</strong></div><div class="eng-selection-values"><div class="eng-selection-primary"><small>${safe(title)}</small><b>${safe(primary)}</b></div>${other.map(m=>`<div><small>${safe(m[1])}</small><b>${safe(fmt(row[m[0]],m[2]))}</b></div>`).join('')}</div><p>Valores da análise de origem; confira o estado e os parâmetros identificados acima. Os campos completos permanecem na tabela e no CSV.</p>`;
}
function fullTable(rows){if(!rows.length)return '<p>Sem resultados detalhados.</p>';
 const keys=Object.keys(rows[0]).filter(k=>!k.startsWith('__'));
 return `<div class="eng-table-scroll"><table class="eng-table"><thead><tr>${keys.map(k=>`<th>${safe(k)}</th>`).join('')}</tr></thead><tbody>${rows.map((r,i)=>`<tr data-eng-row="${i}">${keys.map(k=>`<td>${safe(r[k]===null?(r.feasible===false?'Não calculado':'—'):typeof r[k]==='number'?fnum(r[k],3):r[k])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
function csv(rows){if(!rows.length)return '';
 const keys=Object.keys(rows[0]).filter(k=>!k.startsWith('__'));
 const cell=v=>{
  let text=v===null||v===undefined?'':typeof v==='number'?String(v).replace('.',','):String(v);
  if(/^[\s]*[=+\-@\t\r]/.test(text) && typeof v==='string')text="'"+text;
  return '"'+text.replaceAll('"','""')+'"';
 };
 return '\ufeff'+[keys.map(cell).join(';'),...rows.map(r=>keys.map(k=>cell(r[k])).join(';'))].join('\r\n');
}
function downloadCsv(rows,scope,key,result){
 const origin=result?.provenance;
 const status=window.antiMurphyResultStatus?.(result)||{code:'desconhecido',label:'Origem não verificável'};
 const clean=value=>String(value??'').replace(/[\r\n]/g,' ');
 const hdr=origin?`# Projeto: ${clean(origin.project_name||origin.project_id)} (${clean(origin.project_id)}); Execução: ${origin.run_id}; Assinatura: ${origin.signature}; Calculado em: ${origin.calculated_at}; Estado na exportação: ${status.code}; Entradas: ${JSON.stringify(origin.inputs||{})}\r\n`:'# Estado na exportação: desconhecido\r\n';
 const sample=result?.sample||(result?.summary?.viable_runs!==undefined?result.summary:null);
 const sampling=sample?` ; Amostra: ${sample.viable_runs} viáveis de ${sample.runs}; Inviáveis: ${sample.infeasible_runs}; Estatísticas: somente viáveis`:'';
 const metadata='"'+(hdr.trimEnd()+sampling).replaceAll('"','""')+'"\r\n';
 const blob=new Blob(['\ufeff'+metadata+csv(rows).replace(/^\ufeff/,'')],{type:'text/csv;charset=utf-8'}),u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=`anti_murphy_${scope}_${key}.csv`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),500);
}
function downloadSvg(scope){
 const suite=document.querySelector(`.eng-suite[data-eng-scope="${scope}"]`);
 const svg=suite?.querySelector('svg.eng-svg');const item=state.get(scope);
 if(!svg||!item)return;
 const clone=svg.cloneNode(true);clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
 const pr=item.result.provenance||{},status=window.antiMurphyResultStatus?.(item.result)||{code:'desconhecido',label:'Origem não verificável'};
 const view=svg.getAttribute('viewBox')||'0 0 920 350',parts=view.split(/\s+/).map(Number),width=parts[2]||920,height=parts[3]||350;
 // Keep origin and validity visibly inside the exported figure, not only metadata.
 const plot=document.createElementNS('http://www.w3.org/2000/svg','g');
 plot.setAttribute('transform','translate(0 98)');
 while(clone.firstChild)plot.appendChild(clone.firstChild);
 clone.appendChild(plot);clone.setAttribute('viewBox',`${parts[0]||0} ${parts[1]||0} ${width} ${height+98}`);
 clone.setAttribute('width',width);clone.setAttribute('height',height+98);
 const lines=[`ESTADO: ${status.code.toUpperCase()} · ${status.label}`,`Projeto: ${pr.project_name||pr.project_id||'?'} (${pr.project_id||'?'}) · ${pr.calculated_at||''}`,`Entradas: ${JSON.stringify(pr.inputs||{})} · Assinatura: ${pr.signature||'?'}`];
 const sample=item.result.sample||(item.result.summary?.viable_runs!==undefined?item.result.summary:null);
 if(sample)lines.push(`Amostra: ${sample.viable_runs} viáveis de ${sample.runs}; ${sample.infeasible_runs} inviáveis; estatísticas somente viáveis.`);
 lines.forEach((line,i)=>{const text=document.createElementNS('http://www.w3.org/2000/svg','text');text.setAttribute('x','12');text.setAttribute('y',String(20+i*21));text.setAttribute('font-size','12');text.setAttribute('fill','#203C42');text.textContent=line.length>125?line.slice(0,122)+'…':line;clone.appendChild(text);});
 const desc=document.createElementNS('http://www.w3.org/2000/svg','desc');desc.textContent=JSON.stringify({status:status.code,provenance:pr});clone.appendChild(desc);
 const style=document.createElementNS('http://www.w3.org/2000/svg','style');
 style.textContent=`svg{background:#FCFDFC;font-family:Arial,sans-serif} .eng-grid{stroke:#DDE7E7;stroke-width:1}
 .eng-tick{fill:#526C74;font-size:11px}.eng-axis-title{fill:#34545B;font-size:12px;font-weight:700}
 .eng-series-line{fill:none;stroke:#527E83;stroke-width:3}.eng-point circle{fill:#2F7876;stroke:#F8FCFA;stroke-width:2.5}
 .eng-point.bad circle{fill:#E56E38}.eng-point.selected circle{fill:#FF681B}
 .eng-target{stroke:#D97733;stroke-width:2.5;stroke-dasharray:8 6}.eng-target-label{font-size:12px;fill:#AA511C;font-weight:700}
 .eng-zero-backing{fill:#F0F4F3}.eng-zero-line{stroke:#4A6268;stroke-width:2.1;stroke-dasharray:4 3}
 .eng-diverge-bar{fill:#3A8B7D}.eng-diverge-row.bad .eng-diverge-bar{fill:#DB6E39}
 .eng-bar-name{font-size:12px;fill:#25454C}.eng-bar-value{font-size:11px;fill:#304E55;font-weight:700}`;
 clone.insertBefore(style,clone.firstChild);
 const body='<?xml version="1.0" encoding="utf-8"?>\n'+new XMLSerializer().serializeToString(clone);
 const url=URL.createObjectURL(new Blob([body],{type:'image/svg+xml;charset=utf-8'}));
 const link=document.createElement('a');link.href=url;link.download=`anti_murphy_${scope}_${item.result.mode}.svg`;
 document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),500);
}
function render(result,scope){
 const key=scope+':'+result.mode,cfg=configs[key];if(!cfg)return '';
 const rows=dataOf(result,scope);const prior=state.get(scope);
 const metricIndex=prior?.key===key?Math.min(prior.metric,cfg.metrics.length-1):0;
 if(prior?.key!==key && prior?.zoom){document.body.classList.remove('eng-chart-zoom-active');}
 state.set(scope,{key,metric:metricIndex,result,rows,zoom:prior?.key===key&&!!prior?.zoom});
 return html(scope);
}
function html(scope){
 const st=state.get(scope);if(!st)return '';
 const {key,metric,result,rows}=st,cfg=configs[key],mode=result.mode,m=cfg.metrics[metric];
 return `<section class="eng-suite ${st.zoom?'chart-focus':''}" data-eng-scope="${safe(scope)}" aria-label="Análise gráfica de ${safe(cfg.heading)}"><div class="eng-heading"><div><span class="eng-overline">VISUALIZAÇÃO TÉCNICA · ${rows.length} RESULTADOS</span><h3>${safe(cfg.heading)}</h3><p>${safe(cfg.intro)}</p></div><div class="eng-actions"><button class="eng-export" type="button" data-eng-export="${scope}">Dados CSV <span aria-hidden="true">↗</span></button><button class="eng-export" type="button" data-eng-export-svg="${scope}">Figura SVG <span aria-hidden="true">↗</span></button><button class="eng-export eng-zoom-btn" type="button" data-eng-zoom="${scope}" aria-pressed="${!!st.zoom}" aria-label="${st.zoom?'Fechar ampliação do gráfico':'Ampliar gráfico para apresentação'}">${st.zoom?'Fechar ampliação ✕':'Ampliar gráfico ⤢'}</button></div></div><div class="eng-controls" role="group" aria-label="Escolher indicador">${cfg.metrics.map((v,i)=>`<button class="eng-metric ${metric===i?'active':''}" data-eng-metric="${i}" data-eng-scope="${scope}" aria-pressed="${metric===i}">${safe(v[1])}</button>`).join('')}</div>${summary(rows,cfg,m,result)}<div class="eng-visual">${plot(rows,cfg,m,result)}</div>${indexedLegend(rows,cfg)}${cfg.kind==='diverging'||(cfg===configs['lab:goal']&&m[0]==='savings')?'<div class="eng-sign-legend"><span><i class="favorable"></i> Variação favorável ao objetivo do indicador</span><span><i class="unfavorable"></i> Variação desfavorável</span><span>Zero = sem variação</span></div>':''}<div class="eng-selected" role="status" aria-live="polite">Selecione um ponto ou barra para examinar a observação original do motor.</div><details class="eng-raw"><summary>Dados detalhados · ${rows.length} observações</summary>${fullTable(rows)}</details><p class="eng-source">Origem: motor Python de eventos discretos · estudo sintético. Linhas apenas conectam amostras discretas; não preveem pontos intermediários. Nenhum custo, tempo ou SLA é recalculado no navegador.</p></section>`;
}
function closeChartFocus(){
 document.querySelectorAll('.eng-suite.chart-focus').forEach(suite=>{
  suite.classList.remove('chart-focus');
  const button=suite.querySelector('[data-eng-zoom]');
  if(button){button.textContent='Ampliar gráfico ⤢';button.setAttribute('aria-pressed','false');button.setAttribute('aria-label','Ampliar gráfico para apresentação');}
 });
 for(const st of state.values())st.zoom=false;
 document.body.classList.remove('eng-chart-zoom-active');
}
document.addEventListener('click',e=>{
 const zoom=e.target.closest('[data-eng-zoom]');
 if(zoom){
  const scope=zoom.dataset.engZoom,item=state.get(scope),suite=zoom.closest('.eng-suite');
  if(!suite||!item)return;
  const now=!item.zoom;closeChartFocus();item.zoom=now;
  suite.classList.toggle('chart-focus',now);
  document.body.classList.toggle('eng-chart-zoom-active',now);
  zoom.textContent=now?'Fechar ampliação ✕':'Ampliar gráfico ⤢';
  zoom.setAttribute('aria-pressed',String(now));
  zoom.setAttribute('aria-label',now?'Fechar ampliação do gráfico':'Ampliar gráfico para apresentação');
  if(now)suite.scrollTop=0;
  return;
 }
 if(e.target.closest('.rail-item, #back-home, #back-previous, #presentation-toggle'))closeChartFocus();
 const metric=e.target.closest('[data-eng-metric]');
 if(metric){const scope=metric.dataset.engScope,st=state.get(scope),i=Number(metric.dataset.engMetric);if(!st||!configs[st.key].metrics[i])return;st.metric=i;{const suite=document.querySelector(`.eng-suite[data-eng-scope="${scope}"]`);if(suite)suite.outerHTML=html(scope);}return;}
 const exp=e.target.closest('[data-eng-export]');if(exp){const scope=exp.dataset.engExport,st=state.get(scope);if(st)downloadCsv(st.rows,scope,st.result.mode,st.result);return;}
 const svgExport=e.target.closest('[data-eng-export-svg]');if(svgExport){downloadSvg(svgExport.dataset.engExportSvg);return;}
 const point=e.target.closest('[data-eng-point]');if(point){
  const suite=point.closest('.eng-suite');if(!suite)return;
  const st=state.get(suite.dataset.engScope),i=Number(point.dataset.engPoint),r=st?.rows[i];if(!r)return;
  const label=String(r.label||r['Ação']||r['Posto']||r.run||r.seed||`#${i+1}`);
  suite.querySelectorAll('.eng-point,.eng-diverge-row,.eng-index-chip').forEach(el=>{
   const selected=Number(el.dataset.engPoint)===i;el.classList.toggle('selected',selected);
   if(el.classList.contains('eng-index-chip'))el.setAttribute('aria-pressed',String(selected));
  });
  suite.querySelector('.eng-selected').innerHTML=selectedDetail(r,configs[st.key],configs[st.key].metrics[st.metric]);
  const row=suite.querySelector(`[data-eng-row="${i}"]`);if(row){suite.querySelectorAll('[data-eng-row]').forEach(el=>el.classList.remove('selected'));row.classList.add('selected');}
 }
});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.querySelector('.eng-suite.chart-focus')){e.preventDefault();closeChartFocus();return;}if((e.key==='Enter'||e.key===' ') && e.target.matches('[data-eng-point]')){e.preventDefault();e.target.click();}});
window.AMCharts={render,configs,csv,dataOf,plot};
})();
