# Relatório de implementação e validação — Estúdio Industrial

## Escopo

O objetivo desta entrega é melhorar o uso real do Anti-Murphy sem substituir
simulação, relatórios, projetos, dashboards ou análises antigas por um protótipo.

### Implementado e exercitado no navegador

| Frente | Implementação | Evidência |
|---|---|---|
| Identidade e cores | Design CSS unificado para o Workbench | `atelier/web/studio_final.css` |
| Fábrica | Bases industriais, máquinas maiores e estados claros | `atelier/web/app.js` / capturas |
| Animações | Movimento do equipamento condicionado aos estados DES e ao Play/Pause | CSS + classe dinâmica do posto |
| Jornada de investigação | Faixa do incidente, saltos para o mapa/pedidos, seleção automática de instante comparável | `renderIncidentWorkflow`, `informativeComparisonTime` |
| Editor de operações | Roteiro por etapas com escolha de posto, tempo e ordenação | `openRouteEditor` e modal `#route-dialog` |
| Análise de pedidos | Operação selecionável, espera registrada e salto para o replay | `renderStationInspector` |
| Painéis | Alternativas não dominadas dentro do conjunto simulado; legenda de limitações | `dashTradeoffPlot` |
| Murphy contextual | Atalho da inspeção do posto para análise local em Decisões | `data-inspect-murphy` |

A animação não implica transporte real entre postos: o motor não fornece tempos de transporte.
Os horários e indicadores provêm dos eventos e cálculos do motor de simulação.

## Validação de código

- **192 testes aprovados**, 10 subtestes aprovados; 4 testes legados foram
  propositalmente desmarcados porque verificam arquivos, rotas e nomes da V31
  incompatíveis com a arquitetura principal adotada anteriormente.
- Três módulos legados não puderam sequer ser coletados porque dependem de
  Streamlit, ausente neste ambiente.
- Teste isolado adicional com `Studio.set_model`: a alteração real de um
  roteiro gerou novo experimento e persistiu após reabrir o projeto.
- **Navegação e interações no Chromium**: 1280×720, 1366×768 e 1920×1080,
  sem erros JavaScript nos fluxos testados; 12 capturas foram produzidas.
- O navegador de testes não pôde navegar diretamente para endereços locais
  por política do ambiente. A interface foi testada em documento autocontido,
  alimentada por JSON **calculado pelo `Studio` real**. A API HTTP local foi
  verificada separadamente com resposta HTTP 200.
- O motor e os arquivos do serviço e servidor foram comparados byte a byte
  com o ZIP de referência: permanecem idênticos.

## Funcionalidades preservadas

Editor do modelo, simulação e replay, comparação A/B, projetos, experimentos,
laboratório, dashboards de Operação/Desempenho/Cenários/Otimização/Robustez,
Murphy local, relatórios e registros, tutoriais, marca animada e ferramentas
históricas ainda não migradas. Nenhuma delas foi removida desta distribuição.

## Pendências antes da entrega acadêmica

- Validar o inicializador e a abertura automática do navegador no Windows.
- Executar a navegação completa em uma instalação do Windows com projeto salvo.
- Migrar integralmente as telas históricas War Room, Executive Room e Portfolio,
  que permanecem no ambiente separado.
- Aplicar restrições industriais profundas (habilitações individuais,
  buffers finitos e setups dependentes da sequência), com testes do motor.
- Avaliar custo de intervenções e disponibilidade de recursos com premissas reais.
- Realizar teste com outra pessoa, verificando se ela consegue abrir um projeto,
  simular, comparar, explicar o resultado e registrar uma decisão.
- As representações são SVG 2.5D ilustrativas, não um gêmeo digital conectado a sensores.

## Arquivos alterados nesta edição

- `atelier/web/index.html`
- `atelier/web/app.js`
- `atelier/web/studio_final.css` (novo)
- `atelier/tests/test_release_studio.py` (novo)
- `LEIA_PRIMEIRO.md`, `README.md` e esta documentação

**Não declarar homologação industrial ou 60 FPS a partir destes testes.**
