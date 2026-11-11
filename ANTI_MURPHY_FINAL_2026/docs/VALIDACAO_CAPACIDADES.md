# Validação — recuperação de capacidades e integração

## Escopo desta revisão

Base técnica: pacote `ANTI_MURPHY_CORRECAO_NAVEGACAO_LEGIBILIDADE.zip`.
As funções originais do motor de eventos discretos (`simulation/engine.py`),
modelagem, decisões e ferramentas clássicas não foram reescritas nesta entrega.
As novas ferramentas chamam diretamente módulos que já existiam no histórico.

### Ferramentas nativas implementadas

| Ferramenta | Função do motor | Resultados no exemplo |
|---|---|---|
| Diagnóstico operacional | `operating_alerts`, `model_confidence`, `explain_comparison` | 5 postos, 4 alertas |
| Oportunidades de melhoria | `generate_opportunities` | 21 alternativas |
| Sensibilidade de capacidade | `sensitivity_analysis` | 4 níveis de recurso |
| Limite de demanda | `demand_breakpoint` | 7 níveis de 1,0× a 1,6× |
| Monte Carlo | `monte_carlo_analysis` | 12 sementes |
| Recuperação | `recovery_plan` | 4 respostas exploratórias |

**Nota de engenharia:** os testes pressupõem o modelo de demonstração sintético.
A quantidade de resultados depende dos dados que o usuário informar.
Resultados de capacidade não incluem custos completos de investimento,
competências individuais nem buffers finitos. As ferramentas são explorações,
não recomendações industrialmente certificadas.

### Testes executados

- **147 testes Python aprovados**, 10 subtestes, em regressão selecionada de motor,
  decisões, replay, contratos e integração; **quatro testes antigos desse grupo
  foram desmarcados** porque exigem nomes de inicializador, uma prévia HTML ou
  roteamento de telas de versões anteriores, que não correspondem à estrutura
  atual. Não foram alterados apenas para fazê-los passar.
- Um grupo adicional de testes antigos que importa `streamlit` não pôde ser
  coletado porque Streamlit não está instalado no ambiente de teste.
- `node --check atelier/web/app.js`: sintaxe validada.
- Navegação Chromium/Playwright: 1280×720, 1366×768 e 1920×1080;
  área inicial, Modelo, Análise, Ensaios, Ferramentas, Decisões e Registros;
  Início, Voltar e retorno do navegador funcionando.
- QA Chromium com backend Python real via ponte de teste: seis ferramentas,
  resultados visíveis, sem alteração do experimento atual, registro de decisão
  condicionado a justificativa, replay A/B, edição do modelo e consulta ao
  Murphy. Capturas em `docs/capturas_reais`.
- Smoke HTTP real via `urllib`: servidor iniciado, GET `/`, GET `/styles.css`,
  GET `/api/state` e POST `/api/advanced` com **21 resultados**.

### Limitações de teste

- O navegador foi automatizado com uma ponte de teste para a API Python porque
  o navegador do ambiente não permite acessar HTTP loopback. Endpoints HTTP
  reais foram testados em processo separado via `urllib`.
- Não foi possível iniciar um Windows real; o arquivo `INICIAR_ANTI_MURPHY.bat`
  exige validação no computador do usuário. Foi incluída abertura automática
  pelo navegador padrão no Windows, com fallback.
- Não houve medição de FPS no hardware do usuário nem testes de operação fabril.
- O código original da suíte ATLAS/NEXUS permanece no pacote e pode ser iniciado
  separadamente, mas suas telas completas não foram convertidas para a nova
  interface. **Não afirmar que a migração total já foi concluída.**

### Testes para repetir

```bash
python -m unittest atelier.tests.test_service atelier.tests.test_advanced_product -q
python -m atelier.tests.browser_nav_qa
python -m atelier.tests.browser_advanced_qa
python -m atelier.tests.browser_quality
node --check atelier/web/app.js
```

A suíte browser usa Playwright/Chromium e não é necessária para o usuário final.
