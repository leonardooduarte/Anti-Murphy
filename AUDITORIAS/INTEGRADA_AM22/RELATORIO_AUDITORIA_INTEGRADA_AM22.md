# Auditoria integrada — Anti-Murphy AM22

## Parecer

A base atual passou na regressão disponível e nos fluxos de aceitação executados. A auditoria adicional confirmou quatro pendências: importação que não restaura a regra de despacho exportada; precisão da folga na auditoria por pedido; leitura da biblioteca diante de documento inválido; contraste de rótulos. Não foi demonstrado bloqueador P0 ou erro do núcleo DES nos casos independentes executados. Isso não certifica ausência de outros defeitos nem homologação industrial.

Recomendo quatro correções pequenas e separadas antes de ampliar funcionalidades ou redesenhar telas. A validação no Windows e no projetor continua necessária antes de declarar a versão pronta para banca. Não atribuo percentual de conclusão.

## Base, integridade e limites

AM22-2026.1, commit **8599a5c6f8ce361e5804f4403a8770939546df79**, branch de origem correcao-am22-host-origin. Aplicativo examinado por extração do ZIP efetivamente entregue, SHA-256 **a6f706acdf78a0184691fa1338d3d99803f3628d3242caa3887bce97da7bc13e**. O manifesto contém os 650 arquivos. Ao final, todos conservaram seus hashes. Nenhum código, teste existente, fórmula, recurso visual ou dado-base foi modificado. Os ensaios utilizaram diretórios temporários; capturas e relatórios ficam fora da distribuição. Não houve agentes paralelos.

Nova branch de documentação: auditoria-integrada-am22. O checkpoint 2d3dccd registra escopo/base. Esta entrega é uma auditoria, não uma versão corrigida nova; o aplicativo para uso continua sendo o ZIP AM22. Não há patch de código nesta etapa.

O ambiente foi Linux, Python 3.12 e Chromium com Playwright. Não houve execução nativa do BAT no Windows nem teste em projetor. Os caminhos Streamlit e runners históricos adicionais não receberam homologação visual integral nesta etapa. Documentos antigos de status são referências históricas; seus números de testes e próximos passos não descrevem necessariamente o commit atual.

## Validação executada

- Regressão no ZIP extraído: **664 testes aprovados, zero falhas, dez subtestes**. Warning de depreciação do plugin AnyIO, sem falha funcional. Nenhum teste foi removido, desativado ou alterado.
- Três experimentos oficiais aprovados. A: SLA nominal/incidente/resposta 100/40/100%, custo total da decisão R$12.113,00 e economia líquida R$4.103,68. B/C conservaram os resultados registrados em banca.log.
- AM05 no navegador: estados atual/desatualizado/histórico, metas, posto/recurso, seleção, origem de projeto, CSV/SVG e respostas retardadas, nas três resoluções.
- Treze módulos adicionais de navegador aprovados: AM07, AM08, AM09, AM10, AM12, AM13, AM14, AM15, AM16, AM17, AM22, recuperação e prioridade opcional. AM12 usa 1366×768; os demais percorrem as três resoluções. AM15 também testa 1/5/9/16/50 postos; AM22 usa 127.0.0.1 e localhost. Resultados/tempos estão em browser-results.json.
- Modo Banca HTTP real com seis etapas, justificativa, registro e relatório; gráficos/ampliação/exportações nas três resoluções. As resoluções foram 1280×720, 1366×768 e 1920×1080.
- Novo roteiro integrado: oito áreas em cada resolução, sem overflow horizontal do documento e sem exceções JavaScript não tratadas; abertura normal com saída da introdução; exportação/importação real por arquivo; arquivo inválido na biblioteca. Os dois defeitos são resultados esperados da investigação, não aprovações do comportamento incorreto.
- Nova revisão dos componentes visuais: abrir narrativa pelo teclado, ativar comparação, acessar resumo econômico e consequências nos pedidos e ir às decisões. Tudo respondeu nas três resoluções. Foram inspecionadas capturas de simulação, painéis e decisões; contraste foi calculado em amostra específica, não em toda a aplicação.
- Referências numéricas independentes e desempenho controlado detalhados abaixo. Os novos roteiros de auditoria não estão incluídos na contagem dos 664 testes.

