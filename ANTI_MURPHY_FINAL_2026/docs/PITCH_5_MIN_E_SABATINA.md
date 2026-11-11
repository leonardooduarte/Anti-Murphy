# Roteiro de cinco minutos — Anti-Murphy

**Objetivo:** demonstrar um caso de apoio à decisão com evidência e limites, não fazer um passeio por todas as telas.

## Ensaio recomendado

| Tempo aproximado | Ação no software | Fala sugerida |
|---|---|---|
| 0:00–0:40 | Logo oficial e **Modo banca → Plano** | O PCP sofre com imprevistos e precisa avaliar o efeito nos pedidos antes de escolher como agir. O Anti-Murphy foi construído como protótipo de apoio a essa análise. |
| 0:40–1:20 | **Falha** | No exemplo sintético, a CNC para às 4 h por 8 h. O simulador recalcula filas, programação, capacidade e entregas. |
| 1:20–2:00 | **Pedidos** | O SLA cai de 100% para 40%; três pedidos atrasam. Isso é uma consequência do cenário, não um evento observado em fábrica. |
| 2:00–3:00 | **Intervenção** e **Comparação** | Avaliamos respostas enumeradas. Neste caso, a manutenção expressa recupera o SLA para 100%, com custo de decisão modelado de R$ 12.113,00, incluindo R$ 1.800 de investimento. |
| 3:00–3:50 | **Evidências / Análise de impacto** | A diferença frente à falha sem resposta é de R$ 4.103,68 nas premissas do modelo. Os efeitos por pedido e a composição de custos podem ser conferidos. |
| 3:50–4:30 | **Ferramentas → Sensibilidade** ou **Painéis → Auditoria** | A sensibilidade mostra que adicionar máquinas CNC isoladamente não melhorou throughput neste cenário. O sistema também distingue criticidade heurística de prova de gargalo. |
| 4:30–5:00 | Retomar comparação / conclusão | O valor está na rastreabilidade da decisão. Reconhecemos limites: custos modelados, recursos não validados em planta e alternativas enumeradas. |

*Os tempos são um roteiro, não tempos automáticos do programa. Ensaie o fluxo no computador e projetor reais. Evite demonstrar dois módulos avançados se a navegação consumir tempo.*

## Perguntas da banca e respostas defensáveis

**Professor de PCP — Por que CORTE aparece como gargalo e CNC tem maior espera?**  
O indicador usa uma heurística combinada de utilização, fila e espera. Não comprova uma restrição estrutural. Para confirmar, testamos a produtividade sob incremento marginal de capacidade e acompanhamos prazos e custos.

**Professor de Pesquisa Operacional — Vocês resolveram um problema de otimização?**  
O motor é uma simulação de eventos discretos; calcula alternativas enumeradas para condições dadas. Não demonstramos ótimo global nem fronteira contínua ótima. Confrontamos o trade-off de makespan, SLA e custo.

**Professor de custos — R$ 4.103,68 é economia comprovada?**  
Não. É diferença econômica projetada pela função de custos do cenário. Ela depende do horizonte simulado, dos custos de capacidade e das penalidades por atraso. Uma análise de custos evitáveis seria necessária em fábrica real.

**Professor de manutenção — Como garantir manutenção expressa em três horas?**  
Não garantimos. É um efeito paramétrico hipotético sobre o restante da parada; disponibilidade de técnico, peça, deslocamento e risco de segurança não foram aferidos. A decisão exige validação operacional externa.

**Professor de qualidade — O que acontece com refugos e retrabalhos?**  
Não há parametrização suficiente para calcular taxa de refugo, FPY ou OEE real. O cenário não deve ser apresentado como modelo físico completo da fábrica.

**Professor de software — Por que não usar IA multiagente?**  
A aplicação prioriza determinismo, baixo custo operacional e rastreabilidade das premissas. Não depende de serviço de IA externo. Uma discussão multiagente poderia apoiar crítica exploratória, mas não substituiria validação do motor.

**Professor de gestão de projetos — O que é inovação de fato?**  
A combinação do fluxo incidente → consequências por pedido → comparação calculada → registro e auditoria em uma estação local, com acesso à programação e indicadores. Não reivindicamos que cada técnica isolada seja inédita.

## Risco durante a apresentação

Se um botão falhar ou a rede do projetor não estiver disponível, o software principal é local. Tenha capturas da apresentação e um resultado impresso como contingência; não simule um teste que não foi realmente executado.


Nota AM-11: diferença econômica calculada com valores não arredondados; o resultado final é arredondado para apresentação. A diferença de R$ 0,01 frente à edição AM-06 é esperada.
