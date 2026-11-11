# Registro de validação da entrega

## Execuções comprovadas

- Serviço HTTP local inicializou, serviu `/`, CSS, JavaScript, `/api/state` e respondeu a `POST /api/lab` com 7 pontos de sensibilidade (requisição HTTP real via Python `urllib`).
- Testes de serviço `atelier/tests/test_service.py` cobrem: modelo editável e persistente, recomputação, 18 alternativas na configuração padrão, execução dos seis modos de laboratório, Murphy local, registro verificável e rejeição de modelos/assinaturas inválidos.
- Suite de regressão selecionada do motor, replay e contratos: **79 testes Python aprovados**. Não equivale a aprovação de todos os testes históricos.
- Verificação de JavaScript: `node --check atelier/web/app.js` sem erros de sintaxe.
- Jornada de uso em Chromium/Playwright **1366×768 e 1920×1080**: abertura, fábrica com cinco postos, timeline/reprodução, Split A/B, seleção de alternativa, edição de pedido, execução de laboratório, consulta Murphy, registro e consulta histórica. Não foram reportados erros JavaScript.
- Verificação específica de fidelidade da comparação: em t=10h, CNC sem resposta **parada**, e após intervenção selecionada **recuperada**, segundo o mesmo motor.
- Capturas reais da interface em `docs/capturas_reais/`.

## Limitações da verificação

- **O Windows não foi executado** nesta avaliação; o inicializador `.bat` precisa ser validado no computador do usuário. O Python precisa estar instalado.
- O navegador automatizado deste ambiente bloqueia HTTP loopback; a interface foi testada com API de ensaio local em processo, que invoca o serviço Python real. A interface foi renderizada e acionada de fato; **a conexão navegador→HTTP direta não foi comprovada no browser**. Endpoints HTTP foram verificados separadamente por `urllib`.
- A biblioteca Streamlit não está instalada aqui. Testes históricos que a importam falharam na **coleta**, não na asserção; não foram contados como aprovados. A UI histórica completa não foi auditada visualmente nesta entrega.
- Não foram medidos FPS em dispositivos Windows nem feitos testes com operadores/gestores industriais reais.
- Os resultados são derivados de modelos e hipóteses sintéticas; não são homologação industrial. Competências individuais, setups dependentes da sequência e buffers físicos exigem implementação/validação adicional.

## Repetição de testes (ambiente de desenvolvimento)

```bash
python -m unittest atelier.tests.test_service -q
python -m pytest -q atelier/tests/test_service.py tests/test_timed_response.py tests/test_decision_priorities.py tests/test_factory_command_trace.py tests/test_decision_store.py contract_tests/test_observer.py contract_tests/test_simulation_contract.py
node --check atelier/web/app.js
PYTHONPATH=. python atelier/tests/browser_quality.py
```

A última linha requer Playwright e Chromium, **não** necessários para o programa normal.
