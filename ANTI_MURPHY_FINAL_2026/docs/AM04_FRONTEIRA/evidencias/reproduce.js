const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync(process.argv[2], 'utf8');
const extract = (start, end) => src.slice(src.indexOf(start), src.indexOf(end, src.indexOf(start)));
const scenarios = {
  lower_first: [['A', 100, 80], ['B', 100, 100]],
  higher_first: [['B', 100, 100], ['A', 100, 80]],
  equivalent: [['A', 100, 100], ['B', 100, 100]],
  precise_sla: [['A', 100, 80], ['B', 101, 80.00005]],
};
for (const [name, rows] of Object.entries(scenarios)) {
  const alternatives = rows.map(([signature, decision_cost, sla_pct]) => ({signature, action: signature, decision_cost, sla_pct, feasible: true, within_budget: true, meets_sla: true}));
  const nodes = {'frontier-chart': {setAttribute(){}, innerHTML:'', querySelectorAll(){return [];}}, 'frontier-description':{textContent:''}};
  const ctx = {$: id=>nodes[id], st:{data:{alternatives,selected:'A'}}, dashUI:{data:{alternatives,selected:'A'}}, esc:String,brl:String,h:String,dashMoney:String,dashPct:String};
  vm.createContext(ctx);
  vm.runInContext(extract('const modeledEligible', 'function dashScenarios(')+extract('function renderFrontier(', 'async function selectAlternative(')+extract('function dashTradeoffPlot(', 'function dashOptimize('), ctx);
  vm.runInContext('renderFrontier()', ctx);
  const dashboard = vm.runInContext('dashTradeoffPlot()', ctx);
  console.log(JSON.stringify({case:name,analysis:nodes['frontier-description'].textContent,dashboard:dashboard.match(/<strong>(\d+) alternativa\(s\) não dominada\(s\)/)?.[1],line:nodes['frontier-chart'].innerHTML.match(/<polyline[^>]*>/)?.[0]||null}));
}
