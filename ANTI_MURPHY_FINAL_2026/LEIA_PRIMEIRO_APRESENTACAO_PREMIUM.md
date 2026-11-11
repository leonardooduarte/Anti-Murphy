# ANTI-MURPHY · MODO BANCA PREMIUM · 09/11/2026

**Esta é a edição de apresentação desenvolvida a partir da revisão funcional de 09/11/2026.**

## Como iniciar no Windows

1. Extraia o ZIP inteiro em uma nova pasta, sem substituir versões antigas.
2. Dê dois cliques em **`INICIAR_ANTI_MURPHY.bat`**.
3. Quando abrir o navegador local, clique em **Modo banca**. Não são necessários Node.js, npm, Zep, MiroFish ou API de IA.
4. Percorra as etapas **Plano → Falha → Pedidos → Intervenção → Comparação → Evidências**.
5. Na etapa **Comparação**, observe as duas fábricas no mesmo instante e use **Ver layout completo / Ampliar posto afetado** para alternar a visão.
6. Na etapa **Evidências**, insira e **revise** a sugestão de justificativa, informe responsável, valide riscos, confirme o reconhecimento das limitações e clique em **Registrar decisão**.
7. Depois do retorno positivo do serviço, clique em **Abrir relatório final** para imprimir ou salvar como PDF. Caso o navegador bloqueie a janela, um relatório HTML será baixado. Utilize **↺ Reiniciar** para ensaiar outra vez.

**Teclas úteis:** setas ←/→ avançam/retrocedem entre etapas, exceto quando o cursor está em um campo de texto; botão **Tela cheia** melhora a projeção quando permitido pelo navegador; Esc sai do Modo Banca ou da tela cheia conforme o estado do navegador.

## O que mudou nesta revisão

- **Divulgação progressiva:** indicadores da resposta não são mostrados antecipadamente no Plano e na Falha.
- **Comparação A/B legível:** duas cenas independentes simultâneas, com mesma referência temporal, identificação clara de cenário e foco no posto da ocorrência. O modo normal mantém a comparação original com divisor móvel.
- **Leitura contextual em tempo real:** cada cenário mostra o estado e a fila do posto afetado, extraídos do replay do motor.
- **Registro técnico guiado:** sugestão editável produzida a partir das métricas calculadas, sem registrar automaticamente nada. O Modo Banca desencoraja textos de teste; para salvar, exige justificativa fundamentada, riscos descritos e reconhecimento das limitações.
- **Fechamento da história:** o botão final abre o relatório de uma decisão efetivamente registrada, com fallback para arquivo HTML caso pop-ups sejam bloqueados.
- **Projeção e legibilidade:** ajuste de tamanhos e densidade da etapa final, inclusive em telas de 1280×720, e opção de tela cheia.

## Evidências e limitações

Os indicadores de custo, atraso, SLA, conclusão, filas e estados continuam sendo fornecidos pelo **motor Python de eventos discretos**. A apresentação não os substitui por valores programados, histórias geradas ou previsões de agentes de IA.

Os custos e as economias resultam de um **cenário sintético** com hipóteses de capacidade. Habilitação individual de operadores, disponibilidade real de técnicos e peças, buffers, setup industrial, qualidade, retrabalho e dados reais de MTBF/MTTR não são integralmente comprovados pelo modelo.

A edição foi exercitada com Chrome/Chromium automatizado em Linux em **1280×720, 1366×768 e 1920×1080**; o Windows, o antivírus, o zoom do navegador e o projetor da banca exigem um ensaio no computador da equipe. Os módulos legados que dependem de Streamlit não foram homologados nesta revisão.

Mais detalhes em `docs/RELATORIO_MODO_BANCA_PREMIUM.md`, `docs/TESTES_APRESENTACAO_PREMIUM.md` e `docs/ROTEIRO_DEMONSTRACAO_PREMIUM.md`.
