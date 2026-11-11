"""Real HTTP app with controlled tie fixtures, then real engine selection.

The fixtures exercise chart rendering only; they are never saved as results.
"""
from http.server import ThreadingHTTPServer
from copy import deepcopy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import sync_playwright, expect

from atelier import server
from atelier.service import Studio

OUT = Path(os.environ.get('AM04_QA_OUT', 'docs/AM04/capturas'))
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                 args=['--no-sandbox', '--disable-dev-shm-usage'])
    try:
        for width, height in [(1280, 720), (1366, 768), (1920, 1080)]:
            with TemporaryDirectory() as storage:
                studio = Studio(Path(storage))
                server.STUDIO = studio
                httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
                Thread(target=httpd.serve_forever, daemon=True).start()
                page = browser.new_page(viewport={'width': width, 'height': height})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                real_state, real_dash = studio.info(), studio.dashboards()
                fixture = {'alternatives': None, 'selected': None}
                def serve_fixture(route):
                    if fixture['alternatives'] is None:
                        route.continue_()
                        return
                    original = real_dash if route.request.url.endswith('/api/dashboards') else real_state
                    body = {**deepcopy(original), **deepcopy(fixture)}
                    route.fulfill(status=200, json=body)
                page.route('**/api/state', serve_fixture)
                page.route('**/api/dashboards', serve_fixture)
                def load():
                    page.goto(f'http://127.0.0.1:{httpd.server_port}/', wait_until='networkidle')
                    page.wait_for_selector('#factory-a .station-group')
                    page.evaluate('document.querySelector("#splash")?.remove()')
                def set_fixture(costs, slas, qualifies, selected=0):
                    rows = deepcopy(real_state['alternatives'][:2])
                    for i, a in enumerate(rows):
                        a.update(action=f'Ensaio de empate {i+1}', decision_cost=costs[i], sla_pct=slas[i],
                                 feasible=True, within_budget=True, meets_sla=qualifies[i])
                    fixture.update(alternatives=rows, selected=rows[selected]['signature'])
                try:
                    signatures = [a['signature'] for a in real_state['alternatives'][:2]]
                    cases = [
                        ('custo_empatado', [100, 100], [80, 100], [True, True], [1]),
                        ('custo_empatado_inverso', [100, 100], [100, 80], [True, True], [0]),
                        ('equivalentes', [100, 100], [100, 100], [True, True], [0, 1]),
                        ('rival_fora_meta', [100, 10], [80, 100], [True, False], [0]),
                        ('sla_preciso', [100, 101], [80, 80.00005], [True, True], [0, 1]),
                    ]
                    for name, costs, slas, qualifies, expected_indices in cases:
                        expected = [signatures[i] for i in expected_indices]
                        set_fixture(costs, slas, qualifies)
                        load()
                        page.locator('[data-nav=analise]').click()
                        expect(page.locator('#frontier-chart .frontier-point')).to_have_count(2)
                        expect(page.locator('#frontier-description')).to_contain_text(f'{len(expected)} não dominada(s) em custo e SLA')
                        if name == 'custo_empatado':
                            expect(page.locator('#frontier-chart .frontier-line')).to_have_count(0)
                            page.locator('.frontier-panel').screenshot(path=str(OUT/f'analise_{width}.png'))
                        page.locator('[data-nav=paineis]').click()
                        page.wait_for_selector('#dash-body .dash-panel')
                        page.locator('[data-dash-tab=otimizacao]').click()
                        expect(page.locator('.dash-plot-note strong')).to_have_text(f'{len(expected)} alternativa(s) não dominada(s)')
                        actual = page.locator('.dash-chart-option.pareto').evaluate_all('es=>es.map(e=>e.dataset.dashSelect)')
                        assert sorted(actual) == sorted(expected), (name, actual, expected)
                        expect(page.locator('.dash-chart-option')).to_have_count(2)
                        if name == 'custo_empatado':
                            page.locator('#dash-body .dash-primary-panel').screenshot(path=str(OUT/f'dashboard_{width}.png'))
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+3')
                    # A real alternative remains selectable even when the controlled
                    # visual comparison classifies it as dominated. Use keyboard.
                    set_fixture([100, 100], [80, 100], [True, True], selected=1)
                    load()
                    page.locator('[data-nav=analise]').click()
                    point = page.locator('#frontier-chart .frontier-point').first
                    point.focus()
                    fixture['alternatives'] = None  # Subsequent requests use the real server.
                    with page.expect_response(lambda r: r.url.endswith('/api/select')) as response:
                        point.press('Enter')
                    assert response.value.ok
                    expect(page.locator('#frontier-chart .frontier-point.selected')).to_have_attribute('data-signature', signatures[0])
                    assert studio.info()['selected'] == signatures[0]
                    assert studio.history() == []
                    assert not errors, errors
                    print(json.dumps({'resolution': [width, height], 'controlled_cases': len(cases),
                                      'real_keyboard_selection': True, 'errors': errors}), flush=True)
                finally:
                    page.close()
                    httpd.shutdown()
                    httpd.server_close()
    finally:
        browser.close()
