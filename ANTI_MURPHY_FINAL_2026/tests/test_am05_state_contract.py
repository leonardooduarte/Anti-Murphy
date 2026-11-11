"""Independent AM05 client-state contracts, using the shipped JavaScript module."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def js(source):
    node = shutil.which('node')
    if not node:
        pytest.skip('Optional JavaScript state tests require Node.')
    helper = ROOT / 'atelier/web/analysis_state.js'
    prelude = 'const {createStore,canonical}=require(' + json.dumps(str(helper)) + ');\n'
    return json.loads(subprocess.check_output([node, '-e', prelude + source], text=True))


@pytest.mark.parametrize('change,expected', [
    ('controls.min_sla=100;', 'desatualizado'),
    ('contexts["lab:goal"].context_signature="project-B";', 'desatualizado'),
    ('contexts["lab:duration"].context_signature="unrelated";', 'atual'),
    ('controls.min_sla=100;controls.min_sla=80;', 'atual'),
    ('contexts["lab:goal"].context_signature="B";contexts["lab:goal"].context_signature="A";', 'atual'),
])
def test_live_inputs_and_context_compared_without_mutating_origin(change, expected):
    data = js('''
let controls={min_sla:80},contexts={'lab:goal':{context_signature:'A'}};
const store=createStore(()=>({contexts,inputs:()=>controls}));
const result={mode:'goal',provenance:{scope:'lab',context_key:'lab:goal',context_signature:'A',inputs:{min_sla:80},signature:'deterministic',calculated_at:'original'}};
store.add(result,'lab');const original=JSON.stringify(result);
''' + ("contexts['lab:duration']={context_signature:'duration'};\n" if 'duration' in change else '') + change + '''
console.log(JSON.stringify({status:store.status(result).code,unchanged:JSON.stringify(result)===original}));
''')
    assert data == {'status': expected, 'unchanged': True}


def test_out_of_order_async_completion_keeps_later_request_current():
    data = js('''
const ctx={'advanced:uncertainty':{context_signature:'A'}};
const store=createStore(()=>({contexts:ctx,inputs:()=>({})}));
const make=()=>({mode:'uncertainty',provenance:{scope:'advanced',context_key:'advanced:uncertainty',context_signature:'A',inputs:{}}});
const older=make(),newer=make(),olderID=store.begin(),newerID=store.begin();
store.add(newer,'advanced',newerID);store.add(older,'advanced',olderID);
console.log(JSON.stringify({older:store.status(older).code,newer:store.status(newer).code,first:store.list('advanced','uncertainty')[0].id}));
''')
    assert data == {'older': 'historico', 'newer': 'atual', 'first': 2}


def test_old_results_unknown_and_scope_separation():
    data = js('''
const contexts={'lab:duration':{context_signature:'D'},'advanced:uncertainty':{context_signature:'U'}};
const store=createStore(()=>({contexts,inputs:()=>({})}));
const lab={mode:'duration',provenance:{scope:'lab',context_key:'lab:duration',context_signature:'D',inputs:{}}};
store.add(lab,'lab');store.add({mode:'uncertainty',provenance:{scope:'advanced',context_key:'advanced:uncertainty',context_signature:'U',inputs:{}}},'advanced');
console.log(JSON.stringify({old:store.status({mode:'duration',provenance:{analysis_signature:'legacy'}}).code,lab:store.status(lab).code,labEntries:store.list('lab','duration').length}));
''')
    assert data == {'old': 'desconhecido', 'lab': 'atual', 'labEntries': 1}


def test_more_than_25_results_are_retained_and_older_exports_historical():
    data = js('''
const store=createStore(()=>({contexts:{'lab:goal':{context_signature:'A'}},inputs:()=>({min_sla:80})}));
const make=()=>({mode:'goal',provenance:{scope:'lab',context_key:'lab:goal',context_signature:'A',inputs:{min_sla:80}}});
const first=make();store.add(first,'lab');for(let n=0;n<30;n++)store.add(make(),'lab');
console.log(JSON.stringify({count:store.list('lab','goal').length,first:store.status(first).code,last:store.status(store.list('lab','goal')[0].result).code}));
''')
    assert data == {'count': 31, 'first': 'historico', 'last': 'atual'}


def test_canonical_control_key_order_and_numeric_equivalence():
    assert js('console.log(JSON.stringify(canonical({min_sla:80.0,target_throughput:5.5})===canonical({target_throughput:5.5,min_sla:80})));') is True
