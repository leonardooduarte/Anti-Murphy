# Verificação da versão candidata — 06/11/2026

## Escopo e resultados executados

| Verificação | Resultado | Evidência / ressalva |
|---|---|---|
| Verificação SHA-256 de componentes críticos | 11/11 byte a byte iguais | `MANIFESTO_COMPONENTES_PRESERVADOS.json`; inclui engine, serviço, inicializador, gráficos e logo |
| Testes Python de motor, contrato e interface | **204 aprovados**, 4 retirados por incompatibilidade com versão anterior, 10 subtestes aprovados | Execução `pytest -q atelier/tests contract_tests tests` com exclusões detalhadas abaixo |
| Três experimentos de engenharia | **3 aprovados** | `python -m atelier.tests.validacao_experimentos_banca` |
| Modo banca, navegação e falha no navegador | **3 resoluções** verificadas | Chromium 1280×720, 1366×768 e 1920×1080 com adaptador para o serviço Python real; sem exceções JS nos fluxos exercitados |
| Ferramentas avançadas, registro e navegação | **2 resoluções** verificadas | Chromium 1366×768 e 1920×1080 com serviço Python real adaptado; 6 análises, decisão e retorno à página inicial |
| Rotas HTTP reais | **Aprovadas** | `http_charts_smoke.py` e `http_banca_smoke.py`: recursos, dashboards, auditoria, 12 análises e troca da alternativa |
| Compilação sintática do JavaScript | **Aprovada** | `node --check atelier/web/app.js` |
| Windows 10 e hardware da apresentação | **Não confirmado** | Esta execução de testes ocorreu em ambiente Linux com Chromium |
| Módulos históricos Streamlit | **Não homologados nesta rodada** | Preservados nos arquivos, mas sem teste de abertura integral no Windows |
| Uso do MiroFish | **Não realizado** | Nenhuma avaliação multiagente foi usada como evidência |

## Exclusões explícitas do grupo de testes

Os testes de interface e plataforma preservados de versões antigas incluem afirmações que se tornaram incompatíveis com o **inicializador local `start.py` e o frontend HTML/SVG integrado**. Foram retirados da contagem de aprovação, sem adulterar o código para satisfazer expectativas obsoletas:

- `tests/test_restauracao_acesso.py::test_inicio_prioriza_o_workspace_original_e_nao_o_mapa`
- `tests/test_restauracao_acesso.py::test_modulos_importantes_tem_atendimento_direto`
- `tests/test_v31_editorial.py::test_only_one_root_launcher`
- `tests/test_v31_editorial.py::test_preview_has_no_external_script_dependency`

Também não foram executados nessa regressão os arquivos `tests/test_nexus_ui.py`, `tests/test_nexus_v30.py`, `tests/test_operation_ui.py` e os dois testes de `tests/test_workspace_bridge.py` (a execução envolvendo esse último grupo excedeu o limite operacional durante o ensaio, sem resultado conclusivo). **Portanto, “204 aprovados” não deve ser apresentado como aprovação universal do acervo histórico.**

## Comandos para reproduzir

```bash
# Na pasta raiz da aplicação; sem interferir em workspace do usuário
python -m atelier.tests.validacao_experimentos_banca
PYTHONPATH=. python atelier/tests/browser_final_banca.py
PYTHONPATH=. python atelier/tests/browser_advanced_qa.py
PYTHONPATH=. python atelier/tests/http_charts_smoke.py
PYTHONPATH=. python atelier/tests/http_banca_smoke.py
```

`browser_final_banca.py` usa Chromium local e `playwright`, instalados no ambiente de QA mas **não exigidos para usar o software**. Os smoke tests HTTP usam biblioteca padrão e simulador real.

## O que foi confrontado de maneira independente

- Ordem e quantidade de pedidos, total de 96 unidades e conclusão de cada pedido.
- SLA contado por pedido a partir de horário de conclusão e prazo.
- Makespan frente à última conclusão dos pedidos.
- Throughput calculado de novo por unidades/makespan.
- Penalidades somadas a partir dos pedidos e composição dos custos do cenário.
- Identidade do custo de decisão e da diferença projetada, com tolerância explícita por arredondamento.
- Monotonicidade temporal dos inícios, paradas segmentadas e términos das operações.
- Resposta marginal de throughput ao aumento isolado de máquinas CNC.
- Trade-off entre makespan, SLA e custo em duas alternativas calculadas.

**Limitação essencial:** os mesmos dados sintéticos alimentam motor e conferências, portanto não demonstram precisão preditiva no mundo real. Uma auditoria de código mais profunda, análise de exceções de capacidade e validação industrial seriam etapas posteriores.

## Checklist no computador da banca

- Abrir `INICIAR_ANTI_MURPHY.bat` sem npm, instalar pacotes ou cadastrar API.
- Ativar Modo banca e percorrer as seis etapas com eventos sincronizados e texto legível no projetor.
- Verificar diferença visual de A e B e dados de SLA/custo; voltar ao modo padrão sem perder o modelo.
- Entrar em **Ensaios**, executar uma análise; repetir em **Ferramentas** e exportar CSV/SVG.
- Registrar decisão com justificativa e reconhecimento das limitações; reabrir no histórico.
- Abrir auditoria técnica e relatório; conferir salvamento local e reinicialização.
- Testar sem Internet, se possível, e guardar capturas como contingência.
