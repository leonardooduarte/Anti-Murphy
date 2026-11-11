# Revisão de produto e engenharia — Modo Banca Premium

**Base preservada:** `ANTI_MURPHY_BANCA_REVISADA_09_11_2026.zip`.
**Motivação:** vídeos `09_11_a.mp4` (navegação normal) e `09_11_abanca.mp4` (demonstração orientada).

## Problemas observados e correções

| Achado dos vídeos | Implementação realizada | Evidência |
|---|---|---|
| O Plano já revelava custo e SLA da resposta | Função de evidências faseada: Plano mostra apenas dados nominais; Falha mostra somente momento, posto e duração; Pedidos revela atrasos; resposta/custos aparecem depois | Capturas `01_plano_*`, `02_falha_*`, `03_pedidos_*` |
| O divisor A/B cortava equipamentos em metades difíceis de interpretar | No Modo Banca, os dois replays ocupam painéis independentes com foco ampliado no posto afetado e opção de layout inteiro | Capturas `05_comparacao_foco_*` e `05b_comparacao_layout_*` |
| Faltava explicitar por que o cenário B aparentava reagir melhor | Estado e unidades em fila no posto afetado em A e B, no mesmo instante. Todos os números são derivados de `machineState` e dos dados do replay | Painel comparativo sob o mapa |
| Registro podia aceitar texto genérico, sem reflexão técnica | Sugestão editável fundamentada em métricas reais e alerta de qualidade de texto no Modo Banca; exige descrição de riscos e confirmação de premissas | Captura `06b_justificativa_*`; teste com texto repetitivo rejeitado |
| A demonstração não abria o relatório no encerramento | Depois do registro confirmado, botão **Abrir relatório final**, preservando histórico e acesso separado; fallback de download HTML para bloqueio de pop-up | Capturas `07_registro_*`; teste de relatório e fallback |
| Legibilidade limitada em 720p | Layout condensado, botão de salvar visível, opção de tela cheia e contraste dos cenários | Captura `06_decisao_1280.png` |

## Escopo técnico e rastreabilidade

- **Alterados:** `atelier/web/app.js`, `atelier/web/index.html`, `atelier/web/apresentacao_premium.css`, QA do navegador e documentação.
- **Não alterados:** motor `simulation/engine.py` e módulos de cálculo, serviço `atelier/service.py`, revisão multicritério `atelier/decision_quality.py`, gráficos técnicos `atelier/web/engineering_charts.js`, inicializador do Windows e identidade visual.
- **Comportamento preservado:** funcionalidades normais de simulação, seleção de respostas, comparação A/B com divisor no modo convencional, Ensaios, Ferramentas, painéis, auditoria, registros, histórico, projetos e exportações.
- **Regra de validação do texto:** a aplicação mantém o mínimo histórico de 12 caracteres no modo convencional. O texto é livre nos dois modos; exige-se apenas justificativa mínima de 12 caracteres e reconhecimento das limitações do estudo. O campo de riscos e as sugestões do sistema são opcionais. Quantias em R$ divergentes são sinalizadas e podem ser mantidas como não conferidas mediante ciência explícita. **Isso não certifica a interpretação técnica da redação.**
- **Relatório:** o próprio serviço continua responsável pelo registro persistente. O botão final somente abre o documento do experimento registrado, sem acionar equipamentos.

## Resultado de engenharia preservado (cenário padrão, dados sintéticos)

O teste repetido em Python confirma operação nominal com **100% de SLA**, falha sem resposta com **40% de SLA** e manutenção expressa com **100% de SLA**, dentro dos parâmetros padrão. Custo total estimado da falha sem resposta **R$ 16.216,67** e custo de decisão da manutenção expressa **R$ 12.113,00**, incluindo investimento modelado; diferença **R$ 4.103,68**. São resultados **do modelo**, não valores de caixa medidos numa fábrica.

No ensaio de capacidade, acrescentar máquinas CNC sem corrigir a restrição correspondente não aumenta o throughput (permanece em aproximadamente **5,682 unidades/h**, nas condições testadas). Isso não significa que capacidade nunca melhora a operação; é válido apenas para o modelo e os parâmetros deste ensaio.

## Limitações que a banca pode questionar

1. **O sistema não é uma otimização industrial universal:** enumera respostas e compara indicadores sob restrições modeladas; não prova um ótimo global.
2. **A dominância de custo, makespan e SLA é condicional:** outros riscos, recursos físicos e aspectos de qualidade não computados podem alterar a decisão.
3. **O software não monitora uma planta em tempo real:** esta é uma representação de um cenário sintético por eventos discretos.
4. **Economia modelada não é economia de caixa comprovada:** custos fixos de capacidade ao longo do horizonte não se tornam necessariamente evitáveis.
5. **O Modo Banca não inventa eventos:** a mudança de máquina parada para processando em cada cenário é obtida do replay do motor, num instante comum.
6. **O texto de justificativa é um rascunho:** deve ser revisado, personalizado e aprovado pelo responsável antes do registro.

**Conclusão:** o refinamento melhora a transmissão do resultado técnico, especialmente para uma apresentação de até cinco minutos, sem ampliar alegações de capacidade industrial.


Nota AM-11: diferença econômica calculada com valores não arredondados; o resultado final é arredondado para apresentação. A diferença de R$ 0,01 frente à edição AM-06 é esperada.
