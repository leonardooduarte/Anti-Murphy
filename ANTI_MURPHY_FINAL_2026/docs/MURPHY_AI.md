# Murphy AI: contrato real

## Camadas

1. **Motor DES:** determina tempos, filas, capacidade, custos e resultados. Usa a mesma carteira e a mesma semente para alternativas.
2. **Analista local:** regras para reconhecer posto, duração, início, orçamento, SLA e intenção. Formula hipóteses como hipóteses e lê o resultado assinado. Não é um modelo de linguagem local.
3. **Modelo generativo opcional:** interpreta um pacote de evidências e pode emitir `prepare_experiment`; nunca recebe uma ferramenta para aplicar mudanças físicas.
4. **Interface e autorização:** revisa parâmetros, verifica assinaturas e executa ferramentas Python permitidas somente por botão.

## Ferramentas implementadas

| Ferramenta | Resultado | Aprovação |
| --- | --- | --- |
| Comparar respostas ao incidente | Executa as alternativas enumeradas e publica uma única análise. | Botão dedicado na proposta. |
| Sensibilidade pareada | 8 pares de incidentes/respostas, sementes 700–707, com economia líquida. | Botão dedicado na proposta. |
| Ler evidências existentes | Explica o que já foi calculado, com filtros. | Não executa um novo experimento. |

O workspace calcula o cenário nominal para mostrar o estado inicial. Essa inicialização não é um novo experimento de falha disparado pelo chat.

## Aprovação e estado

Cada proposta inclui modelo, política vigente, parâmetros, ferramenta, alternativa de sensibilidade quando aplicável, nonce e identificador. A execução confere o conteúdo, o contexto e se a autorização já foi consumida. Uma mudança no modelo ou orçamento invalida planos antigos. Uma solicitação explícita posterior pode criar nova autorização para repetir os mesmos parâmetros.

A confirmação é exclusivamente no botão do aplicativo; escrever “autorizo” no chat não o substitui. Aprovar é executar uma simulação, não executar a decisão na fábrica.

## Continuidade e restrições

Um orçamento informado após uma proposta ainda pendente preserva o posto e os tempos dessa proposta. Resultados exibidos antes da autorização continuam sendo os do experimento anterior e são identificados assim. Um pedido de comparação sobre dados existentes não dispara uma simulação redundante.

No modo local, textos fora das intenções conhecidas recebem uma resposta limitada ao contexto disponível. Não há compreensão irrestrita de linguagem, busca web ou acesso automático a arquivos e equipamentos.

## API opcional

A integração usa o SDK oficial OpenAI, `responses.create`, `store=False`, timeout e schema estrito com `additionalProperties=False`. Modelo e chave são configuráveis. A chave permanece na sessão ou no ambiente e não entra em exportações. O pacote numérico exclui nomes de clientes; as últimas mensagens da conversa são enviadas, o que pode incluir dados escritos pelo usuário.

A integração foi testada com um mock do SDK para verificar que uma chamada de ferramenta apenas produz uma proposta e que não inclui a chave no pacote. Nenhuma chamada paga, latência de provedor ou disponibilidade de modelo foi validada nesta entrega. Em caso de erro, o aplicativo oferece análise local e não imprime a exceção de rede com detalhes da requisição.

Referências de implementação: documentação oficial de [function calling](https://developers.openai.com/api/docs/guides/function-calling) e [Responses](https://developers.openai.com/api/reference/resources/responses/methods/create). As referências descrevem o protocolo; não constituem validação da aplicação.


## Integração na sala de operação 30.1
A conversa está no painel contextual da operação. Os contratos e as ferramentas descritos acima foram preservados; no novo fluxo a execução usa respostas temporizadas e replicações com a mesma TimedAction. A autorização também incorpora o horário da resposta e o experimento vigente. O plano mostra a alternativa de sensibilidade, os custos de implantação e as restrições. A curva de quando agir tem um comando explícito próprio na aba Respostas.

O modo local continua sendo por regras. A nova interface não afirma compreender arbitrariamente qualquer pedido. OpenAI é opcional e configurável, com chamada real ainda não verificada.


## Integração na experiência 30.2

A área Murphy apresenta explicações curtas da resposta em exame. A sugestão do ranking pode ser outra. A conversa visual mostra até quatro mensagens do experimento atual, com até três linhas de alternativas por resposta.

Os planos incluem prioridade, pedido específico, semântica de orçamento, tempo de resposta e assinatura do experimento. Alterar esses critérios exige preparar outro plano. Pedir R$ 0 prepara um limite zero; pedir explicitamente orçamento sem teto prepara investimento ilimitado.

“Verificar variação” prepara oito execuções pareadas da resposta selecionada. O plano permanece revisável e só executa com o botão de autorização. O resultado é uma faixa observada, sem interpretação como probabilidade industrial.

O modo generativo continua opcional. A interface identifica o modo local por regras e o retorno local quando o provedor não responde. Nenhuma API paga foi utilizada na verificação desta entrega.
