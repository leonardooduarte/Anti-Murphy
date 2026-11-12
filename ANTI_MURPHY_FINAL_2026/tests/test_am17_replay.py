import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

JS=r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const src=fs.readFileSync(process.argv[1],'utf8');
const ctx={};vm.createContext(ctx);
vm.runInContext(src.slice(src.indexOf('function _binaryCount('),src.indexOf('const positions =')),ctx);
function reference(p,idx,t){
 const s=p.stations[idx],n=arr=>arr.filter(x=>x<=t).length;
 let workers=s.workers,machines=s.machines;
 for(const c of s.changes||[])if(c.time<=t){workers=c.workers_after;machines=c.machines_after;}
 const active=p.operations.filter(o=>o[0]===idx&&o[2]<=t&&t<o[3]);
 const live=active.filter(o=>o[8].some(([a,b])=>a<=t&&t<b));
 const wait=p.operations.filter(o=>o[0]===idx&&o[1]<=t&&t<o[2]);
 return {id:s.id,name:s.name,queued:Math.max(0,n(s.arrivals)-n(s.starts)),active:Math.max(0,n(s.starts)-n(s.ends)),processing:live.length,
  paused:active.length-live.length,finished:n(s.ends),down:!!(p.outage&&p.outage.station===s.id&&t>=p.outage.start&&t<p.outage.end),
  workers,machines,queue:wait.map(o=>`${o[4]} · ${o[5]}`),working:live.map(o=>`${o[4]} · ${o[5]}`),operations:active,raw:s};
}
function referenceEvents(p,t){
 const events=[];
 for(const o of p.operations)for(const [i,kind] of [[2,'Início'],[3,'Conclusão']])if(o[i]<=t+1e-9)
  events.push({t:o[i],kind,station:p.stations[o[0]].id,order:String(o[4]||'—'),unit:String(o[5]||'')});
 if(p.outage)for(const [i,kind] of [['start','Parada'],['end','Fim da parada']])if(p.outage[i]<=t+1e-9)
  events.push({t:p.outage[i],kind,station:p.outage.station,order:'—',unit:''});
 return events.sort((a,b)=>a.t-b.t||a.kind.localeCompare(b.kind,'pt-BR')).slice(-6).reverse();
}
const p={stations:[],operations:[],outage:{station:'P0',start:1,end:2}};
for(let j=0;j<6;j++)p.stations.push({id:'P'+j,name:'Posto '+j,workers:2,machines:2,changes:[{time:3,workers_after:3,machines_after:3}],arrivals:[],starts:[],ends:[]});
for(let i=0;i<800;i++){
 const station=i%6,start=Math.floor(i/6)*.1,end=start+.25+(i%5)*.01,arrival=Math.max(0,start-.15);
 const op=[station,arrival,start,end,'OP-'+i,1,0,0,[[start,start+.08],[start+.12,end]]];
 p.operations.unshift(op); // Completion/input order differs from start order.
 const s=p.stations[station];s.arrivals.push(arrival);s.starts.push(start);s.ends.push(end);
}
for(const s of p.stations)for(const field of ['arrivals','starts','ends'])s[field].sort((a,b)=>a-b);
const before=JSON.stringify(p),times=[0,1,2,3,.08,.12,.25,1-1e-10,-1,100];
for(let i=0;i<150;i++)times.push((i*73%150)/10);
let queries=0;
for(const t of times){
 for(let j=0;j<6;j++){assert.equal(JSON.stringify(ctx.machineState(p,j,t)),JSON.stringify(reference(p,j,t)));queries++;}
 assert.equal(JSON.stringify(ctx.recentReplayEvents(p,t)),JSON.stringify(referenceEvents(p,t)));
}
assert.equal(JSON.stringify(p),before);
assert.equal(ctx.replayIndex(p),ctx.replayIndex(p));
assert.notEqual(ctx.replayIndex(p),ctx.replayIndex(JSON.parse(before)));
const reduced=JSON.parse(before);reduced.operations=[];reduced.details_omitted=true;
assert.equal(ctx.machineState(reduced,0,1).processing,0); // AM07 stays explicit and separate.
assert.ok(ctx.machineState(reduced,0,1).active>0);
process.stdout.write(JSON.stringify({queries,event_queries:times.length,unchanged:true}));
"""


def test_index_preserves_states_events_order_segments_and_seeks():
    run=subprocess.run(['node','-e',JS,str(ROOT/'atelier/web/app.js')],text=True,capture_output=True,check=True)
    result=json.loads(run.stdout)
    assert result=={'queries':960,'event_queries':160,'unchanged':True}
