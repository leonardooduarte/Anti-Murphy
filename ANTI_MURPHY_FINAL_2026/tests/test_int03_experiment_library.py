"""A malformed archive must not hide or overwrite valid experiments."""
from copy import deepcopy
import json
from unittest.mock import patch
import pytest
from atelier.service import Studio,StudioError


@pytest.fixture
def archived(tmp_path):
    app=Studio(tmp_path);first=app.save_experiment('Primeiro válido')
    app.calculate({'duration_h':10});second=app.save_experiment('Segundo válido')
    return app,first,second


def files(app):return {p:p.read_bytes() for p in app.experiments_dir.glob('*.json')}


@pytest.mark.parametrize('damage',['array','null','text','truncated','encoding','no_id','wrong_id','unsafe_id','no_project','no_hash','bad_name','bad_date','bad_metrics','bad_response','bad_precise','bad_metric','nonfinite','bad_economics'])
def test_invalid_document_does_not_block_listing_comparison_or_new_save(archived,damage):
    app,a,b=archived;doc=deepcopy(a);doc['id']='invalid';p=app.experiments_dir/'invalid.json'
    if damage=='array':raw=b'[]'
    elif damage=='null':raw=b'null'
    elif damage=='text':raw=b'"text"'
    elif damage=='truncated':raw=b'{broken'
    elif damage=='encoding':raw=b'\xff'
    else:
        if damage=='no_id':doc.pop('id')
        if damage=='wrong_id':doc['id']='another'
        if damage=='unsafe_id':doc['id']='../outside'
        if damage=='no_project':doc.pop('project_id')
        if damage=='no_hash':doc.pop('model_hash')
        if damage=='bad_name':doc['name']=[]
        if damage=='bad_date':doc['created_at']=17
        if damage=='bad_metrics':doc['metrics']=[]
        if damage=='bad_response':doc['metrics']['response']=[]
        if damage=='bad_precise':doc['metrics']['incident']['precise']=[]
        if damage=='bad_metric':doc['metrics']['incident']['sla_pct']='wrong'
        if damage=='nonfinite':doc['metrics']['incident']['total_cost']=float('inf')
        if damage=='bad_economics':doc['economics']=[]
        raw=json.dumps(doc).encode()
    p.write_bytes(raw);before=files(app)
    status=app.experiment_library()
    assert {x['id'] for x in status['items']}=={a['id'],b['id']}
    assert status['project_id']==app.project_id
    assert len(status['issues'])==1 and status['issues'][0]['filename']=='invalid.json'
    assert status['issues'][0]['reason']
    assert {x['id'] for x in app.experiment_list()}=={a['id'],b['id']}
    assert app.compare_experiments(a['id'],b['id'])['same_model']
    assert files(app)==before
    saved=app.save_experiment('Terceiro válido')
    assert saved['id'] not in {a['id'],b['id']}
    assert all(path.read_bytes()==raw for path,raw in before.items())
    assert len(app.experiment_list())==3


def test_legacy_economics_and_missing_optional_response_key_stay_read_only(archived):
    app,a,b=archived
    for doc in [a,b]:
        doc.pop('economics');doc['metrics'].pop('response');doc.pop('created_at')
        (app.experiments_dir/(doc['id']+'.json')).write_text(json.dumps(doc))
    before=files(app);status=app.experiment_library()
    assert not status['issues'] and len(status['items'])==2
    result=app.compare_experiments(a['id'],b['id'])
    assert result['economics']['first']['investment'] is None
    assert result['economics']['first']['status']=='partial'
    assert files(app)==before


def test_invalid_files_are_not_deleted_and_notice_updates_after_external_repair(archived):
    app,a,b=archived;path=app.experiments_dir/'repaired.json';path.write_text('[]')
    assert app.experiment_library()['issues']
    fixed=deepcopy(a);fixed['id']='repaired';path.write_text(json.dumps(fixed));raw=path.read_bytes()
    assert not app.experiment_library()['issues']
    assert len(app.experiment_list())==3 and path.read_bytes()==raw


def test_project_isolation_and_unknown_origin_warning(archived):
    app,a,b=archived;original=app.project_id;app.create_project('Outro projeto')
    saved=app.save_experiment('Válido no outro projeto')
    assert [x['id'] for x in app.experiment_list()]==[saved['id']]
    with pytest.raises(StudioError):app.compare_experiments(a['id'],saved['id'])
    path=app.experiments_dir/'unknown.json';path.write_text('[]')
    assert app.experiment_library()['issues'][0]['filename']=='unknown.json'
    app.open_project(original)
    assert {x['id'] for x in app.experiment_list()}=={a['id'],b['id']}


def test_invalid_selected_document_returns_controlled_error(archived):
    app,a,b=archived;(app.experiments_dir/(a['id']+'.json')).write_text('[]')
    with pytest.raises(StudioError,match='dois experimentos'):app.compare_experiments(a['id'],b['id'])


def test_unreadable_file_is_reported_without_hiding_others(archived):
    app,a,b=archived;path=app.experiments_dir/'denied.json';path.write_text('{}')
    original=type(path).read_text
    def read(p,*args,**kwargs):
        if p==path:raise PermissionError('controlled')
        return original(p,*args,**kwargs)
    with patch.object(type(path),'read_text',read):
        status=app.experiment_library()
    assert len(status['items'])==2 and status['issues'][0]['filename']=='denied.json'
    assert path.read_text()=='{}'


def test_invalid_documents_do_not_consume_limit_but_valid_documents_do(archived):
    app,a,b=archived
    for i in range(100):(app.experiments_dir/f'bad{i}.json').write_text('[]')
    for i in range(97):
        doc=deepcopy(a);doc['id']=f'copy{i}';(app.experiments_dir/(doc['id']+'.json')).write_text(json.dumps(doc))
    assert len(app.experiment_list())==99
    app.save_experiment('Centésimo válido')
    with pytest.raises(StudioError,match='100 experimentos'):app.save_experiment('Excesso válido')
    assert len(app.experiment_list())==100
    assert all((app.experiments_dir/f'bad{i}.json').read_text()=='[]' for i in range(100))


def test_enumeration_failure_is_not_reported_as_an_empty_collection(archived):
    app,a,b=archived
    with patch.object(type(app.experiments_dir),'iterdir',side_effect=PermissionError('controlled')):
        with pytest.raises(StudioError,match='consultar a pasta'):app.experiment_library()
        with pytest.raises(StudioError):app.save_experiment('Não deve gravar')


def test_deeply_nested_invalid_json_does_not_block_valid_records(archived):
    app,a,b=archived;path=app.experiments_dir/'nested.json';path.write_text('['*1500+'0'+']'*1500)
    status=app.experiment_library()
    assert len(status['items'])==2 and status['issues'][0]['filename']=='nested.json'
    assert path.exists()
