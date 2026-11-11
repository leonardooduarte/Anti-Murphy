"""Bootstrap regressions independent from the Streamlit UI and a Windows shell."""
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from tools import start_nexus as boot


@pytest.mark.parametrize('version,expected',[((3,10,20),False),((3,11,0),True),((3,12,14),True),((3,14,0),True),((3,15,0),True),((3,16,0),True)])
def test_python_versions_are_checked_against_dependency_minimum(version,expected):
    assert boot.supported(version)==expected


def test_existing_environment_is_reused_without_global_python_or_reinstallation(tmp_path,monkeypatch):
    root=tmp_path/'project with spaces';target=boot.environment_python(root,windows=True)
    target.parent.mkdir(parents=True);target.touch()
    monkeypatch.setattr(boot,'interpreter_info',lambda executable:{'version':[3,12,0]})
    create=Mock(side_effect=AssertionError('Existing environment must be reused'))
    monkeypatch.setattr(boot,'create_environment',create)
    assert boot.ensure_environment(root,boot.Log(tmp_path/'start.log'),windows=True)==target
    create.assert_not_called()


def test_broken_venv_is_preserved_and_new_one_is_verified(tmp_path,monkeypatch):
    root=tmp_path/'project';old=root/'.venv';old.mkdir(parents=True)
    (old/'user_marker.txt').write_text('preserve')
    monkeypatch.setattr(boot,'interpreter_info',lambda executable:{'version':[3,12,0]} if Path(executable).is_file() else None)
    def create(directory):
        target=directory/'Scripts/python.exe';target.parent.mkdir(parents=True);target.touch()
    monkeypatch.setattr(boot,'create_environment',create)
    selected=boot.ensure_environment(root,boot.Log(tmp_path/'start.log'),windows=True)
    assert selected.is_file()
    backups=list(root.glob('.venv_anterior_*'))
    assert len(backups)==1 and (backups[0]/'user_marker.txt').read_text()=='preserve'


def test_pip_failure_keeps_original_error_and_stops_before_launch(tmp_path,monkeypatch):
    monkeypatch.setattr(boot,'dependencies_ready',lambda _:False)
    calls=[]
    def run(args,root,log):
        calls.append(args)
        if 'install' in args:
            log.write('ERROR: original pip diagnostic')
            return 1
        return 0
    monkeypatch.setattr(boot,'run_logged',run)
    logfile=tmp_path/'start.log'
    with pytest.raises(boot.StartupError,match='instalacao de dependencias falhou'):
        boot.ensure_dependencies('python path with spaces.exe',tmp_path,boot.Log(logfile))
    assert 'original pip diagnostic' in logfile.read_text()
    assert all('streamlit' not in c for c in calls)


def test_launch_argument_array_preserves_spaces_without_shell_interpolation(tmp_path):
    root=tmp_path/'Anti Murphy';python=root/'.venv/Scripts/python.exe'
    args=boot.launch_arguments(python,root)
    assert args[0]==str(python)
    assert args[4]==str(root/'app.py')
    assert args[-1]=='--server.address=127.0.0.1'


def test_diagnostics_checks_project_without_installing_or_starting(tmp_path,monkeypatch):
    (tmp_path/'app.py').touch();(tmp_path/'requirements.txt').touch()
    fail=Mock(side_effect=AssertionError('Diagnostic should not install'))
    monkeypatch.setattr(boot,'ensure_environment',fail)
    assert boot.main([str(tmp_path),str(tmp_path/'diagnostic.txt'),'--diagnose-only'])==0
    fail.assert_not_called()


def test_invalid_or_missing_interpreter_is_reported_cleanly(tmp_path):
    assert boot.interpreter_info(tmp_path/'does-not-exist.exe') is None
    actual=boot.interpreter_info(sys.executable)
    assert actual and boot.supported(actual['version'])


def test_incomplete_project_returns_actionable_error(tmp_path):
    log=tmp_path/'diagnostic.txt'
    assert boot.main([str(tmp_path),str(log),'--diagnose-only'])==1
    assert 'Extraia o ZIP completo' in log.read_text()


def test_python315_requirements_select_binary_compatible_pandas_profile():
    from packaging.requirements import Requirement
    file=Path(__file__).resolve().parents[1]/'requirements.txt'
    specs=[Requirement(line) for line in file.read_text().splitlines() if line.strip() and not line.startswith(('#','--'))]
    def pandas_spec(version):
        return next(r for r in specs if r.name=='pandas' and (r.marker is None or r.marker.evaluate({'python_version':version})))
    assert '3.0.6' in pandas_spec('3.15').specifier
    assert '2.3.3' not in pandas_spec('3.15').specifier
    assert '2.2.3' in pandas_spec('3.12').specifier


def test_dependency_installer_forbids_source_builds(tmp_path,monkeypatch):
    ready=iter([False,True]);monkeypatch.setattr(boot,'dependencies_ready',lambda _:next(ready))
    calls=[]
    monkeypatch.setattr(boot,'run_logged',lambda args,*rest:calls.append(args) or 0)
    boot.ensure_dependencies('python.exe',tmp_path,boot.Log(tmp_path/'startup.log'))
    install=next(c for c in calls if 'install' in c)
    assert '--only-binary=:all:' in install
    assert str(tmp_path/'requirements.txt') in install


def test_user_repair_instruction_keeps_requirements_file_valid(tmp_path):
    from packaging.requirements import Requirement
    old=tmp_path/'requirements.txt';old.write_text('streamlit>=1.66,<2\npandas>=2.2,<3\nnumpy>=1.26,<3\nplotly>=5.22,<8\nopenpyxl>=3.1,<4\n')
    old.write_text('--only-binary=:all:\n'+old.read_text().replace('pandas>=2.2,<3\n','pandas==3.0.6\n'))
    pandas=next(Requirement(line) for line in old.read_text().splitlines() if line.startswith('pandas'))
    assert '3.0.6' in pandas.specifier
    assert '--only-binary=:all:' in old.read_text()
