"""QA without loopback (the sandbox blocks browser HTTP to localhost).
Uses the true Python Studio service through the same local in-process bridge as browser_quality.py.
"""
import base64
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from atelier.service import Studio
ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'atelier'/'web'

def main():
    html=(WEB/'index.html').read_text('utf8')
    for filename in ['icon-dark.svg','logo-light.svg','logo-dark.svg','icon-32.png']:
        content=(WEB/'brand'/filename).read_bytes()
        kind='image/png' if filename.endswith('.png') else 'image/svg+xml'
        html=html.replace('/brand/'+filename,'data:'+kind+';base64,'+base64.b64encode(content).decode())
    html=html.replace('<link rel="stylesheet" href="/styles.css">','').replace('<script src="/app.js" defer></script>','')
    css=(WEB/'styles.css').read_text('utf8')
    js=(WEB/'app.js').read_text('utf8')
    with TemporaryDirectory() as scratch,sync_playwright() as p:
        studio=Studio(Path(scratch))
        def bridge(path,method='GET',body=None):
            try:
                body=body or {}
                if path=='/api/state':data=studio.info()
                elif path=='/api/history':data=studio.history()
                elif path=='/api/run':data=studio.calculate(body)
                elif path=='/api/select':data=studio.select(body['signature'])
                elif path=='/api/model':data=studio.set_model(body)
                elif path=='/api/reset':data=studio.reset()
                elif path=='/api/lab':data=studio.lab(body)
                elif path=='/api/advanced':data=studio.advanced(body)
                elif path=='/api/record':data=studio.decision(body)
                elif path=='/api/assistant':data=studio.assistant(body.get('question',''))
                else:raise RuntimeError('Unsupported route: '+path)
                return {'ok':True,'status':200,'data':data}
            except Exception as e:return {'ok':False,'status':400,'data':{'error':str(e)}}
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        for width,height in [(1280,720),(1366,768),(1920,1080)]:
            page=browser.new_page(viewport={'width':width,'height':height})
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.expose_function('am_bridge',bridge)
            page.set_content(html,wait_until='load')
            page.add_style_tag(content=css)
            page.evaluate('''window.fetch=async(path,options={})=>{const r=await window.am_bridge(path,options.method||'GET',options.body?JSON.parse(options.body):{});return {ok:r.ok,status:r.status,json:async()=>r.data}}''')
            page.add_script_tag(content=js)
            page.locator('#view-simulacao .metrics-line .metric-unit').first.wait_for(timeout=30000)
            page.locator('#skip-intro').click()
            assert page.locator('#back-home').is_visible()
            assert page.locator('#back-previous').is_visible()
            for route in ['modelo','analise','laboratorio','decisoes','historico']:
                page.locator(f'[data-nav="{route}"]').click()
                assert page.locator(f'#view-{route}').is_visible(),route
                assert page.locator('#back-home').is_enabled()
                page.locator('#back-home').click()
                assert page.locator('#view-simulacao').is_visible()
            page.locator('[data-nav="modelo"]').click()
            page.locator('[data-nav="analise"]').click()
            page.locator('#back-previous').click()
            assert page.locator('#view-modelo').is_visible(),'Voltar should restore model'
            page.locator('#back-home').click()
            assert page.locator('#view-simulacao').is_visible()
            page.locator('[data-nav="analise"]').click()
            page.locator('[data-nav="laboratorio"]').click()
            page.go_back(wait_until='domcontentloaded')
            assert page.locator('#view-analise').is_visible(), 'Browser Back should restore previous area'
            page.locator('#back-home').click()
            measured=page.evaluate('''() => ({
               width:window.innerWidth,scrollWidth:document.documentElement.scrollWidth,
               color:getComputedStyle(document.querySelector('.section-intro h1')).color,
               sidebar:getComputedStyle(document.querySelector('.rail-item.active')).color,
               back:getComputedStyle(document.querySelector('#back-previous')).color,
               buttons:document.querySelectorAll('.rail-item').length
             })''')
            assert measured['scrollWidth']<=measured['width']+2,measured
            assert not errors,errors
            print(f'NAV PASS {width}x{height}: 5 areas, home, previous, text, no JS errors',measured)
            (ROOT/'docs'/'capturas_reais').mkdir(parents=True,exist_ok=True)
            page.screenshot(path=str(ROOT/'docs'/'capturas_reais'/f'navegacao_{width}.png'))
            page.close()
        browser.close()
if __name__=='__main__':main()
