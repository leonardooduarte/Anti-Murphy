# Versão atual: INT02-2026.1 sobre INT01

[Aplicativo completo](ENTREGAS/INT02/ANTI_MURPHY_INT02_COMPLETO_2026.zip) · [Patch](ENTREGAS/INT02/ANTI_MURPHY_PATCH_INT02_2026.zip) · [Relatório](ENTREGAS/INT02/RELATORIO_INT02_2026.md) · [Continuidade](ENTREGAS/INT02/CONTINUIDADE_INT02_2026.md).

Auditoria por pedido usa horários precisos, identifica dados legados e não apresenta valores indisponíveis como no prazo. A tabela do relatório conserva os sinais e os tempos curtos. Evolução visual preservada. 706 testes aprovados, zero falhas, dez subtestes; três experimentos e navegador nas três resoluções passaram. ZIP e patch conferem 697 arquivos. Extraia em pasta nova e execute INICIAR_ANTI_MURPHY.bat. Windows/projetor pendentes de validação nativa.

---
# Versão atual: INT01-2026.1 sobre AM22

[Aplicativo completo](ENTREGAS/INT01/ANTI_MURPHY_INT01_COMPLETO_2026.zip) · [Patch](ENTREGAS/INT01/ANTI_MURPHY_PATCH_INT01_2026.zip) · [Relatório](ENTREGAS/INT01/RELATORIO_INT01_2026.md) · [Continuidade](ENTREGAS/INT01/CONTINUIDADE_INT01_2026.md).

Importação JSON preserva EDD/SPT/FIFO explícita; ausência mantém a regra atual com aviso; inválidos são recusados antes de aplicar o modelo. Evolução visual preservada. 682 testes aprovados, zero falhas, dez subtestes; três experimentos e navegador nas três resoluções passaram. ZIP e patch conferem 669 arquivos. Extraia em pasta nova e execute INICIAR_ANTI_MURPHY.bat. Windows/projetor pendentes de validação nativa.

---
# Versão atual: AM22-2026.1 sobre RECUPERACAO/PRIORIDADE/AM19

[Auditoria integrada da AM22](AUDITORIAS/INTEGRADA_AM22/RELATORIO_AUDITORIA_INTEGRADA_AM22.md) · [Evidências para baixar](AUDITORIAS/INTEGRADA_AM22/AUDITORIA_INTEGRADA_AM22_2026.zip). Auditoria sem alteração de código; quatro pendências confirmadas, com plano de correções.

[Aplicativo completo](ENTREGAS/AM22/ANTI_MURPHY_AM22_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM22/ANTI_MURPHY_PATCH_AM22_2026.zip) · [Relatório](ENTREGAS/AM22/RELATORIO_AM22_2026.md) · [Continuidade](ENTREGAS/AM22/CONTINUIDADE_AM22_2026.md).

GET e POST exigem Host local na porta ativa; Origin presente deve corresponder à origem HTTP local. Clientes locais sem Origin continuam permitidos. Evolução visual preservada. 664 testes aprovados, zero falhas, dez subtestes; três experimentos e navegador nas três resoluções passaram. ZIP e patch conferem 650 arquivos. Extraia em pasta nova e execute INICIAR_ANTI_MURPHY.bat. Windows/projetor pendentes de validação nativa.

---
# Versão atual: RECUPERACAO-2026.1 sobre PRIORIDADE/AM19

[Aplicativo completo](ENTREGAS/RECUPERACAO/ANTI_MURPHY_RECUPERACAO_COMPLETO_2026.zip) · [Patch](ENTREGAS/RECUPERACAO/ANTI_MURPHY_PATCH_RECUPERACAO_2026.zip) · [Relatório](ENTREGAS/RECUPERACAO/RELATORIO_RECUPERACAO_2026.md) · [Continuidade](ENTREGAS/RECUPERACAO/CONTINUIDADE_RECUPERACAO_2026.md).

