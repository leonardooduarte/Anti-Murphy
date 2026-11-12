from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('AM16_QA_OUT','docs/AM16/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   s=Studio(Path(d));result=s.advanced({'mode':'uncertainty'});server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h});pending=[];errors=[]
   p.on('pageerror',lambda e:errors.append(str(e)))
   def hold(route):
    if route.request.post_data_json.get('mode')=='uncertainty':pending.append(route)
    else:route.continue_()
   p.route('**/api/advanced',hold)
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
    p.locator('[data-nav=paineis]').click();p.locator('[data-dash-tab=robustez]').click()
    action=p.locator('[data-dash-robust-run]');action.click();expect(action).to_be_disabled()
    action.dispatch_event('click');p.wait_for_timeout(100);assert len(pending)==1
    p.locator('[data-dash-tab=operacao]').click();p.locator('[data-dash-tab=robustez]').click();expect(p.locator('[data-dash-robust-run]')).to_be_disabled()
    p.locator('[data-nav=avancadas]').click();p.locator('[data-advanced=uncertainty]').click();expect(p.locator('#advanced-run')).to_be_disabled()
    p.locator('[data-advanced=diagnostic]').click();expect(p.locator('#advanced-run')).to_be_enabled()
    p.locator('[data-advanced=uncertainty]').click();expect(p.locator('#advanced-run')).to_be_disabled()
    pending[0].fulfill(status=500,json={'error':'Falha controlada de teste'})
    expect(p.locator('#advanced-run')).to_be_enabled()
    p.locator('#advanced-run').click();expect(p.locator('#advanced-run')).to_be_disabled()
    p.locator('[data-nav=paineis]').click();p.locator('[data-dash-tab=robustez]').click();expect(p.locator('[data-dash-robust-run]')).to_be_disabled()
    p.wait_for_timeout(100);assert len(pending)==2
    p.screenshot(path=str(out/f'andamento_{w}.png'))
    pending[1].fulfill(status=200,json=result)
    expect(p.locator('[data-dash-robust-run]')).to_be_enabled()
    assert not errors,errors
    print('AM16 BROWSER OK',w,h,'duplo clique, navegação, duas entradas, erro e repetição',flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
