# AM19 — contratos de testes e artefatos distribuídos

## Base, escopo e recuperação

Base obrigatória: `ANTI_MURPHY_EVOLUCAO_VISUAL_02_COMPLETO.zip`, SHA-256
`4908c612fd98c2b8a8bc4e3e102089ee985e7f97b22ed675cbc4489fe0954bec`.
Os 576 arquivos foram extraídos e preservados em uma base limpa.

O pacote contém AM15-2026.1 e alterações visuais posteriores sem um manifesto
próprio de release: comparado à branch `correcao-am15-legibilidade`, commit
`c7e132da54a4f398df13fcdbac6152f41971f922`, muda `atelier/web/app.js`,
`index.html` e `acabamento_banca_final.css`, e acrescenta `experience_v01.css`.
Não muda Python, testes, dados ou relatórios daquela base. Não é uma versão
reconstruída do zero nem o ZIP original antigo.

Branch AM19: `correcao-am19-contratos`. O checkpoint
`8000e8d33470a6167a6e2c669f80f1d4df0b9de5` registra o conteúdo visual recebido
antes das correções. Checkpoints seguintes preservam as mudanças e o pacote
final. A AM15 e as branches anteriores permanecem sem alteração. Trabalho
executado sem agentes paralelos.

## Reprodução e classificação de cada falha

As cinco falhas foram executadas juntas antes de modificar os testes ou gerar
artefatos: **5 falhas**, registradas em `before.log`.

| Teste | Contrato protegido e causa confirmada | Classificação e solução |
| --- | --- | --- |
| `test_operation_ui::test_evidence_exports_the_current_timed_experiment` | Exportar o experimento temporal corrente. O teste escrevia `op_page=Registros`, mas o shell atual controla esse campo por `am_area` e o restaurava para Operação. Não eram exibidos os três downloads. | Contrato de navegação obsoleto. O teste agora clica no botão público Registros, captura os argumentos reais dos downloads e confere run_id, assinatura e instante solicitado no JSON, além da alternativa no HTML e CSV. Mantém a exigência dos três downloads. Nenhum código de exportação foi alterado. |
| `test_restauracao_acesso::test_inicio_prioriza_o_workspace_original_e_nao_o_mapa` | Abrir a operação e manter navegação acessível. Procurava constantes e fragmentos da estrutura anterior (`CORE`, `SECTIONS`) ausentes no shell atual. | Contrato textual obsoleto. AppTest verifica abertura em Operação, navegação pelos botões públicos para Modelo, Registros e Mapa comparativo, retorno à Operação e botão Início, sem exceções. |
| `test_restauracao_acesso::test_modulos_importantes_tem_atendimento_direto` | Manter as dez ferramentas históricas acessíveis. A busca literal com aspas duplas não reconhecia os nomes existentes no dicionário `TOOLS`, escrito com aspas simples. | Contrato textual frágil. Cada ferramenta é aberta diretamente pelo seu botão público a partir de uma sessão inicial, verificando área, ferramenta ativa e ausência de exceções. Não se alterou o roteador para satisfazer um texto antigo. |
| `test_v31_editorial::test_only_one_root_launcher` | Distribuir um único BAT e abrir o programa correto. Exigia `tools/start_nexus.py`, mas o BAT já usa `start.py` para o Studio local. | Alvo de teste obsoleto. Preserva a exigência de BAT único, confere as alternativas `py -3` e `python`, executa `start.py` com a chamada do servidor interceptada e acrescenta teste de partida real em processo isolado. |
| `test_v31_editorial::test_preview_has_no_external_script_dependency` | Disponibilizar uma prévia offline autocontida com o contrato de replay. `PREVIEW_OPERACAO.html` não existia no ZIP. A prévia companheira exigida por `tools/test_studio_replay.py` também estava ausente. | Defeito real de distribuição. Restaura ambas com geração reproduzível a partir de `ui/factory_studio.html`, `factory_command_demo.json` e marca já distribuídos. Verifica equivalência integral do contrato tipado, ausência de placeholders/dependência externa de script e igualdade com a geração atual. |

Nenhum teste foi apagado, marcado como skip/xfail ou removido da regressão.
As expectativas funcionais foram ampliadas; não foram ajustados números para
forçar aprovação. O assert de uma legenda fixa `6,00 h` foi substituído pela
conferência do instante realmente solicitado no experimento exportado.

## Correções e verificações associadas

`tools/build_previews.py` é um gerador de desenvolvimento em biblioteca padrão:
não executa simulação, não acessa rede nem escreve no workspace. Produz
`PREVIEW_OPERACAO.html` e `PREVIEW_FACTORY_COMMAND.html` com dados fixos da
fixture e marca em data URI. O JSON é escapado para inserção segura no script
de dados. As prévias são exemplos estáticos históricos, não o projeto ativo.

`tools/qa_editorial_browser.py` deixou de depender de
`/mnt/data/ANTI_MURPHY_V31_OPERACAO`, passando a localizar a prévia no pacote.
Sua matriz inclui 1280×720, 1366×768 e 1920×1080. O teste de replay existente
voltou a executar sem modificação de suas asserções: 16 comparações A/B entre
JavaScript e contrato Python, mais cinco fluxos interativos aprovados.

O teste anterior de preservação do motor apenas comparava hashes se uma
pasta externa existisse; neste ambiente não fazia verificação alguma. Agora
usa a referência versionada `docs/AM19/base-reference.json`, obtida do ZIP
recebido, e sempre confere o motor. Um teste adicional confere os quatro
arquivos visuais recebidos. Isso protege o escopo AM19 sem congelar o projeto:
uma mudança futura legítima deve atualizar a referência e explicar sua base.

