# Continuidade — INT03-2026.1

Base INT02 f0baa1a. Branch correcao-int03-biblioteca-resiliente; checkpoint 025e4ce. Leitura individual isola documentos inválidos, conserva originais e apresenta filename/motivo em aviso na biblioteca. Válidos continuam consultáveis, comparáveis e graváveis. Reabertura com arquivo inválido é coberta; falha de acesso à pasta inteira continua sendo erro explícito, sem fingir coleção vazia.

API /api/experiments permanece em lista; /api/experiment-library acrescenta snapshot com projeto/items/issues para interface e clientes que precisam dos avisos. Compatibilidade econômica legada não presume investimento zero. Comparação usa documentos validados; não há reparo automático nem regravação de históricos. Regra INT01, precisão INT02, DES, fórmulas, CSS, abertura, gráficos e Modo Banca preservados.

732 testes aprovados, zero falhas, dez subtestes; 26 casos novos. Browser INT03/AM08, Modo Banca e gráficos/exportações nas três resoluções; três experimentos oficiais preservados. ZIP/patch comparados em base limpa e publicação recuperada do GitHub antes da conclusão. Adaptações de transporte e hash rastreáveis estão descritas no relatório, sem exclusão de testes.

Próxima etapa: INT04, correção pontual de contraste/legibilidade dos rótulos identificados na auditoria AM22 (fonte 10 px, cor #758681 sobre branco, contraste aproximado 3,83:1). Reproduzir na versão atual; ajustar cor/tipografia com critério >=4,5:1 para texto normal, testar as três resoluções e preservar identidade, mapa/foco, abertura, Modo Banca e navegação. Não redesenhar o projeto nem avançar para AM18/20/21 nessa etapa.

Windows/BAT/projetor e validação industrial permanecem pendentes. Usar sempre a última entrega confirmada, sem voltar ao ZIP original antigo. Trabalhar sem agentes paralelos, com uma branch, checkpoints, ZIP completo, patch e downloads verificados por etapa.
