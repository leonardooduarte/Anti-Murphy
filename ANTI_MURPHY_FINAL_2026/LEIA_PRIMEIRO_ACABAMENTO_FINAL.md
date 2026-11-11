# Anti-Murphy — Edição Acabamento Final / Banca 2026

Esta atualização refina a leitura dos **gráficos do Laboratório** e das **Ferramentas** a partir da versão "Banca Final — Usabilidade" de 09/11/2026. Não há uma segunda simulação, integração com IA externa ou alteração de fórmulas do motor.

## Iniciar no Windows

1. Extraia o ZIP em uma pasta nova e curta, por exemplo `C:\Anti-Murphy-Banca`.
2. Entre na pasta extraída `ANTI_MURPHY_EDICAO_ACABAMENTO_FINAL_2026`.
3. Execute `INICIAR_ANTI_MURPHY.bat` com duplo clique. Não use o arquivo de outra pasta/versão.
4. Na interface, abra **Ensaios → Otimização de capacidade → Executar experimento**.
5. O gráfico de 12 cenários agora usa os identificadores **01 a 12**, vinculados aos **nomes completos em uma legenda**. Clique em um cenário para ver seus indicadores.
6. Use **Ampliar gráfico** para projetar o resultado e **Esc** ou **Fechar ampliação** para voltar. Os downloads CSV e SVG continuam disponíveis.

## Demonstração à banca

No pitch, use o **Modo banca** para mostrar operação normal → falha → pedidos → intervenção → comparação → decisão e relatório. Ao final, encerre o Modo banca antes de explorar Ensaios e Ferramentas em perguntas dos professores. O modo de apresentação não é obrigatório para executar análises.

## Limitações e testes

Os dados do projeto são sintéticos. A legenda numérica **não altera a ordenação dos cenários, os custos ou o throughput**; ela apenas evita sobreposição de texto. As tabelas e o CSV preservam as observações originais. A ampliação é um painel sobreposto que pode ser fechado, não um segundo motor gráfico.

Testes automatizados com Chromium em 1280×720, 1366×768 e 1920×1080 verificaram a legibilidade dos eixos, seleção, ampliação, troca de indicador e downloads CSV/SVG. A execução real no computador Windows e no projetor da equipe ainda precisa ser verificada. Veja `docs/ACABAMENTO_FINAL_DESIGN_2026.md` e `docs/VALIDACAO_ACABAMENTO_FINAL_2026.md`.
