# Continuidade — AM22-2026.1

Base RECUPERACAO-2026.1, e52b245. Branch correcao-am22-host-origin; checkpoints 6dbca22 e db66668. Somente atelier/server.py foi alterado em produção: GET/POST exigem Host local na porta ativa; Origin, quando presente, deve corresponder à origem HTTP local. Ausência de Origin continua permitida para clientes locais; Host ausente/duplicado/externo e Origin inválido são recusados antes de acessar o serviço. Lançamento, bind, navegação, interface e motor preservados.

664 testes aprovados, zero falhas, dez subtestes, 67 casos novos. Três experimentos preservados. Navegador com 127.0.0.1 e localhost em três resoluções; Modo Banca, gráficos e exportações conferidos. ZIP/patch extraídos e comparados; publicação recuperada do GitHub antes da conclusão. Instale em pasta nova e preserve versões e projetos anteriores.

Próxima etapa: auditoria integrada da versão efetivamente entregue, sem modificar código inicialmente. Conferir simulação, A/B, rastreabilidade econômica, ensaios, dados locais, recuperação, decisões/relatórios, interface e desempenho em fluxos completos. Separar defeitos confirmados de suspeitas. Usar os documentos mais recentes e o código, pois quadros antigos de status têm pendências já resolvidas. Não iniciar novos recursos ou redesenho antes de avaliar os resultados.

Ainda pendente: validação real no Windows/BAT/projetor, a ser executada no computador da apresentação; avaliação visual dos componentes recebidos. AM18 é organização gradual; AM20/21 são caminhos históricos cuja prioridade depende de uso. Não foram corrigidos nesta etapa. Continuar sem agentes paralelos, com checkpoints, branch própria, ZIP, patch e downloads verificados para correções futuras.
