# Arquitetura real — Anti-Murphy, versão candidata à banca

## Função do software

O Anti-Murphy é um **protótipo acadêmico de apoio à decisão em Planejamento e Controle da Produção**. Constrói cenários de uma operação fabril a partir de um cadastro sintético, simula uma interrupção, enumera respostas, compara resultados, registra a escolha e permite auditar dados por pedido, posto e cenário.

## Componentes atuais

1. **Motor DES em Python:** `simulation/engine.py` com agenda de eventos em `heapq` e regras de disponibilidade, capacidade e roteiros. `simulation/nexus.py` agrega cenários, políticas, respostas e indicadores. Não descrever a arquitetura atual como dependente de SimPy.
2. **Serviço e persistência local:** `atelier/service.py` coordena `Studio` e pastas do projeto em `workspace`; o servidor HTTP `atelier/server.py` atende `127.0.0.1`, JSON e recursos estáticos. Nenhuma API externa é necessária para a aplicação principal.
3. **Interface integrada:** `atelier/web/index.html`, `app.js`, CSS e `engineering_charts.js` usam HTML, CSS, JavaScript e SVG; a fábrica é **representação lógica 2.5D** (não gêmeo digital físico WebGL).
4. **Auditoria técnica de apoio:** `atelier/technical_audit.py` deriva folga dos pedidos, reconciliação de custos e distinções de gargalo, fila e espera. É um verificador de consistência dos resultados, não uma certificação do motor.
5. **Modo banca:** camada HTML/CSS/JS do frontend. Os seis passos posicionam a câmera temporal em instantes provenientes da reprodução do mesmo experimento; não recalculam a produção.
6. **Ferramentas históricas:** ATLAS/NEXUS e recursos associados permanecem arquivados em `FERRAMENTAS_HISTORICAS` e arquivos `app_classico.py`, `app_nexus_v30.py`, mas sua compatibilidade com o ambiente legado não foi integralmente homologada.

## Indicadores e identidade de custo

- **Makespan:** horário final previsto para concluir a carteira em horas simuladas.
- **Throughput:** unidades concluídas dividido pelo horizonte de makespan, em unidades/hora.
- **SLA:** pedidos concluídos dentro do prazo dividido pelo total de pedidos, em porcentagem. Ponderação por **pedido**, não por unidade.
- **Custo do cenário:** custo de capacidade/recursos no horizonte modelado + penalidades de atraso.
- **Custo da decisão:** custo do cenário de resposta + investimento da intervenção modelado.
- **Diferença estimada:** custo da falha sem resposta − custo da decisão.
- **Gargalo:** heurística de criticidade (utilização, fila e espera); o posto de maior fila ou maior espera pode ser outro. Não é prova de gargalo estrutural.

**Arredondamento:** parcelas e totais podem diferir em R$ 0,01 após formatação independente. O controle de consistência utiliza tolerância, não reinterpreta centavos como evidência de precisão da operação física.

## Condições não integralmente verificadas

- Habilidades e certificações individuais de operadores; recursos de manutenção e disponibilidade de peças.
- Buffers com capacidade finita, transporte intrafabril, restrições ergonômicas e segurança do trabalho.
- Setup dependente da sequência, qualidade, refugo, retrabalho, rendimento conforme, OEE, MTBF e MTTR calibrados.
- Parâmetros validados em fábrica, estudo de sensibilidade com amostragem probabilística representativa ou confirmação empírica de economias.
- Otimização matemática global: as alternativas são **enumeradas**, não solução global certificada.

## Consistência entre documentos

A documentação acadêmica das versões V26 e V30 pode utilizar nomes de módulos e tecnologias históricas. Atualizar a entrega acadêmica e os slides com esta arquitetura real, distinguindo versão histórica, frontend integrado e módulo legado. Não se deve afirmar que Streamlit, React/PixiJS ou SimPy são componentes ativos do fluxo principal se a implementação entregue não os utiliza nessa função.
