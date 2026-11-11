# Anti-Murphy — roteiro de demonstração para avaliação de Engenharia de Produção

> **Proposta de valor:** ambiente local de simulação de eventos discretos e apoio à avaliação de respostas a interrupções produtivas. O usuário define um modelo de produção, executa uma parada simulada, compara alternativas, examina os impactos sobre os pedidos e registra uma justificativa rastreável. Não é um MES real, nem controla máquinas.

## Antes da apresentação

1. Faça uma cópia de segurança da versão que está funcionando. Extraia este ZIP em uma **pasta nova**.
2. No Windows, execute apenas `INICIAR_ANTI_MURPHY.bat`. Necessário Python 3.10 ou superior; o aplicativo principal não necessita npm ou Streamlit.
3. Confirme que abrem **Início**, **Painéis → Auditoria técnica**, **Análise**, **Decisões** e **Registros**.
4. Use o projeto sintético padrão para demonstrar, sem reivindicar calibração com dados reais.
5. Verifique a velocidade **1×** e a caixa **Pausar nos eventos** marcadas. Não confunda velocidade visual com tempo de processamento das máquinas.
6. Se houver público assistindo, use **Ampliar mapa** para a fábrica e **Retornar** para os dashboards; o fullscreen é somente visual.
7. Faça um ensaio completo de registro de decisão e confira se o histórico mostra o experimento, a justificativa e as verificações pendentes.

## Demonstração principal — aproximadamente 5 minutos

| Minuto | Interação | O que explicar |
|---|---|---|
| 0:00–0:40 | Início → fábrica → cenário **Sem intervenção**. | Modelo de cinco postos, carteira de pedidos, sequências de operações e programação por eventos discretos. |
| 0:40–1:20 | Escolha **8×** para chegar à parada. O replay interrompe em **04:00 h**; retorne a **1×**. | A simulação tem um relógio próprio: 1× = **10 min simulados por segundo real**. A parada é um evento do modelo, não uma animação arbitrária. |
| 1:20–2:05 | Alterne para **Comparar**. Inspecione CNC, fila e progresso dos pedidos. | Mesmo instante simulado para A/B; os KPIs vêm dos dois cenários calculados. A animação não cria resultados e não simula deslocamento físico de peças. |
| 2:05–2:50 | Painéis → **Auditoria técnica**. Mostre folgas, gargalo, maior espera e verificação dos custos. | Pontuação de gargalo e maior espera **não são sinônimos**; o programa também revela o que não foi modelado, em vez de preencher com dados fictícios. |
| 2:50–3:35 | Painéis → **Desempenho** / Análise. Examine a composição de custos. | Operação + multas formam o custo do cenário. Com investimento da intervenção, formam o **custo da decisão**; a diferença não é caixa economizado comprovadamente. |
| 3:35–4:20 | Decisões → Murphy local. Pergunte sobre gargalos/pedidos. | Resposta determinística baseada no experimento, sem API externa nem decisões aplicadas automaticamente. |
| 4:20–5:00 | Registre justificativa, reconheça limites e abra Registros/Relatório técnico. | Rastreabilidade: registro local, hash do modelo, responsável, riscos e condições não homologadas. |

## Perguntas que provavelmente serão feitas por especialistas

### PCP

**Qual o método de simulação?** Motor discreto em Python com fila de eventos priorizada (`heapq`). Operações são registradas em seus instantes de entrada, início e término. A interface visual apenas reproduz os estados e interpola a apresentação temporal.

**Quais regras de despacho existem?** O modelo permite EDD, FIFO e SPT; a escolha influencia a prioridade da fila. Roteiros e recursos são configuráveis.

**Como o sistema define o gargalo?** Atualmente por um **índice heurístico**: utilização de máquina + mínimo entre 50 e metade da espera média em minutos + 2 vezes a fila máxima. Não é demonstração de restrição estrutural segundo a Teoria das Restrições. A confirmação exige experimento marginal de capacidade e comparação do throughput.

