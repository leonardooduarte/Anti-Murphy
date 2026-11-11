const fs=require('fs'), path=require('path');
const b=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const {ReplayEngine}=require(path.resolve(process.argv[3], 'engine/ReplayEngine.js'));
const times=[0,100000000,1800000000,3599999999,3600000000,5400000000,6840000000,18000000000,35762452561];
const rows=[];
for(const branch of ['A','B'])for(const time_us of times){
 const state=ReplayEngine.computeStateAtTime(b,time_us,branch);
 rows.push({branch,time_us,seq:state.seq,statuses:Object.fromEntries(Object.entries(state.stations).map(([id,s])=>[id,s.status])),queues:Object.fromEntries(Object.entries(state.stations).map(([id,s])=>[id,s.queue_unit_ids]))});
}
process.stdout.write(JSON.stringify(rows));
