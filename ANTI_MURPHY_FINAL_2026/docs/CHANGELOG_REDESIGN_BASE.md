# Mudanças implementadas na base funcional integrada

1. `app.py`: novo shell central com tarefas persistentes e roteamento para toda a capacidade histórica.
2. `app_classico.py`: modo shell gerenciado; dispensa navegação duplicada; mantém todas as áreas anteriores e seus comandos.
3. `legacy_app.py`: modo shell gerenciado com ferramentas ATLAS; remove menu redundante, mantém análise e formulários originais.
4. `ui/brand_launch.py`: restaura a entrada oficial baseada no símbolo SVG original, com animação não bloqueante e modo movimento reduzido.
5. `ui/unified_shell.css`: hierarquia de títulos, contraste, barra de ferramentas e um sistema visual comum para a navegação.
6. `ui/operation/operation.js`: peças aguardando são renderizadas proporcionalmente à fila real do simulador; estados de processamento e parada distinguem animações.
7. `ui/operation/operation.css`: animações de estado, foco e seleção, com preferência de movimento reduzido.
8. `ui/operation/index.html`: textos operacionais mais objetivos; sem slogans artificiais nas funções revisadas.
9. `INICIAR_ANTI_MURPHY.bat`: um ponto de entrada por projeto; não requer npm.
10. `tests/test_integrated_shell.py`: testes de inventário, integridade do motor, rota, marca e inicialização.

## Preservado

Motor `simulation/engine.py` sem mudanças; demais arquivos de simulação, dados, contratos de replay, Murphy AI, testes e ferramentas históricas. Nenhuma intervenção física externa é executada.

## Não concluído

Uniformização visual completa dos módulos antigos; fechamento de todas as restrições industriais; validação de todas as telas no Windows e testes de uso com participantes externos.