O primeiro ensaio do roteiro integrado capturou uma resposta 200 anterior à resposta 500 pretendida, por falta de espera pelo término da atualização da biblioteca. browser-integrated-first.log foi preservado. O roteiro externo passou a esperar a lista arquivada e a resposta alvo; só então confirmou os achados nas três resoluções. Essa falha de sincronização do instrumento não foi classificada como defeito adicional do aplicativo.

## Achados confirmados

### INT-01 — P1 — Importação do modelo ignora a regra exportada

**Arquivos/funções:** atelier/web/app.js:1636 — importModel; atelier/service.py:611 — set_model; atelier/service.py:867 — export_model.

**Reprodução:** Exportar modelo em SPT; mudar a sessão para EDD; importar o JSON exportado. HTTP 200, mas regra continua EDD. Reproduzido no navegador nas três resoluções.

**Impacto:** O mesmo arquivo pode produzir sequenciamento diferente conforme o estado anterior da sessão, prejudicando reprodução de estudos.

**Correção proposta:** Definir contrato de importação: preservar dispatch_rule explícita válida; definir ausência legada; rejeitar inválida antes de alterar memória/disco; não confundir modelo com experimento completo.

**Evidências:** integrated-browser.json, browser-integrated.log.

### INT-02 — P2 — Auditoria por pedido recalcula folga a partir de conclusão arredondada

**Arquivos/funções:** atelier/technical_audit.py:53 — summarize_audit; atelier/web/app.js:988 — auditSlackStatus; simulation/engine.py — campos completion_h e lateness_h.

**Reprodução:** Ciclo 0,06 min, prazo 0,0005 h, multa 10000/h. Conclusão real 0,0010359130029347337 h, atraso 0,0005359130029347337 h, multa 5,36. Auditoria recebe conclusão 0 e publica folga +0,001 h, atraso 0.

**Impacto:** Diagnóstico de folga/atraso da auditoria contradiz a simulação em operações curtas. Não demonstrou erro do makespan, utilização ou throughput do motor.

**Correção proposta:** Consumir completion_h/lateness_h precisos, usar fallback explícito para legado e arredondar só no texto; testar perto do prazo e ciclos curtos.

**Evidências:** probes.json, probes.log.

### INT-03 — P2 — Um arquivo inválido impede leitura da biblioteca de experimentos

**Arquivos/funções:** atelier/service.py:338 — experiment_list; atelier/service.py:350 — save_experiment; atelier/web/app.js — loadExperiments.

**Reprodução:** Com um experimento válido, criar experimentos/invalid.json contendo []. GET /api/experiments retorna 500 por AttributeError em d.get. Reproduzido nas três resoluções; arquivo válido e inválido preservados.

**Impacto:** A biblioteca e novas gravações que consultam sua lista ficam indisponíveis por um documento malformado; não foi demonstrada perda dos arquivos.

**Correção proposta:** Validar estrutura por arquivo, preservar documentos inválidos e informar sua existência; não ocultar todo o acervo nem apagar registros para recuperar a lista.

**Evidências:** probes.json, integrated-browser.json, browser-integrated.log.

### INT-04 — P2 — Contraste insuficiente e rótulos muito pequenos em decisões

**Arquivos/funções:** atelier/web/styles.css — .alt-metrics small; atelier/web/app.js:1528 — renderização de métricas da decisão.

**Reprodução:** Cor computada rgb(117,134,129), fundo branco, fonte 10 px; contraste calculado pela luminância sRGB 3,829729:1 nas três resoluções.

**Impacto:** A amostra fica abaixo de 4,5:1 para texto normal (WCAG 1.4.3 AA); leitura em projetor ainda não testada. Tamanho 10 px é evidência de densidade, não um tamanho mínimo universal imposto pela WCAG.

