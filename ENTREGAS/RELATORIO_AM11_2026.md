# Anti-Murphy — correção exclusiva AM-11

Base: ANTI_MURPHY_AM01_AM06_RECONSTRUIDO_LEVE_2026.zip  
SHA-256 da base: b2e0b234a275432523698836bda0f596d7110ff4d264ae6ed6fb197a96a81419  
Versão desta etapa: AM11-2026.1. Não é o pacote perdido do Codex.

## Resultado

Corrigidos pisos artificiais do motor atual, denominadores físicos e precisão intermediária. Foram preservados os campos legados e adicionados valores precisos para filtros/comparações. Operações que não podem ser representadas com float finito e progresso temporal são rejeitadas explicitamente, sem inventar tempo mínimo. Não houve reescrita do DES.

## Reprodução antes/depois com referências independentes

Ruído fixado em 1 apenas no processo de teste; fontes não são alteradas para reproduzir. Há também testes com ruído real.

| Caso | Antes | Depois / referência |
|---|---|---|
| Uma operação de 0,06 min = 0,001 h | makespan publicado 0; utilização 10%; TP 100 un/h | 0,001 h; utilização 100%; TP 1.000 un/h |
| Ciclo de 60 min, eficiência 0,001 | 100 h, pois fator virava 0,01 | 1.000 h, mantendo fator original |
| Mesmo caso, prazo 100 h, multa 100/h, custo 30/h | SLA 100%; custo R$ 3.000 | SLA 0%; operação R$ 30.000 + multa R$ 90.000 = R$ 120.000 |
| Dois de três pedidos no prazo; meta 66,68% | 66,7% arredondado podia aprovar | 66,666…% preciso: reprova |
| TP real 1,0004; meta 1,0002 | 1,000 arredondado podia reprovar | Aprova pelo valor preciso |

## Contrato de precisão

- `simulation.numeric.metric(result, key)` usa `result.precise`; resultados antigos sem esse campo ou com null continuam aceitos por fallback.
- `precise` guarda makespan, throughput, SLA, custos e balanceamento sem arredondamento de apresentação.
- Campos legados continuam disponíveis. Makespan/throughput positivos que arredondariam a zero preservam o valor positivo.
- Pedidos recebem `completion_h`, `lateness_h`, `penalty`; postos recebem `precise` com utilização, espera e custo.
- Filtros de SLA/throughput, comparação, ranking econômico, instantes críticos e consumidores avançados usam valores precisos. Tolerâncias explícitas de decisão (.005 h/centavos/epsilons) permanecem políticas existentes.
- Zeros físicos: custos/setup podem ser zero; operador zero em posto automatizado continua válido; 0/0 só é definido como zero na utilização de recurso não empregado. Throughput/custo por horizonte exigem denominador positivo.
- Entradas nulas, negativas incompatíveis com domínio e não finitas continuam rejeitadas. Eficiência/disponibilidade/tempo de ciclo exigem valor positivo; ciclo zero não é operação suportada.
- `product_ratio` utiliza Decimal somente quando produtos intermediários perdem faixa normal (overflow/underflow/subnormal), recuperando respostas representáveis; resultados fora da faixa são rejeitados.
- Custos, multas e eventos não podem publicar infinito/NaN. Se a duração positiva não faz avançar o relógio no instante atual, a entrada é rejeitada com erro de precisão temporal.
- Formatação JS mantém o padrão normal, mas usa precisão adaptativa para não exibir como zero valores pequenos não nulos.

## Pisos encontrados e classificação

Removidos do motor ativo: fatores de eficiência/disponibilidade0,01, horas de capacidade0,01, makespan0,01. Removido horizonte0,01 da análise financeira e pisos de referências positivas nos percentuais/radar. A normalização por série do radar não foi redesenhada (AM-21 continua pendente).

Preservados por terem outra semântica: mínimos inteiros de quantidade e capacidade do domínio; arredondamento monetário de apresentação e registro em centavos; epsilons/tolerâncias de decisão; pisos de escalas gráficas; saturação do índice heurístico de fragilidade. O motor antigo `engine_v26_legacy.py` e os limites do editor histórico não foram reescritos. AM-09, AM-10 e AM-05 não foram corrigidos disfarçadamente.

## Três experimentos oficiais

| Cenário | Makespan exibido | SLA | Custo cenário exibido |
|---|---:|---:|---:|
| Nominal | 16,90 h | 100% | R$ 8.076,37 |
| Falha CNC | 24,58 h | 40% | R$ 16.216,67 |
| Manutenção expressa | 21,58 h | 100% | R$ 10.313,00 |

