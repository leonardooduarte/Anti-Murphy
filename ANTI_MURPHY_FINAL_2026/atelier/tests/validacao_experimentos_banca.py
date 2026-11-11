"""Reproduz três casos da banca e grava evidências em arquivos locais.
Execução: python -m atelier.tests.validacao_experimentos_banca
Executa SOMENTE o motor DES existente; sem calibração fabril.
"""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import date
import json, math
from atelier.service import Studio
from simulation.nexus import current_analysis, selected_action

OUT=Path(__file__).resolve().parents[2]/'docs'

def close(actual,expected,tol=.06):
    if not math.isfinite(float(actual)) or abs(float(actual)-float(expected))>tol:
        raise AssertionError(f'Esperado {expected}, encontrado {actual}; tolerância {tol}')

def measured_order_metrics(result):
    rows=result['orders'];units=sum(int(row['Quantidade']) for row in rows)
    lateness=sum(1 for row in rows if float(row['Conclusão (h)'])>float(row['Prazo (h)'])+.011)
    penalty=sum(float(row['Multa (R$)']) for row in rows)
    return {'orders':len(rows),'units':units,'late_orders':lateness,
            'sla_pct':round(100*(len(rows)-lateness)/len(rows),2),
            'throughput_by_total_units_over_makespan':round(units/float(result['makespan_h']),3),
            'sum_penalties':round(penalty,2)}

def validate_operation_timeline(result):
    """Independent temporal invariants on the DES-produced operation log."""
    for op in result['operations']:
        arrival,start,finish=(float(op[k]) for k in ('arrival_h','start_h','end_h'))
        assert 0 <= arrival <= start+1e-9 <= finish+1e-9,op
        segments=op.get('process_segments') or []
        last=-1.0
        for a,b in segments:
            assert start-1e-8<=a<=b+1e-9<=finish+1e-8,(op,a,b)
            assert a>=last-1e-9,(op,last,a)
            last=b
    close(max(float(o['Conclusão (h)']) for o in result['orders']),result['makespan_h'],.03)

