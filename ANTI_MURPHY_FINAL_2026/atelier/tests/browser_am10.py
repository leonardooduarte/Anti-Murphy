"""Real HTTP capacity enumeration and explicit search-space exports."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os,csv,io,json
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server
out=Path(os.environ.get('AM10_QA_OUT','docs/AM10/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 try:
  for w,h in [(1280,720),(1366,768),(1920,1080)]:
   with TemporaryDirectory() as d:
    s=Studio(Path(d));s.set_model({'stations':{'P':{'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':10,'setup_min':0}},'orders':[{'id':'A','quantidade':20,'prazo_h':100,'multa_hora':10,'route':[('P',60)]}]});server.STUDIO=s
    httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
    p=b.new_page(viewport={'width':w,'height':h},accept_downloads=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
     p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()');p.locator('[data-nav=laboratorio]').click();p.locator('[data-lab=capacity]').click();p.locator('#goal-value').fill('80');p.locator('#throughput-value').fill('1.5')
     with p.expect_response(lambda r:r.url.endswith('/api/lab')) as ev:p.locator('#run-lab').click()
     result=ev.value.json();assert result['search_space']['candidates_evaluated']==5
     assert result['points'][0]['goal_met'];changes=json.loads(result['points'][0]['changes']);assert {x['resource'] for x in changes}=={'operadores','maquinas'}
     expect(p.locator('[data-capacity-search]')).to_contain_text('5 candidatos avaliados')
     expect(p.locator('#lab-results .eng-point')).to_have_count(5)
     with p.expect_download() as ev:p.locator('#lab-results [data-eng-export]').click()
     text=Path(ev.value.path()).read_text('utf-8-sig');rows=list(csv.reader(io.StringIO(text),delimiter=';'));assert 'Busca: 5 candidatos' in rows[0][0]
     assert any('operadores' in line and 'maquinas' in line for line in text.splitlines()[2:])
     with p.expect_download() as ev:p.locator('#lab-results [data-eng-export-svg]').click()
     svg=Path(ev.value.path()).read_text();assert '5 avaliados / 5 exibidos' in svg
     p.locator('#lab-results').screenshot(path=str(out/f'busca_{w}.png'))
     assert not errors,errors;assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
     print('AM10 BROWSER OK',w,h,'combinação local encontra meta, espaço e exportações identificados',flush=True)
    finally:p.close();httpd.shutdown();httpd.server_close()
 finally:b.close()
