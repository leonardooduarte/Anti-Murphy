import json
import pytest
from simulation.decision_store import save_record,archived_records
from simulation.operation import initialize_operation,handle_command,memo


def record_state(directory):
    state={};initialize_operation(state);state['op_store_dir']=str(directory)
    for i,kind in enumerate(['demo','record']):
        handle_command(state,{'id':str(i),'token':state['op_token'],'kind':kind,'body':{'note':'Recurso confirmado'}})
    return state


def test_record_survives_a_new_session_without_changing_its_model(tmp_path):
    state=record_state(tmp_path)
    fresh={};initialize_operation(fresh)
    archive=archived_records(tmp_path)
    assert len(archive)==1
    body=archive[0]['data'];assert body['record']['note']=='Recurso confirmado'
    assert fresh.get('op_record') is None and fresh.get('v29_analysis') is None
    assert body['record']['signature']==body['examined_action']['signature']
    assert not list(tmp_path.glob('*.tmp'))


def test_modified_archive_is_rejected_and_not_listed(tmp_path):
    state=record_state(tmp_path);path=next(tmp_path.glob('*.json'))
    modified=json.loads(path.read_bytes());modified['examined_action']['savings']=999999
    raw=json.dumps(modified).encode();path.write_bytes(raw)
    assert archived_records(tmp_path)==[]
    with pytest.raises(ValueError,match='integridade'):save_record(tmp_path,raw)