def run():
    with TemporaryDirectory() as storage:
        studio=Studio(Path(storage));analysis=current_analysis(studio.state)
        selected=selected_action(studio.state,analysis)
        r0=analysis['normal'];r1=analysis['incident'];r2=selected['result']
        independent={}
        for key,r in [('normal',r0),('incident',r1),('response',r2)]:
            validate_operation_timeline(r)
            independent[key]=measured_order_metrics(r)
            assert independent[key]['units']==r['total_units']==96
            assert independent[key]['late_orders']==r['late_orders']
            close(independent[key]['sla_pct'],r['sla_pct'],.005)
            close(independent[key]['throughput_by_total_units_over_makespan'],r['throughput_h'],.005)
            close(independent[key]['sum_penalties'],r['penalty_total'],.02)
            close(r['operating_cost']+r['penalty_total'],r['total_cost'],.02)
        close(r1['total_cost']-(r2['total_cost']+selected['investment']),selected['savings'],.02)
        close(r2['total_cost']+selected['investment'],selected['decision_cost'],.02)
        assert r0['late_orders']==0 and r1['late_orders']>0
        assert r2['late_orders']<r1['late_orders']
        assert studio.technical_audit()['costs']['all_reconciled']
        # Experimento B: vary capacity in nominal model; unit count and dispatch remain constant.
        capacity=studio.advanced({'mode':'sensitivity','station':'CNC','resource':'maquinas'})['rows']
        assert [r['Adição'] for r in capacity]==[0,1,2,3]
        close(capacity[0]['Throughput'],r0['throughput_h'],.001)
        assert all(abs(r['Throughput']-capacity[0]['Throughput'])<=.001 for r in capacity[1:])
        assert all(r['Custo/un']>capacity[i-1]['Custo/un'] for i,r in enumerate(capacity) if i>0)
        # Experimento C: conflict between fastest scheduling and service/cost.
        alt=next(a for a in analysis['rows'] if a['action']=='+1 operador · CNC')
        assert alt['makespan_h']<selected['makespan_h'], (alt['makespan_h'],selected['makespan_h'])
        assert alt['sla_pct']<selected['sla_pct']
        assert alt['decision_cost']>selected['decision_cost']
        # Regime is deterministic and doesn't alter the active selected answer.
        after=studio.info()
        assert after['selected']==selected['signature']
        assert after['metrics']['incident']['late_orders']==r1['late_orders']
        payload={'title':'Anti-Murphy | Três ensaios reproduzíveis de engenharia',
                 'source':'Motor original: simulation/nexus.py e simulation/engine.py; dados sintéticos do projeto exemplo',
                 'scope':'Verificação interna, não homologação industrial',
                 'case_A':{'input':{'incidence':analysis.get('incident',{}).get('name'),
                                     'station':'CNC','start_h':4,'duration_h':8,'response':selected['action'],
                                     'investment_brl':selected['investment']},
                           'nominal':{k:r0[k] for k in ('makespan_h','throughput_h','sla_pct','late_orders','operating_cost','penalty_total','total_cost')},
                           'incident':{k:r1[k] for k in ('makespan_h','throughput_h','sla_pct','late_orders','operating_cost','penalty_total','total_cost')},
                           'response':{k:r2[k] for k in ('makespan_h','throughput_h','sla_pct','late_orders','operating_cost','penalty_total','total_cost')},
                           'response_decision_cost_brl':selected['decision_cost'],
                           'difference_vs_incident_brl':selected['savings'],
                           'independent_order_checks':independent},
                 'case_B':{'input':{'scenario':'nominal','station':'CNC','resource':'maquinas','additions':[0,1,2,3]},
                           'rows':capacity,'interpretation':'No modelo estudado, adicionar máquinas CNC isoladamente não altera o throughput. O custo unitário aumenta.'},
                 'case_C':{'compared':{'express_maintenance':{'action':selected['action'],'makespan_h':selected['makespan_h'],
                                       'sla_pct':selected['sla_pct'],'decision_cost_brl':selected['decision_cost']},
                                       'extra_cnc_operator':{'action':alt['action'],'makespan_h':alt['makespan_h'],
                                       'sla_pct':alt['sla_pct'],'decision_cost_brl':alt['decision_cost']}},
                           'interpretation':'Menor makespan isolado não assegura melhor SLA ou menor custo nos cenários enumerados.'},
                 'checks':['Integridade temporal de operações, segmentos e conclusão final','Quantidades por ordem e total de unidades','SLA e atrasos por comparação de conclusões e prazos',
                           'Throughput = total unidades / makespan','Soma das multas por pedido','Composição de custos ±2 centavos',
                           'Custo da decisão = cenário + investimento modelado','Economia = referência sem resposta - custo da decisão',
                           'Capacidade marginal sem ganho no cenário específico','Alternativa mais rápida com SLA e custo diferentes'],
                 'known_limits':['Tempos, demandas e falhas são sintéticos','Estudo de capacidade sem verificação de habilitações individuais ou custos completos de contratação',
                                 'Somatórios publicados são arredondados; diferenças de R$0,01 são esperadas',
                                 'Não confirma ótimo global nem economia observada em fábrica','Não usa MTBF/MTTR, refugo ou inspeção reais']}
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'RESULTADOS_TRES_EXPERIMENTOS_BANCA.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
        fmt=lambda v: f'{v:,.2f}'.replace(',','_').replace('.',',').replace('_','.')
        def row(label,r):return f"| {label} | {fmt(r['makespan_h'])} | {fmt(r['throughput_h'])} | {fmt(r['sla_pct'])}% | {r['late_orders']} | R$ {fmt(r['total_cost'])} |"
        md=f'''# Anti-Murphy — três experimentos de validação interna

**Natureza:** experimentos reexecutados no motor de eventos discretos da edição de banca. **Dados sintéticos; não há calibração industrial.** As avaliações são internas, não validação científica externa.

## A. Efeito da falha de CNC e intervenção

**Entradas:** cinco ordens, 96 unidades; parada na CNC às 4 h durante 8 h; referência nominal, incidente sem resposta, resposta selecionada `{selected['action']}` com investimento de R$ {fmt(selected['investment'])}.

| Cenário | Makespan (h) | Throughput (un/h) | SLA | Atrasos | Custo de operação e multas |
|---|---:|---:|---:|---:|---:|
{row('Plano',r0)}
{row('Falha sem resposta',r1)}
{row('Falha com intervenção',r2)}

- **Custo da decisão**, incluindo investimento: R$ {fmt(selected['decision_cost'])}.
- **Diferença estimada** frente à falha sem resposta: R$ {fmt(selected['savings'])}.
- **Conferências independentes:** recontagem de pedidos atrasados comparando conclusão e prazo; SLA a partir de cinco pedidos; somatório de multas; cronologia das operações e subintervalos de processamento; throughput por 96 unidades dividido pelo makespan; identidade dos custos com tolerância de R$ 0,02 devido ao arredondamento por componente.
- **Limite:** custo por hora do modelo não equivale a saída real de caixa ou viabilidade de reparo acelerado.

## B. Sensibilidade ao número de máquinas CNC

**Entradas:** operação nominal; incremento isolado de máquinas CNC em 0, 1, 2 e 3. Regras e pedidos permanecem constantes.

| Máquinas adicionais | Throughput (un/h) | SLA | Custo por unidade (R$) | Ganho marginal (un/h) |
|---:|---:|---:|---:|---:|
'''
        for r in capacity:md+=f"| {r['Adição']} | {fmt(r['Throughput'])} | {fmt(r['SLA'])}% | {fmt(r['Custo/un'])} | {fmt(r['Ganho marginal TP'])} |\n"
        md+='''\n**Interpretação:** adicionar máquinas CNC, isoladamente, não melhora o throughput **nesta configuração sintética**. Não é demonstração de que CNC nunca seja gargalo ou de que operadores sejam a única restrição. A análise de gargalo do programa é heurística, não diagnóstico TOC comprovado.\n\n'''
        md+=f'''## C. Decisão multicritério (makespan, SLA e custo)

**Alternativas do mesmo incidente:**

| Resposta enumerada | Makespan (h) | SLA | Custo da decisão |
|---|---:|---:|---:|
| {selected['action']} | {fmt(selected['makespan_h'])} | {fmt(selected['sla_pct'])}% | R$ {fmt(selected['decision_cost'])} |
| {alt['action']} | {fmt(alt['makespan_h'])} | {fmt(alt['sla_pct'])}% | R$ {fmt(alt['decision_cost'])} |

A intervenção com menor makespan nesta comparação não é a de melhor SLA nem a de menor custo de decisão. Os resultados dependem dos prazos, custos e restrições parametrizados. **Não se afirma ótimo global.**

## Procedimento de reprodução

1. Na pasta do aplicativo, execute `python -m atelier.tests.validacao_experimentos_banca` (Python 3.10+ compatível com o projeto).
2. O script usa uma pasta temporária para preservar os projetos e decisões do usuário.
3. Confirme a mensagem `3 EXPERIMENTOS APROVADOS` e compare este relatório com `RESULTADOS_TRES_EXPERIMENTOS_BANCA.json`.
4. Para a visualização, abra o Anti-Murphy, acesse **Modo banca** e depois **Ensaios → Capacidade** e **Ferramentas → Sensibilidade**.

## Ressalvas de método

- Valores de tempos e custos não foram calibrados por coleta industrial.
- Operadores individualmente habilitados, indisponibilidade de manutenção, buffers finitos, refugo e retrabalho não são integralmente representados.
- O centavo de diferença possível entre custo operacional, multas e custo publicado deve-se aos arredondamentos independentes da saída do motor. Isso não é evidência de validação externa.
- Os experimentos verificam coerência e consistência interna de casos específicos, não a correção universal da simulação.
'''
        (OUT/'EXPERIMENTOS_VALIDACAO_ENGENHARIA.md').write_text(md,encoding='utf8')
        print('3 EXPERIMENTOS APROVADOS')
        print('A:',r0['sla_pct'],r1['sla_pct'],r2['sla_pct'],'custos',r1['total_cost'],selected['decision_cost'],selected['savings'])
        print('B:',[(row['Adição'],row['Throughput'],row['Custo/un']) for row in capacity])
        print('C:',selected['action'],selected['makespan_h'],alt['action'],alt['makespan_h'])
        return payload

if __name__=='__main__':run()
