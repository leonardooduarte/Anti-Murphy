# Continuidade — AM10-2026.1

Base: AM09, commit `a56c407f35bd11b3091791c5e561ea82fa90812d`.
Branch desta etapa: `correcao-am10-capacidade`.
Preservadas as etapas AM09, AM08, AM12, AM05, AM11 e a base reconstruída AM01–AM06.

AM10 corrige a enumeração de capacidade: uma ou duas combinações posto/recurso,
respeitando limites totais de operadores e máquinas adicionais. Inclui máquina
e operador no mesmo posto, ambas as orientações entre postos e partições das
quantidades. A interface, o CSV e o SVG declaram a abrangência da busca.
Não há demonstração de ótimo global. Mais de 10.000 candidatos são recusados
explicitamente antes da simulação. A análise é estrutural desde o início da
operação; intervenções temporais continuam em suas ferramentas existentes.

Validação: 457 testes aprovados, cinco falhas preexistentes e dez subtestes
aprovados. Os 17 testes novos do AM10 passaram. Três experimentos oficiais
e navegador em 1280×720, 1366×768 e 1920×1080 passaram. Após extração,
36 testes direcionados e a verificação HTTP passaram novamente.
Windows e projetor ainda exigem validação local.

O ZIP contém 451 arquivos. O patch verifica os hashes da base e cria uma pasta
nova, preservando a origem. Use o ZIP completo para instalar diretamente;
o patch é uma alternativa para reproduzir a mudança sobre a AM09 exata.
Guarde esta versão, os arquivos de entrega e seus projetos locais como backup.
O commit final pode ser consultado no histórico da branch.

Próxima etapa recomendada, ainda não implementada: revisar o empate na
fronteira visual do AM04. Depois, retomar os achados de robustez AM17/AM07/AM16
e rastreabilidade AM13/AM14, conferindo cada definição na auditoria antes de
iniciar. Manter uma correção por etapa, com reprodução, testes e entrega.
