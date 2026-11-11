/** Streamlit Components v2 entry. Do not send animation frames to Python. */
import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
import type {ComparisonBundle} from './types/simulation_contract';
interface ComponentArgs {
  parentElement:HTMLElement|ShadowRoot;
  data:{bundle:ComparisonBundle};
  setTriggerValue:(name:string,value:unknown)=>void;
}
export default function mount(component:ComponentArgs):()=>void {
  const node=component.parentElement.querySelector('#anti-murphy-factory-command');
  if(!(node instanceof HTMLElement))throw new Error('Mount point do Factory Command ausente');
  const root=createRoot(node);
  root.render(<App bundle={component.data.bundle} onSelectStation={id=>component.setTriggerValue('selected_station',id)}/>);
  return ()=>root.unmount();
}
