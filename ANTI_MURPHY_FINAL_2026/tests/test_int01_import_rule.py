"""INT01 import/export contract, preserving legacy absence and transactionality."""
from copy import deepcopy
import json
from unittest.mock import patch
import pytest
from atelier.service import Studio,StudioError


def documents(folder):
    return {str(p.relative_to(folder)):p.read_bytes() for p in folder.rglob('*.json')}


@pytest.mark.parametrize('rule',['EDD','SPT','FIFO'])
def test_exported_rule_roundtrip_in_another_project_reproduces_model_results(tmp_path,rule):
    app=Studio(tmp_path);app.calculate({'rule':rule})
    source=app.info();model=json.loads(app.export_model())
    target=app.create_project('Projeto de destino')
    app.calculate({'rule':'EDD' if rule!='EDD' else 'SPT'})
    restored=app.set_model(model)
    assert restored['active_project_id']!=source['active_project_id']
    assert restored['rule']==rule
    assert restored['metrics']['normal']==source['metrics']['normal']
    reopened=Studio(tmp_path).info()
    assert reopened['active_project_id']==target['active_project_id']
    assert reopened['rule']==rule
    assert reopened['metrics']['normal']==source['metrics']['normal']
    assert json.loads(app.export_model())==model


@pytest.mark.parametrize('rule',['EDD','SPT','FIFO'])
def test_legacy_absence_preserves_current_rule_and_non_model_controls(tmp_path,rule):
    app=Studio(tmp_path);app.calculate({'rule':rule,'min_sla':73,'delay_h':3,'duration_h':7})
    before=app.info();model=json.loads(app.export_model());model.pop('dispatch_rule')
    restored=app.set_model(model)
    assert restored['rule']==rule
    assert restored['spec']==before['spec']
    assert restored['delay_h']==before['delay_h']
    assert Studio(tmp_path).info()['rule']==rule


@pytest.mark.parametrize('invalid',[None,'','spt','SPT ',True,1,[],{},'INVALID'])
def test_explicit_invalid_rule_is_rejected_without_memory_or_disk_changes(tmp_path,invalid):
    app=Studio(tmp_path);app.calculate({'rule':'SPT'})
    before=app.info();disk=documents(tmp_path);model=json.loads(app.export_model())
    model['dispatch_rule']=invalid;model['orders'][0]['quantidade']+=1
    with pytest.raises(StudioError,match='despacho'):
        app.set_model(model)
    assert app.info()==before
    assert documents(tmp_path)==disk


@pytest.mark.parametrize('operation',['simulation','persistence'])
def test_import_does_not_publish_new_rule_when_execution_or_save_fails(tmp_path,operation):
    app=Studio(tmp_path);app.calculate({'rule':'EDD'})
    before=app.info();disk=documents(tmp_path);model=json.loads(app.export_model());model['dispatch_rule']='SPT'
    target='atelier.service.execute' if operation=='simulation' else 'atelier.service.atomic_bundle'
    error=ValueError('Falha controlada') if operation=='simulation' else OSError('Falha controlada')
    with patch(target,side_effect=error),pytest.raises(StudioError):app.set_model(model)
    assert app.info()==before
    assert documents(tmp_path)==disk
    assert Studio(tmp_path).info()['rule']=='EDD'


def test_conflicting_writer_keeps_newer_project_and_original_importer_state(tmp_path):
    app=Studio(tmp_path);other=Studio(tmp_path)
    model=json.loads(app.export_model());model['dispatch_rule']='SPT';before=app.info()
    other.calculate({'rule':'FIFO'});disk=documents(tmp_path)
    with pytest.raises(StudioError,match='outra instância'):app.set_model(model)
    after=app.info()
    for key in ('rule','run_id','spec','orders','stations','selected','metrics','analysis_signature'):
        assert after[key]==before[key]
    assert documents(tmp_path)==disk
    assert Studio(tmp_path).info()['rule']=='FIFO'
