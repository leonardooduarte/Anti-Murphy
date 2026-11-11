# Anti-Murphy — três experimentos de validação interna

**Natureza:** experimentos reexecutados no motor de eventos discretos da edição de banca. **Dados sintéticos; não há calibração industrial.** As avaliações são internas, não validação científica externa.

## A. Efeito da falha de CNC e intervenção

**Entradas:** cinco ordens, 96 unidades; parada na CNC às 4 h durante 8 h; referência nominal, incidente sem resposta, resposta selecionada `Manutenção expressa · CNC` com investimento de R$ 1.800,00.

| Cenário | Makespan (h) | Throughput (un/h) | SLA | Atrasos | Custo de operação e multas |
|---|---:|---:|---:|---:|---:|
| Plano | 16,90 | 5,68 | 100,00% | 0 | R$ 8.076,37 |
| Falha sem resposta | 24,58 | 3,91 | 40,00% | 3 | R$ 16.216,67 |
| Falha com intervenção | 21,58 | 4,45 | 100,00% | 0 | R$ 10.313,00 |

- **Custo da decisão**, incluindo investimento: R$ 12.113,00.
- **Diferença estimada** frente à falha sem resposta: R$ 4.103,68.
- **Conferências independentes:** recontagem de pedidos atrasados comparando conclusão e prazo; SLA a partir de cinco pedidos; somatório de multas; cronologia das operações e subintervalos de processamento; throughput por 96 unidades dividido pelo makespan; identidade dos custos com tolerância de R$ 0,02 devido ao arredondamento por componente.
- **Limite:** custo por hora do modelo não equivale a saída real de caixa ou viabilidade de reparo acelerado.

## B. Sensibilidade ao número de máquinas CNC

**Entradas:** operação nominal; incremento isolado de máquinas CNC em 0, 1, 2 e 3. Regras e pedidos permanecem constantes.

| Máquinas adicionais | Throughput (un/h) | SLA | Custo por unidade (R$) | Ganho marginal (un/h) |
|---:|---:|---:|---:|---:|
| 0 | 5,68 | 100,00% | 84,13 | 0,00 |
| 1 | 5,68 | 100,00% | 96,10 | 0,00 |
| 2 | 5,68 | 100,00% | 108,07 | 0,00 |
| 3 | 5,68 | 100,00% | 120,03 | 0,00 |

**Interpretação:** adicionar máquinas CNC, isoladamente, não melhora o throughput **nesta configuração sintética**. Não é demonstração de que CNC nunca seja gargalo ou de que operadores sejam a única restrição. A análise de gargalo do programa é heurística, não diagnóstico TOC comprovado.

## C. Decisão multicritério (makespan, SLA e custo)

**Alternativas do mesmo incidente:**

| Resposta enumerada | Makespan (h) | SLA | Custo da decisão |
|---|---:|---:|---:|
| Manutenção expressa · CNC | 21,58 | 100,00% | R$ 12.113,00 |
| +1 operador · CNC | 19,97 | 60,00% | R$ 12.712,94 |

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
