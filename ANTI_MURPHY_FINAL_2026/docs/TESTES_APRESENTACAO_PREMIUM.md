# Evidências de testes — Modo Banca Premium

## Procedimentos executados

1. `node --check atelier/web/app.js` — parser JavaScript: aprovado.
2. `python -m atelier.tests.browser_premium_banca` — Chromium em 1280×720, 1366×768 e 1920×1080: 6 etapas, revelação progressiva, painéis lado a lado, estado da CNC, alternância de foco, registro, justificativa técnica, relatório em pop-up, fallback para HTML e retorno ao modo convencional. **Aprovado nas três resoluções, sem exceções JS nos percursos exercitados**.
3. `python -m atelier.tests.browser_final_banca` — suíte anterior adaptada ao novo botão de relatório da etapa final; as três resoluções aprovadas.
4. `python -m atelier.tests.http_premium_banca` — HTTP local real: `/`, `/app.js`, `/apresentacao_premium.css`, `/api/state`, `/engineering_charts.js` e CSS anterior. **Aprovado**.
5. `python -m atelier.tests.http_refino_09_11` — parecer multicritério, alternativa selecionada, registro persistido, histórico. **Aprovado**.
6. `python -m atelier.tests.validacao_experimentos_banca` — três experimentos sintéticos de parada, capacidade e decisão multicritério. **Aprovados**.
7. `pytest -q atelier/tests contract_tests tests --ignore=tests/test_nexus_ui.py --ignore=tests/test_nexus_v30.py --ignore=tests/test_operation_ui.py` — 211 testes e 10 subtestes aprovados; **quatro falhas em testes legados não aplicáveis**, que procuram um roteador Streamlit antigo e um `PREVIEW_OPERACAO.html` não distribuído na interface integrada.
8. Reexecutado com `--deselect` apenas nesses quatro casos legados: **211 passed, 4 deselected, 10 subtests passed**.

Os três módulos legados que dependem de Streamlit não foram coletados neste ambiente; o motor de cálculo e a interface HTTP atual foram testados, mas os caminhos históricos não foram homologados. Esta bateria **não equivale a auditoria de segurança**, validação física da fábrica ou teste de compatibilidade no Windows real.

## Testes de negação relevantes

- Um texto repetitivo sem análise técnica foi recusado na etapa final do Modo Banca. O modo normal manteve a validação mínima original.
- Uma janela de relatório bloqueada resultou em **download HTML**, mantendo acessível o registro já persistido.
- A apresentação não mostrou custo de intervenção no Plano antes da ocorrência.
- O Modo Banca preserva a seleção atual e não altera automaticamente a resposta multicritério.
- O divisor móvel continua disponível fora do modo apresentação.

## Arquivos de captura de tela

`docs/capturas_apresentacao_premium/`: plano, falha, pedidos, intervenção, comparação focada, comparação do layout, decisão e registro — cada um nas três resoluções.
