"""Real cooperating processes and independent stale Studio instances."""
from copy import deepcopy
from pathlib import Path
import multiprocessing
import subprocess
import sys
import json
import pytest
from atelier.service import Studio, StudioError
from atelier.workspace_guard import workspace_lock, project_revision


def model(s):
    d=s.info();return {'stations':deepcopy(d['stations']),'orders':deepcopy(d['orders'])}


def race_worker(folder,ready,go,result,name):
    s=Studio(Path(folder));ready.put(True);go.wait(15)
    try:s.rename_project(name);result.put('saved')
    except StudioError as exc:result.put(str(exc))


def test_stale_rename_preserves_saved_edit(tmp_path):
    a=Studio(tmp_path);b=Studio(tmp_path);m=model(a);m['orders'][0]['quantidade']+=1
    a.set_model(m);before=project_revision(tmp_path)
    with pytest.raises(StudioError,match='outra instância'):
        b.rename_project('Nome antigo bloqueado')
    assert project_revision(tmp_path)==before
    assert Studio(tmp_path).info()['orders'][0]['quantidade']==m['orders'][0]['quantidade']


def test_opening_and_inspection_do_not_write_or_invalidate_owner(tmp_path):
    a=Studio(tmp_path);before=project_revision(tmp_path)
    b=Studio(tmp_path);b.info();b.projects()
    assert project_revision(tmp_path)==before
    a.rename_project('Primeira continua válida')
    assert Studio(tmp_path).projects()[0]['name']=='Primeira continua válida'


@pytest.mark.parametrize('action',['reset','calculate','model','create','open','decision','experiment'])
def test_stale_writes_are_rejected_without_disk_or_memory_publish(tmp_path,action):
    a=Studio(tmp_path);b=Studio(tmp_path);m=model(a);m['orders'][0]['quantidade']+=1;a.set_model(m)
    before=project_revision(tmp_path);oldrun=b.info()['run_id']
    calls={'reset':lambda:b.reset(),'calculate':lambda:b.calculate({'duration_h':1}),
           'model':lambda:b.set_model(model(b)),'create':lambda:b.create_project('Cópia desatualizada'),
           'open':lambda:b.open_project('principal'),
           'decision':lambda:b.decision({'note':'Justificativa suficiente para registrar','constraints_ack':True}),
           'experiment':lambda:b.save_experiment('Experimento antigo')}
    with pytest.raises(StudioError,match='outra instância'):calls[action]()
    assert project_revision(tmp_path)==before
    assert b.info()['run_id']==oldrun
    assert not list((tmp_path/'registros').glob('*.json'))
    assert not list((tmp_path/'experimentos').glob('*.json'))


def test_external_edit_detected_and_restart_loads_new_data(tmp_path):
    a=Studio(tmp_path);p=tmp_path/'projetos/principal.json';d=json.loads(p.read_text());d['orders'][0]['quantidade']+=2;p.write_text(json.dumps(d))
    with pytest.raises(StudioError,match='outra instância'):a.rename_project('Conflito externo')
    b=Studio(tmp_path);assert b.info()['orders'][0]['quantidade']==d['orders'][0]['quantidade']
    b.rename_project('Reaberto com segurança')


def test_independent_workspaces_and_symlink_alias(tmp_path):
    a=Studio(tmp_path/'a');b=Studio(tmp_path/'b');a.rename_project('Pasta independente');b.rename_project('Outra pasta independente')
    alias=tmp_path/'alias'
    try:alias.symlink_to(tmp_path/'a',target_is_directory=True)
    except OSError:pytest.skip('Symlink unavailable on this machine')
    c=Studio(alias);a.rename_project('Nova revisão')
    with pytest.raises(StudioError):c.rename_project('Alias desatualizado')


def test_two_processes_cannot_both_commit_same_revision(tmp_path):
    Studio(tmp_path)
    ctx=multiprocessing.get_context('spawn');ready=ctx.Queue();results=ctx.Queue();go=ctx.Event()
    ps=[ctx.Process(target=race_worker,args=(str(tmp_path),ready,go,results,'Concorrente '+str(i))) for i in range(2)]
    try:
        for p in ps:p.start()
        for _ in ps:ready.get(timeout=20)
        go.set();out=[results.get(timeout=20) for _ in ps]
        assert out.count('saved')==1
        assert sum('outra instância' in x for x in out)==1
    finally:
        for p in ps:
            p.join(5)
            if p.is_alive():p.terminate();p.join(5)


def test_lock_released_after_process_crash_without_deleting_lockfile(tmp_path):
    code="from atelier.workspace_guard import workspace_lock;import sys;from pathlib import Path\nwith workspace_lock(Path(sys.argv[1])):\n print('locked',flush=True);sys.stdin.read()"
    child=subprocess.Popen([sys.executable,'-c',code,str(tmp_path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    try:
        assert child.stdout.readline().strip()=='locked'
        with pytest.raises(OSError,match='ocupado'):
            with workspace_lock(tmp_path,timeout=.1):pass
    finally:child.kill();child.wait(timeout=5)
    with workspace_lock(tmp_path,timeout=1):assert (tmp_path/'.workspace.lock').exists()
