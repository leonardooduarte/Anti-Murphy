"""Read-only experiment collection: isolate invalid documents, never repair on read."""
import json
import re


METRICS=('late_orders','sla_pct','makespan_h','total_cost','operating_cost',
         'penalty_total','throughput_h','planned_units','total_units')


def _validate(document, path):
    for key in ('id','name','project_id','model_hash'):
        if not isinstance(document.get(key),str) or not document[key].strip():
            raise ValueError(f'Campo {key} ausente ou inválido.')
    if not re.fullmatch(r'[A-Za-z0-9_-]+',document['id']) or document['id']!=path.stem:
        raise ValueError('Identificador incompatível com o nome do arquivo.')
    if document.get('created_at') is not None and not isinstance(document['created_at'],str):
        raise ValueError('Data do experimento em formato inválido.')
    metrics=document.get('metrics')
    if not isinstance(metrics,dict):raise ValueError('Métricas em formato inválido.')
    if not any(isinstance(metrics.get(k),dict) for k in ('incident','response')):
        raise ValueError('Experimento sem métricas de cenário disponíveis.')
    for key in ('incident','response'):
        result=metrics.get(key)
        if result is None:continue
        if not isinstance(result,dict):raise ValueError('Cenário em formato inválido.')
        precise=result.get('precise')
        if precise is not None and not isinstance(precise,dict):
            raise ValueError('Métricas precisas em formato inválido.')
        for values in (result,precise or {}):
            for field in METRICS:
                value=values.get(field)
                if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float))):
                    raise ValueError(f'Métrica {field} em formato inválido.')
    if document.get('economics') is not None and not isinstance(document['economics'],dict):
        raise ValueError('Componentes econômicos em formato inválido.')
    # The API serializes the original snapshot as well as the displayed metrics.
    # Validate all numbers, including optional/unknown nested fields.
    try:json.dumps(document,allow_nan=False)
    except (ValueError,OverflowError) as exc:
        raise ValueError('Documento contém número não finito ou não representável.') from exc


def read_library(directory, project_id):
    """Return validated current-project documents and per-file diagnostics.

    An unreadable/malformed file of unknown origin is reported for the shared
    collection. Well-identified documents of other projects are not presented.
    Enumeration failures propagate: an unreadable collection is never empty
    merely because access failed.
    """
    documents={};issues=[]
    for path in sorted(directory.iterdir()):
        if path.suffix.lower()!='.json':continue
        try:
            try:document=json.loads(path.read_text('utf-8'))
            except (json.JSONDecodeError,UnicodeError) as exc:
                raise ValueError('JSON inválido ou codificação diferente de UTF-8.') from exc
            if not isinstance(document,dict):raise ValueError('Documento deve ser um objeto JSON.')
            origin=document.get('project_id')
            if isinstance(origin,str) and origin and origin!=project_id:continue
            _validate(document,path)
            documents[document['id']]=document
        except OSError:
            issues.append({'filename':path.name,'reason':'Não foi possível ler o arquivo.'})
        except (ValueError,TypeError,OverflowError,RecursionError) as exc:
            reason=str(exc) if isinstance(exc,ValueError) else 'Estrutura do documento inválida ou excessivamente aninhada.'
            issues.append({'filename':path.name,'reason':reason})
    return documents,issues
