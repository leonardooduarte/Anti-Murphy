"""Baseline AM11 reproduction through real HTTP, without editing that source."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
import json
from playwright.sync_api import sync_playwright
from atelier.service import Studio
from atelier import server
OUT=Path('/workspace/work/am05');results={}
with TemporaryDirectory() as tmp:
 s=Studio(Path(tmp));server.STUDIO=s
 httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
 Thread(target=httpd.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
   p=b.new_page(viewport={'width':1366,'height':768},accept_downloads=True)
   p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group',state='attached');p.evaluate('document.querySelector("#splash")?.remove()')
   p.locator('[data-nav=laboratorio]').click();p.locator('[data-lab=goal]').click();p.locator('#goal-value').fill('0')
   with p.expect_response(lambda r:r.url.endswith('/api/lab')) as r:p.locator('#run-lab').click()
   old=r.value.json();p.wait_for_selector('#lab-results .eng-suite')
   p.locator('#goal-value').fill('100');p.locator('#goal-value').blur()
   results['goal_after_target100']=p.locator('#lab-result-count').inner_text()
   with p.expect_download() as d:p.locator('#lab-results [data-eng-export]').click()
   text=Path(d.value.path()).read_text('utf-8-sig');results['goal_csv_status']=text.splitlines()[0]
   results['old_goal_count']=len(old['points'])
   p.screenshot(path=str(OUT/'before-goal.png'))
   p.locator('[data-lab=duration]').click()
   with p.expect_response(lambda r:r.url.endswith('/api/lab')) as r:p.locator('#run-lab').click()
   p.wait_for_selector('#lab-results .eng-suite');points=r.value.json()['points']
   p.locator('[data-nav=analise]').click()
   state=s.info();other=next(a for a in state['alternatives'] if a['action']=='Não intervir')
   with p.expect_response(lambda r:r.url.endswith('/api/select')):p.locator('#alternatives-table tr[data-signature="'+other['signature']+'"]').click()
   p.locator('[data-nav=laboratorio]').click();results['duration_after_irrelevant_selection']=p.locator('#lab-result-count').inner_text()
   results['duration_points_equal_after_select']=points==s.lab({'mode':'duration'})['points']
   p.locator('[data-nav=avancadas]').click();p.locator('[data-advanced=sensitivity]').click();p.locator('#advanced-station').select_option('CNC')
   with p.expect_response(lambda r:r.url.endswith('/api/advanced')):p.locator('#advanced-run').click()
   p.wait_for_selector('#advanced-results .eng-suite');before=p.locator('#advanced-results').inner_text();p.locator('#advanced-station').select_option('SOLDA')
   results['advanced_unchanged_after_station']=before==p.locator('#advanced-results').inner_text()
   with p.expect_download() as d:p.locator('#advanced-export').click()
   results['advanced_export_status']=json.loads(Path(d.value.path()).read_text())['status']
   p.locator('[data-nav=laboratorio]').click();p.locator('[data-lab=duration]').click()
   for _ in range(2):
    with p.expect_response(lambda r:r.url.endswith('/api/lab')):p.locator('#run-lab').click()
   p.locator('#lab-results details.am-lab-history summary').click();p.locator('[data-lab-history]').nth(1).click()
   results['historical_ui']=p.locator('#lab-result-count').inner_text()
   with p.expect_download() as d:p.locator('#lab-results [data-eng-export]').click()
   results['historical_csv']=Path(d.value.path()).read_text('utf-8-sig').splitlines()[0]
   p.request.post(f'http://127.0.0.1:{httpd.server_port}/api/reset',data={})
   p.reload(wait_until='networkidle');p.wait_for_selector('#factory-a .station-group',state='attached');p.evaluate('document.querySelector("#splash")?.remove()')
   p.locator('[data-nav=paineis]').click();p.locator('[data-dash-tab=robustez]').click()
   with p.expect_response(lambda r:r.url.endswith('/api/advanced')) as r:p.locator('[data-dash-robust-run]').click()
   origin=r.value.json()['provenance']['project_id'];p.wait_for_selector('#dash-body .eng-suite')
   p.locator('#project-manager').click();p.locator('#project-new-name').fill('Duplicação QA');p.locator('#project-duplicate').check()
   with p.expect_response(lambda r:r.url.endswith('/api/project/create')) as r:p.locator('#project-create').click()
   new=r.value.json();p.locator('[data-nav=paineis]').click();p.locator('[data-dash-tab=robustez]').click()
   results['dashboard_cache_new_project']=new['active_project_id'];results['dashboard_cache_origin']=origin
   results['dashboard_cached_chart_survives_clone']=p.locator('#dash-body .eng-suite').count()==1
   b.close()
 finally:httpd.shutdown();httpd.server_close()
(OUT/'before-browser.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False,indent=2))
