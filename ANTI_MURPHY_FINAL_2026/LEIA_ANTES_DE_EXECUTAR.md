# Anti-Murphy — edição de recuperação de capacidades

## Por que esta entrega foi feita

A sequência V29.1 → V30.2 → Factory Command → V31 manteve funções nos arquivos,
mas tornou várias inacessíveis no produto novo. A prioridade foi recuperar
capacidades da análise, evitando criar uma demonstração desconectada.

## O que mudou no aplicativo principal

- Área **Ferramentas** integrada à navegação principal, sem Streamlit ou npm.
- Diagnóstico operacional do cenário com falha: filas, capacidade, utilização e alertas.
- **Oportunidades:** 21 cenários enumerados no exemplo; operadores, máquinas,
  realocações, regras de despacho e redução de setup.
- **Sensibilidade de capacidade:** 0 a 3 unidades adicionais de um recurso.
- **Limite de demanda:** varredura entre 1,0× e 1,6× da carteira.
- **Monte Carlo:** 12 execuções sintéticas do mesmo incidente, sementes diferentes.
- **Recuperação:** intervenções de capacidade sobre o cenário de falha.
- Gráficos de sensibilidade e cumprimento de prazos com valores do motor.
- Alertas clicáveis que levam ao posto de trabalho correspondente na simulação.
- Exportação da análise em JSON, com experimento identificável.
- Uma decisão registrada exige justificativa própria; textos anteriores não
  são reaproveitados automaticamente.
- A antiga abertura com a marca foi mantida; os movimentos de máquina seguem
  o estado de processamento calculado, e o modo de comparação A/B permanece.
- Inicializador principal único: **INICIAR_ANTI_MURPHY.bat**.

## Funcionalidades que permanecem acessíveis

Modelo editável, simulação de evento discreto, alternativas para incidentes,
comparação de custos/prazos, replay, Murphy local, laboratório de metas, estresse,
despacho e registro de decisões. O código clássico de War Room, Optimization Hub,
Executive Room, Scenario Portfolio e outros módulos está preservado; para abrir
a interface histórica separada use `FERRAMENTAS_HISTORICAS/ABRIR_ATLAS_NEXUS.bat`.
O aplicativo principal não é equivalente a todas as telas históricas.

## Limitações honestas

- **Não é uma reconstrução visual integral** de toda a suíte ATLAS/NEXUS.
- Skills individuais, buffers físicos limitados, setups por sequência e custos
  completos de investimento **não foram validados industrialmente**.
- O ranking de oportunidades não comprova aplicabilidade real nem ótimo global.
- A interface clássica ainda usa Streamlit e pode solicitar bibliotecas na
  primeira utilização; os estados de sessão não são sincronizados automaticamente.
- Testes de tela realizados em Chromium/Linux; o launcher `.bat` requer validação
  em Windows.

## Passo a passo no Windows

1. Descompacte todo o ZIP em uma pasta nova (não substitua a versão anterior).
2. Clique duas vezes em **INICIAR_ANTI_MURPHY.bat**.
3. O navegador padrão deve abrir o aplicativo local automaticamente.
4. Experimente **Modelo → Simulação → Análise → Ferramentas → Decisões → Registros**.
5. Feche com `Ctrl + C` na janela que abriu o servidor quando terminar.

Requer Python 3.10+; não exige `npm install` nem instalar Streamlit para a
interface principal. O código não acessa a fábrica real, nem serviços externos.

Consulte `docs/VALIDACAO_CAPACIDADES.md` para testes e comparativos.
