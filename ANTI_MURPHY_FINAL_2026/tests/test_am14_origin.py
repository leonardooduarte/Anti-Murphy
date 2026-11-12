from pathlib import Path
import json,hashlib,subprocess
import pytest
from atelier.service import Studio
from simulation.decision_store import decode_record,save_record

def record(s):
 return s.decision({'note':'Decisão fundamentada no experimento atual.','constraints_ack':True})

def test_snapshot_name_survives_rename_and_project_switch(tmp_path):
 s=Studio(tmp_path);name=s.info()['active_project_name'];first=record(s);path=tmp_path/'registros'/first['filename'];raw=path.read_bytes()
 s.rename_project('Nome novo');s.create_project('Segundo');record(s)
 rows=s.history();assert len(rows)==2
 original=next(r for r in rows if r['filename']==first['filename'])
 assert original['project_id']=='principal' and original['project_name']==name
 assert len({r['project_id'] for r in rows})==2
 assert path.read_bytes()==raw
 assert s.read_history(first['filename'])==decode_record(raw)

@pytest.mark.parametrize('keep_id',[False,True])
def test_legacy_files_remain_byte_identical_and_do_not_gain_invented_name(tmp_path,keep_id):
 s=Studio(tmp_path);saved=record(s);body=s.read_history(saved['filename']);body.pop('sha256');body['record'].pop('project_name',None)
 if not keep_id:body['record'].pop('project_id',None)
 body['sha256']=hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 path=save_record(tmp_path/'registros',json.dumps(body,ensure_ascii=False).encode());raw=path.read_bytes()
 item=next(r for r in s.history() if r['filename']==path.name)
 assert item['project_name'] is None
 assert item['project_id']==('principal' if keep_id else None)
 assert s.read_history(path.name)==decode_record(raw) and path.read_bytes()==raw

@pytest.mark.parametrize('record,expected',[
 ({'project_id':'P','project_name':'Antigo'},'nome arquivado'),
 ({'project_id':'P'},'nome atual do cadastro'),
 ({'project_id':'removido'},'origem preservada pelo identificador'),
 ({},'não identificado'),
])
def test_rendered_origin_distinguishes_snapshot_lookup_and_unknown(record,expected):
 src=Path(__file__).resolve().parents[1]/'atelier/web/app.js'
 js="const fs=require('fs'),vm=require('vm');const s=fs.readFileSync(process.argv[1],'utf8'),c={st:{data:{projects:[{id:'P',name:'Atual'}]}}};vm.createContext(c);vm.runInContext(s.slice(s.indexOf('function historyProjectOrigin('),s.indexOf('async function loadHistory(')),c);process.stdout.write(c.historyProjectOrigin(JSON.parse(process.argv[2])));"
 run=subprocess.run(['node','-e',js,str(src),json.dumps(record)],capture_output=True,text=True,check=True)
 assert expected in run.stdout
