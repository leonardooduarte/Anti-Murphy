"""Real DES stress sample and CSV/SVG contract in three viewports."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os,csv,io
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server
out=Path(os.environ.get('AM09_QA_OUT','docs/AM09/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 try:
  for width,height in [(1280,720),(1366,768),(1920,1080)]:
   with TemporaryDirectory() as d:
    s=Studio(Path(d));s.set_model({'stations':{'P':{'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':10,'setup_min':0}},'orders':[{'id':'A','quantidade':20,'prazo_h':100,'multa_hora':10,'route':[('P',60)]}]});server.STUDIO=s
    httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
    p=b.new_page(viewport={'width':width,'height':height},accept_downloads=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
     p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()');p.locator('[data-nav=laboratorio]').click();p.locator('[data-lab=stress]').click()
     with p.expect_response(lambda r:r.url.endswith('/api/lab')) as ev:p.locator('#run-lab').click()
     r=ev.value.json();valid=r['summary']['viable_runs'];invalid=r['summary']['infeasible_runs'];assert invalid==11 and valid==5
     expect(p.locator('#lab-results [data-analysis-sample]')).to_contain_text('Viáveis: 5 · Inviáveis: 11')
     expect(p.locator('#lab-results .eng-point')).to_have_count(5)
     with p.expect_download() as ev:p.locator('#lab-results [data-eng-export]').click()
     text=Path(ev.value.path()).read_text('utf-8-sig');rows=list(csv.reader(io.StringIO(text),delimiter=';'));assert 'Amostra: 5 viáveis de 16' in rows[0][0]
     data=[dict(zip(rows[1],row)) for row in rows[2:]];bad=[x for x in data if x['feasible']=='false'];assert len(bad)==11;assert all(x['makespan_h']=='' and x['unit_cost']=='' and x['reason'] for x in bad)
     with p.expect_download() as ev:p.locator('#lab-results [data-eng-export-svg]').click()
     svg=Path(ev.value.path()).read_text();assert '5 viáveis de 16' in svg
     p.locator('#lab-results .eng-suite').screenshot(path=str(out/f'amostra_{width}.png'))
     assert not errors,errors;assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
     print('AM09 BROWSER OK',width,height,'5 pontos válidos,11 inviáveis preservados,CSV/SVG amostra explícita',flush=True)
    finally:p.close();httpd.shutdown();httpd.server_close()
 finally:b.close()