**Qual a diferença entre SLA e folga?** O indicador de atendimento considera o percentual de **pedidos** concluídos dentro do prazo, não a proporção de unidades. A folga é calculada por pedido como `prazo − conclusão prevista`. Um pedido em dia com folga mínima continua exposto a variações.

**A liberação de materiais é realista?** `release_h` pode escalonar a liberação; pedidos sem tempo de liberação explícito entram em `t=0`. Os buffers finitos e o WIP máximo ainda não estão integralmente impostos.

### Administração da manutenção

**A manutenção expressa é executável?** É uma hipótese parametrizada de redução do **tempo de reparo restante**. A disponibilidade real de técnicos, peças, ferramental, deslocamento e segurança não está integralmente modelada. O sistema não autoriza intervenção em máquinas.

**Onde estão MTBF e MTTR?** Não há histórico industrial suficiente para calcular estimativas estatísticas. O tempo de parada programado em um cenário não deve ser apresentado como MTTR observado. O painel de auditoria deixa esses indicadores indisponíveis.

### Controle de qualidade

**O sistema calcula OEE, FPY, perdas de qualidade ou taxa de defeitos?** Não de forma válida. O modelo ainda não incorpora refugo, retrabalho e inspeção de maneira suficientemente completa. Esses indicadores **não são inventados**. Uma extensão realista exigiria registrar defeitos por operação, peças retrabalhadas, tempos e custos associados.

### Custos e finanças

**O que entra no custo do cenário?** Custos de máquinas e operadores assumidos por capacidade contratada ao longo do horizonte mais multas previstas por atraso. Não é custo de atividade contabilizado apenas durante o processamento.

**Como aparece a economia?** `custo sem resposta − (custo do cenário com intervenção + investimento modelado)`. Pode ser chamada de **diferença econômica estimada no modelo**, mas não de economia financeira real verificada. Custos fixos, evitáveis e investimentos não cadastrados precisam de verificação.

### Software e pesquisa operacional

**O simulador é reproduzível?** As mesmas condições, regras e sementes geram o mesmo experimento determinístico. Há registros persistentes e testes automatizados. O arquivo contém hash do modelo e identificador do experimento.

**A comparação A/B é simultânea de verdade?** Os cenários são simulados separadamente a partir de condições compatíveis e reproduzidos no **mesmo tempo simulado**. O motor de eventos discretos realiza o cálculo antes da apresentação; não é um comando em fábrica real.

**O Monte Carlo valida risco industrial?** Não sem calibração. As 12 execuções demonstrativas usam tempos de processamento variados por distribuição triangular do motor, tipicamente `0,96` a `1,05` vezes o tempo-base. Não representa falhas aleatórias históricas, nem fornece intervalo de confiança industrial.

**Por que o replay agora é mais lento?** Antes, 1× tentava comprimir toda a simulação em 35 segundos; agora 1× equivale a 10 minutos simulados/segundo real, com 0,5×, 2×, 4× e 8×. É uma escolha de **apresentação**, independente das equações de produção. A pausa opcional nos eventos garante tempo para interpretar a ocorrência.

**E a viabilidade de realocar operadores?** A solução pode satisfazer os parâmetros codificados, porém habilidades individuais, setups dependentes de sequência, buffers e disponibilidade física não estão totalmente validados. O aplicativo diferencia **atende ao modelo** de **homologado industrialmente**, e apenas o primeiro pode ser demonstrado.

## Critério de aceitação final

A versão apresentada deve permitir executar, sem sair do aplicativo: **abrir projeto → simular → inspecionar falha → comparar A/B → conferir folgas e custos → consultar Murphy → registrar justificativa → recuperar registro → imprimir relatório**.

Não afirme 60 FPS, homologação industrial, otimização global, MTBF/MTTR real ou taxa de defeitos sem testes e dados que os comprovem.
