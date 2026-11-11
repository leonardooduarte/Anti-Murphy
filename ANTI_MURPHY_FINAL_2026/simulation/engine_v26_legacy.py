from __future__ import annotations

import math
import random
from collections import defaultdict
from copy import deepcopy
from typing import Dict, Any, List, Tuple

import simpy

from simulation.factory import ScenarioConfig


class SimulationResult(dict):
    """Dict com acesso por atributo para facilitar uso na interface."""
    __getattr__ = dict.__getitem__


def _priority(order: Dict[str, Any], cycle_min: float, rule: str, unit_index: int) -> Tuple[float, float, int]:
    if rule == "SPT":
        return (cycle_min, order["prazo_h"], unit_index)
    if rule == "FIFO":
        return (order.get("release_h", 0.0), unit_index, order.get("prioridade", 9))
    # EDD default: prazo mais curto, depois prioridade comercial, depois unidade
    return (order["prazo_h"], order.get("prioridade", 9), unit_index)


def _overlap_delay(start: float, duration: float, outage_start: float, outage_end: float) -> float:
    if outage_end <= outage_start:
        return 0.0
    end = start + duration
    overlap = max(0.0, min(end, outage_end) - max(start, outage_start))
    # Se a operação entra durante a pane, espera também até o fim da janela.
    if outage_start <= start < outage_end:
        return max(overlap, outage_end - start)
    return overlap


