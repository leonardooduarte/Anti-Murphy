# INT-02 — precisão da auditoria por pedido

## Base e escopo

Base obrigatória: INT01-2026.1, commit 1bbe141ee4ee5d52aecbe109a8b2bb53d5088c92, branch correcao-int01-importacao-regra. Nova branch: correcao-int02-precisao-auditoria. Checkpoint b8f8338. Sem agentes paralelos. Não foi usado ZIP antigo nem reconstruído o aplicativo.

Correção exclusiva dos horários, folgas, atrasos e sua classificação/apresentação na auditoria por pedido e tabela correspondente do relatório. Nenhuma fórmula ou função do motor DES foi alterada. Permanecem pendentes INT-03 (biblioteca com arquivo inválido), INT-04 (contraste), Windows/BAT/projetor e os caminhos históricos documentados. A INT-01 e demais versões anteriores são preservadas.

## Reprodução e referência independente

before.log registra a operação CURTA: ciclo 0,06 min (0,001 h antes da variação sintética), prazo 0,0005 h e multa 10.000/h. O motor calcula conclusão 0,0010359130029347337 h, atraso 0,0005359130029347337 h e multa apresentada R$5,36. A auditoria anterior lia Conclusão (h)=0,00 e publicava folga +0,001 h e atraso zero. O erro estava no consumidor da informação, não no makespan ou no throughput do motor.

A referência é prazo menos conclusão precisa; o atraso é a diferença positiva em relação ao prazo. Os casos unitários usam Decimal para conferir diferenças e sinais em ciclos curtos e proximidade do prazo. before-tests.log contém os 24 casos do novo contrato executados contra uma extração INT01 intacta: todos falharam; isso não significa 24 defeitos independentes, pois parte das asserções verifica a nova identificação da origem dos dados. Uma primeira preparação do ensaio real não selecionava uma resposta quando não havia líder elegível; a preparação foi ajustada para examinar conscientemente uma alternativa existente, sem alterar o motor ou a seleção automática.

## Contrato e implementação

atelier/technical_audit.py, summarize_audit:

- Usa completion_h quando presente e válido. Só utiliza Conclusão (h) se a chave precisa estiver ausente, compatibilizando dados legados.
- Conserva finish_h e slack_h sem arredondar antes de comparar ou classificar. slack_h = due_h − finish_h.
- Usa lateness_h preciso quando presente. Na sua ausência deriva max(0, −slack_h), identificando essa origem; não usa o atraso arredondado como prova de atraso nulo.
- Campos precisos explicitamente inválidos (null, booleano, texto inválido, não finitos ou duração negativa) não são substituídos silenciosamente pelos valores arredondados. Valores indisponíveis ficam null e a classificação fica desconhecida.
- Acrescenta timing_source (precise/legacy_rounded/unavailable), lateness_source (precise/derived/unavailable) e is_late. São campos aditivos; os campos existentes continuam numéricos ou null.
- Conserva Status do motor, quando disponível, inclusive a tolerância numérica que já existia no DES. Não acrescenta outro piso nem muda o critério de SLA. Se o status não existir em um dado legado, a classificação deriva do atraso disponível.

O fallback legado conserva o que foi publicado, mas não recupera precisão perdida. Por isso recebe identificação explícita e aviso. Um status legado conhecido pode refletir um atraso que seu horário arredondado não consegue resolver; o aviso não certifica os horários legados como exatos. Não há regravação de registros antigos.

atelier/web/app.js:

- auditTime aplica apresentação de seis algarismos significativos a horários não nulos menores que 0,01 h; abaixo de 1e-6 h usa notação científica de quatro algarismos. São regras de apresentação, não limites físicos ou alterações dos dados numéricos da API. Valores usuais conservam dashH; null e não finitos mostram travessão.
- auditSlackStatus e dashAudit usam a classificação por pedido e os valores não arredondados. Um valor negativo dentro da tolerância já adotada pelo motor é identificado como no prazo com tolerância; indisponíveis são Não calculado. Contadores não classificam desconhecidos como no prazo.
- O painel informa horários legados arredondados e quantidade de pedidos não calculados, quando aplicável.
- generateReport usa o mesmo formato e classificação na tabela Impacto por pedido, preservando sinais e tempos curtos tanto no pop-up quanto no download HTML. Os formatos de outros cartões e gráficos não foram redesenhados nesta etapa. Não se afirma que todo formatador do programa mudou.

A função _num passa também a tratar OverflowError como valor indisponível. Multas, custos, investimentos e fórmulas econômicas não foram recalculados nem alterados pela auditoria. O diagnóstico de gargalo e demais seções continuam com seus contratos anteriores.

