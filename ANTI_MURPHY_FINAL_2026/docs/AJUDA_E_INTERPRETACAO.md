# Ajuda e interpretação — Especificação implementada

## Recursos implementados

- **Ajuda contextual:** botão no cabeçalho e link em cada seção. Define o propósito, quando usar, interpretação e próximo passo. Nada é enviado a serviços externos.
- **Percurso guiado opcional:** seis etapas ligadas à interface: modelo, simulação, replay, análise, laboratório, decisões. O usuário pode encerrar quando quiser; ao terminar, retorna à seção de origem.
- **Ajuda de KPI:** botões `?` junto aos indicadores explicam significado, unidade e interpretação. Não substituem auditoria da implementação do cálculo.
- **Rastreio por pedido:** botão **Por que este resultado?** no posto selecionado. Examina operações, horários de chegada/início e conclusão do pedido a partir do replay. Indica o maior tempo de espera observado; não atribui causalidade total sem evidência contrafactual.
- **Interpretação das alternativas:** comparação entre atrasos e custos derivados de `metrics` e `order_impacts`, com ressalvas sobre investimentos e restrições.
- **Navegação temporal por eventos:** início, falha, solicitação/efetivação da resposta, fim previsto da parada, fim do horizonte, conforme campos do replay.
- **Relatório técnico:** abre uma página imprimível com dados da operação nominal, falha, resposta, efeitos por pedido e limites metodológicos. Os dados vêm da simulação ativa.

## Proveniência e restrições

- A fonte de tempos, operações e intervenções é o serviço `atelier/service.py` e o motor de eventos discretos original `simulation/engine.py`.
- As máquinas exibem **atividade visual**, não movimento físico medido. As linhas entre postos são relações de precedência, não transportes temporizados. Por isso, as conexões não simulam material trafegando com velocidade inventada.
- Custos de cenários incluem operação e penalidades. A comparação de custo líquido deve utilizar `decision_cost`, `investment` e `savings` da alternativa, com hipóteses explícitas.
- Não há confirmação completa de habilidades individuais, setups dependentes de sequência e capacidade finita de buffers.
- O painel não utiliza modelos generativos nem faz chamadas à internet.

## Arquivos alterados

`atelier/web/index.html`, `atelier/web/app.js` e `atelier/web/styles.css`. O contrato Pydantic e o motor não foram reescritos nesta edição.
