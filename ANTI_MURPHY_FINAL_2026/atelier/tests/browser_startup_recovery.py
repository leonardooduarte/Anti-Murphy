"""Real HTTP recovery warning, preserved files and explicit save at three sizes."""
import json,os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('RECOVERY_QA_OUT','docs/RECUPERACAO/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for w,h in [(1280,720),(1366,768),(1920,1080)]:
        with TemporaryDirectory() as d:
            folder=Path(d);Studio(folder).calculate({'min_sla':73,'duration_h':5})
            (folder/'projeto_ativo.json').write_text('{"id":"../invalid"}')
            before={p:p.read_bytes() for p in folder.rglob('*.json')}
            studio=Studio(folder);server.STUDIO=studio
            httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            Thread(target=httpd.serve_forever,daemon=True).start()
            page=browser.new_page(viewport={'width':w,'height':h});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            try:
                page.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle')
                expect(page.locator('#toast')).to_contain_text('Abertura com recuperação')
                page.evaluate('document.querySelector("#splash")?.remove()')
                assert studio.info()['spec']['min_sla']==73
                assert all(p.read_bytes()==b for p,b in before.items())
                page.screenshot(path=str(out/f'recuperacao_{w}.png'))
                page.locator('[data-nav=modelo]').click()
                with page.expect_response(lambda r:r.url.endswith('/api/model')) as ev:
                    page.locator('#model-save').click()
                assert ev.value.ok
                assert not studio.info()['recovery_warning']
                assert Studio(folder).info()['spec']['min_sla']==73
                assert not errors,errors
                print('RECOVERY BROWSER OK',w,h,flush=True)
            finally:
                page.close();httpd.shutdown();httpd.server_close()
    browser.close()
