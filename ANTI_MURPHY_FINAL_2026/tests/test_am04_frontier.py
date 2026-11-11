"""Independent finite-set oracle for the actual JavaScript chart functions."""
import itertools
import json
from pathlib import Path
import random
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
DRIVER = r"""
const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(process.argv[1],'utf8');
const extract=(start,end)=>src.slice(src.indexOf(start),src.indexOf(end,src.indexOf(start)));
const functions=extract('const modeledEligible','function dashScenarios(')
 +extract('function renderFrontier(','async function selectAlternative(')
 +extract('function dashTradeoffPlot(','function dashOptimize(');
const cases=JSON.parse(fs.readFileSync(0,'utf8'));
const results=cases.map(alternatives=>{
 const before=JSON.stringify(alternatives),selected=alternatives[0]?.signature;
 const nodes={'frontier-chart':{innerHTML:'',setAttribute(){},querySelectorAll(){return [];}},'frontier-description':{textContent:''}};
 const ctx={alternatives,$:id=>nodes[id],st:{data:{alternatives,selected}},dashUI:{data:{alternatives,selected}},esc:String,brl:String,h:String,dashMoney:String,dashPct:String};
 vm.createContext(ctx);vm.runInContext(functions,ctx);
 const frontier=vm.runInContext('costSlaFrontier(alternatives).map(a=>a.signature)',ctx);
 vm.runInContext('renderFrontier()',ctx);
 const dashboard=vm.runInContext('dashTradeoffPlot()',ctx);
 return {frontier,description:nodes['frontier-description'].textContent,
  dashboardCount:Number(dashboard.match(/<strong>(\d+) alternativa\(s\) não dominada\(s\)/)?.[1]||0),
  analysisDots:(nodes['frontier-chart'].innerHTML.match(/data-signature=/g)||[]).length,
  dashboardDots:(dashboard.match(/data-dash-select=/g)||[]).length,
  analysisLine:nodes['frontier-chart'].innerHTML.match(/<polyline[^>]*>/)?.[0]||null,
  unchanged:JSON.stringify(alternatives)===before&&ctx.st.data.selected===selected&&ctx.dashUI.data.selected===selected};
});
process.stdout.write(JSON.stringify(results));
"""


def row(signature, cost, sla, **extra):
    return dict(signature=signature, action=signature, decision_cost=cost,
                sla_pct=sla, feasible=True, within_budget=True, meets_sla=True, **extra)


def charts(cases):
    run = subprocess.run(['node', '-e', DRIVER, str(ROOT/'atelier/web/app.js')],
                         input=json.dumps(cases), text=True, capture_output=True, check=True)
    return json.loads(run.stdout)


def oracle(rows):
    """Reference definition: a is dominated iff a strictly better rival exists."""
    eligible = [x for x in rows if all(x[k] is True for k in ('feasible', 'within_budget', 'meets_sla'))]
    return sorted(x['signature'] for x in eligible if not any(
        y['decision_cost'] <= x['decision_cost'] and y['sla_pct'] >= x['sla_pct']
        and (y['decision_cost'] < x['decision_cost'] or y['sla_pct'] > x['sla_pct'])
        for y in eligible))


@pytest.mark.parametrize('rows', [
    [row('A', 100, 80), row('B', 100, 100)],
    [row('B', 100, 100), row('A', 100, 80)],
    [row('A', 100, 100), row('B', 100, 100)],
    [row('A', 99, 80), row('B', 100, 80)],
    [row('A', 100, 80), row('B', 101, 80.00005)],
    [row('A', 100.000001, 80), row('B', 100, 80)],
    [row('A', 0, 0), row('B', 0, 100)],
    [],
])
def test_frontier_matches_exact_independent_definition(rows):
    got = charts([rows])[0]
    assert sorted(got['frontier']) == oracle(rows)
    assert got['dashboardCount'] == len(got['frontier'])
    assert got['analysisDots'] == got['dashboardDots'] == len(rows)
    assert got['unchanged']  # A dominated selection remains available and selected.
    if rows:
        assert f"{len(got['frontier'])} não dominada(s) em custo e SLA" in got['description']


def test_permutations_keep_membership_order_and_equivalent_alternatives():
    rows = [row('A', 100, 80), row('B', 100, 100), row('C', 100, 100), row('D', 90, 70)]
    got = charts(list(itertools.permutations(rows)))
    assert all(x['frontier'] == ['D', 'B', 'C'] for x in got)
    assert all(x['dashboardCount'] == 3 and x['unchanged'] for x in got)
    assert len({x['analysisLine'] for x in got}) == 1


@pytest.mark.parametrize('flag', ['feasible', 'within_budget', 'meets_sla'])
def test_unqualified_rival_cannot_dominate_a_qualified_alternative(flag):
    valid, unqualified = row('A', 100, 80), row('B', 1, 100)
    unqualified[flag] = False
    got = charts([[valid, unqualified]])[0]
    assert got['frontier'] == ['A']
    assert got['analysisDots'] == got['dashboardDots'] == 2
    assert got['unchanged']


def test_all_unqualified_produces_no_frontier_but_preserves_points():
    rows = [row('A', 100, 80), row('B', 50, 100)]
    for x in rows:
        x['meets_sla'] = False
    got = charts([rows])[0]
    assert got['frontier'] == [] and got['dashboardCount'] == 0
    assert got['analysisLine'] is None
    assert got['analysisDots'] == got['dashboardDots'] == 2


def test_many_tied_and_untied_sets_match_independent_oracle():
    rng = random.Random(2026)
    cases = [[row(str(i), rng.choice([0, 10, 20, 30]), rng.choice([0, 40, 80, 100]))
              for i in range(rng.randrange(1, 12))] for _ in range(120)]
    for rows, got in zip(cases, charts(cases)):
        assert sorted(got['frontier']) == oracle(rows)
        assert got['dashboardCount'] == len(got['frontier'])
        assert got['unchanged']


def test_nonfinite_metrics_are_not_plotted_or_ranked():
    rows = [row('A', 100, 80), row('B', 'Infinity', 100), row('C', 0, 'NaN')]
    got = charts([rows])[0]
    assert got['frontier'] == ['A']
    assert got['analysisDots'] == got['dashboardDots'] == 1


def test_two_objective_plot_does_not_change_three_objective_record_review():
    from atelier.decision_quality import review_alternatives
    rows = [row('A', 100, 80, makespan_h=1), row('B', 100, 100, makespan_h=2)]
    assert charts([rows])[0]['frontier'] == ['B']
    review = review_alternatives(rows, 'A')
    assert review['status'] == 'non_dominated'
    assert review['metrics'] == ['decision_cost', 'makespan_h', 'sla_pct']
