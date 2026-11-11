# Anti-Murphy — Edição para banca 2026

## Executar em Windows

1. Extraia o ZIP inteiro para uma **pasta nova**. Não sobrescreva suas outras versões.
2. Execute **`INICIAR_ANTI_MURPHY.bat`** com dois cliques.
3. Mantenha a janela do servidor aberta; o programa deve abrir no navegador padrão.
4. Requer Python 3.10 ou superior; o aplicativo principal não requer npm, Node.js nem Streamlit.
5. Para encerrar, use `Ctrl+C` na janela do processo.

## Recomendo testar primeiro

- **Início:** nova reprodução 1× = 10 minutos simulados por segundo real; 0,5×, 2×, 4× e 8× disponíveis.
- **Pausar nos eventos:** marque a opção e veja o programa interromper a reprodução quando começa a falha.
- **Comparar:** observe A e B no mesmo instante e os dois conjuntos de indicadores; B exibe o custo da decisão, incluindo investimento.
- **Painéis → Auditoria técnica:** folga por pedido, diferença entre gargalo pontuado e maior espera, verificação dos custos e limitações do modelo.
- **Decisões:** registre justificativa, riscos e reconhecimento das limitações. **Registros** apresenta a ficha legível e permite abrir o JSON técnico.
- **Relatório técnico:** imprimir ou salvar como PDF pelo navegador, com custos e folgas explicados.

**Para a apresentação aos professores:** `docs/GUIA_DE_DEMONSTRACAO_PARA_BANCA.md`.

**Relatório de testes:** `docs/VALIDACAO_TECNICA_BANCA.md`.

## Limites

Os exemplos são sintéticos. Este software é de apoio à avaliação de alternativas de PCP, não controla máquinas e não certifica a viabilidade física de intervenções. As ferramentas clássicas ATLAS/NEXUS continuam preservadas em `FERRAMENTAS_HISTORICAS`, mas não foram integralmente migradas. Ainda é necessário verificar abertura e desempenho no Windows que será usado na banca.
