"""Model editor parsing retained from V29, independent of Streamlit."""
import pandas as pd
import math

def integer(value,label,minimum=0):
    v=float(value)
    if not math.isfinite(v) or v!=int(v) or v<minimum:
        raise ValueError(f"{label}: informe um inteiro maior ou igual a {minimum}.")
    return int(v)

def route_to_text(route):
    return "; ".join(f"{sid}:{float(minutes):g}" for sid, minutes in route)

def parse_route(text: str, valid_stations: set[str]):
    route = []
    raw = str(text or "").strip()
    if not raw:
        raise ValueError("O roteiro não pode ficar vazio.")
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(f"Etapa inválida '{part}'. Use POSTO:minutos.")
        sid, mins = [x.strip() for x in part.split(":", 1)]
        sid = sid.upper()
        if sid not in valid_stations:
            raise ValueError(f"Posto '{sid}' não existe no modelo.")
        try:
            mins = float(mins.replace(",", "."))
        except Exception as exc:
            raise ValueError(f"Tempo inválido em '{part}'.") from exc
        if mins <= 0:
            raise ValueError(f"O tempo de '{sid}' deve ser maior que zero.")
        route.append((sid, mins))
    if not route:
        raise ValueError("O roteiro precisa ter pelo menos uma etapa.")
    return route

def normalize_station_id(value: str) -> str:
    return "_".join(str(value or "").strip().upper().replace("-", " ").split())

def frames_to_model(station_df: pd.DataFrame, order_df: pd.DataFrame):
    new_stations = {}
    for i, r in station_df.iterrows():
        sid = normalize_station_id(r.get("ID", ""))
        nome = str(r.get("Posto", "")).strip()
        if not sid:
            raise ValueError(f"A linha {i+1} da estrutura produtiva precisa de um ID.")
        if not nome:
            raise ValueError(f"O posto {sid} precisa de um nome.")
        if sid in new_stations:
            raise ValueError(f"ID de posto duplicado: {sid}.")
        new_stations[sid] = {
            "nome": nome, "setor": nome,
            "maquinas": integer(r.get("Máquinas",1),f"Máquinas de {sid}",1),
            "operadores": integer(r.get("Operadores",0),f"Operadores de {sid}"),
            "operadores_por_maquina": float(r.get("Operadores/máquina", 1) or 1),
            "eficiencia_operador": float(r.get("Eficiência operador", 1.0) or 1.0),
            "disponibilidade": float(r.get("Disponibilidade", 1.0) or 1.0),
            "custo_operador_h": float(r.get("Custo operador/h", 0.0) or 0.0),
            "custo_maquina_h": float(r.get("Custo máquina/h", 0.0) or 0.0),
            "setup_min": float(r.get("Setup (min)", 0.0) or 0.0), "icone": "◇",
        }
        if 'Automatizada' in r:
            value=r['Automatizada']
            if pd.isna(value):value=False
            text=str(value).strip().lower()
            if text not in {'true','false','sim','não','nao','1','0','1.0','0.0'}:
                raise ValueError(f'Automação de {sid}: use verdadeiro/falso, sim/não ou 1/0.')
            new_stations[sid]['automatizada']=text in {'true','sim','1','1.0'}
        if not 0.50 <= new_stations[sid]["disponibilidade"] <= 1.0:
            raise ValueError(f"Disponibilidade de {sid} deve estar entre 0,50 e 1,00.")
        if not 0.55 <= new_stations[sid]["eficiencia_operador"] <= 1.20:
            raise ValueError(f"Eficiência do operador em {sid} deve estar entre 0,55 e 1,20.")

    valid_ids = set(new_stations)
    new_orders = []
    seen_orders = set()
    for i, r in order_df.iterrows():
        oid = str(r.get("ID", "")).strip().upper()
        if not oid:
            raise ValueError(f"A linha {i+1} da carteira precisa de um ID de ordem.")
        if oid in seen_orders:
            raise ValueError(f"ID de ordem duplicado: {oid}.")
        seen_orders.add(oid)
        cliente = str(r.get("Cliente", "")).strip()
        produto = str(r.get("Produto", "")).strip()
        if not cliente or not produto:
            raise ValueError(f"A ordem {oid} precisa de cliente e produto.")
        new_orders.append({
            "id": oid, "cliente": cliente, "produto": produto,
            "quantidade": integer(r.get("Quantidade",1),f"Quantidade de {oid}",1),
            "prazo_h": float(r.get("Prazo (h)", 1.0) or 1.0),
            "multa_hora": float(r.get("Multa/h (R$)", 0.0) or 0.0),
            "prioridade": integer(r.get("Prioridade",3),f"Prioridade de {oid}",1),
            "route": parse_route(r.get("Roteiro", ""), valid_ids),
        })
        if 'Liberação (h)' in r:new_orders[-1]['release_h']=float(r['Liberação (h)'])
    if not new_orders:
        raise ValueError("A carteira precisa ter pelo menos uma ordem.")
    return new_stations, new_orders