def run_simulation(config: ScenarioConfig) -> SimulationResult:
    rng = random.Random(config.seed)
    env = simpy.Environment()

    stations = deepcopy(config.stations)
    absent = config.absent_workers or {}

    machine_resources = {}
    worker_resources = {}
    station_stats = defaultdict(lambda: {
        "busy_machine_h": 0.0,
        "busy_worker_h": 0.0,
        "wait_h": 0.0,
        "operations": 0,
        "units": 0,
    })

    for sid, s in stations.items():
        machines = max(1, int(s["maquinas"]))
        available_workers = max(0, int(s["operadores"]) - int(absent.get(sid, 0)))
        worker_cap = max(1, available_workers)  # recurso existe; ausência total é tratada com penalidade extrema
        machine_resources[sid] = simpy.PriorityResource(env, capacity=machines)
        worker_resources[sid] = simpy.PriorityResource(env, capacity=worker_cap)
        s["available_workers"] = available_workers

    orders = deepcopy(config.orders)
    order_completion: Dict[str, float] = {}
    unit_completion: Dict[str, List[float]] = defaultdict(list)
    event_log: List[Dict[str, Any]] = []
    queue_samples: Dict[str, List[Tuple[float, int]]] = defaultdict(list)

    total_units = 0
    processes = []

    def process_unit(order: Dict[str, Any], unit_index: int):
        release = float(order.get("release_h", 0.0))
        if release > env.now:
            yield env.timeout(release - env.now)

        for step_idx, (sid, base_cycle_min) in enumerate(order["route"]):
            s = stations[sid]
            available_workers = s["available_workers"]
            if available_workers <= 0:
                # Sem operador, o posto não para o programa; representa colapso operacional grave.
                yield env.timeout(24.0)

            machines = max(1, int(s["maquinas"]))
            required_workers_for_full = max(1, math.ceil(machines * float(s.get("operadores_por_maquina", 1))))
            staffing_ratio = min(1.0, max(0.12, available_workers / required_workers_for_full))
            operator_eff = max(0.55, min(1.20, float(s.get("eficiencia_operador", 1.0))))
            availability = max(0.50, min(1.0, float(s.get("disponibilidade", 1.0))))

            # Tempo efetivo cresce quando há subalocação, baixa eficiência ou baixa disponibilidade.
            cycle_h = (float(base_cycle_min) / 60.0) / (staffing_ratio * operator_eff * availability)
            # Pequena variabilidade reproduz a dispersão natural de execução, mantendo comparação reprodutível.
            cycle_h *= rng.triangular(0.96, 1.05, 1.0)

            pr = _priority(order, base_cycle_min, config.dispatch_rule, unit_index)
            pr_value = pr[0] * 10000 + pr[1] * 100 + pr[2] / 1000

            queue_samples[sid].append((env.now, len(machine_resources[sid].queue)))
            wait_start = env.now
            with machine_resources[sid].request(priority=pr_value) as mreq, worker_resources[sid].request(priority=pr_value) as wreq:
                yield mreq & wreq
                wait = env.now - wait_start
                station_stats[sid]["wait_h"] += wait

                setup_h = 0.0
                # Setup amortizado no primeiro item do lote em cada etapa.
                if unit_index == 0:
                    setup_h = float(s.get("setup_min", 0.0)) / 60.0

                operation_h = cycle_h + setup_h
                if config.chaos_station == sid and config.chaos_duration_h > 0:
                    outage_start = float(config.chaos_start_h)
                    outage_end = outage_start + float(config.chaos_duration_h)
                    operation_h += _overlap_delay(env.now, operation_h, outage_start, outage_end)

                start = env.now
                yield env.timeout(operation_h)
                elapsed = env.now - start
                station_stats[sid]["busy_machine_h"] += elapsed
                station_stats[sid]["busy_worker_h"] += elapsed
                station_stats[sid]["operations"] += 1
                station_stats[sid]["units"] += 1

                if unit_index == 0:
                    event_log.append({
                        "time": env.now,
                        "type": "flow",
                        "message": f"{order['id']} liberou a 1ª peça de {s['nome']}.",
                    })

        unit_completion[order["id"]].append(env.now)
        if len(unit_completion[order["id"]]) >= int(order["quantidade_sim"]):
            order_completion[order["id"]] = max(unit_completion[order["id"]])

    for order in orders:
        qty = max(1, int(round(order["quantidade"] * config.demand_multiplier)))
        order["quantidade_sim"] = qty
        total_units += qty
        for unit_idx in range(qty):
            processes.append(env.process(process_unit(order, unit_idx)))

    env.run(until=simpy.events.AllOf(env, processes))
    makespan = float(env.now)

    # Eventos de perturbação entram na Black Box mesmo quando não coincidem
    # com a liberação da primeira peça de uma OP. Isso melhora a leitura causal.
    if config.chaos_station and float(config.chaos_duration_h) > 0:
        event_log.append({
            "time": float(config.chaos_start_h), "type": "murphy",
            "message": f"EVENTO MURPHY iniciado em {config.chaos_station}: janela de perturbação de {float(config.chaos_duration_h):.1f} h.",
        })
        event_log.append({
            "time": float(config.chaos_start_h) + float(config.chaos_duration_h), "type": "recovery",
            "message": f"Janela de perturbação encerrada em {config.chaos_station}; o fluxo entra em recuperação.",
        })
    for sid, n_abs in (config.absent_workers or {}).items():
        if int(n_abs) > 0:
            event_log.append({"time": 0.0, "type": "workforce", "message": f"{sid}: {int(n_abs)} ausência(s) considerada(s) no cenário."})

    order_rows = []
    penalty_total = 0.0
    late_orders = 0
    sla_units = 0
    for order in orders:
        finish = float(order_completion.get(order["id"], makespan))
        lateness = max(0.0, finish - float(order["prazo_h"]))
        penalty = lateness * float(order["multa_hora"])
        penalty_total += penalty
        if lateness > 0:
            late_orders += 1
        else:
            sla_units += int(order["quantidade_sim"])
        order_rows.append({
            "OP": order["id"],
            "Cliente": order["cliente"],
            "Produto": order["produto"],
            "Quantidade": int(order["quantidade_sim"]),
            "Prazo (h)": float(order["prazo_h"]),
            "Conclusão (h)": round(finish, 2),
            "Atraso (h)": round(lateness, 2),
            "Multa (R$)": round(penalty, 2),
            "Status": "No prazo" if lateness <= 0 else "Atrasada",
        })

    station_rows = []
    operating_cost = 0.0
    bottleneck_sid = None
    bottleneck_score = -1.0
    for sid, s in stations.items():
        stats = station_stats[sid]
        machines = max(1, int(s["maquinas"]))
        workers = max(0, int(s["available_workers"]))
        machine_util = min(100.0, 100 * stats["busy_machine_h"] / max(0.01, makespan * machines))
        worker_util = min(100.0, 100 * stats["busy_worker_h"] / max(0.01, makespan * max(1, workers)))
        avg_wait_min = (stats["wait_h"] / max(1, stats["operations"])) * 60.0
        max_queue = max([q for _, q in queue_samples[sid]], default=0)
        station_cost = makespan * (
            machines * float(s["custo_maquina_h"]) + max(0, workers) * float(s["custo_operador_h"])
        )
        operating_cost += station_cost
        score = machine_util + min(50, avg_wait_min / 2) + max_queue * 2
        if score > bottleneck_score:
            bottleneck_score = score
            bottleneck_sid = sid
        station_rows.append({
            "Posto": sid,
            "Nome": s["nome"],
            "Máquinas": machines,
            "Operadores": workers,
            "Utilização máquina (%)": round(machine_util, 1),
            "Utilização mão de obra (%)": round(worker_util, 1),
            "Espera média (min)": round(avg_wait_min, 1),
            "Fila máx.": int(max_queue),
            "Custo cenário (R$)": round(station_cost, 2),
        })

    throughput_h = total_units / max(makespan, 0.01)
    unit_cost = operating_cost / max(total_units, 1)
    sla = 100 * (len(orders) - late_orders) / max(1, len(orders))
    balance_loss = 0.0
    utils = [r["Utilização máquina (%)"] for r in station_rows]
    if utils:
        balance_loss = max(utils) - min(utils)

    return SimulationResult({
        "name": config.name,
        "dispatch_rule": config.dispatch_rule,
        "makespan_h": round(makespan, 2),
        "total_units": total_units,
        "throughput_h": round(throughput_h, 3),
        "sla_pct": round(sla, 1),
        "late_orders": late_orders,
        "penalty_total": round(penalty_total, 2),
        "operating_cost": round(operating_cost, 2),
        "total_cost": round(operating_cost + penalty_total, 2),
        "unit_cost": round(unit_cost, 2),
        "bottleneck": bottleneck_sid or "-",
        "balance_loss_pp": round(balance_loss, 1),
        "orders": order_rows,
        "stations": station_rows,
        "events": sorted(event_log, key=lambda x: x["time"]),
        "config": config,
    })
