import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from unittest.mock import patch
from simulation.factory import build_scenario
from simulation.engine import run_simulation

def cfg(eff=1,minutes=.06):
 s={'P':{'nome':'Posto','maquinas':1,'operadores':1,'operadores_por_maquina':1,'eficiencia_operador':eff,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':20,'setup_min':0}}
 o=[{'id':'A','cliente':'C','produto':'X','quantidade':1,'prazo_h':100,'multa_hora':100,'route':[('P',minutes)]}]
 return build_scenario('Referência independente',s,o)
with patch('simulation.engine._noise',return_value=1):
 for name,c in [('short',cfg()),('efficiency',cfg(.001,60))]:
  r=run_simulation(c)
  print(json.dumps({'case':name,'end_h':r['operations'][0]['end_h'],'makespan_h':r['makespan_h'],'throughput_h':r['throughput_h'],'utilization':r['stations'][0]['Utilização máquina (%)'],'sla_pct':r['sla_pct'],'total_cost':r['total_cost']},ensure_ascii=False))