Abertura com arquivos inválidos recupera uma configuração válida, informa o usuário e preserva originais sem gravação automática. Evolução visual preservada. 597 testes aprovados, zero falhas, dez subtestes; três experimentos e navegador nas três resoluções passaram. ZIP e patch conferem 631 arquivos. Extraia em pasta nova e execute INICIAR_ANTI_MURPHY.bat. Windows/projetor pendentes de validação nativa.

---
# Versão atual: PRIORIDADE-2026.1 sobre AM19

[Aplicativo completo](ENTREGAS/PRIORIDADE/ANTI_MURPHY_PRIORIDADE_COMPLETO_2026.zip) · [Patch](ENTREGAS/PRIORIDADE/ANTI_MURPHY_PATCH_PRIORIDADE_2026.zip) · [Relatório](ENTREGAS/PRIORIDADE/RELATORIO_PRIORIDADE_2026.md) · [Continuidade](ENTREGAS/PRIORIDADE/CONTINUIDADE_PRIORIDADE_2026.md).

Ausência ou campo vazio omite prioridade; inteiros explícitos são preservados; valores inválidos são recusados antes do envio. Evolução visual preservada. 577 testes aprovados, zero falhas, dez subtestes; três experimentos e navegador nas três resoluções passaram. ZIP e patch conferem 617 arquivos. Extraia em pasta nova e execute INICIAR_ANTI_MURPHY.bat. Windows/projetor pendentes de validação nativa.

---
# Versão atual: AM19-2026.1 sobre Evolução Visual 02

Base recebida: `ANTI_MURPHY_EVOLUCAO_VISUAL_02_COMPLETO.zip`, preservando AM15 e as correções anteriores. A evolução visual do pacote permanece byte a byte igual; esta etapa trata testes e distribuição.

[Baixar aplicativo completo](ENTREGAS/AM19/ANTI_MURPHY_AM19_COMPLETO_2026.zip) · [Patch sobre o ZIP visual](ENTREGAS/AM19/ANTI_MURPHY_PATCH_AM19_2026.zip) · [Relatório](ENTREGAS/AM19/RELATORIO_AM19_2026.md) · [Continuidade](ENTREGAS/AM19/CONTINUIDADE_AM19_2026.md) · [Entradas do programa](ENTREGAS/AM19/ENTRADAS_AM19_2026.md) · [ZIP-base recebido](ENTREGAS/AM19/ANTI_MURPHY_EVOLUCAO_VISUAL_02_COMPLETO.zip).

Abra o ZIP e clique em **Download raw file**. Extraia em pasta nova e execute `ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat`. Preserve a instalação anterior e seus projetos. As prévias HTML restauradas são exemplos estáticos; o aplicativo atual é aberto pelo BAT/start.py.

As cinco falhas anteriores foram resolvidas sem apagar ou desativar testes. Regressão: **556 aprovados, zero falhas e dez subtestes aprovados**. Três experimentos oficiais e navegador nas três resoluções passaram. Partida real sem pacotes de site verificada. ZIP e patch reproduzem 602 arquivos; 19 testes direcionados passaram novamente após extração.

Windows/BAT/projetor aguardam homologação nativa. Um runner Node opcional antigo depende de `DEMO_NEXUS_V30.html`, ausente da base; não foi homologado. Leia as limitações do harness e da cobertura histórica no relatório. As versões e branches anteriores permanecem preservadas.

---

Histórico das versões anteriores:

# Versão atual AM15 sobre AM14

[Aplicativo completo](ENTREGAS/AM15/ANTI_MURPHY_AM15_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM15/ANTI_MURPHY_PATCH_AM15_2026.zip) · [Relatório](ENTREGAS/AM15/RELATORIO_AM15_2026.md).

Fábrica tem enquadramento para mais postos, foco por posto e leitura textual com nomes e estados. Extraia em pasta nova. Windows/projetor pendentes.

---
# Versão atual AM14 sobre AM13

[Aplicativo completo](ENTREGAS/AM14/ANTI_MURPHY_AM14_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM14/ANTI_MURPHY_PATCH_AM14_2026.zip) · [Relatório](ENTREGAS/AM14/RELATORIO_AM14_2026.md).

