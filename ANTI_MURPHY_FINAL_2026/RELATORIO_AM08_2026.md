# Anti-Murphy AM08-2026.1 — economia arquivada

Base AM12/AM05/AM11, commit6410e6bfa7919864c965d4c9dd9ca6e43740afbf. Branch correcao-am08-economia. Escopo exclusivoAM08.

## Reprodução e causa

O arquivo de experimento guardava resumo dos resultados do cenário, mas não o investimento nem custo total/economia da decisão. Na referência sintética, comparar Não intervir com manutenção expressa retornava delta de custo de cenário -5903,676785762309; a economia líquida ativa era4103,68, após1800 de investimento. A subtração era correta para o cenário, mas não representava o custo total da decisão.

## Implementação

atelier/experiment_economics.py fornece snapshot e visão somente leitura. Novos experimentos possuem economics schema1.0/currencyBRL, com scenario_cost (operação+multas), investment, decision_cost, savings e reference_cost. Valores vêm dos campos precisos existentes AM11; não se alterou fórmula econômica. A assinatura da referência vem da configuração do incidente, preservando distinção entre referências/modelos diferentes.

Comparação preserva delta.total_cost legado como custo do cenário e acrescenta economics.first/second/delta, sempre B−A. A interface identifica separadamente os componentes em reais. Economia líquida usa a referência sem resposta do próprio experimento; não é sinônimo da variação B−A de custo. Referências diferentes ou não identificadas geram aviso; modelos distintos continuam explicitamente sinalizados.

Documentos antigos são lidos sem migração ou regravação: custo de cenário e referência podem ser recuperados das métricas explícitas, mas investimento, custo da decisão e economia ausentes ficam null, mesmo que o nome da ação seja Não intervir ou a política permita inferências. A interface mostra Não registrado/não calculado e comparação econômica parcial. Nenhum zero é inventado. Documentos novos parciais também preservam ausência; custo de cenário inviável não é tratado como execução gratuita. Investimento zero explicitamente registrado continua zero; economia negativa permanece negativa.

Foram alterados somente atelier/service.py (gravação/listagem/comparação) e atelier/web/app.js (tabela e rótulos). Novo módulo atelier/experiment_economics.py. Novos testes tests/test_am08_economics.py e atelier/tests/browser_am08.py. Nenhum código de simulation/, proteçãoAM12, proveniênciaAM05, CSS/identidade, inicializador ou dados-base foi modificado. A comparação não recalcula experimentos nem substitui dados antigos pelas condições atuais.

## Antes/depois de referência

- Custo de cenário da falha:16216,673139707087 → exibidoR$16216,67.
- Cenário da manutenção:10312,996353944778 → R$10313,00.
- Investimento:1800.
- Custo da decisão:12112,996353944778 → R$12113,00.
- Economia líquida:4103,676785762309 → R$4103,68.
- Delta cenário B−A:-5903,676785762309; delta decisão B−A:-4103,676785762309. Agora aparecem como conceitos separados.

## Validação

428testes aprovados, cinco falhas históricas e dez subtestes.13testes novosAM08 aprovados, cobrindo persistência/reabertura, precisão, investimento zero, economia negativa real, arquivos antigos e novos parciais, dados inválidos/não finitos, referências/modelos diferentes e ausência de regravação dos documentos históricos.

Browser HTTP real passou1280x720,1366x768,1920x1080: componentes separados, valores corretos, legado parcial, bytes antigos preservados, sem erroJS nem transbordamento horizontal nos fluxos. ModoBanca HTTP real registro/relatório passou nas3resoluções. Três experimentos oficiais sem alterações: SLA100/40/100%; custos8076,37/16216,67/10313,00; custo decisão12113,00/economia4103,68.

As5falhas permanecem test_operation_ui::test_evidence_exports_the_current_timed_experiment; dois testes test_restauracao_acesso; test_v31_editorial::test_only_one_root_launcher e ::test_preview_has_no_external_script_dependency. Nenhum teste existente foi alterado para mascarar falhas.

Linux/Python3.12/Chromium. Windows/bat/projetor não homologados nativamente. Valores são do modelo sintético, não economia de caixa comprovada. Dados antigos ausentes não foram recuperados ou estimados: para registrar componentes completos é preciso guardar um novo experimento a partir de cálculo conhecido, mantendo o anterior.

## Reprodução

python -m pytest tests contract_tests atelier/tests -q
python -m atelier.tests.browser_am08
python -m atelier.tests.validacao_experimentos_banca

Execute testes em cópia. Browser requer Playwright/Chromium. Entrega inclui ZIP completo, patch sobreAM12, evidências e continuidade; arquivos e branches anteriores são preservados.
