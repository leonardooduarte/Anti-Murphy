# INT-04 — contraste e legibilidade pontuais

## Base e escopo

Base INT03-2026.1, commit 974f38e70634ee6250878036fbd8759fc315bd17, branch correcao-int03-biblioteca-resiliente. Nova branch correcao-int04-legibilidade; checkpoint 2059b39. Sem agentes paralelos. Não houve reconstrução, uso de ZIP antigo ou correção de outros achados.

Único arquivo de produção alterado: atelier/web/styles.css, regra .alt-metrics small. A alteração alcança os rótulos dos indicadores da alternativa na análise e nas decisões. Não muda todo o texto do aplicativo nem redesenha telas. HTML, JavaScript, motor DES, fórmulas, dados, navegação, abertura e demais folhas CSS são preservados.

## Reprodução e critérios

O navegador da versão INT03 mediu as duas áreas em 1280x720,1366x768,1920x1080. Os 24 rótulos observados usavam fonte de 10 px, cor rgb(117,134,129) (#758681), fundo branco e contraste 3,829729:1. O limiar adotado é 4,5:1 para texto normal, conforme WCAG 1.4.3 AA. Fonte de 10 px é uma evidência de densidade/legibilidade; a WCAG não estabelece 14 px como mínimo universal.

A medição aguarda o término da animação de entrada da área. As primeiras tentativas do instrumento mediam durante a transição de opacidade do painel; não se alterou a animação do produto para fazer o teste passar. Os resultados consolidados antes da alteração estão em before.log e before/medicoes.json, com capturas correspondentes. A comparação usa cores computadas e luminância sRGB linearizada, sem arredondar o contraste para decidir a aprovação.

## Alteração

Antes: .alt-metrics small com font-size:10px e color:#758681.

Depois: font-size:14px, line-height:1.4 e color:#48615D. O tom já pertence à identidade do aplicativo; não foi introduzida outra paleta. display:block e toda a estrutura dos indicadores permanecem.

Resultado medido: 14 px e contraste mínimo **6,680486:1** nas duas áreas e nas três resoluções. A ampliação e o espaçamento dão mais presença aos rótulos, enquanto os valores conservam suas dimensões/peso e a hierarquia existente. O objetivo é leitura, sem modificar o significado dos indicadores ou esconder conteúdo.

A referência AM19 não congelava styles.css entre seus arquivos selecionados. Não foi necessário alterar ou afrouxar seu teste de preservação. VERSAO_INT04.json registra o hash da folha-base, o hash final e o critério aplicado; o manifesto do pacote compara todos os 719 arquivos-base e confirma que a única alteração anterior à documentação/teste novos é styles.css. Referências de prioridade e INT01/02/03 permanecem intactas.

## Validação

atelier/tests/browser_int04.py é o teste funcional novo: lê o estilo real no navegador por HTTP, calcula contraste, verifica o tamanho de fonte, largura disponível e separação entre rótulo e valor. Testa as duas áreas em três resoluções, com 24 rótulos medidos. Compara também estado de cálculo e bytes de todos os JSON temporários antes/depois, sem simular de novo ou registrar decisões. Não é teste textual que espelha uma declaração CSS.

O modo INT04_EXPECT_BEFORE=1 verifica a reprodução da fonte de 10 px e contraste abaixo de 4,5. O modo normal exige >=14 px e >=4,5:1, sem corte horizontal do rótulo ou sobreposição com o valor e sem overflow horizontal do documento. Sem exceções JavaScript não tratadas nos fluxos. Capturas antes/depois e medicoes.json acompanham a entrega.

Regressão completa: **732 testes aprovados, zero falhas e dez subtestes aprovados**. A contagem não aumentou porque o novo teste é um roteiro de navegador, executado separadamente. Warning de depreciação do plugin AnyIO, sem falha funcional. Não houve exclusão, desativação ou mudança de testes existentes para obter aprovação.

Modo Banca HTTP real, seis etapas, justificativa, registro e relatório passaram nas três resoluções. Gráficos, ampliação e exportações passaram nas três resoluções. AM15 verificou foco/enquadramento com 1/5/9/16/50 postos em cada resolução, incluindo os controles de foco por teclado; os rótulos do mapa e sua geometria não foram alterados.

Uma execução inicial do runner AM15, em paralelo com outras validações, falhou no enquadramento de 50 postos em 1280x720 (limite inferior medido 441,79 frente a 371,30). O log foi preservado como browser-am15-initial.log. A base INT03 executada separadamente passou nos 15 casos, e a versão atual reexecutada separadamente também passou nos 15. Não houve alteração de mapa, script AM15 ou asserções para obter essa repetição. A causa da ocorrência intermitente não foi demonstrada; ela fica registrada para monitoramento na verificação final, sem atribuí-la ao ajuste de rótulos nem declarar um defeito de mapa corrigido nesta etapa.

Os três experimentos oficiais permaneceram iguais: A com SLA nominal/incidente/resposta 100/40/100%, custo total da decisão R$12.113,00 e economia líquida R$4.103,68; B e C conforme banca.log. Nenhum número de referência foi ajustado. Os testes de importação INT01, precisão INT02 e biblioteca INT03 permanecem na regressão.

Comandos: python -m pytest tests contract_tests atelier/tests -q -p no:cacheprovider; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_int04; python -m atelier.tests.browser_am15; python -m atelier.tests.browser_acabamento_final; python docs/AM19/evidencias/actual_http_browser.py. Roteiros de navegador requerem Playwright/Chromium no Linux; não são dependências novas do aplicativo principal.

## Entrega e limites

ZIP completo atualizado, patch reproduzível sobre INT03, relatório, continuidade, medições, logs e comparação antes/depois. O aplicador confere a base e cria outra pasta, sem modificar a origem. O ZIP é extraído; patch aplicado sobre base limpa e comparação de hashes confirmam os mesmos arquivos. Testes da distribuição e medição de navegador são executados na extração; os arquivos publicados no GitHub são recuperados e comparados aos locais antes de declarar conclusão.

Este resultado é localizado: não certifica acessibilidade integral, contraste de todos os componentes, experiência de pessoas com deficiência ou legibilidade em qualquer projetor. Windows, BAT, escala de tela e projetor não foram validados nativamente. Cores e fontes devem ser conferidas nas condições reais da apresentação.

Os quatro achados INT01–INT04 identificados na auditoria AM22 receberam etapas próprias de correção. Isso não substitui uma verificação final da combinação das versões. Recomendo uma rodada final focada nesses contratos e um ensaio real no Windows/projetor, sem iniciar novas funcionalidades, redesenho ou reorganização ampla como substituto da homologação. As pendências históricas AM18/20/21 e a calibração industrial não foram resolvidas por uma alteração de tipografia.

Extraia o aplicativo em uma pasta nova e preserve versões e projetos anteriores. A versão INT03 continua no GitHub como recuperação. Não se exige aplicar patch se for utilizado o ZIP completo.
