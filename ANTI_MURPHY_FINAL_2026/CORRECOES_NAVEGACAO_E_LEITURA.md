# Anti-Murphy — correções de navegação e leitura

Correção focada no problema mostrado no vídeo `13.mp4`, sem alterar os resultados do motor.

- `Início` e `Voltar` agora são controles explícitos e fixos no topo da aplicação principal. A barra lateral também identifica `Início`.
- Cada área preserva um caminho de retorno. O histórico de páginas do navegador também funciona com as rotas `#simulacao`, `#modelo` etc.
- Contraste e tamanho de fontes secundárias ajustados na interface principal.
- O ambiente clássico Streamlit recebe camada final de contraste específica para fundo claro e um link para o ambiente principal se ele estiver em execução.
- O servidor principal grava a porta local para permitir retorno entre os ambientes e remove a referência ao encerrar.
- Nenhuma alteração no `simulation/engine.py`, custos ou regras de simulação.

## Limites

A interface histórica continua sendo um aplicativo Streamlit separado, e seus muitos temas herdados ainda merecem unificação completa. A correção não é um redesign funcional geral. É necessário testar o ambiente clássico no Windows com as dependências opcionais instaladas.
