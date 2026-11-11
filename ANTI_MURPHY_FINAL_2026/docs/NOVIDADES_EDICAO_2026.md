# Alterações implementadas nesta edição

| Capacidade | O que o usuário faz | Como foi testado |
|---|---|---|
| Projetos independentes | Criar, duplicar, renomear e reabrir um modelo sem sobrescrever o anterior | Persistência em disco e teste Chromium |
| Arquivo de experimentos | Salvar o estado de uma simulação e confrontar resultados anteriores | Testes de isolamento por projeto e comparação no navegador |
| Advertência de comparabilidade | Identificar que dois experimentos utilizaram modelos diferentes | Hash do modelo e testes de regressão |
| Programação por posto | Consultar calendário de operações por recurso, pausas e paradas | 402 operações mostradas a partir do DES em QA; clique em barra seleciona objeto |
| Custo × cumprimento de prazo | Visualizar alternativas calculadas e selecionar uma intervenção | Navegação e análise de dados em Chromium |
| Inspeção por pedido | Selecionar ordem, visualizar prazo, conclusão, atraso e trecho de roteiro da simulação | Verificação em Chromium com ordem OP-102 |
| Marca e movimento | Abertura animada da logo original, controles de replay e movimento condicionado ao processamento | Teste de navegação e JavaScript, preferência de movimento reduzido |
| Preservação de capacidades | Manter simulação, múltiplas respostas, análises operacionais e código histórico | Testes selecionados do motor, smoke test via HTTP, inventário funcional |

**Não foram implementados nesta edição:** migração integral das telas históricas, IA generativa offline, restrições físicas completas (skills individuais, buffers finitos, setups sequenciais), executável Windows nativo e homologação industrial.

## Decisões de design

- Interações contextualizadas; sem títulos de marketing, sem chat ou KPIs artificialmente inventados.
- HTML/CSS/JS compilação-zero para o usuário, servido localmente por Python puro.
- Cores da marca oficial: `#1D292D`, `#FF681B`, `#F7F7F3`.
- O motor de eventos discretos `heapq` continua intacto. Animações do browser nunca ajustam os resultados do simulador.
- O impacto financeiro real de uma intervenção depende das hipóteses, custos e restrições ainda não verificadas no mundo físico.
