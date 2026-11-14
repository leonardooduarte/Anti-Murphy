import json,subprocess
from pathlib import Path
import pytest
from simulation.validation import validate_model

ROOT=Path(__file__).resolve().parents[1]
JS="""const fs=require('fs'),vm=require('vm');const s=fs.readFileSync(process.argv[1],'utf8'),m=JSON.parse(fs.readFileSync(0,'utf8')),c={structuredClone,st:{editing:m}};vm.createContext(c);vm.runInContext(s.slice(s.indexOf('function normalizedModel('),s.indexOf('async function saveModel(')),c);try{process.stdout.write(JSON.stringify({model:c.normalizedModel()}));}catch(e){process.stdout.write(JSON.stringify({error:e.message}));}"""
def normalize(value,missing=False):
 station={'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'setup_min':0,'custo_maquina_h':1,'custo_operador_h':1}
 order={'id':'A','quantidade':1,'prazo_h':10,'multa_hora':1,'route':[['P',1]]}
 if not missing:order['prioridade']=value
 return json.loads(subprocess.check_output(['node','-e',JS,str(ROOT/'atelier/web/app.js')],input=json.dumps({'stations':{'P':station},'orders':[order]}),text=True))
@pytest.mark.parametrize('value',[None,'','  '])
def test_absence_and_blank_omit_field(value):
 r=normalize(value,missing=value is None)['model'];assert 'prioridade' not in r['orders'][0];assert not validate_model(**r)
@pytest.mark.parametrize('value',[0,1,-2,99,'0',' -2 ','1e2'])
def test_valid_explicit_integer_is_preserved(value):
 r=normalize(value)['model'];assert r['orders'][0]['prioridade']==float(value);assert not validate_model(**r)
@pytest.mark.parametrize('value',[None,True,False,{},[],1.5,'abc','NaN','Infinity','0x10','1,2'])
def test_invalid_never_becomes_zero_or_null(value):
 assert 'prioridade' in normalize(value)['error']
