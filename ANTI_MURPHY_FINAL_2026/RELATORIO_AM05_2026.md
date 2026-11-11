# Anti-Murphy — conclusão da correção AM-05

Versão AM05-2026.1, aplicada sobre AM11-2026.1, commit-base4cc48a4f32045278b2fc520bfa8e022419f26cfc da branch recuperacao-anti-murphy. Nova branch correcao-am05-resultados. Escopo exclusivo: atualidade/origem/histórico de ensaios, ferramentas e painéis relacionados. Sem reescrita.

## Defeitos reproduzidos antes de modificar

Reprodução HTTP real da base AM11: Goal com meta0 retorna18alternativas; após mudarcontrole100 as18permanecem Atual e CSVatual. Sensibilidade CNC conserva resultado/JSONatual com seletorSOLDA. Duration vira Desatualizado após seleçãoirrelevante embora pontosiguais. Entrada Histórico exportaCSVatual. MonteCarlo do projeto principal sobrevive em projeto clonado sem classificação de histórico. Evidências before-browser.json/log e script de reprodução preservadas em docs/AM05/evidencias.

## Correção

`atelier.analysis_provenance` define dependências para12tipos. A assinatura determinística SHA256 reduzida24hex depende de schema, projetoID, tipo, dados/constantes pertinentes e entradas efetivas. Data/hora, nome de projeto, runID e metadados de apresentação não são identidade da configuração. Numericamente80 e80.0 são equivalentes. Ordem de postos é explícita porque enumeração e escolhas aleatórias podem depender dela. A assinatura identifica configuração; não autentica autoria nem é certificação industrial.

`Studio.info` publica apenas tokens compactos. Resultados conservam snapshot de dependências, entradas efetivas normalizadas, projetoID/nome à época, origem, execução e instante. Foram mantidos campos legados de proveniência para compatibilidade; eles não decidem mais a atualidade.

| Ferramenta | Dependências específicas além de modelo/pedidos/projeto |
|---|---|
| Laboratório duração | regra, semente, posto/início da falha; varre0/1/2/4/6/8/12h; ignora duração original, seleção e atraso |
| Laboratório despacho | semente/incidente; varreEDD/SPT/FIFO, ignora regra global escolhida |
| Laboratório robustez pareada | incidente, regra, ação temporal selecionada e investimento; sementes700–705 fixas |
| Laboratório Stress | regra;16réplicas, demanda0.9–1.2, ausências e durações2/4/8h; seed2026; ignora incidente selecionado |
| Laboratório capacidade | operação nominal/regra/semente, limites de busca e controles SLA/throughput; ignora incidente/seleção |
| Laboratório Goal | incidente/regra/semente, política e atraso que definem alternativas, meta específica do ensaio; ignora seleção examinada |
| Diagnóstico | nominal/incidente/regra/semente; gargalo exibido é o snapshot do resultado |
| Oportunidades | nominal/regra/semente e limite28candidatos |
| Sensibilidade | nominal/regra/semente, posto e recurso, incrementos0–3 |
| Limite de demanda | nominal/regra/semente, meta específica; faixa1–1.6 passo0.1 |
| MonteCarlo | incidente/regra e sementes2100–2111 fixas; ignora seleção e semente global substituída |
| Recuperação | incidente/regra/semente, atraso da resposta, limite8; ignora intervenção apenas examinada |

Modelo e pedidos incluem todos os seus campos; é uma projeção conservadora. Drafts ainda não salvos no editor ou não aplicados pelo formulário principal não substituem o estado calculado. Controles específicos de ensaio (SLA, throughput, posto, recurso) definem a consulta imediatamente, antes de uma nova execução.

## Interface e exportações

Um módulo comum `analysis_state.js` decide o estado a cada render/exportação:
- Atual: dependências e controles pertinentes correspondem e não há execução posterior do mesmo tipo.
- Desatualizado: dependências/projeto/controles diferem, inclusive troca para clone com números idênticos.
- Histórico: execução anterior do mesmo tipo que ainda corresponde à configuração atual.
- Origem não verificável: resultado antigo sem o novo contrato nunca é automaticamente rotulado Atual.

Histórico do Laboratório, ferramentas avançadas e MonteCarlo é mantido na memória da página, sem descarte automático após25resultados. A interface avisa explicitamente que recarregar/fechar perde esse histórico; exportar é necessário para guardar. Não foi criado armazenamento persistente novo nem apagados dados locais. Navegação entre ferramentas preserva resultados.

