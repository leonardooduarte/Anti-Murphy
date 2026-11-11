# Anti-Murphy — reconstrução das correções AM-01 a AM-06

**Data:** 10/11/2026  
**Base:** `ANTI_MURPHY_ACABAMENTO_FINAL_BANCA_2026.zip` (última versão original disponível no histórico da conversa).  
**Status:** reconstrução independente dos seis achados da auditoria. **Não** é o ZIP nem o código original criado pelo Codex, que não foi recuperado.

## Instalação segura no Windows

1. **Faça uma cópia** da pasta atual do Anti-Murphy. Nunca extraia por cima da única versão existente.
2. Extraia este ZIP **inteiro** para uma pasta nova. Não execute o `.bat` dentro do arquivo compactado.
3. Abra `INICIAR_ANTI_MURPHY.bat` dentro da pasta extraída.
4. Confirme que a operação nominal, falha CNC e resposta selecionada carregam normalmente. O aplicativo principal usa servidor HTTP local e motor Python, sem serviços pagos nem dependências de IA.
5. Se você tiver projetos e decisões próprios em uma pasta `workspace` de outra instalação, **copie essa pasta para um backup separado antes** de considerar migrá-la. A pasta `workspace` neste ZIP vem do original arquivado, não do trabalho que aconteceu somente no Codex.

## Mudanças

- **AM-01 — modelo e persistência:** edição, troca de projetos, reset e cálculo usam estado candidato. Antes de publicar, verificam configuração, pedido prioritário, despacho, cálculo, replay e gravação. Novo `atelier/persistence.py` prepara quatro arquivos JSON e tenta desfazer gravações incompletas após erros de I/O. Um `projeto_confirmado.json` permite recuperar a última configuração confirmada quando o projeto ativo não abre. A validação de operabilidade ao salvar não impede que o simulador represente *cenários inviáveis* no motor.
- **AM-02 — EDD/SPT:** o motor agrupa chegadas, conclusões e mudanças de recursos de mesmo instante antes de iniciar operações novas. FIFO mantém chegada/ID/unidade como desempate; não há preempção. O fluxo de eventos e as fórmulas econômicas não foram reescritos.
- **AM-03 — decisões:** o estado e a seleção só recebem o registro após confirmação da gravação; uma falha de escrita não cria confirmação visual falsa. O replay é preparado antes de salvar.
- **AM-04 — classificação:** dashboards, gráfico de alternativas e fronteira usam os três indicadores independentes `feasible`, `within_budget`, `meets_sla`; alternativas abaixo da meta continuam selecionáveis. Dominância não é apresentada como comprovação de atendimento à meta.
- **AM-05 — validade de ensaios:** o backend inclui assinatura, projeto, execução, parâmetros e hora em resultados do Laboratório e de ferramentas avançadas. O Laboratório guarda até 25 análises na memória da sessão do navegador, permite consulta de resultados anteriores e apresenta **Atual / Desatualizado / Histórico**. CSV e SVG incluem identificação da origem. Não há recálculo automático. Dados do histórico temporário desaparecem ao encerrar a sessão.
- **AM-06 — recuperação temporal:** `recovery_plan` usa `TimedAction`, com reforço de pessoal/máquina ou EDD somente no instante solicitado (`início da falha + espera configurada`). Resultados preservam operações anteriores; a interface apresenta início/efetivação da intervenção. Investimentos externos em máquinas/pessoal **não estão precificados**, mesmo após a correção.

## Verificações realmente executadas nesta reconstrução

- **234 testes aprovados**, **10 subtestes aprovados** na suíte disponível após excluir quatro testes históricos que verificam uma organização anterior (e três módulos Streamlit indisponíveis nesta instalação).
- **20 testes específicos novos** para AM-01 a AM-06 (incluídos nos 234), cobrindo rollback em falha simulada, decisão sem gravação, pedido renomeado, EDD/SPT, classificação, assinatura e intervenção posterior à falha.
- **Três experimentos oficiais da banca aprovados:** `python -m atelier.tests.validacao_experimentos_banca`.
- **Smoke HTTP real aprovado:** arquivos estáticos, estado, painéis, auditoria, Laboratório e Recuperação respondendo com HTTP 200.
- **Sintaxe Python e JavaScript verificada** com `compileall` e `node --check`.
- **Não foi executada validação visual real em três resoluções:** o navegador automatizado do ambiente desta reconstrução bloqueou o acesso ao localhost por política administrativa. **Também não foi homologado o `.bat` no Windows**, nem o projetor.
- A suíte geral completa, sem excluir testes, **não passou** neste ambiente: três módulos antigos exigem Streamlit não instalado, e quatro testes textuais verificam os arquivos de uma arquitetura anterior. Os quatro defeitos históricos não foram alterados.

## Indicadores de referência do cenário sintético

| Cenário | Makespan | SLA | Custo do cenário |
|---|---:|---:|---:|
| Nominal | 16,90 h | 100% | R$ 8.076,37 |
| Falha CNC (8 h) | 24,58 h | 40% | R$ 16.216,67 |
| Manutenção expressa | 21,58 h | 100% | R$ 10.313,00 |
| Recuperação +1 operador CNC **a partir de t=6h** | 19,97 h | 60% | Consulte ferramenta |

A decisão de manutenção expressa acrescenta investimento modelado de R$ 1.800,00 ao custo do cenário (R$ 10.313,00), resultando em **R$ 12.113,00**. Diferença modelada frente à falha: **R$ 4.103,67**. Não confundir economia modelada com caixa comprovadamente economizado.

## Limitações restantes

Esta reconstrução não é cópia byte a byte das seis correções do Codex. Os demais achados da auditoria (AM-07 a AM-22, incluindo AM-11) **não foram corrigidos**. A gravação em vários arquivos possui rollback de melhor esforço e checkpoint, mas não equivale a transação resistente a queda de energia; não foi implementado bloqueio/controle de revisões para múltiplas instâncias. Modelos e custos continuam sintéticos, com restrições industriais não calibradas. Faça testes de aceitação na sua máquina antes da banca.

## Arquivos centrais modificados

`atelier/service.py`, `atelier/persistence.py` (novo), `simulation/validation.py`, `simulation/engine.py`, `simulation/advanced.py`, `atelier/web/app.js`, `atelier/web/engineering_charts.js`, `atelier/tests/test_am01_am06_reconstruido.py` (novo).

As cores oficiais, abertura, logotipo, folhas CSS e recursos de mídia foram mantidos do pacote de origem.
