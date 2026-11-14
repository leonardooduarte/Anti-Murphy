# Ensaio real — Windows e projetor

Versão alvo: INT04, aplicativo ac852d8. Este roteiro ainda NÃO foi executado no seu Windows/projetor. Os arquivos de homologação começam como NÃO EXECUTADO; só marque resultados depois de observar o comportamento real.

## Preparação e diagnóstico

1. Baixe o ZIP completo INT04 e extraia em uma pasta nova. Preserve a instalação anterior; não substitua sua pasta de projetos. Use primeiro a cópia com dados sintéticos para o ensaio. O ZIP da verificação contém roteiro e ferramentas, não outra versão do aplicativo.
2. Extraia este pacote de verificação inteiro em outra pasta, mantendo juntos VERIFICAR_WINDOWS.bat, VERIFICAR_AMBIENTE.py, MODELO_CICLO_CURTO.json e base-manifest.json. É necessário Python 3.10 ou superior. O aplicativo principal não exige instalar dependências extras.
3. Arraste a pasta ANTI_MURPHY_FINAL_2026 recém-extraída sobre VERIFICAR_WINDOWS.bat. Alternativa no terminal, dentro da pasta da verificação: `py -3 VERIFICAR_AMBIENTE.py --app "C:\caminho\ANTI_MURPHY_FINAL_2026"`.
4. Guarde o resultado_ambiente_*.json gerado junto ao verificador. Ele identifica o sistema/Python, confere os 748 arquivos da versão, cria uma cópia temporária sem seus projetos, inicia o servidor, verifica importação/arquivo inválido/reabertura/precisão de ciclo curto e executa os três experimentos oficiais. Não instala pacotes nem altera seu aplicativo. Se houver diferenças nos arquivos, registra os caminhos e encerra antes do ensaio automático.
5. O verificador inicia start.py diretamente; ele NÃO comprova que o BAT original, a interface visual ou o projetor funcionam. `windows_automatizado_aprovado` só é preenchido ao rodar no Windows, mas não é homologação visual. A validação desta ferramenta aqui foi no Linux e permanece identificada assim.

## Ensaio manual na pasta nova

Registre a observação e evidência na ficha FICHA_WINDOWS_PROJETOR.csv. Use APROVADO/FALHOU/NÃO EXECUTADO/NÃO APLICÁVEL, sem preencher por suposição.

| ID | Ação | Critério observado |
| --- | --- | --- |
| W01 | Anote Windows, versão do Python, navegador, resolução e escala do Windows | Configuração real identificada na ficha |
| W02 | Execute INICIAR_ANTI_MURPHY.bat do aplicativo, por duplo clique | Console sem erro, endereço local e navegador abertos; introdução/abertura visível, com opção de avançar |
| W03 | Explore as oito áreas pelo menu e pelos botões Início/Voltar | Acesso livre, sem travamento, corte de controles ou erro visível |
| W04 | No exemplo sintético, confira operação nominal, falha sem resposta e resposta | SLA 100/40/100%; decisão com manutenção expressa, custo total R$12.113,00 e diferença modelada R$4.103,68 nas condições oficiais |
| W05 | Modifique um pedido e aplique; feche e reabra o programa na mesma pasta | Alteração persistida e resultados coerentes; registre o que mudou |
| W06 | Crie/duplique um projeto; use SPT, exporte modelo, altere para EDD e importe o arquivo | Regra SPT recuperada; confira regra e valores antes/depois, inclusive ao reabrir |
| W07 | Guarde dois experimentos e compare | Custos do cenário, investimento, custo da decisão e economia separados; não confundir economia com fluxo de caixa garantido |
| W08 | Na cópia de ensaio, feche o app e crie workspace\experimentos\invalid.json com conteúdo [] (use “Todos os arquivos” para evitar .txt) | Ao reabrir, aplicativo inicia; biblioteca mostra aviso com esse nome; registros válidos podem ser comparados e outro experimento pode ser guardado; arquivo inválido não é apagado |
| W09 | Em outro projeto da cópia de ensaio, importe MODELO_CICLO_CURTO.json e configure o início da parada para depois de 1 h; consulte a referência Plano original da auditoria | Auditoria por pedido usa conclusão positiva e folga negativa; JSON/relatório não transforma os horários por pedido em zero. Se não houver resposta recomendada, você pode examinar conscientemente Não intervir antes de gerar o relatório. Mantenha o exemplo oficial em outro projeto |
| W10 | Abra Laboratório/Ferramentas; execute um ensaio, altere parâmetro relevante e veja o resultado anterior | Resultado desatualizado/histórico identificado; acesso anterior preservado, sem recálculo contínuo |
| W11 | Exporte um gráfico/CSV e amplie o gráfico | Arquivo abre com origem/estado coerentes; eixos e textos legíveis; nada é apresentado como dado industrial medido |
| W12 | Selecione alternativa e escreva justificativa; registre e reabra o histórico | Confirmação após gravação, projeto/execução corretos, justificativa e componentes econômicos preservados |
| W13 | Gere relatório; teste impressão/salvar PDF e abra o arquivo salvo | Alternativa e justificativa corretas; tabelas legíveis, sem cortes; PDF abre depois de fechar o aplicativo |
| W14 | Ative Modo Banca e percorra as seis etapas | Narrativa, falha, pedido, resposta, A/B e registro coerentes; sair do modo mantém navegação livre |
| W15 | Teste fonte/contraste em análise e decisões nas resoluções disponíveis | Rótulos legíveis, sem sobreposição; meta medida no Linux: 14 px e 6,68:1 nos rótulos corrigidos. Não presumir leitura a distância |
| W16 | Se usar modelo com muitos postos, teste 9/16/50 e foque o último posto; volte à planta inteira | Planta e legenda sem corte após estabilizar; repita a ida/volta. Caso haja corte, capture imediatamente e após um segundo, anotando resolução/escala e posto |
| P01 | Conecte o projetor real e anote resolução, escala, modo duplicar/estender e distância do público | Condições reais registradas |
| P02 | Mostre mapa, foco de posto, painel, alternativa e relatório a partir do lugar da banca | Pessoas conseguem ler rótulos, valores e distinguir situações sem depender apenas de cor |
| P03 | Execute o roteiro completo de apresentação com cronômetro | Tempo real registrado; transições e arquivos acessíveis sem improvisar etapas |
| P04 | Feche tudo e reabra pelo BAT, já com o projetor conectado | Mesmo projeto e registros recuperados; apresentação pronta nas condições reais |

Não é necessário instalar a ferramenta em sua versão de trabalho nem criar arquivo inválido em projetos reais. O caso W08 é exclusivo da pasta nova de ensaio; preserve a cópia de trabalho. Não altere o ZIP ou o código para fazer um resultado de homologação parecer aprovado.

## O que enviar para concluir a homologação

- resultado_ambiente_*.json criado no Windows.
- FICHA_WINDOWS_PROJETOR.csv preenchida com os testes realmente executados.
- Capturas/PDF referentes a falhas ou dificuldades de leitura; para o mapa, detalhe instante e após estabilizar.
- Windows/navegador/Python, resolução, escala e condições do projetor.

Se alguma etapa falhar, preserve a pasta e a mensagem exata para reprodução. A existência dos testes Linux aprovados não substitui os resultados acima. Uma única apresentação de demonstração também não homologa todos os caminhos históricos nem calibração industrial.
