"""INT01 real HTTP/file download/upload acceptance at three viewports."""
import json,os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('INT01_QA_OUT','docs/INT01/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   folder=Path(d);s=Studio(folder);server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h},accept_downloads=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   def reload():
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
   def upload(model):
    p.locator('[data-nav=modelo]').click()
    with p.expect_response(lambda r:r.url.endswith('/api/model')) as ev:
     p.locator('#model-file').set_input_files({'name':'modelo.json','mimeType':'application/json','buffer':json.dumps(model).encode()})
    return ev.value
   try:
    for rule in ['EDD','SPT','FIFO']:
     s.calculate({'rule':rule});reload();reference=s.info()['metrics']['normal'];source=s.project_id
     with p.expect_download() as ev:p.locator('#header-export').click()
     model=json.loads(Path(ev.value.path()).read_text());assert model['dispatch_rule']==rule
     p.locator('#project-manager').click();p.locator('#project-new-name').fill(f'Destino {rule} {w}');p.locator('#project-duplicate').check()
     with p.expect_response(lambda r:r.url.endswith('/api/project/create')) as ev:p.locator('#project-create').click()
     assert ev.value.ok
     s.calculate({'rule':'EDD' if rule!='EDD' else 'SPT'});reload()
     assert s.project_id!=source
     response=upload(model);assert response.ok
     expect(p.locator('#toast')).to_contain_text('Regra de despacho do arquivo preservada')
     assert s.info()['rule']==rule and s.info()['metrics']['normal']==reference
     assert Studio(folder).info()['rule']==rule
    legacy=dict(model);legacy.pop('dispatch_rule');assert upload(legacy).ok
    expect(p.locator('#toast')).to_contain_text('Arquivo sem regra: mantida a regra de despacho atual')
    assert s.info()['rule']=='FIFO'
    for invalid in [None,'spt',[]]:
     bad=json.loads(json.dumps(model));bad['dispatch_rule']=invalid;bad['orders'][0]['quantidade']+=1
     before=s.info();disk={p:p.read_bytes() for p in folder.rglob('*.json')}
     assert upload(bad).status==400
     expect(p.locator('#toast')).to_contain_text('Regra de despacho inválida')
     assert s.info()==before and all(p.read_bytes()==data for p,data in disk.items())
    p.screenshot(path=str(out/f'importacao_{w}.png'));assert not errors,errors
    print('INT01 BROWSER OK',w,h,'EDD/SPT/FIFO, outro projeto, download/upload, legado, inválidos e reabertura',flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
