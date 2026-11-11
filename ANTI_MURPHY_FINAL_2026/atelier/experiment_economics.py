"""AM08 immutable monetary components; legacy reads never invent investment."""
from math import isfinite
from simulation.numeric import metric
from simulation.decision_lab import config_signature

FIELDS=('scenario_cost','investment','decision_cost','savings','reference_cost')


def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        return None
    try:return float(value) if isfinite(value) else None
    except (OverflowError,ValueError):return None


def cost(result):
    if not result or result.get('feasible') is False:return None
    return number((result.get('precise') or {}).get('total_cost',result.get('total_cost')))


def snapshot(analysis,selected):
    selected=selected or {};reference=analysis['incident'];result=selected.get('result')
    def chosen(key):
        if not result or result.get('feasible') is False:return None
        try:return metric(selected,key)
        except (ValueError,TypeError):return None
    values={'schema':'1.0','currency':'BRL','scenario_cost':cost(result),
            'investment':chosen('investment'),'decision_cost':chosen('decision_cost'),
            'savings':chosen('savings'),'reference_cost':cost(reference),
            'reference_signature':config_signature(reference['config']),
            'basis':'Custos do modelo sintético; não equivalem a economia de caixa comprovada.'}
    return normalize({'economics':values})


def normalize(document):
    """Read-only view. Absence remains unknown, even for 'Não intervir'."""
    saved=document.get('economics')
    if isinstance(saved,dict) and saved.get('schema')=='1.0':
        values={k:number(saved.get(k)) for k in FIELDS}
        source=saved.get('source','registered');reference=saved.get('reference_signature')
    else:
        metrics=document.get('metrics') or {}
        values={k:None for k in FIELDS}
        values['scenario_cost']=cost(metrics.get('response') or metrics.get('incident'))
        values['reference_cost']=cost(metrics.get('incident'))
        source='legacy';reference=None
    missing=[k for k,v in values.items() if v is None]
    return {'schema':'1.0','currency':'BRL',**values,'reference_signature':reference,
            'status':'partial' if missing else 'complete','missing':missing,'source':source,
            'basis':'Custos do modelo sintético; não equivalem a economia de caixa comprovada.'}


def compare(first,second):
    a,b=normalize(first),normalize(second)
    return {'first':a,'second':b,'delta':{k:b[k]-a[k] if a[k] is not None and b[k] is not None else None for k in FIELDS},
            'same_reference':bool(a['reference_signature'] and a['reference_signature']==b['reference_signature'])}
