# Anti-Murphy — Revisão de produto e visualização industrial

## Objetivo e referência

Base desta edição: **Anti-Murphy — Edição de apresentação guiada 2026**. A aplicação principal continua em `atelier/server.py` + `atelier/web` e usa o motor original de eventos discretos (`simulation/engine.py`). Os dados de produção são sintéticos; a animação não é um gêmeo digital conectado a sensores reais.

## Oito frentes do redesign: estado verificável

| Frente | Entregue nesta edição | Pendente / restrição |
|---|---|---|
| 1. Sistema visual e fundo | Nova paleta industrial em `atelier/web/design_vnext.css`; fundo cinza-azulado frio; hierarquia de textos, separadores e componentes consistente | Revisão visual de todas as telas históricas Streamlit |
| 2. Fábrica | Equipamentos SVG mais visíveis, bases técnicas, telemetria de estação, detalhe visual do equipamento selecionado, foco em máquina e tela ampliada | Geometrias industriais não são CAD real nem 3D físico |
| 3. Movimento operacional | Partes móveis ligadas ao estado `processing`, indicação de interrupção, transições de fila apenas quando a composição muda, progresso temporal ligado a operações; respeita movimento reduzido | Não representa transporte físico ou ocupação espacial de chão de fábrica |
| 4. Ambiente de simulação | Replay próximo do mapa e disponível antes da área de pedidos; visualização ampliada e inspeção contextual do posto | Requer confirmação de ergonomia no Windows do usuário |
| 5. Gráficos | Histograma de cumprimento de prazos das execuções Monte Carlo; comparador A/B de avanço de cada ordem, fila e estado das máquinas | Os demais gráficos históricos não foram totalmente redesenhados |
| 6. Ferramentas históricas | Preservadas em `FERRAMENTAS_HISTORICAS`; funcionalidades integradas da aplicação principal permanecem acessíveis | Migração completa de War Room e Optimization Hub para a mesma UI continua pendente |
| 7. Murphy AI | Mantém o assistente local determinístico, análises de evidência e sugestões contextualizadas existentes; não foram alterados indicadores | Não foi criado um agente autônomo nem chamadas a modelos externos |
| 8. Telas e identidade | CSS aplicado às sete áreas principais, com revisão visual de operação, comparação, análises e ferramenta Monte Carlo | Homologação visual da interface clássica pendente |

**Regra de compatibilidade:** os módulos `simulation/engine.py` e `atelier/service.py` são idênticos aos da edição de referência, confirmados por comparação SHA-256 e `diff`. Os contratos de simulação não foram enfraquecidos.

## Projeto de interface

- Identidade: `#1D292D`, `#FF681B` e `#F7F7F3` preservadas; o fundo geral passou a `#E9EDF0`, evitando o cinza esverdeado anterior.
- Operação: “Mapas da produção / inspeção”, não uma frase de marketing. Ações principais permanecem **Configurar incidente** e **Analisar alternativas**.
- O botão **Focar neste posto** amplia visualmente a máquina selecionada, sem alterar o estado da simulação.
- **Ampliar mapa** usa a API Fullscreen nativa; sem player ou instalação de bibliotecas.
- No comparador, as ordens exibem o progresso em A e B, enquanto o inspetor apresenta fila e estado no mesmo instante.
- A área de Monte Carlo mostra a **distribuição real do SLA das execuções**, não uma distribuição teórica inventada.

## Testes executados

1. **107 testes Python aprovados + 10 subtestes** em suítes selecionadas (`atelier/tests`, `contract_tests` e regressões de decisões e simulação).
2. `node --check atelier/web/app.js`: sintaxe do JavaScript aprovada.
3. O serviço local foi iniciado e respondeu HTTP 200 para `/`, `/app.js`, `/design_vnext.css` e `/api/state`.
4. Teste visual Chromium **1366×768** e **1920×1080**: sete áreas acessíveis, ajuda contextual, percurso guiado, rastreio de pedido, foco do equipamento, comparação A/B, Fullscreen e histograma Monte Carlo sem erros JavaScript nos percursos realizados.
5. A validação de UI utilizou um documento HTML autocontido com **estado extraído do Studio Python verdadeiro** e transporte HTTP simulado, pois o navegador automatizado do ambiente bloqueia o acesso direto a endereços locais. As rotas HTTP foram verificadas separadamente.
6. A coleta de `tests/test_nexus_v30.py` não foi possível neste ambiente por exigir o pacote opcional `streamlit`; essa suíte não foi contabilizada como aprovada.

**Não verificado:** inicialização e desempenho no Windows, FPS de hardware do usuário, todas as telas clássicas e validação operacional industrial de restrições de skills, buffers e setups.

## Referências que informaram a direção

- ISA-101, princípios de projeto e ciclo de vida de HMI industrial: https://www.isa.org/standards-and-publications/isa-standards/isa-101-standards
- AnyLogic, animação vinculada a estados do modelo: https://anylogic.help/anylogic/presentation/index.html
- Nielsen Norman Group, divulgação progressiva de ferramentas avançadas: https://www.nngroup.com/articles/progressive-disclosure/

Estas referências informaram **decisões de projeto**, não certificam o software em relação a normas industriais.
