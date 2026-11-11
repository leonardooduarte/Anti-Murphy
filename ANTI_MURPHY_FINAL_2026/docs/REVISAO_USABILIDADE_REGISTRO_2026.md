# Registro de decisão — texto livre com conferência contextual

## O que mudou nesta revisão

A interface preserva a autonomia de quem toma a decisão. O texto produzido automaticamente é **somente uma sugestão editável**. Não há frase obrigatória, lista de palavras ou estilo exigido pelo Modo Banca. A regra mínima é uma justificativa breve (12 caracteres) e o reconhecimento explícito de que se trata de um estudo sintético sem homologação física.

O campo **Riscos e verificações pendentes** é opcional; a aplicação incentiva o preenchimento, mas não impede o registro em caso de ausência ou repetição de conteúdo. A avaliação textual não é apresentada como uma certificação técnica da redação.

Se a justificativa contém valores explícitos em `R$` não encontrados entre os indicadores da execução atual, a interface avisa qual quantia não corresponde ao experimento; **não altera, apaga ou substitui o texto do usuário**. Um usuário que esteja discutindo informação externa ou outro cenário pode confirmar que deseja mantê-la **como não conferida**. Essa confirmação é preservada no registro, e o relatório não apresenta essa quantia como resultado validado pelo motor.

Sem quantias em `R$`, não é necessário inserir números no texto, nem usar o botão de sugestão.

## Salvaguardas mantidas

- Não é permitido salvar uma justificativa vazia ou sem contexto mínimo.
- O identificador do experimento é checado para impedir que um registro de uma execução anterior seja vinculado silenciosamente a uma execução nova.
- A intervenção deve fazer parte das opções elegíveis reconhecidas pelo motor.
- Limitações físicas da simulação precisam ser reconhecidas antes do registro.
- Os custos calculados, o aviso de montantes não conferidos e o vínculo ao experimento são preservados na ficha de decisão.

## Verificações executadas

- Testes Python `atelier/tests/test_record_integrity.py` e `atelier/tests/test_decision_quality.py`: oito aprovados.
- Teste de navegador do Modo Banca em **1280 × 720, 1366 × 768 e 1920 × 1080**: aprovado para texto livre, alerta de quantia antiga, confirmação de valor não conferido, sugestões opcionais e fluxo até o relatório.
- Testes HTTP de distribuição e três experimentos de engenharia: aprovados.

## Limitações

A conferência monetária reconhece apenas valores explicitamente escritos no formato `R$ ...`, e não determina automaticamente se a interpretação econômica da frase está correta. Um usuário pode optar por manter um valor incorreto como não conferido; nesse caso, o registro ressalva a divergência, mas não valida o conteúdo. As demonstrações no Windows e no projetor precisam ser repetidas no equipamento da equipe.
