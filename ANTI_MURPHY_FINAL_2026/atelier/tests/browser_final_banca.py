"""Final-presentation QA with real Studio state via an in-process HTTP adapter.
No cloud model, no npm and no invented engine values.
Run: python atelier/tests/browser_final_banca.py
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import base64
from playwright.sync_api import sync_playwright
from atelier.service import Studio

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'atelier'/'web'
OUT=ROOT/'docs'/'capturas_banca_final'
OUT.mkdir(exist_ok=True,parents=True)
html=(WEB/'index.html').read_text('utf8')
css_names=['styles','design_vnext','dashboards','studio_final','release_quality','prefinal_polish','banca','engineering_charts','final_banca','polimento_09_11','apresentacao_premium']
for n in css_names:html=html.replace(f'<link rel="stylesheet" href="/{n}.css">','')
html=html.replace('<script src="/engineering_charts.js" defer></script>','').replace('<script src="/app.js" defer></script>','')
for n in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
    b=(WEB/'brand'/n).read_bytes();mime='image/png' if n.endswith('png') else 'image/svg+xml'
    html=html.replace('/brand/'+n,'data:'+mime+';base64,'+base64.b64encode(b).decode())
css='\n'.join((WEB/(n+'.css')).read_text('utf8') for n in css_names)
chart_js=(WEB/'engineering_charts.js').read_text('utf8')
app_js=(WEB/'app.js').read_text('utf8')
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for width,height in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as tmp:
   studio=Studio(Path(tmp));errors=[]
   def bridge(path, method='GET',body=None):
    body=body or {}
    try:
     if path=='/api/state':res=studio.info()
     elif path=='/api/dashboards':res=studio.dashboards()
     elif path=='/api/technical-audit':res=studio.technical_audit()
     elif path=='/api/history':res=studio.history()
     elif path=='/api/experiments':res=studio.experiment_list()
     elif path=='/api/experiment-library':res=studio.experiment_library()
     elif path=='/api/projects':res=studio.projects()
     elif path=='/api/select':res=studio.select(body.get('signature',''))
     elif path=='/api/record':res=studio.decision(body)
     elif path.startswith('/api/history/'):res=studio.read_history(path.rsplit('/',1)[-1])
     elif path=='/api/run':res=studio.calculate(body)
     elif path=='/api/advanced':res=studio.advanced(body)
     elif path=='/api/lab':res=studio.lab(body)
     else:raise ValueError('Unsupported QA endpoint '+path)
     return {'ok':True,'status':200,'data':res}
    except Exception as e:return {'ok':False,'status':400,'data':{'error':str(e)}}
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,accept_downloads=True)
   page.on('pageerror',lambda e: errors.append(str(e)))
   page.expose_function('am_bridge',bridge)
   page.set_content(html.replace('<script src="/analysis_state.js" defer></script>',''),wait_until='load');page.add_style_tag(content=css)
   page.evaluate('''window.fetch=async (path,opts={})=>{const r=await window.am_bridge(path,opts.method||'GET',opts.body?JSON.parse(opts.body):{});return {ok:r.ok,status:r.status,json:async()=>r.data};}''')
   page.add_script_tag(content=(WEB/'analysis_state.js').read_text('utf8'))
   page.add_script_tag(content=chart_js);page.add_script_tag(content=app_js)
   page.wait_for_selector('#factory-a .station-group',timeout=15000)
   page.evaluate('document.querySelector("#splash")?.remove()')
   assert page.locator('#presentation-guide').is_hidden()
   page.locator('#presentation-toggle').click()
   assert page.locator('#presentation-guide').is_visible()
   assert page.locator('#presentation-title').inner_text().startswith('01 / 06')
   assert page.locator('#factory-a .station-group').count()==5
   page.screenshot(path=str(OUT/f'01_plano_{width}.png'))
   page.locator('#presentation-next').click()
   assert '02 / 06' in page.locator('#presentation-title').inner_text()
   assert page.locator('#event-status').inner_text().startswith('PARADA')
   assert page.locator('#stage-event-alert').is_visible()
   assert page.locator('#factory-a .station-group.down').count()==1
   assert 'PARADA SIMULADA' in page.locator('.station-group.down .station-outage-badge').text_content()
   page.screenshot(path=str(OUT/f'02_falha_{width}.png'))
   page.locator('#presentation-next').click()
   assert page.locator('#presentation-title').inner_text().startswith('03 / 06')
   assert page.locator('#factory-a .station-group.down').count()==1
   page.locator('#presentation-next').click()
   assert page.locator('#presentation-title').inner_text().startswith('04 / 06')
   assert 'RESPOSTA MODELADA' in page.locator('#stage-event-alert').inner_text()
   page.screenshot(path=str(OUT/f'04_resposta_{width}.png'))
   assert page.locator('#scene-tabs [data-scene="response"]').get_attribute('class') is not None
   page.locator('#presentation-next').click()
   assert page.locator('#presentation-title').inner_text().startswith('05 / 06')
   assert page.locator('#compare-scoreboard').is_hidden() # suppressed in presentation mode, not removed
   assert page.locator('#scene-b').is_visible()
   assert page.locator('#presentation-evidence').inner_text().count('R$')>=3
   page.screenshot(path=str(OUT/f'05_comparacao_{width}.png'))
   page.locator('#presentation-next').click()
   assert page.locator('#view-decisoes').is_visible()
   assert page.locator('#decision-selected .decision-quality').is_visible()
   assert page.locator('#presentation-title').inner_text().startswith('06 / 06')
   page.screenshot(path=str(OUT/f'06_decisao_{width}.png'))
   # Validated close: actual record in backend, not a UI-only success toast.
   page.locator('#decision-owner').fill('Equipe Anti-Murphy')
   page.locator('#decision-note').fill('Escolha documentada após verificar SLA, prazo e custo. A execução depende de validação física.')
   page.locator('#decision-risks').fill('Confirmar competência do operador, manutenção disponível e custo evitável.')
   page.locator('#decision-ack').check()
   page.locator('#register-decision').click()
   page.wait_for_selector('#record-see-report',timeout=18000)
   assert studio.history() and studio.history()[0]['action']
   assert page.locator('#record-see-report').is_visible()
   page.screenshot(path=str(OUT/f'07_registro_{width}.png'))
   assert page.locator('#presentation-guide').get_attribute('data-finalized')=='true'
   with page.expect_popup() as popup_info:page.locator('#record-see-report').click()
   popup=popup_info.value
   assert 'Decisão efetivamente registrada' in popup.locator('body').inner_text()
   assert 'Confirmar competência do operador' in popup.locator('body').inner_text()
   popup.close()
   page.locator('#record-see-history').click()
   page.wait_for_selector('#history-list .history-item',timeout=10000)
   page.locator('#history-list .history-item').first.click()
   assert 'Escolha documentada' in page.locator('#history-detail').inner_text()
   with page.expect_popup() as final_report:
    page.locator('#presentation-next').click()
   assert 'Decisão efetivamente registrada' in final_report.value.locator('body').inner_text()
   final_report.value.close()
   page.locator('#presentation-restart').click()
   assert page.locator('#view-simulacao').is_visible()
   assert page.locator('#presentation-title').inner_text().startswith('01 / 06')
   page.locator('#presentation-toggle').click()
   assert page.locator('#presentation-guide').is_hidden()
   assert page.locator('#view-simulacao .metrics-line').is_visible()
   assert page.locator('.inspector').is_visible()
   # Verify a dominated alternative is explicitly flagged, not silently reselected.
   page.locator('[data-nav="analise"]').click()
   page.locator('#form-sla').fill('40')
   page.locator('#analysis-recalculate').click()
   page.wait_for_function('document.querySelector("#alternative-count").textContent.includes("respostas")')
   page.locator('#alternatives-table tr[data-signature]').filter(has_text='Não intervir').click()
   page.wait_for_selector('#alternative-detail .review-warning',timeout=10000)
   assert 'Manutenção expressa' in page.locator('#alternative-detail .review-warning').inner_text()
   assert studio.info()['decision_review']['status']=='dominated'
   page.screenshot(path=str(OUT/f'08_alerta_multicriterio_{width}.png'))
   page.locator('#alternative-detail .review-compare-action').click()
   page.wait_for_selector('#alternative-detail .review-positive',timeout=10000)
   assert studio.info()['decision_review']['status']=='non_dominated'
   page.locator('[data-nav="laboratorio"]').click()
   assert page.locator('#view-laboratorio').is_visible()
   page.locator('[data-nav="paineis"]').click()
   page.wait_for_selector('#dash-body .dash-stat',timeout=14000)
   assert page.locator('#view-paineis').is_visible()
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 3')
   assert not errors,errors
   print(f'Banca E2E OK {width}x{height} · six authentic stages; existing nav; 0 JS exceptions',flush=True)
   page.close()
 browser.close()
