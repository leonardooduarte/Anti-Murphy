from pathlib import Path
import subprocess
import pytest

@pytest.mark.parametrize('failure',[False,True])
def test_shared_pending_guard_and_retry(failure):
    src=Path(__file__).resolve().parents[1]/'atelier/web/app.js'
    js=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');const s=fs.readFileSync(process.argv[1],'utf8');
let resolve,reject,calls=0,added=0;const button={dataset:{},textContent:'Executar',setAttribute(){},removeAttribute(){}};
const c={document:{querySelectorAll:()=>[button]},$:()=>button,st:{advanced:'uncertainty',view:'avancadas'},dashUI:{},
 analysisHistory:{begin:()=>1,add:()=>added++,find:()=>null},api:()=>{calls++;return new Promise((a,b)=>{resolve=a;reject=b})},perform:async p=>p,
 analysisInputs:()=>({}),renderAdvancedInfo(){},notify(){}};
vm.createContext(c);vm.runInContext(s.slice(s.indexOf('let monteCarloPending='),s.indexOf('function dashBindEvents('))+
s.slice(s.indexOf('async function runAdvanced('),s.indexOf('/* Editable engineering-language')),c);
(async()=>{let first=c.dashRunRobustness();assert.equal(button.disabled,true);await c.dashRunRobustness();await c.runAdvanced();assert.equal(calls,1);
if(process.argv[2]==='true')reject(new Error('network'));else resolve({});await first;assert.equal(button.disabled,false);
let second=c.runAdvanced();await c.dashRunRobustness();assert.equal(calls,2);resolve({});await second;assert.equal(button.disabled,false);assert.equal(added,process.argv[2]==='true'?1:2);})().catch(e=>{console.error(e);process.exitCode=1});
'''
    subprocess.run(['node','-e',js,str(src),str(failure).lower()],check=True,capture_output=True,text=True)
