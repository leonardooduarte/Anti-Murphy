# INT-03 — biblioteca de experimentos resiliente

## Base e escopo

Base INT02-2026.1, commit f0baa1a813212c70e35045cdf22aeafb19817641, branch correcao-int02-precisao-auditoria. Nova branch correcao-int03-biblioteca-resiliente; checkpoint 025e4ce. Sem agentes paralelos. Não houve reconstrução, uso de ZIP antigo, remoção de funcionalidades ou alteração do motor.

Escopo exclusivo: impedir que documentos inválidos na coleção de experimentos bloqueiem os válidos, a comparação, novas gravações ou a abertura do projeto; informar os problemas e preservar seus arquivos. INT-04 (contraste), Windows/BAT/projetor e pendências históricas continuam separados. INT01/INT02, identidade visual, abertura, Modo Banca, gráficos e cálculos anteriores são preservados.

## Reprodução

before.log mostra que, após salvar um experimento válido e adicionar experimentos/invalid.json com [], tanto experiment_list quanto save_experiment levantavam AttributeError em d.get. Os arquivos continuavam presentes, mas a coleção não era utilizável.

before-startup.log executa o mesmo caso na extração INT02 intacta: Studio também falhava na inicialização. O método info consulta a contagem dos experimentos; portanto, o erro da coleção podia impedir a abertura de uma instalação já existente, além da tela de biblioteca. Não foi demonstrada perda de dados, mas indisponibilidade confirmada.

Os 24 primeiros casos do contrato proposto falharam na base e passaram após a alteração. Depois foram adicionados os casos de enumeração inacessível e JSON excessivamente aninhado, chegando a 26 casos novos. A preservação na reabertura também foi incorporada aos casos de documentos inválidos. before-tests.log registra o estágio inicial; não representa 24 defeitos independentes.

## Contrato de leitura

O novo módulo atelier/experiment_library.py faz leitura individual, sem reparo ou gravação. Reconhece .json e .JSON, sem depender da sensibilidade a maiúsculas do sistema de arquivos. Cada documento do projeto atual deve ter objeto JSON, identidade textual coerente com o nome do arquivo, nome, projeto e model_hash identificáveis, além de métricas de cenário em estrutura suportada. Campos opcionais, como data e resposta, podem faltar; economia ausente ou null continua pelo contrato legado da AM08, sem inferir investimento zero. Um documento sem os campos mínimos é preservado e listado como problema, sem inventar sua origem ou seu conteúdo.

São isolados, entre outros: JSON truncado, null/lista/texto no lugar de objeto, codificação inválida, identificador incompatível, campos estruturais incompatíveis, métricas numéricas com tipo inadequado, números não finitos, documento aninhado além da capacidade de leitura e falha de acesso a um arquivo. Os dados são conferidos também quanto à serialização JSON finita, para que um valor inválido escondido não derrube toda a resposta.

Arquivos reconhecidamente de outros projetos não entram na biblioteca corrente. Arquivos sem origem identificável geram diagnóstico na coleção compartilhada; a interface explica que eles podem pertencer a outro projeto. Os nomes são relativos à pasta experimentos, sem adivinhar associação.

Nenhum arquivo inválido é apagado, movido, normalizado, sobrescrito ou considerado experimento válido. O limite de 100 experimentos por projeto continua existindo e conta os registros válidos desse projeto. Falha ao enumerar a pasta inteira é um erro controlado de acesso, não uma coleção vazia fictícia. Não se promete abertura normal se a própria pasta não puder ser consultada; nesse caso é necessário restabelecer acesso aos arquivos.

## Serviços, API e interface

Studio._experiment_documents concentra o acesso e converte falha de enumeração em StudioError com mensagem de acesso. Studio.experiment_library retorna um snapshot com project_id, items e issues. Cada issue informa filename e reason. A leitura não executa simulação nem altera modelo ou arquivos.

Studio.experiment_list conserva o retorno em lista, inclusive em GET /api/experiments. Clientes locais anteriores continuam recebendo o mesmo tipo de resposta. GET /api/experiment-library é o endpoint adicional usado pela interface para obter registros e avisos na mesma leitura. A validação Host/Origin da AM22 se aplica a ele como às demais rotas GET.

A comparação seleciona os documentos já validados daquela leitura, sem reabrir caminhos formados por identificadores não validados. IDs não pertencentes à coleção válida/projeto atual recebem erro controlado. Usa get para resposta opcional em registros antigos. Fórmulas de delta e componentes econômicos não foram alteradas. A gravação de um novo experimento continua com o mesmo contrato de persistência; os documentos antigos não são regravados.

loadExperiments usa o snapshot do projeto corrente e descarta resposta identificada com outra origem. Um aviso na biblioteca apresenta quantidade e detalhes dos arquivos problemáticos, com nomes/motivos escapados. Os controles de consulta, comparação e gravação dos válidos permanecem disponíveis. O aviso não obriga etapas de reparo para usar os válidos. Ao reler, um reparo externo explicitamente realizado passa a ser reconhecido; a aplicação não faz esse reparo automaticamente.