Investimento da manutenção R$1.800; custo de decisão exibido R$12.113,00. Economia agora **R$4.103,68**, antes R$4.103,67. Valores precisos: incidente16216.673139707087; resposta10312.996353944778; decisão12112.996353944778; diferença4103.676785762309. Subtrair valores já arredondados explica o centavo anterior. Não se ajustou o motor para forçar os números antigos.

Sensibilidade CNC: TP preciso5.681763308299117 un/h, antes publicado5.682; continua sem ganho ao adicionar máquinas isoladamente. Custos/unidade precisos84.12881249414335,96.09692807908425,108.06504366402514,120.033159248966; as diferenças de exibição vêm da retenção de precisão e não de um modelo novo. Recuperação +operador6h continua19,97h/SLA60%.

## Verificação executada

- Suíte completa nas pastas `tests`, `contract_tests`, `atelier/tests`: **352 aprovados, 5 falhas preexistentes, 10 subtestes aprovados**. Base auditada:271 aprovados e as mesmas5 falhas. **81 testes novos**, todos aprovados.
- Não houve alteração dos testes preexistentes para mascarar falhas.
- Três experimentos oficiais aprovados; módulo existente e resultados regenerados incluídos.
- Modo Banca completo, registro/relatório e fallback de download, via HTTP real em1280x720,1366x768,1920x1080: passou, sem erros JS capturados nos fluxos.
- Script de acabamento/gráficos/exportações: passou nas3 resoluções.
- Caso curto no navegador real: `0,001 h` visível, sem erro JS.
- HTTP charts smoke passou. Sintaxe JavaScript passou; Python foi importado e executado pelos testes.

Falhas preexistentes: `tests/test_operation_ui.py::test_evidence_exports_the_current_timed_experiment`; dois testes de `test_restauracao_acesso.py`; `test_v31_editorial.py::test_only_one_root_launcher`; `test_v31_editorial.py::test_preview_has_no_external_script_dependency`. São divergências históricas já discriminadas na auditoria, incluindo PREVIEW_OPERACAO.html ausente. A suíte não é declarada100% verde.

Ambiente: Linux/Python3.12.14,pytest9.2.0,pytest-subtests0.15.0,Streamlit1.67.0,pandas2.2.3,numpy2.3.5,Plotly7.1.0,pydantic2.13.4,Playwright1.62.0,Chromium. Node24.22.1 para sintaxe/formatadores. Windows/bat e projetor físico não homologados. Aplicativo principal continua sem dependências adicionais.

## Preservação e limites

Fonte e workspace da base recebida são preservados na cópia original. O pacote desta etapa usa exatamente os arquivos locais de projeto arquivados no ZIP-base, não recupera dados do Codex perdido e não importa seus projetos de outra instalação. Identidade, CSS, imagens, abertura e inicializador não mudaram. Somente formatação numérica JS e componentes relacionados ao AM-11 foram ajustados.

AM-05 continua incompleto. Fronteira em empate, investimentos arquivados, inviáveis nas estatísticas, busca de capacidade e demais achados continuam pendentes. Dados permanecem sintéticos; sem calibração industrial ou garantia de ótimo global.

Documentos históricos foram preservados; podem conter centavos e limites da edição anterior. Use os experimentos regenerados e esta nota para a apresentação desta versão.

## Arquivos modificados

- `LEIA_PRIMEIRO_VERSAO_FINAL.md`
- `atelier/decision_quality.py`
- `atelier/service.py`
- `atelier/web/app.js`
- `atelier/web/engineering_charts.js`
- `docs/EXPERIMENTOS_VALIDACAO_ENGENHARIA.md`
- `docs/PITCH_5_MIN_E_SABATINA.md`
- `docs/RELATORIO_FINAL_BANCA_2026.md`
- `docs/RELATORIO_MODO_BANCA_PREMIUM.md`
- `docs/RESULTADOS_TRES_EXPERIMENTOS_BANCA.json`
- `simulation/advanced.py`
- `simulation/atlas.py`
- `simulation/decision_council.py`
- `simulation/decision_lab.py`
- `simulation/engine.py`
- `simulation/innovation.py`
- `simulation/metrics.py`
- `simulation/numeric.py`
- `simulation/response.py`
- `tests/test_am11_consumers.py`
- `tests/test_am11_display.py`
- `tests/test_am11_numeric_precision.py`
- `tests/test_am11_review_regressions.py`

## Comandos de reprodução

```bash
python -m pytest tests contract_tests atelier/tests -q
python -m atelier.tests.validacao_experimentos_banca
python -m atelier.tests.browser_acabamento_final
```
Os scripts de navegador exigem Playwright/Chromium. O teste HTTP real adicional utilizado está nas evidências desta etapa. Executar sempre em cópia nova, pois scripts antigos podem regenerar documentos.
