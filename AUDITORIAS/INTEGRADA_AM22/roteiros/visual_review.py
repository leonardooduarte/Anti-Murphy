from pathlib import Path
import os
import sys,json,tempfile,re
from threading import Thread
from http.server import ThreadingHTTPServer
sys.path.insert(0,os.environ['ANTI_MURPHY_AUDIT_APP'])
from atelier import server
from atelier.service import Studio
from playwright.sync_api import sync_playwright,expect
r=Path(os.environ['ANTI_MURPHY_AUDIT_OUT']);out=r/'capturas-visuais';out.mkdir(exist_ok=True);results=[]
def luminance(rgb):
 a=[v/255 for v in rgb];a=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a]
 return sum(a*b for a,b in zip(a,[.2126,.7152,.0722]))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with tempfile.TemporaryDirectory() as d:
   s=Studio(Path(d));server.STUDIO=s;httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
    summary=p.locator('#am-experience-journey>summary');summary.scroll_into_view_if_needed();summary.focus();summary.press('Enter')
    expect(p.locator('#experience-story')).to_be_visible()
    p.locator('#experience-story [data-experience-scene=split]').click();expect(p.locator('#scene-b')).to_be_visible()
    p.locator('[data-nav=analise]').click();expect(p.locator('#experience-brief')).to_be_visible();expect(p.locator('#experience-orders')).to_be_visible()
    p.locator('#experience-brief').screenshot(path=str(out/f'resumo_{w}.png'))
    p.locator('#experience-brief [data-experience-go=decisions]').click();expect(p.locator('#view-decisoes')).to_be_visible()
    labels=p.locator('.alt-metrics small').evaluate_all('''es=>es.map(e=>{let b=e,backgrounds=[];while(b){let s=getComputedStyle(b);backgrounds.push({color:s.backgroundColor,image:s.backgroundImage});b=b.parentElement;}let c=getComputedStyle(e);return {text:e.textContent,color:c.color,font_px:parseFloat(c.fontSize),backgrounds}})''')
    for label in labels:
     fg=[float(x) for x in re.findall(r'[\d.]+',label['color'])][:3];bg=None
     for layer in label.pop('backgrounds'):
      nums=[float(x) for x in re.findall(r'[\d.]+',layer['color'])]
      if len(nums)>=3 and (len(nums)<4 or nums[3]==1):bg=nums[:3];break
     if bg:
      lo,hi=sorted([luminance(fg),luminance(bg)]);label.update(background_rgb=bg,contrast=(hi+.05)/(lo+.05))
    results.append({'resolution':[w,h],'narrative_keyboard':True,'narrative_comparison':True,'new_brief_and_orders':True,'js_errors':errors,'decision_labels':labels})
    assert not errors
    print(json.dumps(results[-1],ensure_ascii=False),flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
(r/'visual-review.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
