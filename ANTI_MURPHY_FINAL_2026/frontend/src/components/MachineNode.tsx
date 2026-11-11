import { Graphics, Text } from '@pixi/react';
import * as PIXI from 'pixi.js';
import { useCallback, useMemo } from 'react';
import type { StationState } from '../types/simulation_contract';
interface Props { x:number;y:number;id:string;state:StationState;selected:boolean;onSelect:(id:string)=>void;side:'A'|'B'; }
export function MachineNode({x,y,id,state,selected,onSelect,side}:Props) {
  const stroke = state.status==='down'?0xFF681B:state.status==='running'?0x8ECAA9:state.status==='blocked'?0xE8B86D:0x647D81;
  const draw=useCallback((g:PIXI.Graphics)=>{
    g.clear();g.lineStyle(selected?3:1.5,selected?0xFF681B:stroke,1);
    g.beginFill(0x213137,1);g.drawRoundedRect(-75,-53,150,110,11);g.endFill();
    // machine equipment, status bezel and footprint (schematic, not a machine geometry model)
    g.lineStyle(1,0x688084,0.75);g.beginFill(0x354A50);g.drawRoundedRect(-57,-32,114,47,5);g.endFill();
    g.beginFill(0x0E1A20);g.drawRoundedRect(-43,-24,76,27,4);g.endFill();
    g.lineStyle(1,stroke,0.9);g.drawRect(40,-22,8,16);g.lineStyle(0);
    g.beginFill(stroke);g.drawCircle(-56,-43,4);g.endFill();
    if(state.status==='down'){g.lineStyle(2,stroke,1);g.moveTo(-29,-21);g.lineTo(-8,-4);g.moveTo(-8,-21);g.lineTo(-29,-4);g.lineStyle(0);}
    else if(state.status==='running'){g.lineStyle(2,stroke,1);for(let i=0;i<3;i++){g.moveTo(-32+i*14,-5);g.lineTo(-24+i*14,-14);}g.lineStyle(0);}
    g.beginFill(0x162429);g.drawRoundedRect(-57,24,114,20,4);g.endFill();
    // Individual queue units, rendered without invented travel animation
    const q=state.queue_unit_ids.length;
    for(let i=0;i<Math.min(q,10);i++){g.beginFill(0xFF681B,0.86);g.drawRoundedRect(-70+i*13,65,9,9,2);g.endFill();}
    for(let i=0;i<Math.min(state.processing_unit_ids.length,4);i++){g.beginFill(0x8ECAA9);g.drawCircle(-14+i*10,35,3.3);g.endFill();}
    for(let i=0;i<Math.min(state.paused_unit_ids.length,4);i++){g.beginFill(0xFF681B);g.drawRect(22+i*8,32,5,6);g.endFill();}
    g.lineStyle(0);
  },[stroke,selected,state.status,state.queue_unit_ids.length,state.processing_unit_ids.length,state.paused_unit_ids.length]);
  const titleStyle=useMemo(()=>new PIXI.TextStyle({fill:'#F7F7F3',fontSize:15,fontWeight:'bold',fontFamily:'Segoe UI, sans-serif'}),[]);
  const small=useMemo(()=>new PIXI.TextStyle({fill:'#9FB2B4',fontSize:11,fontFamily:'Segoe UI, sans-serif'}),[]);
  const label = state.status==='down'?'PARADA':state.status==='running'?'OPERANDO':state.status==='blocked'?'BLOQUEADA':state.status==='setup'?'PREPARAÇÃO':'EM ESPERA';
  return <>
    <Graphics x={x} y={y} draw={draw} interactive cursor="pointer" pointertap={()=>onSelect(id)} />
    <Text x={x} y={y-45} anchor={{x:0.5,y:0.5}} text={id} style={titleStyle} />
    <Text x={x} y={y+34} anchor={{x:0.5,y:0.5}} text={`${label} · ${state.busy_slots}/${state.machine_capacity}`} style={small} />
    {state.queue_unit_ids.length>10 && <Text x={x+69} y={y+68} text={`+${state.queue_unit_ids.length-10}`} style={small} />}
  </>;
}
