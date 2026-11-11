"""Run a genuine V30.2 3-station case and export v1.1.0 Factory Command JSON."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from simulation.factory import ScenarioConfig, TimedAction
from simulation.trace_export import export_comparison_json


def demo_scenario():
    stations={
        sid:dict(nome=label,maquinas=1,operadores=1,operadores_por_maquina=1,
                 eficiencia_operador=1,disponibilidade=1,custo_operador_h=20,
                 custo_maquina_h=30,setup_min=0)
        for sid,label in [('CORTE','Corte'),('CNC','CNC'),('MONTAGEM','Montagem')]
    }
    orders=[dict(id='OP-DEMO',cliente='Exemplo sintético',produto='Componente',
                 quantidade=5,prazo_h=9.5,multa_hora=250,prioridade=1,
                 route=[('CORTE',12),('CNC',90),('MONTAGEM',15)])]
    cfg=ScenarioConfig(name='Factory Command — demo 3 postos',stations=stations,
                       orders=orders,chaos_station='CNC',chaos_start_h=.5,
                       chaos_duration_h=2.,seed=42)
    action=TimedAction(at_h=1.,label='Manutenção expressa (hipotética)',
                       repair_remaining_factor=.5)
    return cfg,action


if __name__=='__main__':
    cfg,action=demo_scenario()
    path=ROOT/'simulation_snapshot.json'
    bundle,a,b=export_comparison_json(cfg,action,path,keyframe_every=20,
                                       experiment_id='FC-V302-THREE-STATIONS')
    print('JSON:',path,'bytes:',path.stat().st_size)
    print('common:',len(bundle.common_history.events),'A:',len(bundle.branch_a.events),
          'B:',len(bundle.branch_b.events))
    print('A',a['makespan_h'],a['total_cost'],a['sla_pct'])
    print('B',b['makespan_h'],b['total_cost'],b['sla_pct'])
