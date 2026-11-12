const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const files=process.argv.slice(2),p={stations:[],operations:[],outage:null};
for(let j=0;j<12;j++)p.stations.push({id:'P'+j,name:'P'+j,workers:1,machines:1,arrivals:[],starts:[],ends:[],changes:[]});
for(let i=0;i<12000;i++){
 const j=i%12,start=Math.floor(i/12)*.03,arrival=Math.max(0,start-.02),end=start+.025;
 p.operations.push([j,arrival,start,end,'A',i,0,0,[[start,end]]]);
 const s=p.stations[j];s.arrivals.push(arrival);s.starts.push(start);s.ends.push(end);
}
for(const path of files){
 const src=fs.readFileSync(path,'utf8'),ctx={};vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('function _binaryCount('),src.indexOf('const positions =')),ctx);
 const cold=performance.now();ctx.machineState(p,0,0);const coldMs=performance.now()-cold;
 const samples=[];let checksum;
 for(let trial=0;trial<5;trial++){
  let sum=0;const begin=performance.now();
  for(let i=0;i<300;i++)for(let j=0;j<12;j++){
   const x=ctx.machineState(p,j,i*.1);sum+=x.processing+x.queued+x.finished;
  }
  samples.push(performance.now()-begin);checksum=sum;
 }
 samples.sort((a,b)=>a-b);
 console.log(JSON.stringify({file:path,operations:12000,stations:12,queries:3600,cold_ms:coldMs,median_ms:samples[2],samples_ms:samples,checksum}));
}
