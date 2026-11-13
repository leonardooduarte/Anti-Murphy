"""Executable distribution checks, isolated from installed user workspaces."""
import json
import os
from pathlib import Path
from queue import Queue,Empty
import re
import shutil
import subprocess
import sys
from threading import Thread
import time
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]


def test_offline_previews_are_reproducible_without_touching_workspace(tmp_path):
    from tools.build_previews import build,preview_html
    for rel in ['factory_command_demo.json','ui/factory_studio.html','assets/brand/logo-light.svg']:
        p=tmp_path/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,p)
    workspace=tmp_path/'workspace';workspace.mkdir();sentinel=workspace/'project.json';sentinel.write_text('{"preserve":true}')
    build(tmp_path);expected=preview_html(tmp_path)
    first=[(tmp_path/n).read_bytes() for n in ['PREVIEW_OPERACAO.html','PREVIEW_FACTORY_COMMAND.html']]
    build(tmp_path)
    assert all(x==expected.encode('utf-8') for x in first)
    assert first==[(tmp_path/n).read_bytes() for n in ['PREVIEW_OPERACAO.html','PREVIEW_FACTORY_COMMAND.html']]
    assert sentinel.read_text()=='{"preserve":true}'


def test_real_primary_launcher_serves_local_app_without_site_packages(tmp_path):
    app=tmp_path/'app';shutil.copytree(ROOT,app,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
    process=subprocess.Popen([sys.executable,'-S','start.py','--no-browser','--port','0'],cwd=app,
        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    output=[];queue=Queue()
    def read():
        for line in process.stdout:output.append(line);queue.put(line)
    thread=Thread(target=read,daemon=True);thread.start()
    try:
        deadline=time.monotonic()+20;url=None
        while time.monotonic()<deadline:
            try:line=queue.get(timeout=.2)
            except Empty:
                assert process.poll() is None,''.join(output)
                continue
            found=re.search(r'http://127\.0\.0\.1:\d+',line)
            if found:url=found.group();break
        assert url,''.join(output)
        for path in ['/','/app.js','/experience_v01.css','/analysis_state.js','/api/state','/api/dashboards']:
            with urlopen(url+path,timeout=10) as response:
                raw=response.read();assert response.status==200 and raw,path
                if path=='/':assert b'experience-story' in raw and b'Modo banca' in raw
                if path=='/api/state':assert json.loads(raw)['run_id']
        assert process.poll() is None
    finally:
        process.terminate();process.wait(timeout=5);thread.join(timeout=2)