**Correção proposta:** Ajustar tokens de cor e tipografia desses rótulos; conferir contraste >=4,5:1, alinhamentos e overflow nas três resoluções; preservar identidade e foco/zoom do mapa.

**Evidências:** visual-review.json, visual-review.log, capturas-integradas/decisoes_1920.png.

Os achados INT-01 a INT-03 não foram corrigidos neste trabalho. INT-04 também permanece como medido. A interface ainda permite os fluxos normais verificados; não se deve transformar o resultado da auditoria em afirmação de que todo uso está comprometido.

## Matemática, simulação, A/B e economia

probes.py calcula referências sem chamar helpers numéricos ou de despacho do motor. Seis casos de um posto usam conservação de trabalho e uma fila independente de máquinas livres. A variação sintética por unidade é reproduzida a partir da definição pública seed/id/unidade/etapa; ela não é eliminada para fazer o resultado coincidir. Foram comparados makespan, throughput, custo de capacidade e utilizações de máquina/equipe, com tolerância relativa 1e-12.

Casos: operação de 0,001 h; operação ainda menor; eficiência positiva 0,001; disponibilidade 0,5 e máquinas paralelas; quatro máquinas com equipe limitante e razão de 0,5 operador/máquina; três máquinas com dois operadores por máquina. Todos coincidiram com as referências. Isso é validação localizada, não enumeração de todo modelo fabril.

Na resposta temporal de reforço em 0,05 h, duas operações concluídas anteriormente conservaram exatamente o registro. O custo pela integral de capacidade antes/depois foi R$5,3059370988793875 na referência e R$5,305937098879387 no motor. A/B e recuperação também têm cobertura existente de despacho, tempo da ação e recursos. Não foi observada retroatividade nesses casos.

A fronteira, elegibilidade e economia arquivada mantêm contratos distintos: não dominância não significa SLA atendido ou ótimo global; custo do cenário não inclui automaticamente investimento; custo da decisão e economia líquida o consideram; componente ausente em legado não é zero. AM08/09/10 passaram nos roteiros de navegador. Não extrapolar busca finita para otimização global nem dispersão de sementes para probabilidade empírica de falha.

O motor cobra capacidade contratada no horizonte total do plano e usa disponibilidade/eficiência como fatores de ciclo. O score de criticidade mistura utilização, espera e fila como heurística explicitada. Operação interrompida mantém recursos, sem contar parada como processamento. Habilidades individuais, buffers finitos, setups dependentes de sequência, refugo/retrabalho/inspeção e recursos físicos de manutenção não são integralmente modelados. Esses limites aparecem no produto e não foram reclassificados como falhas de implementação.

## Arquitetura, persistência, segurança e registros

start.py → atelier.server → Studio → módulos simulation é uma separação operacional clara. O launcher principal usa biblioteca padrão e loopback, sem depender de Streamlit. O frontend consome o mesmo serviço e o replay usa eventos calculados. Existe acoplamento elevado: app.js tem 2.141 linhas e service.py 873, além de várias folhas CSS sobrepostas. Isso aumenta custo de manutenção, mas não justifica reconstrução nem troca do motor. AM18 deve ser gradual, depois das correções observáveis, com extração de responsabilidades mantendo contratos.

A persistência conserva bloqueio local, revisão por conteúdo e gravação preparada com rollback de falhas ordinárias. AM12 no browser bloqueou uma instância desatualizada e preservou a edição mais recente. Recuperação de projeto inválido e prioridades opcionais passaram novamente; a falha INT-03 é de outra coleção (experimentos) e não invalida as verificações de recuperação de projeto.

O registro de decisão segue condicionado à gravação, com origem, modelo, execução e conferência de quantias explícitas. O histórico antigo não é reescrito para completar componentes ausentes. Hash de integridade não é assinatura de identidade nem prova industrial; o modelo de uso é local. A conferência de texto não verifica toda afirmação econômica. Modo Banca/relatório reproduziram esse fluxo. A identidade do projeto acompanha registros e cache nos casos testados.

