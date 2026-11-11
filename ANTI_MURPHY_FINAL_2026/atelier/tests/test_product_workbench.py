"""Integrated-product behavior, covering disk persistence and experiment comparability."""
import json
from copy import deepcopy
from pathlib import Path

import pytest

from atelier.service import Studio, StudioError


def test_project_create_duplicate_reopen_and_persist(tmp_path):
    app=Studio(tmp_path)
    original=app.info()
    new=app.create_project('Linha Alfa',duplicate=True)
    assert new['active_project_name']=='Linha Alfa'
    assert new['stations']==original['stations']
    assert new['orders']==original['orders']
    assert len(new['projects'])==2
    pid=new['active_project_id']
    changed=deepcopy(new['orders'])
    changed[0]['quantidade']+=1
    app.set_model({'stations':new['stations'],'orders':changed})
    app.rename_project('Linha Alfa Revisada')
    reopened=Studio(tmp_path)
    assert reopened.info()['active_project_id']==pid
    assert reopened.info()['active_project_name']=='Linha Alfa Revisada'
    assert reopened.info()['orders'][0]['quantidade']==changed[0]['quantidade']
    old=reopened.open_project('principal')
    assert old['orders']==original['orders']
    assert old['stations']==original['stations']


def test_project_new_example_is_isolated(tmp_path):
    app=Studio(tmp_path)
    orig=app.info()['orders']
    app.create_project('Estudo B',duplicate=False)
    assert app.info()['orders']==orig
    assert app.info()['active_project_name']=='Estudo B'
    assert (tmp_path/'projetos'/'principal.json').is_file()
    assert (tmp_path/'projeto_ativo.json').is_file()


def test_project_rejects_invalid_names_ids_and_limit_escape(tmp_path):
    app=Studio(tmp_path)
    for name in ('', 'ab', '\nproject', 'a'*71):
        with pytest.raises(StudioError):app.create_project(name)
    for identifier in ('../../etc/passwd', '../foo', 'INVALID/PROJECT', ''):
        with pytest.raises(StudioError):app.open_project(identifier)


def test_experiment_archival_compare_reproducible_and_no_state_mutation(tmp_path):
    app=Studio(tmp_path)
    first=app.save_experiment('Cenário de referência')
    app.calculate({'duration_h':10})
    second=app.save_experiment('Parada prolongada')
    assert first['id']!=second['id']
    assert first['model_hash']==second['model_hash']
    original_state=(app.info()['run_id'],app.info()['selected'])
    out=app.compare_experiments(first['id'],second['id'])
    assert out['same_model'] is True
    assert out['delta']['makespan_h'] is not None
    assert (app.info()['run_id'],app.info()['selected'])==original_state
    assert len(Studio(tmp_path).experiment_list())==2


def test_experiments_are_scoped_to_project(tmp_path):
    app=Studio(tmp_path)
    a=app.save_experiment('No projeto principal')
    app.create_project('Outro projeto')
    assert app.experiment_list()==[]
    b=app.save_experiment('Experimento novo')
    assert b['project_id']!=a['project_id']
    with pytest.raises(StudioError):app.compare_experiments(a['id'],b['id'])
    app.open_project('principal')
    assert [x['id'] for x in app.experiment_list()]==[a['id']]


def test_experiment_comparison_marks_different_models(tmp_path):
    app=Studio(tmp_path)
    first=app.save_experiment('Antes da alteração')
    current=app.info()
    modified=deepcopy(current['orders'])
    modified[0]['quantidade']+=1
    app.set_model({'stations':current['stations'],'orders':modified})
    second=app.save_experiment('Depois da alteração')
    out=app.compare_experiments(first['id'],second['id'])
    assert out['same_model'] is False
    assert 'modelos distintos' in out['note']