Registros exibem o projeto de origem e distinguem nome arquivado de nome atual do cadastro. Extraia em pasta nova. Windows/projetor pendentes.

---
# Versão atual AM13 sobre AM16

[Aplicativo completo](ENTREGAS/AM13/ANTI_MURPHY_AM13_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM13/ANTI_MURPHY_PATCH_AM13_2026.zip) · [Relatório](ENTREGAS/AM13/RELATORIO_AM13_2026.md).

Murphy identifica pedidos completos e explica o critério de escolha do motor. Extraia em pasta nova. Windows/projetor pendentes.

---
# Versão atual AM16 sobre AM17

[Aplicativo completo](ENTREGAS/AM16/ANTI_MURPHY_AM16_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM16/ANTI_MURPHY_PATCH_AM16_2026.zip) · [Relatório](ENTREGAS/AM16/RELATORIO_AM16_2026.md).

Monte Carlo impede submissões duplicadas na mesma página e sinaliza execução entre telas. Extraia em pasta nova. Windows/projetor pendentes.

---
# Versão atual AM07 sobre AM17

[Aplicativo completo](ENTREGAS/AM07/ANTI_MURPHY_AM07_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM07/ANTI_MURPHY_PATCH_AM07_2026.zip) · [Relatório](ENTREGAS/AM07/RELATORIO_AM07_2026.md).

Modo reduzido agora preserva processamento agregado exato e informa detalhes omitidos. Extraia em pasta nova. Windows/projetor pendentes.

---
# Versão atual: AM17-2026.1

Continuação do complemento AM04 sobre AM10. Preserva AM09/AM08/AM12/AM05/AM11 e a base reconstruída AM01–AM06.

[Baixar aplicativo completo](ENTREGAS/AM17/ANTI_MURPHY_AM17_COMPLETO_2026.zip) · [Patch sobre AM04/AM10](ENTREGAS/AM17/ANTI_MURPHY_PATCH_AM17_2026.zip) · [Relatório](ENTREGAS/AM17/RELATORIO_AM17_2026.md) · [Continuidade](ENTREGAS/AM17/CONTINUIDADE_AM17_2026.md) · [Próximas etapas](ENTREGAS/AM17/STATUS_AM17_E_PROXIMAS_ETAPAS_2026.md).

Abra o ZIP e clique em **Download raw file**. Extraia em pasta nova e execute `ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat`. Preserve instalações anteriores e faça backup dos seus projetos.

O editor mostra a dimensão do modelo antes de aplicar. Pedidos acima dos limites locais são recusados antes do cálculo: 25.000 operações por cenário e 250.000 por análise, contando os cenários. Projetos grandes salvos abrem para edição sem simular nem regravar automaticamente. O replay usa índices e o diário de eventos é consultado sem reordenar tudo a cada atualização.

Benchmark específico de 3.600 consultas com 12.000 operações: mediana 790,47→10,58 ms após aquecimento, com 48,86 ms de construção inicial do índice. Não é ganho de velocidade global da aplicação. Fórmulas, indicadores e resultados oficiais foram preservados.

510 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados; 37 casos novos do AM17. Três experimentos oficiais e navegador nas três resoluções passaram. ZIP e patch reproduzem os mesmos 506 arquivos; após extração, 94 testes direcionados e a verificação HTTP passaram. Windows/projetor ainda exigem aceite local. As versões anteriores permanecem preservadas.

---

Histórico das versões anteriores:

# Versão atual: complemento AM04 sobre AM10

AM04-FRONTEIRA-2026.1 preserva AM10/AM09/AM08/AM12/AM05/AM11 e a base reconstruída AM01–AM06. O número AM04 identifica o achado complementado; esta é a continuação da AM10.

