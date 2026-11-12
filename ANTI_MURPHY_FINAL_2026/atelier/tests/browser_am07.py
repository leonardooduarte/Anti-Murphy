from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('AM07_QA_OUT','docs/AM07/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   s=Studio(Path(d));station=next(iter(s.state['stations'].values())).copy()
   station.update(maquinas=1,operadores=1,setup_min=0)
   s.set_model({'stations':{'P':station},'orders':[{'id':'A','quantidade':1001,'prioridade':1,'prazo_h':1000,'multa_hora':1,'route':[['P',1]]*12}]})
   server.STUDIO=s;httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':width,'height':height});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
    expect(p.locator('#event-log')).to_contain_text('Modo reduzido')
    p.locator('#factory-a .station-group').first.click()
    expect(p.locator('#station-inspector')).to_contain_text('Modo reduzido')
    p.screenshot(path=str(out/f'reduzido_{width}.png'))
    assert not errors,errors
    print('AM07 BROWSER OK',width,height,flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
