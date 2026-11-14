# Verificação final conjunta — INT04

Data de referência: 14/11/2026, contexto do usuário America/Sao_Paulo.

## Resultado e limite do parecer

A versão combinada INT04 passou nas verificações executadas neste Linux: regressão completa, contratos INT01/02/03/04 por navegador, economia arquivada, gráficos/exportações, Modo Banca e repetição do mapa. Nenhum código do aplicativo foi alterado nesta etapa.

Não há, nesta rodada, nova falha funcional reproduzida que justifique outra correção imediata no aplicativo. Isso não é garantia de ausência de defeitos, homologação industrial, auditoria completa de acessibilidade nem validação nativa no Windows/projetor. O próximo passo é executar o kit e o roteiro no computador real da apresentação, não começar funcionalidades ou redesenho por padrão.

## Base realmente examinada

Aplicativo INT04, branch correcao-int04-legibilidade, commit **ac852d85e454c4b5df37f9f57d1c749aed045189**. ZIP SHA-256 **111b1ea20f15a73618ee2ae21a8b9ce390fc95f29f65a8efbe273ca798c72933**. A verificação começou por nova extração do ZIP entregue; os 748 arquivos originais conservaram seus hashes após os ensaios. base-manifest.json contém o inventário.

A branch verificacao-final-int04 contém somente documentação, evidências e ferramentas de verificação fora do aplicativo. Checkpoint 5d8f5e4 registra escopo/base. O aplicativo para baixar continua sendo a INT04; não foi criado outro ZIP de aplicativo idêntico nem patch vazio. As versões anteriores permanecem preservadas no GitHub. Sem agentes paralelos.

## Validações executadas

- Regressão completa na extração: **732 testes aprovados, zero falhas, dez subtestes**. Warning de depreciação do plugin AnyIO, sem falha funcional. Nenhum teste foi excluído, desativado ou modificado no aplicativo.
- Três experimentos oficiais aprovados. A: SLA 100/40/100%, custo total da decisão R$12.113,00 e economia líquida R$4.103,68. B/C mantiveram os resultados registrados em banca.log.
- INT01: exportação/importação de EDD/SPT/FIFO entre projetos, reabertura, ausência legada e valores inválidos, nas três resoluções.
- INT02: horários precisos da auditoria nos três cenários, sinais e classificação, relatório pop-up/download, avisos de legado/indisponível, nas três resoluções.
- INT03: coleção mista, nomes escapados, API anterior em lista, comparação/gravação com arquivos inválidos preservados, isolamento de projetos e releitura, nas três resoluções.
- INT04: 24 rótulos nas duas áreas e três resoluções, 14 px e contraste mínimo 6,680486:1, sem corte/sobreposição nos alvos medidos.
- AM08: componentes econômicos arquivados e legado sem investimento presumido zero, nas três resoluções.
- Gráficos/ampliação/exportações e Modo Banca HTTP real, seis etapas, justificativa, registro e relatório, nas três resoluções.
- Sete roteiros de aceitação foram executados sequencialmente; contract-results.json registra seus resultados. Os testes do mapa vieram depois deles e da regressão. As resoluções foram 1280x720, 1366x768 e 1920x1080.

Os roteiros de navegador usam dados sintéticos temporários. Não constituem um ensaio realizado no computador Windows do usuário. O roteiro INT02 mantém as injeções de transporte de legado/desconhecido documentadas na sua etapa; casos normais usam HTTP/DES reais.

## Ocorrência anterior do mapa de 50 postos

A entrega INT04 registrou uma falha inicial do runner AM15 em 50 postos/1280x720 e repetições isoladas aprovadas. Nesta verificação, o runner original foi executado sem alteração e aprovou os 15 casos (1/5/9/16/50 postos em três resoluções).

Foi acrescentado apenas um instrumento externo de investigação, map_investigation.py, sem modificar o mapa ou o runner original. Ele repete o caso de 50 postos cinco vezes por resolução: **15 repetições adicionais**. Registra a leitura separada usada pelo teste original, uma leitura atômica das duas geometrias no mesmo instante e outra após 300 ms, incluindo scroll, viewBox, tamanho da fonte e identidade da execução.