O README passou a distinguir a entrada principal das históricas; todo o texto
anterior foi preservado abaixo do cabeçalho atual. `ENTRADAS_AM19_2026.md`
registra launcher, dependências e artefatos, incluindo limites dos runners
opcionais antigos. Nenhum BAT, roteador, motor ou componente visual foi alterado.

## Resultados finais

- **556 testes aprovados, zero falhas e dez subtestes aprovados** na regressão
  completa `tests contract_tests atelier/tests`. A base tinha 548 aprovados e
  cinco falhas; os cinco casos passam e foram acrescentados três testes de
  distribuição. O único aviso remanescente é de depreciação do plugin anyio
  usando a API CallSpec2 do pytest; não é falha do projeto.
- Os 16 testes direcionados dos três módulos originais passaram, além dos
  testes novos de distribuição. O log `focused.log` foi obtido antes do
  fortalecimento adicional do hash do motor; a regressão final inclui esse
  fortalecimento e o terceiro teste novo.
- Partida real com `python -S start.py --no-browser --port 0` em cópia isolada:
  servidor local ativo, HTML e recursos do pacote visual entregues por HTTP,
  estado com execução calculada e dashboards disponíveis. `-S` desativa pacotes
  de site, confirmando a ausência de dependências de terceiros nesse caminho.
- Três experimentos oficiais aprovados, sem diferença: SLA nominal/incidente/
  resposta 100/40/100%; custo do incidente R$16.216,67; investimento expresso
  R$1.800,00; custo da decisão R$12.113,00; economia líquida R$4.103,68.
- Browser HTTP real: Modo Banca, comparação, justificativa, registro e relatório
  passaram nas três resoluções. Gráficos, legendas de 12 alternativas, ampliação
  e exportações CSV/SVG passaram nas três resoluções. Prévias históricas passaram
  nas três resoluções; a comparação de contrato A/B usou sua resolução original
  1440×990. Logs e capturas acompanham o pacote.
- Testes direcionados são executados novamente no ZIP extraído. A verificação
  final, incluindo a partida real, fica em `zip-tests.log` ao lado do download.

Ambiente: Linux, Python 3.12.14, pytest 9.2.0, Streamlit 1.67.0, pandas 2.2.3,
Pydantic 2.13.4 e Playwright 1.62.0 com Chromium. Versões completas em
`environment.json`. Não houve homologação nativa do BAT, Windows ou projetor.

## Preservação e limites da conclusão

O patch parte dos hashes dos 576 arquivos do ZIP visual, não de uma extração
somente da AM15. Todos os arquivos da base permanecem presentes. As únicas
alterações em arquivos existentes são README, três módulos de teste e o runner
editorial portátil. As duas prévias, o gerador, os três testes adicionais
(em um módulo), as referências e os documentos são acréscimos.

Motor, cálculos, seeds, fórmulas econômicas, recursos visuais recebidos, abertura,
Modo Banca, gráficos, projetos e registros da base são preservados byte a byte.
As mudanças AM01–AM17 presentes na base não foram reimplementadas. Não foram
corrigidos investimento ausente na nova apresentação, prioridade opcional do
editor, recuperação de arquivos inválidos ou Host/Origin: são outros achados.

Limitação do harness: uma tentativa de passar por várias ferramentas legadas
na mesma sessão AppTest encontrou uma falha do serializador de selectbox
formatada após `runpy` (valor `CORTE` versus rótulo formatado). O teste de acesso
direto usa uma sessão inicial por ferramenta, correspondente ao contrato que
protege. Não se afirma homologação de toda sequência possível entre ferramentas
históricas. A navegação entre áreas e retorno ao início é exercitada em sessão
contínua; os fluxos do aplicativo principal são exercitados em Chromium real.

Outro limite identificado: `tools/browser_offline.js` ainda se refere ao
artefato histórico `DEMO_NEXUS_V30.html`, ausente do ZIP recebido. Esse runner
Node não foi homologado, nem substituído por outra tela para fazê-lo passar.
Ele não integra a regressão pytest nem o launcher principal. A etapa resolve
as cinco falhas reproduzidas e as prévias associadas, sem alegar que todo runner
antigo foi atualizado. Scripts adicionais preservados podem exigir dependências
de desenvolvimento e dados históricos externos, como documentado no mapa de
entradas. Essa limitação não impede recuperar ou executar o aplicativo atual.

## Reprodução e entrega

```sh
python -m pytest tests contract_tests atelier/tests -q
python -m pytest tests/test_operation_ui.py tests/test_restauracao_acesso.py tests/test_v31_editorial.py tests/test_am19_distribution.py -q
python -m tools.build_previews
python tools/test_studio_replay.py
python tools/qa_editorial_browser.py
python -m atelier.tests.validacao_experimentos_banca
python -m atelier.tests.browser_acabamento_final
```

O script adicional de aceitação HTTP e os logs estão em `docs/AM19/evidencias`.
Execute testes em cópia. Streamlit/pytest/Node/Playwright são requisitos de
desenvolvimento ou de caminhos adicionais, não do launcher principal. O BAT é
inspecionado e seu alvo Python é testado; isso não equivale a executá-lo no Windows.

O ZIP completo é extraído e conferido. O aplicador do patch verifica a base
visual exata e cria uma pasta nova. Os arquivos resultantes são comparados por
SHA-256 aos do ZIP completo. Os arquivos publicados são recuperados do GitHub
e comparados aos locais. SHA256SUMS, logs, relatório e continuidade acompanham
a entrega; uma cópia do ZIP-base recebido também é preservada na pasta AM19.
Nenhuma branch anterior foi sobrescrita e nenhum registro histórico foi regravado.
