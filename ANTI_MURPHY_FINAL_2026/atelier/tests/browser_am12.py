"""Real HTTP conflict notice; no persistent user workspace is touched."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from copy import deepcopy
import os
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server
out=Path(os.environ.get('AM12_QA_OUT','docs/AM12/capturas'));out.mkdir(parents=True,exist_ok=True)
with TemporaryDirectory() as d, sync_playwright() as pw:
    primary=Studio(Path(d));other=Studio(Path(d));server.STUDIO=primary
    httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    try:
        page=browser.new_page(viewport={'width':1366,'height':768})
        page.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');page.wait_for_selector('#factory-a .station-group');page.evaluate('document.querySelector("#splash")?.remove()')
        m={'stations':deepcopy(other.info()['stations']),'orders':deepcopy(other.info()['orders'])};m['orders'][0]['quantidade']+=1;other.set_model(m)
        page.locator('#project-manager').click();page.locator('#project-rename-name').fill('Gravação bloqueada')
        with page.expect_response(lambda r:r.url.endswith('/api/project/rename')) as event:page.locator('#project-rename').click()
        assert event.value.status==400
        expect(page.locator('#toast')).to_contain_text('outra instância')
        assert Studio(Path(d)).info()['orders'][0]['quantidade']==m['orders'][0]['quantidade']
        page.screenshot(path=str(out/'conflito_gravacao.png'))
        print('AM12 HTTP/browser: conflito400, aviso visível, edição mais recente preservada')
    finally:browser.close();httpd.shutdown();httpd.server_close()
