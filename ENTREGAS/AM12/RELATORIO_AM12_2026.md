# Anti-Murphy AM12-2026.1

Base AM05 sobre AM11, commit bbc4ff10fd5c6af50e2478c75df41f385e1c4195. Branch correcao-am12-persistencia. Escopo exclusivo AM12.

## Causa e reprodução

Duas instâncias tinham revisões independentes na memória e RLock próprio. A segunda renomeava o projeto salvando também seu modelo antigo, sem verificar o disco. Reprodução na base: quantidade22, primeira salva23, segunda apenas renomeia e disco volta22.

## Correção

atelier/workspace_guard.py implementa bloqueio curto do sistema operacional, por caminho resolvido da pasta, e revisão SHA256 dos bytes de projeto.json, projeto_ativo.json, projeto_confirmado.json e todos os projetos/*.json. O bloqueio usa fcntl.flock em POSIX e msvcrt.locking em Windows, com timeout5s. Há serialização entre threads e reentrância no mesmo thread para inicialização/gravação aninhadas.

Studio inicializa sob o mesmo bloqueio, capturando a revisão antes de ler. Abrir outra instância com estado válido não regrava os arquivos nem invalida quem já estava usando. Antes de salvar modelo/configuração, renomear, resetar ou criar/abrir projeto, a instância confere sua revisão sob bloqueio. Se mudou, recusa a gravação com StudioError e não publica o candidato em memória. A revisão só é atualizada após persistência bem-sucedida. Decisões e arquivamento de experimentos também conferem a revisão, impedindo registrar como atual uma instância cujo modelo ficou antigo.

O aviso orienta fechar e reabrir o programa nesta pasta para carregar os dados recentes. Nenhuma alteração é mesclada ou descartada silenciosamente. A interface usa o aviso de erro existente; HTTP400 preserva o contrato atual.

O arquivo .workspace.lock permanece na pasta. Sua existência não indica bloqueio ativo; o sistema operacional libera o lock ao sair, inclusive após encerramento abrupto. Não o exclua enquanto houver instâncias em execução. Pasta precisa ser gravável. Não se implementou auto-merge, recarga automática ou instância única: duas instâncias podem consultar, mas uma revisão desatualizada não pode gravar.

## Testes

415aprovados,5falhas preexistentes,10subtestes.13testes novos AM12 aprovados. Os testes cobrem reprodução23→22agora bloqueada, abertura sem regravação, todos os caminhos de gravação, dados externos alterados, reinício, pastas independentes/alias, dois processos reais com mesma revisão (exatamenteum grava), lock ocupado e liberação após matar processo.

Navegador HTTPreal: conflito400 com aviso visível e quantidade23preservada. ModoBanca completo registro/relatório passou1280x720,1366x768,1920x1080. Três experimentos oficiais passaram: SLA100/40/100%, custos8076,37/16216,67/10313,00; decisão manutenção12113,00, economia4103,68. Motor, fórmulas, AM11, AM05, CSS, identidade, abertura e dados-base foram preservados.

As5falhas continuam: test_operation_ui::test_evidence_exports_the_current_timed_experiment; dois testes test_restauracao_acesso; test_v31_editorial::test_only_one_root_launcher e ::test_preview_has_no_external_script_dependency. Não foram removidas ou alteradas para mascarar falhas.

## Limites

Validação em Linux/Python3.12/Chromium. Caminho Windows foi implementado com biblioteca padrão, mas não homologado nativamente; conferir no computador da apresentação. Locks são cooperativos e voltados ao disco local: não garantem exclusão para versões antigas do aplicativo, outros editores que ignorem lock ou pastas de rede/sincronização. Modificações externas concluídas antes da conferência são detectadas. Não executar versões antigas simultaneamente na mesma pasta. Não há garantia de transação resistente à queda de energia: rollback/checkpoint AM01 permanecem com suas limitações anteriores.

## Reprodução

python -m pytest tests contract_tests atelier/tests -q
python -m atelier.tests.browser_am12
python -m atelier.tests.validacao_experimentos_banca

Os scripts de navegador exigem Playwright/Chromium. Execute em cópia. Os arquivos modificados são atelier/service.py e o novo atelier/workspace_guard.py; testes novos tests/test_am12_workspace.py e atelier/tests/browser_am12.py. Nenhum outro achado foi corrigido.
