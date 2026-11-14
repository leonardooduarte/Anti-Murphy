# AM22 — validação local de Host e Origin

## Base e escopo

Base exata e52b2456043ec53d6be00f938032f8907f35c955, RECUPERACAO-2026.1 sobre PRIORIDADE/AM19. Branch correcao-am22-host-origin. Checkpoints 6dbca22 e db66668 (validação ASCII). Trabalhado sem agentes paralelos. Único arquivo de produção alterado: atelier/server.py. Os recursos visuais, editor, DES, fórmulas, decisões, relatórios e dados-base permanecem idênticos. Não foi iniciada auditoria integrada ou correção de outro achado.

## Reprodução anterior à alteração

before.log demonstra, com servidor HTTP real em diretório temporário, GET /api/state com Host external.example:porta retornando 200 e POST /api/run com Host e Origin externos coincidentes retornando 200 e alterando min_sla de 80 para 71. O código anterior verificava apenas a igualdade entre Origin e Host no POST; GET não verificava nenhum dos dois. O bind em 127.0.0.1 não constituía validação da autoridade solicitada.

after.log repete as mesmas requisições na versão corrigida: ambas retornam 403 e a meta permanece 80.

Os primeiros 58 casos automatizados produziram 44 falhas e 14 aprovações na base original; before-tests.log registra a reprodução. Depois foram adicionados nove casos de sintaxe/porta padrão, totalizando 67 novos testes. Foi demonstrada a aceitação indevida dos cabeçalhos por conexão HTTP local; não foi executado um ataque completo com domínio público e mudança real de DNS.

## Contrato implementado

_local_authority aceita somente localhost, 127.0.0.1 e [::1], com a porta efetiva do servidor. Não faz resolução DNS nem confia em Forwarded/X-Forwarded-Host. Nomes externos que resolvam para loopback continuam inválidos. Porta omitida equivale à porta HTTP 80 e só é aceita quando o servidor efetivamente está nessa porta. Outros endereços do bloco 127/8, nomes com ponto final, userinfo, listas, caminhos, sufixos externos e sintaxe inválida são recusados. Maiúsculas em localhost são normalizadas; a comparação é estritamente ASCII para não aceitar caracteres Unicode semelhantes.

Handler._allow_local_request é chamado no início de GET e POST, antes de rotas, leitura de corpo, acesso ao Studio, arquivos estáticos ou exportações. Host ausente, vazio, duplicado ou fora da lista retorna 403. Requisições em formato de URL absoluta também são recusadas; a aplicação usa caminhos locais normais.

Quando Origin está presente, deve existir exatamente um cabeçalho com origem HTTP local, mesma autoridade e porta do Host. null, vazio, esquema diferente, credenciais, caminho, consulta, fragmento e outra porta são recusados com 403. localhost e 127.0.0.1 são origens distintas, como no navegador. Origin ausente continua permitido com Host local válido, preservando clientes locais que não enviam esse cabeçalho; a ausência não é tratada como origem externa nem autenticação. Navegadores serializam origens sem barra final, conforme o contrato aceito. O serviço não é um servidor HTTPS/proxy público.

O lançamento principal continua escutando em 127.0.0.1 com porta dinâmica ou configurada. A aceitação do cabeçalho [::1] não muda o bind nem comprova uma conexão IPv6 nativa. Não foram acrescentadas dependências, autenticação, CORS permissivo ou mudanças de navegação. Esta proteção não identifica usuários nem impede um processo local de enviar requisições locais autorizadas.

## Testes e resultados

67 novos casos em tests/test_am22_http_boundary.py, usando servidor HTTP real, Studio isolado e spy para verificar ausência de chamadas ao serviço nas recusas. Cobrem Host externo com Origin coincidente, GET/POST, Host ausente/inválido/duplicado, Origin inválido/duplicado, portas, aliases locais, clientes sem Origin, navegador com Origin correspondente, arquivos estáticos e exportações. O checkpoint é comparado byte a byte nas recusas de Host; ações locais válidas continuam alterando e persistindo os parâmetros. Os nove casos diretos conferem a sintaxe estrita e a porta HTTP padrão.

atelier/tests/browser_am22.py executa acesso real por 127.0.0.1 e localhost nas resoluções 1280x720, 1366x768 e 1920x1080: abertura, carregamento do mapa, aplicação do modelo por POST, exportação JSON e painéis. Sem erros JavaScript nem respostas 403 nos fluxos permitidos. Seis capturas acompanham a entrega.

Regressão completa: 664 testes aprovados, zero falhas, dez subtestes. Nenhum teste anterior foi apagado, desativado ou relaxado. Os três experimentos oficiais preservaram resultados: A com SLA 100/40/100%, custo da decisão R$12.113,00 e economia líquida R$4.103,68; B e C conforme log. Modo Banca HTTP real (justificativa, registro e relatório) e gráficos/exportações passaram nas três resoluções. O warning AnyIO é de depreciação do plugin de teste.

Comandos: python -m pytest tests contract_tests atelier/tests -q; python -m pytest tests/test_am22_http_boundary.py tests/test_am19_distribution.py -q; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_am22; python -m atelier.tests.browser_acabamento_final; python docs/AM19/evidencias/actual_http_browser.py. Browser requer Playwright/Chromium no ambiente de teste Linux, não no aplicativo distribuído.

## Entrega e limitações

ZIP completo, patch reproduzível sobre e52b245, relatório, logs, continuidade e hashes. Patch confere a base e cria outra pasta sem modificar a origem. ZIP extraído e resultado do patch são comparados por SHA-256; testes direcionados são executados na extração. Os arquivos publicados são recuperados do GitHub e comparados à versão local antes da conclusão.

Windows, BAT e projetor não foram validados nativamente. A auditoria integrada final e avaliação dos componentes visuais continuam pendentes. Limitações históricas e de recuperação já documentadas permanecem; não se promete segurança universal, recuperação física de dados ou homologação de caminhos históricos adicionais nesta etapa.
