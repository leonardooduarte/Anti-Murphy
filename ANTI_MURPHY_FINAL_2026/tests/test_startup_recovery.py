"""Recovery must never overwrite the evidence or publish partial candidates."""
import json
from pathlib import Path

import pytest
from atelier.service import Studio


def files(folder):
    return {str(p.relative_to(folder)):p.read_bytes() for p in folder.rglob('*.json')}


@pytest.fixture
def saved(tmp_path):
    studio=Studio(tmp_path)
    studio.calculate({'duration_h':5,'min_sla':73,'delay_h':3,'rule':'SPT'})
    return tmp_path


@pytest.mark.parametrize('damage', ['json','array','null','missing','id','id_null','model','rule','spec','critical','delay'])
def test_active_damage_recovers_complete_checkpoint_and_preserves_all_files(saved,damage):
    active=saved/'projeto_ativo.json';project=saved/'projetos/principal.json'
    body=json.loads(project.read_text())
    if damage=='json':project.write_text('{broken')
    elif damage=='array':project.write_text('[]')
    elif damage=='null':project.write_text('null')
    elif damage=='missing':project.unlink()
    elif damage=='id':active.write_text('{"id":"../outside"}')
    elif damage=='id_null':active.write_text('{"id":null}')
    else:
        if damage=='model':body['orders']=None
        if damage=='rule':body['dispatch_rule']='INVALID'
        if damage=='spec':body['spec']={'station':'inexistente'}
        if damage=='critical':body['spec'].update(objective='critical',critical_order='inexistente')
        if damage=='delay':body['delay_h']=float('inf')
        project.write_text(json.dumps(body))
    before=files(saved)
    for _ in range(2):
        info=Studio(saved).info()
        assert info['recovery_warning']
        assert info['spec']['duration_h']==5
        assert info['spec']['min_sla']==73
        assert info['rule']=='SPT'
        assert files(saved)==before


@pytest.mark.parametrize('damage',['json','id','rule','critical','spec'])
def test_invalid_checkpoint_is_never_used_or_overwritten(saved,damage):
    (saved/'projeto_ativo.json').write_text('{broken')
    path=saved/'projeto_confirmado.json';body=json.loads(path.read_text())
    if damage=='json':path.write_text('{broken')
    else:
        if damage=='id':body['id']='../outside'
        if damage=='rule':body['dispatch_rule']='INVALID'
        if damage=='critical':body['spec'].update(objective='critical',critical_order='missing')
        if damage=='spec':body['spec']={'duration_h':None}
        path.write_text(json.dumps(body))
    before=files(saved);info=Studio(saved).info()
    assert info['recovery_warning']
    assert info['spec']['duration_h']==8 # basic model has no experiment spec
    assert files(saved)==before


def test_all_invalid_uses_demo_without_overwriting_any_source(saved):
    for p in saved.rglob('*.json'):p.write_text('null')
    before=files(saved);info=Studio(saved).info()
    assert 'exemplo padrão' in info['recovery_warning']
    assert info['run_id']
    assert files(saved)==before


def test_missing_pointer_prefers_full_checkpoint(saved):
    (saved/'projeto_ativo.json').unlink();before=files(saved)
    info=Studio(saved).info()
    assert info['spec']['min_sla']==73
    assert info['recovery_warning']
    assert files(saved)==before


def test_healthy_reopen_preserves_bytes_without_warning(saved):
    before=files(saved);info=Studio(saved).info()
    assert not info['recovery_warning']
    assert files(saved)==before


def test_explicit_apply_after_recovery_can_save_and_reopen(saved):
    (saved/'projeto_ativo.json').write_text('{broken')
    studio=Studio(saved)
    assert studio.info()['recovery_warning']
    studio.calculate({'min_sla':79})
    reopened=Studio(saved).info()
    assert reopened['spec']['min_sla']==79
    assert not reopened['recovery_warning']
