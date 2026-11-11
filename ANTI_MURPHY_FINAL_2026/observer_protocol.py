"""Observer de EVENTOS DE DOMINIO do Anti-Murphy (nao integrado ao V30.2).

O motor deve chamar emit() somente APOS mutacoes atomicas da simulacao.
Nao retorna valores para o motor; caso o observer falhe, a politica de erro
precisa ser definida no adaptador de execucao (fail-fast para export auditavel).
"""
from __future__ import annotations
from typing import Callable, Literal
from simulation_contract import (
    EventDelta, SimulationSnapshot, StationState, UnitState, OrderState,
    apply_delta,
)


class RecordingObserver:
    def __init__(self, initial: SimulationSnapshot, keyframe_every: int = 100,
                 verify_state: Callable[[], SimulationSnapshot] | None = None):
        if keyframe_every < 1:
            raise ValueError("intervalo de keyframe deve ser positivo")
        self._current = initial
        self._first = initial
        self.events: list[EventDelta] = []
        self.keyframes: list[SimulationSnapshot] = [initial]
        self._stride = keyframe_every
        # Integração opcional: extrai estado REAL do motor apos cada evento.
        # Compare com replay reconstruido para flagrar hooks faltantes.
        self._verify_state = verify_state

    @property
    def state(self) -> SimulationSnapshot:
        return self._current

    def emit(self, *, time_us: int, kind: str, entity_id: str | None = None,
             station_upserts: dict[str, StationState] | None = None,
             unit_upserts: dict[str, UnitState] | None = None,
             order_upserts: dict[str, OrderState] | None = None) -> EventDelta:
        event = EventDelta(
            seq=self._current.seq + 1, time_us=time_us, kind=kind,
            entity_id=entity_id,
            station_upserts=station_upserts or {},
            unit_upserts=unit_upserts or {},
            order_upserts=order_upserts or {},
        )
        next_state = apply_delta(self._current, event)
        if self._verify_state is not None:
            observed = self._verify_state()
            if observed != next_state:
                raise ValueError("observer nao corresponde ao estado real do motor")
        self.events.append(event)
        self._current = next_state
        if event.seq % self._stride == 0:
            self.keyframes.append(next_state)
        return event

    def finalize(self) -> tuple[list[SimulationSnapshot], list[EventDelta]]:
        if self.keyframes[-1].seq != self._current.seq:
            self.keyframes.append(self._current)
        return self.keyframes.copy(), self.events.copy()
