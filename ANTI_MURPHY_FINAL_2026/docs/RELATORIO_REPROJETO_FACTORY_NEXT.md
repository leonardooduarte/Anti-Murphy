# Anti-Murphy · Factory Command Studio — Relatório de implementação

## 1. Objetivo e arquivos examinados

Base usada: Sprint 5 corrigido com motor V30.2, Observer/Event-Delta Buffer, Pydantic v1.1.0, frontend React/PixiJS e módulos anteriores. Foi inspecionado o vídeo de execução (amostras em ~35 s, ~125 s, ~220 s); ele mostra um fluxo NEXUS de 5 postos e uma navegação ATLAS mais fragmentada. Os arquivos v8/v9 exibem `ui/cinematic.py` como experimentos de movimento.

O problema observado é que um segundo frontend dependente de npm não melhorou suficientemente a experiência e introduziu etapas de instalação. A reconstrução reorganiza a página inicial e reaproveita o mesmo **motor Python** e **contrato de eventos**. O código original do workspace foi preservado em `app_classico.py` (com o Factory Command legado redirecionado), e os módulos legados permanecem disponíveis.

## 2. Implementação efetiva

- **Nova home:** Factory Command Studio, com a marca original, uma fábrica vetorial 2.5D, cinco postos da base, representação diferenciada das máquinas, estados e buffers com IDs consultáveis, contexto da falha e análise comparativa.
- **Split Futures:** A/B no mesmo instante, com divisor arrastável, modo A, modo B e visualização simultânea; o estado do futuro é reconstruído usando `common_history`, keyframes e `EventDelta` reais.
- **Replay:** play/pause, scrubber, voltar ao início, avançar para próximo evento, velocidades, marcadores de falha e bifurcação.
- **Pedidos:** evolução temporal da quantidade concluída, rota/prazo no contrato e inspeção contextual dos pedidos.
- **Indicadores:** makespan, custo de operação e SLA derivados do resultado **do motor**; o custo do reparo é explicitamente excluído do valor apresentado.
- **Murphy AI local:** uma consulta determinística simples que resume indicadores calculados e, quando se pergunta por uma OP existente, identifica seus horários de conclusão; não se apresenta como um agente generativo completo.
- **Registro:** gravar a seleção A/B ou adiamento num JSONL local com justificativa, ID, timestamp, indicadores e status `recorded_not_applied`.
- **Parâmetros:** formulário para posto afetado, instante, duração, fator hipotético de reparo e atraso de decisão; há opção de modelo demonstrativo ou modelo do workspace (limitado a 250 unidades para a visualização).
- **Início:** `app.py` novo com Factory Command como padrão e acesso ao workspace anterior. Visualização usa HTML/CSS/SVG/JavaScript **pré-incluídos**, em um iframe Streamlit. Nada precisa ser compilado com Node/npm para executar.
- **Preview offline:** `PREVIEW_FACTORY_COMMAND.html` funciona sem Streamlit, mas usa cenários fixos calculados durante a geração do pacote. Não permite editar modelo nem salvar decisões.

### Por que abandonar PixiJS na experiência padrão?

Com cinco postos e algumas dezenas de peças, SVG/DOM é suficiente e reduz drasticamente o custo de instalação, a fragilidade da integração e os compiladores necessários no Windows. O frontend React/PixiJS anterior continua no diretório `frontend/` como referência histórica, não como dependência de execução. Essa escolha deve ser reavaliada somente com benchmark quando a demanda efetiva ultrapassar o limite prático dessa visualização. O motor não ganhou novas funcionalidades por mudar o renderizador.

## 3. Experimento sintético demonstrativo

- Postos: Corte, CNC, Solda, Pintura, Montagem.
- Pedidos: OP-101 a OP-105, 58 unidades após escala sintética de demanda.
- Incidente: parada da CNC às 3 h por 12 h.
- Futuro A: sem intervenção.
- Futuro B: hipótese de manutenção expressa às 4 h, reduzindo a 45% o reparo restante (a recuperação real não é garantida).

**Resultados do motor V30.2 para esta configuração**:

