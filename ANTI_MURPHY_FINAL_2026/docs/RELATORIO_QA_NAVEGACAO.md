# Verificação — Navegação e legibilidade

## Fonte
Vídeo `13.mp4`, fornecido pelo usuário. Observados retorno pouco evidente, troca de ambiente entre aplicação HTML e Streamlit clássico, e legendas claras quase invisíveis sobre superfícies claras.

## Testes executados
- `pytest`: **85 testes Python aprovados**, incluindo inicialização, motor, decisões, replay, contrato e exportação.
- `atelier/tests/browser_quality.py`: **2 resoluções** (1366×768 e 1920×1080), fluxo de seleção de alternativa, A/B, animação, edição de pedido, ensaio, Murphy local e registro, sem erro de JavaScript.
- `atelier/tests/browser_nav_qa.py`: **3 resoluções** (1280×720, 1366×768 e 1920×1080), transição por cinco áreas, voltar ao início, voltar à área anterior, botão de voltar do navegador, verificação de overflow e textos gerais, sem erro de JavaScript.
- `atelier/tests/browser_classic_css_qa.py`: cálculo de contraste em amostras estáticas com CSS legado + CSS do shell + correções. Razões texto/fundo: 10.9:1 (texto principal), 6.12:1 (legenda), 9.28:1 (rótulo), 13.89:1 (título), 9.32:1 (texto do painel escuro).
- `python -m compileall` e `node --check`: aprovados.

## Limites
- `Streamlit` **não está instalado neste ambiente**: não foi possível abrir e inspecionar visualmente todos os módulos históricos. Os contrastes das amostras estáticas foram testados, mas não é prova de que todas as telas clássicas estejam legíveis.
- Windows não disponível aqui, então não afirmamos que o inicializador foi homologado nesse sistema.
- Recursos históricos seguem em aplicativo separado; este pacote corrige orientação e contraste, não é ainda o redesign completo do portfólio.
- A ponte do navegador automatizado para o serviço Python usa substituição de transporte porque o navegador desta execução bloqueia HTTP local; o serviço real e o JS de produção foram utilizados.
