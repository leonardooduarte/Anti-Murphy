# Entrega para apresentação — 5 de novembro de 2026

## Novidades funcionais

1. Ajuda contextual acionável em sete áreas, com textos específicos para modelo, simulação, análise, ensaios, ferramentas, decisões e histórico.
2. Percurso de seis etapas **opcional**, não bloqueante, encerrável e com retorno à seção original.
3. Explicações dos indicadores; distinção entre custo do cenário e custo da intervenção.
4. Rastreio do pedido com espera observada, atraso previsto e comparação dos cenários derivada dos registros de operação.
5. Sumário de interpretação da alternativa selecionada na Análise.
6. Marcos temporais clicáveis com timestamps de eventos do motor, sem simular transporte não modelado.
7. Relatório imprimível (pode ser salvo como PDF pelo navegador) com custos, entregas, pedidos e hipóteses.
8. Ajustes de tipografia no mapa, cor de fundo, contraste, densidade e disposição em telas de altura limitada.
9. Indicadores dinâmicos de postos processando, unidades em fila e paradas no próprio mapa.
10. Eliminação da animação de conexões que poderia sugerir transporte físico cronometrado.

## Preservação

- Simulação com motor `heapq` original, modelo editável, alternativas e análise de pedidos, projetos, experimentos, laboratórios, análises avançadas, Murphy local, decisões e registros.
- Identidade visual oficial e animação de abertura permanecem presentes.
- Ferramentas antigas continuam disponíveis separadamente em `FERRAMENTAS_HISTORICAS`.
- Um único inicializador principal `INICIAR_ANTI_MURPHY.bat`, Python padrão sem npm para o ambiente atual.

## Limitações

A interface principal foi verificada no Chromium usando HTML/CSS/JS reais e resposta do serviço Python fornecida por uma ponte de teste. As rotas HTTP reais foram verificadas separadamente. **A execução de toda a UI servida por HTTP dentro do Chromium foi bloqueada pela política do ambiente de teste**; não significa que o programa falhou, mas esta combinação ainda precisa ser homologada no Windows do usuário. Também não foi testada aqui a interface clássica Streamlit. Não há alegação de 60 FPS ou validação industrial real.
