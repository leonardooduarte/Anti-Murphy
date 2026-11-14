"""AM22 browser acceptance: numeric/localhost origins, assets, POST and export."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('AM22_QA_OUT','docs/AM22/capturas'));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for w,h in [(1280,720),(1366,768),(1920,1080)]:
        for host in ['127.0.0.1','localhost']:
            with TemporaryDirectory() as d:
                studio=Studio(Path(d));server.STUDIO=studio
                httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
                Thread(target=httpd.serve_forever,daemon=True).start()
                page=browser.new_page(viewport={'width':w,'height':h});errors=[];blocked=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('response',lambda r:blocked.append((r.url,r.status)) if r.status==403 else None)
                try:
                    page.goto(f'http://{host}:{httpd.server_port}/',wait_until='networkidle')
                    page.wait_for_selector('#factory-a .station-group')
                    page.evaluate('document.querySelector("#splash")?.remove()')
                    page.locator('[data-nav=modelo]').click()
                    with page.expect_response(lambda r:r.url.endswith('/api/model')) as ev:
                        page.locator('#model-save').click()
                    assert ev.value.ok
                    expect(page.locator('#view-simulacao')).to_be_visible()
                    result=page.evaluate("""async()=>{const r=await fetch('/api/model/export');return {status:r.status,body:await r.json()}}""")
                    assert result['status']==200 and result['body']['orders']
                    page.locator('[data-nav=paineis]').click()
                    expect(page.locator('#view-paineis')).to_be_visible()
                    page.screenshot(path=str(out/f'am22_{host}_{w}.png'))
                    assert not errors,errors
                    assert not blocked,blocked
                    print('AM22 BROWSER OK',host,w,h,flush=True)
                finally:page.close();httpd.shutdown();httpd.server_close()
    browser.close()
