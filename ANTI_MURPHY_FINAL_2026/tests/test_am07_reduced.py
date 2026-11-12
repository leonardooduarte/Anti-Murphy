from copy import deepcopy
import json
from pathlib import Path
import subprocess
import pytest
from simulation.factory import build_scenario
from simulation.engine import run_simulation
from simulation.replay import replay_payload,snapshot


@pytest.fixture(scope='module')
def replay():
    station={'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,
             'disponibilidade':1,'setup_min':0,'custo_maquina_h':1,'custo_operador_h':1}
    cfg=build_scenario('Large',{'P':station},[{'id':'A','quantidade':1001,'prazo_h':1000,'multa_hora':1,'route':[['P',1]]*12}],chaos_station='P',chaos_start_h=.1,chaos_duration_h=.2)
    result=run_simulation(cfg)
    return result,replay_payload(result)


@pytest.mark.parametrize('t',[0,.05,.1,.15,.3,.31,1,10,1000])
def test_reduced_counts_match_independent_segment_reference(replay,t):
    result,p=replay
    assert p['details_omitted'] and p['operations']==[] and p['operation_count']==12012
    expected=sum(a<=t<b for op in result['operations'] for a,b in op['process_segments'])
    assert snapshot(p,t)['stations'][0]['processing']==expected
    source=Path(__file__).resolve().parents[1]/'atelier/web/app.js'
    driver="const fs=require('fs'),vm=require('vm');const s=fs.readFileSync(process.argv[1],'utf8'),c={};vm.createContext(c);vm.runInContext(s.slice(s.indexOf('function _binaryCount('),s.indexOf('const positions =')),c);const p=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(c.machineState(p,0,Number(process.argv[2]))));"
    run=subprocess.run(['node','-e',driver,str(source),str(t)],input=json.dumps(p),text=True,capture_output=True,check=True)
    state=json.loads(run.stdout)
    assert state['processing']==expected
    assert state['paused']==state['active']-expected


def test_full_and_reduced_segment_arrays_agree(replay):
    result,p=replay
    small=deepcopy(result);small['operations']=small['operations'][:100]
    full=replay_payload(small)
    assert not full['details_omitted']
    assert len(full['stations'][0]['processing_starts'])==sum(len(x['process_segments']) for x in small['operations'])
