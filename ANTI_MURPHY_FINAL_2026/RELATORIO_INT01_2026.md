# INT-01 — contrato de importação da regra de despacho

## Base e escopo

Aplicativo base: AM22-2026.1, commit 8599a5c6f8ce361e5804f4403a8770939546df79. A branch parte da auditoria integrada c7e023c, cujo aplicativo tem exatamente os mesmos 650 arquivos da AM22. Branch de correção: correcao-int01-importacao-regra. Checkpoint 40d049d. Não foi usado ZIP antigo, não houve reconstrução nem agentes paralelos.

Escopo exclusivo: preservar dispatch_rule do JSON de modelo ao importar na interface e no backend. A auditoria permanece preservada como ponto de recuperação. INT-02 (precisão da auditoria por pedido), INT-03 (arquivo inválido na biblioteca) e INT-04 (contraste) não foram corrigidos aqui. A evolução visual, abertura, motor DES, fórmulas, gráficos, Modo Banca, arquivos arquivados e dados-base são preservados.

## Reprodução

Na AM22, exportar modelo em SPT e importar na mesma sessão após mudar para EDD mantém EDD. Há duas perdas: importModel enviava só stations/orders; set_model também ignorava dispatch_rule mesmo quando recebida diretamente. before.log registra a reprodução antes da alteração. A auditoria anterior já comprovava o caminho real de arquivo nas três resoluções.

A bateria final de 18 casos novos foi executada também contra a extração AM22 intacta, antes de considerar a correção válida: 12 falhas confirmavam perda de regra explícita ou aceitação de regra inválida; seis casos de compatibilidade/rollback já passavam. before-tests.log contém esse resultado. Uma primeira versão da asserção de conflito comparava também a lista de projetos atualizada externamente; ela foi ajustada para comparar o estado de cálculo e dados em memória que a instância deveria preservar. Isso é correção do instrumento de teste, não mudança do produto para ocultar falha. Os testes e provas finais verificam os bytes gravados e a edição externa mais recente.

## Contrato adotado

- dispatch_rule explicitamente presente deve ser string exata EDD, SPT ou FIFO. É aplicada ao candidato antes do cálculo e confirmada com o modelo na transação existente.
- Campo ausente mantém a regra atual, para compatibilidade com modelos antigos e com a atualização normal pelo editor. A importação na interface informa: arquivo sem regra; mantida a regra de despacho atual.
- null, vazio, minúsculas, espaço adicional, booleanos, números, arrays, objetos ou identificador desconhecido são inválidos. Não são convertidos em EDD nem confundidos com ausência. A interface recebe erro antes de publicar outra configuração.
- A importação continua sendo de modelo produtivo, não restauração de todo um experimento arquivado. Incidente, orçamento, meta e espera atuais seguem os contratos anteriores. Se um pedido crítico deixa de existir, continua valendo a proteção anterior que limpa essa referência.

Não há recálculo automático adicional: continua ocorrendo uma aplicação por importação. Arquivos com regra válida já são recalculados pela mesma operação que aplicava o modelo. Não se acrescentou novo formato de arquivo, dependência ou serviço externo.

## Arquivos e funções alterados

1. atelier/service.py, Studio.set_model: valida presença/tipo/valor; aplica nx_rule somente ao candidato local; publica memória e disco apenas depois de calcular e persistir com sucesso. Ausência mantém o estado vigente. As proteções de carga e de conflito da AM12 permanecem.
2. atelier/web/app.js, importModel: transmite dispatch_rule quando o JSON contém a propriedade e distingue no aviso a origem explícita do caso legado. Não normaliza inválidos para uma regra válida.
3. tests/test_int01_import_rule.py: 18 casos automatizados novos.
4. atelier/tests/browser_int01.py: exportação/download e importação/upload reais nas três resoluções, troca de projeto, legado, inválidos e reabertura.
5. VERSAO_INT01.json e tests/test_am19_distribution.py: adendo de hash da alteração autorizada em app.js. A referência AM19 e VERSAO_PRIORIDADE.json continuam byte a byte intactas. O teste confere a cadeia de hashes e continua verificando os demais arquivos visuais e engine. Não foi desativado nem afrouxado para aceitar qualquer conteúdo.

Outras alterações do pacote são somente relatório, continuidade, instruções e evidências. Nenhuma função de INT-02/03/04 foi modificada. A alteração do importador não resolve AM20, que é de caminho clássico separado.

## Validação

Regressão completa: 682 testes aprovados, zero falhas, dez subtestes aprovados. São 18 casos novos, não 18 módulos. Warning de depreciação do plugin AnyIO, sem falha funcional.

Casos novos: round-trip de EDD/SPT/FIFO em outro projeto e reabertura, com igualdade das métricas nominais; arquivos sem campo sob as três regras, preservando parâmetros não pertencentes ao modelo; nove valores explicitamente inválidos, com memória e todos os JSON intactos; falhas controladas de cálculo e persistência sem publicar a regra candidata; conflito entre instâncias preservando a gravação mais recente. O teste de falha de persistência simula OSError na transação; a cobertura anterior de rollback por substituição de arquivos continua na regressão.

Navegador HTTP real em 1280x720,1366x768,1920x1080: exportação pelo botão do produto, criação de projeto pela interface, preparação da regra oposta e importação por upload. As três regras foram preservadas e os resultados nominais coincidiram com a origem. Arquivo sem campo mantém FIFO com aviso explícito; null, spt e array retornam 400 sem alterar memória/disco. Reabertura confirmou a regra. Sem exceções JavaScript não tratadas.

AM05 foi novamente conferida nas três resoluções, incluindo origem/assinatura e resultados atuais/desatualizados/históricos. Modo Banca real com justificativa/registro/relatório e gráficos/ampliação/exportações passaram nas três resoluções.

Os três experimentos oficiais permaneceram iguais. A: SLA nominal/incidente/resposta 100/40/100%, custo total da decisão R$12.113,00, economia líquida R$4.103,68. B e C conforme banca.log. Nenhum número de referência foi ajustado para obter aprovação.

Comandos: python -m pytest tests contract_tests atelier/tests -q -p no:cacheprovider; python -m pytest tests/test_int01_import_rule.py tests/test_am19_distribution.py -q -p no:cacheprovider; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_int01; python -m atelier.tests.browser_am05; python -m atelier.tests.browser_acabamento_final; python docs/AM19/evidencias/actual_http_browser.py. Os testes de navegador usam Playwright/Chromium no Linux, sem dependências novas no aplicativo principal.

## Empacotamento e limites

ZIP completo com recursos essenciais e todos os arquivos anteriores, patch reproduzível sobre os 650 arquivos AM22 originais, relatório e continuidade. O aplicador confere a base e cria uma pasta nova, preservando a origem. ZIP extraído e patch aplicado são comparados por SHA-256; testes direcionados são executados na extração. Os arquivos publicados no GitHub são recuperados e comparados à versão local antes da conclusão.

Instale em pasta nova e preserve sua instalação e projetos anteriores. A base da auditoria e os ZIPs anteriores permanecem no GitHub. Não houve validação nativa no Windows, BAT ou projetor. Limites e pendências da auditoria integrada permanecem explícitos; esta etapa não os declara resolvidos.
