# Anti-Murphy Factory Command — Sprint 5 / Integração de código

**Estado: candidata para compilação e teste visual. NÃO homologada no Windows.**

## O que este pacote realmente contém

- Base V30.2/Sprint 3, com motor Python instrumentado, Observer, exportador e contrato `ComparisonBundle 1.1.0` sem alteração de schema.
- Frontend Gemini Sprint 4 **corrigido** para os formatos do Pydantic real (estações, unidades, pedidos, seq e timestamps em `common_history`, `branch_A`, `branch_B`). A fixture reduzida enviada pelo Gemini foi substituída pelos **82 KB de JSON real** calculado pela V30.2.
- Replay determinístico TypeScript com mesmo estado verificado no Python em timestamps selecionados, incluindo 1,9 h.
- Canvas PixiJS React com máscara reutilizada e estrutura visual, controles play/pause/scrubber/slider e clique em máquina. Animações representam mudanças de estado e filas; **não representam transporte físico, pois o motor não simula transporte.**
- Painel de `branch_A.summary` e `branch_B.summary` com makespan, custo de simulação, SLA e indicador de viabilidade. O custo **não inclui implantação da manutenção expressa**.
- Ponte Python `st.components.v2.component(...)`, com seleção de máquina como trigger de volta ao Streamlit. **Não** usamos `st.components.v1.html` como canal bidirecional.
- Página `Factory Command` adicionada a `app.py` (aplicativo principal) e `app_nexus_v30.py` (interface NEXUS), podendo comparar demo de três postos ou gerar do workspace atual. Assinatura do modelo e do incidente invalida JSON antigo.

## Instalar e executar no Windows

Pré-requisitos: Python 3.12 x64 recomendado, Node.js LTS x64 + npm, conexão para instalação inicial; GPU/navegador com WebGL habilitado.

1. Extraia a pasta completa; mantenha `frontend/` e o restante no mesmo diretório.
2. Execute **`PREPARAR_FACTORY_COMMAND.bat`** com conexão à internet. Ele instala as dependências React/PixiJS no seu computador e cria `frontend/dist-component/factory_command.js` e `*.css`.
3. Execute **`EXECUTAR_ANTI_MURPHY.bat`** para instalar dependências Python da base e abrir a aplicação.
4. Na navegação selecione **Factory Command**. Comece com `Demonstração de três postos`.
5. Teste play, pausa, scrubber, divisão A/B, seleção da CNC e a diferença em 1,9 h de simulação.
6. Se desejar, escolha **Meu modelo atual** e clique **Calcular meus dois futuros**. O programa usa a configuração atual, com **uma ação hipotética de manutenção expressa**, não a melhor alternativa do otimizador.

### Executar frontend fora do Streamlit (para diagnosticar)

```bash
cd frontend
npm install
npm run dev
```

A versão Vite `dev` importa o arquivo real `src/data/simulation_snapshot.json`; a versão Streamlit v2 recebe `data.bundle` gerado pelo Python. **As duas devem produzir os mesmos estados**.

### Comandos de verificação

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q contract_tests tests/test_factory_command_trace.py tests/test_frontend_replay.py tests/test_workspace_bridge.py tests/test_timed_response.py tests/test_decision_priorities.py tests/test_v27.py tests/test_decision_store.py tests/test_model_optional_fields.py tests/test_v28_decision_and_ai.py tests/test_v291_regressions.py tests/test_atlas_agent.py
cd frontend
npm install
npm run typecheck
npm run build:component
```

**Importante:** o build `npm` e o teste visual dependem de um ambiente com rede e pacotes JS instalados. Este ambiente de desenvolvimento não conseguiu acessar registry.npmjs.org (`EAI_AGAIN`). O código React/JSX foi verificado quanto à sintaxe, mas **não** compilado completamente com as dependências nem inspecionado no navegador/Windows. Portanto não atestamos 60 FPS, ausência de vazamento de memória ou funcionamento visual de ponta a ponta.

## Resultados efetivamente verificados aqui

- 123 testes Python selecionados aprovados, incluindo regressões do motor e reconstrução entre Python e Node.
- `ReplayEngine.ts` + `simulation_contract.ts` compilados via TypeScript global `--strict` (sem dependências React).
- 8 fontes TS/TSX transpilaram sintaticamente, **não é o mesmo que typecheck completo**.
- `ComparisonBundle.model_validate_json` e `validate_reconstruction` aprovaram o JSON real.
- Cenário padrão do workspace (5 postos, 96 unidades) gerou dois futuros reais e validou os deltas. A proposta não calcula ações automaticamente, apenas a manutenção hipotética.

## Limitações importantes

- Skills individuais, setups dependentes da sequência e buffers finitos **ainda não são impostos pelo motor**; `feasible = unverified` é comunicado pela interface.
- `branch.summary.total_cost_cents` é custo simulado de operação e penalidade; **não é ganho líquido** após custo da manutenção.
- A visualização mostra conectividade lógica, sem tempo de transporte físico.
- O frontend do Gemini **não estava 100% compatível**; as divergências identificadas foram corrigidas em código aqui, mas a validação final depende de compilar e executar a interface.
- Sem métricas medidas de FPS; o próximo teste deve registrar hardware, navegador, tamanho de cenário, FPS mínimo/médio e uso de memória.
- O componente é executado localmente, sem conexão com ERP/MES, sensores ou chão de fábrica.

## Próximas tarefas, em ordem

1. Compilar no Windows e capturar eventuais erros TS de dependências e de runtime PixiJS; corrigir antes de afirmar integração pronta.
2. Verificar seleção, máscara do Split Wipe e barra temporal em todos os tempos, principalmente eventos simultâneos.
3. Incluir custos de reparo/implantação como variáveis explícitas antes de anunciar economia líquida.
4. Modelar operadores identificados e habilidades, transferências autorizadas, turnos e suas competências; definir restrições rígidas no motor e testes de cenários inviáveis.
5. Modelar capacidade física de buffers e bloqueio a montante sem deadlock, com testes de conservação de peças.
6. Modelar setup dependente da sequência e validar seu efeito sobre o custo e a conclusão da carteira.
7. Adaptar o Factory Command para mostrar alternativas vindas da otimização principal NEXUS, não apenas manutenção expressa fixa.
