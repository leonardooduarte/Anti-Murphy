"""Dados-base do Anti-Murphy 2.0.

O cenário foi desenhado para demonstrar balanceamento de linha, restrições de
mão de obra, paralelização de postos e comparação econômica de cenários.
"""

STATIONS_BASE = {
    "CORTE": {
        "nome": "Corte Laser",
        "setor": "Preparação",
        "maquinas": 1,
        "operadores": 1,
        "operadores_por_maquina": 1,
        "eficiencia_operador": 0.95,
        "disponibilidade": 0.97,
        "custo_operador_h": 25.0,
        "custo_maquina_h": 42.0,
        "setup_min": 12.0,
        "icone": "✦",
    },
    "CNC": {
        "nome": "Usinagem CNC",
        "setor": "Usinagem",
        "maquinas": 2,
        "operadores": 1,
        "operadores_por_maquina": 1,
        "eficiencia_operador": 0.92,
        "disponibilidade": 0.94,
        "custo_operador_h": 29.0,
        "custo_maquina_h": 68.0,
        "setup_min": 18.0,
        "icone": "◈",
    },
    "SOLDA": {
        "nome": "Soldagem",
        "setor": "Caldeiraria",
        "maquinas": 2,
        "operadores": 1,
        "operadores_por_maquina": 1,
        "eficiencia_operador": 0.94,
        "disponibilidade": 0.96,
        "custo_operador_h": 28.0,
        "custo_maquina_h": 36.0,
        "setup_min": 15.0,
        "icone": "✺",
    },
    "PINTURA": {
        "nome": "Pintura & Cura",
        "setor": "Acabamento",
        "maquinas": 1,
        "operadores": 1,
        "operadores_por_maquina": 1,
        "eficiencia_operador": 0.96,
        "disponibilidade": 0.98,
        "custo_operador_h": 24.0,
        "custo_maquina_h": 31.0,
        "setup_min": 10.0,
        "icone": "⬡",
    },
    "MONTAGEM": {
        "nome": "Montagem Final",
        "setor": "Montagem",
        "maquinas": 3,
        "operadores": 2,
        "operadores_por_maquina": 1,
        "eficiencia_operador": 0.93,
        "disponibilidade": 0.99,
        "custo_operador_h": 23.0,
        "custo_maquina_h": 15.0,
        "setup_min": 8.0,
        "icone": "◇",
    },
}

ORDERS_BASE = [
    {
        "id": "OP-101",
        "cliente": "AutoPeças Alvorada",
        "produto": "Eixo Transmissor",
        "quantidade": 22,
        "prazo_h": 13.0,
        "multa_hora": 420.0,
        "prioridade": 2,
        "route": [
            ("CORTE", 4.0), ("CNC", 9.0), ("PINTURA", 5.0), ("MONTAGEM", 6.0)
        ],
    },
    {
        "id": "OP-102",
        "cliente": "Tratores do Brasil",
        "produto": "Braço Hidráulico",
        "quantidade": 18,
        "prazo_h": 15.0,
        "multa_hora": 650.0,
        "prioridade": 1,
        "route": [
            ("CORTE", 5.0), ("CNC", 8.0), ("SOLDA", 11.0), ("PINTURA", 6.0), ("MONTAGEM", 7.0)
        ],
    },
    {
        "id": "OP-103",
        "cliente": "AgroTech Máquinas",
        "produto": "Mancal Flangeado",
        "quantidade": 26,
        "prazo_h": 18.0,
        "multa_hora": 290.0,
        "prioridade": 3,
        "route": [
            ("CORTE", 3.0), ("CNC", 10.0), ("SOLDA", 7.0), ("MONTAGEM", 5.0)
        ],
    },
    {
        "id": "OP-104",
        "cliente": "Mineração Vale do Sul",
        "produto": "Quadro Reforçado",
        "quantidade": 16,
        "prazo_h": 20.0,
        "multa_hora": 560.0,
        "prioridade": 2,
        "route": [
            ("CORTE", 6.0), ("SOLDA", 13.0), ("PINTURA", 8.0), ("MONTAGEM", 9.0)
        ],
    },
    {
        "id": "OP-105",
        "cliente": "Sistemas Robóticos SA",
        "produto": "Base Automatizada",
        "quantidade": 14,
        "prazo_h": 22.0,
        "multa_hora": 900.0,
        "prioridade": 1,
        "route": [
            ("CORTE", 4.0), ("CNC", 12.0), ("PINTURA", 5.0), ("MONTAGEM", 12.0)
        ],
    },
]

DEFAULT_RULE = "EDD"
DEFAULT_SEED = 42
DEFAULT_DEMAND_MULTIPLIER = 1.0