Sem problemas, o aviso fica oculto e a aparência normal é preservada. O novo elemento é criado pelo JavaScript, mantendo index.html e todas as folhas CSS intactos. Não houve redesenho nem correção de contraste nesta etapa.

## Arquivos e testes

Produção: atelier/experiment_library.py (novo leitor/validador); atelier/service.py (leitura, lista e comparação); atelier/server.py (rota adicional); atelier/web/app.js (snapshot e aviso).

Testes: tests/test_int03_experiment_library.py acrescenta 26 casos. Dezoito variantes de documento inválido conferem listagem, comparação, nova gravação, bytes anteriores e reabertura. Outros casos cobrem legado econômico com resposta/data opcionais ausentes e extensão .JSON, reparo externo explícito, isolamento entre projetos, seleção de documento inválido, leitura negada por arquivo, limite de válidos com 100 inválidos presentes, enumeração da pasta negada e aninhamento excessivo.

atelier/tests/browser_int03.py usa HTTP e serviço reais nas três resoluções: biblioteca mista com válidos/legado/inválidos, aviso expandido, nomes escapados (sem criação de elementos HTML pelo nome do arquivo), API antiga em lista, comparação normal e econômica parcial, nova gravação com aviso, separação de projetos e releitura após reparo externo. Verifica que somente a contagem cresce após guardar, conservando o restante do cálculo e os arquivos anteriores.

O primeiro instrumento de navegador comparava info inteiro antes/depois de uma gravação esperada. browser-initial.log e browser-instrument-diff.log preservam a investigação: a única diferença era experiment_count de 3 para 4. A asserção final exige exatamente esse incremento e igualdade de todos os outros campos, além dos bytes dos arquivos anteriores. Não houve mudança do produto para encobrir uma alteração do cálculo.

Cinco adaptadores de transporte dos runners browser_acabamento_final, browser_banca_gate, browser_final_banca, browser_prefinal_gate e browser_premium_banca receberam uma rota adicional delegada ao serviço real. As rotas e verificações anteriores foram mantidas; não se substituiu o serviço por resposta fixa. A execução atual cobre o acabamento/gráficos por seu adaptador e o Modo Banca por HTTP real; não significa que todos os runners históricos foram homologados novamente.

VERSAO_INT03.json e tests/test_am19_distribution.py estendem a cadeia de hashes da alteração autorizada em app.js. AM19, prioridade, INT01 e INT02 conservam suas referências originais; o teste continua conferindo engine e os demais arquivos visuais. Nenhum teste foi removido, desativado ou convertido em aprovação incondicional.

## Resultados

Regressão completa: 732 testes aprovados, zero falhas e dez subtestes. Warning de depreciação do plugin AnyIO, sem falha funcional. Os testes direcionados sobre o pacote extraído conferem também as asserções finais de reabertura da coleção.

INT03 no navegador passou em 1280x720, 1366x768 e 1920x1080, sem exceções JavaScript não tratadas e sem overflow horizontal do documento. As verificações de economia AM08 também passaram nas três resoluções, incluindo investimento ausente em legado sem regravação. Modo Banca, justificativa, registro, relatório, gráficos, ampliação e exportações passaram nas três resoluções.

Três experimentos oficiais preservados. A: SLA nominal/incidente/resposta 100/40/100%, custo total da decisão R$12.113,00 e economia líquida R$4.103,68; B/C conforme banca.log. Nenhuma referência foi artificialmente ajustada.

Comandos: python -m pytest tests contract_tests atelier/tests -q -p no:cacheprovider; python -m pytest tests/test_int03_experiment_library.py tests/test_am19_distribution.py -q -p no:cacheprovider; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_int03; python -m atelier.tests.browser_am08; python -m atelier.tests.browser_acabamento_final; python docs/AM19/evidencias/actual_http_browser.py. Navegador usa Playwright/Chromium no Linux; não são dependências novas para iniciar o aplicativo principal.

## Entrega, limites e continuidade

ZIP completo atualizado, patch sobre os 697 arquivos INT02, relatório, continuidade, logs e capturas. O patch confere a base e cria outra pasta, preservando a origem. ZIP é extraído, patch aplicado em base limpa e resultados comparados por SHA-256. Testes direcionados rodam na extração; arquivos publicados no GitHub são recuperados e comparados aos locais antes da conclusão.

A validação é estrutural e de disponibilidade da coleção, não autenticação criptográfica dos experimentos nem comprovação industrial dos valores. Campos/formatos históricos fora do contrato suportado permanecem preservados com aviso, sem migração por adivinhação. Arquivos reparados ou acrescentados externamente dependem de nova leitura da biblioteca; não foi criado monitoramento contínuo da pasta.

Não houve validação nativa no Windows, BAT ou projetor. Instale em pasta nova e mantenha versões e projetos anteriores. Próximo passo recomendado: INT-04, legibilidade/contraste pontuais identificados pela auditoria, preservando a identidade e os fluxos. Não avançar para reorganização ampla ou novos recursos nesta entrega.
