# Anti-Murphy AM10-2026.1 — espaço de busca de capacidade

Base AM09/AM08/AM12/AM05/AM11, commit `a56c407f35bd11b3091791c5e561ea82fa90812d`. Branch correcao-am10-capacidade. Escopo exclusivo AM10.

## Reprodução

Um posto com 1 máquina/1 operador e 20 unidades de 60 min: candidatos isolados +1 operador e+1 máquina ficaram em 0,9871777 un/h, sem atingir meta 1,5 un/h. A combinação omitida atingia 1,9656476 un/h/SLA 100%. Após correção ela é pesquisada e aparece como atende. Referência independente com ruído fixo 1: horizonte 20 h/TP 1 isoladamente, horizonte 10 h/TP 2 com os dois recursos; prazos 100 h, sem alterar motor.

## Enumeração

A busca completa o espaço delimitado de uma ou duas combinações posto/recurso (canais). Cada canal é uma adição positiva em operadores ou máquinas de um posto. Os montantes respeitam os limites TOTAIS de operadores e máquinas adicionais, incluindo:
- adições isoladas com montantes até os limites;
- máquina+operador no mesmo posto;
- máquina emA/operador emB e a orientação inversa;
- dois postos com operadores, inclusive partições de montantes;
- dois postos com máquinas, quando o limite total permitir.

Não são enumeradas três ou mais combinações posto/recurso. Montantes maiores que 1 são permitidos no mesmo canal; por isso duas combinações não significam necessariamente duas unidades. O cenário nominal é referência e não é adicionado como candidato novo. Não há prova de ótimo global.

Planos são identificados por estrutura, não por nome, sem duplicação, em ordem determinística de IDs. A validação e enumeração precedem simulações. Acima de 10000 candidatos a busca é recusada com mensagem para reduzir postos/limites; não se apresenta busca parcial como completa. Esse é um limite declarado da ferramenta, não correção geralAM17. Quantidade máxima retornada trunca somente a apresentação após avaliar o espaço permitido. Limite zero de resultados não executa cenários.

O score existente foi preservado, mas alternativas que efetivamente atendem à meta são ordenadas antes das que não atendem, evitando que custo alto esconda uma solução válida. Viabilidade física do motor também é exigida; SLA/throughput zero não aprovam cenário bloqueado.

## Apresentação e rastreabilidade

O Laboratório informa candidatos avaliados, retornados, limites globais e abrangência. CSV e SVG levam essa descrição e mantêm o estado/origemAM05. Linhas de resultado incluem alterações explícitas por posto/recurso. O contextoAM05 de capacidade recebeu nova search_policy; contextos de outras ferramentas não mudaram. A assinatura continua determinística.

Na fábrica padrão, a chamada do Laboratório (até 2 operadores/1 máquina) avalia 75 candidatos e exibe 12. Os gráficos existentes de 12 legendas/ampliação/exportação passaram sem alterar suas asserções. Não foram adicionados custos de compra/contratação não modelados: a análise é de capacidade estrutural sobre operação nominal desde o início, não recuperação temporalAM06.

## Validação

457 testes aprovados,5 falhas históricas,10 subtestes.17 novosAM10 aprovados. Testes independentes comparam os planos à enumeração cartesiana de 2 postos para 7 orçamentos; validam montantes, ambas orientações, pares locais, ausência de duplicatas, permutação de postos, metas/precisão, orçamento inválido, truncamento, pré-validação do limite sem simular e ausência de mutação do modelo.

BrowserHTTP real passou 1280 x 720,1366 x 768,1920 x 1080: modelo mínimo encontra combinação local que atende; espaço declarado e exportaçõesCSV/SVG coerentes; sem errosJS/overflowhorizontal nos fluxos. Script de acabamento/legendas/zoom/exportação passou nas 3 resoluções. ModoBanca HTTP real registro/relatório passou nas 3 resoluções. Três experimentos oficiais preservados: SLA 100/40/100%; custos 8076,37/16216,67/10313,00; custo decisão 12113,00/economia 4103,68.

As 5 falhas permanecem test_operation_ui::test_evidence_exports_the_current_timed_experiment; dois testes test_restauracao_acesso; test_v31_editorial::test_only_one_root_launcher e ::test_preview_has_no_external_script_dependency. Nenhum teste existente foi alterado para mascará-las.

## Arquivos e preservação

simulation/innovation.py (enumeração/validação/ordenação); atelier/service.py (metadados e alterações); atelier/analysis_provenance.py (somente contexto capacidade); atelier/web/app.js e engineering_charts.js (descrição do espaço e exportações). Novos tests/test_am10_capacity.py e atelier/tests/browser_am10.py. Nenhuma mudança em engine.py, fórmulas de custo, recuperação, persistênciaAM12, economiaAM08, estatísticasAM09, CSS/identidade/abertura ou dados-base.

Linux/Python 3.12/Chromium; Windows/projetor pendentes de aceite local. Dados sintéticos, sem calibração industrial. Orçamentos são limites de recursos da enumeração, não garantia de disponibilidade física ou ótimo global. Resultados novos do Laboratório podem diferir porque o espaço pesquisado foi ampliado; números não foram forçados para manter a lista antiga. Experimentos oficiais mantiveram seus resultados.

## Reprodução

python -m pytest tests contract_tests atelier/tests -q
python -m atelier.tests.browser_am10
python -m atelier.tests.browser_acabamento_final
python -m atelier.tests.validacao_experimentos_banca

Execute em cópia; navegador exige Playwright/Chromium. ZIP/patch são extraídos e conferidos, depois os arquivos do GitHub são recuperados para verificar hashes. Arquivos e branches anteriores permanecem preservados.

Conferência do pacote: ZIP e patch reproduzem os mesmos 451 arquivos por SHA-256. Após extração, 36 testes direcionados e os endpoints HTTP principais passaram novamente. Veja VERIFICACAO_AM10.json e os logs da entrega.
