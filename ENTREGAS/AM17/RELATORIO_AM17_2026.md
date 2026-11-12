# Anti-Murphy — AM17: dimensão do cálculo e consultas do replay

Versão AM17-2026.1. Base obrigatória: complemento AM04 sobre AM10,
commit `3e4bf47892be46cc3640ab2baee34a44faed4248`.
Branch: `correcao-am17-desempenho`.

## Mudanças percebidas pelo usuário

O editor apresenta um cartão integrado à identidade visual: operações por
cenário, unidades e postos. A contagem acompanha a edição, sem executar
simulações. Ao exceder o limite por cenário, mostra como reduzir o volume.
O servidor verifica também a soma dos cenários antes de calcular.

Um pedido excessivo não substitui o resultado anterior nem grava o modelo.
Projetos grandes já salvos podem ser abertos para edição sem simulação ou
regravação automática. A redução e aplicação explícita do modelo reabilitam
o cálculo. Abrir outro projeto dessa forma não muda o ponteiro persistido
até uma gravação autorizada pelo usuário; reiniciar pode voltar ao projeto
anterior. Os dados continuam preservados nos respectivos arquivos.

A fábrica virtual usa índices de consulta para evitar percorrer todo o
histórico de operações a cada atualização de posto. O diário de eventos é
ordenado uma vez por replay e consultado por busca binária.

## Reprodução antes/depois

Na base anterior, um JSON de 100.371 bytes com um posto, 2.500 unidades e
10.000 etapas por unidade passava pelas verificações do Studio. Uma chamada
interceptada a `execute` provou que seriam solicitadas **25 milhões de
operações por cenário**. A interceptação parou antes de executar o DES.
O caso extremo não foi simulado.

Depois, o mesmo pedido é recusado com explicação antes de `execute`: zero
chamadas ao motor, arquivos JSON e experimento anterior preservados.
O limite inclui o número de cenários, além da operação nominal. Os logs
`before.log` e `after.log` e o script `reproduce.py` estão nas evidências.

## Política de volume

O módulo novo `atelier/workload.py` centraliza limites desta versão local:

- 25.000 operações por cenário;
- 250.000 operações por análise, somando cenários.

São limites de recursos do aplicativo, não pisos de cálculo nem correções de
indicadores físicos. O DES independente não recebeu limites novos e suas
fórmulas não foram alteradas. A ampliação futura dessa política deve ser
acompanhada de medições e validação no computador de destino.

Para cada pedido, a contagem usa `max(1, round(quantidade × demanda)) × etapas`,
com o mesmo arredondamento por pedido do motor. A análise principal conta
nominal, incidente, regras, acréscimos, realocações elegíveis e reparo expresso.
Na fábrica padrão: 402 operações nominais, 19 cenários e 7.638 operações.

Nos ensaios, usam-se limites superiores conhecidos: sete durações, três
regras, seis pares de sementes, 16 cenários de estresse com demanda até 1,2,
ou todos os planos de capacidade AM10. Análises avançadas incluem as réplicas,
demanda até 1,6 e uma possível execução nominal para preencher o cache.
Isso pode ser conservador quando o cache já está preenchido. A filtragem
de metas, que usa resultados existentes, não é cobrada como nova simulação.

Todos os modos que simulam são verificados antes de criar configurações ou
preencher o cache nominal. Testes acompanham chamadas reais do DES nas 11
ferramentas para verificar que os limites declarados cobrem o trabalho.
Contadores e números de réplicas devem ser mantidos juntos em mudanças futuras.
Essa política não é um orçamento de tempo de CPU nem uma garantia universal
de memória, especialmente sob concorrência ou configurações extremas de
recursos. A submissão duplicada de Monte Carlo permanece no escopo AM16.

## Otimização do replay

`replayIndex` mantém índices por objeto de replay em `WeakMap`. Cada posto
possui intervalos de processamento e espera ordenados por início, com máximos
acumulados de término para interromper buscas que já não podem produzir
resultados. As operações retornam na mesma ordem original. Segmentos reais de
processamento, pausas, mudanças de recursos e intervalos semiabertos são
preservados. Busca para trás no tempo também funciona.

`recentReplayEvents` usa eventos previamente ordenados e busca binária para os
seis eventos mais recentes. Mantém o desempate por tipo e a tolerância temporal
de apresentação existente. Um replay novo recebe índice novo; objetos antigos
podem ser coletados sem um cache global que os retenha indefinidamente.
O índice assume o contrato de replay imutável que a interface já utiliza.
Em intervalos muito sobrepostos, a busca por máximos acumulados ainda pode
percorrer muitos itens; não se afirma complexidade logarítmica universal.

O Opportunity Engine também passou a construir somente os candidatos que
realmente vai avaliar. A lista, ordem, scores e fórmulas dos candidatos usados
permanecem iguais. Evita clonar previamente modelos que seriam descartados
pelo limite existente de candidatos.

## Medição de desempenho

Ensaio controlado em Node, 12.000 operações distribuídas em 12 postos, 3.600
consultas por repetição, mediana de cinco repetições:

| Medida | Base anterior | AM17 |
| --- | ---: | ---: |
| Consultas após aquecimento | 790,47 ms | 10,58 ms |
| Primeira consulta, incluindo construção do índice | 1,16 ms | 48,86 ms |
| Soma de verificação dos estados | 1.798.788 | 1.798.788 |

