# Continuidade — AM17-2026.1

Base: `3e4bf47892be46cc3640ab2baee34a44faed4248`, complemento AM04 sobre AM10.
Branch: `correcao-am17-desempenho`.

AM17 acrescenta limites explícitos de operações, contagem dos cenários e
réplicas, cartão de dimensão do modelo, abertura de projetos grandes para
edição sem simular, índices do replay e geração limitada de oportunidades.
Não altera fórmulas do DES nem dos indicadores econômicos.

Política local: 25.000 operações por cenário e 250.000 por análise. São limites
de recursos, não uma garantia de tempo/memória para toda configuração. Perfis
de ensaio usam limites superiores e podem contar um cache nominal ainda vazio.
A função `profile` deve acompanhar mudanças de cenários e réplicas das ferramentas.

Validação: 510 aprovados, cinco falhas preexistentes e dez subtestes aprovados;
37 casos novos. Três experimentos oficiais e navegador nas três resoluções
passaram. Benchmark de consultas de replay: mediana 790,47→10,58 ms após
aquecimento; construção do índice 48,86 ms uma vez. Não é ganho global de FPS.
Os testes e logs após extração acompanham os arquivos da entrega.

Preservados AM04, AM10, AM09, AM08, AM12, AM05, AM11 e a base reconstruída
AM01–AM06. Dados-base e arquivos históricos não foram regravados. Instale
o ZIP completo em pasta nova e guarde versões anteriores e seus projetos.
O patch exige a AM04/AM10 exata e cria uma pasta nova após conferir hashes.

Ao abrir um projeto salvo acima do limite, a edição permanece acessível e
não há simulação ou regravação automática. Reduza o volume e aplique para
voltar a calcular. Ao trocar para projeto grande nesse modo, o ponteiro
persistido só é atualizado quando houver gravação explícita.

Próxima etapa recomendada: AM07, indicação correta do replay com detalhes
omitidos; depois AM16, submissões duplicadas. AM15 é o próximo ganho visual
relevante: legibilidade e enquadramento da fábrica, preservando identidade.
Também restam rastreabilidade AM13/14, cinco contratos históricos AM19 e
os complementos listados no plano. Um defeito anterior de prioridade ausente
em modelos opcionais foi documentado e continua pendente.

Seguir sem agentes paralelos, uma etapa por branch, checkpoints no GitHub,
reprodução, regressão, três experimentos, navegador e entrega verificável.
Não reconstruir a partir dos ZIPs antigos. Windows/projetor seguem pendentes.
