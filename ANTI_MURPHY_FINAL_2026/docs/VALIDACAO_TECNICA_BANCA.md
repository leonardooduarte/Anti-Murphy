# Validação da edição para banca — 05/11/2026

## Escopo entregue

A edição foi derivada da **Anti-Murphy Pré-Final Validada 2026**, sem reescrever a fila de eventos `heapq` nem substituir o motor. A marca e a animação de abertura foram preservadas. A interface principal continua offline-first, servida por Python local, sem npm.

**Correções de alto impacto:**

1. Escala realista de replay: 1× = 10 min simulados por segundo real, ajustável a 0,5×, 2×, 4× e 8×; não depende do horizonte total.
2. A reprodução começa pausada; opção de pausa automática ao início da falha e no instante de intervenção efetiva.
3. Correção de atualização do relógio no próprio quadro em que a pausa automática é aplicada. Era possível o relógio ficar um quadro atrasado após a pausa.
4. Horizonte da reprodução ajustado à cena; a comparação A/B utiliza o máximo dos dois horizontes. Os KPIs do comparador mostram A e B separadamente, incluindo **custo da decisão com investimento**.
5. Nova API `GET /api/technical-audit`, derivada do experimento ativo. Exibe folga, gargalo pontuado, maior espera, maior fila, custo reconciliado, premissas de manutenção, ausência de indicadores de qualidade e restrições pendentes.
6. Painel **Painéis → Auditoria técnica**, limiar configurável para alerta de pouca folga (15, 30, 60 ou 120 minutos).
7. Registros estruturados com responsável opcional, riscos, hash do modelo, reconhecimento explícito das limitações e indicação de que a viabilidade física **não foi homologada**.
8. Histórico em formato legível e dados técnicos recolhidos; timestamps legíveis no horário de Brasília.
9. Relatório técnico imprimível com folga por pedido, reconciliação de custos, metodologia e limitações.
10. Testes automatizados de consistência do modelo e da interface, além de rotas HTTP locais verificadas.

## Fontes dos indicadores

- `simulation/engine.py`: operações, filas, custos, datas e indicadores do DES (permaneceu inalterado).
- `simulation/nexus.py`: operação nominal, incidente e respostas enumeradas (permaneceu inalterado).
- `atelier/technical_audit.py`: somente **auditoria de consistência e cálculo aritmético de folga**. Não executa intervenções nem altera o modelo.
- `atelier/decision_explainer.py`: Murphy local determinístico (preservado).

## Testes executados nesta sessão

- `pytest` sobre motor, contratos, serviços e regressões compatíveis: **206 testes aprovados e 10 subtestes**, com quatro testes legados desmarcados por refletirem nomes/estrutura de versões anteriores.
- Suítes dependentes de Streamlit não coletadas devido à dependência opcional não instalada no ambiente de avaliação.
- `browser_banca_gate.py`: Chromium em **1280×720, 1366×768 e 1920×1080**; abertura pausada; 8× e pausa na falha às 04:00; comparação A/B; auditoria e custos; dashboards anteriores; Murphy local; validação do registro e leitura do histórico; relatório técnico imprimível. **Sem erros JavaScript nos fluxos exercitados.**
- `browser_prefinal_gate.py`: regressão do fluxo anterior com checklist de limites, também nas três resoluções. **Sem erros JavaScript.**
- `http_banca_smoke.py`: servidor Python verdadeiro em localhost com respostas HTTP 200 em `/`, `/app.js`, `/banca.css`, `/dashboards.css`, `/api/dashboards` e `/api/technical-audit`; troca de alternativa refletida na auditoria posterior.
- Integridade do ZIP verificada durante empacotamento.

### Limites de validação

1. A navegação Chromium → `127.0.0.1` do servidor foi bloqueada pela política do ambiente; a interface foi testada em documento HTML autocontido que chama o **Studio Python real** por uma ponte. As rotas HTTP foram testadas separadamente. Não alegar homologação gráfica ponta a ponta da instalação Windows a partir destes testes.
2. **Não foi medido FPS no hardware do usuário**. Não há alegação de 60 FPS.
3. Não foram executadas nem migradas integralmente todas as telas históricas ATLAS/NEXUS em Streamlit.
4. Não há dados de produção reais para calibrar MTBF/MTTR, refugo, setups complexos, skills individuais ou buffers finitos. Esses recursos foram **marcados como pendentes**, não fingidos como concluídos.
5. O motor cobra custo de **capacidade contratada pelo horizonte do plano**, e não exclusivamente custo variável das horas efetivamente processadas.

A versão é candidata à **demonstração acadêmica**, não a um sistema industrial homologado. Antes da apresentação real, efetuar ensaio no computador Windows e conferir os resultados que serão exibidos.
