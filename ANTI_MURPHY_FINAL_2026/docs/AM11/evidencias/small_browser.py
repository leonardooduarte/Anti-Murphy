from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import json
from playwright.sync_api import sync_playwright
from atelier.service import Studio
from atelier import server
out=Path(__file__).resolve().parent
with TemporaryDirectory() as tmp, patch('simulation.engine._noise',return_value=1):
 s=Studio(Path(tmp))
 v=s.set_model({'stations':{'P':{'nome':'Posto','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':20,'setup_min':0}},'orders':[{'id':'A','cliente':'C','produto':'X','quantidade':1,'prazo_h':1,'multa_hora':100,'route':[['P',.06]]}]})
 server.STUDIO=s
 httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
 Thread(target=httpd.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
   page=b.new_page(viewport={'width':1366,'height':768});errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle')
   page.wait_for_selector('#factory-a .station-group')
   page.evaluate('document.querySelector("#splash")?.remove()')
   page.locator('[data-nav=analise]').click()
   text=page.locator('#view-analise').inner_text()
   assert '0,001' in text, text
   assert not errors,errors
   page.screenshot(path=str(out/'ciclo_curto_browser.png'),full_page=True)
   (out/'ciclo_curto_browser.json').write_text(json.dumps({'metrics':v['metrics'],'page_errors':errors,'short_time_visible':True},ensure_ascii=False,indent=2))
   print('CICLO CURTO HTTP BROWSER OK: 0,001 h visível, sem erro JS')
   b.close()
 finally:httpd.shutdown();httpd.server_close()
