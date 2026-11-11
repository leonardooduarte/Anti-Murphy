/* Exact right-continuous DES state; shared by rendering and Node regression tests. */
(function(root){
function upper(a,t){let lo=0,hi=a.length;while(lo<hi){const m=(lo+hi)>>1;if(a[m]<=t)lo=m+1;else hi=m;}return lo;}
function snapshot(p,t){return {time:t,completed:upper(p.completion_times,t),stations:p.stations.map(s=>{
const a=upper(s.arrivals,t),b=upper(s.starts,t),c=upper(s.ends,t),o=p.outage;
const down=!!(o&&o.station===s.id&&o.start<=t&&t<o.end);
return {id:s.id,queue:a-b,active:b-c,processing:down?0:b-c,completed:c,down};})};}
function progress(op,t){let done=0,total=0;for(const [a,b] of op[8]){total+=b-a;done+=Math.max(0,Math.min(t,b)-a);}return total>0?Math.max(0,Math.min(1,done/total)):0;}
const api={upper,snapshot,progress};root.MurphyReplay=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
