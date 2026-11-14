from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('PRIORITY_QA_OUT','docs/PRIORIDADE/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   s=Studio(Path(d));station=next(iter(s.state['stations'].values())).copy();station.update(maquinas=1,operadores=1)
   s.set_model({'stations':{'P':station},'orders':[{'id':'A','quantidade':2,'prazo_h':10,'multa_hora':1,'route':[['P',1]]}]});server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h});errors=[];posts=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
    def editor():
     p.locator('[data-nav=modelo]').click();p.locator('[data-model-tab=orders]').click()
    def save():
     with p.expect_response(lambda r:r.url.endswith('/api/model')) as ev:p.locator('#model-save').click()
     assert ev.value.ok
     expect(p.locator('#view-simulacao')).to_be_visible()
    editor();save();assert 'prioridade' not in s.state['orders'][0]
    editor();p.locator('[data-field=prioridade]').fill('0');save();assert s.state['orders'][0]['prioridade']==0
    editor();p.locator('[data-field=prioridade]').fill('');save();assert 'prioridade' not in s.state['orders'][0]
    editor();p.locator('[data-field=prioridade]').fill('1.5');count=len(posts);run=s.info()['run_id'];p.locator('#model-save').click()
    expect(p.locator('#toast')).to_contain_text('prioridade')
    assert len(posts)==count and s.info()['run_id']==run and 'prioridade' not in s.state['orders'][0]
    p.screenshot(path=str(out/f'prioridade_{w}.png'));assert not errors,errors
    print('PRIORITY BROWSER OK',w,h,flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
