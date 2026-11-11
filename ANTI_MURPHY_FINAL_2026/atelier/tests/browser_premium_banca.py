"""QA cross-browser-size for progressive reveal, real split scenarios and closing evidence.
Run: python -m atelier.tests.browser_premium_banca
All endpoints backed by a temporary real Studio instance; no artificial engine results.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from atelier.service import Studio
import base64

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'atelier'/'web'
OUT=ROOT/'docs'/'capturas_apresentacao_premium'
OUT.mkdir(parents=True,exist_ok=True)
html=(WEB/'index.html').read_text('utf8')
css_names=['styles','design_vnext','dashboards','studio_final','release_quality',
           'prefinal_polish','banca','engineering_charts','final_banca','polimento_09_11','apresentacao_premium','integridade_final']
for n in css_names:html=html.replace(f'<link rel="stylesheet" href="/{n}.css">','')
html=html.replace('<script src="/engineering_charts.js" defer></script>','').replace('<script src="/app.js" defer></script>','')
for n in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
 b=(WEB/'brand'/n).read_bytes()
 mime='image/png' if n.endswith('png') else 'image/svg+xml'
 html=html.replace('/brand/'+n,'data:'+mime+';base64,'+base64.b64encode(b).decode())
css='\n'.join((WEB/(name+'.css')).read_text('utf8') for name in css_names)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for width,height in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as tmp:
   studio=Studio(Path(tmp));errors=[]
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
     elif path.startswith('/api/history/'):res=studio.read_history(path.rsplit('/',1)[-1])
     elif path=='/api/run':res=studio.calculate(body)
     elif path=='/api/advanced':res=studio.advanced(body)
     elif path=='/api/lab':res=studio.lab(body)
     else:raise ValueError('QA missing endpoint '+path)
     return {'ok':True,'status':200,'data':res}
    except Exception as e:return {'ok':False,'status':400,'data':{'error':str(e)}}
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,accept_downloads=True)
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.expose_function('am_bridge',bridge)
   page.set_content(html,wait_until='load')
   page.add_style_tag(content=css)
   page.evaluate('''window.fetch=async (path,opts={})=>{const r=await window.am_bridge(path,opts.method||'GET',opts.body?JSON.parse(opts.body):{});return {ok:r.ok,status:r.status,json:async()=>r.data};}''')
   page.add_script_tag(content=(WEB/'engineering_charts.js').read_text('utf8'))
   page.add_script_tag(content=(WEB/'app.js').read_text('utf8'))
   page.wait_for_selector('#factory-a .station-group',timeout=18000)
   page.evaluate('document.querySelector("#splash")?.remove()')
   page.locator('#presentation-toggle').click()
   assert '01 / 06' in page.locator('#presentation-title').inner_text()
   evidence=page.locator('#presentation-evidence')
   assert 'CONCLUSÃO NOMINAL' in evidence.inner_text()
   assert 'SEM INTERVENÇÃO' not in evidence.inner_text() and 'R$' not in evidence.inner_text(),evidence.inner_text()
   page.screenshot(path=str(OUT/f'01_plano_{width}.png'))
   page.locator('#presentation-next').click()
   assert '02 / 06' in page.locator('#presentation-title').inner_text()
   assert 'INCIDENTE' in evidence.inner_text() and 'DIFERENÇA' not in evidence.inner_text()
   assert page.locator('#factory-a .station-group.down').count()==1
   page.screenshot(path=str(OUT/f'02_falha_{width}.png'))
   page.locator('#presentation-next').click()
   assert '03 / 06' in page.locator('#presentation-title').inner_text()
   assert 'PEDIDOS ATRASADOS' in evidence.inner_text()
   page.screenshot(path=str(OUT/f'03_pedidos_{width}.png'))
   page.locator('#presentation-next').click()
   assert '04 / 06' in page.locator('#presentation-title').inner_text()
   assert 'INVESTIMENTO MODELADO' in evidence.inner_text()
   page.screenshot(path=str(OUT/f'04_intervencao_{width}.png'))
   page.locator('#presentation-next').click()
   assert '05 / 06' in page.locator('#presentation-title').inner_text()
   assert page.locator('#factory-viewport').get_attribute('data-presentation-compare')=='true'
   assert page.locator('#presentation-compare-insights').is_visible()
   assert page.locator('#presentation-compare-view').is_visible()
   assert page.locator('#split-divider').is_hidden()
   assert page.locator('#factory-a').get_attribute('viewBox')!='0 0 1200 600'
   assert page.locator('#scene-b').bounding_box()['x']>=page.locator('#scene-a').bounding_box()['x']+page.locator('#scene-a').bounding_box()['width']-4
   assert page.locator('#presentation-compare-insights').inner_text().count('CNC')>=2
   page.screenshot(path=str(OUT/f'05_comparacao_foco_{width}.png'))
   page.locator('#presentation-compare-view').click()
   assert page.locator('#factory-a').get_attribute('viewBox')=='0 0 1200 600'
   page.screenshot(path=str(OUT/f'05b_comparacao_layout_{width}.png'))
   page.locator('#presentation-compare-view').click()
   page.locator('#presentation-next').click()
   assert '06 / 06' in page.locator('#presentation-title').inner_text()
   assert 'ESTADO DO REGISTRO' in evidence.inner_text()
   assert page.locator('#view-decisoes').is_visible()
   page.screenshot(path=str(OUT/f'06_decisao_{width}.png'))
   # Free-text reasoning: no artificial 65-character, 8-term or risk quota.
   page.locator('#decision-note').fill('Escolha pela menor multa.')
   page.locator('#decision-risks').fill('')
   page.locator('#decision-ack').check()
   assert page.locator('#register-decision').is_enabled()
   assert 'Texto livre' in page.locator('#decision-validation').inner_text() or 'Registro disponível' in page.locator('#decision-validation').inner_text()
   # An outdated R$ value triggers a transparent warning, not forced rewriting.
   page.locator('#decision-note').fill('A manutenção expressa foi escolhida por reduzir atrasos. A economia modelada neste experimento é R$ 4.223,17. A decisão depende de conferência dos prazos e custos efetivos.')
   page.locator('#decision-risks').fill('')
   assert 'R$ 4.223,17' in page.locator('#decision-money-audit').inner_text()
   assert 'Confira uma quantia' in page.locator('#decision-money-audit').inner_text()
   assert page.locator('#register-decision').is_disabled()
   assert page.locator('#decision-external-ack-wrap').is_visible()
   page.locator('#decision-external-ack').check()
   assert page.locator('#register-decision').is_enabled()
   page.locator('#decision-external-ack').uncheck()
   assert len(studio.history())==0
   page.screenshot(path=str(OUT/f'06a_valor_anterior_alerta_{width}.png'))
   # Repeated reasoning/risk text is an editorial suggestion, not a forced form.
   repeated='Decidimos validar a resposta com os resultados calculados e verificar restrições antes da aplicação, pois o modelo é sintético e requer verificação em campo.'
   page.locator('#decision-note').fill(repeated)
   page.locator('#decision-risks').fill(repeated)
   assert page.locator('#register-decision').is_enabled()
   assert 'Dica' in page.locator('#decision-validation').inner_text()
   page.locator('#decision-note').fill('')
   page.locator('#decision-risks').fill('')
   page.locator('#decision-draft').click()
   assert 'cenário sintético' in page.locator('#decision-note').input_value()
   assert 'disponibilidade' in page.locator('#decision-risks').input_value()
   assert page.locator('#register-decision').is_enabled()
   assert 'Quantias reconhecidas' in page.locator('#decision-money-audit').inner_text()
   page.locator('#decision-owner').fill('Equipe de apresentação')
   page.screenshot(path=str(OUT/f'06b_justificativa_{width}.png'))
   page.locator('#register-decision').click()
   page.wait_for_selector('#record-see-report',timeout=18000)
   assert len(studio.history())==1
   assert 'Registrado' in evidence.inner_text()
   assert 'Abrir relatório final' in page.locator('#presentation-next').inner_text()
   page.screenshot(path=str(OUT/f'07_registro_{width}.png'))
   with page.expect_popup() as popup_event:page.locator('#presentation-next').click()
   popup=popup_event.value
   assert 'Decisão efetivamente registrada' in popup.locator('body').inner_text()
   assert 'cenário sintético' in popup.locator('body').inner_text()
   assert 'Valores com R$ conferidos' not in popup.locator('body').inner_text()
   assert 'conferidas numericamente' in popup.locator('body').inner_text()
   assert 'RESULTADO DO EXPERIMENTO' in popup.locator('body').inner_text()
   assert 'verificações' in popup.locator('body').inner_text().lower()
   popup.close()
   # Pop-up blockers should not make the report disappear: fall back to HTML download.
   page.evaluate('window.open = () => null')
   with page.expect_download() as download_event:
    page.locator('#record-see-report').click()
   saved_report=download_event.value
   assert saved_report.suggested_filename.endswith('.html')
   assert 'anti-murphy-relatorio-' in saved_report.suggested_filename
   assert 'Decisão efetivamente registrada' in Path(saved_report.path()).read_text('utf8')
   assert page.locator('#presentation-restart').is_visible()
   page.locator('#presentation-restart').click()
   assert '01 / 06' in page.locator('#presentation-title').inner_text()
   assert 'SEM INTERVENÇÃO' not in evidence.inner_text()
   page.locator('#presentation-toggle').click()
   assert page.locator('#presentation-guide').is_hidden()
   assert page.locator('#sim-metrics').is_visible()
   page.locator('[data-nav="analise"]').click()
   assert page.locator('#view-analise').is_visible()
   assert not errors,errors
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 3')
   print(f'Modo Banca premium OK {width}x{height} · progressive / dual panels / justification / record / report',flush=True)
   page.close()
 browser.close()
