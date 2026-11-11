from io import BytesIO
import pandas as pd
from data.importer import make_template,read_client_workbook
from simulation.model_io import frames_to_model


def frames():
    stations=pd.DataFrame([{'ID':'A','Posto':'Automática','Máquinas':1,'Operadores':0,
        'Automatizada':True,'Eficiência operador':1.,'Disponibilidade':1.}])
    orders=pd.DataFrame([{'ID':'OP-1','Cliente':'Exemplo','Produto':'Peça','Quantidade':1,
        'Prazo (h)':4.,'Liberação (h)':1.5,'Roteiro':'A:10'}])
    return stations,orders


def test_excel_round_trip_preserves_automation_and_order_release():
    ss,oo=frames();file=BytesIO(make_template(ss,oo));file.name='modelo.xlsx'
    s,o,_=read_client_workbook(file);stations,orders=frames_to_model(s,o)
    assert stations['A']['automatizada'] is True
    assert stations['A']['operadores']==0
    assert orders[0]['release_h']==1.5


def test_csv_locale_decimal_and_boolean_false_are_not_lost():
    ss,oo=frames();ss['Automatizada']='False';ss['Operadores']=1
    f=BytesIO(oo.to_csv(index=False,sep=';',decimal=',').encode());f.name='ordens.csv'
    s,o,_=read_client_workbook(f)
    assert s is None
    stations,orders=frames_to_model(ss,o)
    assert stations['A']['automatizada'] is False
    assert orders[0]['release_h']==1.5
