"""Real-HTTP mixed archives: visible diagnostics, valid saves/comparisons and legacy."""
import json,os
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
from atelier import server
from atelier.service import Studio

out=Path(os.environ.get('INT03_QA_OUT','docs/INT03/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   folder=Path(d);s=Studio(folder);first=s.save_experiment('Referência válida');s.calculate({'duration_h':10});second=s.save_experiment('Comparação válida')
   legacy=deepcopy(first);legacy.pop('economics');legacy['id']='legacy';legacy['name']='Histórico legado'
   (s.experiments_dir/'legacy.json').write_text(json.dumps(legacy))
   for name,raw in [('invalid.json',b'[]'),('truncated.json',b'{broken'),('<img src=x>.json',b'null')]:
    (s.experiments_dir/name).write_bytes(raw)
   originals={p:p.read_bytes() for p in s.experiments_dir.iterdir()};before=s.info();server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   def open_analysis():
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()');p.locator('[data-nav=analise]').click()
   try:
    open_analysis();expect(p.locator('#experiment-count')).to_have_text('3 arquivados')
    expect(p.locator('#experiment-warnings')).to_contain_text('3 arquivo(s)')
    p.locator('#experiment-warnings summary').click()
    expect(p.locator('#experiment-warnings')).to_contain_text('<img src=x>.json')
    assert p.locator('#experiment-warnings img').count()==0
    p.screenshot(path=str(out/f'biblioteca_{w}.png'))
    # Old clients still receive an array, not the new diagnostic envelope.
    old=p.request.get(f'http://127.0.0.1:{httpd.server_port}/api/experiments');assert old.ok and len(old.json())==3
    p.locator('#experiment-first').select_option(first['id']);p.locator('#experiment-second').select_option(second['id'])
    with p.expect_response(lambda r:r.url.endswith('/api/experiment/compare')) as ev:p.locator('#experiment-compare').click()
    assert ev.value.ok
    expect(p.locator('[data-economic-component=investment]')).to_be_visible()
    p.locator('#experiment-first').select_option('legacy')
    with p.expect_response(lambda r:r.url.endswith('/api/experiment/compare')) as ev:p.locator('#experiment-compare').click()
    assert ev.value.ok
    expect(p.locator('#experiment-comparison')).to_contain_text('Comparação econômica parcial')
    p.locator('#experiment-name').fill('Novo válido com avisos')
    with p.expect_response(lambda r:r.url.endswith('/api/experiment/save')) as ev:p.locator('#experiment-save').click()
    assert ev.value.ok
    expect(p.locator('#experiment-count')).to_have_text('4 arquivados')
    expect(p.locator('#experiment-warnings')).to_be_visible()
    assert all(p.read_bytes()==raw for p,raw in originals.items())
    assert s.info()==before
    original_project=s.project_id;s.create_project('Outro projeto');open_analysis()
    expect(p.locator('#experiment-count')).to_have_text('0 arquivados')
    expect(p.locator('#experiment-list')).not_to_contain_text('Referência válida')
    assert p.locator('#experiment-compare').is_disabled()
    s.open_project(original_project);open_analysis();expect(p.locator('#experiment-count')).to_have_text('4 arquivados')
    # Repair is external and explicit; the application only rereads it.
    fixed=deepcopy(first);fixed['id']='invalid';(s.experiments_dir/'invalid.json').write_text(json.dumps(fixed))
    open_analysis();expect(p.locator('#experiment-warnings')).to_contain_text('2 arquivo(s)')
    assert not errors,errors
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
    print('INT03 BROWSER OK',w,h,'avisos, nomes escapados, legado, listagem antiga, comparação/gravação, projetos e releitura',flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