| Indicador | A | B |
|---|---:|---:|
| Makespan | 22,64 h | 16,59 h |
| Pedidos atrasados | 3 | 0 |
| SLA | 40% | 100% |
| Custo operacional modelado | R$ 14.035 aprox. | R$ 7.928 aprox. |

Custos não incluem aquisição/urgência/risco/serviço da manutenção expressa, portanto a diferença é **não equivalente** a economia líquida. Falta validação industrial de restrições de pessoal, buffers e setup por sequência.

## 4. Testes executados neste ambiente

- `python -m pytest ...` nas áreas de exportação, contrato, resposta temporal, decisão e inicialização: **81 aprovados** (8,87 s no ambiente de execução).
- Comparação cruzada da reconstrução JS com `simulation_contract.seek` em **16 combinações** de instante e ramificação, para estados completos de estações, unidades e pedidos: aprovadas.
- Teste automatizado em Chromium headless com Play/Pause, navegação até a falha, seleção de posto, alternância de futuro, uso do divisor: **cinco fluxos verificados**, sem exceções JS.
- `python -m compileall` nos arquivos alterados: sem erros de sintaxe.
- O arquivo `PREVIEW_VISUAL.png` é captura do Chromium real durante o replay em 10 h. Nesse instante a CNC em A está parada e em B não está parada.

**Ainda não testado:** renderização dentro de um servidor Streamlit real (biblioteca indisponível neste contêiner sem acesso ao registro pip), execução do launcher em Windows e calibração dos modelos em fábrica real. NÃO declarar essas verificações concluídas. A interface de preview no navegador foi testada separadamente.

## 5. Critérios de sucesso e limitações

| Critério | Avaliação nesta entrega |
|---|---|
| Mais fácil de abrir | **Sim para o preview**; HTML de dois cliques. Aplicativo Windows tem launcher único, mas precisa validação no Windows. |
| Evolução visual perceptível | Nova página inicial substancialmente diferente (screenshot real em `PREVIEW_VISUAL.png`); avaliação subjetiva depende do usuário. |
| Mais animado e interativo | Replay, animações decorativas rotativas, inspeção de máquinas, slider A/B testados. Não é WebGL nem animação física de transporte. |
| Mais inteligente | Análise determinística conectada aos resultados; IA generativa avançada preservada no workspace, não integrada à mesma tela. |
| Matemática correta | Motor V30.2 original sem alterações; testes selecionados e equivalência JS/Python. Validação industrial externa pendente. |
| Integração | Novo shell compartilha os modelos e motor com o workspace clássico; preservados os módulos existentes. |
| Execução comprovada | Preview HTML executado com Chromium; Streamlit/Windows ainda precisam ser testados. |

## 6. Funcionalidades legadas e pendências

O código antigo de War Room, Evidence, Review, Goal Seek, Stress Lab, Optimization, Murphy AI e Decision Store não foi excluído. Permanece disponível via workspace clássico e seus módulos. **Não foi totalmente redesenhado nem unificado em um fluxo único de ponta a ponta**. A experiência atual resolve a fatia mais demonstrável da decisão: interrupção, impactos, comparação e registro. Algumas funções antigas, mesmo preservadas, não passaram por auditoria funcional integral nesta entrega.

Ainda pendente:

1. Restrições de skills por operador, buffers finitos e setups dependentes da sequência no DES.
2. Custo completo das intervenções e validação de premissas com dados reais.
3. Componentização nativa Streamlit bidirecional para seleção de máquina (a interface iframe funciona localmente sem atualizar Python a cada frame).
4. Verificações visuais e de inicialização em Windows, múltiplos monitores e resoluções.
5. Benchmark comparativo SVG vs PixiJS com modelos de centenas de entidades.
6. Fusão da interface antiga de ferramentas avançadas num único fluxo modernizado.

## 7. Referências de produto

- Siemens Tecnomatix Plant Simulation (documentação do produto): visualização e análise de fluxo, gargalos, buffers, throughput e experimentos. https://www.siemens.com/pt-br/products/tecnomatix/plant-simulation-software/
- AnyLogic Process Modeling Library: filas, recursos e animação vinculada a eventos de processo. https://anylogic.help/online/libraries/process-modeling/index.html

Ambas inspiraram a ligação entre visualização operacional e indicadores verificáveis; não foram usadas como fonte de dados para a simulação.
