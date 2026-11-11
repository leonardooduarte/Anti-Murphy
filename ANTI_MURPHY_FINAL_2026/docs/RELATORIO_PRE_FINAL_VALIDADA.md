# Anti-Murphy — Pré-final validada, novembro de 2026

## Objetivo

Consolidar a edição **Qualidade Final 2026** e resolver problemas observados no vídeo `05_11_4.mp4`, preservando todas as funcionalidades existentes.

## Alterações implementadas

1. **Murphy AI: gargalos e pedidos em risco.** A função determinística `atelier/decision_explainer.py` agora responde a perguntas simples e combinadas. Lê `bottleneck`, `stations` (espera média, fila máxima) e `orders` (atraso por pedido) do mesmo experimento. Explica que o gargalo global pode ser diferente do posto com maior espera; nunca deduz causa física só pelo tempo de espera. Identifica pedidos recuperados na resposta selecionada. Perguntas de capacidade orientam a executar o laboratório, sem inventar uma nova simulação.
2. **Estado do pedido coerente no replay.** Os cartões da carteira agora destacam o atraso previsto no cenário *sem intervenção*, usando `late_before`; a resposta usa `late_after`. O plano nominal não recebe indevidamente o atraso do incidente.
3. **Animações com estado e tempo.** Máquinas e ferramentas animadas ficam pausadas quando não há operação em processamento, quando o replay está pausado ou quando o posto está parado. Respeita `prefers-reduced-motion`. Manteve a abertura animada oficial. Não foi atribuída duração falsa ao transporte.
4. **Visualização operacional mais legível.** Tratamento de contraste e leitura dos indicadores do instante no rodapé. A faixa ampliada de valores só aparece em tela cheia, evitando cobrir a solda e outras máquinas durante a operação normal.
5. **Sequência de investigação na Análise.** Incidente → Pedidos afetados → Resposta selecionada. Elementos clicáveis levam à fábrica e ao instante simulado, com contagens calculadas a partir dos `order_impacts` e métricas existentes. Não é alegação de causalidade industrial.
6. **Decisão: validação visível e persistência.** Contador de caracteres e aviso contextual; registro só é confirmado quando o backend salva. A justificativa não é perdida em caso de erro; após salvar, o histórico pode ser consultado.
7. **Custos e investimento.** Conservada a reconciliação das três parcelas com o custo total da decisão e a diferença líquida em relação à falha sem resposta. Valores negativos que arredondam a zero não são exibidos como `-R$ 0`. Investimento modelado zero recebe ressalva explícita.
8. **Navegação do Murphy.** A resposta sobre gargalos oferece ação para investigar a fábrica e o painel operacional.

## Validações concluídas

- **201 testes Python aprovados + 10 subtestes** em `atelier/tests`, `contract_tests` e `tests`, com **4 testes legados desmarcados** por dependerem da estrutura da V31. Três módulos de testes da UI clássica dependentes de Streamlit foram excluídos por falta da biblioteca no ambiente.
- **12 testes de qualidade, dashboards e pré-final** incluídos nos 201, examinando composição econômica, respostas factuais, read-only, restrições industriais, registro e recuperação da justificativa.
- **Chromium com Python real e ponte de transporte de teste:** resoluções 1280×720, 1366×768 e 1920×1080. Verificados mapa de CNC parada, 3 pedidos em atraso no cenário sem intervenção, comparação A/B, sequência de investigação, dashboards, Murphy AI e registro/histórico. Sem erros JavaScript nos fluxos executados.
- **HTTP local real:** status 200 para `/`, `/app.js`, `/styles.css`, `/prefinal_polish.css`, logo, `/api/state` e `/api/dashboards`. A consulta real `POST /api/assistant` retornou a resposta específica de gargalo e pedidos.
- **Integridade:** motor, serviço, servidor, inicializador e logos comparados byte a byte com o ZIP Qualidade Final enviado pelo usuário; permanecem idênticos.

## Verificações ainda necessárias

- **Windows:** executar `INICIAR_ANTI_MURPHY.bat` e acompanhar carregamento, resposta ao replay e salvamento em uma pasta extraída limpa.
- **Desempenho visual:** medir taxa de quadros e tempo de resposta no hardware em que será apresentado; não foi comprovado FPS constante.
- **Funcionalidades históricas ATLAS/NEXUS:** ainda há módulos não migrados integralmente da interface Streamlit para o Workbench.
- **Restrições industriais e dados reais:** modelar e validar skills específicas, setups dependentes da sequência, buffers finitos, custos de recursos e disponibilidade real. O modelo sintético não os certifica.

## Arquivos alterados

- `atelier/decision_explainer.py` — resposta determinística mais contextual.
- `atelier/web/app.js` — coerência do risco, análise navegável, validação da decisão, legibilidade monetária e integração do Murphy.
- `atelier/web/index.html` — status acessível da justificativa e elementos da visualização.
- `atelier/web/prefinal_polish.css` (novo) — refinamento da interface e das animações.
- `atelier/tests/test_prefinal_gate.py` e `atelier/tests/browser_prefinal_gate.py` (novos) — verificações de regressão e navegação.
- `atelier/tests/http_prefinal_smoke.py` (novo) — teste real do HTTP local.

As novas camadas não instalam bibliotecas externas, não reescrevem o motor e não alteram as fórmulas de simulação.