Todas as 15 repetições adicionais mantiveram foco legível, execução inalterada e ausência de exceções JavaScript. Nenhum limite inferior foi excedido na leitura separada, na leitura atômica ou após 300 ms. As margens finais aproximadas foram 26,50 px em 1280x720, 30,62 px em 1366x768 e 73,60 px em 1920x1080, abaixo da legenda. Dados completos em map-investigation.json e map-summary.json.

A ocorrência anterior **não foi reproduzida**; sua causa **não foi demonstrada**. Não é correto declarar que um bug de mapa foi corrigido ou que a falha inicial era certamente apenas do instrumento. Não houve mudança de asserções para passar o teste original. A ocorrência fica como ponto de monitoramento no ensaio real, especialmente ao mudar foco, escala do Windows e resolução do projetor.

## Kit de ensaio no Windows

VERIFICAR_AMBIENTE.py usa apenas biblioteca padrão, confere os 748 hashes da INT04 e cria uma cópia temporária sem workspace/projetos do usuário. Nessa cópia, inicia o servidor sem pacotes extras, confere recursos/API e referência de SLA, verifica round-trip da regra de despacho, coleção com arquivo inválido e reabertura, horário preciso do ciclo curto e os três experimentos oficiais. Os processos iniciados pelo verificador são encerrados; a pasta de entrada não é alterada.

A ferramenta foi executada e aprovada aqui no Linux. diagnostico-linux-final.json registra sistema Linux, resultado de verificações automáticas e windows_automatizado_aprovado=null. O campo só é preenchido ao executar no Windows. BAT original, interface visual e projetor continuam explicitamente false, mesmo que a verificação automática passe. Isso evita transformar uma checagem de API em homologação visual inexistente.

VERIFICAR_WINDOWS.bat é uma conveniência para arrastar a pasta recém-extraída sobre o verificador. Ele também não substitui o teste de INICIAR_ANTI_MURPHY.bat do aplicativo. Nenhum dos dois BATs foi executado nativamente aqui. O roteiro manual e a ficha incluem essa etapa.

O kit completo deve ser extraído mantendo verificador, manifesto e MODELO_CICLO_CURTO.json juntos. Use uma pasta nova do aplicativo, como indicado no roteiro. Uma pasta com arquivos já modificados pode ser recusada pelo manifesto; isso é proteção de identificação da versão, não autorização para sobrescrever projetos.

## O que ainda precisa ser feito no computador real

ROTEIRO_WINDOWS_PROJETOR.md detalha 16 verificações Windows e quatro de projetor. FICHA_WINDOWS_PROJETOR.csv e AMBIENTE_WINDOWS_PROJETOR.json começam como NÃO EXECUTADO, sem dados inventados.

São necessários: executar o verificador no Windows; testar o BAT original e abertura; usar as oito áreas; salvar/fechar/reabrir; importar/exportar regra; comparar experiências e guardar com aviso de arquivo inválido na cópia de ensaio; conferir curto ciclo, dados desatualizados, exportações, registro/histórico e PDF; percorrer o Modo Banca; repetir foco/planta inteira; verificar leitura na posição do público com resolução e escala reais; medir o tempo do roteiro da apresentação.

Para concluir essa parte, são esperados o resultado_ambiente_*.json gerado no Windows, ficha preenchida com observações reais e evidências de falhas/dificuldade de leitura. Não há acesso direto ao PC Windows ou ao projetor nesta execução Linux. O resultado da etapa é, portanto, verificação Linux concluída e homologação Windows/projetor pendente de execução real.

## Entrega e continuidade

Relatório, roteiro, ficha, ferramenta, exemplo, manifesto, scripts de investigação, logs e capturas selecionadas em ZIP próprio. Esse ZIP é do kit de verificação, não de uma nova versão do aplicativo. O pacote é extraído e conferido por hashes; os arquivos publicados no GitHub são recuperados e comparados antes da conclusão. O aplicativo INT04 permanece no seu link anterior.

Se o ensaio real passar, registrar a configuração/hardware como referência da banca e manter a INT04 aprovada como ponto de recuperação. Se falhar, reproduzir a falha específica antes de autorizar outra etapa pequena de correção. Não reabrir AM18/20/21 ou desenvolvimento amplo automaticamente; essas pendências de caminhos adicionais e validade industrial não foram resolvidas nem homologadas por esta verificação.
