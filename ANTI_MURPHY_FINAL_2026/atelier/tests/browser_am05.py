"""AM-05 real-HTTP browser acceptance, using an isolated Studio per viewport.

Run: python -m atelier.tests.browser_am05
Optional AM05_QA_OUT overrides evidence directory. Requires Chromium/Playwright.
Requests execute the real Python engine; response holds test network races only.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer

from playwright.sync_api import sync_playwright, expect

from atelier.service import Studio
from atelier import server

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('AM05_QA_OUT', ROOT / 'docs/AM05/capturas_browser'))
VIEWPORTS = [(1280, 720), (1366, 768), (1920, 1080)]


def status(page, scope, code):
    host = {'lab':'#lab-results','advanced':'#advanced-results','dash':'#dash-body'}[scope]
    node = page.locator(host+' [data-analysis-status]').first
    expect(node).to_have_attribute('data-analysis-status', code, timeout=15000)
    return node.inner_text()


def settle(page):
    # Drain promise/render callbacks after a completed network body.
    page.wait_for_timeout(80)


def run_lab(page, mode):
    page.locator('[data-nav=laboratorio]').click()
    page.locator(f'#lab-tabs [data-lab="{mode}"]').click()
    with page.expect_response(lambda r:r.url.endswith('/api/lab')) as event:
        page.locator('#run-lab').click()
    result=event.value.json();settle(page)
    return result


def run_advanced(page, mode):
    page.locator('[data-nav=avancadas]').click()
    page.locator(f'#advanced-tabs [data-advanced="{mode}"]').click()
    with page.expect_response(lambda r:r.url.endswith('/api/advanced')) as event:
        page.locator('#advanced-run').click()
    result=event.value.json();settle(page)
    return result


def download_text(page, selector):
    with page.expect_download() as event:
        page.locator(selector).click()
    return Path(event.value.path()).read_text('utf-8-sig')


def pick_old(page, scope, index=1):
    attr={'lab':'data-lab-history','advanced':'data-advanced-history','dash':'data-dash-history'}[scope]
    button=page.locator(f'[{attr}]').nth(index)
    expect(button).to_be_attached(timeout=10000)
    details=button.locator('xpath=ancestor::details[1]')
    if details.count() and details.get_attribute('open') is None:
        details.locator('summary').click()
    button.click();settle(page)


def duplicate(page, name):
    page.locator('#project-manager').click()
    page.locator('#project-new-name').fill(name)
    page.locator('#project-duplicate').check()
    with page.expect_response(lambda r:r.url.endswith('/api/project/create')) as event:
        page.locator('#project-create').click()
    result=event.value.json();settle(page)
    return result


def select_action(page, studio, name):
    data=studio.info();row=next(x for x in data['alternatives'] if x['action']==name)
    page.locator('[data-nav=analise]').click()
    with page.expect_response(lambda r:r.url.endswith('/api/select')):
        page.locator(f'#alternatives-table tr[data-signature="{row["signature"]}"]').click()
    settle(page)


def held_request(page, path, click):
    """Finish backend computation, delay only delivery to browser JS."""
    pending=[]
    def hold(route):
        response=route.fetch()
        pending.append((route,response,response.json()))
    page.route('**'+path,hold)
    click()
    for _ in range(300):
        if pending:break
        page.wait_for_timeout(20)
    assert pending,'Request did not reach the real HTTP backend'
    return pending


def release(page,path,pending):
    route,response,result=pending.pop(0)
    route.fulfill(response=response)
    page.unroute('**'+path)
    settle(page)
    return result


def check_viewport(browser,width,height):
    with TemporaryDirectory() as tmp:
        studio=Studio(Path(tmp));server.STUDIO=studio
        httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        worker=Thread(target=httpd.serve_forever,daemon=True);worker.start()
        page=browser.new_page(viewport={'width':width,'height':height},accept_downloads=True)
        errors=[];requests=[];checks=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:requests.append(r.url) if r.method=='POST' else None)
        try:
            page.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle')
            page.wait_for_selector('#factory-a .station-group',timeout=20000)
            page.evaluate('document.querySelector("#splash")?.remove()')
            # Changing a relevant control must invalidate visible results and exports.
            page.locator('[data-nav=laboratorio]').click();page.locator('[data-lab=goal]').click()
            page.locator('#goal-value').fill('0')
            old=run_lab(page,'goal');assert len(old['points'])==18
            status(page,'lab','atual');before_posts=len(requests)
            page.locator('#goal-value').fill('100');page.locator('#goal-value').blur()
            status(page,'lab','desatualizado');assert len(requests)==before_posts
            text=download_text(page,'#lab-results [data-eng-export]')
            assert 'Estado na exportação: desatualizado' in text
            svg=download_text(page,'#lab-results [data-eng-export-svg]')
            assert 'DESATUALIZADO' in svg.upper()
            assert old['provenance']['project_id'] in svg
            page.screenshot(path=str(OUT/f'01_meta_desatualizada_{width}.png'))
            new=run_lab(page,'goal');assert len(new['points'])==1
            status(page,'lab','atual')
            checks.append('SLA0->100: stale, no autorun, CSV/SVG origin+stale, rerun1result')
            # Same parameters preserve deterministic signature and classify older entry as historical.
            again=run_lab(page,'goal')
            assert again['provenance']['signature']==new['provenance']['signature']
            pick_old(page,'lab');status(page,'lab','historico')
            assert 'Estado na exportação: historico' in download_text(page,'#lab-results [data-eng-export]')
            svg=download_text(page,'#lab-results [data-eng-export-svg]')
            assert 'HISTÓRICO' in svg.upper() or 'HISTORICO' in svg.upper()
            checks.append('same-config signature deterministic; historical UI/CSV/SVG')
            # A selected response is irrelevant to the duration sweep.
            run_lab(page,'duration');status(page,'lab','atual')
            select_action(page,studio,'Não intervir')
            page.locator('[data-nav=laboratorio]').click();page.locator('[data-lab=duration]').click()
            status(page,'lab','atual');checks.append('duration current after irrelevant alternative selection')
            # The original sensitivity result is retained through control changes and tabs.
            page.locator('[data-nav=avancadas]').click();page.locator('[data-advanced=sensitivity]').click()
            page.locator('#advanced-station').select_option('CNC');page.locator('#advanced-resource').select_option('operadores')
            advanced=run_advanced(page,'sensitivity');status(page,'advanced','atual')
            before_posts=len(requests)
            page.locator('#advanced-station').select_option('SOLDA');status(page,'advanced','desatualizado')
            assert len(requests)==before_posts
            exported=json.loads(download_text(page,'#advanced-export'));assert exported['status']=='desatualizado'
            assert exported['proveniencia']['inputs']['station']=='CNC'
            page.locator('#advanced-station').select_option('CNC');status(page,'advanced','atual')
            page.locator('#advanced-resource').select_option('maquinas');status(page,'advanced','desatualizado')
            page.locator('#advanced-resource').select_option('operadores');status(page,'advanced','atual')
            page.locator('[data-advanced=diagnostic]').click();page.locator('[data-advanced=sensitivity]').click()
            status(page,'advanced','atual')
            run_advanced(page,'sensitivity');pick_old(page,'advanced');status(page,'advanced','historico')
            assert json.loads(download_text(page,'#advanced-export'))['status']=='historico'
            checks.append('advanced station/resource invalidate+restore, tabs/history, JSON provenance')
            # Capacity inputs are meaningful as well; neither UI control should autorun.
            page.locator('[data-nav=laboratorio]').click();page.locator('[data-lab=capacity]').click()
            page.locator('#goal-value').fill('80');page.locator('#throughput-value').fill('5.5')
            run_lab(page,'capacity');status(page,'lab','atual');before_posts=len(requests)
            page.locator('#throughput-value').fill('6');page.locator('#throughput-value').blur()
            status(page,'lab','desatualizado');assert len(requests)==before_posts
            checks.append('capacity throughput input stale without autorun')
            # Real late response: old goal result is retained but stale against the new control.
            page.locator('[data-lab=goal]').click();page.locator('#goal-value').fill('0')
            held=held_request(page,'/api/lab',lambda:page.locator('#run-lab').click())
            page.locator('#goal-value').fill('100');page.locator('#goal-value').blur()
            release(page,'/api/lab',held);status(page,'lab','desatualizado')
            checks.append('late lab response after target change remains stale')
            # Late advanced response may not replace a different selected tool.
            page.locator('[data-nav=avancadas]').click();page.locator('[data-advanced=sensitivity]').click()
            page.locator('#advanced-station').select_option('CNC')
            held=held_request(page,'/api/advanced',lambda:page.locator('#advanced-run').click())
            page.locator('[data-advanced=diagnostic]').click()
            release(page,'/api/advanced',held)
            expect(page.locator('#advanced-title')).to_have_text('Diagnóstico operacional')
            assert page.locator('#advanced-results .eng-suite').count()==0
            page.locator('[data-advanced=sensitivity]').click()
            pick_old(page,'advanced',0)
            status(page,'advanced','atual')
            checks.append('late advanced response retained without replacing active different tool')
            # Monte Carlo must retain source identity after cloning a numerically equal project.
            select_action(page,studio,'Manutenção expressa · CNC')
            page.locator('[data-nav=paineis]').click();page.locator('[data-dash-tab=robustez]').click()
            with page.expect_response(lambda r:r.url.endswith('/api/advanced')) as event:
                page.locator('[data-dash-robust-run]').click()
            origin=event.value.json()['provenance'];settle(page);status(page,'dash','atual')
            first_project=origin['project_id'];clone=duplicate(page,f'Clone QA {width}')
            assert clone['active_project_id']!=first_project
            page.locator('[data-nav=paineis]').click();page.locator('[data-dash-tab=robustez]').click()
            text=status(page,'dash','desatualizado');assert first_project in text
            checks.append('Monte Carlo project clone source retained and stale, not current')
            # Arrival of a result after project switch must not be accepted as current.
            page.locator('[data-nav=avancadas]').click();page.locator('[data-advanced=uncertainty]').click()
            held=held_request(page,'/api/advanced',lambda:page.locator('#advanced-run').click())
            old_project=held[0][2]['provenance']['project_id']
            cloned=duplicate(page,f'Novo projeto QA {width}')
            assert cloned['active_project_id']!=old_project
            release(page,'/api/advanced',held)
            page.locator('[data-nav=avancadas]').click();page.locator('[data-advanced=uncertainty]').click()
            text=status(page,'advanced','desatualizado');assert old_project in text
            page.screenshot(path=str(OUT/f'02_origem_historica_{width}.png'))
            checks.append('late response after project switch accessible with original source+stale')
            assert not errors,errors
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
            print(f'AM05 BROWSER OK {width}x{height}: {len(checks)} checks, no JS errors',flush=True)
            return {'viewport':[width,height],'checks':checks,'page_errors':errors,'post_requests':len(requests)}
        except Exception:
            page.screenshot(path=str(OUT/f'FALHA_{width}.png'),full_page=True)
            raise
        finally:
            page.close();httpd.shutdown();httpd.server_close();worker.join(timeout=5)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        try:results=[check_viewport(browser,*size) for size in VIEWPORTS]
        finally:browser.close()
    (OUT/'resultados_am05_browser.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    return results


if __name__=='__main__':run()