## Testes e arquivos alterados

24 novos casos em tests/test_int02_audit_precision.py: diferenças exatas com Decimal; conclusão antes/no/depois do prazo; tolerância e classificação do motor; fallback apenas por ausência; zero preciso; seis conclusões precisas inválidas; seis atrasos precisos inválidos; origem legada; cenário real com máquinas paralelas, falha e manutenção temporal. O ensaio real confere os três cenários, igualdade de métricas e arquivos, e impede execução do motor durante a leitura da auditoria.

atelier/tests/test_technical_audit.py deixa de cristalizar a comparação com conclusão arredondada e passa a conferir conclusão precisa, diferença prazo−conclusão, atraso e classificação do resultado DES. É atualização do contrato que reproduzia o defeito; o teste ficou mais específico e não foi apagado ou desativado.

VERSAO_INT02.json e tests/test_am19_distribution.py acrescentam um elo à cadeia de hashes da alteração autorizada em app.js. Referência AM19, VERSAO_PRIORIDADE.json e VERSAO_INT01.json permanecem intactas; engine e demais fontes visuais continuam conferidas. Não foi criada aprovação incondicional de arquivos.

atelier/tests/browser_int02.py: HTTP real e DES real em 1280x720, 1366x768 e 1920x1080. Confere os três cenários, sinais/valores apresentados, precisão JSON, relatório em pop-up e download. Só os avisos de dados legados/indisponíveis usam respostas de transporte controladas; a compatibilidade numérica é coberta diretamente no backend. Memória e todos os JSON do diretório de teste permanecem intactos. Sem erros JavaScript não tratados ou overflow horizontal do documento.

A primeira asserção do ensaio de navegador usava tolerância relativa mais estreita que o arredondamento de seis algarismos exibidos. browser-initial.log foi preservado. O instrumento passou a conferir igualdade com arredondamento Decimal independente de seis algarismos, sem mudar os valores precisos, a apresentação do produto ou encobrir uma divergência numérica. O teste de API e os testes unitários continuam conferindo os valores não arredondados.

Uma sondagem Node externa (format-probe.js/log) executa os helpers reais: 12 verificações de sinal, zero legítimo, indisponível, valores usuais, tempos submicroscópicos em notação científica e classificação com tolerância. Não altera a contagem da regressão.

## Resultados finais

706 testes aprovados, zero falhas, dez subtestes. Warning de depreciação do plugin AnyIO, sem falha funcional. Não houve exclusão ou desativação de testes para obter aprovação.

Os três experimentos oficiais permaneceram iguais: A com SLA nominal/incidente/resposta 100/40/100%, custo total da decisão R$12.113,00 e economia líquida R$4.103,68; B e C conforme banca.log. Não houve ajuste artificial de números de referência.

Importação INT-01 foi novamente conferida nas três resoluções: EDD/SPT/FIFO, download/upload em outro projeto, legado, inválidos e reabertura. Modo Banca com justificativa, registro e relatório, além de gráficos/ampliação/exportações, também passou nas três resoluções. Dados locais e motor foram preservados.

Depois, ZIP extraído e patch aplicado são comparados por SHA-256; testes direcionados rodam na extração; arquivos publicados no GitHub são recuperados e comparados antes de concluir a entrega.

Comandos: python -m pytest tests contract_tests atelier/tests -q -p no:cacheprovider; python -m pytest tests/test_int02_audit_precision.py atelier/tests/test_technical_audit.py tests/test_am19_distribution.py -q -p no:cacheprovider; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_int02; python -m atelier.tests.browser_int01; python -m atelier.tests.browser_acabamento_final; python docs/AM19/evidencias/actual_http_browser.py. Chromium/Playwright são dependências de desenvolvimento no Linux, não requisitos novos do aplicativo principal.

## Entrega e continuidade

ZIP completo atualizado, patch sobre os 669 arquivos INT01, relatório, continuidade, logs e evidências. O aplicador exige a base correta e cria uma pasta nova, sem alterar a origem. As versões, ZIPs e auditoria anteriores continuam no GitHub. Extraia em pasta nova; preserve sua instalação e projetos antes de experimentar a atualização.

Não foi realizada validação nativa do Windows, BAT ou projetor, nem homologação industrial. A precisão dos horários depende dos dados do motor; resultados legados sem precisão não são reconstruídos por aproximação oculta. Próxima etapa recomendada: INT-03, leitura resiliente da biblioteca, exclusivamente sobre esta versão ou sucessora imediata confirmada.
