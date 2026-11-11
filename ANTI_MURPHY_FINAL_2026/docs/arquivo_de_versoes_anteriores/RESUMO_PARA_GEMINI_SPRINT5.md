# Revisão cruzada para o Gemini — Sprint 5

O ZIP original do Sprint 4 continha `definition.stations` como lista, keyframes com somente `{time_us,state}`, deltas incompletos, `metadata` não pertencente ao contrato e sem `experiment_id`, `incident`, `fork`, `orders`, `units` ou `branch.summary`. O replay usava somente horários, ignorando `seq` ao buscar eventos dentro do keyframe. A máscara era alocada por `new PIXI.Graphics()` durante o render.

Essas incompatibilidades foram corrigidas neste pacote candidato Sprint 5:
- `src/types/simulation_contract.ts`: contrato ComparisonBundle v1.1.0 oficial (sem `any`).
- `src/engine/ReplayEngine.ts`: busca determinística por `time_us, seq`, keyframes completos, eventos com upserts absolutos, resumo por ramo.
- `src/App.tsx`, `MachineNode.tsx`, `ControlsOverlay.tsx`, `useSimulationStore.ts`: ids/topologia do modelo, máquina, seleção, filas, A/B com máscara reutilizada, linha do tempo, resumo econômico.
- `src/streamlit_entry.tsx` + `vite.component.config.ts`: ponto de entrada ES para Streamlit Custom Component v2.
- `bridge/factory_command_component.py`: valida JSON com Pydantic antes de enviar a `data.bundle`; `setTriggerValue('selected_station', id)` no frontend, sem enviar frames por WebSocket.
- `app.py` / `app_nexus_v30.py`: nova página, opção demo ou simulação de workspace atual.

**Evidência:** 123 testes Python passam; TS core compilou; Node conferiu estados de A/B contra Python. Não conseguimos `npm install` neste container, devido à falha de DNS EAI_AGAIN, então integração React/PixiJS **não foi compilada nem testada no navegador**. Não afirmar performance, mask correctness ou homologação até o teste no Windows.

**Pedido de revisão ao Gemini:** compilar `npm run typecheck && npm run build:component`, testar streamlit v2 em navegador no Windows, corrigir eventuais erros do PixiJS v7, avaliar a máscara e fluxo do slider, verificar que a seleção de posto não zera o replay após callback, testar FPS e memória; devolver patch, capturas e relatório com evidências. Respeitar esquema v1.1.0 intacto.

**Hard constraints pendentes:** skills individuais, buffers finitos e setups por sequência, todos com `unverified` no pacote. Uma recomendação operacional só deverá receber status `feasible` após cálculo válido e evidência de todas as restrições aplicáveis.
