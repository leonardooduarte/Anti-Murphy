"""Browser visual and interaction QA with a local in-process API bridge.
Browser policy blocks loopback HTTP in this environment, so only the transport
is substituted; the V30.2 Python service and production JavaScript are real.
Requires playwright and an installed Chromium, not needed by end users.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import base64, json
from playwright.sync_api import sync_playwright
from atelier.service import Studio

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'atelier'/'web'
OUT=ROOT/'docs'/'capturas_reais'
OUT.mkdir(parents=True,exist_ok=True)

html=(WEB/'index.html').read_text('utf-8')
for name in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
 data=(WEB/'brand'/name).read_bytes()
 mime='image/png' if name.endswith('png') else 'image/svg+xml'
 html=html.replace('/brand/'+name,'data:'+mime+';base64,'+base64.b64encode(data).decode())
html=html.replace('<link rel="stylesheet" href="/styles.css">','').replace('<script src="/app.js" defer></script>','')
css=(WEB/'styles.css').read_text('utf-8')
js=(WEB/'app.js').read_text('utf-8')

with TemporaryDirectory() as storage, sync_playwright() as pw:
  studio=Studio(Path(storage))
  def bridge(path,method='GET',body=None):
    try:
      body=body or {}
      if path=='/api/state':data=studio.info()
      elif path=='/api/history':data=studio.history()
      elif path.startswith('/api/history/'):data=studio.read_history(path.rsplit('/',1)[-1])
      elif path=='/api/run':data=studio.calculate(body)
      elif path=='/api/model':data=studio.set_model(body)
      elif path=='/api/reset':data=studio.reset()
      elif path=='/api/select':data=studio.select(body['signature'])
      elif path=='/api/lab':data=studio.lab(body)
      elif path=='/api/advanced':data=studio.advanced(body)
      elif path=='/api/record':data=studio.decision(body)
      elif path=='/api/assistant':data=studio.assistant(body.get('question',''))
      else:raise RuntimeError('Unsupported test bridge route: '+path)
      return {'ok':True,'status':200,'data':data}
    except Exception as e:return {'ok':False,'status':400,'data':{'error':str(e)}}
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'],headless=True)
  all_errors=[]
  for width,height in [(1366,768),(1920,1080)]:
    page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
    page.on('pageerror',lambda e:all_errors.append(str(e)))
    page.expose_function('am_bridge',bridge)
    page.set_content(html,wait_until='load')
    page.add_style_tag(content=css)
    page.evaluate('''window.fetch=async (path, options={})=>{
       const raw=options.body ? JSON.parse(options.body) : {};
       const result=await window.am_bridge(path,options.method||'GET',raw);
       return {ok:result.ok,status:result.status,json:async()=>result.data};
    };''')
    page.add_script_tag(content=js)
    page.wait_for_timeout(2650)
    assert page.locator('#splash').count()==0, 'Splash should dismiss automatically'
    assert page.locator('#factory-a .station-group').count()==5
    assert page.locator('#split-control').is_hidden()
    assert page.locator('body').evaluate('(el)=>el.scrollWidth')<=width+1
    page.screenshot(path=str(OUT/f'operacao_{width}.png'),full_page=True)
    # Timeline and comparison
    page.locator('[data-scene=split]').click()
    assert page.locator('#split-control').is_visible()
    assert page.locator('#factory-b .station-group').count()==5
    # A/B at a shared simulated instant: CNC remains down in the incident,
    # but selected time-limited intervention should allow production again.
    total_h=max(x['horizon'] for x in studio.info()['replay'].values())
    page.locator('#timeline-range').fill(str(round(10000*10.0/total_h)))
    cnc_a=page.locator('#factory-a .station-group[data-station="CNC"]')
    cnc_b=page.locator('#factory-b .station-group[data-station="CNC"]')
    assert 'down' in (cnc_a.get_attribute('class') or ''), 'CNC A must be down at t=10h'
    assert 'down' not in (cnc_b.get_attribute('class') or ''), 'CNC B must have recovered at t=10h'
    page.locator('#wipe-range').fill('70')
    page.locator('#timeline-range').fill('5000')
    assert '12:' in page.locator('#clock-label').inner_text()
    page.locator('#play-button').click()
    before=page.locator('#clock-label').inner_text();page.wait_for_timeout(470)
    after=page.locator('#clock-label').inner_text()
    assert before!=after,(before,after)
    page.locator('#play-button').click()
    page.screenshot(path=str(OUT/f'comparacao_{width}.png'),full_page=True)
    # Analysis -> select alternative -> data changes in service
    page.locator('[data-nav=analise]').click()
    assert page.locator('#alternatives-table tbody tr').count()>=10
    assert page.locator('#impact-orders tbody tr').count()==5
    page.screenshot(path=str(OUT/f'analise_{width}.png'),full_page=True)
    page.locator('#alternatives-table tbody tr').nth(2).click();page.wait_for_timeout(180)
    assert studio.info()['selected']==studio.info()['alternatives'][2]['signature']
    # Model editing: change quantity and apply
    page.locator('[data-nav=modelo]').click()
    page.locator('[data-model-tab=orders]').click()
    qty=page.locator('#model-table input[data-field=quantidade]').first
    qty.fill('24')
    page.locator('#model-save').click();page.wait_for_timeout(350)
    assert studio.info()['orders'][0]['quantidade']==24
    page.screenshot(path=str(OUT/f'modelo_{width}.png'),full_page=True)
    # Lab -> actual engine
    page.locator('[data-nav=laboratorio]').click();page.locator('#run-lab').click();page.wait_for_timeout(220)
    assert page.locator('#lab-results .plot-row').count()==7
    page.screenshot(path=str(OUT/f'ensaios_{width}.png'),full_page=True)
    # AI and decision recording -> persisted record list
    page.locator('[data-nav=decisoes]').click()
    page.locator('#assistant-input').fill('Quais pedidos estão em risco?')
    page.locator('#assistant-form button').click();page.wait_for_timeout(230)
    assert page.locator('.assistant-message').count()>=2
    page.locator('#decision-note').fill('Validar hipótese de manutenção e disponibilidade antes de executar.')
    page.locator('#register-decision').click();page.wait_for_timeout(350)
    assert len(studio.history())>=1
    assert page.locator('#view-historico').is_visible()
    assert len(all_errors)==0,all_errors
    print('QA',width,'screens, model editing, player, A/B, assistant, lab, record OK')
    page.close()
  browser.close()
  print('Browser JS errors:',all_errors)
