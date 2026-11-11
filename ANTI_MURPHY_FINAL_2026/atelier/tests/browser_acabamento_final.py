import base64, sys
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from atelier.service import Studio
WEB=ROOT/'atelier/web'
OUT=ROOT/'docs'/'capturas_acabamento_final';OUT.mkdir(parents=True,exist_ok=True)
html=(WEB/'index.html').read_text('utf8')
for n in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
 b=(WEB/'brand'/n).read_bytes(); mime='image/png' if n.endswith('png') else 'image/svg+xml'
 html=html.replace('/brand/'+n,'data:'+mime+';base64,'+base64.b64encode(b).decode())
css_names=['styles','design_vnext','dashboards','studio_final','release_quality','prefinal_polish','banca','engineering_charts','final_banca','polimento_09_11','apresentacao_premium','integridade_final','acabamento_banca_final']
for n in css_names:html=html.replace(f'<link rel="stylesheet" href="/{n}.css">','')
for n in ['engineering_charts','app']:html=html.replace(f'<script src="/{n}.js" defer></script>','')
css='\n'.join((WEB/(x+'.css')).read_text('utf8') for x in css_names)
with TemporaryDirectory() as tmp,sync_playwright() as pw:
 studio=Studio(Path(tmp));browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 def bridge(path,method='GET',body=None):
  body=body or {}
  try:
   if path=='/api/state':res=studio.info()
   elif path=='/api/dashboards':res=studio.dashboards()
   elif path=='/api/technical-audit':res=studio.technical_audit()
   elif path=='/api/history':res=studio.history()
   elif path=='/api/experiments':res=studio.experiment_list()
   elif path=='/api/projects':res=studio.projects()
   elif path=='/api/select':res=studio.select(body.get('signature',''))
   elif path=='/api/record':res=studio.decision(body)
   elif path=='/api/advanced':res=studio.advanced(body)
   elif path=='/api/lab':res=studio.lab(body)
   elif path=='/api/run':res=studio.calculate(body)
   else:raise ValueError('No bridge '+path)
   return {'ok':True,'status':200,'data':res}
  except Exception as ex:return {'ok':False,'status':400,'data':{'error':str(ex)}}
 for width,height in [(1280,720),(1366,768),(1920,1080)]:
  errors=[]
  page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,accept_downloads=True)
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.expose_function('am_bridge',bridge)
  page.set_content(html.replace('<script src="/analysis_state.js" defer></script>',''),wait_until='load')
  page.add_style_tag(content=css)
  page.evaluate('''window.fetch=async (path,opts={})=>{const r=await window.am_bridge(path,opts.method||'GET',opts.body?JSON.parse(opts.body):{});return {ok:r.ok,status:r.status,json:async()=>r.data};}''')
  page.add_script_tag(content=(WEB/'analysis_state.js').read_text('utf8'))
  page.add_script_tag(content=(WEB/'engineering_charts.js').read_text('utf8'))
  page.add_script_tag(content=(WEB/'app.js').read_text('utf8'))
  page.wait_for_selector('#factory-a .station-group',timeout=20000)
  page.evaluate('document.querySelector("#splash")?.remove()')
  page.locator('[data-nav=laboratorio]').click()
  page.locator('#lab-tabs [data-lab="capacity"]').click()
  page.locator('#run-lab').click()
  page.wait_for_selector('#lab-results .eng-index-legend',timeout=25000)
  assert page.locator('#lab-results .eng-index-chip').count()==12
  assert page.locator('#lab-results .eng-x-index').count()==12
  assert page.locator('#lab-results .eng-x-index').first.text_content()=='01'
  labels=page.locator('#lab-results .eng-index-chip span').all_inner_texts()
  assert '+1 op. CNC +1 op. SOLDA' in labels,labels
  # Detect actual overlapping SVG x-axis text boxes. The screenshot from 09/11 had 12 colliding strings.
  bounds=page.locator('#lab-results .eng-x-index').evaluate_all('''es=>es.map(x=>{const r=x.getBoundingClientRect();return {left:r.left,right:r.right};})''')
  assert all(bounds[i]['right']+2<bounds[i+1]['left'] for i in range(11)),bounds
  page.locator('#lab-results .eng-index-chip').nth(1).click()
  assert page.locator('#lab-results .eng-index-chip.selected').count()==1
  assert '+1 op. CNC +1 op. SOLDA' in page.locator('#lab-results .eng-selected').inner_text()
  assert page.locator('#lab-results .eng-point.selected').count()==1
  assert page.locator('#lab-results .eng-index-chip').nth(1).get_attribute('aria-pressed')=='true'
  (OUT/f'01_capacidade_legivel_{width}.png').parent.mkdir(parents=True,exist_ok=True)
  page.locator('#lab-results .eng-suite').screenshot(path=str(OUT/f'01_capacidade_legivel_{width}.png'))
  # Evidence: zoom is a user action; a metric switch must preserve enlarged view.
  page.locator('#lab-results .eng-zoom-btn').click()
  assert page.locator('#lab-results .eng-suite.chart-focus').count()==1
  assert page.locator('body.eng-chart-zoom-active').count()==1
  page.locator('#lab-results .eng-metric').nth(3).click()
  assert page.locator('#lab-results .eng-suite.chart-focus').count()==1
  assert page.locator('#lab-results .eng-x-index').count()==12
  (OUT/f'02_capacidade_ampliada_{width}.png').parent.mkdir(parents=True,exist_ok=True)
  page.screenshot(path=str(OUT/f'02_capacidade_ampliada_{width}.png'))
  page.keyboard.press('Escape')
  assert page.locator('.eng-suite.chart-focus').count()==0
  assert page.locator('body.eng-chart-zoom-active').count()==0
  # CSV and SVG remain valid exports on live motor results.
  with page.expect_download(timeout=10000) as d:page.locator('#lab-results [data-eng-export-svg]').click()
  dl=d.value
  xml=Path(dl.path()).read_text('utf8')
  assert '<svg' in xml and '01' in xml
  with page.expect_download(timeout=10000) as d:page.locator('#lab-results [data-eng-export]').click()
  txt=Path(d.value.path()).read_text('utf-8-sig')
  assert 'CNC' in txt and 'throughput_h' in txt
  page.locator('#lab-tabs [data-lab="dispatch"]').click()
  page.locator('#run-lab').click()
  page.wait_for_selector('#lab-results .eng-suite',timeout=25000)
  assert page.locator('#lab-results .eng-index-legend').count()==0
  page.locator('[data-nav=avancadas]').click()
  page.locator('#advanced-tabs [data-advanced=sensitivity]').click()
  page.locator('#advanced-run').click()
  page.wait_for_selector('#advanced-results .eng-suite',timeout=25000)
  assert page.locator('#advanced-results .eng-svg').count()==1
  assert page.locator('#advanced-results .eng-index-legend').count()==0
  page.locator('#advanced-results .eng-zoom-btn').click()
  assert page.locator('body.eng-chart-zoom-active').count()==1
  page.locator('[data-nav=simulacao]').evaluate('(el)=>el.click()')
  assert page.locator('body.eng-chart-zoom-active').count()==0
  assert page.locator('#view-simulacao').is_visible()
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 3')
  assert not errors,errors
  print('ACABAMENTO OK',width,height,'legenda 12', 'não sobrepõe', 'ampliação', 'exportações', 'ensaios', 'ferramentas',flush=True)
  page.close()
 browser.close()
