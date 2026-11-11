# Testes e limitações desta revisão

## Execução realizada no ambiente Linux

- `python -m pytest -q atelier/tests contract_tests tests --ignore=tests/test_nexus_ui.py --ignore=tests/test_nexus_v30.py --ignore=tests/test_operation_ui.py`: **197 testes aprovados e 10 subtestes; 4 falhas**. Estas quatro falhas verificam caminhos, nomes e conteúdo de telas anteriores (`test_restauracao_acesso.py` e `test_v31_editorial.py`); não são falhas de cálculo registradas nessa rodada. Mantidas como não resolvidas para revisão dos testes históricos.
- Os três módulos Streamlit citados acima **não foram coletados**, pois `streamlit` não está instalado neste ambiente.
- `node --check atelier/web/app.js`: aprovado.
- Teste do servidor HTTP local: `GET /` e `GET /release_quality.css` retornaram 200.
- Chromium headless com interface real e ponte de teste para o serviço HTTP Python: **1280×720, 1366×768, 1920×1080**, sem exceções JavaScript observadas nos fluxos exercitados: Início, Análise, Painéis → Desempenho, Laboratório, Ferramentas, Decisões, pergunta ao Murphy, ação contextual de navegação, regresso ao Início, replay e seleção de registro de operação. As capturas estão em `docs/capturas_qualidade/`.
- Testes novos em `atelier/tests/test_final_quality.py`: auditoria da soma de componentes de custo e economia, não alteração do experimento por consulta ao Murphy, explicação de pedidos, aviso sobre restrições não modeladas e coerência dos dashboards.

## O que esta verificação NÃO comprova

- Não comprova desempenho em FPS, estabilidade de sessões longas, instalação em Windows, nem uso com dados industriais reais.
- A ponte utilizada nos testes de Chromium encaminha solicitações ao serviço HTTP real, mas não substitui homologação ponta a ponta no navegador do usuário.
- A aprovação dos testes do motor não significa que todas as restrições industriais estejam representadas.

## Revisão sugerida no Windows antes da apresentação

1. Extraia em pasta independente; execute `INICIAR_ANTI_MURPHY.bat`; confira se o navegador abre automaticamente.
2. Em **Simulação**, teste Play/Pause, incidente, pedidos, marcos temporais e **Registros da operação**.
3. Em **Análise**, selecione uma intervenção; confira operação + multas + investimento = custo da decisão e que a diferença líquida usa a falha sem resposta.
4. Em **Painéis → Desempenho**, confira que as mesmas parcelas aparecem e que a seleção atualiza os dados.
5. Em **Decisões**, pergunte ao Murphy sobre custos, OP-102 e viabilidade; teste o retorno pelo botão contextual.
6. Registre uma decisão com justificativa e confirme sua presença em **Registros**.
7. Verifique a animação inicial da marca e o encerramento pelo terminal.
