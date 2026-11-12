"""Deterministic, read-only explanations derived from one evaluated DES experiment.

Never turns a projected response into a physically validated recommendation.
"""
from __future__ import annotations
import re
import unicodedata


def norm(value: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value).lower())
                   if not unicodedata.combining(c))


def money(value) -> str:
    if value is None: return 'não calculado'
    return 'R$ ' + f'{float(value):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def fmt(value, suffix='') -> str:
    if value is None: return 'não calculado'
    return f'{float(value):.2f}'.replace('.', ',') + suffix


def explain(question: str, analysis: dict | None, selected: dict | None, order_ids) -> dict | None:
    """Return a grounded explanation for recognized intents; None defers to old assistant."""
    if not analysis: return None
    q=norm(question)
    incident=analysis.get('incident') or {}
    impacts=(selected or {}).get('order_impacts') or []
    matches=[x for x in order_ids if re.search(r'(?<![\w./-])'+re.escape(norm(x))+r'(?![\w-]|[./][\w-])',q)]
    if len(matches)>1:
        return {'label':'MURPHY · RASTREIO DO PEDIDO','text':'Há mais de um identificador possível: '+', '.join(sorted(matches))+'. Informe um único pedido completo para consultar seus tempos sem confundir as origens.'}
    wanted=matches[0] if matches else None
    unknown=re.search(r'\bop-?\d+[a-z0-9-]*\b',q)
    if unknown and not wanted and any(k in q for k in ('pedido','op-','atras','prazo')):
        return {'label':'MURPHY · RASTREIO DO PEDIDO', 'text':f'O pedido {unknown.group(0).upper()} não existe no modelo atual. Confira o identificador em Modelo → Ordens de produção ou selecione um pedido na simulação.'}
    # Distinguish the bottleneck identified by the simulator from the station
    # with the longest measured waiting time. Neither should be guessed from UI.
    bottleneck_intent=any(k in q for k in ('gargal','maior espera','fila mais longa','posto critico'))
    risk_intent=any(k in q for k in ('risco','atrasad','atraso','prazo','pedidos afetados'))
    if bottleneck_intent or (risk_intent and not wanted):
        station_rows=incident.get('stations') or []
        bottleneck=incident.get('bottleneck')
        wait_rows=[r for r in station_rows if r.get('Espera média (min)') is not None]
        longest=max(wait_rows,key=lambda r:float(r['Espera média (min)'])) if wait_rows else None
        # Exact order rows from the incident baseline, not the selected action.
        late=[r for r in (incident.get('orders') or []) if float(r.get('Atraso (h)') or 0)>0]
        late.sort(key=lambda r:(-float(r.get('Atraso (h)') or 0),str(r.get('OP'))))
        pieces=[]
        if bottleneck_intent:
            if bottleneck:
                pieces.append(f'Gargalo identificado pelo motor no cenário de parada: {bottleneck}.')
            else:
                pieces.append('O motor não identificou um gargalo único para o cenário de parada.')
            if longest:
                pieces.append(f'Maior espera média registrada: {longest.get("Posto", "—")} '
                    f'({fmt(longest.get("Espera média (min)"), " min")}); '
                    f'fila máxima nesse posto: {int(longest.get("Fila máx.") or 0)} unidades.')
            pieces.append('O posto com maior espera média não precisa coincidir com o gargalo global. '
                          'A parada, as filas e os recursos do modelo influenciam esses indicadores.')
        if risk_intent:
            if late:
                pieces.append(f'Pedidos com atraso previsto sem intervenção ({len(late)}): '+
                  '; '.join(f'{r.get("OP")}: {fmt(r.get("Atraso (h)"), " h")}' for r in late)+'.')
            else:
                pieces.append('Nenhum pedido apresenta atraso previsto no cenário de parada sem resposta.')
            if selected and selected.get('order_impacts'):
                recovered=[r['id'] for r in selected['order_impacts'] if r.get('late_before') and not r.get('late_after')]
                if recovered:
                    pieces.append('A intervenção selecionada recupera o prazo de '+', '.join(recovered)+
                     ' nas projeções do modelo; isso não comprova execução física.')
        # A station mentioned in the question is an inspection focus, not proof it is the bottleneck.
        mentions=[r for r in station_rows if norm(str(r.get('Posto',''))) in q]
        if mentions:
            focus=mentions[0]
            pieces.append(f'Posto mencionado para inspeção: {focus.get("Posto")}; '
              f'espera média {fmt(focus.get("Espera média (min)"), " min")}; '
              f'fila máxima {int(focus.get("Fila máx.") or 0)} unidades.')
        pieces.append('Dados do experimento ativo. Para investigar o encadeamento das operações, '
          'selecione o pedido na fábrica e use o histórico temporal. '
          'Skills individuais, setups e buffers finitos ainda exigem validação.')
        return {'label':'MURPHY · GARGALOS E PEDIDOS' if bottleneck_intent and risk_intent else
                 ('MURPHY · GARGALOS' if bottleneck_intent else 'MURPHY · PEDIDOS EM RISCO'),
                'text':'\n'.join(pieces)}
    if any(k in q for k in ('aumentar capacidade','mais operadores','mais maquinas',
                         'adicionar operador','capacidade da cnc','capacidade do posto')):
        return {'label':'MURPHY · TESTE DE CAPACIDADE', 'text':
          'Não alterei o modelo nem calculei um cenário novo a partir desta pergunta. '
          'Para avaliar o efeito, abra Laboratório → Otimização de capacidade ou '
          'Análises avançadas → Sensibilidade de recursos; informe a meta e execute o ensaio. '
          'Depois compare custo, atendimento aos prazos e disponibilidade real de operadores. '
          'As restrições físicas incompletas impedem garantir a execução da resposta.'}
    if wanted and any(k in q for k in ('atras','pedido','op-','porque','por que','quando','prazo')):
        row=next((x for x in impacts if x.get('id')==wanted),None)
        if not row:
            return {'label':'MURPHY · RASTREIO DO PEDIDO', 'text':f'O pedido {wanted} não possui comparação individual no experimento selecionado. Abra Simulação → pedido para inspecionar suas operações e tempos registrados.'}
        due=float(row['due_h']);before=row.get('before_h');after=row.get('after_h')
        bdelay=max(0,float(before)-due) if before is not None else None
        adelay=max(0,float(after)-due) if after is not None else None
        text=(f'Pedido {wanted} · prazo {fmt(due," h")}.\n'
              f'Sem intervenção: conclusão {fmt(before," h")}; atraso {fmt(bdelay," h")}.\n'
              f'Com a resposta examinada: conclusão {fmt(after," h")}; atraso {fmt(adelay," h")}.\n'
              'Esses valores são previsões do motor. A comparação, isoladamente, não prova qual operação causou a espera. '
              'Para investigar a sequência registrada, abra Simulação → selecione o pedido → programação por posto.')
        return {'label':'MURPHY · RASTREIO DO PEDIDO','text':text}
    if any(k in q for k in ('custo','economia','investimento','multa','penalidade','preco')):
        if not selected or not selected.get('result'):
            return {'label':'MURPHY · COMPOSIÇÃO DE CUSTOS','text':'Não há resposta calculada para decompor custos. Selecione uma alternativa simulável.'}
        result=selected['result']
        operating=result.get('operating_cost');penalty=result.get('penalty_total');investment=selected.get('investment');decision=selected.get('decision_cost')
        if operating is None or penalty is None or investment is None or decision is None:
            return {'label':'MURPHY · COMPOSIÇÃO DE CUSTOS','text':'O cenário ainda não contém todos os valores necessários para reconciliar o custo da decisão.'}
        baseline=incident.get('total_cost')
        savings=selected.get('savings')
        text=(f'Resposta: {selected.get("action","Alternativa atual")}\n'
              f'Operação: {money(operating)} + penalidades: {money(penalty)} = custo do cenário: {money(result.get("total_cost"))}.\n'
              f'Investimento modelado: {money(investment)}. Custo da decisão: {money(decision)}.\n'
              f'Referência: falha sem resposta, {money(baseline)}. Diferença líquida estimada: {money(savings)}.\n'
              'A diferença é uma projeção para as hipóteses cadastradas. Não é economia real medida nem comprovação de viabilidade industrial.')
        return {'label':'MURPHY · COMPOSIÇÃO DE CUSTOS','text':text}
    if any(k in q for k in ('viavel','viabilidade','habilita','skill','restri','buffer','setup','operador disponivel')):
        reasons=(selected or {}).get('restriction_reasons') or []
        flag='atende às regras implementadas' if selected and selected.get('feasible') else 'não atende às regras implementadas ou não foi calculada'
        return {'label':'MURPHY · LIMITES DO MODELO','text':(
            f'A alternativa examinada {flag}. Isso NÃO confirma viabilidade física.\n'
            'Habilidades individuais, capacidade finita de buffers e setups dependentes da sequência não estão integralmente verificados.\n'
            +(f'Condições registradas: {"; ".join(map(str,reasons))}.\n' if reasons else '')+
            'Antes de executar no ambiente real, verifique operadores habilitados, disponibilidade de máquinas, fluxo entre postos e custos de intervenção.')}
    if any(k in q for k in ('melhor alternativa','qual escolher','recomend','o que fazer')):
        rows=[r for r in analysis.get('rows',[]) if r.get('feasible') and r.get('decision_cost') is not None and r.get('within_budget') and r.get('meets_sla')]
        if not rows:
            return {'label':'MURPHY · ALTERNATIVAS', 'text':'Nenhuma resposta enumerada atende simultaneamente às metas e às restrições já representadas. Revise as metas ou compare cenários; não há solução industrial validada.'}
        objective=analysis.get('objective','cost')
        leader=analysis.get('leader')
        best=next((r for r in rows if leader and r.get('signature')==leader.get('signature')),None)
        criterion={'cost':'menor custo total','delivery':'entregas no prazo','critical':'pedido prioritário'}.get(objective,'critério do experimento')
        if best is None and objective!='cost':
            return {'label':'MURPHY · ALTERNATIVAS','text':f'Prioridade ativa: {criterion}. O motor não apontou uma resposta recomendada para esse objetivo. Consulte a comparação e os impactos por pedido; uma alternativa de menor custo não substitui esse critério.'}
        if best is None:
            best=min(rows,key=lambda r:(float(r['decision_cost']),-float(r.get('sla_pct',0))))
            basis='Comparação descritiva por menor custo entre alternativas elegíveis; o motor não apontou uma recomendação.'
        else:
            basis='Resposta apontada pelo motor para a prioridade ativa: '+criterion+'. '+str(analysis.get('selection_reason') or '')
        return {'label':'MURPHY · ALTERNATIVAS', 'text':(
            basis+'\n'+f'Alternativa: "{best.get("action")}" '
            f'({money(best.get("decision_cost"))}; entregas no prazo: {fmt(best.get("sla_pct"),"%")} ).\n'
            'Este é um resultado do modelo, não a melhor solução global nem autorização para executar. '
            'Confirme as limitações industriais e compare impactos por pedido antes de registrar a decisão.')}
    return None
