"""INT04 measured contrast/typography and geometry in both affected views."""
import json,math,os,re
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
from atelier import server
from atelier.service import Studio

out=Path(os.environ.get('INT04_QA_OUT','docs/INT04/capturas'));out.mkdir(parents=True,exist_ok=True)
before=os.environ.get('INT04_EXPECT_BEFORE')=='1';results=[]
def lum(rgb):
 values=[v/255 for v in rgb];values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
 return sum(v*w for v,w in zip(values,[.2126,.7152,.0722]))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   s=Studio(Path(d));state=s.info();disk={p:p.read_bytes() for p in Path(d).rglob('*.json')};server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
    for view in ['analise','decisoes']:
     p.locator(f'[data-nav={view}]').click();labels=p.locator(f'#view-{view} .alt-metrics small');expect(labels.first).to_be_visible();p.locator(f'#view-{view}').evaluate('(e)=>Promise.all(e.getAnimations().map(a=>a.finished))')
     measurements=labels.evaluate_all('''es=>es.filter(e=>e.getClientRects().length).map(e=>{
      const c=getComputedStyle(e),box=e.getBoundingClientRect(),value=e.nextElementSibling?.getBoundingClientRect();
      let parent=e,background=null,opacity=1;
      while(parent){const s=getComputedStyle(parent);opacity*=Number(s.opacity);const a=s.backgroundColor.match(/[\\d.]+/g)?.map(Number)||[];if(!background&&a.length>=3&&(a.length<4||a[3]===1))background=a.slice(0,3);parent=parent.parentElement;}
      return {text:e.textContent,color:c.color,font_px:parseFloat(c.fontSize),line_height:c.lineHeight,background,opacity,box:{width:box.width,height:box.height,bottom:box.bottom},value_top:value?.top,scroll_width:e.scrollWidth,client_width:e.clientWidth};
     })''')
     assert measurements
     for x in measurements:
      rgb=[float(v) for v in re.findall(r'[\d.]+',x['color'])][:3];low,high=sorted([lum(rgb),lum(x['background'])]);x['contrast']=(high+.05)/(low+.05)
      assert x['opacity']==1,x
      if before:assert x['font_px']==10 and x['contrast']<4.5
      else:
       assert x['font_px']>=14 and x['contrast']>=4.5,x
       assert x['scroll_width']<=x['client_width']+1,x
       assert x['value_top']>=x['box']['bottom']-.5,x
     assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
     p.locator(f'#view-{view} .alt-metrics').first.screenshot(path=str(out/f'{view}_{w}.png'))
     results.append({'resolution':[w,h],'view':view,'labels':measurements});print('INT04 BROWSER OK',view,w,h,'contrast',round(min(x['contrast'] for x in measurements),3),'font',min(x['font_px'] for x in measurements),flush=True)
    assert s.info()==state and all(p.read_bytes()==raw for p,raw in disk.items())
    assert not errors,errors
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
(out/'medicoes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
