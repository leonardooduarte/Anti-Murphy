"""End-to-end UI flows backed by a real Python Studio.

Chromium cannot navigate to localhost in this runner, so HTML/CSS/JS are
loaded in-page; fetch is bridged to the real service functions. Separately,
HTTP route checks verify the live server.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from atelier.service import Studio
import base64, json

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'atelier'/'web'
OUTPUT=ROOT/'docs'/'banca_qa'
OUTPUT.mkdir(parents=True,exist_ok=True)
html=(WEB/'index.html').read_text('utf8')
for name in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
    mime='image/png' if name.endswith('png') else 'image/svg+xml'
    source=(WEB/'brand'/name).read_bytes()
    html=html.replace('/brand/'+name, 'data:'+mime+';base64,'+base64.b64encode(source).decode())
css_parts=['styles','design_vnext','dashboards','studio_final','release_quality','prefinal_polish','banca']
for name in css_parts: html=html.replace(f'<link rel="stylesheet" href="/{name}.css">','')
html=html.replace('<script src="/app.js" defer></script>','')
css='\n'.join((WEB/(name+'.css')).read_text('utf8') for name in css_parts)
js=(WEB/'app.js').read_text('utf8')
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    for width,height in [(1366,768),(1920,1080),(1280,720)]:
        with TemporaryDirectory() as folder:
            studio=Studio(Path(folder))
            def bridge(path,method='GET',body=None):
                body=body or {}
                try:
                    if path=='/api/state': value=studio.info()
                    elif path=='/api/dashboards': value=studio.dashboards()
                    elif path=='/api/technical-audit': value=studio.technical_audit()
                    elif path=='/api/history': value=studio.history()
                    elif path.startswith('/api/history/'):value=studio.read_history(path.rsplit('/',1)[-1])
                    elif path=='/api/record':value=studio.decision(body)
                    elif path=='/api/select':value=studio.select(body['signature'])
                    elif path=='/api/assistant':value=studio.assistant(body.get('question',''))
                    elif path=='/api/advanced':value=studio.advanced(body)
                    elif path=='/api/experiments':value=studio.experiment_list()
                    elif path=='/api/experiment-library':value=studio.experiment_library()
                    elif path=='/api/projects':value=studio.projects()
                    elif path=='/api/model':value=studio.set_model(body)
                    elif path=='/api/run':value=studio.calculate(body)
                    else:raise RuntimeError('Missing QA bridge for '+path)
                    return {'ok':True,'status':200,'data':value}
                except Exception as e:
                    return {'ok':False,'status':400,'data':{'error':str(e)}}
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            page.on('pageerror',lambda e:errors.append(f'{width}: {e}'))
            page.expose_function('am_bridge',bridge)
            page.set_content(html,wait_until='load')
            page.add_style_tag(content=css)
            page.evaluate('''window.fetch=async (path,options={})=>{
                const body=options.body?JSON.parse(options.body):{};
                const result=await window.am_bridge(path,options.method||'GET',body);
                return {ok:result.ok,status:result.status,json:async()=>result.data};
            }''')
            page.add_script_tag(content=js)
            page.wait_for_selector('#factory-a .station-group',timeout=20000)
            page.evaluate('document.querySelector("#splash")?.remove()')
            page.wait_for_timeout(100)
            assert 'reprodução pausada' in page.locator('#time-conversion').inner_text().lower() or not page.locator('#stage-mode-indicator').inner_text().endswith('ATIVA')
            assert page.locator('#speed-control').input_value()=='1'
            assert '10,00 min' in page.locator('#time-conversion').inner_text(),page.locator('#time-conversion').inner_text()
            page.locator('#speed-control').select_option('0.5')
            assert '5,00 min simulados/s' in page.locator('#time-conversion').inner_text()
            page.locator('#speed-control').select_option('1')
            page.screenshot(path=str(OUTPUT/f'inicio_{width}.png'),full_page=False)
            # On 8x, start of interruption occurs after ~3 s; automated pause is testable.
            page.locator('#speed-control').select_option('8')
            page.locator('#play-button').click(force=True)
            try:
                page.wait_for_function("document.querySelector('#stage-mode-indicator')?.textContent==='REPRODUÇÃO PAUSADA' && document.querySelector('#clock-label')?.textContent==='04:00 h'",timeout=9000)
            except Exception:
                print('CLOCK DEBUG',width,page.locator('#clock-label').inner_text(),page.locator('#stage-mode-indicator').inner_text(),page.locator('#toast').inner_text(),page.locator('#time-conversion').inner_text(),errors,flush=True)
                raise
            assert 'PARADA' in page.locator('#event-status').inner_text()
            # Response has a second distinct pause at the effective intervention time.
            if width==1366:
                page.locator('[data-scene="response"]').click(force=True)
                page.locator('#play-button').click(force=True)
                page.wait_for_function("document.querySelector('#stage-mode-indicator')?.textContent==='REPRODUÇÃO PAUSADA' && document.querySelector('#clock-label')?.textContent==='06:00 h'",timeout=7000)
                assert 'Intervenção aplicada' in page.locator('#toast').inner_text()
            page.locator('#speed-control').select_option('1')
            page.locator('[data-scene="split"]').click(force=True)
            assert page.locator('#compare-scoreboard').is_visible()
            assert page.locator('.compare-score').count()==2
            page.screenshot(path=str(OUTPUT/f'comparacao_{width}.png'),full_page=False)
            # Dashboard evidence: distinct criticality indicator and maximum wait.
            page.locator('[data-nav="paineis"]').click(force=True)
            page.wait_for_selector('#dash-body .dash-stat',timeout=12000)
            page.locator('[data-dash-tab="auditoria"]').click(force=True)
            page.wait_for_selector('.audit-heading',timeout=12000)
            heading=page.locator('#dash-body').inner_text()
            assert 'CORTE' in heading and 'CNC' in heading and 'MTBF' in heading
            assert page.locator('.audit-checks .failed').count()==0
            assert page.locator('.audit-checks .passed').count()==4
            page.screenshot(path=str(OUTPUT/f'auditoria_{width}.png'),full_page=True)
            page.locator('#dash-risk-limit').select_option('120')
            assert page.locator('#dash-risk-limit').input_value()=='120'
            # Existing dashboards still accessible.
            page.locator('[data-dash-tab="desempenho"]').click(force=True)
            assert 'Composição de custos' in page.locator('#dash-body').inner_text()
            page.locator('[data-dash-tab="otimizacao"]').click(force=True)
            assert page.locator('.dash-chart-option').count()>=1
            # Murphy's grounded answer
            page.locator('[data-nav="decisoes"]').click(force=True)
            page.locator('#assistant-input').fill('Qual o gargalo e quais pedidos estão em risco?')
            page.locator('#assistant-form button').click(force=True)
            page.wait_for_function("document.querySelectorAll('.assistant-message').length>=2",timeout=12000)
            assert 'Gargalo identificado' in page.locator('#assistant-messages').inner_text()
            note='Realocação avaliada por custo e prazo; verificar disponibilidade real de recursos e treinamento.'
            page.locator('#decision-note').fill(note)
            page.locator('#register-decision').click(force=True)
            assert len(studio.history())==0, 'Acknowledgement is mandatory in new UI'
            page.locator('#decision-ack').check(force=True)
            page.locator('#decision-risks').fill('Habilitação individual, tempo de manutenção, buffers e custo efetivamente evitável.')
            page.locator('#decision-owner').fill('Equipe de PCP')
            page.locator('#register-decision').click(force=True)
            page.wait_for_function("document.querySelector('#view-historico') && !document.querySelector('#view-historico').hidden",timeout=12000)
            assert len(studio.history())==1
            record=studio.read_history(studio.history()[0]['filename'])['record']
            assert record['constraints_ack'] and record['physical_feasibility_verified'] is False
            assert record['model_hash'] and record['responsible']=='Equipe de PCP'
            page.locator('.history-item').first.click(force=True)
            assert 'Riscos e verificações pendentes' in page.locator('#history-detail').inner_text()
            assert page.locator('.history-technical').count()==1
            page.screenshot(path=str(OUTPUT/f'registro_{width}.png'),full_page=False)
            # Report: its HTML is generated on click and remains locally printable.
            page.locator('[data-nav="decisoes"]').click(force=True)
            with page.expect_popup(timeout=9000) as popup_event:
                page.locator('#decision-report').click(force=True)
            popup=popup_event.value
            popup.wait_for_load_state('domcontentloaded')
            body=popup.locator('body').inner_text()
            assert 'Método econômico e indicadores' in body
            assert 'Folga B' in body
            assert 'Refugo' in body or 'refugo' in body
            assert popup.locator('tbody tr').count()==len(studio.info()['orders'])
            if width==1366:popup.screenshot(path=str(OUTPUT/'relatorio_tecnico.png'),full_page=True)
            popup.close()
            overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
            assert overflow<=2, (width,'horizontal page overflow',overflow)
            assert not errors,errors
            print('QA BANCA',width,'replay, costs, audit, dashboards, Murphy, structured record OK',flush=True)
            page.close()
    browser.close()
print('browser page errors',errors)
