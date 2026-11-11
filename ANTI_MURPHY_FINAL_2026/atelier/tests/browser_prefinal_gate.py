"""Pre-final browser QA with the real Python Studio, real scripts and a local bridge.
Uses an embedded HTML document because this runner disallows direct local browser navigation.
The app's HTTP endpoints are separately tested over an actual server connection.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import base64, json, traceback
from playwright.sync_api import sync_playwright
from atelier.service import Studio

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'atelier'/'web'
OUT=ROOT/'docs'/'prefinal_qa'
OUT.mkdir(exist_ok=True)
html=(WEB/'index.html').read_text('utf8')
for name in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
    data=(WEB/'brand'/name).read_bytes()
    mime='image/png' if name.endswith('png') else 'image/svg+xml'
    html=html.replace('/brand/'+name,'data:'+mime+';base64,'+base64.b64encode(data).decode())
for name in ('styles','design_vnext','dashboards','studio_final','release_quality','prefinal_polish','banca'):
    html=html.replace(f'<link rel="stylesheet" href="/{name}.css">','')
html=html.replace('<script src="/app.js" defer></script>','')
css='\n'.join((WEB/(name+'.css')).read_text('utf8') for name in ('styles','design_vnext','dashboards','studio_final','release_quality','prefinal_polish','banca'))
js=(WEB/'app.js').read_text('utf8')
all_errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width,height in [(1366,768),(1920,1080),(1280,720)]:
      with TemporaryDirectory() as temp:
        studio=Studio(Path(temp))
        def bridge(path,method='GET',body=None):
          try:
            body=body or {}
            if path=='/api/state':value=studio.info()
            elif path=='/api/dashboards':value=studio.dashboards()
            elif path=='/api/history':value=studio.history()
            elif path.startswith('/api/history/'):value=studio.read_history(path.rsplit('/',1)[-1])
            elif path=='/api/assistant':value=studio.assistant(body.get('question',''))
            elif path=='/api/run':value=studio.calculate(body)
            elif path=='/api/select':value=studio.select(body.get('signature',''))
            elif path=='/api/record':value=studio.decision(body)
            elif path=='/api/lab':value=studio.lab(body)
            elif path=='/api/advanced':value=studio.advanced(body)
            elif path=='/api/model':value=studio.set_model(body)
            elif path=='/api/reset':value=studio.reset()
            elif path=='/api/projects':value=studio.projects()
            elif path=='/api/experiments':value=studio.experiment_list()
            else:raise RuntimeError('Not part of QA: '+path)
            return {'ok':True,'status':200,'data':value}
          except Exception as e:return {'ok':False,'status':400,'data':{'error':str(e)}}
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        page.on('pageerror',lambda e:all_errors.append(f'{width}: {e}'))
        page.expose_function('am_bridge',bridge)
        page.set_content(html,wait_until='load')
        page.add_style_tag(content=css)
        page.evaluate('''window.fetch=async (path,options={})=>{
          const body=options.body ? JSON.parse(options.body):{};
          const result=await window.am_bridge(path,options.method||'GET',body);
          return {ok:result.ok,status:result.status,json:async()=>result.data};
        }''')
        page.add_script_tag(content=js)
        page.wait_for_selector('#factory-a .station-group',timeout=20000)
        page.wait_for_timeout(1850)
        page.evaluate('document.querySelector("#splash")?.remove()')
        assert page.locator('#operational-hud').count()==1
        assert page.locator('#operational-hud strong').count()==3
        # At t=10 in scenario incident, the CNC is down and all incident-delayed orders are marked.
        horizon=max(r['horizon'] for r in studio.info()['replay'].values())
        page.locator('#timeline-range').fill(str(int(10000*10/horizon)))
        page.wait_for_timeout(150)
        assert 'down' in page.locator('#factory-a [data-station="CNC"]').get_attribute('class')
        assert '1 parado(s)' in page.locator('#stage-activity-summary').inner_text(),page.locator('#stage-activity-summary').inner_text()
        assert page.locator('#orders-row .order-mini.delayed').count()==studio.info()['metrics']['incident']['late_orders']
        page.screenshot(path=str(OUT/f'operacao_{width}.png'),full_page=False)
        # A/B comparison preserved.
        page.locator('[data-scene="split"]').click()
        assert page.locator('#split-control').is_visible()
        assert page.locator('#factory-b .station-group').count()==5
        page.screenshot(path=str(OUT/f'comparacao_{width}.png'),full_page=False)
        # The investigation path uses recorded late orders and leads back to the replay.
        page.locator('[data-nav="analise"]').click()
        assert page.locator('.impact-path-node').count()==3
        assert 'CNC' in page.locator('.impact-path').inner_text()
        page.locator('#impact-interpretation').scroll_into_view_if_needed()
        page.screenshot(path=str(OUT/f'analise_{width}.png'),full_page=False)
        page.locator('[data-impact-go="orders"]').click()
        assert page.locator('#view-simulacao').is_visible()
        assert page.locator('#station-inspector .order-trace').count()==1
        # Dashboard cost scope, navigation, responsiveness.
        page.locator('[data-nav="paineis"]').click()
        page.wait_for_selector('#dash-body .dash-stat',timeout=20000)
        page.locator('[data-dash-tab="desempenho"]').click()
        assert 'Multas' in page.locator('#dash-body').inner_text()
        page.screenshot(path=str(OUT/f'custos_{width}.png'),full_page=False)
        # Murphy answer about bottleneck and risk must reflect the same DES records.
        page.locator('[data-nav="decisoes"]').click()
        page.locator('#assistant-input').fill('Qual o gargalo da operação e quais pedidos estão em risco? Posto selecionado CNC')
        page.locator('#assistant-form button').click()
        page.wait_for_function("document.querySelectorAll('.assistant-message').length>=2",timeout=15000)
        assistant_text=page.locator('#assistant-messages').inner_text()
        assert 'Gargalo identificado pelo motor' in assistant_text
        assert 'Maior espera média registrada' in assistant_text
        assert 'Pedidos com atraso previsto' in assistant_text
        page.screenshot(path=str(OUT/f'murphy_{width}.png'),full_page=False)
        # Validation is visible inline before persistence.
        page.locator('#decision-note').fill('curto')
        page.locator('#register-decision').click()
        assert page.locator('#decision-validation').is_visible()
        assert not studio.history()
        note='Optamos por avaliar manutenção rápida devido aos prazos simulados; confirmar custos e habilidades.'
        page.locator('#decision-note').fill(note)
        page.locator('#decision-risks').fill('Confirmar recursos, habilidades, manutenção e limites do modelo.')
        page.locator('#decision-ack').check()
        page.locator('#register-decision').click()
        page.wait_for_function("document.querySelector('#view-historico') && !document.querySelector('#view-historico').hidden",timeout=10000)
        assert len(studio.history())==1
        assert note in page.locator('#history-detail').inner_text() or note in json.dumps(studio.history(),ensure_ascii=False)
        assert not all_errors,all_errors
        # horizontal overflow on body is not okay, vertical navigation is allowed.
        overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
        assert overflow<=2,('horizontal overflow',width,overflow)
        print('QA',width,'AI+costs+decision+factory+dashboards OK',flush=True)
        page.close()
    browser.close()
print('browser JS errors',all_errors)
