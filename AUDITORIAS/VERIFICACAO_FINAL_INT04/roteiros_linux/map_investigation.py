from pathlib import Path
import sys,json,os,tempfile
from threading import Thread
from http.server import ThreadingHTTPServer
sys.path.insert(0,'/workspace/work/verificacao-final/base/ANTI_MURPHY_FINAL_2026')
from atelier import server
from atelier.service import Studio
from playwright.sync_api import sync_playwright,expect
r=Path('/workspace/work/verificacao-final');out=r/'capturas-mapa';out.mkdir(exist_ok=True);results=[]
GEOMETRY='''()=>{const svg=document.querySelector('#factory-a'),bottom=document.querySelector('.factory-bottom').getBoundingClientRect().top,rects=[...svg.querySelectorAll('.selection-halo')].map(e=>e.getBoundingClientRect().bottom);return {clock:performance.now(),scroll_y:scrollY,view_box:svg.getAttribute('viewBox'),bottom,max_halo:Math.max(...rects),difference:Math.max(...rects)-bottom}}'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  for repeat in range(5):
   with tempfile.TemporaryDirectory() as d:
    s=Studio(Path(d));station=next(iter(s.state['stations'].values())).copy();station.update(maquinas=1,operadores=1)
    s.set_model({'stations':{f'P{i}':{**station,'nome':f'Célula de produção {i}'} for i in range(50)},'orders':[{'id':'A','quantidade':2,'prioridade':1,'prazo_h':100,'multa_hora':1,'route':[['P0',1]]}]});server.STUDIO=s
    httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
    p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
     p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
     expect(p.locator('#factory-a .station-group')).to_have_count(50);before=s.info()['run_id']
     last=p.locator('[data-readable-station]').last;last.scroll_into_view_if_needed();last.focus();last.press('Enter')
     expect(p.locator('#factory-a')).to_have_attribute('viewBox',__import__('re').compile(r'.*400 320$'))
     font=p.locator('#factory-a .station-name').last.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a');assert font>=12
     p.locator('[data-inspect-focus]').click()
     expect(p.locator('#factory-a')).not_to_have_attribute('viewBox',__import__('re').compile(r'.*400 320$'))
     # Original runner reads these in separate browser calls.
     bottom=p.locator('.factory-bottom').bounding_box()['y']
     bounds=p.locator('#factory-a .selection-halo').evaluate_all('es=>es.map(e=>e.getBoundingClientRect().bottom)')
     atomic=p.evaluate(GEOMETRY)
     p.wait_for_timeout(300) # observed settling window, not a production delay
     settled=p.evaluate(GEOMETRY)
     row={'resolution':[w,h],'repeat':repeat+1,'font_px':font,'original_split_difference':max(bounds)-bottom,'atomic':atomic,'settled':settled,'js_errors':errors,'run_preserved':s.info()['run_id']==before}
     if repeat==0 or row['original_split_difference']>2 or settled['difference']>2:p.screenshot(path=str(out/f'mapa_{w}_{repeat+1}.png'))
     results.append(row);(r/'map-investigation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(row),flush=True)
     assert not errors and row['run_preserved']
    finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
