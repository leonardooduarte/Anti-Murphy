# Roteiro de cinco minutos — Anti-Murphy

## Apresentação operacional (modelo sintético, com resultados reproduzidos)

| Intervalo | Tela/ação | Mensagem a transmitir |
|---|---|---|
| 0:00–0:40 | Introdução e **Modo banca → Plano** | Problema: imprevistos alteram filas, sequenciamento e prazos; a decisão precisa ser fundamentada. |
| 0:40–1:15 | **Falha** | CNC para no instante modelado de 4 h; o replay mostra o estado calculado, não uma animação inventada. |
| 1:15–1:55 | **Pedidos** | Sem resposta, o exemplo passa de 100% para 40% de SLA; identificar pedidos afetados. |
| 1:55–2:35 | **Intervenção** | Manutenção expressa é uma alternativa hipotética, condicionada à viabilidade real. |
| 2:35–3:35 | **Comparação** | Duas trajetórias; três atrasos versus zero; diferença econômica modelada de R$ 4.103,67 e composição de custos, não dinheiro realmente poupado. |
| 3:35–4:45 | **Evidências** | Exibir o parecer multicritério, justificar a escolha com uma frase verdadeira, registrar riscos e salvar. |
| 4:45–5:00 | **Gerar relatório** | Mostrar evidência impressa e ressalvas. Encerrar. |

## Falar o essencial

> “O Anti-Murphy é um protótipo de apoio à decisão em PCP. Ele compara consequências de respostas simuladas a uma falha, registrando impactos em pedidos, custo modelado e prazo. O mecanismo de eventos discretos é verificável, mas as previsões ainda não foram calibradas em uma indústria real.”

## Observações técnicas importantes

- Na configuração padrão, a manutenção expressa é a **única resposta que atinge integralmente os critérios modelados**; isso não demonstra solução ótima global.
- Se o professor alterar prazos, orçamento ou metas e a escolha passar a ser **dominada**, demonstre o aviso e clique em **Examinar alternativa concorrente**. Isso é evidência de pensamento crítico, não uma falha do motor.
- Nem menor makespan nem menor custo isolados são suficientes para selecionar uma intervenção.
- O mapa representa **lógica do processo**, não distâncias, transportes nem movimentação física cronometrada.
- O registro salva **a avaliação humana de uma resposta simulada**; não aciona uma máquina nem transforma o modelo em um sistema de controle real.

## Perguntas prováveis e respostas técnicas

**“Como é determinada a melhor alternativa?”** O motor enumera alternativas e usa critérios de objetivo, SLA, custo, orçamento e regras da simulação. O parecer multicritério adicional compara custo de decisão, makespan e SLA entre opções elegíveis, mas não afirma ótimo global.

**“Por que o custo muda quando o makespan cai?”** O modelo contabiliza custos operacionais de capacidade ao longo do horizonte, penalidades e investimento da intervenção. A composição é apresentada e deve ser reconciliada; não é um demonstrativo de caixa industrial.

**“Como saber se o operador realmente pode ser realocado?”** Não sabemos sem dados adicionais de habilitação, disponibilidade e regras físicas. A ferramenta analisa possibilidades modeladas e pede verificação industrial antes de agir.

**“Onde estão os testes?”** Há testes de unidade, integração HTTP, interface em três resoluções e três experimentos reproduzíveis com conferências independentes dos totais e cronologia.

**“Por que o Monte Carlo às vezes mostra o mesmo SLA?”** A variação de parâmetros testada pode não mudar se um pedido cumpre ou não o prazo. Isso não prova ausência de incerteza operacional, especialmente sem calibração histórica.
