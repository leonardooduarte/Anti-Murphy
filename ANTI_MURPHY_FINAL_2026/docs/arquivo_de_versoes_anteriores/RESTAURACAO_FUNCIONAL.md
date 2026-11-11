# Anti-Murphy — recuperação funcional (V31.1)

## Motivo
A V31 abria somente a visualização experimental, com barra lateral
recolhida. Isso escondia o fluxo V30.2 e os módulos de análise histórica,
causando impressão de remoção de ferramentas. O código estava presente,
mas a organização deixou o produto menos útil.

## Alterações
- `app.py`: padrão é Operação e decisões; navegação visível com acesso direto
  às ferramentas ATLAS e mapa experimental.
- `app_classico.py`: removido caminho quebrado de rerun para Factory Command;
  botão de ferramentas anteriores aponta para a área correspondente.
- `legacy_app.py`: configurações de página centralizadas em `app.py`;
  retorno ao workspace corrigido.
- `tools/start_nexus.py`: localiza porta livre, espera servidor iniciar e
  abre navegador padrão automaticamente. Reutiliza `.venv` quando possível.

## O que está preservado
As implementações de V30.2 e ATLAS, inclusive War Room, Murphy AI,
Scenario Studio, Decision Evidence, Optimization Hub, Stress Lab,
Opportunity Engine, Goal Seek/Mission Control, portfólio e modelo.
O mapa da produção V31 também permanece na área experimental.

## O que NÃO é afirmado
- Nenhuma funcionalidade do motor foi reescrita.
- Não foi realizada uma reformulação visual completa.
- Não há homologação em Windows, porque o ambiente de desenvolvimento atual
  não executa Streamlit. O browser automático é implementado mas precisa
  ser validado no computador de destino.
- Ainda não há verificação industrial completa de skills, setups e buffers.
