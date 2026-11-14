# Continuidade — INT01-2026.1

Aplicativo base AM22 8599a5c; branch criada sobre a auditoria integrada c7e023c, que não alterou o aplicativo. Correção: correcao-int01-importacao-regra, checkpoint 40d049d. Importação JSON preserva dispatch_rule explícita EDD/SPT/FIFO, ausência mantém a regra atual com aviso e inválidos são recusados. Falhas e conflitos não publicam estado parcial. Modelo importado não é restauração de todo um experimento.

682 testes aprovados, zero falhas, dez subtestes; 18 casos novos. Três experimentos oficiais preservados. Importação/download/upload em outro projeto, reabertura, legado e inválidos passaram nas três resoluções. AM05, Modo Banca, gráficos e exportações novamente conferidos. ZIP/patch extraídos e comparados; GitHub recuperado e conferido antes da conclusão. VERSAO_INT01.json estende a cadeia de hash autorizada sem modificar referências anteriores.

Próxima etapa recomendada: INT-02, precisão da auditoria por pedido (atelier/technical_audit.py, summarize_audit). Reproduzir o caso de 0,001 h da auditoria integrada, consumir completion_h/lateness_h precisos e aplicar fallback legado explícito. Não alterar o motor, fórmulas nem outros achados nessa etapa. Base deve ser a entrega INT01 mais recente confirmada, nunca AM22 antiga se houver uma sucessora.

Depois: INT-03, documentos inválidos na biblioteca; INT-04, contraste/legibilidade pontuais. Windows/BAT/projetor continuam pendentes. AM18/20/21 e validade industrial não foram resolvidos por esta importação. Continuar sem agentes paralelos, etapas pequenas, checkpoints, ZIP completo, patch, relatório e downloads verificados.
