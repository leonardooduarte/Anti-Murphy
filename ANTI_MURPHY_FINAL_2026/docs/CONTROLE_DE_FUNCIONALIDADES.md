# Inventário de funcionalidades — estado verificável

A arquitetura nova não deve substituir recursos avançados silenciosamente. A tabela separa o que está **integrado e testado** na nova aplicação, o que foi **preservado no código clássico** e o que permanece **pendente**.

| Funcionalidade | Situação nesta entrega | Evidência/limitação |
|---|---|---|
| Projetos independentes, duplicação e retomada | Integrada nesta edição | Persistência atômica e isolamento por projeto; teste browser e Python |
| Biblioteca de experimentos e comparação histórica | Integrada nesta edição | Comparação de resultado com SHA-256 do modelo, ressalva se modelos diferentes |
| Programação temporal por posto | Integrada nesta edição | 402 operações de referência visualizadas a partir do registro DES; parada destacada apenas no posto afetado |
| Comparador interativo custo × prazos | Integrado nesta edição | Seleção da alternativa simulada e Pareto derivado dos dados retornados pelo motor |
| Rastreio de ordem no inspetor | Integrado nesta edição | Prazo, término, atraso e trechos de operações do replay calculados pelo motor |
| Edição de recursos, custos, roteiros e pedidos | Integrada | Alteração de quantidade é salva, persistida e recalcula DES (teste Python e navegador) |
| Simulação DES V30.2 | Integrada | Motor `simulation/engine.py`; regressão selecionada |
| Visão da fábrica e filas por posto | Integrada | Replay do motor e animação de processamento; não é modelo cinemático industrial |
| Logo animada na abertura | Integrada | Arquivo oficial de marca + transição CSS, permite pular |
| Incidente programado | Integrada | Início/duração e posto configuráveis, comparação com operação original |
| Intervenções múltiplas | Integrada | 18 alternativas para o modelo de demonstração; dependem da configuração |
| Comparação A/B e replay | Integrada | Duas cenas sincronizadas, estados provenientes do motor; CNC A/B testada em 10h |
| Impacto por pedido | Integrada | `order_impacts` e conclusão por unidade do motor |
| Registros de decisão e evidências | Integrada | JSON persistente com SHA-256 calculado pelo módulo histórico; não equivale a proteção contra adulteração |
| Murphy AI local determinístico | Integrada | Consulta de fatos do experimento, sem API externa |
| Sensibilidade a duração, despacho e robustez pareada | Integrada | Experimentos reais executados pelo motor; hipóteses sintéticas |
| Stress Lab sintético e Goal Seek discreto | Integrados, com escopo reduzido | Ensaios reais de estresse e capacidade; não representam otimização global |
| Diagnóstico operacional e inspeção contextual | Integrados | Alertas calculados, índice de completude cadastral e acesso direto ao posto no replay |
| Opportunity Engine: variações de recursos, setups e despacho | Integrado (versão read-only) | 21 oportunidades no exemplo; todos os candidatos recalculados no DES, resultados não aplicados automaticamente |
| Sensibilidade de recursos e limite de demanda | Integrados | Curvas calculadas com motor V30.2, sob hipóteses sintéticas |
| Monte Carlo e recuperação após falha | Integrados (versão read-only) | 12 sementes e alternativas de recuperação do motor histórico, com ressalvas de investimento/skills |
| War Room / Executive Room completos | Preservados no modo clássico; diagnóstico operacional novo integrado | A interface histórica exige Streamlit e é aberta separadamente |
| Optimization Hub / Opportunity Engine / Portfolio / Trust Center originais | Preservados no modo clássico; oportunidades, sensibilidade e qualidade cadastral agora integradas nativamente | A migração das ferramentas históricas completas ainda é parcial; o ranking de oportunidade não prova viabilidade física |
| Gemini/LLM generativo opcional da versão histórica | Preservado no modo clássico | Requer configuração/API; não integra o novo modo local |
| Modelo compartilhado com modo clássico | Parcial | `app.py` carrega `workspace/projeto.json` na primeira abertura; experimentos/decisões não migram automaticamente |
| Skills individuais, buffers finitos, setups sequenciais | Pendentes de implementação/validação completa | Não classificar alternativa como industrialmente certificada |
| Executável `.exe` Windows sem Python | Não entregue | `.bat` principal abre com Python local; ainda requer teste no Windows |

## Princípio de compatibilidade

**Nunca inferir que “arquivo existe” significa “fluxo integrado”.** O modo clássico está guardado para não perder código e ferramentas, mas a migração integral de suas interfaces e mecanismos operacionais não foi concluída. O ambiente novo executa tarefas reais, não uma demonstração de dados codificados na interface.
