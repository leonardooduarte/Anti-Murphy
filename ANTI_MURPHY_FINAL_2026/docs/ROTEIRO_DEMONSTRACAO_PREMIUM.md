# Demonstração recomendada — cinco minutos

**Objetivo:** demonstrar uma ocorrência industrial simulada, quantificar o efeito, explicar uma decisão e registrar suas evidências. Não percorrer todos os menus.

| Janela | Etapa/ação | Fala sugerida |
|---|---|---|
| 0:00–0:35 | **Plano**. Abrir pelo `.bat`, mostrar a fábrica e operação nominal | “O Anti-Murphy apoia decisões de PCP quando um evento altera a programação. Esta fábrica e seus pedidos são um exemplo sintético reproduzível.” |
| 0:35–1:10 | **Falha**. Avançar à parada e mostrar o posto destacado | “A CNC sofre uma parada modelada. O estado operacional e o relógio vêm do motor de eventos discretos.” |
| 1:10–1:50 | **Pedidos**. Mostrar atrasos/SLA, identificando os pedidos afetados | “A consequência é mensurada no cumprimento de prazos e nos tempos calculados por pedido.” |
| 1:50–2:25 | **Intervenção**. Apresentar a resposta escolhida e as premissas | “Esta é uma alternativa simulada. Não afirmamos que peças e técnicos estejam disponíveis sem conferência.” |
| 2:25–3:20 | **Comparação**. Mostrar A/B, CNC parada versus processando, alternar visão de layout se necessário | “Estamos olhando o mesmo instante em duas evoluções possíveis. O sistema calcula como a decisão altera pedidos, custo modelado e conclusão.” |
| 3:20–4:25 | **Evidências**. Explicar o parecer multicritério, inserir justificativa técnica, editar a sugestão e registrar | “A escolha é documentada com custos, SLA, tempo, riscos e reconhecimento dos limites. Ela não é um comando para a fábrica.” |
| 4:25–5:00 | **Relatório**. Clique em Abrir relatório final e mostre o registro concluído | “O estudo termina com um relatório rastreável. Ensaios, gráficos e auditoria ficam disponíveis para aprofundamento na discussão.” |

## Preparação antes da banca

- Abrir o programa no computador efetivamente utilizado e validar o projetor; fechar notificações e abas desnecessárias.
- Confirmar que o navegador permite o relatório em pop-up ou abrir o HTML baixado; se necessário, usar `Ctrl+P` para salvar PDF.
- Testar a justificativa técnica **antes** da apresentação. **Não copiar textos sem verificar os valores do experimento atual.**
- Usar o botão Tela cheia no Modo Banca ou F11 do navegador. No mapa comparativo, começar com **foco no posto afetado** e só abrir o layout completo se solicitado.
- Conferir que “multa”, “investimento” e “custo operacional” são parcelas do modelo; uma suposta economia real exige validação de custos evitáveis.

## Perguntas-prováveis e respostas defensáveis

**Por que uma alternativa é preferível?** Explicar critérios (SLA, custo, makespan) e confrontar a análise de dominância com restrições não modeladas.

**É simulação ou controle de máquina?** Simulação de eventos discretos de um cenário produtivo; não envia comandos de automação nem faz telemetria real.

**O que significa a CNC estar ativa no cenário B?** Que o replay da alternativa inclui operação em andamento naquele instante, não que uma máquina real tenha sido recuperada.

**Vocês mediram economia industrial?** Não. A diferença é estimada sob o modelo de custo declarado; economias efetivas dependem de custos evitáveis e dados de campo.

**E os gráficos e ensaios?** São análises complementares. Mostrar um exemplo de capacidade caso solicitado e consultar a tabela original para auditar números.
