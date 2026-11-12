from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
from atelier.service import Studio

with TemporaryDirectory() as d:
    s=Studio(Path(d))
    station=next(iter(s.state['stations'].values())).copy()
    station.update(maquinas=1,operadores=1,operadores_por_maquina=1)
    payload={'stations':{'P':station},'orders':[{'id':'A','quantidade':2500,'prazo_h':100,
             'multa_hora':10,'route':[['P',1]]*10000}]}
    previous=s.info()['run_id']
    with patch('atelier.service.execute',side_effect=RuntimeError('EXECUTION_REACHED_WITHOUT_RUNNING_DES')) as execute:
        try:s.set_model(payload)
        except Exception as e:print(type(e).__name__,str(e))
        print(json.dumps({'json_bytes':len(json.dumps(payload).encode()),'requested_operations':25000000,
                          'execute_calls':execute.call_count,'previous_run_preserved':s.info()['run_id']==previous}))
