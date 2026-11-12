# AM15 — legibilidade e enquadramento da fábrica

Base AM14, commit 5eb0e0db19a0a90c3d077d239e66ebdc4c3b067f. Branch correcao-am15-legibilidade.

## Problema e solução

A planta usava grade de quatro colunas em um canvas fixo para seis ou mais postos, aproximando cartões de largura 310 de centros separados por 300. O canvas também não reservava altura para plantas maiores. Textos eram reduzidos pela escala do SVG; várias regras antigas de CSS se sobrepunham e limitavam as fontes.

Para seis ou mais postos, a grade passa a três colunas com espaçamento vertical e altura proporcionais às linhas. A visão geral reserva margem inferior para o rodapé, evitando cobrir os últimos cartões. Plantas de um a cinco postos preservam as posições e o viewBox geral anterior. O foco usa uma janela de 400x320 unidades centrada no posto, em vez de ampliar a planta inteira com origem aproximada. Zoom, retorno à planta e seleção continuam disponíveis. O enquadramento do Modo Banca permanece em seu fluxo próprio.

Fontes principais e contraste existente foram preservados na paleta e ampliados com regras locais ao mapa. Em visão compacta, telemetria, nomes descritivos e detalhes que não cabem deixam de disputar o desenho. IDs longos podem ser abreviados visualmente na visão geral, mantendo o valor completo no foco, no inspetor e na lista textual. Isso não altera identificadores do modelo ou resultados.

A nova Leitura dos postos oferece nomes completos, estado, quantidade processando e fila em texto HTML. Usa fontes de 14px nos nomes e 13px nos estados, com botões nativos acessíveis por teclado para focar no mapa. Abre por padrão acima de cinco postos e pode ser recolhida; sua rolagem interna limita a altura. A lista acompanha o mesmo instante do replay e identifica seu cenário; em A/B, declara que mostra A sem intervenção. Não agrega os dois cenários nem cria cálculos de PCP. Durante o Modo Banca, a lista é ocultada para preservar a apresentação guiada.

## Evidências

No modelo de nove postos a 1366x768, o identificador SVG medido com tamanho computado multiplicado pela escala de getScreenCTM passou de aproximadamente 8,70px na AM14 para 11,89px na visão geral. No foco, chega a aproximadamente 24,96px. A leitura HTML mantém nomes em 14px independentemente da escala da planta. Logs registram medições nas três resoluções. É tamanho CSS efetivo, não medição física de projetor nem prova universal de legibilidade.

A visão geral de 16 ou 50 postos continua reduzindo os desenhos para caber. Não se promete texto grande em todos os cartões simultaneamente: foco e leitura textual são os caminhos de detalhe. Nomes extensos são truncados no desenho, mas permanecem completos nos outros canais. O layout é lógico, sem validação de distâncias, transporte ou organização física industrial.

## Validação

548 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados. Oito testes novos verificam os limites e a ausência de interseção dos halos para 1,3,4,5,6,9,16 e 50 postos. Nenhum teste antigo foi alterado ou excluído. As cinco falhas preservadas continuam em operation_ui, restauracao_acesso (dois) e v31_editorial (dois), detalhadas em regression.log.

Browser real: 15 combinações de modelo/resolução, com 1,5,9,16 e 50 postos em 1280x720,1366x768,1920x1080. Verifica presença de todos os postos, lista completa, foco por teclado, retorno à planta, IDs em foco com tamanho efetivo de pelo menos 12px nesses ensaios e cartões fora da área do rodapé. Os modelos de layout usam um roteiro simples e postos adicionais para inspecionar a geometria; não representam uma calibração fabril de 50 postos.

Três experimentos oficiais aprovados sem mudar resultados: SLA 100/40/100%, decisão R$12.113,00, economia R$4.103,68. O fluxo HTTP real anterior do Modo Banca passou nas três resoluções, com justificativa, comparação, registro e relatório. Os testes existentes de gráficos, legendas, ampliação e exportações passaram nas três resoluções, sem alterar as asserções.

## Arquivos e preservação

Produção alterada apenas em atelier/web/app.js e atelier/web/acabamento_banca_final.css: posições para plantas grandes, altura/visão geral/foco, leitura dos postos, etiquetas e renderização. Novos testes test_am15_layout.py e browser_am15.py. Motor, replay numérico, fórmulas econômicas, sementes, projetos, registros, abertura, marcas e demais correções preservados. O trabalho mantém equipamentos ilustrados e paleta; não é reconstrução do design.

Windows e projetor continuam pendentes de validação local. Não foi feita homologação WCAG integral nem teste de leitor de tela. A lista textual e os botões por teclado ampliam o acesso, sem garantir acessibilidade completa. O custo extra da lista usa os índices existentes do replay e atualiza linhas quando seus estados mudam; não é um novo benchmark de FPS.

## Reprodução e entrega

Em cópia: python -m pytest tests contract_tests atelier/tests -q; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_am15. Os testes JavaScript exigem Node e o navegador usa Playwright/Chromium no Linux. Para repetir a medição anterior, defina AM15_BASE_WEB como a pasta atelier/web extraída da AM14; essa medição é opcional e não impede executar os testes da versão atual. O script adicional do fluxo Banca e seu log acompanham as evidências. Screenshots mostram plantas, foco e leitura dos postos.

ZIP e patch são extraídos e comparados por SHA-256 sobre a AM14 exata. O aplicador cria uma pasta nova, sem modificar a origem. Testes direcionados são reexecutados no ZIP extraído e os arquivos do GitHub são recuperados para conferência antes da entrega. Instale o ZIP completo em pasta nova e guarde projetos anteriores.

Próxima fase recomendada: estabilização, tratamento dos cinco contratos antigos (AM19) e nova auditoria integrada. Rever complementos de recuperação, prioridade opcional no editor e validação local de Host/Origin antes de encerrar a lista de achados. AM18 é manutenção gradual; caminhos históricos AM20/21 exigem decisão explícita de uso. A versão não deve ser declarada final para a banca sem o ensaio no Windows/projetor.
