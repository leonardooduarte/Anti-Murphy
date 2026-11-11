# Anti-Murphy AM09-2026.1 — estatísticas de execuções inviáveis

Base AM08/AM12/AM05/AM11, commit4d877444df33d0a7ae1fa503fb6ab465ad2c124c. Branch correcao-am09-inviaveis. Escopo exclusivoAM09.

## Reprodução

No modelo mínimo de um posto, uma máquina/equipe e20unidades de60min, stress16/seed2026 gerou11execuções inviáveis e5viáveis. Antes, a média de makespan do posto era7,7h, incluindo11zeros; os cenários viáveis tinham média24,7h. Agora a média descreve somente os5viáveis. A contagem de11inviáveis permanece explícita. O SLA médio condicional dos viáveis é100%; a taxa de resiliência de todas as16tentativas continua31,2%. Esses indicadores possuem denominadores diferentes e não podem ser confundidos.

## Tratamento

Stress e MonteCarlo conservam cada execução com feasible e reason. Métricas dos inviáveis são null, não duração/custo zero. Estatísticas são calculadas sobre execuções viáveis, com contadores de amostra. Quando não há amostra, médias/percentis/índice não são calculados (null). Com somente uma execução válida no MonteCarlo, média/percentis continuam disponíveis, mas desvio amostral e intervalo ficam ausentes. Duas ou mais replicações válidas mantêm a aproximação de intervalo anterior, sem interpretação industrial calibrada.

Stress mantém16tentativas e as mesmas perturbações/sementes. Resilience_rate usa todas as tentativas: apenas viáveis comSLA>=80contam como atendidas; inviáveis são não atendidas. O índice heurístico de fragilidade usa somente viáveis e fica indisponível sem amostra. A ordenação de postos prioriza taxa de inviabilidade, depois o índice condicional existente; nenhum peso arbitrário novo foi inventado para substituir métrica ausente.

MonteCarlo mantém as sementes e o motor. Resumos incluem n, e gargalo dominante/participação usam somente viáveis. Nenhum gargalo estatístico é inferido de postos bloqueados de execuções inviáveis.

O motorDES continua com seu contrato original para cenários inviáveis; a camada de análises interpreta explicitamente feasible=False. Não foram alterados os resultados físicos ou fórmulas de cenários viáveis. A apresentação preserva valores positivos pequenos conformeAM11.

## Interface, origem e exportação

Painéis mostram tentativas, viáveis, inviáveis e a base estatística. Gráficos não desenham inviáveis como pontos emzero; todas as linhas continuam na tabela/CSV, com motivos. CSV mantém métricas não calculadas vazias e inclui tamanho de amostra no metadado. SVG exibe a amostra na figura; sem pontos válidos, mostra diagnóstico de amostra ausente, sem fabricar observações. JSON mantém contagens, viabilidade e nulls.

Somente os contextosAM05 de Stress e MonteCarlo receberam nova statistics_policy; ferramentas não alteradas não são invalidadas por esse marcador. Histórico temporário e classificação Atual/Desatualizado/Histórico foram preservados. Arquivos exportados anteriormente não foram regravados.

Leitores históricos Streamlit afetados foram adaptados para aceitar valores ausentes sem erro ou zeros artificiais: fragilidade, resumoStress, paisagem e painelMonteCarlo. São adaptações ao contrato estatístico, sem redesenho de estilos ou correção de outros achados.

## Arquivos

simulation/innovation.py (Stress), simulation/advanced.py (MonteCarlo); atelier/service.py (transporte de viabilidade/amostra); atelier/analysis_provenance.py (versão dos2contextos); atelier/web/app.js e engineering_charts.js (avisos/exportação/gráficos); legacy_app.py e ui/experience.py,v15.py,v16.py,v18.py,v21.py e novo ui/stat_values.py (compatibilidade nullable). Novos testes tests/test_am09_infeasible_statistics.py e atelier/tests/browser_am09.py.

## Validação

440testes aprovados, cinco falhas históricas, dez subtestes.12novosAM09 aprovados. Cobrem11/16inviáveis reais, mistos/todosviáveis/todosinviáveis, ausência de amostra, singleton, variância/intervalo independentes, sementes, transporteHTTP, proveniência e painéis históricos.

BrowserHTTP real passou1280x720,1366x768,1920x1080:5pontosviáveis,11inviáveis preservados; contagem/motivos e CSV/SVG coerentes, sem erroJS/overflowhorizontal nos fluxos. ModoBanca HTTP real registro/relatório passou nas3resoluções. Três experimentos oficiais preservados: SLA100/40/100%; custos8076,37/16216,67/10313,00; custo decisão12113,00/economia4103,68.

Cinco falhas preexistentes: test_operation_ui::test_evidence_exports_the_current_timed_experiment; dois testes test_restauracao_acesso; test_v31_editorial::test_only_one_root_launcher e ::test_preview_has_no_external_script_dependency. Nenhum teste existente foi alterado para mascará-las.

AmbienteLinux/Python3.12/Chromium. Windows/bat/projetor não homologados nativamente. Não foi feita exploração completa de todas as telas históricas no navegador; consumidores atingidos foram testados diretamente com amostra ausente. Estatísticas dos viáveis são condicionais à viabilidade; a taxa de inviáveis não é probabilidade industrial calibrada. Intervalos são exploratórios do modelo.

AM10 enumeração e demais achados continuam pendentes. Identidade, CSS, abertura, proteçãoAM12, economia arquivadaAM08 e engine.py não foram modificados. Dados e arquivos-base foram preservados.

## Reprodução

python -m pytest tests contract_tests atelier/tests -q
python -m atelier.tests.browser_am09
python -m atelier.tests.validacao_experimentos_banca

Execute em cópia. Navegador exige Playwright/Chromium. Pacote e patch são verificados por extração e equivalência e depois recuperados do GitHub para conferir hashes.
