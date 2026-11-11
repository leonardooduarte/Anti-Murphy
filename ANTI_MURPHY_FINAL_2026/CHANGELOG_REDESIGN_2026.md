# Changelog — Redesign técnico de apresentação

## Adicionado
- Sistema visual Industrial Workbench (`atelier/web/design_vnext.css`), com novo tratamento do fundo, superfícies, hierarquia de textos e estados.
- Planta de produção com desenho de equipamentos mais visível, leitura do estado, IDs de unidades em fila e representação de progresso temporal.
- Visualização detalhada da máquina selecionada no inspetor.
- Foco em posto, acesso ao cronograma e tela ampliada para apresentações.
- Comparação A/B de estado de posto e filas no mesmo instante; barras de progresso por ordem para ambos os futuros.
- Histograma de SLA a partir dos dados do ensaio Monte Carlo.
- Teste visual reproduzível com fixture derivada do motor Python e documentação de verificação.

## Corrigido
- Fila SVG deixa de ter seu conteúdo substituído a cada quadro sem mudanças reais na fila.
- Inspetor interativo deixa de ser recriado a cada atualização de animação; seus controles ficam mais estáveis.
- As animações da fábrica ficam pausadas quando o replay está pausado.
- Reorganização do painel da simulação mantendo a linha do tempo junto à fábrica.

## Preservado
- Animação da marca oficial e a navegação de sete áreas.
- Modelagem, projetos, experimentos, laboratório, ferramentas avançadas, assistência local, relatórios e registros.
- Código original do motor e do serviço de simulação, sem alterações de parâmetros matemáticos.
- Ferramentas clássicas ATLAS/NEXUS no diretório separado.

## Não concluído
- Migração completa dos módulos clássicos para a interface principal.
- Novo modelo físico de transporte, restrições de skills/buffer/setup e integração generativa externa.
- Homologação visual e de inicialização no Windows do usuário.