AM22 mantém validação de Host/Origin na porta efetiva; casos negativos e aliases locais passaram. Não há demonstração de proteção universal: não foi realizado ataque com DNS público, autenticação de usuários ou revisão de todos os serviços históricos. CSV principal possui neutralização de prefixos de fórmula para strings e renderizações examinadas usam escape; a inspeção não substitui fuzzing integral de todas as importações e exportações. Não foi demonstrado novo defeito de segurança nesta auditoria.

## Desempenho e experiência visual

Medições únicas controladas neste Linux, com outras verificações em andamento: abertura padrão aproximadamente 0,16 s; 12 réplicas de incerteza aproximadamente 0,09 s; 500 operações/cenário em aproximadamente 0,15 s; 25.000 operações/cenário, estimativa de 175.000 na análise, em aproximadamente 3,63 s. Esse último estado JSON teve 5.004.967 bytes e serialização de 0,10 s. Pico observado do processo: aproximadamente 199 MiB (203.380 KiB). Não são percentis, metas garantidas ou resultados para o Windows do usuário.

A entrada com 27.500 operações por cenário foi recusada antes de executar o motor, mantendo a execução anterior. A troca para modo reduzido e a indexação de replay passaram. Não foi executada carga irrestrita ou prometida responsividade equivalente em qualquer computador. O servidor serializa cálculos de Studio com lock; cargas pesadas devem ser avaliadas no hardware real antes de uso livre em apresentação.

A identidade visual atual é consistente nas capturas examinadas; mapa, foco, painéis e Modo Banca funcionaram. Não recomendo redesenho geral. A EV02 mantém a fábrica como primeira leitura e recolhe a narrativa em detalhes; resumo e consequências ficam na análise. Portanto, parte da evolução é discreta por posicionamento e opção de recolhimento, não ausência do código visual. Aumentar a percepção de qualidade deve começar por legibilidade e hierarquia, preservando a liberdade de navegação e as evidências.

A amostra de contraste INT-04 pede correção real. Outros pontos dependem de validação: leitura a distância, escala do Windows, contraste/iluminação do projetor e tempo de exposição da introdução. Não foi feita auditoria completa WCAG, nem ensaio com usuários; não se deve chamar essas suspeitas de falhas confirmadas.

## Situação em relação às etapas anteriores

| Etapa | Resultado nesta integração |
| --- | --- |
| AM01/AM02/AM03 | Contratos de persistência, despacho e confirmação de registro passaram; recuperação de projetos novamente verificada |
| AM04/AM05 | Elegibilidade/dominância e origem/validade de resultados passaram nos casos disponíveis |
| AM06/AM07 | Temporalidade e modo reduzido passaram; referência temporal independente coincidiu |
| AM08/AM09/AM10 | Componentes econômicos, amostras inviáveis e busca de capacidade passaram |
| AM11 | Núcleo numérico passou nas referências; INT-02 identifica consumidor de auditoria ainda arredondando cedo |
| AM12/AM13/AM14 | Conflitos de instâncias e rastreabilidade/identificação de pedidos e projetos passaram |
| AM15 | Foco/enquadramento passaram em 1/5/9/16/50 postos; legibilidade fora do mapa ainda tem INT-04 e validação de projetor |
| AM16/AM17 | Submissão duplicada e orçamento de trabalho passaram; carga controlada foi medida |
| AM19 | Suíte atual verde; as cinco falhas antigas não reapareceram. Runners históricos adicionais continuam com limites documentados |
| Prioridade opcional/recuperação | Novos testes e browser passaram; preservar ausência/inteiro explícito e originais na abertura |
| AM22 | Casos HTTP negativos e uso por endereços locais passaram |
| AM18/AM20/AM21 | Manutenção e caminhos históricos continuam como pendências de uso/escopo; não foram corrigidos nem integralmente homologados aqui |

