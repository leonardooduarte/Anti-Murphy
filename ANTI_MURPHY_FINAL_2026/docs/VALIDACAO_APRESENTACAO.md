# Verificação da edição de apresentação — 05/11/2026

## Testes concluídos neste ambiente

- **109 testes Python aprovados e 10 subtestes**: pacote `atelier/tests`, `contract_tests`, decisão, replay, resposta temporal, prioridades, modelo e workspace.
- **Sintaxe JavaScript** verificada por `node --check atelier/web/app.js`.
- **Compilação sintática Python** validada por `compileall`.
- **Testes de componentes no Chromium** em 1366×768 e 1920×1080, usando HTML/CSS/JS reais e estado calculado pelo `Studio` em uma ponte de teste. Sem erros de JavaScript nos percursos exercitados.
- **Ajuda contextual** verificada nas sete áreas: simulação, modelo, análise, laboratório, ferramentas, decisões e registros.
- **Percurso guiado** de seis etapas: navegação, destaque, conclusão e retorno à seção de origem.
- **Rastreio de pedido**: dados de operação, prazo, conclusão e maior espera apresentados.
- **Marcos de eventos**: clique na parada levou exatamente a 04:00 h no cenário padrão; cenário A/B gerou marcos específicos.
- **Relatório técnico**: nova aba com três cenários, cinco pedidos e ressalvas de viabilidade.
- **HTTP local**: `/`, `/app.js`, `/styles.css`, `/api/state`, `/api/projects`, `/api/experiments` e `/api/assistant` retornaram HTTP 200 no servidor Python real.

## O que esta validação não comprova

- O navegador automatizado deste ambiente bloqueou navegação direta a `127.0.0.1` por política de segurança. Por isso a UI foi testada com resposta do serviço real injetada no Chromium; rotas HTTP foram testadas separadamente. **A execução integral da UI servida pelo navegador não foi homologada neste ambiente**.
- **Windows:** ainda depende de execução no computador de quem receber a pasta.
- **Streamlit clássico:** não foi testado porque o pacote não está instalado no ambiente. O código permanece preservado na pasta de ferramentas históricas.
- **Industria:** cenários sintéticos e intervenções hipotéticas; habilidades específicas, setups e buffers finitos ainda dependem de modelagem e validação. Nenhuma alegação de 60 FPS ou otimização global.

As capturas anexadas são do código real executado em Chromium com dados calculados pelo motor por meio da ponte de teste, não imagens conceituais.
