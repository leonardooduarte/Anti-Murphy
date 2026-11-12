"""Real HTTP workload preview, safe rejection, editing recovery, and saved large model."""
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import sync_playwright, expect

from atelier import server
from atelier.service import Studio

OUT=Path(os.environ.get('AM17_QA_OUT','docs/AM17/capturas'));OUT.mkdir(parents=True,exist_ok=True)


def model():
    return {'stations':{'P':{'nome':'Célula de produção','maquinas':1,'operadores':1,
            'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,
            'custo_maquina_h':10,'custo_operador_h':10,'setup_min':0}},
            'orders':[{'id':'A','quantidade':100,'prazo_h':100,'multa_hora':10,'route':[['P',1]]*12}]}


with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    try:
        for width,height in [(1280,720),(1366,768),(1920,1080)]:
            with TemporaryDirectory() as storage:
                studio=Studio(Path(storage));studio.set_model(model());server.STUDIO=studio
                httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
                Thread(target=httpd.serve_forever,daemon=True).start()
                page=browser.new_page(viewport={'width':width,'height':height});errors=[];posts=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
                try:
                    def open_editor():
                        page.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle')
                        page.wait_for_selector('#status-run')
                        page.evaluate('document.querySelector("#splash")?.remove()')
                        page.locator('[data-nav=modelo]').click()
                        expect(page.locator('#model-workload')).to_be_visible()
                        page.locator('[data-model-tab=orders]').click()
                    open_editor()
                    expect(page.locator('#model-workload strong')).to_contain_text('1.200')
                    page.locator('#model-workload').screenshot(path=str(OUT/f'dimensao_{width}.png'))
                    before=studio.info()['run_id'];initial_posts=len(posts)
                    page.locator('input[data-field=quantidade]').fill('2500')
                    expect(page.locator('#model-workload')).to_have_class('model-workload workload-over')
                    expect(page.locator('#model-workload strong')).to_contain_text('30.000')
                    assert len(posts)==initial_posts  # Preview does not run a simulation.
                    page.locator('#model-workload').screenshot(path=str(OUT/f'limite_{width}.png'))
                    with page.expect_response(lambda r:r.url.endswith('/api/model')) as ev:
                        page.locator('#model-save').click()
                    assert ev.value.status==400 and 'Nenhum resultado foi substituído' in ev.value.json()['error']
                    assert studio.info()['run_id']==before and studio.state['orders'][0]['quantidade']==100
                    page.locator('input[data-field=quantidade]').fill('10')
                    with page.expect_response(lambda r:r.url.endswith('/api/model')) as ev:
                        page.locator('#model-save').click()
                    assert ev.value.ok
                    expect(page.locator('#view-simulacao')).to_be_visible()
                    assert studio.state['orders'][0]['quantidade']==10
                    # An already saved large project remains editable without rewriting.
                    path=Path(storage)/'projetos/principal.json'
                    data=json.loads(path.read_text());data['orders'][0]['quantidade']=2500
                    path.write_text(json.dumps(data));saved=path.read_bytes()
                    server.STUDIO=Studio(Path(storage))
                    assert server.STUDIO.info()['calculation_blocked'] and path.read_bytes()==saved
                    open_editor()
                    expect(page.locator('#model-workload strong')).to_contain_text('30.000')
                    page.locator('input[data-field=quantidade]').fill('10')
                    with page.expect_response(lambda r:r.url.endswith('/api/model')) as ev:
                        page.locator('#model-save').click()
                    assert ev.value.ok and not server.STUDIO.info()['calculation_blocked']
                    assert not errors,errors
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
                    print(json.dumps({'resolution':[width,height],'preview_without_simulation':True,
                                      'safe_rejection':True,'saved_large_model_editable':True,'errors':errors}),flush=True)
                finally:
                    page.close();httpd.shutdown();httpd.server_close()
    finally:
        browser.close()
