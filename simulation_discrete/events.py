"""
==============================================================================
EVENTOS DE SIMULACIÓN DISCRETA
==============================================================================
Jerarquía de clases para los eventos futuros programados en la cola de prioridad.
"""

from typing import Any


class Event:
    """Clase base para cualquier evento discreto en el tiempo."""
    def __init__(self, timestamp: float, event_type: str, data: Any = None):
        self.timestamp = timestamp
        self.event_type = event_type
        self.data = data

    def __lt__(self, other: "Event") -> bool:
        """Comparador para heapq (orden ascendente por marca de tiempo)."""
        return self.timestamp < other.timestamp

    def __repr__(self) -> str:
        return f"<Event {self.event_type} @ {self.timestamp:.2f}s>"


class OrderArrivalEvent(Event):
    """Evento: Llega una nueva orden de laptop a la fábrica."""
    def __init__(self, timestamp: float, order_id: int):
        super().__init__(timestamp, "LLEGADA_ORDEN", data={"order_id": order_id})


class AssemblyCompleteEvent(Event):
    """Evento: La estación concluye el ensamblaje de la laptop actual."""
    def __init__(self, timestamp: float, order_id: int):
        super().__init__(timestamp, "FIN_ENSAMBLAJE", data={"order_id": order_id})


class RestockArrivalEvent(Event):
    """Evento: Llega el lote de 50 procesadores despachado por el proveedor."""
    def __init__(self, timestamp: float, batch_id: int):
        super().__init__(timestamp, "LLEGADA_REABASTECIMIENTO", data={"batch_id": batch_id})