O ganho de aproximadamente 75 vezes refere-se **somente às consultas desse
ensaio após aquecimento**. Não mede FPS, velocidade total da aplicação, rede
ou desempenho no Windows. A construção do índice introduz um custo inicial
único, mostrado na tabela. Os scripts e cinco tempos individuais estão nas
evidências; resultados variam conforme máquina e carga.

Também foram executados cenários individuais limitados, em processos Python
separados, sem instrumentar o motor:

| Operações | Tempo medido | Pico RSS do processo Linux |
| --- | ---: | ---: |
| 400 | 0,0075 s | 14.336 KiB |
| 6.000 | 0,1433 s | 19.328 KiB |
| 25.000 | 0,4350 s | 35.328 KiB |

São cenários sintéticos simples, não uma homologação de todo arranjo possível.
RSS inclui o processo; não é memória incremental nem estimativa de Windows.

## Validação e preservação

- 510 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados.
- 37 casos novos: limites individuais e por análise, crescimento da demanda,
  candidatos/repetições, rejeição antes do motor, arquivos preservados,
  abertura/edição de projetos grandes e construção limitada de oportunidades.
- A referência independente do replay compara 960 estados e 160 consultas
  de eventos, incluindo retrocesso, empates, pausas, recursos e ordem das linhas.
- Três experimentos oficiais aprovados sem mudança de resultados:
  SLA nominal/incidente/resposta 100/40/100%; custo do incidente R$16.216,67;
  decisão da manutenção expressa R$12.113,00; economia líquida R$4.103,68;
  conclusão da manutenção 21,57530617980079 h e operador temporal
  19,973006391870044 h.
- Navegador HTTP real nas três resoluções: cartão de volume, edição sem
  recálculo, recusa sem perda, redução e aplicação, projeto salvo grande
  reaberto para edição, sem erros JavaScript nos fluxos exercitados.
- Testes anteriores de legendas, ampliação, gráficos e exportações passaram
  nas três resoluções. Modo Banca, justificativa, registro e relatório também.

As cinco falhas preservadas continuam em `test_operation_ui` (evidência),
`test_restauracao_acesso` (dois contratos históricos) e `test_v31_editorial`
(launcher/prévia). Não foram removidas nem ajustadas para esconder problemas.
Não se declara suíte totalmente verde; o detalhamento está no log de regressão.

Arquivos de produção alterados: `atelier/service.py`, `atelier/web/app.js`,
`atelier/web/index.html`, `atelier/web/integridade_final.css` e
`simulation/decisions.py`; módulo novo `atelier/workload.py`.
Testes novos: `tests/test_am17_workload.py`, `tests/test_am17_replay.py` e
`atelier/tests/browser_am17.py`.

Motor `engine.py`, contratos numéricos, fórmulas econômicas, persistência AM12,
proveniência AM05, estatísticas AM09, enumeração AM10 e fronteira AM04 não
foram modificados. Marcas, abertura, projetos-base e registros arquivados
permanecem byte a byte iguais à base. O CSS novo se limita ao cartão do editor.

## Pendências e limites

AM07 não foi antecipado: quando o backend omite detalhes acima de 12.000
operações, a indicação de processamento ainda exige sua correção própria.
Um teste registra explicitamente esse comportamento anterior. AM16,
rastreabilidade e legibilidade ampla permanecem nas próximas etapas.

Foi confirmado um defeito preexistente ao preparar um modelo sem `prioridade`
de pedido: ele é válido no backend, mas `normalizedModel` converte o campo
ausente em NaN, serializado como null, e a reaplicação é recusada por prioridade
inválida. A reprodução foi feita na fonte anterior, registrada em
`pending-priority.log`. Não foi corrigido nesta etapa. O fluxo de aceitação
AM17 usa prioridade explícita, como a carteira padrão. Não afirmar cobertura
universal da importação de modelos opcionais.

Windows, BAT e projetor ainda requerem validação local. Os dados continuam
sintéticos; esta etapa não comprova calibração industrial. Leia o plano
de continuidade antes de iniciar outra correção.

## Como reproduzir e recuperar a entrega

```sh
python -m pytest tests contract_tests atelier/tests -q
python -m pytest tests/test_am17_workload.py tests/test_am17_replay.py -q
python -m atelier.tests.browser_am17
python -m atelier.tests.browser_acabamento_final
python -m atelier.tests.validacao_experimentos_banca
```

Testes JavaScript exigem Node; navegador exige Playwright/Chromium. Esses
requisitos de desenvolvimento não são novos requisitos para executar o app.
Os scripts adicionais de reprodução e benchmark ficam em `docs/AM17/evidencias`.
Execute em cópia. O benchmark JavaScript recebe os caminhos de `app.js` da
base e da versão atual como argumentos; o benchmark de RSS usa Linux.

O ZIP completo e o patch sobre a base exata são extraídos e comparados por
SHA-256. O aplicador cria uma pasta nova e preserva a origem. Logs dos testes
do pacote extraído e `VERIFICACAO_AM17.json` acompanham a entrega. Os arquivos
publicados no GitHub são recuperados e conferidos antes de declarar a conclusão.
