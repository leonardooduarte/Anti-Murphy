# Continuidade após verificação final INT04

Aplicativo ainda ac852d8, INT04. Branch verificacao-final-int04 contém somente evidências, roteiro e ferramentas fora do aplicativo; 748 arquivos-base inalterados. Sem agentes paralelos. Regressão 732 aprovados, zero falhas, dez subtestes; três experimentos oficiais preservados. Browser INT01/02/03/04, AM08, gráficos/exportações e Modo Banca passaram nas três resoluções.

Mapa: runner AM15 original passou 15 casos. Instrumento externo repetiu 50 postos mais 15 vezes (cinco por resolução), sem exceder os limites imediatamente ou após 300 ms. A falha anterior não foi reproduzida e sua causa continua indeterminada; não há correção nova de mapa. Monitorar no Windows/projetor real, com foco e volta à planta inteira.

VERIFICAR_AMBIENTE.py aprovado somente no Linux aqui, com flag Windows não preenchida e sem declarar GUI/BAT/projetor testados. Kit inclui VERIFICAR_WINDOWS.bat, MODELO_CICLO_CURTO.json, base-manifest.json, ROTEIRO_WINDOWS_PROJETOR.md, ficha CSV e formulário de ambiente. Usar cópia recém-extraída; o script usa cópia temporária e não modifica a origem.

Próximo passo depende da execução pelo usuário no computador Windows/projetor: devolver resultado_ambiente_*.json e ficha/evidências reais. Não afirmar homologação antes disso. Não criar novas funcionalidades ou ciclos de correção por padrão. Se houver falha, reproduzir e trabalhar exclusivamente nela, sobre a última versão confirmada, preservando backups e entregas verificadas. AM18/20/21 e calibração industrial permanecem escopos adicionais.
