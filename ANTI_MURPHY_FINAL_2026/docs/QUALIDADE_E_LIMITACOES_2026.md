# Qualidade, testes e limitações — 03/11/2026

## Execução automatizada

- `python -m pytest -q atelier/tests contract_tests`: **53 aprovados + 10 subtestes aprovados**.
- `python -m pytest -q atelier/tests contract_tests tests --ignore=tests/test_nexus_ui.py --ignore=tests/test_nexus_v30.py --ignore=tests/test_operation_ui.py`: **186 aprovados, 4 falhas**. As quatro falhas são expectativas da arquitetura antiga: nomes/strings específicos do `app.py`, inicializador apontando para `tools/start_nexus.py` e o antigo arquivo estático `PREVIEW_OPERACAO.html`, que não é mais ponto de entrada. Foram mantidas e reportadas, não ocultadas ou alteradas artificialmente para passar.
- Três módulos de teste que exigem Streamlit foram excluídos da execução integral porque Streamlit não está disponível neste ambiente.
- `node --check atelier/web/app.js`: aprovado.
- Chromium headless com servidor Python real em `127.0.0.1`: simulação, replay, programação por posto, seleção de ordem, criação e reabertura de projetos, dois arquivos de experimentos, comparação histórica, evidências de decisão e análise avançada. **Sem exceções de JavaScript** nos fluxos executados; verificou-se ausência de overflow horizontal a 1920px. O navegador de testes utilizou uma ponte para o serviço HTTP real devido à restrição de navegação localhost do ambiente; não equivale a homologação completa do navegador no Windows.

## O que não foi testado / comprovado

- Inicialização `INICIAR_ANTI_MURPHY.bat` e abertura automática do navegador no Windows real.
- Todas as configurações possíveis de modelo; executamos cenários sintéticos de referência e casos selecionados.
- Testes completos do aplicativo legado Streamlit.
- Desempenho de renderização em GPUs integradas Windows, FPS e consumo de memória sob cargas industriais reais.
- Efetividade das decisões em uma planta física; o produto não é um gêmeo digital conectado nem sistema de controle industrial.
- Restrições físicas individuais de operador, buffers finitos e setups dependentes de sequência integralmente validadas.

## Comunicação correta de resultados

Os valores indicados para custo, atraso e cumprimento de prazo correspondem ao modelo e às premissas da simulação. Não equivalem a promessa de economia líquida. A visualização de cenários é uma análise exploratória, e a viabilidade física precisa ser verificada antes de aplicar decisões reais.

## Próximos testes prioritários

1. Windows: executar do zero por `INICIAR_ANTI_MURPHY.bat`, fechar e reabrir sem configuração manual.
2. UX: convidar pessoa não desenvolvedora para configurar, simular, comparar, registrar e recuperar projeto sem instruções.
3. Confiabilidade: testar prioridade de pedidos, custos e alterações de recursos em cenários com poucos elementos e contas manuais.
4. Integrar gradualmente telas históricas com **paridade funcional comprovada**, sem reduzir a profundidade do software.
5. Perfilar animações e dados no hardware de destino antes de impor WebGL/PixiJS.
