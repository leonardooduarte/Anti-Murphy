# Prioridade opcional — correção exclusiva sobre AM19

Base 6f6c13501a787113edaf062a32639445240d52a9, branch correcao-am19-contratos. Nova branch correcao-prioridade-opcional. Checkpoint b7d7459 registra a correção e seus testes. Não foi utilizada base antiga.

## Reprodução

Na AM19, um pedido sem prioridade é válido no backend. normalizedModel aplicava Number(undefined), produzindo NaN e serializando prioridade:null. A reaplicação era recusada com prioridade inválida. before.log reproduz a função original do commit solicitado e a validação posterior. Não depende de uma alteração do motor.

## Contrato e implementação

Campo ausente ou undefined é omitido. Campo em branco ou só espaços no editor é omitido quando o usuário aplica, permitindo retirar uma prioridade opcional. Inteiros explícitos, incluindo zero e negativos, permanecem com seu valor. Strings decimais válidas são convertidas em inteiro numérico, preservando a convenção do editor; exemplos 0, -2 e 1e2. Não se introduziu piso ou prioridade padrão no frontend.

null explícito, booleanos, objetos, arrays, frações, textos inválidos e valores não finitos são rejeitados com mensagem antes da requisição. Representações hexadecimais não são tratadas como prioridades decimais. O handler do campo conserva o texto vazio em vez de convertê-lo silenciosamente em zero; badInput é conservado como inválido para o normalizador rejeitar. O backend e seus contratos de importação direta não foram alterados: null explícito ou prioridade vazia em um JSON importado continuam submetidos à validação existente. O campo vazio no editor é uma ação de remoção do campo opcional, não investimento zero nem prioridade zero.

Produção alterada apenas em atelier/web/app.js: handler do editor e normalizedModel. A renderização, CSS, abertura, motor, seeds, fórmulas econômicas, registros e dados-base não mudaram. Não houve avanço para outros achados.

O teste de preservação visual da AM19 congelava também app.js. A referência original docs/AM19/base-reference.json permanece intacta; VERSAO_PRIORIDADE.json declara o hash original e o hash desta alteração autorizada. O teste confere a ligação dos dois e continua verificando engine e demais arquivos originais. Não foi desativado nem trocado por aprovação incondicional.

## Validação

577 testes aprovados, zero falhas, dez subtestes aprovados. São 21 novos casos de ausência, campo vazio, inteiros explícitos e entradas inválidas; os modelos normalizados válidos também são verificados pelo validador Python. Browser HTTP real em 1280x720,1366x768,1920x1080: pedido sem prioridade reaplicado, zero explícito preservado, remoção do campo ao limpar, fração recusada sem POST nem substituição do modelo salvo, sem erros JavaScript nos fluxos. Valores não finitos numéricos também são protegidos por Number.isFinite no código; as strings NaN/Infinity integram os casos automatizados.

Três experimentos oficiais preservados: SLA 100/40/100%, custo da decisão R$12.113,00, economia líquida R$4.103,68. Gráficos, ampliação e exportações passaram nas três resoluções. Modo Banca HTTP real, justificativa, registro e relatório passaram nas três resoluções. Logs acompanham a entrega. Não houve homologação nativa no Windows/BAT/projetor. As limitações de runners históricos documentadas na AM19 permanecem.

## Entrega e continuidade

ZIP completo, patch sobre a AM19 exata, relatório e continuidade na nova branch. O patch confere todos os hashes e cria pasta nova; não modifica a base. ZIP extraído e patch aplicado são comparados por SHA-256. Testes direcionados são executados no pacote extraído. Os arquivos publicados no GitHub são recuperados e conferidos antes da conclusão.

Extraia em pasta nova e execute INICIAR_ANTI_MURPHY.bat. Preserve a instalação anterior e seus projetos. Próximas pendências permanecem independentes: recuperação de arquivos inválidos, Host/Origin e avaliação dos componentes visuais novos. Nenhuma dessas correções foi iniciada aqui.

Reprodução em cópia: python -m pytest tests contract_tests atelier/tests -q; python -m pytest tests/test_optional_priority.py tests/test_am19_distribution.py -q; python -m atelier.tests.browser_optional_priority; python -m atelier.tests.validacao_experimentos_banca. Testes JavaScript usam Node e navegador usa Playwright/Chromium no Linux; o aplicativo principal não recebeu dependências novas.
