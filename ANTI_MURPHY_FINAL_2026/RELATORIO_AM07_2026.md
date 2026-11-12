# AM07 — Replay reduzido sobre AM17

Base ef1624ea3b81db2ded022e78af89092a558129ab. Branch correcao-am07-replay.

O backend continua omitindo detalhes por peça acima de 12.000 operações, mas conserva agora inícios e términos de cada segmento de processamento por posto. A contagem usa intervalos semiabertos: inícios até t menos términos até t. Não se presume que toda operação ativa esteja processando: setup e interrupções ficam suspensos. O frontend usa busca binária nessas séries para o modo reduzido. O snapshot Python também consulta segmentos reais; para payloads antigos sem essas séries retorna processamento desconhecido (None).

Antes: referência mínima com active=1, operações omitidas e um segmento [0,2] mostrava processing=0 em t=1. Depois: processing=1. Log reproduction.log. Testes usam resultado real com 12.012 operações e comparação independente dos segmentos, inclusive durante falha, retomada e limites de tempo. O motor DES não mudou.

O diário e o cronograma avisam que os detalhes por peça foram omitidos. O mapa e o inspetor deixam de afirmar ausência de trabalho apenas porque a identificação da peça não está disponível. Contagens agregadas, recursos e navegação continuam disponíveis. Não se inventam identificações nem cronogramas individuais.

520 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados. Dez casos novos aprovados. Três experimentos oficiais preservados: SLA 100/40/100%, custo de decisão R$12.113,00, economia líquida R$4.103,68. Browser HTTP real com 12.012 operações passou em 1280x720, 1366x768 e 1920x1080. As cinco falhas antigas continuam nos testes operation_ui, restauracao_acesso (dois) e v31_editorial (dois), detalhadas em regression.log; nenhum foi removido.

Produção: simulation/replay.py (replay_payload, snapshot) e atelier/web/app.js (machineState, frameStation, renderEventLog, renderSchedule e texto do inspetor). Testes novos test_am07_reduced.py e browser_am07.py. Fórmulas, engine.py, dados locais, identidade, abertura, AM17 e demais correções preservados. As séries agregadas aumentam o payload proporcionalmente aos segmentos; continuam sujeitas aos limites de cálculo AM17. Replays antigos em memória sem as novas séries precisam de atualização da página/servidor; não há migração de payloads externos arbitrários. O histórico armazenado de decisões não foi regravado.

Windows e projetor não homologados nativamente. Próxima etapa recomendada: AM16, submissões duplicadas de Monte Carlo; depois rastreabilidade e legibilidade AM15. A pendência de prioridade opcional do editor documentada no AM17 continua aberta.

Reprodução: python -m pytest tests contract_tests atelier/tests -q; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_am07. Testes JavaScript exigem Node; navegador usa Playwright e Chromium em Linux. Execute em cópia.

ZIP extraído e patch aplicado sobre a base exata são comparados por SHA-256. O aplicador cria uma pasta nova. Instale o ZIP completo em pasta nova e execute INICIAR_ANTI_MURPHY.bat. Preserve sua instalação e projetos anteriores.
