# ANTI-MURPHY — PRÉ-FINAL VALIDADA 2026

## Iniciar no Windows

1. **Extraia o ZIP inteiro em uma pasta nova** (não misture arquivos com outras versões).
2. Dê dois cliques em **`INICIAR_ANTI_MURPHY.bat`**. É necessário Python 3.10 ou mais recente.
3. Mantenha a janela preta do servidor aberta. O navegador padrão deve abrir automaticamente no endereço local. Caso não abra, leia a URL na janela.
4. Para fechar o programa, pressione `Ctrl+C` na janela do servidor.

O aplicativo principal é local e **não precisa de npm, React ou API de IA** para abrir. Os dados padrão são um exemplo **sintético**, não telemetria industrial.

## O que testar primeiro

- **Simulação:** pause por volta de 10 h na parada da CNC, veja a fila e os pedidos destacados como atrasados; compare os dois cenários usando o divisor A/B.
- **Análise:** confira a composição `operação + penalidades + investimento = custo da decisão`. Logo abaixo, use a sequência de investigação: **Incidente → Efeito sem resposta → Intervenção**. Os elementos abrem o replay correspondente.
- **Murphy AI:** pergunte **"Qual o gargalo da operação e quais pedidos estão em risco?"**. A resposta diferencia o gargalo identificado pelo motor do posto com maior espera média, apresentando os pedidos atrasados registrados.
- **Decisões:** escreva uma justificativa. O editor mostra o mínimo de caracteres, rejeita notas insuficientes e permite recuperar a decisão no histórico após salvar.
- **Painéis:** acesse Operação, Desempenho, Cenários, Otimização e Robustez sem abrir outro software.
- **Modelo:** use o editor de roteiros por etapas, e só aplique mudanças quando quiser recalcular.

## O que NÃO fazer

- Não considerar uma alternativa automaticamente segura ou viável para a fábrica real. Habilidades de operadores, setups por sequência e capacidades finitas de buffers ainda precisam de verificação.
- Não interpretar investimento *modelado* igual a zero como custo real necessariamente zero.
- Não tratar as animações como medidas de velocidade ou transporte real: o mapa é uma visualização 2.5D **lógica**.

## Compatibilidade e limites

O código central do motor, o serviço da aplicação, o servidor HTTP local, os arquivos de abertura e a identidade visual foram preservados. As ferramentas históricas ATLAS/NEXUS continuam na pasta `FERRAMENTAS_HISTORICAS`, separadas do ambiente principal e com possíveis dependências extras.

Esta versão passou nos testes automatizados, mas a **homologação final do inicializador e do desempenho no seu Windows** ainda precisa ser feita no seu computador.

Consulte `docs/RELATORIO_PRE_FINAL_VALIDADA.md` para detalhes da implementação e dos testes.
