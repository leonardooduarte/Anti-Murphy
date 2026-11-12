from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('AM13_QA_OUT','docs/AM13/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   s=Studio(Path(d));station=next(iter(s.state['stations'].values())).copy();station.update(maquinas=1,operadores=1)
   s.set_model({'stations':{'P':station},'orders':[{'id':oid,'quantidade':1,'prioridade':1,'prazo_h':due,'multa_hora':10,'route':[['P',1]]} for oid,due in [('OP-1',1),('OP-10',10)]]})
   s.select(s.info()['alternatives'][0]['signature'])
   original=s.info()['run_id'];server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()');p.locator('[data-nav=decisoes]').click()
    for question,expected in [('Quando termina o pedido OP-10?','Pedido OP-10 · prazo 10,00 h'),('Quando termina o pedido OP-1?','Pedido OP-1 · prazo 1,00 h'),('Prazo do pedido OP-100?','não existe'),('Compare pedido OP-1 e OP-10','mais de um')]:
     p.locator('#assistant-input').fill(question)
     with p.expect_response(lambda r:r.url.endswith('/api/assistant')) as ev:p.locator('#assistant-form button').click()
     assert expected in ev.value.json()['text'];expect(p.locator('.assistant-message').last).to_contain_text(expected)
    p.locator('#assistant-messages').screenshot(path=str(out/f'murphy_{w}.png'))
    assert not errors and s.info()['run_id']==original and not s.history()
    print('AM13 BROWSER OK',w,h,flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
