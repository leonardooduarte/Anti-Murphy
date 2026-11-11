from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass(frozen=True)
class TimedAction:
    """A response requested at a model time, with no changes to prior history."""
    at_h: float
    label: str = 'Resposta operacional'
    workers_delta: Dict[str, int] | None = None
    machines_delta: Dict[str, int] | None = None
    dispatch_rule: str | None = None
    repair_remaining_factor: float | None = None


@dataclass
class ScenarioConfig:
    name: str
    stations: Dict[str, Dict[str, Any]]
    orders: List[Dict[str, Any]]
    dispatch_rule: str = "EDD"
    demand_multiplier: float = 1.0
    chaos_station: str | None = None
    chaos_start_h: float = 6.0
    chaos_duration_h: float = 0.0
    absent_workers: Dict[str, int] | None = None
    seed: int = 42

    def clone(self, name: str | None = None) -> "ScenarioConfig":
        return ScenarioConfig(
            name=name or self.name,
            stations=deepcopy(self.stations),
            orders=deepcopy(self.orders),
            dispatch_rule=self.dispatch_rule,
            demand_multiplier=self.demand_multiplier,
            chaos_station=self.chaos_station,
            chaos_start_h=self.chaos_start_h,
            chaos_duration_h=self.chaos_duration_h,
            absent_workers=deepcopy(self.absent_workers or {}),
            seed=self.seed,
        )


def build_scenario(name: str, stations: Dict[str, Dict[str, Any]], orders: List[Dict[str, Any]], **kwargs) -> ScenarioConfig:
    return ScenarioConfig(name=name, stations=deepcopy(stations), orders=deepcopy(orders), **kwargs)
