"""Bounded individual scenarios, never the refused 25-million-operation case."""
import json, resource, subprocess, sys, time

if len(sys.argv)==1:
    for quantity,stages in [(100,4),(1000,6),(2500,10)]:
        subprocess.run([sys.executable,__file__,str(quantity),str(stages)],check=True)
else:
    from simulation.factory import build_scenario
    from simulation.engine import run_simulation
    q,k=map(int,sys.argv[1:])
    s={'nome':'P','maquinas':1,'operadores':1,'operadores_por_maquina':1,
       'eficiencia_operador':1,'disponibilidade':1,'custo_maquina_h':10,'custo_operador_h':10,'setup_min':0}
    cfg=build_scenario('Bounded benchmark',{'P':s},[{'id':'A','quantidade':q,'prazo_h':100,
                        'multa_hora':10,'route':[['P',1]]*k}])
    begin=time.perf_counter();result=run_simulation(cfg);elapsed=time.perf_counter()-begin
    assert len(result['operations'])==q*k
    print(json.dumps({'operations':q*k,'seconds':elapsed,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),flush=True)