INT-01 é do importador JSON do aplicativo principal; não deve ser confundido com AM20, que trata de importação clássica e defaults. Não há base para afirmar que todos os achados históricos adicionais foram resolvidos só porque a regressão principal passou.

## Suspeitas e pendências sem confirmação de defeito novo

1. Legibilidade no projetor e com escala do Windows: não testada; risco de apresentação, sem falha nativa demonstrada.
2. Latência/memória em outras topologias próximas dos limites: uma carga controlada não caracteriza todo o espaço permitido. O caso medido foi concluído; não há travamento confirmado.
3. Caminhos históricos de importação, radar/confiabilidade e runners Node antigos: há pendências registradas em documentos anteriores; esta rodada não os promove a homologados nem os usa para inferir falha da entrada principal.
4. Calibração industrial: dados sintéticos não comprovam aderência à fábrica real. Isso é uma limitação de validade externa, não um bug a resolver com CSS ou números ajustados.

Foi examinada a hipótese de filtragem do ensaio-meta por SLA arredondado: na base atual, as linhas da resposta usam metric(...), com precisão. Sem reprodução de erro; não entrou na lista de defeitos. Arredondamentos usados apenas na apresentação não foram tratados automaticamente como defeitos; INT-02 tem consequência calculada e contraditória comprovada.

## Plano de correções e critério de encerramento

1. **INT-01, próxima etapa recomendada:** contrato completo do round-trip JSON. Testar SPT/FIFO/EDD explícitos, ausência legada, entrada inválida, arquivo exportado reimportado em outro projeto e preservação transacional em falhas. Comparar resultados com a regra originalmente exportada. Branch/patch sobre AM22 ou sua sucessora imediata, nunca ZIP antigo.
2. **INT-02:** precisão na auditoria por pedido, sem reescrever motor. Conclusão/atraso precisos, fallback legado e classificação coerente perto do prazo, com testes de ciclos curtos e exportação/relatório que consomem esses campos.
3. **INT-03:** leitura resiliente da coleção arquivada. Um arquivo inválido não pode indisponibilizar válidos; aviso rastreável, sem apagar ou regravar históricos; testar objetos incompatíveis, JSON truncado, componentes legados e comparação após recuperação.
4. **INT-04:** correção pontual de contraste/escala tipográfica, sem redesenho. Conferir contraste, foco/teclado, três resoluções e legibilidade em Windows/projetor. Preservar abertura, gráficos, Modo Banca e zoom/foco do mapa.
5. **Portão final de demonstração:** instalar ZIP novo em pasta nova no Windows real; abrir/salvar/reabrir, importar/exportar, duplicar/trocar projetos, configurar falha e resposta, comparar A/B, executar ensaio, registrar justificativa, reabrir histórico e salvar PDF. Testar foco e zoom no projetor e confirmar fontes/cores. Preservar backup e evidências, sem substituir a instalação anterior até conferir dados.

Cada correção deve ser pequena, com reprodução, testes relevantes, checkpoint, ZIP/patch e downloads verificados. Uma nova auditoria de integração deve conferir a combinação final. Não começar AM18 ou funções novas como substituto desses quatro achados.

## Evidências e reprodução

base-manifest.json identifica o aplicativo; achados.json é o inventário estruturado; probes.json e performance.json trazem referências/medidas; browser-results.json lista os 13 módulos; integrated-browser.json e visual-review.json registram as novas verificações. Logs completos, scripts externos e capturas selecionadas acompanham o ZIP da auditoria. Falhas esperadas das sondagens documentam os bugs e não foram ocultadas para obter um parecer verde.

Regressão: `python -m pytest tests contract_tests atelier/tests -q -p no:cacheprovider`, a partir da extração AM22. Experimentos: `python -m atelier.tests.validacao_experimentos_banca`. A reprodução de navegador exige ambiente de desenvolvimento com Playwright/Chromium; não são dependências novas do aplicativo. Consulte LEIA_AUDITORIA.md para os scripts externos.
