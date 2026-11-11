# Factory Command Studio — Primeira revisão visual integrada

- Criada página inicial de decisão com layout novo, marca oficial, piso industrial 2.5D e cinco tipos visuais de máquina.
- Implantado replay JS compatível com o estado Pydantic v1.1.0, sob dados V30.2 gerados no Python.
- Acrescentados seletor A/B, comparador wipe, tempo, filas, pedidos e indicadores econômicos.
- Adicionado formulário para recalcular falha e alternativa hipotética no motor.
- Acrescentada análise local determinística e registro JSONL de decisão (sem aplicação física).
- Implementado `ABRIR_ANTI_MURPHY.vbs` e fallback BAT; **sem npm na execução normal**.
- Preservado workspace operacional V30.2 e todo o código original das versões anteriores dentro do pacote.
- Criado preview HTML offline para verificar a experiência sem Streamlit nem Python.
- Auditoria mínima de regressão: 81 testes pytest + 16 pares de equivalência de replay + 5 ações de navegador.
- Limitações industriais e impossibilidade de testar Streamlit/Windows documentadas explicitamente.