CSV, SVG e JSON usam a mesma classificação dinâmica. CSV inclui origem, assinatura, hora e controles, com metadados em uma única célula para preservar delimitadores/nomes sem criar fórmulas. A primeira linha é metadata; a tabela começa na segunda linha (`skiprows=1` se importar em pandas). Neutralização de fórmulas da tabela permanece. SVG possui aviso de estado e origem visível dentro da figura e proveniência completa em desc; JSON mantém snapshot imutável. A figura histórica não se identifica como resultado atual.

Respostas recebem sequência na solicitação, não na chegada. Uma resposta atrasada fica acessível no histórico com origem/estado corretos e não troca a ferramenta ativa nem toma foco de uma seleção histórica consciente. Dashboards e auditoria técnica verificam projeto, seleção e assinatura do contexto no cache/retorno. Dados de um projeto não são publicados como snapshot de outro.

Nenhum controle dispara nova simulação automaticamente. GET de painéis é leitura de resultados já calculados. Métodos de cálculo, sementes, custos, AM11, enumeração de alternativas e tratamento de inviáveis foram preservados.

## Validação final

- **402 testes aprovados, cinco falhas preexistentes, dez subtestes aprovados**. BaseAM11:352aprovados com as mesmas5falhas. **50testes novos aprovados**:40backend e10contratos JS/exportação.
- Três experimentos oficiais aprovados: nominal16,90h/SLA100%/R$8076,37; incidente24,58h/SLA40%/R$16216,67; manutenção21,58h/SLA100%/R$10313,00 de cenário. DecisãoR$12113,00/economiaR$4103,68. Sem alterações frenteAM11.
- Browser AM05 HTTP real:9grupos de verificações por resolução1280x720,1366x768,1920x1080. Sem errosJS capturados nem overflowhorizontal nos fluxos.
- Cobertura browser: meta0→100, parâmetros irrelevantes, sensibilidade posto/recurso, histórico entre abas, CSV/SVG/JSON, cloneMonteCarlo, respostas atrasadas após controles, ferramenta e projeto. Nenhum recálculo automático após mudanças isoladas.
- ModoBanca premium, registro/relatório e download alternativo: passou3resoluções, inclusive por HTTP real.
- Gráficos, legenda, ampliação, CSV e SVG: passou3resoluções.
- HTTP smoke:6rotas,12análises reais, modelo/seleção preservados.
- SintaxeJS validada; códigoPython executado pelos testes e analisado com gramáticaPython3.10. Quatro scripts antigos de browser que injetam conteúdo passaram a carregar o módulo novo antes da aplicação; suas asserções existentes não foram removidas.

As5falhas: test_operation_ui::test_evidence_exports_the_current_timed_experiment; dois testes test_restauracao_acesso; test_v31_editorial::test_only_one_root_launcher; test_v31_editorial::test_preview_has_no_external_script_dependency. Divergências históricas e artefato ausente já documentados. Suíte não é declarada100%verde.

AmbienteLinux/Python3.12/Chromium/Node24. Não houve homologação nativaWindows/bat/projetor, teste industrial calibrado nem auditoria de acessibilidade completa. Dados continuam sintéticos. A memória do histórico é limitada pelos recursos do navegador, sem retenção após recarregar. Arquivos exportados de versões anteriores não são reescritos.

## Arquivos de implementação

- atelier/analysis_provenance.py: projeções de dependências, normalização e assinaturas.
- atelier/service.py: proveniência, tokens por ferramenta e snapshots dos painéis.
- atelier/web/analysis_state.js: histórico, ordenação de solicitações e estado comum.
- atelier/web/app.js: controles, apresentação, histórico e proteção de respostas atrasadas.
- atelier/web/engineering_charts.js: metadados/status em CSV e SVG.
- atelier/web/index.html: carregamento do módulo comum.
- tests/test_am05_provenance.py e test_am05_state_contract.py; atelier/tests/browser_am05.py: testes novos.
- atelier/tests/browser_acabamento_final.py, browser_advanced_qa.py, browser_final_banca.py, browser_premium_banca.py: carga do novo módulo nos harnesses de injeção existentes.

## Preservação e reprodução

O pacote contém todos os353arquivos da baseAM11, mais as correções/documentos novos. Nenhum arquivo de simulation/, CSS, marca, inicializador ou workspace da base foi alterado. Os ZIPsAM11 e a branch de recuperação são mantidos. O patch usa hashes da base e escreve em pasta nova.

```text
python -m pytest tests contract_tests atelier/tests -q
python -m atelier.tests.validacao_experimentos_banca
python -m atelier.tests.browser_am05
python -m atelier.tests.browser_acabamento_final
python -m atelier.tests.browser_premium_banca
```

Os testes de navegador exigem Playwright/Chromium. Os scripts antigos podem gerar capturas/documentos; execute em cópia. A evidência de validação dos pacotes acompanha a entrega no GitHub.
