import { create } from 'zustand';
import type { ComparisonBundle, SimulationSnapshot } from '../types/simulation_contract';
import { assertBundle } from '../types/simulation_contract';
import { ReplayEngine } from '../engine/ReplayEngine';
interface State {
  snapshot:ComparisonBundle|null; currentTimeUs:number;maxTimeUs:number;isPlaying:boolean;
  playbackSpeed:number; splitX:number;stateA:SimulationSnapshot|null; stateB:SimulationSnapshot|null;
  selectedStation:string|null;
  loadSnapshot:(b:ComparisonBundle)=>void;setTime:(n:number)=>void;togglePlay:()=>void;
  setPlaying:(b:boolean)=>void;setSplitX:(n:number)=>void;setSpeed:(n:number)=>void;
  setSelectedStation:(s:string|null)=>void;
}
export const useSimulationStore=create<State>((set,get)=>({
 snapshot:null,currentTimeUs:0,maxTimeUs:0,isPlaying:false,playbackSpeed:3600,splitX:50,
 stateA:null,stateB:null,selectedStation:null,
 loadSnapshot:(b)=>{assertBundle(b);set({snapshot:b,currentTimeUs:0,maxTimeUs:ReplayEngine.maxTimeUs(b),isPlaying:false,selectedStation:null,
   stateA:ReplayEngine.computeStateAtTime(b,0,'A'),stateB:ReplayEngine.computeStateAtTime(b,0,'B')});},
 setTime:(n)=>{const s=get(); const t=Math.round(Math.min(s.maxTimeUs,Math.max(0,n)));
   if (!s.snapshot)return; set({currentTimeUs:t, stateA:ReplayEngine.computeStateAtTime(s.snapshot,t,'A'),stateB:ReplayEngine.computeStateAtTime(s.snapshot,t,'B'),isPlaying:t>=s.maxTimeUs?false:s.isPlaying});},
 togglePlay:()=>set(s=>({isPlaying:!s.isPlaying && s.currentTimeUs<s.maxTimeUs})),
 setPlaying:(b)=>set({isPlaying:b}),
 setSplitX:(n)=>set({splitX:Math.max(0,Math.min(100,n))}),
 setSpeed:(n)=>set({playbackSpeed:Math.max(1,Math.min(36000,n))}),
 setSelectedStation:(id)=>set({selectedStation:id}),
}));
