# AM14 — projeto de origem nos registros históricos

Base AM13: 49d3da54a3392d95b5e9cdb7fd3ee78d044286d4. Branch correcao-am14-origem.

Antes, history() descartava project_id na lista, embora o JSON arquivado preservasse esse identificador. O log reproduction.log registra as chaves da lista anterior e o ID presente no arquivo. Lista e ficha não permitiam distinguir claramente decisões de projetos distintos, inclusive com mesmo run_id.

Novos registros guardam project_name junto ao project_id no record assinado, com nome consultado no momento da gravação sob o bloqueio de workspace existente. Renomear depois não muda o nome arquivado. A lista retorna ambos os campos. A ficha e a lista usam historyProjectOrigin para mostrar a mesma origem, com escape HTML existente.

Para registros antigos com ID e sem nome, a interface consulta o cadastro carregado e identifica expressamente o nome como atual, não arquivado na época. Se o projeto não está disponível, mostra apenas o ID e explica a ausência de nome. Se não há ID, informa origem não identificada. Não presume projeto principal ou atual. A lista permanece aberta a todos os projetos, com esse escopo identificado no contador; não introduz filtro que esconda registros.

Nenhum arquivo histórico é migrado, regravado ou reassinado. read_history devolve o envelope original, preservando sha256 e compatibilidade de verificação; metadados de visualização não são acrescentados ao documento assinado. O nome novo passa pelo mesmo mecanismo de assinatura e gravação atomicamente confirmado já existente. Renomeações de projetos não alteram registros anteriores.

Arquivos de produção: atelier/service.py, decision e history; atelier/web/app.js, historyProjectOrigin, loadHistory e openHistory. Testes novos test_am14_origin.py e browser_am14.py. Não há mudança no DES, fórmulas econômicas, seleção, abertura, CSS, marcas, motor de ensaios ou demais correções.

Validação: 540 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados. Sete testes novos verificam dois projetos, renomeação, nome à época, legado sem nome/sem ID, envelopes assinados e bytes preservados. Três experimentos oficiais mantidos: SLA 100/40/100%, custo da decisão R$12.113,00 e economia R$4.103,68. Browser real passou em 1280x720,1366x768,1920x1080: lista com duas origens, ficha do projeto anterior, nome arquivado após renomeação, nenhum erro JavaScript e arquivos de decisões byte a byte preservados. As cinco falhas anteriores continuam em operation_ui, restauracao_acesso (dois) e v31_editorial (dois), sem exclusão de testes. Logs completos acompanham a entrega.

Limitações: nomes antigos não arquivados não podem ser reconstruídos com certeza. O cadastro usado na visualização é o carregado pela interface; atualize o projeto/página para consultar mudanças externas. Identificadores continuam sendo a referência primária; nomes repetidos não fundem origens. Não foram alteradas as regras anteriores de listagem de até 500 registros nem feito ensaio com milhares de arquivos. O relatório técnico corrente da simulação não foi transformado em ficha histórica; esta etapa trata Registros. Windows/projetor continuam pendentes de validação local.

ZIP e patch são extraídos e comparados por SHA-256 sobre a base exata. O aplicador cria pasta nova e preserva a origem. Testes direcionados também são executados no ZIP extraído. Fonte e downloads são recuperados do GitHub e comparados aos locais antes de concluir. Extraia o aplicativo completo em pasta nova e guarde instalações/projetos anteriores.

Reprodução em cópia: python -m pytest tests contract_tests atelier/tests -q; python -m pytest tests/test_am14_origin.py -q; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_am14. Testes do helper JavaScript exigem Node; navegador usa Playwright/Chromium em Linux. Próxima etapa recomendada: AM15, legibilidade e enquadramento da fábrica, preservando identidade. Demais pendências da AM17, incluindo contratos antigos e prioridade opcional, permanecem abertas.
