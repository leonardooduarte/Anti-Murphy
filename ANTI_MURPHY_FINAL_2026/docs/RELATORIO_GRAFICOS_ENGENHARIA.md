# Anti-Murphy — Revisão técnica das visualizações para a banca

## Princípio adotado

O motor de eventos discretos Python mantém a responsabilidade por custo, filas, throughput,
SLA, makespan e cenários. O navegador **não recalcula esses valores**; apenas desenha
os pontos correspondentes ao JSON do motor. Não foram adicionadas dependências JS,
APIs pagas ou compilações npm.

### Ensaios

| Ensaio | Gráfico | Observações para interpretação |
|---|---|---|
| Sensibilidade da parada | Curvas de duração × término/custo/SLA | Os pontos são discretos. A linha não prevê durações intermediárias |
| Regras EDD, SPT e FIFO | Diagrama de pontos comparativos | Mesma semente e incidente; diferentes indicadores podem favorecer políticas distintas |
| Robusteza da resposta | Barras divergentes com eixo zero | Economia líquida negativa é **prejuízo**, mostrada à esquerda do zero; verde/laranja respeitam a direção do indicador |
| Meta de entregas | Comparação das alternativas filtradas | Não constitui otimização global |
| Stress Lab | Dispersão do SLA versus custo/unidade, com troca de métrica | Dezesseis cenários sintéticos não são frequências industriais medidas |
| Capacidade adicional | Comparação de throughput, custo/unidade, SLA e makespan | Investimento em aquisição/contratação não está incluído |

### Ferramentas

| Ferramenta | Gráfico | Observações para interpretação |
|---|---|---|
| Diagnóstico operacional | Pontos por posto: fila, espera e utilização | Não demonstra isoladamente um gargalo estrutural |
| Oportunidades | Barras divergentes de variações relativas e índice | Custo negativo significa redução de custo e é favorável; há limite visual para 14 oportunidades e tabela completa |
| Sensibilidade de capacidade | Curva de throughput e ganho marginal versus recursos **inteiros** | Incrementos discretos; não sugere 0,6 máquina |
| Limite de demanda | Curva SLA × multiplicador com **linha da meta** | Ponto de ruptura conforme meta cadastrada; somente ensaios realizados |
| Monte Carlo | Pontos de cada uma das 12 simulações por indicador | Sem probabilidade empírica ou IC industrial calibrado |
| Recuperação | Comparação de alternativas por SLA, throughput, término e custo/unidade | Custo de investimento e restrições físicas ainda não totalmente representados |

### Dashboard de Robustez

Também foi substituído o gráfico de barras com altura relativa arbitrária por observações
do Monte Carlo com escala explícita, quatro seletores de indicadores, detalhes e exportação.

## Interação e rastreabilidade

- Seletor de indicadores em cada gráfico; mudanças não alteram o modelo.
- Seleção de cada ponto/barra com mouse ou teclado, com valores originais em um painel de inspeção.
- Tabela detalhada expansível, mantendo todos os valores devolvidos pelo motor.
- Exportação CSV em português (separador `;`, BOM UTF-8, proteção contra valores de texto interpretados como fórmulas).
- Exportação SVG autônoma, com estilos incorporados para impressão e slides.
- SVG nativo no navegador, sem Recharts, Chart.js ou dependências adicionais.
- Indicadores econômicos com sinal: prejuízo/ganho diferenciados e referenciados ao zero.
- Legendas e ressalvas de metodologia para evitar conclusões além do suporte dos dados.

## Evidências de validação

1. **206 testes Python e 10 subtestes aprovados**. Quatro testes históricos desmarcados porque exigem estruturas de versões anteriores. Três módulos legados com dependência Streamlit não fazem parte da regressão neste ambiente.
2. Em Chromium, executamos cada um dos **12 modos** nas larguras 1280×720, 1366×768 e 1920×1080: **36 execuções de painel**, sem erros JavaScript no fluxo exercitado.
3. Seletor de métrica, seleção de ponto/barra, linha de detalhes e tabela com a mesma quantidade de linhas do JSON: aprovados.
4. Gráfico de economia líquida com valor positivo **e negativo**: verificação de que o negativo está à esquerda do zero, com sinal e cor distintos.
5. Download CSV e SVG: arquivos efetivamente baixados no Chromium; SVG lido e validado como XML.
6. Dashboard de Robustez: consulta a 12 resultados e troca de indicador, sem erros de JavaScript.
7. Smoke test HTTP local: `/`, `engineering_charts.js`, `engineering_charts.css`, dashboard e **12 rotas reais** de ensaios: HTTP 200; projeto e resposta selecionada permanecem inalterados.

**Limites da validação:** no ambiente automático, Chromium não conseguiu navegar diretamente ao servidor localhost; as visualizações foram exercitadas com HTML/CSS/JS originais e respostas do Studio Python real, fornecidas por uma ponte de testes. HTTP foi validado separadamente. Ainda é necessária confirmação da inicialização e dos controles no Windows da equipe.

## Arquivos novos/alterados

- `atelier/web/engineering_charts.js` — camada reutilizável de gráficos SVG e exportações.
- `atelier/web/engineering_charts.css` — estilos do estúdio analítico.
- `atelier/web/app.js` — integração com Ensaios, Ferramentas e Painéis/Robustez.
- `atelier/web/index.html` — carregamento local dos dois novos arquivos.
- `atelier/tests/http_charts_smoke.py` — teste manual das rotas reais.
- Documentação e imagens da entrega, sem alterações nas regras de simulação.

## Advertências sobre o modelo

O Anti-Murphy é uma ferramenta de apoio à decisão com dados sintéticos, não um sistema industrial homologado. Skills individuais, setups dependentes da sequência, buffers finitos e custos completos de aquisição/contratação ainda exigem validação. Os gráficos não constituem comprovação de ótimo global, distribuição de falhas reais ou ganhos financeiros garantidos.
