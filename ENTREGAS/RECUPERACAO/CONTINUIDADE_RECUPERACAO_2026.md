# Continuidade — RECUPERACAO-2026.1

Base e9ba7a2 (prioridade opcional sobre AM19). Branch correcao-recuperacao-local, checkpoint 0ff38d2. Corrige exclusivamente abertura com dados inválidos: valida candidato completo, recupera checkpoint antes do modelo básico e informa fallback. Abertura com recuperação não regrava originais nem checkpoint; salvamento explícito permanece permitido e limpa aviso após sucesso. 20 testes novos; regressão 597 aprovados, zero falhas, dez subtestes; três experimentos preservados; recuperação, gráficos/exportações e Modo Banca nas três resoluções.

ZIP e patch são conferidos por extração e comparação de hashes; patch exige a versão de prioridade e cria pasta nova. Instale em pasta nova e preserve sua versão e seus projetos. Consulte relatório para limites do fallback legado e da preservação após salvamento explícito. Windows/BAT/projetor ainda pendentes.

Próxima etapa recomendada: AM22, validação local de Host/Origin, reproduzindo o achado na base desta entrega. Não iniciada. Depois, auditoria integrada e ensaio real no Windows/projetor, incluindo os componentes visuais recebidos. Não presumir que documentos antigos de status reflitam o último commit. Continuar sem agentes paralelos, uma etapa por branch, checkpoints, ZIP, patch e links verificados.
