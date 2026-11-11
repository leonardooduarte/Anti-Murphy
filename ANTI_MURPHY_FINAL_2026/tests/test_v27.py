"""Regressões de engenharia, decisões causais e consistência de modelo."""
import math
import unittest
from copy import deepcopy

from data.scenarios import STATIONS_BASE, ORDERS_BASE
from simulation.engine import run_simulation
from simulation.factory import build_scenario
from simulation.validation import validate_model
from simulation.intelligence import resilience_index
from simulation.advanced import model_confidence
from simulation.decision_lab import (candidate_actions,config_signature,
                                     evaluate_decisions,paired_stress_test,pareto_flags,decision_report)


def simple(orders=1,staff=1,machines=1):
    stations={'P1':{'nome':'Posto 1','maquinas':machines,'operadores':staff,
        'operadores_por_maquina':1,'eficiencia_operador':1.,'disponibilidade':1.,
        'custo_maquina_h':20.,'custo_operador_h':10.,'setup_min':0}}
    ops=[{'id':'O1','cliente':'Teste','produto':'Peça','quantidade':orders,'prazo_h':5.,
        'multa_hora':100.,'route':[('P1',60.)]}]
    return build_scenario('Simples',stations,ops,dispatch_rule='FIFO',seed=17)


class TestV27(unittest.TestCase):
    def test_baseline_completo(self):
        r=run_simulation(build_scenario('Base',STATIONS_BASE,ORDERS_BASE))
        self.assertTrue(r['feasible'])
        self.assertEqual(r['total_units'],sum(o['quantidade'] for o in ORDERS_BASE))
        self.assertEqual(len(r['orders']),len(ORDERS_BASE))
        self.assertEqual(len(r['operations']),sum(o['quantidade']*len(o['route']) for o in ORDERS_BASE))
        self.assertGreater(r['makespan_h'],0)
        self.assertAlmostEqual(r['total_cost'],round(r['operating_cost']+r['penalty_total'],2),places=2)

    def test_same_seed_reproducible_and_scenario_name_neutral(self):
        c=simple(orders=15)
        r=run_simulation(c)
        self.assertEqual(r['operations'],run_simulation(c.clone('Outro nome'))['operations'])

    def test_worker_is_required(self):
        c=simple(orders=2,staff=0)
        r=run_simulation(c)
        self.assertFalse(r['feasible'])
        self.assertEqual(r['total_units'],0)
        self.assertEqual(len(r['operations']),0)
        self.assertTrue(all(o['Status']=='Bloqueada' for o in r['orders']))
        self.assertIsNone(r['orders'][0]['Conclusão (h)'])

    def test_absenteeism_total_blocks(self):
        c=simple(orders=2)
        c.absent_workers={'P1':1}
        self.assertFalse(run_simulation(c)['feasible'])

    def test_capacity_affects_completion(self):
        a=run_simulation(simple(orders=20,staff=1,machines=2))
        b=run_simulation(simple(orders=20,staff=2,machines=2))
        self.assertLess(b['makespan_h'],a['makespan_h'])

    def test_staffing_ratio_limits_parallel_resources(self):
        a=simple(orders=8,staff=1,machines=2)
        a.stations['P1']['operadores_por_maquina']=.5
        b=simple(orders=8,staff=1,machines=2)
        self.assertLess(run_simulation(a)['makespan_h'],run_simulation(b)['makespan_h'])
        c=simple(orders=2,staff=1,machines=2)
        c.stations['P1']['operadores_por_maquina']=2
        self.assertFalse(run_simulation(c)['feasible'])

    def test_incident_lowers_performance_and_busy_time_excludes_pause(self):
        c=simple(orders=1)
        normal=run_simulation(c)
        c.chaos_station='P1';c.chaos_start_h=.4;c.chaos_duration_h=3
        incident=run_simulation(c)
        self.assertGreater(incident['makespan_h'],normal['makespan_h']+2.9)
        self.assertGreater(incident['operations'][0]['Parada (h)'],2.9)
        self.assertLess(incident['stations'][0]['Utilização máquina (%)'],normal['stations'][0]['Utilização máquina (%)'])

    def test_outage_after_finishing_does_not_change_makespan(self):
        c=simple(orders=2)
        normal=run_simulation(c)
        c.chaos_station='P1';c.chaos_start_h=100.;c.chaos_duration_h=3
        later=run_simulation(c)
        self.assertEqual(later['makespan_h'],normal['makespan_h'])
        self.assertEqual(later['total_cost'],normal['total_cost'])
        self.assertFalse(any(x['type']=='murphy' for x in later['events']))

    def test_incident_before_release_waits(self):
        c=simple()
        c.orders[0]['release_h']=1
        c.chaos_station='P1';c.chaos_start_h=0;c.chaos_duration_h=3
        result=run_simulation(c)
        self.assertGreaterEqual(result['operations'][0]['Início (h)'],3)

    def test_validation_rejects_missing_station_and_negative_cost(self):
        c=simple()
        c.orders[0]['route']=[('FAKE',10)]
        c.stations['P1']['custo_maquina_h']=-1
        errors=validate_model(c.stations,c.orders)
        self.assertTrue(any('FAKE' in x for x in errors))
        self.assertTrue(any('custo_maquina_h' in x for x in errors))
        with self.assertRaises(ValueError):
            run_simulation(c)

    def test_model_score_not_perfect_with_invalid_route(self):
        c=simple()
        c.orders[0]['route']=[('POSTO_INEXISTENTE',60)]
        result=model_confidence(c.stations,c.orders)
        self.assertLess(result['score'],85)
        self.assertTrue(result['validation_errors'])

    def test_resilience_decreases_if_penalty_rises(self):
        a={'sla_pct':100,'penalty_total':0,'balance_loss_pp':10,'bottleneck':'P1',
           'stations':[{'Posto':'P1','Utilização máquina (%)':75.,'Espera média (min)':0,'Fila máx.':0}]}
        b=deepcopy(a);b['penalty_total']=8000
        self.assertGreater(resilience_index(a)['score'],resilience_index(b)['score'])

    def test_incident_equal_across_options(self):
        c=simple(orders=7)
        c.chaos_station='P1';c.chaos_start_h=.5;c.chaos_duration_h=2
        data=evaluate_decisions(c,budget=5000,sla_floor=10,cost_machine=3000)
        self.assertEqual(data['incident']['makespan_h'],run_simulation(c)['makespan_h'])
        self.assertFalse(data['normal']['config'].chaos_station)
        for row in data['rows']:
            if 'Manutenção expressa' not in row['action']:
                self.assertEqual(row['config'].chaos_duration_h,c.chaos_duration_h)
            self.assertEqual(row['config'].chaos_start_h,c.chaos_start_h)
            self.assertEqual(row['config'].seed,c.seed)
        self.assertTrue(any(r['action']=='Não intervir' and r['savings']==0 for r in data['rows']))

    def test_budget_and_infeasible_excluded(self):
        c=simple(orders=4)
        c.chaos_station='P1';c.chaos_duration_h=1
        data=evaluate_decisions(c,budget=100,cost_machine=1000,cost_worker=200)
        exp=[r for r in data['rows'] if r['investment']>100]
        self.assertTrue(exp)
        self.assertTrue(all(not x['within_budget'] and not x['pareto'] for x in exp))

    def test_signature_and_exports(self):
        c=simple()
        a=config_signature(c)
        self.assertEqual(a,config_signature(c.clone('Renomeado')))
        c.stations['P1']['maquinas']+=1
        self.assertNotEqual(a,config_signature(c))
        c=simple()
        data=evaluate_decisions(c)
        import json
        content=json.loads(decision_report(data,data['rows'][0]))
        self.assertEqual(content['modelo_sha256_16'],config_signature(c))

    def test_paired_runs(self):
        c=simple(orders=4)
        e=c.clone();e.stations['P1']['maquinas']=2;e.stations['P1']['operadores']=2
        result=paired_stress_test(c,e,runs=4)
        self.assertTrue(result['feasible'])
        self.assertEqual([p['seed'] for p in result['pairs']],[700,701,702,703])

    def test_pareto_dominance(self):
        a={'feasible':True,'within_budget':True,'decision_cost':80,'sla_pct':90,'makespan_h':5}
        b={'feasible':True,'within_budget':True,'decision_cost':100,'sla_pct':90,'makespan_h':6}
        c={'feasible':False,'within_budget':True,'decision_cost':1,'sla_pct':100,'makespan_h':1}
        self.assertEqual(pareto_flags([a,b,c]),[True,False,False])


if __name__=='__main__':
    unittest.main()
