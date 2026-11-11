# Revisão técnica do Anti-Murphy — 09/11/2026

## Base e escopo

**Origem:** versão candidata à banca, examinada na gravação de 5m03s (`09_11.mp4`). A revisão é concentrada em um conjunto delimitado de melhorias técnicas e de UX; não representa homologação industrial, calibração de tempos ou revisão de todos os módulos legados Streamlit.

**Problema mais relevante da gravação:** em uma configuração de intervenção, a resposta examinada poderia ser dominada por outra alternativa, sem que a interface destacasse esse fato. O vídeo também terminava com uma justificativa incompleta, sem o registro concluído. Em telas de 720p, o formulário de conclusão ficava abaixo da área imediatamente visível.

## Mudanças implementadas

### 1. Parecer multicritério rastreável (Python)

Novo módulo `atelier/decision_quality.py`, utilizado por `atelier/service.py` nos retornos de `/api/state` e `/api/dashboards` e arquivado nos registros de decisão. O diagnóstico **não altera a alternativa escolhida**, não recalcula a simulação e não fornece ranking global.

Uma alternativa **B domina A** quando, no conjunto de respostas enumeradas e elegíveis do experimento atual, satisfaz simultaneamente:

- `custo_B ≤ custo_A`, admitindo tolerância de R$ 0,01;
- `makespan_B ≤ makespan_A`, admitindo tolerância de 0,005 h;
- `SLA_B ≥ SLA_A`, admitindo tolerância de 0,005 ponto percentual;
- apresenta melhoria estrita em ao menos um desses indicadores, além da tolerância.

Uma alternativa só participa do conjunto concorrente quando `feasible`, `within_budget` e `meets_sla` forem verdadeiros no **modelo** e os números forem finitos. Esses critérios **não garantem viabilidade física**: habilitações individuais, técnicos, componentes, buffers, custos evitáveis e outras restrições não são validados por essa regra.

Status possíveis: `dominated`, `non_dominated`, `outside_criteria` e `unknown`. A tela explicita qual alternativa foi comparada, com custo, conclusão e SLA. O usuário pode examinar a concorrente, mas não ocorre uma troca automática. Se houver apenas um cenário elegível, o texto registra essa condição sem alegação de ótimo.

### 2. Fechamento real do fluxo decisório

A etapa 6 do **Modo banca** agora abre **Decisões**, mantendo visíveis o parecer multicritério e os indicadores principais enquanto o usuário registra responsável, justificativa, riscos e reconhecimento das limitações. Em telas largas os componentes são dispostos lado a lado; o modo convencional conserva todos os detalhes.

O botão **Registrar decisão** envia dados ao serviço Python. A confirmação visual depende da resposta do backend, e os registros são guardados localmente. Após a gravação, são exibidos **Gerar relatório** e **Abrir registro**. O relatório diferencia prévia de decisão arquivada e inclui a justificativa e o parecer vigente, com valores monetários em centavos.

### 3. Visualização e interpretação

O painel de Robustez informa explicitamente quando todas as execuções têm o mesmo SLA e ressalva que isso não evidencia confiabilidade industrial. O assistente local recebe uma orientação inicial baseada na contagem real de pedidos atrasados do experimento.

A identidade `#1D292D`, `#FF681B`, `#F7F7F3`, logo animada e mapa 2.5D foram preservados. A camada CSS `polimento_09_11.css` aprimora o fechamento, a leitura e o posicionamento em projetor, sem substituir controles nem algoritmos.

## Evidências e testes

- **Python:** 211 testes aprovados, 10 subtestes aprovados, 4 testes legados incompatíveis com a inicialização atual explicitamente excluídos. Três módulos de testes Streamlit não foram coletados pela ausência de Streamlit nesta estação de validação.
- **Navegador Chromium:** Modo banca, seis etapas, alerta multicritério, seleção explícita, registro persistido, abertura de relatório e histórico, em **1280×720, 1366×768 e 1920×1080**, sem exceções de JS nas operações exercitadas.
- **HTTP local real:** página, JavaScript, CSS novo, resposta `/api/state`, dashboards, cálculo, seleção e persistência em `/api/record` e `/api/history` verificados.
- **Três experimentos de engenharia:** scripts reproduzíveis de parada, sensibilidade de capacidade e comparação de critérios. Dados e verificações: `docs/EXPERIMENTOS_VALIDACAO_ENGENHARIA.md` e `docs/RESULTADOS_TRES_EXPERIMENTOS_BANCA.json`.
- **Preservação:** arquivos sensíveis da simulação, identidade visual, inicializador e scripts de gráficos comparados por SHA-256 com o ZIP de entrada.

## Limitações abertas

1. **Calibração ausente:** tempos de processo, demanda, custo e paradas são sintéticos; os resultados não representam uma medição fabril.
2. **Viabilidade industrial parcial:** habilitações individuais, disponibilidade de manutenção, materiais, buffers, setup dependente da sequência, inspeção/refugo/retrabalho não estão integralmente modelados.
3. **Sem ótimo global:** a comparação de Pareto cobre só as respostas enumeradas sob as premissas ativas.
4. **Custo econômico aproximado:** custo de capacidade ao longo do horizonte pode não ser caixa evitável; economia é diferença do modelo, não valor financeiro comprovado.
5. **Amostra Monte Carlo exploratória:** 12 execuções sintéticas não sustentam probabilidade empírica de atraso nem intervalo de confiança industrial.
6. **Ambiente Windows a confirmar:** a versão foi exercitada no Python HTTP e Chromium neste ambiente. A abertura via `.bat`, antivírus, permissões de disco, pop-ups e projetor dependem de verificação no computador da apresentação.
7. **Legados não homologados nesta revisão:** os módulos antigos que dependem de Streamlit não foram testados em execução completa.

## Arquivos mais importantes

- `atelier/decision_quality.py` — função de análise multicritério.
- `atelier/service.py` — exposição do parecer e arquivo do snapshot na decisão.
- `atelier/web/app.js` — visualização, conclusão do Modo banca, relatório e histórico.
- `atelier/web/polimento_09_11.css` — acabamento específico da edição.
- `atelier/tests/test_decision_quality.py` — testes unitários de dominância e registro.
- `atelier/tests/browser_final_banca.py` — teste E2E de navegador e capturas.
- `atelier/tests/http_refino_09_11.py` — smoke do HTTP local.

**Status sugerido:** candidata refinada à apresentação, ainda sujeita ao teste final no Windows/projetor. Evitar novos módulos ou alterações estruturais antes desse teste.
