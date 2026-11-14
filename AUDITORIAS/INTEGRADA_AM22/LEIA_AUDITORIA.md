# Auditoria integrada AM22

Esta entrega contém relatório e evidências; não modifica o aplicativo AM22. Não há patch de código. O aplicativo continua no commit 8599a5c, ZIP AM22 anterior. Leia achados.json e RELATORIO_AUDITORIA_INTEGRADA_AM22.md antes de iniciar correções.

Os scripts em roteiros/ investigam comportamentos; não são testes de homologação que devem ser mantidos verdes após corrigir os bugs. Algumas assertivas confirmam a existência dos defeitos. Os arquivos .executado.txt preservam exatamente os scripts originais e caminhos Linux usados nesta auditoria; as cópias .py permitem escolher caminhos por variáveis de ambiente.

Para reproduzir, use uma EXTRAÇÃO NOVA da AM22. Nunca execute QA em instalação com dados de trabalho. Os scripts usam diretórios temporários para projetos. Use ambiente de desenvolvimento com as dependências do projeto, pytest e, para browser, Playwright e Chromium. Não são dependências novas para iniciar o aplicativo. A referência do browser aqui é /usr/bin/chromium; a cópia portátil ainda requer Linux/Chromium, não é homologação Windows.

Defina ANTI_MURPHY_AUDIT_APP com o caminho absoluto da extração ANTI_MURPHY_FINAL_2026; ANTI_MURPHY_AUDIT_OUT com uma pasta nova de resultados previamente criada. Execute os scripts desejados com o Python de desenvolvimento. probes.py e performance.py não precisam de navegador; browser_integrated.py e visual_review.py requerem Chromium; run_browsers.py executa 13 módulos existentes em sequência, com logs separados. Os resultados podem variar em tempo e UUIDs. A própria aplicação continua preservada por comparação dos hashes do manifesto. Para regressão, na extração: python -m pytest tests contract_tests atelier/tests -q -p no:cacheprovider; para os oficiais: python -m atelier.tests.validacao_experimentos_banca.

Evidências incluem um primeiro ensaio do roteiro integrado com erro de sincronização do instrumento; o relatório distingue essa ocorrência dos defeitos do produto. Capturas selecionadas ficam em capturas/; os JSON/logs referem os nomes originais dos diretórios de captura. A versão ZIP deste pacote contém todos os arquivos do relatório, não outra cópia do aplicativo.

Próxima etapa recomendada: correção exclusiva INT-01, importação de dispatch_rule, sobre a AM22 ou descendente imediato confirmado. Windows/BAT/projetor e validação industrial ainda pendentes.
