# Revisão independente — AM05

Revisão somente leitura da produção. Base AM11 commit4cc48a4. Root implementa JS e backend agent implementa proveniência. Nenhuma correção de motor, fórmulas ou problemas foraAM05 sugerida.

## Contratos esperados

- Assinatura de configuração determinística, excluindo hora/runid acidental e parâmetros irrelevantes por ferramenta.
- Origem imutável: projetoID/nome à época, modo, entradas efetivas, sementes/constantes relevantes e instante do cálculo separados da identidade.
- Atualidade avaliada a cada render e exportação contra contexto do projeto atual E controles relevantes do mesmo modo.
- Resultado antigo deve permanecer acessível. Histórico em memória precisa explicar perda em reload/fechamento e qualquer limite; não apagar silenciosamente a25ªentrada.
- Resultado recebido após mudança da configuração, controle ou projeto não pode reaparecer como atual. Mudança de aba não pode colocar resultado de um modo no painel de outro.
- CSV, SVG e JSON devem transportar a mesma classificação. SVG precisa ter aviso visível, não só desc oculto.
- Cache MonteCarlo dashboard usa advanced:uncertainty (mesmo motor/entradas), com separação de origem e histórico de execução.
- Cache e respostas assíncronas dos dashboards e auditoria técnica devem verificar projeto, execução, seleção/contexto pertinente; apenas run_id é insuficiente em clone.

## Observações enviadas

1. openDashboards original valida somente run_id no retorno GET; troca para clone de mesmo run pode publicar snapshot de outro projeto. loadAudit já valida projeto/run/seleção no retorno, mas deve integrar mecanismo de atualidade/contexto sem misturar painelantigo.
2. renderAdvanced diagnostic original usa gargalo de st.data corrente com alertas/resultados antigos. Adicionar snapshot do gargalo no resultado e usar somente esse snapshot ao renderizar histórico.
3. analysis_contexts draft backend retorna dados de modelo repetidos12x em info. Sugerido expor assinaturas compactas, mantendo projeções completas apenas internas/testes.
4. Histórico temporário atual some em reload, não apenas fechamento do navegador; a limitação deve mencionar ambos.

## Revisão das dependências backend draft

Model stations/orders e station_order preservados. station_order importa por enumeração e escolhas aleatórias indexadas. Seeds fixas de stress/uncertainty/paired corretamente excluem seed global. duration exclui duration original e seleção; dispatch exclui regra global pois a varre; capacity/sensitivity/demand/opportunities excluem incidente. recovery dependeincidente+atrasoresposta, nãointervençãoselecionada. labgoal usa políticacompleta conservadora (até ordem deempates pode depender da classificação/sourceordem). Nomeprojeto não precisa invalidar configuração; snapshot do nomeorigem deve permanecerimutável.

Aguardando contrato JS definitivo para reproduções independentes.

## Revisão final da implementação e reproduções

Revisados analysis_state.js, integração em app.js, exportadores engineering_charts.js e backend analysis_provenance/service. A implementação usa assinatura específica, contextos compactos em info, snapshot completo de origem uma vez em cada resultado, classificação comum e histórico de página sem corte silencioso25. Nomeprojeto/rótulo à época são preservados; snapshot de gargalo no diagnóstico elimina mistura de métricas atuais com histórico.

Dashboards agora validam analysis_signature/projeto/seleção no retorno; auditoria inclui assinatura e valida origem no retorno; cache MonteCarlo compartilha família uncertainty e é apresentado como histórico/desatualizado quando o projeto/configuração diverge. Respostas atrasadas são armazenadas com ID de solicitação, sem vencer solicitação mais nova. Controles relevantes disparam atualização de validade sem cálculo novo. Abas retornam aos resultados anteriores; exportações CSV/JSON usam estado ao clicar, SVG tem estado e origem visíveis.

### Regressão de metadados CSV tratada

A inclusão de project_name na linha inicial cria superfície para nomes com ponto-e-vírgula virarem células adicionais. Sugeri manter a linha de metadados em UMA célulaCSV citada, com aspas escapadas e prefixo#. O responsável implementou. CR/LF dos campos de origem são neutralizados; entradasJSON preservam escaping. O backend já rejeita caracteres de controle em nomes pelaUI (constatado ao revisar base); a provaNode usa dados vindos de origem antiga/importada para testar defesa adicional, sem alegar exploração demonstrada pelaUI.

### Testes independentes

Novo arquivo `tests/test_am05_state_contract.py`: **10 aprovados**, sem alteração de produção por este revisor. Usa o módulo JS e exportador reais executados em Node, não uma cópia lógica.

Cobre: alteração/reversão de parâmetros; troca/retorno de projeto; contexto irrelevante preservando atualidade; origem imutável; conclusão de requisições fora de ordem; dados legados sem origem nunca atuais; separação de famílias; retenção31resultados; equivalência canônica de entradas; exportaçãoCSV com estadohistórico e nome malicioso contendo delimitadores, mantendo metadados em uma única célula e proteção de fórmula na linha de dados.

Comando: `PYTHONDONTWRITEBYTECODE=1 /workspace/work/audit/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_am05_state_contract.py`. Log externo: `/workspace/work/am05/review-state-tests.log`.

Sem novos bloqueadores confirmados na revisão final. Limites: não é prova universal de toda combinação de rede/navegador; testesHTTP/browser do agente principal complementam as verificaçõesunitárias. Histórico é memória desta página, perdido ao recarregar/fechar, explicitado naUI. Formulário principal de incidente e editor de modelo são rascunhos até calcular/salvar; contexto aplicado no backend define a configuração experimental vigente. Normalização do radar, estatísticas de inviáveis, busca de capacidade e demais achados não foram corrigidos nesta revisão.
