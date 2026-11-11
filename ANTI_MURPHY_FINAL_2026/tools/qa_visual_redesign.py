"""Visual QA: isolated Chromium DOM with authentic Studio results.
Chromium policy here blocks HTTP/file navigation; inline source and a mocked
transport are used ONLY for visual interaction checks. Backend tested separately.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
import base64, json
from atelier.service import Studio
ROOT=Path(__file__).resolve().parents[2] if False else Path(__file__).resolve().parents[1]
WEB=ROOT/'atelier'/'web';OUT=ROOT/'docs'/'qa';OUT.mkdir(exist_ok=True,parents=True)
print('starting',flush=True)
with TemporaryDirectory() as temp:
  studio=Studio(Path(temp))
  state=studio.info();print('studio prepared',flush=True)
  try: monte=studio.advanced({'mode':'uncertainty'})
  except Exception as e: print('Monte Carlo fixture failed',e);monte=None
  # Build a single self-contained document for browser inspection.
  html=(WEB/'index.html').read_text('utf8')
  styles=(WEB/'styles.css').read_text('utf8')+'\n'+(WEB/'design_vnext.css').read_text('utf8')
  html=html.replace('<link rel="stylesheet" href="/styles.css">','<style>'+styles+'</style>')
  html=html.replace('<link rel="stylesheet" href="/design_vnext.css">','')
  for file in (WEB/'brand').iterdir():
    if file.suffix not in ('.svg','.png'):continue
    mime='image/svg+xml' if file.suffix=='.svg' else 'image/png'
    uri=f'data:{mime};base64,'+base64.b64encode(file.read_bytes()).decode()
    html=html.replace('"/brand/'+file.name+'"','"'+uri+'"')
  fixture={'state':state,'monte':monte}
  # Requests are simulated using state exported by REAL Python DES above.
  bootstrap='''<script>
  const F=__TEST_FIXTURE__;
  window.__tests=[];
  window.__fixtures=F;
  window.fetch=async function(path,opts){
   const mode=opts?.body?JSON.parse(opts.body):{};
   let obj=F.state;
   if(String(path).endsWith('/api/advanced'))obj=F.monte;
   if(String(path).endsWith('/api/experiments'))obj=[];
   if(String(path).endsWith('/api/history'))obj=[];
   if(String(path).endsWith('/api/assistant'))obj={text:'Resposta local de teste, calculada no motor.',label:'TESTE',rows:[]};
   return {ok:!!obj,status:obj?200:400,json:async()=>structuredClone(obj),text:async()=>JSON.stringify(obj)};
  };
  </script>'''.replace('__TEST_FIXTURE__',json.dumps(fixture,ensure_ascii=False))
  script=(WEB/'app.js').read_text('utf8')
  html=html.replace('<script src="/app.js" defer></script>',bootstrap+'<script>'+script+'</script>');print('html prepared',len(html),flush=True)
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    for w,height in ((1366,768),(1920,1080)):
      page=browser.new_page(viewport={'width':w,'height':height},device_scale_factor=1)
      errors=[]
      page.on('pageerror',lambda err: errors.append(str(err)))
      page.set_content(html,wait_until='domcontentloaded',timeout=15000)
      page.wait_for_function('document.querySelector("#sim-metrics .metric-unit")', timeout=15000)
      page.wait_for_timeout(1600)
      page.evaluate("document.querySelector('#splash')?.remove()")
      page.screenshot(path=str(OUT/f'operacao_{w}.png'),full_page=False)
      print('loaded',w,'metrics',page.locator('#sim-metrics .metric-unit').count(),'stations',page.locator('#factory-a .station-group').count())
      page.locator('#factory-a [data-station="CNC"]').click(force=True)
      page.locator('[data-inspect-focus]').click()
      print('focus',page.locator('#factory-viewport').get_attribute('class'))
      page.screenshot(path=str(OUT/f'foco_{w}.png'),full_page=False)
      page.locator('[data-inspect-focus]').click()
      page.locator('#scene-tabs [data-scene="split"]').click()
      page.screenshot(path=str(OUT/f'comparar_{w}.png'),full_page=False)
      print('split',page.locator('#split-control').is_visible())
      page.locator('#stage-fullscreen').click(force=True)
      page.wait_for_timeout(400)
      print('fullscreen',page.evaluate('!!document.fullscreenElement'))
      page.screenshot(path=str(OUT/f'apresentacao_{w}.png'),full_page=False)
      page.evaluate('document.exitFullscreen()')
      page.wait_for_timeout(350)
      print('leaving fullscreen',page.evaluate('!!document.fullscreenElement'),flush=True);page.locator('[data-nav="avancadas"]').click()
      page.locator('[data-advanced="uncertainty"]').click()
      page.locator('#advanced-run').click()
      page.wait_for_selector('.mc-distribution',timeout=30000)
      page.screenshot(path=str(OUT/f'monte_carlo_{w}.png'),full_page=False)
      print('montecarlo histogram',page.locator('.mc-distribution .mc-bar').count())
      for name in ('modelo','analise','laboratorio','decisoes','historico'):
        page.locator(f'[data-nav="{name}"]').click()
        assert page.locator(f'#view-{name}').is_visible(),f'{name} inaccessible'
        if name in ('analise','decisoes'):
          page.screenshot(path=str(OUT/f'{name}_{w}.png'),full_page=False)
      page.locator('#guide-start').click()
      assert page.locator('#tour-panel').is_visible()
      page.locator('#tour-close').click()
      assert not page.locator('#tour-panel').is_visible()
      page.locator('#help-button').click()
      assert page.locator('#guide-panel').is_visible()
      page.locator('#guide-close').click()
      page.locator('[data-nav="simulacao"]').click()
      page.locator('#orders-row .order-mini').first.click()
      assert page.locator('#station-inspector .order-trace').count()==1
      print('screens + help + order trace:',w,'OK')
      print('JS errors:',errors)
      if errors:raise RuntimeError('Browser errors '+str(errors))
      page.close()
    browser.close()
