# Correção do erro TypeScript TS2352 no Windows

## Sintoma
Após `npm install` concluir, `npm run build:component` interrompe em `src/main.tsx:6` por incompatibilidade entre o tipo inferido do JSON importado e `ComparisonBundle`.

## Modificação
Em `frontend/src/main.tsx`, substituímos a conversão direta `bundle as ComparisonBundle` por um valor `unknown`, validado com a função `assertBundle` já existente em `src/types/simulation_contract.ts`.

O import JSON é inferido pelo TypeScript como uma estrutura heterogênea: alguns `station_upserts` só têm CORTE, outros só CNC; o TS interpreta campos ausentes como opcionais `undefined`, causando conflito com `Record<string, StationState>`. Isso não indica, isoladamente, erro no JSON, pois os deltas são parciais por definição.

## Teste executado neste ambiente
O trecho de verificação e estreitamento de tipo foi compilado com TypeScript 5.8.3. **Não foram executados** `npm run build:component`, `npm run build` nem testes visuais da interface neste ambiente por falta de instalação das bibliotecas npm.

## No Windows
No pacote corrigido, abra `PREPARAR_FACTORY_COMMAND.bat` novamente. `npm install` deve reutilizar as dependências instaladas na pasta se você preservar `frontend/node_modules` da versão anterior. Caso extraia o pacote em uma pasta nova, o comando instalará novamente as dependências. Alternativa na pasta `frontend`: `npm run build:component`.

Se surgir outro erro, copie a saída completa do terminal.
