# Anti-Murphy — complemento AM-04: fronteira custo/SLA

Versão: AM04-FRONTEIRA-2026.1, sobre AM10-2026.1.
Base: `97683444f7160f35d86f0bb7b8c96baddb07412a`.
Branch: `correcao-am04-fronteira`.

## Problema reproduzido antes da alteração

A correção principal de elegibilidade do AM-04 já estava presente: participar
da fronteira exige `feasible`, `within_budget` e `meets_sla` verdadeiros.
Esta etapa trata somente a inconsistência residual da fronteira visual.

As funções originais da base AM10 foram executadas em Node, sem edição,
com alternativas controladas. `before.log` registra a reprodução.

| Alternativas elegíveis | Análise antes | Dashboard antes | Depois, em ambas as telas |
| --- | ---: | ---: | ---: |
| A: R$100/SLA80%; B: R$100/SLA100%, nesta ordem | 2 | 1 | 1, somente B |
| Mesmos valores, ordem inversa | 1 | 1 | 1, somente B |
| A e B: R$100/SLA100% | 1 | 2 | 2 alternativas equivalentes |
| A: R$100/SLA80%; B: R$101/SLA80,00005% | 1 | 2 | 2, pois existe compromisso entre custo e SLA |

Com custos empatados, o algoritmo sequencial da Análise aceitava primeiro o
ponto de menor SLA e não o retirava quando encontrava o superior. Também
descartava equivalentes e diferenças positivas de SLA de até 0,0001 ponto.
A lista de entrada podia, portanto, alterar a interpretação apresentada.

## Correção e referência independente

`atelier/web/app.js` ganhou `costSlaFrontier`, usada por `renderFrontier`
e `dashTradeoffPlot`. A definição aplicada é: B domina A se tem custo menor
ou igual, SLA maior ou igual e melhora estritamente pelo menos uma métrica.
Somente alternativas elegíveis e com métricas numéricas finitas participam.
Comparações usam a precisão recebida, sem arredondamento ou tolerância nova.
As convenções existentes de conversão numérica dos pontos foram preservadas.

Empates exatos nas duas métricas permanecem como alternativas equivalentes.
O conjunto é ordenado por custo, SLA e assinatura, sem alterar a lista
original. Pontos coincidentes podem se sobrepor no gráfico; a tabela de
alternativas continua permitindo consultar e selecionar cada resposta.

Uma definição matemática independente em Python verifica a implementação
JavaScript real, incluindo 120 conjuntos determinísticos e as 24 permutações
de um conjunto com empate. Nenhuma fórmula do motor foi alterada.

Os textos das duas telas declaram as duas métricas e os limites do conjunto
enumerado. A revisão de decisões em `atelier/decision_quality.py` continua
usando custo, makespan e SLA, com suas tolerâncias existentes. Um teste
demonstra que uma alternativa dominada no gráfico bidimensional pode seguir
não dominada na revisão tridimensional se terminar antes.

## Arquivos e funções

- Produção: somente `atelier/web/app.js`, com a função nova `costSlaFrontier`
  e alterações em `renderFrontier` e `dashTradeoffPlot`.
- Testes novos: `tests/test_am04_frontier.py` e
  `atelier/tests/browser_am04.py`.
- Documentação, continuidade, plano de finalização, versão e evidências novas.

Não foram alterados o DES, fórmulas econômicas, persistência, projetos locais,
registros arquivados, identificação de resultados AM-05, precisão AM-11,
economia AM-08, estatísticas AM-09 ou a enumeração AM-10. CSS, marcas,
abertura e controles de navegação foram preservados.

## Resultados de validação

- Regressão completa: **473 aprovados, cinco falhas preexistentes e dez
  subtestes aprovados**, sem exclusão de testes. São 16 casos novos do AM-04.
- Testes direcionados de fronteira e revisão de decisão: **21 aprovados**.
- Três experimentos oficiais aprovados, com resultados iguais aos da AM10.
- Navegador em 1280×720, 1366×768 e 1920×1080: cinco casos controlados por
  resolução, consistência das telas, pontos preservados, seleção por teclado
  com resposta do serviço real e ausência de erros JavaScript nos fluxos.
- Testes anteriores de gráficos, legendas, ampliação e exportações passaram
  nas três resoluções, sem alterar suas asserções.
- Fluxo HTTP real do Modo Banca, justificativa, registro e relatório passou
  nas três resoluções.

Os casos controlados interceptam somente respostas de leitura para produzir
empates específicos no navegador. Não gravam métricas artificiais no projeto.
A seleção por teclado retorna ao serviço real em armazenamento temporário.
O fluxo do Modo Banca e os experimentos oficiais usam o motor real, sem esses
dados controlados. Screenshots dos empates são evidências de interface,
não resultados industriais.

As cinco falhas preservadas são:

1. `tests/test_operation_ui.py::test_evidence_exports_the_current_timed_experiment`;
2. `tests/test_restauracao_acesso.py::test_inicio_prioriza_o_workspace_original_e_nao_o_mapa`;
3. `tests/test_restauracao_acesso.py::test_modulos_importantes_tem_atendimento_direto`;
4. `tests/test_v31_editorial.py::test_only_one_root_launcher`;
5. `tests/test_v31_editorial.py::test_preview_has_no_external_script_dependency`.

Nenhum desses testes foi alterado ou removido nesta etapa. Não se declara
suíte totalmente verde. O tratamento desses contratos antigos permanece
pendente em AM-19, com investigação funcional antes de mudar qualquer teste.

## Indicadores oficiais antes/depois

| Indicador | AM10 | Esta entrega |
| --- | ---: | ---: |
| SLA nominal / incidente / resposta | 100% / 40% / 100% | iguais |
| Custo do incidente | R$16.216,67 | R$16.216,67 |
| Investimento da manutenção expressa | R$1.800,00 | R$1.800,00 |
| Custo total da decisão | R$12.113,00 | R$12.113,00 |
| Economia líquida | R$4.103,68 | R$4.103,68 |
| Makespan manutenção expressa | 21,57530617980079 h | igual |
| Makespan +1 operador, resposta temporal | 19,973006391870044 h | igual |

## Reprodução e limites

Na pasta do aplicativo, com dependências de desenvolvimento disponíveis:

```sh
python -m pytest tests contract_tests atelier/tests -q
python -m pytest tests/test_am04_frontier.py atelier/tests/test_decision_quality.py -q
python -m atelier.tests.browser_am04
python -m atelier.tests.browser_acabamento_final
python -m atelier.tests.validacao_experimentos_banca
```

Node é necessário aos testes do JavaScript; não foi acrescentado como
dependência de execução do aplicativo. Os testes de navegador usam
Playwright e Chromium (`/usr/bin/chromium` neste ambiente Linux).
O script adicional de aceitação HTTP está nas evidências, junto aos logs.
Execute testes em cópia para preservar seus projetos de trabalho.

O ZIP completo e o patch são extraídos e comparados por SHA-256. O patch
verifica a base AM10 exata e cria uma pasta nova. A verificação detalhada da
entrega e os testes do pacote extraído constam em `VERIFICACAO_AM04_FRONTEIRA.json`
e nos logs ao lado do ZIP. Os arquivos publicados são recuperados do GitHub
e comparados aos locais antes de informar a conclusão da entrega.

Windows, instalação pelo BAT e projetor não foram homologados nativamente.
Permanecem limitações do modelo sintético e os achados listados em
`STATUS_E_PLANO_FINALIZACAO_2026.md`. Esta etapa não corrige outros achados
nem representa uma nova auditoria integral.
