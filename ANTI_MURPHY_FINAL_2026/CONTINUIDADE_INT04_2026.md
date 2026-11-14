# Continuidade — INT04-2026.1

Base INT03 974f38e. Branch correcao-int04-legibilidade; checkpoint 2059b39. Alteração exclusiva em .alt-metrics small de atelier/web/styles.css: 10→14 px, line-height 1.4, #758681→#48615D. Contraste medido 3,829729→6,680486:1 sobre branco em análise/decisões, nas três resoluções. Não foi redesenhado o programa nem alterado motor, HTML, JavaScript, fórmulas ou dados.

732 testes aprovados, zero falhas, dez subtestes. Novo roteiro de browser mede 24 rótulos em duas áreas/três resoluções, com contraste >=4,5:1, fontes >=14 px e geometria sem corte/sobreposição. Modo Banca, gráficos/exportações e mapa com 1/5/9/16/50 postos também conferidos. Três experimentos oficiais preservados. ZIP/patch comparados em base limpa e arquivos do GitHub recuperados antes da conclusão.

A execução inicial do teste AM15 falhou no limite de enquadramento de 50 postos/1280x720; base INT03 e versão atual passaram nos 15 casos quando executadas separadamente. Logs inicial, base e repetição são preservados. Causa não demonstrada, sem alteração do mapa ou das asserções. Monitorar essa ocorrência na verificação final; não a tratar como defeito de mapa corrigido.

INT01/02/03/04 tiveram correções entregues. Próximo passo recomendado: uma verificação final focada da versão combinada, inicialmente sem modificar código, e ensaio no Windows/BAT/projetor real. Conferir importar/exportar/reabrir regra; curto ciclo na auditoria/relatório; biblioteca com arquivos válidos/inválidos; legibilidade; roteiro completo da banca. Não repetir desenvolvimento amplo nem iniciar novos recursos por padrão.

Ainda não há homologação nativa Windows/projetor, auditoria WCAG completa ou validação industrial. AM18 é manutenção gradual; AM20/21 são caminhos históricos adicionais. Instalar em pasta nova, manter cópia e usar sempre a versão imediatamente anterior confirmada. Sem agentes paralelos, checkpoints e entregas verificadas para qualquer correção futura necessária.
