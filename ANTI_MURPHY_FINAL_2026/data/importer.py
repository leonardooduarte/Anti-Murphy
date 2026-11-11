from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List, Tuple

import pandas as pd


STATION_COLUMNS = [
    "ID", "Posto", "Máquinas", "Operadores", "Operadores/máquina",
    "Eficiência operador", "Disponibilidade", "Setup (min)",
    "Custo operador/h", "Custo máquina/h",
]
ORDER_COLUMNS = [
    "ID", "Cliente", "Produto", "Quantidade", "Prazo (h)",
    "Multa/h (R$)", "Prioridade", "Roteiro",
]


def _norm_col(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().replace("_", " ").replace("-", " ").split())


def _pick(df: pd.DataFrame, aliases: List[str]) -> str | None:
    by_norm = {_norm_col(c): c for c in df.columns}
    for alias in aliases:
        key = _norm_col(alias)
        if key in by_norm:
            return by_norm[key]
    return None


def canonicalize_stations(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "ID": ["id", "posto id", "codigo", "código", "station id"],
        "Posto": ["posto", "nome", "estacao", "estação", "station"],
        "Máquinas": ["máquinas", "maquinas", "machines", "qtd maquinas", "qtd máquinas"],
        "Operadores": ["operadores", "operators", "funcionarios", "funcionários"],
        "Operadores/máquina": ["operadores/máquina", "operadores/maquina", "operadores por maquina", "operators per machine"],
        "Eficiência operador": ["eficiência operador", "eficiencia operador", "eficiencia", "efficiency"],
        "Disponibilidade": ["disponibilidade", "availability"],
        "Setup (min)": ["setup (min)", "setup", "setup min", "tempo setup"],
        "Custo operador/h": ["custo operador/h", "custo operador", "operator cost", "custo mao de obra"],
        "Custo máquina/h": ["custo máquina/h", "custo maquina/h", "custo maquina", "machine cost"],
    }
    out = pd.DataFrame()
    defaults = {
        "Máquinas": 1, "Operadores": 1, "Operadores/máquina": 1.0,
        "Eficiência operador": 1.0, "Disponibilidade": 1.0, "Setup (min)": 0.0,
        "Custo operador/h": 0.0, "Custo máquina/h": 0.0,
    }
    for target in STATION_COLUMNS:
        src = _pick(df, aliases[target])
        if src is not None:
            out[target] = df[src]
        elif target in defaults:
            out[target] = defaults[target]
        else:
            out[target] = ""
    auto=_pick(df,['automatizada','automated'])
    if auto is not None:out['Automatizada']=df[auto]
    return out


def canonicalize_orders(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "ID": ["id", "op", "ordem", "ordem id", "order id"],
        "Cliente": ["cliente", "customer"],
        "Produto": ["produto", "product", "item"],
        "Quantidade": ["quantidade", "qtd", "qty", "quantity"],
        "Prazo (h)": ["prazo (h)", "prazo", "due date h", "due h"],
        "Multa/h (R$)": ["multa/h (r$)", "multa", "penalty", "penalty h"],
        "Prioridade": ["prioridade", "priority"],
        "Roteiro": ["roteiro", "route", "routing"],
    }
    out = pd.DataFrame()
    defaults = {"Multa/h (R$)": 0.0, "Prioridade": 3}
    for target in ORDER_COLUMNS:
        src = _pick(df, aliases[target])
        if src is not None:
            out[target] = df[src]
        elif target in defaults:
            out[target] = defaults[target]
        else:
            out[target] = ""
    release=_pick(df,['liberação (h)','liberacao (h)','release h','release_h'])
    if release is not None:out['Liberação (h)']=df[release]
    return out


def read_client_workbook(uploaded_file) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, List[str]]:
    """Lê Excel ou CSV e tenta reconhecer Postos e Ordens.

    Excel: procura abas parecidas com 'Postos' e 'Ordens'. Se houver uma única
    aba, tenta inferir pelo conjunto de colunas. CSV: infere o tipo pelas colunas.
    """
    name = str(getattr(uploaded_file, "name", "")).lower()
    raw = uploaded_file.getvalue()
    warnings: List[str] = []
    stations = orders = None

    def classify(df: pd.DataFrame):
        norms = {_norm_col(c) for c in df.columns}
        routeish = any(x in norms for x in ["roteiro", "route", "routing"])
        machineish = any(x in norms for x in ["maquinas", "máquinas", "machines", "operadores", "operators"])
        if routeish:
            return "orders"
        if machineish:
            return "stations"
        return "unknown"

    if name.endswith(".csv"):
        df = pd.read_csv(BytesIO(raw), sep=None, engine="python",decimal=',')
        kind = classify(df)
        if kind == "stations":
            stations = canonicalize_stations(df)
        elif kind == "orders":
            orders = canonicalize_orders(df)
        else:
            warnings.append("Não foi possível inferir se o CSV representa Postos ou Ordens.")
        return stations, orders, warnings

    book = pd.ExcelFile(BytesIO(raw))
    sheets = {str(s).strip().lower(): s for s in book.sheet_names}
    station_sheet = next((orig for low, orig in sheets.items() if low in {"postos", "posto", "stations", "estrutura", "recursos"}), None)
    order_sheet = next((orig for low, orig in sheets.items() if low in {"ordens", "ordem", "orders", "ops", "carteira"}), None)

    if station_sheet:
        stations = canonicalize_stations(pd.read_excel(book, sheet_name=station_sheet))
    if order_sheet:
        orders = canonicalize_orders(pd.read_excel(book, sheet_name=order_sheet))

    if not station_sheet and not order_sheet:
        for sheet in book.sheet_names:
            df = pd.read_excel(book, sheet_name=sheet)
            kind = classify(df)
            if kind == "stations" and stations is None:
                stations = canonicalize_stations(df)
            elif kind == "orders" and orders is None:
                orders = canonicalize_orders(df)

    if stations is None:
        warnings.append("Nenhuma aba de Postos foi reconhecida.")
    if orders is None:
        warnings.append("Nenhuma aba de Ordens foi reconhecida.")
    return stations, orders, warnings


def make_template(stations_df: pd.DataFrame, orders_df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        stations_df.to_excel(writer, sheet_name="Postos", index=False)
        orders_df.to_excel(writer, sheet_name="Ordens", index=False)
        pd.DataFrame([
            {"Campo": "Roteiro", "Como preencher": "POSTO:minutos; POSTO:minutos", "Exemplo": "CORTE:4; CNC:9; MONTAGEM:6"},
            {"Campo": "Disponibilidade", "Como preencher": "Número entre 0,50 e 1,00", "Exemplo": "0,95"},
            {"Campo": "Eficiência operador", "Como preencher": "Número entre 0,55 e 1,20", "Exemplo": "1,00"},
        ]).to_excel(writer, sheet_name="Leia-me", index=False)
    return output.getvalue()
