"""Live browser E2E with real DES service in Python, transport adapted for sandbox."""
import base64
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from atelier.service import Studio
ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'atelier'/'web'
OUT=ROOT/'docs'/'capturas_reais'
OUT.mkdir(parents=True,exist_ok=True)
html=(WEB/'index.html').read_text('utf8')
for filename in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
    data=(WEB/'brand'/filename).read_bytes()
    mime='image/png' if filename.endswith('.png') else 'image/svg+xml'
    html=html.replace('/brand/'+filename,'data:'+mime+';base64,'+base64.b64encode(data).decode())
for n in ('styles','design_vnext','dashboards','studio_final','release_quality','prefinal_polish','banca','engineering_charts','final_banca'):
    html=html.replace(f'<link rel="stylesheet" href="/{n}.css">','')
for script in ('engineering_charts','app'):
    html=html.replace(f'<script src="/{script}.js" defer></script>','')
with TemporaryDirectory() as tmp,sync_playwright() as pw:
    studio=Studio(Path(tmp))
    def bridge(path,method='GET',body=None):
        try:
            body=body or {}
            if path=='/api/state':ans=studio.info()
            elif path=='/api/history':ans=studio.history()
            elif path=='/api/advanced':ans=studio.advanced(body)
            elif path=='/api/run':ans=studio.calculate(body)
            elif path=='/api/select':ans=studio.select(body.get('signature',''))
            elif path=='/api/model':ans=studio.set_model(body)
            elif path=='/api/reset':ans=studio.reset()
            elif path=='/api/record':ans=studio.decision(body)
            elif path=='/api/assistant':ans=studio.assistant(body.get('question',''))
            elif path=='/api/lab':ans=studio.lab(body)
            else:raise ValueError('Unsupported endpoint '+path)
            return {'ok':True,'status':200,'data':ans}
        except Exception as e:return {'ok':False,'status':400,'data':{'error':str(e)}}
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for w,h in [(1366,768),(1920,1080)]:
        page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.expose_function('am_bridge',bridge)
        page.set_content(html.replace('<script src="/analysis_state.js" defer></script>',''),wait_until='load')
        page.add_style_tag(content='\n'.join((WEB/(n+'.css')).read_text('utf8') for n in ('styles','design_vnext','dashboards','studio_final','release_quality','prefinal_polish','banca','engineering_charts','final_banca')))
        page.evaluate('''window.fetch=async(path,options={})=>{const r=await window.am_bridge(path,options.method||'GET',options.body?JSON.parse(options.body):{});return {ok:r.ok,status:r.status,json:async()=>r.data}}''')
        page.add_script_tag(content=(WEB/'analysis_state.js').read_text('utf8'))
        page.add_script_tag(content=(WEB/'engineering_charts.js').read_text('utf8'))
        page.add_script_tag(content=(WEB/'app.js').read_text('utf8'))
        page.locator('#sim-metrics .metric-unit').first.wait_for(timeout=30000)
        page.locator('#skip-intro').click()
        page.locator('#splash').wait_for(state='hidden',timeout=3000)
        page.locator('[data-nav=avancadas]').click()
        assert page.locator('#view-avancadas').is_visible()
        selected=studio.info()['selected']
        run=studio.info()['run_id']
        for mode in ['diagnostic','opportunities','sensitivity','demand','uncertainty','recovery']:
            page.locator(f'#advanced-tabs [data-advanced={mode}]').click()
            if mode=='sensitivity':page.locator('#advanced-station').select_option('CNC')
            page.locator('#advanced-run').click()
            page.wait_for_function('''() => document.getElementById('advanced-result-count').textContent.includes('resultado') || document.getElementById('advanced-result-count').textContent.includes('postos')''',timeout=30000)
            assert page.locator('#advanced-results tbody tr').count()>0,mode
            assert studio.info()['run_id']==run and studio.info()['selected']==selected
            if mode=='diagnostic':page.screenshot(path=str(OUT/f'diagnostico_avancado_{w}.png'),full_page=True)
            if mode=='opportunities':page.screenshot(path=str(OUT/f'oportunidades_{w}.png'),full_page=True)
        page.locator('#advanced-go-decisions').click()
        assert page.locator('#view-decisoes').is_visible()
        previous_records=len(studio.history())
        page.locator('#register-decision').click()
        page.wait_for_timeout(200)
        assert len(studio.history())==previous_records, 'Must require rationale'
        page.locator('#decision-note').fill('Avaliar alternativas e confirmar recursos antes de executar.')
        page.locator('#decision-ack').check()
        page.locator('#register-decision').click()
        page.wait_for_function('''() => document.querySelector('#view-historico:not([hidden])') !== null''',timeout=12000)
        assert len(studio.history())==previous_records+1
        page.locator('#back-home').click()
        assert page.locator('#view-simulacao').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2')
        assert not errors,errors
        print('ADV QA',w,'six tools, 1 decision, nav, no JS errors')
        page.close()
    browser.close()
