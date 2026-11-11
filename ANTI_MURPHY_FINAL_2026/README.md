# ANTI-MURPHY — VERSÃO CANDIDATA À BANCA (2026)

**Comece por [`LEIA_PRIMEIRO_VERSAO_FINAL.md`](LEIA_PRIMEIRO_VERSAO_FINAL.md).** O modo de apresentação e os três experimentos estão descritos em `docs/`. O código do motor e o inicializador principal foram preservados.

---

# EDIÇÃO PARA BANCA — REVISÃO DE CONFIABILIDADE 2026

Consulte primeiro **`LEIA_PRIMEIRO_BANCA.md`**. Esta revisão acrescenta controle temporal de replay, auditoria de engenharia, folga de prazos, rastreabilidade estruturada e relatório técnico com metodologia e limitações. Para uma demonstração de cinco minutos, siga **`docs/GUIA_DE_DEMONSTRACAO_PARA_BANCA.md`**. O motor DES e o comportamento de cálculo industrial originais foram preservados.

---

> **Edição pré-final validada:** comece por `LEIA_PRIMEIRO_PRE_FINAL.md`. Mudanças e evidências em `docs/RELATORIO_PRE_FINAL_VALIDADA.md`.

# Edição de finalização — leia primeiro `LEIA_PRIMEIRO.md`

# Anti-Murphy — Redesign Industrial Workbench (revisão visual)

**Execução no Windows:** dois cliques em `INICIAR_ANTI_MURPHY.bat`, em uma pasta extraída independente. Python 3.10+ necessário. Não exige `npm install`. A abertura foi preparada para abrir o navegador automaticamente; o funcionamento no Windows ainda não foi homologado neste ambiente.

**Principais diferenças desta edição:** fundo cinza-azulado mais neutro, máquinas e área industrial mais expressivas, timeline visível junto ao mapa, inspeção gráfica e foco em máquinas, tela ampliada para apresentação, comparador A/B com avanço por pedido e histograma Monte Carlo. A abertura da logo oficial, ajuda contextual, projetos, experimentos, Murphy local e relatórios foram preservados. O núcleo `heapq` não foi alterado.

**Documentos:** `CHANGELOG_REDESIGN_2026.md`, `docs/RELATORIO_REDESIGN_2026.md` e `docs/GUIA_DEMONSTRACAO_REDESIGN.md`.

**Limites:** as ferramentas clássicas ATLAS/NEXUS ainda funcionam separadamente; restrições industriais de habilidades, buffers e setups não são integralmente verificadas. Uso com dados sintéticos.

---

# Anti-Murphy | Ambiente integrado de PCP — edição novembro/2026

**Ponto de entrada único:** execute `INICIAR_ANTI_MURPHY.bat` no Windows. O programa abre o navegador automaticamente em `127.0.0.1`; mantenha a janela de execução aberta para usar o sistema e feche-a para encerrar. Requer **Python 3.10+** instalado. No uso do ambiente principal **não há npm, Node.js nem instalação de dependências Python**. A abertura no Windows não foi homologada neste ambiente Linux.

## Novidade: ajuda, interpretação e demonstração

- **Conhecer o software** inicia um percurso guiado opcional. Feche-o a qualquer momento.
- **Ajuda** explica o que faz cada tela, quando utilizá-la e como interpretar os resultados.
- Use os botões **?** dos indicadores, **Por que este resultado?** ao selecionar um pedido, e os **marcos temporais** da simulação.
- Na **Análise**, use **Relatório técnico** para abrir um documento imprimível e salvar como PDF pelo navegador.
- Para apresentar aos colegas, siga `docs/GUIA_DEMONSTRACAO_COLEGAS.md`.

## Comece por aqui

1. Na barra superior, abra **Projeto principal**. Você pode criar um projeto independente, duplicar o modelo atual, renomear ou retomar um projeto salvo.
2. Em **Modelo**, configure postos, operadores, roteiros, pedidos e parâmetros. Alterações geram nova simulação; o modelo fica salvo no projeto ativo.
3. Em **Simulação**, controle a linha do tempo, selecione máquinas e pedidos, examine o roteiro de uma ordem e abra **Programação por posto** para visualizar operações e paradas.
4. Em **Análise**, configure uma falha, escolha alternativas e explore **Custo × Prazo**. Use **Arquivar experimento** para guardar a simulação atual e comparar duas execuções depois.
5. Use **Ensaios**, **Ferramentas**, **Decisões** e **Registros** para análises de sensibilidade, experimentação adicional, consulta ao Murphy local, evidências e registro formal.

A visualização contém dados de **simulações sintéticas**. A representação de equipamentos e seus movimentos não equivale a uma fábrica conectada fisicamente. O simulador não impõe ainda integralmente restrições por habilitação, buffers finitos e setups dependentes da sequência.

## Funções avançadas históricas

O projeto conserva em `FERRAMENTAS_HISTORICAS/` as telas completas do War Room, Executive Room, Optimization Hub, Portfolio e outros módulos ATLAS/NEXUS **em uma interface clássica opcional**. Não afirmamos que esses módulos estejam todos integrados ao novo ambiente. Abra `FERRAMENTAS_HISTORICAS/ABRIR_ATLAS_NEXUS.bat` somente se precisar do modo antigo; ele pode exigir instalar Streamlit na primeira execução. Consulte `docs/CONTROLE_DE_FUNCIONALIDADES.md`.

## Documentos desta edição

- `docs/NOVIDADES_EDICAO_2026.md` — funcionalidades novas e critérios verificados.
- `docs/QUALIDADE_E_LIMITACOES_2026.md` — resultados de testes e falhas conhecidas, sem homologação industrial.
- `docs/PESQUISA_E_DIRECAO_DE_PRODUTO_2026.md` — referências estudadas, alternativas descartadas e próximos investimentos.
- `docs/CONTROLE_DE_FUNCIONALIDADES.md` — inventário dos módulos preservados, integrados e pendentes.
- `docs/capturas_reais/` — imagens geradas no Chromium com dados servidos pelo Python.

O código principal é `atelier/server.py`, `atelier/service.py`, `atelier/web/` e `simulation/engine.py`. Testes em `atelier/tests/` e `contract_tests/`. O legado original continua no projeto. **Mantenha cada instalação em pasta independente; não sobrescreva as versões anteriores.**


## Novembro de 2026 — Painéis analíticos integrados

A seção **Painéis** agora está acessível no menu principal e a partir de **Simulação**. Oferece Operação, Desempenho, Cenários, Otimização e Robustez, compartilhando os resultados do motor V30.2, a seleção de respostas e o projeto ativo. Clique em um posto ou pedido para voltar à fábrica com o elemento selecionado. Os gráficos de robustez são executados sob demanda e não são previsões calibradas.

Documentação técnica, evidências de testes e limitações: `docs/PAINEIS_INTEGRADOS_2026.md`. A versão original das ferramentas históricas foi mantida em `FERRAMENTAS_HISTORICAS/`.
