# Edição de qualidade — novembro de 2026

A versão inclui correções de custos, explicação contextual do Murphy, navegação por registros da operação e melhorias de contraste. **Inicie apenas com `INICIAR_ANTI_MURPHY.bat`.** Não instale npm.

Consulte `docs/CHANGELOG_QUALIDADE_FINAL.md`, `docs/VALIDACAO_QUALIDADE_FINAL.md` e `docs/ROTEIRO_DEMONSTRACAO_FINAL.md`.

Os testes no Windows ainda são necessários. As ferramentas ATLAS/NEXUS não migradas permanecem em `FERRAMENTAS_HISTORICAS`.

---

# ANTI-MURPHY — ESTÚDIO INDUSTRIAL | EDIÇÃO DE FINALIZAÇÃO

Versão baseada na **Anti-Murphy — Painéis Integrados 2026**. A edição mantém
os dados, o motor Python e as análises existentes e adiciona melhorias de
investigação visual e edição dos modelos. O programa não executa ações físicas
sobre equipamentos industriais.

## Abrir no Windows

1. Extraia o ZIP em uma pasta **nova**, fora da pasta da versão anterior.
2. Dê dois cliques em **`INICIAR_ANTI_MURPHY.bat`**.
3. O navegador padrão deve abrir automaticamente. Não precisa de npm, Node,
   Streamlit nem compilação frontend para o aplicativo principal.
4. Caso a abertura automática falhe, leia o endereço exibido pelo inicializador.
   Mantenha a janela do servidor aberta enquanto estiver utilizando o programa.
5. Para encerrar: feche o aplicativo e pressione `Ctrl+C` na janela do servidor.

Requisito: **Python 3.10+** instalado no Windows e disponível como `py` ou `python`.

## O que há de novo

- Novo tratamento visual Industrial Workbench com fundo, tipografia e controles mais consistentes.
- Mapa da fábrica menos parecido com cartões: bases industriais, equipamentos ampliados,
  status e animações de processamento/parada ligadas ao replay do simulador.
- Faixa de investigação do incidente com ações **Localizar no mapa**,
  **Examinar pedidos** e **Comparar respostas**.
- A comparação A/B escolhe automaticamente um instante com diferença operacional
  observável nos estados do motor, sem inventar resultados.
- Editor estruturado de roteiros: adicionar, remover e reordenar etapas, selecionar
  postos válidos e informar minutos por unidade, com validação antes de salvar.
- Rastreio de pedidos com espera registrada por operação e salto para o instante
  no replay.
- Painel de otimização com identificação de alternativas não dominadas entre
  as **respostas enumeradas que atendem aos critérios modelados**; não representa ótimo global.
- Acesso contextual ao Murphy a partir do posto selecionado, reaproveitando o
  assistente local de leitura já existente.
- Abertura com a marca, tutoriais, projetos, registros, dashboards e ferramentas
  históricas seguem preservados na distribuição.

## Teste rápido recomendado

1. Abra **Início** e teste **Localizar no mapa** (CNC).
2. Clique em **Comparar respostas** e arraste a divisão A/B.
3. Selecione uma máquina e abra **Ver programação**.
4. Abra **Modelo → Ordens de produção → Editar etapas**; experimente reordenar.
   Só clique em **Aplicar alterações** se desejar recalcular o projeto.
5. Abra **Painéis → Otimização**; selecione uma alternativa e examine os indicadores.
6. Abra **Decisões** e consulte o Murphy. Confira as premissas e limites antes de registrar.

## Importante

- O **motor de simulação, serviço de dados e servidor local** não foram modificados
  nesta edição. Há novas interações, apresentação e testes.
- Os dados padrão são **sintéticos**, destinados a estudar decisões de PCP.
- Não há validação integral de skills individuais, setups por sequência ou buffers finitos.
- A interface da ATLAS/NEXUS em Streamlit continua em **FERRAMENTAS_HISTORICAS**.
  Nem todos esses módulos foram migrados para a navegação principal.
- A execução ponta a ponta no **Windows do usuário** ainda requer confirmação.
- Nenhum benchmark de 60 FPS ou validação com operação industrial real foi realizado.

Consulte `docs/RELATORIO_ESTUDIO_FINALIZACAO.md` para dados de testes e pendências.
