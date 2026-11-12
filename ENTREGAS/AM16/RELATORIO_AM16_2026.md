# AM16 — execução única de Monte Carlo sobre AM07/AM17

Base 9d4697c0970d4b10a59119004ee7ecc7f02a5198. Branch correcao-am16-monte-carlo.

Reprodução executou a função original em Node: duas ações antes da resposta iniciam duas requisições pendentes. Nenhum DES foi executado nessa reprodução (reproduction.log).

A versão nova usa um estado compartilhado de execução em andamento entre Painéis e Ferramentas. A aquisição acontece antes do primeiro await; cliques repetidos, inclusive eventos programáticos, não iniciam nova requisição. O estado é liberado em finally após sucesso ou erro. O ID de histórico só é criado para uma submissão aceita. Fórmulas, sementes, número de réplicas, backend e origem AM05 dos resultados não mudaram.

Os botões Monte Carlo ficam desabilitados, com texto Monte Carlo em andamento e aria-busy. A sinalização é reaplicada após reconstrução da interface, troca de aba ou navegação entre as duas entradas. Ferramentas de outros tipos continuam habilitadas; a navegação não é bloqueada. Respostas tardias continuam recebendo a classificação de origem AM05. Um resultado anterior não é removido enquanto se espera. Não há recálculo automático.

Produção: somente atelier/web/app.js, funções dashRunRobustness, runAdvanced, renderDashboards, renderAdvancedInfo e novas syncMonteCarloControls/monteCarloPending. Testes novos test_am16_pending.py e browser_am16.py. Motor, dados locais, abertura, CSS, gráficos e correções anteriores preservados.

Regressão: 522 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados. Dois testes novos de sucesso/erro verificam chamadas das duas entradas, proteção contra duplicata e repetição. Três experimentos oficiais preservados: SLA 100/40/100%, custo de decisão R$12.113,00 e economia R$4.103,68. Browser nas três resoluções (1280x720,1366x768,1920x1080) passou: duplo clique, reconstrução do painel, troca de tela, outras ferramentas habilitadas, falha controlada, repetição e sucesso sem erros JavaScript. A rede do Monte Carlo é retida/interceptada para controlar o instante de resposta; o resultado usado é calculado pelo serviço real, em armazenamento temporário. Não se afirma medição de latência real.

As cinco falhas antigas permanecem em operation_ui, restauracao_acesso (dois) e v31_editorial (dois); log completo preservado, sem exclusão de testes. Os testes novos no ZIP extraído também foram executados.

Limite: coordenação por página do navegador. Janelas independentes, outros clientes ou chamadas diretas à API podem submeter análises distintas; não foi introduzido bloqueio global no servidor nem cancelamento de tarefas. Mudanças de projeto continuam livres e a resposta mantém a origem anterior. Um pedido sem resposta permanece sinalizado até a requisição terminar; não se inventa progresso percentual. Windows/projetor pendentes de validação local.

ZIP e patch sobre a base exata são extraídos e comparados por SHA-256. Aplicador cria uma pasta nova, preservando a base. Instale em pasta nova. Próximo recomendado: rastreabilidade AM13/14, depois legibilidade AM15; as demais pendências documentadas na AM17 continuam abertas.

Reprodução: python -m pytest tests contract_tests atelier/tests -q; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_am16. Node é requisito dos testes JavaScript, Playwright/Chromium dos testes de navegador; não são dependências novas do aplicativo.
