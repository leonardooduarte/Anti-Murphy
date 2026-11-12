from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import os
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('AM14_QA_OUT','docs/AM14/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   s=Studio(Path(d));first=s.decision({'note':'Escolha baseada nos resultados calculados.','constraints_ack':True});name=first['record']['project_name']
   s.rename_project('Nome alterado');s.create_project('Projeto B');s.decision({'note':'Segunda decisão para verificar a origem.','constraints_ack':True})
   files={p.name:p.read_bytes() for p in (Path(d)/'registros').glob('*.json')};server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()');p.locator('[data-nav=historico]').click()
    expect(p.locator('.history-item')).to_have_count(2)
    expect(p.locator('#history-list')).to_contain_text('Projeto B')
    expect(p.locator('#history-list')).to_contain_text(name+' (principal)')
    p.locator('.history-item').filter(has_text='(principal)').click()
    expect(p.locator('#history-detail')).to_contain_text(name+' (principal)')
    expect(p.locator('#history-detail')).to_contain_text('nome arquivado na decisão')
    p.screenshot(path=str(out/f'origem_{w}.png'))
    assert not errors and files=={f.name:f.read_bytes() for f in (Path(d)/'registros').glob('*.json')}
    print('AM14 BROWSER OK',w,h,flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
