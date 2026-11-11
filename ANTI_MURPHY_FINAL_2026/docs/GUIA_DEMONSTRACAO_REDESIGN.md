# Demonstração rápida do Anti-Murphy

**Preparação:** extraia em uma pasta nova, execute `INICIAR_ANTI_MURPHY.bat`, abra o projeto de exemplo e mantenha a simulação em tela. A abertura usa a marca oficial. Evite fechar a janela do servidor durante a apresentação.

### Sequência sugerida (cerca de três minutos; adapte ao público)

1. **Simulação:** mostre a fábrica, selecione a CNC, observe o detalhamento da máquina e as filas. Pause para inspecionar o instante.
2. **Incidente:** clique em **Configurar incidente**, escolha duração e horário, e execute as simulações. Não diga que os dados são medições reais: são sintéticos.
3. **Comparação:** volte à **Simulação**, selecione **Comparar** e use o controle de divisão A/B. Arraste a linha do tempo para depois da parada; consulte as filas e a evolução das ordens nos dois cenários.
4. **Análise:** selecione uma intervenção; mostre custo, cumprimento de prazos, impactos por pedido e a indicação de restrições não verificadas. Explique que o investimento da intervenção pode alterar a diferença econômica.
5. **Ferramentas:** abra **Monte Carlo** e execute a análise; o histograma apresenta os valores realmente obtidos nas execuções. Se todos forem iguais, isso é um resultado do modelo, não erro de renderização.
6. **Decisões:** consulte a análise local do Murphy, explique a recomendação e mostre que registrar uma decisão exige justificativa. Abra o relatório técnico se houver tempo.

### Apresentação em telão

Use **Ampliar mapa ↗** no topo da simulação; pressione Escape ou clique em **Sair da tela ampliada** para retornar. O recurso é visual e não altera a produção calculada.

### O que não afirmar

- Que o Anti-Murphy controla máquinas ou utiliza sensores em tempo real.
- Que as restrições de habilitações, buffers finitos e setups estão integralmente validadas.
- Que uma alternativa é economicamente melhor sem incluir todos os investimentos relevantes.
- Que o aplicativo foi homologado no Windows ou mantém 60 FPS, antes de medir no hardware da apresentação.
