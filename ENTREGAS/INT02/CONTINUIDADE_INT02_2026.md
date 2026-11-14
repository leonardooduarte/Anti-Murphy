# Continuidade — INT02-2026.1

Base INT01, commit 1bbe141. Branch correcao-int02-precisao-auditoria; checkpoint b8f8338. Auditoria por pedido usa completion_h/lateness_h precisos e preserva folga sem arredondar. Fallback legado somente por ausência, com origem/aviso explícitos; inválidos ficam desconhecidos, sem zero fabricado. Classificação conserva o status/tolerância do DES; apresentação de horários curtos mantém sinal no painel e tabela do relatório. Nenhuma fórmula do motor mudou.

706 testes aprovados, zero falhas, dez subtestes; 24 casos novos. Três experimentos oficiais preservados. Painel, API, três cenários e relatório/pop-up/download nas três resoluções; avisos legado/indisponível também conferidos com transporte controlado. Importação INT01, Modo Banca, gráficos e exportações novamente aprovados. Testes/hash anteriores atualizados de forma rastreável e mais específica, sem remoções.

ZIP e patch devem reproduzir os mesmos arquivos; GitHub é recuperado e comparado antes da conclusão. Instale em pasta nova e preserve projetos e versões anteriores. Windows/BAT/projetor e validade industrial continuam pendentes.

Próxima etapa: INT-03, biblioteca de experimentos tolerante a documentos inválidos. Reproduzir um arquivo [] na coleção junto a registros válidos; preservar originais, permitir consulta/gravação dos válidos e avisar problemas sem apagamento silencioso. Não avançar para contraste INT04, AM18/20/21 ou outras correções nessa etapa. Usar esta versão mais recente confirmada como base, sem voltar ao ZIP antigo. Sem agentes paralelos, uma branch/checkpoint por etapa, ZIP/patch, relatório e downloads verificados.
