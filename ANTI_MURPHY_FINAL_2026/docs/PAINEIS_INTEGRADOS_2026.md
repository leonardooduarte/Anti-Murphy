# Anti-Murphy — Painéis integrados e consolidação funcional

## Objetivo e alcance

A edição mantém o motor DES da V30.2 e acrescenta cinco painéis interativos **dentro do ambiente principal**. O usuário não precisa instalar Streamlit nem iniciar outro programa para consultar os indicadores fundamentais. Os números são obtidos de `simulation/nexus.py` por `atelier/service.py`, e a interface é uma leitura do experimento atual — não um gerador independente de métricas.

### Novos painéis

| Painel | Fonte calculada | Interação útil |
|---|---|---|
| Operação | `incident/normal/response.stations` | Clicar no posto seleciona e destaca o recurso na fábrica; abrir diagnóstico |
| Desempenho | `metrics`, `cost_breakdown`, `orders` | Alternar o cenário de referência, consultar atraso por pedido, abrir custos de decisão |
| Cenários | Resultados dos três cenários, alternativas enumeradas | Selecionar resposta, voltar ao replay sincronizado A/B |
| Otimização | `alternatives` com custos, SLA e avaliação do modelo | Escolher alternativa pelo gráfico; abrir Goal Seek, Sensibilidade e Opportunity Engine |
| Robustez | `simulation.advanced.monte_carlo_analysis` via `/api/advanced` | Executar 12 simulações com sementes controladas e consultar dispersão; abrir Stress Lab |

A navegação lateral ganhou uma seção **Painéis**. **Início** e **Voltar** continuam funcionais. As sete áreas anteriores permanecem presentes, assim como marca, abertura animada, editor de projetos, biblioteca de experimentos, comparação, registro de decisões e ajuda contextual. Há acesso aos painéis também no cabeçalho de Simulação.

## Alterações no código

- `atelier/service.py`: nova função `Studio.dashboards()`, somente leitura, com informações do mesmo experimento e dados calculados; inclui identificador do projeto e hash do modelo para rastreabilidade.
- `atelier/server.py`: `GET /api/dashboards`.
- `atelier/web/index.html`: nova área Painéis, abas, seleção de cenário e acesso às demais áreas.
- `atelier/web/app.js`: renderização dos cinco painéis, interações de seleção e acesso aos recursos já existentes. Cache é invalidado quando o experimento ou a resposta muda.
- `atelier/web/dashboards.css`: design e gráficos responsivos, contrastes operacionais e regras para movimento reduzido.
- `atelier/tests/test_dashboards.py`: regressões de correspondência com o motor e isolamento por projeto/seleção.

## Restrições e cuidados

1. O painel de custos diferencia custos operacionais + multas do **custo de decisão com investimento**. Uma redução em operação/multa não garante economia líquida.
2. As qualificações individuais, capacidades finitas de buffers e setups dependentes da sequência **não são totalmente validados** pelo modelo. A interface não os apresenta como certificados.
3. Monte Carlo são 12 sementes do **modelo sintético**, não probabilidades empíricas de interrupção industrial nem previsão calibrada em chão de fábrica.
4. As alternativas calculadas são enumeradas; um ponto favorável não é demonstração de ótimo global.
5. As telas completas War Room / Executive Room / Portfolio antigas continuam na pasta `FERRAMENTAS_HISTORICAS`; nesta entrega **não foram migradas integralmente**, mas as principais análises de operação, desempenho e cenários estão no mesmo ambiente principal.

## Testes executados

- `145 passed, 10 subtests passed` (testes selecionados do motor, contrato, serviço, modelos e dashboards).
- Node.js `--check` de `atelier/web/app.js`: aprovado.
- Chromium automatizado em 1280×720, 1366×768 e 1920×1080 usando HTML autocontido e respostas reais do serviço Python capturadas durante os testes. Cinco painéis abriram e navegaram; Monte Carlo retornou 12 execuções; seleção de CNC e comparação A/B voltaram para Simulação; **nenhum erro JavaScript nos fluxos exercitados**.
- HTTP real em processo local: `GET /api/state`, `GET /api/dashboards`, `POST /api/select` e atualização de `GET /api/dashboards` verificadas.
- A comunicação ponta a ponta Chromium → serviço HTTP local e o inicializador Windows **ainda exigem validação no computador do usuário**. O Chromium automatizado disponível bloqueia acesso direto a `127.0.0.1`, por isso foi utilizado um ambiente de renderização com respostas substituídas pelos mesmos dados produzidos pelo Python.
- O módulo histórico `tests/test_nexus_v30.py` não pôde ser coletado: `ModuleNotFoundError: streamlit`. Não representa aprovação nem reprovação desse conjunto de interfaces.

## Demonstração sugerida

1. Abrir `INICIAR_ANTI_MURPHY.bat`.
2. Em **Início**, destacar uma falha da CNC e consultar filas na linha do tempo.
3. Abrir **Painéis / Operação**, clicar em CNC e retornar ao posto no mapa.
4. Abrir **Painéis / Desempenho**, examinar custos e pedidos atrasados.
5. Abrir **Painéis / Cenários**, selecionar uma alternativa e abrir comparação A/B.
6. Abrir **Painéis / Otimização**, demonstrar trade-off de custo versus prazo.
7. Em **Painéis / Robustez**, executar 12 simulações e explicar a diferença entre sensibilidade sintética e previsão industrial.
8. Abrir **Decisões**, consultar Murphy local e registrar justificativa.

Nenhuma tela histórica foi apagada. O ZIP deve ser extraído em uma pasta independente das versões anteriores.
