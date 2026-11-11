# Anti-Murphy — Guia rápido de demonstração

## Antes de apresentar

1. Extraia o ZIP em uma pasta nova. No Windows, dê dois cliques em `INICIAR_ANTI_MURPHY.bat`.
2. O aplicativo abre localmente no navegador (necessário Python 3.10+). Mantenha a janela do processo aberta.
3. O projeto principal contém um exemplo **sintético** com cinco postos e uma falha programada na CNC. Os resultados são calculados pelo motor de eventos discretos.
4. Para explorar o programa sem alterar dados, clique em **Conhecer o software**. O percurso é opcional; botão **Ajuda** mostra instruções de cada área.

## Roteiro sugerido de aproximadamente 2 minutos

**0:00–0:20 — Modelo:** mostre os postos e pedidos editáveis. Explique que os roteiros e os prazos alimentam o simulador. Não é uma animação de fábrica conectada a sensores.

**0:20–0:50 — Simulação:** execute o replay e salte ao marcador **Parada · CNC**. Inspecione os recursos, a fila e um pedido na carteira. Clique em **Por que este resultado?** para examinar a maior espera observada no roteiro; a explicação é descritiva, não prova de causalidade completa.

**0:50–1:20 — Análise:** abra **Analisar alternativas**. Clique em diferentes respostas e mostre os indicadores de custo e prazo. O cenário demonstrativo costuma mostrar pedidos atrasados sem intervenção e uma resposta que reduz o atraso sob hipóteses sintéticas. Os valores concretos dependem do modelo e devem ser lidos na tela.

**1:20–1:40 — Comparar:** na Simulação, escolha **Comparar**. Mostre a divisão visual e use os marcos temporais para observar os estados dos dois futuros no mesmo instante.

**1:40–2:00 — Explicação e relatório:** na Análise, selecione **Entender os atrasos e diferenças**. Em seguida, abra **Relatório técnico** para visualizar um documento imprimível com três cenários, efeitos por pedido e ressalvas. O Chrome permite salvar como PDF pela opção Imprimir.

## Se houver mais tempo

- Demonstre a **Biblioteca de experimentos**, que guarda comparações do projeto.
- Visite **Ensaios** e **Ferramentas** para mostrar sensibilidade, demanda, Monte Carlo e diagnósticos.
- Abra **Decisões** e registre uma justificativa. Isso salva evidências localmente e **não executa comandos em máquinas**.

## Perguntas frequentes

**O Anti-Murphy controla fábricas reais?** Não. É uma ferramenta local de simulação e apoio à decisão, com modelo sintético configurável.

**O Murphy é uma IA generativa?** A análise local funciona sem API e usa resultados do simulador. Recursos generativos são opcionais e não são necessários para esta demonstração.

**A resposta é comprovadamente viável na indústria?** Não automaticamente. Skills individuais, setups dependentes de sequência, transporte físico e capacidade finita de buffers podem não estar integralmente modelados.

**O custo da resposta é completo?** Só para os itens e investimentos cadastrados. Não presuma economia líquida real sem verificar o conjunto de custos.

**Posso compartilhar o ZIP com colegas?** Sim, no contexto de colaboração acadêmica. Cada cópia é local; os dados de projetos e registros são gravados na pasta `workspace` gerada no computador de quem executa.
