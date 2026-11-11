# Situação e plano para finalizar o Anti-Murphy

Referência: AM04-FRONTEIRA-2026.1 sobre AM10, com as entregas anteriores
preservadas. Este quadro consolida a auditoria anterior e o trabalho realizado;
não substitui uma nova auditoria integrada nem comprova funcionamento universal.

## O que já avançou

Os casos originais AM01–AM06 têm implementação reconstruída e evidências de
verificação. Nesta continuidade, foram aprofundados AM11 (precisão), AM05
(origem e validade dos resultados), AM12 (conflitos de persistência), AM08
(economia arquivada), AM09 (ensaios inviáveis) e AM10 (espaço de capacidade).
Esta versão encerra o complemento conhecido do AM04 sobre empates na fronteira.

Os três experimentos oficiais continuam passando. A regressão atual tem 473
testes aprovados, cinco falhas preexistentes e dez subtestes aprovados. O aumento
de cobertura é evidência localizada, não uma porcentagem de conclusão do produto.

## Antes de uma apresentação com exploração livre

| Prioridade | Trabalho pendente | Critério para encerrar |
| --- | --- | --- |
| 1 | AM17: limitar trabalho solicitado por quantidade × etapas e réplicas; medir/indexar consultas de replay | Recusar carga excessiva antes do cálculo, manter casos normais e medir desempenho com cargas controladas |
| 2 | AM07: replay sem detalhes não deve indicar zero processamento | Estado agregado correto e indicação clara do modo reduzido acima do limite de detalhes |
| 3 | AM16: impedir submissões duplicadas de Monte Carlo em andamento | Uma análise por ação, botão/estado coerentes, recuperação após erro e liberdade de navegação |
| 4 | AM13: identificação exata de pedidos e explicação coerente com o objetivo; AM14: origem do histórico | OP-1 e OP-10 distintos; projeto de origem visível; registros antigos preservados |
| 5 | AM15: legibilidade do mapa e enquadramento para mais postos | Conferência no navegador, nas três resoluções e no projetor, mantendo identidade e zoom |
| 6 | AM19: contratos antigos e artefatos históricos de teste | Explicar e resolver as cinco falhas com contratos funcionais, sem simples remoção de asserções |
| 7 | Complemento de recuperação AM01: arquivos já corrompidos/identificador inválido | Abertura com aviso e recuperação consistente, sem sobrescrever a última origem recuperável |
| 8 | AM22: validação local de Host/Origin | Permitir acesso local válido e rejeitar Host externo, sem quebrar o uso normal |
| Final | Auditoria integrada e ensaio de banca no Windows | Instalar ZIP novo, abrir/salvar/reabrir projeto, A/B, gráficos, exportações, decisão e relatório, nas condições reais da apresentação |

Os itens acima são achados previamente confirmados ou complementos já
identificados. Precisam ser reproduzidos na base então vigente antes de cada
correção; esta etapa só alterou AM04. Não foi executada carga de 25 milhões de
operações, nem demonstrada exploração de DNS rebinding. Perda por queda de
energia também não foi demonstrada; a persistência não promete transação
resistente a toda falha física.

## Depois dos bloqueadores, conforme o uso pretendido

- AM20: importação clássica deve preservar zeros explícitos e aplicar defaults
  apenas à ausência, com validação adequada. É um caminho histórico adicional.
- AM21: normalização do radar e regime de validade da aproximação de
  confiabilidade, também em caminhos históricos/adicionais.
- AM18: organização gradual de JavaScript e folhas CSS. Não é necessário
  reescrever a aplicação nem trocar sua identidade para concluir a banca.
- Calibração industrial e acessibilidade completa são objetivos distintos de
  validar uma demonstração acadêmica com dados sintéticos.

## Estamos perto de finalizar?

Estamos na consolidação para a apresentação: os principais defeitos de cálculo
e interpretação já receberam etapas próprias, com versões recuperáveis. Ainda
há pendências concretas de robustez, rastreabilidade e leitura; não há base para
prometer que uma única correção encerra o projeto, nem para estimar uma
porcentagem ou prazo sem validar os itens restantes.

Próxima etapa recomendada: AM17, começando pela validação do orçamento de
operações antes de simular, com medições controladas. Cada etapa deve manter
branch própria, checkpoint, ZIP completo, patch, testes e continuidade.
Nenhuma dessas correções seguintes foi iniciada nesta entrega.
