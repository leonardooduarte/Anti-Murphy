import { useSimulationStore } from '../store/useSimulationStore';
import { ReplayEngine } from '../engine/ReplayEngine';
import { Play, Pause, RotateCcw, AlertTriangle, ShieldAlert, ChevronRight } from 'lucide-react';
export const fmtTime=(us:number)=> {const minutes=Math.floor(us/60_000_000);return `${String(Math.floor(minutes/60)).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')}`;};
const fmtMoney=(c:number|null)=>c==null?'—':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(c/100);
const makeLabel=(t:number, max:number)=>`${Math.max(0,Math.min(100,t/Math.max(1,max)*100))}%`;
export function ControlsOverlay(){
  const s=useSimulationStore(); const b=s.snapshot;
  if(!b)return <div className="hud">Aguardando um pacote de simulação.</div>;
  const marks=ReplayEngine.markers(b);
  return <>
    <header className="fc-header">
      <div className="fc-title"><span className="fc-kicker">ANTI-MURPHY / FACTORY COMMAND</span><h1>Futuros em paralelo</h1><span className="fc-sub">{b.experiment_id} · Cenário sintético simulado</span></div>
      <div className="fc-summaries">
        {(['A','B'] as const).map(branch=>{
          const timeline=b[`branch_${branch}`];const sm=timeline.summary;
          return <div key={branch} className={'fc-stat '+(branch==='B'?'fc-stat-b':'')}><strong>{branch==='A'?'A · SEM AÇÃO':'B · INTERVENÇÃO'}</strong>
          <div className="fc-stat-value">{fmtTime(sm.makespan_us??0)} h <span>· {fmtMoney(sm.total_cost_cents)}</span></div>
          <small>SLA {sm.sla_pct==null?'—':`${sm.sla_pct.toFixed(1)}%`} · {sm.feasible==='unverified'?'Viabilidade não verificada':sm.feasible==='feasible'?'Viabilidade verificada':'Inviável'}</small></div>;
        })}
      </div>
    </header>
    <div className="fc-midline" style={{left:`${s.splitX}%`}} role="separator" aria-label="Comparador A/B" aria-orientation="vertical" tabIndex={0}
       onKeyDown={e=>{if(e.key==='ArrowLeft')s.setSplitX(s.splitX-2);if(e.key==='ArrowRight')s.setSplitX(s.splitX+2);}}
       onPointerDown={e=>{e.currentTarget.setPointerCapture(e.pointerId);}}
       onPointerMove={e=>{if(e.buttons===1){const r=e.currentTarget.parentElement!.getBoundingClientRect();s.setSplitX((e.clientX-r.left)/r.width*100);}}}>
       <div className="fc-handle"><ChevronRight size={19}/><ChevronRight className="mirror" size={19}/></div>
    </div>
    <div className="fc-branch-legend"><span>A · Fábrica sem ação</span><span>B · Fábrica com resposta</span></div>
    {s.selectedStation && <aside className="fc-detail" aria-live="polite">
       <strong>POSTO {s.selectedStation}</strong>
       {(['A','B'] as const).map(x=>{const q=(x==='A'?s.stateA:s.stateB)?.stations[s.selectedStation!];return <div key={x}><b>{x}</b> · {q?.status??'—'} · fila {q?.queue_unit_ids.length??0} · em processo {q?.processing_unit_ids.length??0}<small style={{display:"block",color:"#a9bec2"}}>IDs na fila: {q?.queue_unit_ids.slice(0,8).join(", ")||"Nenhum"}</small></div>;})}
       <button onClick={()=>s.setSelectedStation(null)}>Fechar</button></aside>}
    <footer className="fc-timeline">
      <div className="fc-timeline-tools">
        <button aria-label={s.isPlaying?'Pausar':'Reproduzir'} onClick={s.togglePlay}>{s.isPlaying?<Pause size={19}/>:<Play size={19}/>}</button>
        <button aria-label="Voltar ao início" onClick={()=>{s.setPlaying(false);s.setTime(0);}}><RotateCcw size={18}/></button>
        <strong>{fmtTime(s.currentTimeUs)} <span>/ {fmtTime(s.maxTimeUs)}</span></strong>
        <label>Velocidade <select value={s.playbackSpeed} onChange={e=>s.setSpeed(Number(e.target.value))}>
          <option value={60}>1 h/min</option><option value={360}>6 h/min</option><option value={3600}>1 h/s</option><option value={18000}>5 h/s</option>
        </select></label>
        <span className="fc-caution"><ShieldAlert size={14}/> Manutenção expressa hipotética: investimento não incluído</span>
      </div>
      <div className="fc-range"><input aria-label="Tempo de simulação" type="range" min="0" max={Math.max(1,s.maxTimeUs)} value={s.currentTimeUs} onChange={e=>s.setTime(Number(e.target.value))}/>
        {marks.map((m,i)=><button key={i} title={`${m.label}: ${fmtTime(m.t)} h`} className={'fc-mark '+m.kind} style={{left:makeLabel(m.t,s.maxTimeUs)}} onClick={()=>s.setTime(m.t)} />)}</div>
      <div className="fc-timeline-bottom"><span><AlertTriangle size={13}/> Falha em {fmtTime(b.incident.start_us)} h</span><span>Contrato {b.schema_version} · Origem: motor Python</span></div>
    </footer>
  </>;
}
