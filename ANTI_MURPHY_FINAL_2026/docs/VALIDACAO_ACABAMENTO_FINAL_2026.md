# Evidências de validação — Edição Acabamento Final 2026

## Testes executados

- `node --check atelier/web/engineering_charts.js` — sintaxe JavaScript aprovada.
- `python -m atelier.tests.browser_acabamento_final` — Chromium, dados do motor Python com transporte local adaptado ao ambiente de testes, em **1280×720**, **1366×768** e **1920×1080**. Para 12 cenários, verificou numeração, ausência de sobreposição de rótulos, legenda completa, seleção bidirecional, detalhe legível, modo ampliado, troca de indicador, fechamento por `Esc`, exports CSV e SVG, transição para outras análises e ausência de exceções JavaScript.
- `python -m atelier.tests.http_charts_smoke` — servidor local real e 12 análises, aprovado.
- `python -m atelier.tests.http_premium_banca` — servidor HTTP e Modo Banca, aprovado.
- `python -m atelier.tests.http_acabamento_final` — rotas e arquivos desta revisão, aprovado.
- `python -m atelier.tests.validacao_experimentos_banca` — os três experimentos sintéticos anteriores, aprovados, sem alterar o motor.
- `pytest -q atelier/tests contract_tests tests` com as exclusões legadas abaixo: **213 aprovados, 5 deselected, 10 subtestes aprovados**.

## Testes legados e limites explícitos

Três arquivos de teste que requerem a estrutura histórica Streamlit foram ignorados (`test_nexus_ui`, `test_nexus_v30`, `test_operation_ui`). Cinco expectativas legadas foram retiradas da seleção da suíte porque dependem do antigo roteiro Streamlit, do inicializador `tools/start_nexus.py` ou de `PREVIEW_OPERACAO.html`, que não é o ponto de entrada da interface atual. A exclusão **não equivale a aprovação** de tais testes; não alteramos os testes históricos apenas para obter resultado verde. O Modo Banca Premium foi executado e passou em 1280×720 e 1366×768 nessa rodada; o cenário de 1920×1080 foi interrompido por tempo de execução da suíte ampla. A nova bateria específica dos gráficos passou nas **três** resoluções.

## O que os testes não comprovam

- Homologação do software em fábrica industrial real, calibração estatística e disponibilidade física de recursos.
- Operação e performance em todos os computadores Windows ou projetores.
- Teste completo da interface histórica separada dependente de Streamlit.
- Ausência de todo defeito em fluxos não exercitados.

## Reprodução

Para verificar o gráfico, execute `INICIAR_ANTI_MURPHY.bat`, abra `Ensaios → Otimização de capacidade`, execute o ensaio, selecione `02` na legenda, altere o indicador, amplie, feche com `Esc` e exporte CSV/SVG. Confirme que os dados listados correspondem ao motor e que nenhum nome aparece sobreposto no eixo horizontal.
