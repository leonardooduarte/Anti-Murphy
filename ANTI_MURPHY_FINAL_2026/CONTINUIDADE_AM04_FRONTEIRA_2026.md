# Continuidade — AM04-FRONTEIRA-2026.1

Base obrigatória desta entrega: AM10, commit
`97683444f7160f35d86f0bb7b8c96baddb07412a`.
Branch: `correcao-am04-fronteira`.

O complemento AM04 unifica a fronteira bidimensional custo/SLA das telas de
Análise e Otimização. Resolve custos empatados, preserva equivalentes e não
ignora diferenças pequenas de SLA. A revisão tridimensional da decisão
permanece separada e inalterada. As opções dominadas seguem selecionáveis.

Validação: 473 testes aprovados, cinco falhas preexistentes e dez subtestes
aprovados; 16 casos novos do AM04. Testes direcionados: 21 aprovados.
Três experimentos oficiais e navegador nas três resoluções passaram.
Os logs e o relatório identificam os limites dos testes e os casos controlados.
Windows e projetor ainda precisam de validação local.

Somente `atelier/web/app.js` mudou em produção. As etapas AM10, AM09, AM08,
AM12, AM05, AM11 e a base reconstruída AM01–AM06 estão preservadas.
Registros, dados-base, fórmulas, identidade visual e abertura não foram alterados.

Instale o ZIP completo em pasta nova. Para reproduzir a mudança, use o patch
sobre uma extração limpa da AM10 exata; o aplicador confere hashes e cria
uma pasta nova. Guarde versões anteriores e faça backup dos projetos locais.
O commit final pode ser consultado no histórico da branch.

Próxima recomendação: AM17, conforme `STATUS_E_PLANO_FINALIZACAO_2026.md`.
Não iniciar outra correção sem conferir a base atual e reproduzir o problema.
Continuar sem agentes paralelos, mantendo checkpoints e entrega verificável
no GitHub a cada etapa. Não usar os ZIPs antigos para reconstruir novamente.
