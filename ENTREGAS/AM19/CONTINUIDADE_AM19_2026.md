# Continuidade — AM19-2026.1 sobre Evolução Visual 02

Base obrigatória: ANTI_MURPHY_EVOLUCAO_VISUAL_02_COMPLETO.zip, SHA-256
4908c612fd98c2b8a8bc4e3e102089ee985e7f97b22ed675cbc4489fe0954bec.
Comparação técnica: AM15, c7e132da54a4f398df13fcdbac6152f41971f922.
Checkpoint visual intacto: 8000e8d33470a6167a6e2c669f80f1d4df0b9de5.
Branch da entrega: correcao-am19-contratos.

As cinco falhas da regressão foram reproduzidas e resolvidas: quatro contratos
obsoletos passaram a verificar comportamento atual; uma prévia ausente foi
restaurada com seu artefato companheiro e gerador reproduzível. Não houve
mudança de motor, fórmulas ou design. O README diferencia entrada principal,
interface histórica Streamlit e exemplos estáticos.

Regressão final: 556 aprovados, zero falhas, dez subtestes aprovados. Três
experimentos oficiais preservados. Chromium verificou o Modo Banca atual,
gráficos/exportações e prévias nas três resoluções. A partida real foi testada
sem pacotes de site. Os logs após extração acompanham o download.

Leia as classificações de cada falha no relatório. Não reinstale asserts
textuais antigos nem remova testes para manter a suíte verde. O mapa de
entradas também identifica runners opcionais não homologados; em especial
browser_offline.js depende do DEMO_NEXUS_V30.html que não estava na base.
A serialização de alguns widgets após runpy limita o AppTest em sequências
longas; cada ferramenta tem cobertura de acesso direto e as áreas têm
navegação contínua. Não confundir essa cobertura com homologação integral
de todos os caminhos históricos.

Instale o ZIP completo em pasta nova. Para reproduzir, aplique o patch sobre
uma extração limpa do ZIP visual recebido, sem executá-la antes. O aplicador
cria outra pasta e confere os hashes. O ZIP-base é preservado no GitHub.
O commit final consta no histórico da branch. Guarde versões e projetos locais.

Próximos passos ainda não executados: revisar as pendências de confiabilidade
documentadas (prioridade opcional, recuperação de arquivos inválidos e
Host/Origin) e validar os componentes visuais novos antes de uma evolução
mais ampla. AM18 é manutenção gradual; AM20/21 são caminhos históricos de uso
a decidir. Planejar auditoria integrada e ensaio no Windows/projetor antes de
declarar uma versão final de banca. A validação nativa segue pendente.

Continuar sem agentes paralelos, uma etapa por branch, com reprodução,
checkpoints, testes, ZIP completo, patch e downloads verificados. Não retornar
ao ZIP original antigo nem reconstruir o projeto.
