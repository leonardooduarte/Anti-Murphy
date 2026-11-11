# Anti-Murphy | Versão candidata à banca — 2026

Esta pasta contém a **edição completa Gráficos de Engenharia 2026** e um refinamento final para apresentação. O aplicativo é **local, sem conta, sem API de IA, sem npm e sem conexão com o MiroFish**. Esta é uma versão candidata, não software industrial homologado.

## Executar no Windows

1. Extraia **todo** o ZIP para uma pasta nova (não abra arquivos individualmente de dentro do ZIP).
2. Dê dois cliques em **`INICIAR_ANTI_MURPHY.bat`**; deixe a janela de terminal aberta enquanto usar o programa.
3. O programa deverá abrir no navegador. Se não abrir automaticamente, leia no terminal o endereço `http://127.0.0.1:<porta>/` e abra-o manualmente.
4. Na barra superior, escolha **Modo banca** para abrir uma demonstração em seis etapas: **Plano, Falha, Pedidos, Intervenção, Comparação e Evidências**.
5. Use os botões **Próxima etapa** e **Anterior**, ou as setas ← e → quando nenhum campo estiver em edição. **Esc** encerra o modo. A navegação normal continua disponível.
6. O **Modo banca** não altera o modelo ou os parâmetros; todos os indicadores são os resultados reais da simulação local do exemplo.

**Requisitos:** Python disponível no Windows. Se houver bloqueio do Windows Defender ou erro no inicializador, veja `LEIA_PRIMEIRO_BANCA.md` e `LEIA_ANTES_DE_EXECUTAR.md`. A execução no Windows do usuário não pôde ser validada neste ambiente Linux.

## Diferenciais de apresentação

- Fábrica 2.5D ampliada, legível no projetor, com alerta de **parada de máquina derivado dos eventos** e uma camada gráfica para a intervenção.
- Comparação A/B visualmente separada, com barra de referência de custos que inclui o investimento da resposta.
- Gráficos aprimorados nos seis Ensaios e seis tipos de Ferramentas, com tabelas de origem e exportação CSV/SVG.
- Painéis, auditoria, modelos, histórico e registro de decisões **preservados** na aplicação completa.

## Resultados reexecutados para o cenário sintético padrão

- Plano: 100% de pedidos no prazo, 16,90 h de makespan.
- Falha na CNC às 4 h por 8 h: 40% no prazo, 3 atrasados, custo de cenário R$ 16.216,67.
- Manutenção expressa: 100% no prazo, 21,58 h; custo de decisão (incluindo investimento) R$ 12.113,00; diferença estimada R$ 4.103,68 frente à falha sem resposta.

Esses resultados **não representam dados medidos em uma fábrica**. Eles dependem das premissas adotadas para recursos, tempos, custos e programação; não certificam viabilidade de manutenção real nem economias de caixa.

## Onde estão as evidências

- `docs/EXPERIMENTOS_VALIDACAO_ENGENHARIA.md` — três experimentos reproduzíveis.
- `docs/RESULTADOS_TRES_EXPERIMENTOS_BANCA.json` — resultados estruturados do motor.
- `docs/RELATORIO_FINAL_BANCA_2026.md` — implementação e resultado da auditoria.
- `docs/ARQUITETURA_ATUAL_E_LIMITACOES.md` — fluxos e limitações.
- `docs/TESTES_DA_VERSAO_CANDIDATA.md` — testes, restrições e pontos não verificados.
- `docs/PITCH_5_MIN_E_SABATINA.md` — roteiro de demonstração e questões técnicas.
- `docs/capturas_banca_final/` — capturas reais de navegador.
- `docs/PROXIMAS_MELHORIAS.md` — backlog pós-banca.

## Escopo preservado

A pasta `FERRAMENTAS_HISTORICAS` foi mantida. Os módulos de versões antigas ATLAS/NEXUS **não estão todos unificados** ao frontend atual; seu funcionamento depende do ambiente Streamlit/legado, não validado nesta rodada. O inicializador principal `INICIAR_ANTI_MURPHY.bat` e os arquivos originais do motor de simulação permanecem sem alteração.

**Sugestão:** faça a última verificação no próprio PC da apresentação e, se possível, no projetor: iniciar, ativar modo banca, mostrar a falha, comparar A/B, abrir os gráficos, registrar a justificativa, gerar o relatório e encerrar/reabrir o programa.


Nota AM-11: diferença econômica calculada com valores não arredondados; o resultado final é arredondado para apresentação. A diferença de R$ 0,01 frente à edição AM-06 é esperada.
