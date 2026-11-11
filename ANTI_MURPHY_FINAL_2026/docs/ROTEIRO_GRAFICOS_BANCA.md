# Demonstração das visualizações para professores de PCP e Pesquisa Operacional

Roteiro de **2 a 3 minutos** para usar durante a apresentação, após demonstrar a simulação.

**1. Ensaios → Sensibilidade da parada.** Execute e troque os botões de término, SLA e custos. Explique: "Estamos variando uma única condição mantendo as demais entradas. Cada ponto provém de uma execução do motor."

**2. Ferramentas → Limite de demanda.** Defina o SLA mínimo, execute e selecione "Pedidos no prazo". Mostre a linha laranja da meta e o primeiro multiplicador abaixo dela. Explique que o limite depende do modelo e das hipóteses sintéticas.

**3. Ferramentas → Sensibilidade de capacidade.** Selecione CNC, operadores ou máquinas e execute. Abra "Ganho marginal" para evidenciar quando adicionar recurso deixa de melhorar o throughput.

**4. Ensaios → Teste pareado.** Mostre o gráfico de economia líquida com referência em zero. Um resultado negativo indica prejuízo; o programa distingue esse sinal sem desenhar uma falsa barra de ganho.

**5. Painéis → Robustez.** Execute as 12 sementes do Monte Carlo, examine individualmente as observações e alterne término, SLA, custo/unidade e throughput. Esclareça que não é previsão estatística calibrada em fábrica real.

**6. Exportação e rastreabilidade.** Selecione uma observação, abra a tabela e use **Dados CSV** ou **Figura SVG**. O objetivo é permitir que o professor confronte o gráfico com os dados exatos do simulador.

### Perguntas prováveis

**Por que não usar o mesmo tipo de gráfico em todos os ensaios?** Porque duração, capacidade, incerteza e ganho econômico possuem estrutura e interpretação diferentes. Uma barra absoluta ocultava o sinal da economia.

**A linha de demanda interpola o SLA entre os pontos?** Não. Somente os valores de demanda efetivamente simulados são resultados; a linha é uma conexão visual.

**O cálculo do SLA foi transferido para o frontend?** Não. O motor Python produz todos os indicadores; o navegador os apresenta e permite selecionar métricas.

**A faixa P10/P90 ou Monte Carlo garante entrega?** Não. Sem calibração com dados empíricos, é apenas uma descrição de sementes sintéticas.

**Vocês comprovaram o ótimo de custo/capacidade?** Não. São alternativas enumeradas e restrições modeladas; não alegamos ótimo global nem viabilidade física completa.
