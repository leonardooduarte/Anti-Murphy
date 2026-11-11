## Correção de navegação e legibilidade — novembro/2026

A gravação `13.mp4` mostrou duas falhas de experiência: não havia retorno explícito para o início em todas as áreas e elementos das telas clássicas apareciam claros sobre fundo claro.

- A interface principal agora mantém **Início** e **Voltar** visíveis no cabeçalho; o botão **Início** também aparece na navegação lateral.
- Os botões não reiniciam o experimento; apenas mudam a área. O botão **Voltar** funciona para a área anterior e as teclas de navegação do navegador preservam as rotas.
- Em **FERRAMENTAS_HISTORICAS\ABRIR_ATLAS_NEXUS.bat**, a área Streamlit apresenta **Voltar ao início** no menu. Se a aplicação principal estiver aberta, surge também um link fixo que volta à aplicação principal no navegador.
- Contraste editorial corrigido para títulos, legendas e textos gerais na interface clássica. Tipografia secundária ampliada no ambiente novo.

**Importante:** a interface clássica permanece separada e ainda possui visualizações históricas heterogêneas. Seu teste completo no Windows depende da instalação opcional do Streamlit. As verificações automatizadas de CSS não substituem a homologação dessas telas no Windows.

Os resultados do simulador, arquivos de projeto e regras do motor **não foram alterados** nesta correção. Consulte `CORRECOES_NAVEGACAO_E_LEITURA.md`.

---

# Anti-Murphy — Ambiente integrado de simulação e decisão em PCP

Versão de trabalho destinada a recuperar capacidades reais do Anti-Murphy e tornar o uso mais direto, sem uma coleção de demos isoladas. **Não é um sistema industrial homologado**: os cenários demonstrativos são sintéticos e o software não controla equipamentos físicos.

## Abrir no Windows

1. Extraia o ZIP inteiro para uma pasta própria.
2. Dê dois cliques em **`INICIAR_ANTI_MURPHY.bat`**.
3. O navegador padrão abrirá sozinho na aplicação local (servidor em `127.0.0.1`, porta livre escolhida automaticamente).
4. Mantenha a janela do servidor aberta. Para encerrar, pressione `Ctrl+C` na janela ou feche-a.

**Requisito do novo ambiente:** Python 3.10 ou superior no PATH, sem instalação npm/Node ou Streamlit. A interface, suas animações e a lógica do simulador já estão empacotadas; a primeira execução do aplicativo principal não baixa bibliotecas. No Windows pode aparecer um aviso de firewall ou SmartScreen dependendo das configurações da máquina. O inicializador `.bat` não foi homologado neste ambiente Linux.

### Ferramentas históricas (opcional)

**`FERRAMENTAS_HISTORICAS\ABRIR_ATLAS_NEXUS.bat`** abre a versão histórica Streamlit/ATLAS/NEXUS, que está preservada no mesmo ZIP e ainda possui recursos não migrados para o ambiente novo (War Room completo, Executive Room, Scenario Portfolio, Trust Center, Optimization Hub original e funções opcionais de IA). Esta opção pode precisar de internet *na primeira abertura* para instalar dependências Python em `.venv_classic`. Os dois ambientes são separados em interface; o modelo salvo do novo ambiente é lido pelo clássico ao iniciar, mas resultados e decisões não são sincronizados automaticamente.

## Jornada principal do produto

- **Modelo:** editar máquinas, operadores, tempos, disponibilidade, roteiros, pedidos, custos e prioridades; importar/exportar JSON. Edições são salvas na pasta `workspace/projeto.json` e recalculam a simulação.
- **Simulação:** acompanhar a fábrica por posto, observar filas/operações/peças, selecionar postos e pedidos, acelerar ou pausar o replay, consultar cenário original, incidente ou intervenção e dividir a visualização no mesmo instante para comparar cenários.
- **Análise:** configurar um incidente, duração, horário, orçamento e objetivo; executar uma rodada do DES e comparar as respostas enumeradas pelo motor, inclusive impactos por pedido.
- **Ensaios:** sensibilidade à duração da parada, FIFO/SPT/EDD, seis repetições pareadas, dezesseis perturbações sintéticas, busca de meta de entrega e busca discreta de capacidade.
- **Ferramentas:** diagnóstico operacional com alertas clicáveis, oportunidades de melhoria, sensibilidade a recursos, limite de demanda, Monte Carlo e recuperação após incidentes. Resultados calculados pelo motor, sem alterar o modelo ou a decisão selecionada. Inclui exportação JSON.
- **Decisões:** investigar resultados com o Murphy local determinístico, selecionar alternativa e registrar justificativa obrigatória sem aplicar intervenção física.
- **Registros:** reabrir decisões e consultar evidências guardadas em `workspace/registros`.

O programa possui uma abertura animada com a marca oficial. É possível pular a animação; as preferências de movimento reduzido são respeitadas. As animações operacionais refletem a ocupação e estados calculados pelo motor; o desenho de máquinas é ilustrativo e deslocamentos não são modelados.

## Integridade e limitações

O motor de simulação de eventos discretos do V30.2 foi preservado. Os custos operacionais exibidos no mapa **não incluem investimento da intervenção**; a análise de alternativas apresenta o custo de decisão (incluindo investimento onde calculado pelo motor). Regras de habilidades individuais, capacidade física dos buffers e setups dependentes da sequência **não estão integralmente validadas**. Candidatos que passam nas regras atuais do modelo não devem ser tratados como intervenções industrialmente certificadas. Murphy local trabalha offline, sem rede/serviço generativo externo.

Os recursos avançados históricos não foram todos redesenhados nem unidos à nova UI. Eles estão disponíveis no modo clássico opcional; consulte `docs/CONTROLE_DE_FUNCIONALIDADES.md` para o estado de cada capacidade.

## Testes

A suíte nova usa `unittest` do Python. Testes de integração visual usam Playwright/Chromium **apenas para desenvolvimento** (não são exigências para utilização). A matriz de testes e limitações de ambiente está em `docs/VALIDACAO.md`.

## Estrutura de pastas

- `start.py`: entrada do novo ambiente local.
- `atelier/service.py`: serviços de simulação, edição, comparação e registros.
- `atelier/server.py`: servidor HTTP local, somente `127.0.0.1`.
- `atelier/web/`: interface HTML/CSS/JavaScript, animações e marca oficial.
- `simulation/`, `data/`, `legacy_app.py`, `app.py`, `app_classico.py`: motor V30.2 e ferramentas históricas preservadas.
- `atelier/tests/`: testes de serviço e jornada visual.
- `docs/capturas_reais/`: capturas do aplicativo durante testes em Chromium com API de ensaio conectada ao serviço Python real.
- `workspace/`: criado automaticamente quando o aplicativo é executado; armazena projeto e decisões locais.
