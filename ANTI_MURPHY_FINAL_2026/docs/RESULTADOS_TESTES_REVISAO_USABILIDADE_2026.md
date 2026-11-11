# Resultado da revisão — 09/11/2026

## Testes concluídos nesta execução

- Regressão Python: **214 testes aprovados, 10 subtestes aprovados, 4 testes legados desmarcados**.
- Testes de integridade monetária/decisão: **8 aprovados**.
- Navegador Chromium: Modo Banca completo **1280 × 720, 1366 × 768, 1920 × 1080**, incluindo aviso de valor não conferido, possibilidade de confirmar, justificativa curta livre, risco opcional, registro e relatório.
- Testes HTTP: HTML, JavaScript, CSS, dashboards, auditoria técnica, rotas de estado e replays respondendo normalmente.
- Experimentos sintéticos de engenharia: três experimentos reproduzidos novamente.

## Exclusões e ressalvas

Quatro testes legados foram excluídos por validarem prévia HTML ou strings específicas de um inicializador/fluxo de Streamlit antigo, incompatíveis com a distribuição atual. Não significam que os módulos legados foram homologados. Os módulos dependentes de Streamlit não foram validados nesta execução. A distribuição ainda precisa ser executada no Windows do usuário para validar a inicialização e legibilidade no projetor.

A revisão não modifica o motor de cálculo. O software não prova a execução física de qualquer intervenção nem valida valores externos informados na justificativa.
