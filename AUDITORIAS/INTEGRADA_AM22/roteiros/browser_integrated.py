from pathlib import Path
import os
import sys,json,tempfile,time
from threading import Thread
from http.server import ThreadingHTTPServer
sys.path.insert(0,os.environ['ANTI_MURPHY_AUDIT_APP'])
from atelier.service import Studio
from atelier import server
from playwright.sync_api import sync_playwright,expect
r=Path(os.environ['ANTI_MURPHY_AUDIT_OUT']);out=r/'capturas-integradas';out.mkdir(exist_ok=True);results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with tempfile.TemporaryDirectory() as d:
   s=Studio(Path(d));s.calculate({'rule':'SPT'});exported=s.export_model();s.calculate({'rule':'EDD'});server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=browser.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   row={'resolution':[w,h],'views':[]}
   try:
    t=time.perf_counter();p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');row['initial_ready_s']=time.perf_counter()-t
    if p.locator('#skip-intro').is_visible():p.locator('#skip-intro').click()
    p.wait_for_selector('#splash',state='hidden',timeout=10000)
    for view in ['simulacao','modelo','analise','paineis','laboratorio','avancadas','decisoes','historico']:
     p.locator(f'[data-nav={view}]').click();expect(p.locator(f'#view-{view}')).to_be_visible();p.wait_for_timeout(100)
     widths=p.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})')
     row['views'].append({'view':view,**widths})
     if view in ['simulacao','paineis','decisoes']:p.screenshot(path=str(out/f'{view}_{w}.png'))
    p.locator('[data-nav=modelo]').click()
    with p.expect_response(lambda x:x.url.endswith('/api/model')) as ev:
     p.locator('#model-file').set_input_files({'name':'roundtrip.json','mimeType':'application/json','buffer':exported})
    assert ev.value.ok
    row['model_roundtrip']={'exported_rule':json.loads(exported)['dispatch_rule'],'rule_after_import':s.info()['rule'],'response_status':ev.value.status}
    assert row['model_roundtrip']['exported_rule']=='SPT' and row['model_roundtrip']['rule_after_import']=='EDD'
    p.locator('[data-nav=analise]').click()
    p.locator('#experiment-name').fill('Integrado A')
    with p.expect_response(lambda x:x.url.endswith('/api/experiment/save')) as ev:p.locator('#experiment-save').click()
    assert ev.value.ok
    a=ev.value.json()
    expect(p.locator('#experiment-count')).to_have_text('1 arquivados')
    # A syntactically valid but invalid archive must not block valid archives.
    bad=s.experiments_dir/'invalid.json';bad.write_text('[]');before=bad.read_bytes()
    with p.expect_response(lambda x:x.url.endswith('/api/experiments') and x.status==500) as ev:
     p.locator('[data-nav=simulacao]').click();p.locator('[data-nav=analise]').click()
    row['invalid_archive']={'status':ev.value.status,'preserved':bad.read_bytes()==before,'valid_archive_exists':(s.experiments_dir/(a['id']+'.json')).exists()}
    assert ev.value.status==500
    expect(p.locator('#toast')).to_contain_text('carregar experimentos')
    row['js_errors']=errors
    assert not errors,errors
    results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 browser.close()
(r/'integrated-browser.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
