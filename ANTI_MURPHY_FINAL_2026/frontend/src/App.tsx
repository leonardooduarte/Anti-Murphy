import { useCallback, useEffect, useRef, useState } from 'react';
import type { RefObject } from 'react';
import { Stage, Container, Graphics } from '@pixi/react';
import type * as PIXI from 'pixi.js';
import { useSimulationStore } from './store/useSimulationStore';
import { MachineNode } from './components/MachineNode';
import { ControlsOverlay } from './components/ControlsOverlay';
import type { ComparisonBundle } from './types/simulation_contract';
import './styles.css';

interface Props { bundle:ComparisonBundle; onSelectStation?:(id:string)=>void; }
function useSize(ref:RefObject<HTMLDivElement>) {
  const [size,setSize]=useState({width:960,height:650});
  useEffect(()=>{const host=ref.current;if(!host)return;
    const obs=new ResizeObserver(()=>setSize({width:Math.max(360,host.clientWidth),height:Math.max(550,host.clientHeight)}));
    obs.observe(host);return ()=>obs.disconnect();},[ref]);return size;
}
const fmtCoord=(value:number,size:number,margin:number)=>margin+value*Math.max(0,size-margin*2);
function FactorySurface({bundle,width,height,side,onSelectStation}:{bundle:ComparisonBundle;width:number;height:number;side:'A'|'B';onSelectStation:(id:string)=>void}) {
  const frame=useSimulationStore(s=>side==='A'?s.stateA:s.stateB);
  const selected=useSimulationStore(s=>s.selectedStation);
  const definitions=bundle.definition.stations;
  const coords:Record<string,{x:number;y:number}>={};
  Object.entries(definitions).forEach(([id,d])=>{coords[id]={x:fmtCoord(d.x,width,125),y:170+d.y*Math.max(100,height-355)};});
  const drawEdges=useCallback((g:PIXI.Graphics)=>{
    g.clear();
    for(const edge of bundle.topology.edges){const s=coords[edge.source];const t=coords[edge.target];if(!s||!t)continue;
      g.lineStyle(3,0x4C6A70,0.8);g.moveTo(s.x+75,s.y);g.lineTo(t.x-75,t.y);
      g.lineStyle(0);g.beginFill(0x8AA7AC,0.6);g.drawCircle((s.x+t.x)/2,(s.y+t.y)/2,3);g.endFill();
    }
  },[bundle.topology.edges,width,height]);
  if(!frame)return null;
  return <Container><Graphics draw={drawEdges}/>
    {Object.entries(frame.stations).map(([id,state])=>coords[id]&&<MachineNode key={id} x={coords[id].x} y={coords[id].y} id={id} state={state} selected={selected===id} onSelect={onSelectStation} side={side}/>)}
  </Container>;
}
function FactoryCanvas({bundle,width,height,onSelectStation}:{bundle:ComparisonBundle;width:number;height:number;onSelectStation:(id:string)=>void}) {
  const split=useSimulationStore(s=>s.splitX);const [mask,setMask]=useState<PIXI.Graphics|null>(null);
  const drawMask=useCallback((g:PIXI.Graphics)=>{g.clear();g.beginFill(0xffffff);g.drawRect(width*split/100,0,width*(100-split)/100,height);g.endFill();},[width,height,split]);
  const drawWipeBackground=useCallback((g:PIXI.Graphics)=>{g.clear();g.beginFill(0x19272C,0.88);g.drawRect(0,0,width,height);g.endFill();},[width,height]);
  return <Stage width={width} height={height} options={{backgroundColor:0x121C20,antialias:true,autoDensity:true,resolution:Math.min(2,typeof window==='undefined'?1:window.devicePixelRatio||1)}}>
    <FactorySurface bundle={bundle} width={width} height={height} side="A" onSelectStation={onSelectStation}/>
    {/* Stable graphics instance participates in the display tree and is reused as the mask. */}
    <Graphics ref={setMask} draw={drawMask}/>
    <Container mask={mask??undefined}>
      <Graphics draw={drawWipeBackground}/>
      <FactorySurface bundle={bundle} width={width} height={height} side="B" onSelectStation={onSelectStation}/>
    </Container>
  </Stage>;
}
export default function App({bundle,onSelectStation}:Props){
  const host=useRef<HTMLDivElement>(null);const {width,height}=useSize(host);
  const load=useSimulationStore(s=>s.loadSnapshot);const playing=useSimulationStore(s=>s.isPlaying);const speed=useSimulationStore(s=>s.playbackSpeed);
  const select=useSimulationStore(s=>s.setSelectedStation);
  useEffect(()=>{load(bundle);},[bundle,load]);
  useEffect(()=>{
    if(!playing)return;
    let raf=0;let last=performance.now();
    const tick=(now:number)=>{const delta=Math.min(200,now-last);last=now;const state=useSimulationStore.getState();
      state.setTime(state.currentTimeUs+delta*1000*speed);if(useSimulationStore.getState().isPlaying)raf=requestAnimationFrame(tick);};
    raf=requestAnimationFrame(tick);return ()=>cancelAnimationFrame(raf);
  },[playing,speed]);
  const onSelect=useCallback((id:string)=>{select(id);onSelectStation?.(id);},[select,onSelectStation]);
  return <div className="fc-root" ref={host}><FactoryCanvas bundle={bundle} width={width} height={height} onSelectStation={onSelect}/><ControlsOverlay/></div>;
}
