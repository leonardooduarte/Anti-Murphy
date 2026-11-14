"""INT02: real short operations in audit/API/report; legacy/unknown UI transport fixtures."""
import json,os,math
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
from atelier.service import Studio
from atelier import server

out=Path(os.environ.get('INT02_QA_OUT','docs/INT02/capturas'));out.mkdir(parents=True,exist_ok=True)
def number(text):return float(text.replace(' h','').replace(',','.'))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1280,720),(1366,768),(1920,1080)]:
  with TemporaryDirectory() as d:
   folder=Path(d);s=Studio(folder)
   station={'nome':'P','maquinas':2,'operadores':2,'operadores_por_maquina':1,'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':5,'setup_min':0}
   s.set_model({'stations':{'P':station},'orders':[{'id':'CURTA','quantidade':2,'prazo_h':.0005,'multa_hora':10000,'route':[['P',.06]]}]})
   s.calculate({'station':'P','start_h':.0001,'duration_h':.001,'delay_h':0})
   chosen=next(r for r in s.info()['alternatives'] if r['action'].startswith('Manutenção expressa'));s.select(chosen['signature'])
   before=s.info();disk={p:p.read_bytes() for p in folder.rglob('*.json')};server.STUDIO=s
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);Thread(target=httpd.serve_forever,daemon=True).start()
   p=b.new_page(viewport={'width':w,'height':h},accept_downloads=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    p.goto(f'http://127.0.0.1:{httpd.server_port}/',wait_until='networkidle');p.wait_for_selector('#factory-a .station-group');p.evaluate('document.querySelector("#splash")?.remove()')
    p.locator('[data-nav=paineis]').click()
    with p.expect_response(lambda r:r.url.endswith('/api/technical-audit')) as ev:p.locator('[data-dash-tab=auditoria]').click()
    assert ev.value.ok;data=ev.value.json()
    for scenario in ['normal','incident','response']:
     p.locator('#dash-scenario').select_option(scenario)
     row=p.locator('#dash-body table tbody tr').first;expected=data['orders'][scenario][0]
     expect(row.locator('.dash-status')).to_have_text('Atrasado')
     values=[number(row.locator('td').nth(i).inner_text()) for i in [1,2,3]]
     for actual,key in zip(values,['due_h','finish_h','slack_h']):
      assert math.isclose(actual,expected[key],rel_tol=2e-6,abs_tol=1e-15),(actual,expected[key])
     assert values[1]>0 and values[2]<0
    p.screenshot(path=str(out/f'auditoria_{w}.png'))
    p.locator('[data-nav=decisoes]').click()
    with p.expect_popup() as ev:p.locator('#decision-report').click()
    popup=ev.value;popup.wait_for_load_state();row=popup.locator('table tbody tr').first
    assert 'CURTA' in row.inner_text() and 'Atrasado' in row.inner_text()
    assert number(row.locator('td').nth(3).inner_text())>0
    assert number(row.locator('td').nth(4).inner_text())<0
    (out/f'relatorio_{w}.html').write_text(popup.content());popup.screenshot(path=str(out/f'relatorio_{w}.png'));popup.close()
    p.evaluate('window.open=()=>null')
    with p.expect_download() as ev:p.locator('#decision-report').click()
    downloaded=Path(ev.value.path()).read_text();assert '0,0005 h' in downloaded and 'Atrasado' in downloaded
    # Only legacy/invalid fixture transport is synthetic; normal cases above use real HTTP/DES.
    fixture=deepcopy(data)
    for rows in fixture['orders'].values():
     for entry in rows:entry['timing_source']='legacy_rounded'
    p.route('**/api/technical-audit',lambda route:route.fulfill(status=200,json=fixture))
    p.locator('[data-nav=paineis]').click();p.locator('[data-dash-tab=auditoria]').click();p.locator('[data-audit-refresh]').click()
    expect(p.locator('[data-audit-legacy]')).to_be_visible()
    fixture=deepcopy(data)
    for rows in fixture['orders'].values():
     for entry in rows:entry.update(finish_h=None,slack_h=None,lateness_h=None,is_late=None,timing_source='unavailable')
    p.locator('[data-audit-refresh]').click()
    expect(p.locator('[data-audit-unknown]')).to_be_visible();expect(p.locator('#dash-body table .dash-status')).to_have_text('Não calculado')
    assert s.info()==before and all(p.read_bytes()==content for p,content in disk.items())
    assert not errors,errors
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
    print('INT02 BROWSER OK',w,h,'3 cenários, precisão API, sinais, relatório/pop-up/download, legado e desconhecido',flush=True)
   finally:p.close();httpd.shutdown();httpd.server_close()
 b.close()
