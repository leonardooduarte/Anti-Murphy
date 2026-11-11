# Anti-Murphy — alterações da versão de revisão editorial

## Experiência de produção
- Substituição de títulos de efeito por linguagem objetiva de PCP.
- Composição editorial clara para operação e resultados.
- Fábrica central com máquinas ampliadas, indicadores de estado e topologia do modelo.
- Comparação A/B com wipe, replay, seleção de posto e horários do motor.
- Carteira de pedidos com conclusão prevista de A/B e sinalização de atrasos.
- Pré-posicionamento do replay em momento operacional relevante; usuário pode retroceder.
- Hierarquia tipográfica e legibilidade melhoradas em 1366 e 1920 px.

## Estrutura e inicialização
- Um único `INICIAR_ANTI_MURPHY.bat` na raiz.
- Configuração do experimento, consulta determinística e decisão documental na barra lateral.
- Workspace V30.2 anterior preservado.
- Sem instalação Node/npm na execução normal.
- Tema Streamlit consistente com a marca.

## Engenharia
- Base V30.2 e contratos de simulação preservados.
- Avisos de viabilidade desconhecida e custo não modelado mantidos.
- Dados exportados pelo motor e reconstruídos pelo replay.
- 121 testes Python (não dependentes de Streamlit) passaram.
- Replay standalone testado com Chromium em três resoluções.
- Execução Streamlit no Windows ainda não homologada.
