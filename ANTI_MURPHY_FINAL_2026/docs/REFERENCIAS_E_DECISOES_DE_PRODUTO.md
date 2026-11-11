# Referências, observação e direção de produto

Pesquisa em fontes primárias e inspeção das telas em 20/10/2026. O vídeo `6.mp4` foi a evidência da experiência anterior. As imagens dos fornecedores foram consultadas para análise interna e não incorporadas à interface ou ao pacote.

## O problema observado no vídeo

Por volta de 01:05, a produção aparece reduzida no centro, com ações e resultados concentrados no painel lateral. Em 01:47, a conversa acumula texto sobre a operação e a resposta. Em 02:26, o modo de apresentação conserva a estrutura de operação. A conclusão da revisão foi dar hierarquia ao evento, à consequência nos pedidos e à ação que o usuário pode ensaiar.

## Telas e interações consultadas

| Fonte primária | Tela efetivamente inspecionada | Observação | Aplicação |
| --- | --- | --- | --- |
| [Simul8 — Experiment Builder](https://www.simul8.com/support/help/doku.php?id=features:Experiment_Builder) | Results Manager, lista de experimentos e matriz de resultados | Referência explícita, alternativas organizadas e comparação por indicador. | Matriz completa com investimento, custo total, economia e restrições; a seleção em exame é distinta da sugestão. |
| [AnyLogic — experimento de otimização, tutorial de 23/11/2023](https://www.anylogic.com/blog/anylogic-cloud-2-4-0-optimization-experiment-at-scale/) | Activity Based Cost Analysis: animação associada a custos e operações; resultados de replicações | A solução calculada pode ser reproduzida visualmente, com medidas ligadas ao processo. | Produção, curvas de conclusão e entregas usam o mesmo traço de eventos. A variação é apresentada como faixa observada. |
| [Siemens — Opcenter X 2604, 21/05/2026](https://blogs.sw.siemens.com/opcenter/whats-new-in-opcenter-x-2604/) | Sequência Before change / Drag / Drop no gráfico de Gantt | Ajustar uma decisão deve atualizar consequências e respeitar restrições. | A prioridade, o orçamento e o momento da resposta disparam novos cálculos; a entrega de cada pedido permanece ligada à alternativa. |

Imagens primárias consultadas: [Simul8 — experimentos](https://www.simul8.com/support/help/lib/plugins/ckgedit/fckeditor/userfiles/image/features/eb1.png), [Simul8 — resultados](https://www.simul8.com/support/help/lib/plugins/ckgedit/fckeditor/userfiles/image/features/eb4.png), [AnyLogic — animação e custos](https://www.anylogic.com/upload/medialibrary/2d0/43hxg6sjvhxrui83wxngldvwpemu2fvo.png), [Siemens — alteração no Gantt](https://blogs.sw.siemens.com/wp-content/uploads/sites/3/2026/05/Picture_OC_14-1024x236.png).

As fontes demonstram soluções de interação em seus próprios produtos. A adaptação ao Anti-Murphy é uma decisão de projeto; não significa equivalência de capacidade com esses produtos.

## Alternativas de composição consideradas

1. **Console com três colunas persistentes.** Concentra muitos controles, mas reproduz o problema de uma cena pequena e texto concorrente. Foi descartado para o fluxo principal.
2. **Produção ocupando toda a tela.** Favorece a leitura da fábrica, mas exige sair da cena para escolher e justificar a resposta. Foi aproveitado parcialmente no modo de apresentação.
3. **Área clara de decisão com produção e painel contextual.** Foi escolhida. O evento e o impacto ficam no topo; a resposta examinada e a ação de ensaio ficam visíveis; pedidos, comparação e detalhes são acessados conforme a investigação.

Esta comparação foi interna. Não houve teste de preferência com usuários nem experimento A/B.

## Decisões aplicadas

- Neutro oficial como base, grafite para leitura e laranja para evento ou ação. A marca usa os SVGs originais.
- Ausência da lista lateral permanente de pedidos. A faixa inferior conserva seleção rápida; Entregas mostra prazo e conclusão.
- Equipamentos ampliados e estados textuais. Movimento deriva do processamento e para durante a indisponibilidade.
- Cabeçalho muda de impacto sem resposta para efeito previsto do ensaio, distinguindo contagens atuais de previsões finais.
- Comparação por curvas de conclusão no mesmo relógio. A referência continua nomeada e seus valores são calculados.
- Três objetivos explícitos, com regras de seleção documentadas. As restrições são verificadas por opção.
- Registro local com motivo, alternativa em exame e sugestão distinguíveis; arquivo consultável após fechar o programa.
- Apresentação com seis capítulos e composição própria, usando o experimento atual.

## O diferencial desenvolvido para este caso

O ensaio compartilha o histórico anterior à ação e permite examinar o custo de esperar, proteger um pedido e observar o efeito sobre os demais. A resposta atrasada continua visível mesmo quando passa a gerar perda. As fontes embasaram a composição e as interações; esse fluxo foi desenvolvido para os requisitos do Anti-Murphy.
