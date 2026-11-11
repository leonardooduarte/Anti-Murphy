"""Real-HTTP archived economic comparison, including legacy missing components."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from copy import deepcopy
import json,os
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server
out=Path(os.environ.get('AM08_QA_OUT','docs/AM08/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 try:
  for w,h in [(1280,720),(1366,768),(1920,1080)]:
   with TemporaryDirectory() as d:
    s=Studio(Path(d));rows=s.info()['alternatives']
    s.select(next(x['signature'] for x in rows if x['action']=='Não intervir'));a=s.save_experiment('Referência sem ação')
    s.select(next(x['signature'] for x in rows if x['action'].startswith('Manutenção expressa')));b=s.save_experiment('Manutenção expressa')
    legacy=deepcopy(a);legacy.pop('economics');legacy['id']='legacy01';legacy['name']='Arquivo antigo';path=s.experiments_dir/'legacy01.json';path.write_text(json.dumps(legacy));original=path.read_bytes()
    server.STUDIO=s;httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
    page=browser.new_page(viewport={'width':w,'height':h});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
     page.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');page.wait_for_selector('#factory-a .station-group');page.evaluate('document.querySelector("#splash")?.remove()');page.locator('[data-nav=analise]').click()
     page.locator('#experiment-first').select_option(a['id']);page.locator('#experiment-second').select_option(b['id']);page.locator('#experiment-compare').click()
     expect(page.locator('[data-economic-component=investment] td').nth(2)).to_contain_text('1.800,00')
     expect(page.locator('[data-economic-component=decision_cost] td').nth(2)).to_contain_text('12.113,00')
     expect(page.locator('[data-economic-component=savings] td').nth(2)).to_contain_text('4.103,68')
     expect(page.locator('[data-economic-component=decision_cost] td').nth(3)).to_contain_text('4.103,68')
     expect(page.locator('[data-economic-component=scenario_cost] td').nth(3)).to_contain_text('5.903,68')
     page.locator('[data-archived-economics]').screenshot(path=str(out/f'componentes_{w}.png'))
     page.locator('#experiment-first').select_option('legacy01');page.locator('#experiment-compare').click()
     expect(page.locator('[data-economic-component=investment] td').nth(1)).to_contain_text('Não registrado')
     expect(page.locator('#experiment-comparison')).to_contain_text('Comparação econômica parcial')
     assert path.read_bytes()==original;assert not errors,errors
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
     print('AM08 BROWSER OK',w,h,'componentes separados, legado não regravado, sem erroJS',flush=True)
    finally:page.close();httpd.shutdown();httpd.server_close()
 finally:browser.close()