[Baixar aplicativo completo](ENTREGAS/AM04_FRONTEIRA/ANTI_MURPHY_AM04_FRONTEIRA_COMPLETO_2026.zip) · [Patch sobre AM10](ENTREGAS/AM04_FRONTEIRA/ANTI_MURPHY_PATCH_AM04_FRONTEIRA_2026.zip) · [Relatório](ENTREGAS/AM04_FRONTEIRA/RELATORIO_AM04_FRONTEIRA_2026.md) · [Continuidade](ENTREGAS/AM04_FRONTEIRA/CONTINUIDADE_AM04_FRONTEIRA_2026.md) · [Plano para finalizar](ENTREGAS/AM04_FRONTEIRA/STATUS_E_PLANO_FINALIZACAO_2026.md).

Abra o ZIP e clique em **Download raw file**. Extraia em pasta nova e execute `ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat`. Preserve instalações e dados anteriores.

As telas de Análise e Otimização usam a mesma fronteira custo/SLA: custos empatados, equivalentes e diferenças pequenas são tratados consistentemente. Todas as alternativas continuam consultáveis e selecionáveis. A revisão tridimensional da decisão permanece inalterada; não há garantia de ótimo global.

473 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados; 16 casos novos do AM04. Três experimentos oficiais, navegador com casos controlados e fluxos reais do Modo Banca passaram nas três resoluções. ZIP e patch reproduzem os mesmos 475 arquivos; após extração, 57 testes direcionados e a verificação HTTP passaram. Windows e projetor ainda exigem validação local. Versões anteriores preservadas.

---

Histórico das versões anteriores:

# Versão atual: AM10-2026.1 sobre AM09/AM08/AM12/AM05/AM11

[Baixar aplicativo completo](ENTREGAS/AM10/ANTI_MURPHY_AM10_COMPLETO_2026.zip) · [Patch sobre AM09](ENTREGAS/AM10/ANTI_MURPHY_PATCH_AM10_2026.zip) · [Relatório](ENTREGAS/AM10/RELATORIO_AM10_2026.md) · [Continuidade](ENTREGAS/AM10/CONTINUIDADE_AM10_2026.md).

Abra o ZIP e clique em **Download raw file**. Extraia em pasta nova e execute `ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat`. Preserve instalações e dados anteriores.

A busca de capacidade inclui combinações de máquina e operador no mesmo posto, ambas as orientações entre postos e quantidades dentro dos limites totais. A abrangência e a quantidade de candidatos aparecem na interface e nas exportações. A busca cobre até duas combinações posto/recurso e não comprova ótimo global.

457 testes aprovados, cinco falhas preexistentes e dez subtestes aprovados; 17 testes novos do AM10. Três experimentos oficiais e navegador nas três resoluções passaram. ZIP e patch reproduzem os mesmos 451 arquivos. Após extração, 36 testes direcionados e a verificação HTTP passaram. Windows e projetor aguardam validação local. As versões anteriores permanecem preservadas.

---

Histórico de versões anteriores:

# Versão atual: AM09-2026.1 sobre AM08/AM12/AM05/AM11

[Aplicativo completo](ENTREGAS/AM09/ANTI_MURPHY_AM09_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM09/ANTI_MURPHY_PATCH_AM09_2026.zip) · [Relatório](ENTREGAS/AM09/RELATORIO_AM09_2026.md) · [Continuidade](ENTREGAS/AM09/CONTINUIDADE_AM09_2026.md).

Abra o ZIP e clique Download raw file. Extraia em pasta nova e execute ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat. Guarde versões e dados anteriores.

Stress/MonteCarlo preservam tentativas inviáveis com motivos e não calculam custo/duração como zero. Médias/percentis usam somente viáveis e identificam amostra. Resiliência usa todas as tentativas.440testes aprovados,5falhas históricas,10subtestes;12novosAM09. Três experimentos oficiais e navegador nas3resoluções passaram. Windows/projetor aguardam aceite local. Nenhuma outra correção foi implementada.

---

Histórico de versões anteriores:

# Versão atual: AM08-2026.1 sobre AM12/AM05/AM11

