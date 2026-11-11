# Registro de testes — revisão 09/11

## Resultados obtidos

- `pytest -q atelier/tests contract_tests tests` com três módulos legados Streamlit não coletáveis neste ambiente e quatro testes de versões antigas explicitamente deselected: **211 passed, 4 deselected, 10 subtests passed**.
- `python atelier/tests/browser_final_banca.py`: **aprovado** em 1280×720, 1366×768 e 1920×1080; percorreu seis etapas, salvou registro real, verificou relatório e histórico e testou uma alternativa dominada e a posterior comparação.
- `python -m atelier.tests.validacao_experimentos_banca`: **3 EXPERIMENTOS APROVADOS** (parada, capacidade, decisão multicritério).
- `python atelier/tests/http_banca_smoke.py`: **HTTP checks OK**, rotas de estado, painéis e auditoria técnica.
- `python -m atelier.tests.http_refino_09_11`: **HTTP OK**, arquivos estáticos, cenário recalculado, parecer de dominância, troca de seleção, gravação e histórico.
- `node --check atelier/web/app.js`: verificação de sintaxe JavaScript sem erros.

## Limitações dos testes

A execução no Windows do usuário, o antivírus, a escala do projetor e os módulos históricos Streamlit não foram verificados diretamente nesta estação. O pacote integra os testes para que possam ser reexecutados. Quatro testes legados ainda esperam um inicializador ou uma prévia HTML de versões antigas e não se aplicam ao frontend HTTP atual.

## Casos negados e proteção

O alerta de dominância não escolhe automaticamente outro cenário; só indica as alternativas **elegíveis no modelo**. O registro exige justificativa de pelo menos 12 caracteres e reconhecimento das limitações. O relatório não chama um estudo não registrado de decisão concluída. Custos, SLAs e tempos são derivados do motor, não gerados pelo CSS ou por animações do frontend.
