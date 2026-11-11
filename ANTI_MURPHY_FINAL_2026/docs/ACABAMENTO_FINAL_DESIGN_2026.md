# Revisão final de design — Anti-Murphy (09/11/2026)

## Escopo de mudanças concretas

O vídeo `09_11_c.mp4` mostrou o gráfico de doze cenários de capacidade com os rótulos longos sobrepostos. A revisão soluciona esse problema sem modificar o motor de eventos discretos.

1. **Eixo categórico numerado:** `01…12` para a análise do Laboratório com muitos cenários. Cada número corresponde à mesma linha produzida pelo motor Python.
2. **Legenda de cenários:** apresenta os nomes completos em cartões de seleção com destaque visual e acesso por teclado; ao escolher um deles, o ponto correspondente é selecionado e vice-versa.
3. **Leitura de resultados:** o detalhe do ponto selecionado agora apresenta os indicadores calculados com títulos e unidades, em vez de chaves de código como `makespan_h` e `sla_pct`.
4. **Ampliar gráfico:** botão na barra do gráfico. O gráfico ocupa uma área maior para apresentação, com troca de indicador e exportações preservadas. `Esc` ou o botão de fechar retorna à página.
5. **Ajustes responsivos:** redução da largura da coluna de formulários, revisão de espaçamentos e de contraste, e disposição da legenda em uma, duas ou três colunas conforme a largura.
6. **Acessibilidade:** rótulos completos em `aria-label`, indicadores numerados, foco visível, atalhos usuais e respeito à preferência de movimento reduzido.

O restante foi preservado. O Modo Banca de seis etapas, a comparação A/B da fábrica, a justificativa livre, a conferência monetária não coercitiva, o registro e o relatório **não foram redesenhados** nesta edição. A identidade visual oficial também foi mantida.

## O que deliberadamente não foi implementado

- Gráficos com valores fabricados ou efeitos de animação sem vínculo com a simulação.
- Nova arquitetura, serviços pagos, dependência de npm ou modelo 3D pesado.
- Um novo modo de decisão com critérios obrigatórios de redação.
- Atualizações de bibliotecas ou alterações na lógica do motor sem defeito comprovado.

## Revisão futura, apenas se houver tempo

A legibilidade no projetor físico e o tempo de leitura das telas ainda devem ser avaliados na sala de apresentação. Não recomendo outra reformulação de interface depois dessa verificação; pequenas correções concretas são preferíveis.
