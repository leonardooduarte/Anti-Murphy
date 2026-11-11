"""Optional browser QA (requires Chromium + playwright): compares frontend seek to Pydantic seek."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from simulation_contract import ComparisonBundle,seek
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
bundle=ComparisonBundle.model_validate_json((ROOT/'factory_command_demo.json').read_text('utf8'))
html=(ROOT/'PREVIEW_FACTORY_COMMAND.html').read_text('utf8')
tests=0
with sync_playwright() as w:
    b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'],headless=True)
    page=b.new_page(viewport={'width':1440,'height':990})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    for side in ('A','B'):
        for h in (0,3,4,8,10,15,20,23):
            ti=int(h*3600000000)
            browser=page.evaluate('({side,t}) => window.__ANTI_MURPHY_QA__.stateAt(side,t)',{'side':side,'t':ti})
            python=seek(bundle,side,ti).model_dump(mode='json')
            for key in ('stations','units','orders'):
                if browser[key]!=python[key]:
                    raise AssertionError(f'{side} at {h} h: {key} differs')
            tests+=1
    page.locator('#play').click(); page.wait_for_timeout(350)
    assert float(page.locator('#clock').inner_text().split(' h')[0])>0
    page.locator('#markIncident').click(); assert page.locator('#planeA .down').count()>=1
    page.locator('#markFork').click(); page.locator('#planeA .station').first.click(force=True)
    assert 'visible' in page.locator('#tooltip').get_attribute('class')
    page.locator('#mode [data-mode="B"]').click();assert 'onlyB' in page.locator('#viewport').get_attribute('class')
    page.locator('#mode [data-mode="S"]').click();page.locator('#viewport').click(position={'x':400,'y':270})
    assert '--wipe' in page.locator('#viewport').get_attribute('style')
    assert not errors,errors
    print(f'Browser QA: {tests} A/B equivalence checks + 5 interactive flows; no JS errors')
    b.close()
