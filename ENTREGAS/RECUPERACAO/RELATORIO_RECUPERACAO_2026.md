# Recuperação local — complemento exclusivo da AM01

Base: PRIORIDADE-2026.1, commit e9ba7a25f754ed4c8bf63ccb86db4d42344c0013. Branch correcao-recuperacao-local. Checkpoint 0ff38d2. Evolução visual, correção de prioridade, AM19 e demais entregas preservadas. Não foi utilizado ZIP antigo.

## Defeitos reproduzidos

before.log registra dois casos sobre a base exata: projeto ativo com JSON corrompido abria sem aviso, com duração padrão de 8 h no lugar das 5 h confirmadas; ponteiro com id ../invalido provocava StudioError e impedia a abertura. O checkpoint não foi alterado nessa reprodução, mas não era consultado pelo primeiro caminho. Portanto, a recuperação aparente não garantia recuperação do experimento completo. A cópia de reprodução usou diretório temporário e não projetos reais.

## Contrato e solução

atelier/service.py, Studio._initialize: o candidato completo é validado antes de publicar modelo, regra ou experimento. A ordem é projeto ativo válido; última configuração confirmada válida; modelo básico legado válido; exemplo padrão. O modelo básico não contém os parâmetros completos do experimento: ao utilizá-lo, aplicam-se os defaults compatíveis e mostra-se aviso se houve falha anterior. Ausência total de dados em uma instalação nova continua sendo inicialização normal.

JSON malformado, estrutura incompatível, modelo inválido, identificador inválido, regra inválida, referência a pedido prioritário inexistente e parâmetros inválidos impedem o uso daquele candidato. O tratamento é restrito à leitura e validação de cada candidato; falhas de programação e de simulação não são engolidas por um except genérico. O identificador do ponteiro e o do checkpoint são validados pelo contrato existente, sem permitir caminhos externos.

Studio._persist_model: durante uma abertura com recuperação, não grava projeto.json, projeto_ativo.json, projeto_confirmado.json ou documentos de projeto. Os originais, inclusive os danificados, permanecem disponíveis. Reabrir não destrói evidências nem substitui o último checkpoint. O aviso explica a recuperação e orienta conferir os dados antes de aplicar ou salvar. Uma ação explícita de salvamento usa a transação existente e limpa o aviso após sucesso; a reabertura carrega o estado confirmado. Esta etapa não acrescenta histórico ilimitado nem backup automático após uma ação explícita: para conservar indefinidamente um arquivo danificado, copie a pasta antes de salvar. O lock local e as verificações de revisão da AM12 continuam ativos.

O helper interno validated valida o conjunto modelo/regra/spec/espera antes de substituir qualquer parte do estado. Não alteramos o motor DES, fórmulas, custos, investimentos, prioridades opcionais, CSS, HTML ou JavaScript. Os arquivos visuais e simulation/engine.py permanecem idênticos à base; a regressão também verifica os hashes visuais herdados.

## Testes

20 casos novos em tests/test_startup_recovery.py: JSON truncado, array, null, documento ausente, identificadores inválidos, modelo inválido, regra, spec, pedido crítico e espera inválidos; checkpoint inutilizável em cinco variantes; todas as fontes inválidas; ponteiro ausente; reabertura saudável; salvamento explícito após recuperação. As verificações comparam o conteúdo de todos os JSON e repetem a abertura para demonstrar preservação. Não alteramos nem desativamos testes antigos.

atelier/tests/browser_startup_recovery.py: servidor HTTP real, aviso visível, restauração dos parâmetros, arquivos intactos antes de salvar, aplicação explícita e reabertura, sem erro JavaScript em 1280x720, 1366x768 e 1920x1080. Capturas e logs acompanham a entrega.

Regressão: 597 aprovados, zero falhas, dez subtestes. Três experimentos oficiais preservados: A com SLA 100/40/100%, custo total da decisão R$12.113,00 e economia líquida R$4.103,68; B e C mantiveram os resultados registrados no log. Gráficos/exportações e Modo Banca com justificativa, registro e relatório foram conferidos nas três resoluções. Eventual warning do plugin AnyIO é de depreciação, não falha funcional.

Comandos: python -m pytest tests contract_tests atelier/tests -q; python -m pytest tests/test_startup_recovery.py tests/test_am19_distribution.py -q; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_startup_recovery; python -m atelier.tests.browser_acabamento_final; python docs/AM19/evidencias/actual_http_browser.py. Os testes de navegador usam Chromium/Playwright no Linux.

## Entrega e limites

ZIP completo com recursos essenciais e arquivos anteriores; patch aplicado sobre uma extração limpa da base e criando pasta nova; relatório, continuidade, logs e hashes. Extração do ZIP e aplicação do patch devem produzir os mesmos arquivos, conferidos por SHA-256. A publicação é recuperada do GitHub e comparada aos arquivos locais antes de declarar conclusão.

Não houve validação nativa no Windows, BAT ou projetor. Não se promete resistência a toda falha física nem recuperação de conteúdo inexistente em todas as fontes. Arquivos de dados do usuário não foram modificados. Runners históricos e limitações documentadas nas entregas anteriores permanecem. Host/Origin, avaliação visual e outros achados não foram alterados.