[Aplicativo completo](ENTREGAS/AM08/ANTI_MURPHY_AM08_COMPLETO_2026.zip) · [Patch](ENTREGAS/AM08/ANTI_MURPHY_PATCH_AM08_2026.zip) · [Relatório](ENTREGAS/AM08/RELATORIO_AM08_2026.md) · [Continuidade](ENTREGAS/AM08/CONTINUIDADE_AM08_2026.md).

No GitHub, abra o ZIP e clique Download raw file. Extraia em pasta nova e execute ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat. Guarde instalações e dados anteriores.

Comparação arquivada agora separa custo do cenário, investimento, custo da decisão e economia líquida. Arquivos antigos não foram regravados e valores ausentes não viram zero.428 testes aprovados,5falhas históricas,10subtestes;13novosAM08 aprovados. Três experimentos oficiais e navegador nas3resoluções passaram. Windows/projetor pendem de aceite local. Entregas anteriores permanecem preservadas.

---

Histórico das versões anteriores:

# Versão atual desta branch: AM12-2026.1

AM12 concluído sobre AM05+AM11. [Baixar aplicativo completo](ENTREGAS/AM12/ANTI_MURPHY_AM12_COMPLETO_2026.zip), [patch](ENTREGAS/AM12/ANTI_MURPHY_PATCH_AM12_2026.zip), [relatório](ENTREGAS/AM12/RELATORIO_AM12_2026.md). Abra o ZIP e clique Download raw file no GitHub. Extraia em pasta nova e execute ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat.

415 testes aprovados, cinco falhas históricas, dez subtestes.13 novosAM12 aprovados. Gravações de instâncias desatualizadas são bloqueadas com aviso para reabrir o programa. Caminho Windows implementado, homologação nativa pendente. Arquivos de entregas anteriores permanecem preservados. O texto abaixo é o histórico da versão AM05.

---

# Anti-Murphy — AM05-2026.1 sobre AM11

Nesta branch, AM05 foi concluído sobre a versão AM11 preservada no commit4cc48a4. Foram corrigidas identificação de resultados desatualizados, dependências por ferramenta, histórico e exportações. Motor/fórmulas/identidade visual foram preservados.

## Baixar

- Aplicativo completo: [ANTI_MURPHY_AM05_COMPLETO_2026.zip](ENTREGAS/AM05/ANTI_MURPHY_AM05_COMPLETO_2026.zip). Abra o arquivo e use Download raw file no GitHub.
- Patch sobreAM11: [ANTI_MURPHY_PATCH_AM05_2026.zip](ENTREGAS/AM05/ANTI_MURPHY_PATCH_AM05_2026.zip).
- [Relatório técnico](ENTREGAS/AM05/RELATORIO_AM05_2026.md), [continuidade](ENTREGAS/AM05/CONTINUIDADE_AM05_2026.md) e [hashes](ENTREGAS/AM05/SHA256SUMS.txt).

Extraia em pasta NOVA e execute ANTI_MURPHY_FINAL_2026/INICIAR_ANTI_MURPHY.bat no Windows comPython3.10+. Guarde a versão anterior. Os projetos deste ZIP são os arquivados na base; faça backup dos seus dados antes de considerar migração.

Code → Download ZIP também baixa esta branch inteira, incluindo entregas históricas. Para uso direto, prefira o ZIP AM05 acima. Os ZIPs AM11, o patch anterior e a recuperação integral continuam em ENTREGAS sem alterações.

## Verificação

402testes aprovados,5falhas históricas,10subtestes.50novosAM05 aprovados.3experimentos oficiais e9grupos de aceitaçãoAM05 por resolução passaram em1280x720/1366x768/1920x1080. ModoBanca e gráficos passaram. Patch reproduz385arquivos do pacote completo;131testesAM05+AM11 passaram novamente após extração. Verificação detalhada em ENTREGAS/AM05.

Resultados antigos permanecem acessíveis nesta página. Recarregar/fechar descarta o histórico temporário; exporte para guardar. Metas/controles específicos sinalizam desatualização sem recálculo automático. Windows/projetor não homologados nesta sessão. Outros achados da auditoria permanecem pendentes.
