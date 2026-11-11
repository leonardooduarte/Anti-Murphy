# Anti-Murphy — Gráficos de Engenharia | Edição Banca 2026

Esta edição parte da **ANTI_MURPHY_EDICAO_BANCA_ENGENHARIA_2026** e preserva o motor, os dashboards, a fábrica, o Murphy AI, os projetos, os relatórios e as ferramentas históricas.

## Abrir no Windows

1. Extraia todo o ZIP em **uma pasta nova** (não sobrescreva as versões anteriores).
2. Dê dois cliques em `INICIAR_ANTI_MURPHY.bat`.
3. Mantenha aberta a janela que exibe o servidor local. O navegador deve abrir automaticamente.
4. O aplicativo principal não exige npm ou compilação React, somente Python compatível com os requisitos existentes.

## Onde testar

- **Ensaios:** seis estudos com gráficos específicos. Execute, selecione um indicador, clique em um ponto e confira o dado na tabela.
- **Ferramentas:** Diagnóstico, Oportunidades, Sensibilidade, Limite de demanda, Monte Carlo e Recuperação.
- **Painéis → Robustez:** nova visualização das 12 execuções.
- **Dados CSV** exporta os valores brutos de uma análise; **Figura SVG** exporta o gráfico vetorial, adequado para relatórios e apresentações.

## Cuidados

- Não confunda a linha que liga ensaios discretos com cálculo de pontos intermediários.
- Não declare economia garantida: custos de oportunidade, investimento e certas restrições industriais exigem validação.
- Resultados Monte Carlo provêm de sementes sintéticas, não de distribuições empíricas calibradas.
- As telas históricas ainda estão disponíveis em `FERRAMENTAS_HISTORICAS` (podem requerer Streamlit).

Veja `docs/RELATORIO_GRAFICOS_ENGENHARIA.md` e `docs/ROTEIRO_GRAFICOS_BANCA.md`.
