# Revisão de qualidade — Anti-Murphy · novembro de 2026

Esta revisão parte da edição **Estúdio Industrial**, sem trocar o simulador nem retirar telas.

## Alterações implementadas

1. **Custos reconciliados na interface:** Análise, Painéis → Desempenho, Decisões e relatório usam uma explicação explícita de **custo operacional + multas + investimento = custo da decisão**. A referência de economia é sempre **falha sem resposta**, não operação nominal.
2. **Murphy local mais contextual e rastreável:** perguntas de custo, investimento, viabilidade, pedidos específicos e escolha entre alternativas são respondidas com dados do experimento em memória; caso o pedido não exista, não é inventado. Ações contextuais levam aos painéis, à análise ou à fábrica.
3. **Registros navegáveis de operações:** novo painel expansível na Simulação. Lista inícios, conclusões e parada a partir dos horários já presentes no replay; clicar leva ao instante e ao posto correspondente. Não modela transporte físico.
4. **Fila com prioridade visual fundamentada:** peças de ordens com atraso *previsto pelo motor* recebem destaque. É feito por cenário e por alternativa selecionada, sem projetar risco a partir de heurísticas próprias da UI.
5. **Guias antes de executar experimentos:** os seis ensaios do Laboratório e as análises avançadas mostram finalidade, interpretação e ressalvas, com ação de executar diretamente do painel.
6. **Contraste corrigido:** valores dos quatro indicadores da Análise estavam escuros sobre fundo grafite. Corrigida a leitura e refinado o layout em 1280×720, 1366×768 e 1920×1080.
7. **Animação de alterações de fila:** entrada de blocos apenas quando a composição da fila é atualizada pelo estado simulado; funcionamento visual da máquina permanece atrelado ao processamento. Respeita `prefers-reduced-motion`.
8. **Relatório técnico mais explícito:** composição econômica da intervenção consta também da versão imprimível.

## Preservação funcional

Os arquivos `simulation/engine.py`, `simulation/replay.py`, `simulation/decision_lab.py`, `simulation/nexus.py`, `atelier/server.py` e os SVGs da marca não foram modificados. Os projetos, experimentos, dashboards, editor de roteiros, ajuda, tutorial, decisão, relatórios e ferramentas históricas permanecem no pacote. A camada de serviço `atelier/service.py` foi alterada exclusivamente para incorporar explicações determinísticas do Murphy. A interface `atelier/web` foi alterada para os novos componentes.

## O que NÃO está concluído

- **Módulos históricos ATLAS/NEXUS:** continuam em `FERRAMENTAS_HISTORICAS` e não integram totalmente a nova navegação.
- **Restrições físicas:** skills de operadores, buffers finitos e setups dependentes da sequência permanecem incompletos. A interface deixa isso claro.
- **Validação Windows:** o inicializador contém abertura automática do navegador, mas não foi executado neste ambiente Linux.
- **Gêmeo digital físico:** não há conexão com máquinas reais; a visualização representa um modelo sintético.
- **Animações 3D de alta fidelidade:** a fábrica permanece uma representação SVG 2.5D com movimento funcional, não um renderizador físico 3D.

## Decisão de arquitetura

Manter execução local Python sem npm ou React obrigatório para o usuário final. Proteger estabilidade, rastreabilidade e a experiência funcional em vez de introduzir nova stack perto da apresentação.
