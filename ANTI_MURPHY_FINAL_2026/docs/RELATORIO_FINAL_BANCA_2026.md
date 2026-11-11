# Relatório de entrega — Anti-Murphy, edição candidata à banca 2026

**Projeto:** apoio à decisão em PCP diante de imprevistos. **Base de desenvolvimento:** ZIP da versão *Gráficos de Engenharia 2026* enviado pelo usuário. **Natureza:** protótipo acadêmico; não é uma solução industrial homologada.

## Objetivo realizado

Em vez de reconstruir a aplicação ou acrescentar um módulo de IA externo, a intervenção foi concentrada em **uma camada de apresentação e rastreabilidade do exemplo**, preservando todos os cálculos e o funcionamento das telas existentes.

## Alterações implementadas

1. **Modo banca integrado:** botão persistente no cabeçalho, seis etapas com progressão direta e botões anterior/próxima, navegação por teclado, retorno ao modo normal. A etapa de evidências abre a área de Análise de Impacto com os dados da mesma execução.
2. **Fábrica em destaque:** ocultação apenas visual dos painéis secundários durante o modo banca, palco ampliado para projetores e tipografia maior no mapa. No uso regular, o inspetor, indicadores, módulos, controles e relatórios continuam disponíveis.
3. **Incidente perceptível e correto:** faixa visual na estação interrompida, aviso contextual com posto e horário de falha, estados derivados do replay. A resposta é marcada com seu horário de aplicação conforme o replay, sem inventar eventos físicos.
4. **Comparação A/B mais clara:** chip A/B, régua visual para separar os cenários e eliminação do painel de contagem ambígua (apenas do cenário A) durante a comparação. A faixa de evidências traz os custos com centavos, distingue custo da decisão e custo de operação e preserva o investimento declarado.
5. **Ensaios e ferramentas preservados:** os 12 tipos de gráficos especializados da versão base permanecem intocados. Exportação CSV e SVG, tabela de origem e painéis continuam disponíveis.
6. **Validação reproduzível:** script novo de três experimentos, verificações independentes e saída JSON/Markdown contendo parâmetros, métricas e ressalvas.
7. **Documentação coerente:** guia rápido de execução, arquitetura real, relatório de testes, plano de cinco minutos, questões de sabatina e backlog pós-banca.
8. **Teste automatizado do novo fluxo:** script de navegador com três resoluções, verificações de paradas, comparação, navegação, passo a passo e retorno ao uso normal.

## Arquivos alterados (núcleo)

- `atelier/web/index.html`
- `atelier/web/app.js`
- **Novo:** `atelier/web/final_banca.css`
- **Novos:** `atelier/tests/browser_final_banca.py`, `atelier/tests/validacao_experimentos_banca.py`
- **Ajuste de QA:** `atelier/tests/browser_advanced_qa.py` (carrega CSS e gráficos do frontend atual e exige reconhecimento de limites no registro)
- `README.md`, `LEIA_PRIMEIRO_VERSAO_FINAL.md`, documentação em `docs/`.

**Não alterados:** `simulation/engine.py`, `simulation/nexus.py`, `simulation/advanced.py`, `atelier/service.py`, `atelier/server.py`, `atelier/technical_audit.py`, `INICIAR_ANTI_MURPHY.bat`, `atelier/web/engineering_charts.js`, `atelier/web/engineering_charts.css` e identidades oficiais. Comparativo SHA-256 em `docs/MANIFESTO_COMPONENTES_PRESERVADOS.json`.

## Resultados verificáveis

### A — Parada de máquina

Com cinco pedidos e 96 unidades, a CNC interrompida às 4 h por 8 h altera SLA de 100% para 40%. A manutenção expressa selecionada leva de volta a 100%; no modelo, custo de decisão R$ 12.113,00 e diferença frente à falha sem resposta de R$ 4.103,68. Isso não é uma economia de caixa validada.

### B — Capacidade adicional

No cenário nominal, acrescentar 1, 2 ou 3 máquinas CNC **não altera throughput de 5,682 unidades/h**. O custo unitário modelado aumenta, mostrando que o aumento de equipamento não implica aumento automático de capacidade global.

### C — Múltiplos critérios

`+1 operador · CNC`: 19,97 h, SLA 60%, custo de decisão R$ 12.712,94. `Manutenção expressa · CNC`: 21,58 h, SLA 100%, custo de decisão R$ 12.113,00. Menor makespan isolado não garante maior serviço nem menor custo.

### Conferências

Recontagem independente de quantidades e atrasos, SLA, throughput, penalidades, identidades econômicas e cronologia de operações. A auditoria técnica registra valores sintéticos e limitações das restrições industriais.

## Situação de QA

- Python: **204 testes aprovados, 4 deliberadamente retirados por expectativas de versões antigas, 10 subtestes aprovados**; alguns módulos legados e bridge não concluíram validação nesta rodada.
- Navegador: **modo banca em 1280×720, 1366×768 e 1920×1080**, sem exceções JavaScript nos fluxos exercitados.
- Ferramentas: **seis análises em 1366×768 e 1920×1080**, incluindo registro de decisão.
- HTTP: recursos, API de auditoria e 12 análises verificadas no servidor Python local.
- Windows: **abertura e execução real na máquina de apresentação ainda não verificadas**.

## Decisão sobre o escopo

Esta edição não adiciona dependência de IA generativa, não altera os indicadores para melhorar resultados aparentes e não promete precisão que a base sintética não pode demonstrar. Seu diferencial para a banca é a narrativa de evento real do motor, a documentação das escolhas e a rastreabilidade dos indicadores.

**Status:** **candidata à banca**, condicionada à verificação prática no Windows e no projetor da apresentação.


Nota AM-11: diferença econômica calculada com valores não arredondados; o resultado final é arredondado para apresentação. A diferença de R$ 0,01 frente à edição AM-06 é esperada.
