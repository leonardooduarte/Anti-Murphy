# Anti-Murphy — Novo ambiente de trabalho integrado

**Mudanças efetivas nesta entrega**

- Novo programa local, com interface única, sem exigir Streamlit/React/npm para uso principal; abre automaticamente o navegador a partir de `ABRIR_ANTI_MURPHY.bat`.
- Motor de simulação V30.2 (`heapq`) preservado: cálculo real de operação nominal, incidente e respostas.
- Abertura animada com arquivo oficial da marca e opção de pular; animações operacionais coerentes com os registros da simulação.
- Interface responsiva com seis áreas persistentes de trabalho: Simulação, Modelo, Análise, Ensaios, Decisões, Registros.
- Editor funcional de postos, recursos, roteiros e ordens de produção, com salvamento local e recomputação.
- Simulação visual com máquinas individualizadas, fila, seleção, replay temporal e comparação A/B simultânea.
- Análise de múltiplas alternativas simuladas (18 no exemplo) e consequências para cada pedido.
- Seis tipos de ensaio: duração, despacho, robustez pareada, meta de prazo, estresse sintético e capacidade discreta.
- Murphy local determinístico para perguntas sobre o experimento; registro de decisão com evidências e arquivamento local.
- Arquivos históricos mantidos e opcionais via `FERRAMENTAS_CLASSICAS.bat`, para uso das ferramentas ainda não migradas.

**Não concluído:** migração de todas as ferramentas ATLAS/NEXUS históricas à mesma interface; restrições industriais avançadas; homologação do executável Windows sem Python; avaliação formal com usuários reais.

**Testes:** 79 regressões Python selecionadas, 10 testes novos de fluxo, Chromium nas resoluções 1366 e 1920 com API do serviço Python in-process, HTTP GET/POST locais, sintaxe JS. Confira `docs/VALIDACAO.md`.
