# Anti-Murphy · Edição de revisão crítica para a banca (09/11/2026)

**Esta é a versão integrada refinada a partir do pacote `ANTI_MURPHY_VERSAO_FINAL_CANDIDATA_BANCA_2026.zip` e do vídeo `09_11.mp4`.**

## Abrir no Windows

1. Extraia **todo** o ZIP em uma pasta local independente. Não inicie o programa dentro do ZIP.
2. Dê dois cliques em **`INICIAR_ANTI_MURPHY.bat`**. Não é necessário npm, MiroFish, Zep ou API paga.
3. No navegador, clique em **Modo banca** no topo e avance por **Plano → Falha → Pedidos → Intervenção → Comparação → Evidências**.
4. Na etapa Evidências, escreva uma justificativa real, anote riscos, marque o reconhecimento de limitações e clique em **Registrar decisão**. Após salvar, use **Gerar relatório** ou **Abrir registro**.
5. O relatório é aberto em outra aba. Use **Imprimir ou salvar como PDF**. Se o navegador bloquear a janela, permita pop-ups para a aplicação local.

## O que mudou nesta edição

- Diagnóstico **não automático nem prescritivo** de dominância: verifica custo de decisão, makespan e SLA entre alternativas enumeradas que atendem aos critérios modelados. Se uma alternativa dominar a seleção, o aplicativo indica a concorrente e permite examiná-la. A seleção nunca muda sem um clique do usuário.
- Mensagem especial quando existe **apenas uma** alternativa elegível: evita chamar esse caso de otimização conclusiva.
- **Modo banca encerrando na decisão** em vez de terminar na tabela de alternativas; etapa de registro disposta lado a lado para telas 1280×720, 1366×768 e 1920×1080.
- Confirmação de **registro real no serviço Python**, com acesso imediato à impressão do relatório e ao histórico, inclusive data, justificativa e riscos. Relatório pré-registro é marcado como **análise ainda não registrada**.
- História de decisões guarda o estado do parecer multicritério no momento do registro.
- Valores de custo no relatório são exibidos com **centavos**, sem alterar a contabilidade do motor.
- Aviso contextual quando **12 execuções de Monte Carlo apresentarem SLA idêntico**; ausência de variação não é confirmação de robustez industrial.
- Área do assistente Murphy local começa com uma breve leitura contextual do experimento, sem conexão com IA externa.
- Adições de testes Python, navegador e HTTP, documentação e capturas reais.

## Segurança e preservação

Nenhuma mudança no motor DES `simulation/engine.py`, na seleção original de alternativas `simulation/nexus.py`, nos gráficos de engenharia `atelier/web/engineering_charts.js`, no arquivo `INICIAR_ANTI_MURPHY.bat` nem na logo oficial. Não foi incluído serviço externo ou dependência JavaScript. O novo diagnóstico **não recomenda ação física** e não transforma observações sintéticas em dados industriais.

Leia também `docs/revisao_09_11/RELATORIO_TECNICO.md`, `GUIA_PITCH_CINCO_MINUTOS.md` e `CHECKLIST_WINDOWS_E_PROJETOR.md`.
