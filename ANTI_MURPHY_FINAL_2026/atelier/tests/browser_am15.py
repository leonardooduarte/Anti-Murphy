from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os,json
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('AM15_QA_OUT','docs/AM15/capturas'));out.mkdir(parents=True,exist_ok=True)
web=server.WEB
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  for n in [1,5,9,16,50]:
   with TemporaryDirectory() as d:
    s=Studio(Path(d));station=next(iter(s.state['stations'].values())).copy();station.update(maquinas=1,operadores=1)
    s.set_model({'stations':{f'P{i}':{**station,'nome':f'Célula de produção {i}'} for i in range(n)},'orders':[{'id':'A','quantidade':2,'prioridade':1,'prazo_h':100,'multa_hora':1,'route':[['P0',1]]}]})
    server.STUDIO=s;httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
    p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
     # Measure the shipped AM14 at the same viewport/model before the new UI.
     if w==1366 and n==9 and os.environ.get('AM15_BASE_WEB'):
      server.WEB=Path(os.environ['AM15_BASE_WEB'])
      p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('.station-group')
      print('BEFORE',json.dumps(p.locator('#factory-a .station-name').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a')),flush=True)
      server.WEB=web;p.close();p=b.new_page(viewport={'width':w,'height':h});p.on('pageerror',lambda e:errors.append(str(e)))
     p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
     expect(p.locator('#factory-a .station-group')).to_have_count(n)
     if n<=5:p.locator('#factory-readout summary').click()
     expect(p.locator('[data-readable-station]')).to_have_count(n)
     if n==9:print('AFTER OVERVIEW',w,p.locator('#factory-a .station-name').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a'),flush=True)
     before=s.info()['run_id']
     last=p.locator('[data-readable-station]').last;last.scroll_into_view_if_needed();last.focus();last.press('Enter')
     expect(p.locator('#factory-a')).to_have_attribute('viewBox',__import__('re').compile(r'.*400 320$'))
     px=p.locator('#factory-a .station-name').last.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a')
     assert px>=12,(w,n,px)
     assert p.locator('[data-readable-station] strong').last.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=14
     p.locator('[data-inspect-focus]').click()
     expect(p.locator('#factory-a')).not_to_have_attribute('viewBox',__import__('re').compile(r'.*400 320$'))
     assert not errors and s.info()['run_id']==before,errors
     if n==9:
      p.locator('#factory-viewport').scroll_into_view_if_needed();p.screenshot(path=str(out/f'planta9_{w}.png'))
     print('AM15 BROWSER OK',w,h,n,'focus font px',round(px,2),flush=True)
    finally:p.close();server.WEB=web;httpd.shutdown();httpd.server_close()
 b.close()
