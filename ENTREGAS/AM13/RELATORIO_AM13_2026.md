# AM13 — pedidos completos e critério de escolha

Base AM16: 3b35f3068fbd918dde13e45645b07237117b2c39. Branch correcao-am13-murphy.

Reprodução na versão anterior: perguntar sobre OP-10 com IDs OP-1 e OP-10 devolvia o prazo de OP-1 (before.log, copiado em reproduction.log). A busca utilizava substring e dependia da ordem de cadastro.

A função explain em atelier/decision_explainer.py passa a procurar o identificador completo escapado, com fronteiras que impedem confusão por prefixo, extensão e sufixo. Pontuação de frase continua permitida. Mantém normalização de caixa e acentos existente. Quando há mais de um identificador possível, pede um único pedido, sem selecionar o primeiro arbitrariamente. IDs desconhecidos do padrão OP continuam identificados como ausentes. Não se implementou interpretação irrestrita de qualquer linguagem natural.

Perguntas de escolha reutilizam a alternativa leader produzida pelo motor e explicam a prioridade ativa: custo, entrega ou pedido prioritário. Não recalculam nem reranqueiam alternativas. Quando não existe líder para entrega/prioritário, a resposta informa a ausência de recomendação. Para custo sem líder, pode apresentar comparação descritiva de menor custo, explicitando que o motor não recomendou uma resposta. Não afirma ótimo global nem viabilidade industrial. Resultados continuam somente leitura.

Produção alterada exclusivamente em atelier/decision_explainer.py, função explain. Novos testes test_am13_identity.py e browser_am13.py. Nenhuma alteração no motor, fórmulas, recomendações calculadas, seleção, persistência, identidade visual ou abertura.

Regressão: 533 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados. Onze testes novos cobrem prefixos, pontuação, IDs com barra/ponto, pedidos desconhecidos, múltiplos identificadores e os três objetivos. Três experimentos oficiais mantidos: SLA 100/40/100%, decisão R$12.113,00 e economia R$4.103,68. Navegador nas três resoluções verifica perguntas OP-1/OP-10, inexistente e ambígua, sem alterar run_id nem registrar decisões. O ensaio seleciona explicitamente uma alternativa para ter comparação individual; quando nenhuma está selecionada, o Murphy continua informando que ela não está disponível. As cinco falhas anteriores estão detalhadas em regression.log; nenhum teste foi excluído.

Limites: mantém a normalização de caixa e acentos; identificadores que colidem após normalização são tratados como ambíguos, não resolvidos por suposição. A mensagem de múltiplos pedidos não produz comparação lado a lado; é um pedido de esclarecimento para evitar atribuir dados incorretos. O assistente histórico de fallback e a navegação por atalhos mantêm seus contratos anteriores. AM14 (origem do histórico) não foi antecipado.

ZIP e patch foram extraídos e comparados por SHA-256. O aplicador exige a base exata e cria pasta nova. Testes direcionados foram reexecutados no ZIP extraído. Fonte e downloads publicados são conferidos no GitHub. Instale o pacote completo em pasta nova; versões anteriores preservadas. Windows/projetor ainda precisam de validação local.

Reproduzir em cópia: python -m pytest tests contract_tests atelier/tests -q; python -m pytest tests/test_am13_identity.py -q; python -m atelier.tests.validacao_experimentos_banca; python -m atelier.tests.browser_am13. Navegador usa Playwright/Chromium em Linux. Próxima recomendação: AM14, projeto de origem no histórico; depois AM15, legibilidade da fábrica. Demais pendências da AM17 permanecem abertas.
