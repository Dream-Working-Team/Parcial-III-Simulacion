"""
==============================================================================
MODELOS DE DOMINIO - SIMULACIÓN DE EVENTOS DISCRETOS
==============================================================================
Clases POO que representan los componentes físicos y lógicos de la fábrica:
órdenes de laptops, estación de ensamblaje y gestión de inventario de procesadores.
"""

from enum import Enum
from typing import Optional, List, Tuple


class OrderStatus(Enum):
    PENDING = "PENDIENTE"
    IN_ASSEMBLY = "EN_ENSAMBLAJE"
    BLOCKED_NO_STOCK = "BLOQUEADA_SIN_STOCK"
    COMPLETED = "COMPLETADA"


class StationStatus(Enum):
    IDLE = "LIBRE"
    BUSY = "OCUPADA"
    STOPPED_NO_STOCK = "DETENIDA_SIN_STOCK"


class LaptopOrder:
    """
    Representa una orden individual de producción de laptop en el sistema.
    """
    def __init__(self, order_id: int, arrival_time: float, service_duration: float):
        self.order_id = order_id
        self.arrival_time = arrival_time
        self.service_duration = service_duration
        self.start_service_time: Optional[float] = None
        self.completion_time: Optional[float] = None
        self.status: OrderStatus = OrderStatus.PENDING
        self.delayed_due_to_stock: bool = False

    @property
    def waiting_time(self) -> float:
        """Tiempo de espera en cola antes de iniciar ensamblaje (segundos)."""
        if self.start_service_time is None:
            return 0.0
        return max(0.0, self.start_service_time - self.arrival_time)

    @property
    def total_system_time(self) -> float:
        """Tiempo total transcurrido desde llegada hasta finalización (segundos)."""
        if self.completion_time is None:
            return 0.0
        return max(0.0, self.completion_time - self.arrival_time)

    def __repr__(self) -> str:
        return f"<LaptopOrder #{self.order_id} arribo={self.arrival_time:.1f}s estado={self.status.value}>"


class AssemblyStation:
    """
    Estación principal de ensamblaje de la fábrica.
    Modela un servidor de atención con estados: LIBRE, OCUPADA o DETENIDA POR FALTA DE STOCK.
    """
    def __init__(self, station_id: str = "ESTACION_PRINCIPAL"):
        self.station_id = station_id
        self.status: StationStatus = StationStatus.IDLE
        self.current_order: Optional[LaptopOrder] = None
        
        # Métricas temporales acumuladas
        self.last_state_change: float = 0.0
        self.total_idle_time: float = 0.0
        self.total_busy_time: float = 0.0
        self.total_stopped_time: float = 0.0
        self.line_stops_count: int = 0

    def assign_order(self, order: LaptopOrder, current_time: float) -> None:
        """Asigna una orden para iniciar ensamble."""
        self._update_accumulated_times(current_time)
        self.status = StationStatus.BUSY
        self.current_order = order
        order.start_service_time = current_time
        order.status = OrderStatus.IN_ASSEMBLY

    def complete_order(self, current_time: float) -> Optional[LaptopOrder]:
        """Finaliza el ensamblaje de la orden actual."""
        self._update_accumulated_times(current_time)
        finished = self.current_order
        if finished:
            finished.completion_time = current_time
            finished.status = OrderStatus.COMPLETED
        self.current_order = None
        self.status = StationStatus.IDLE
        return finished

    def stop_line(self, current_time: float) -> None:
        """Detiene la línea de producción por falta de procesadores."""
        if self.status != StationStatus.STOPPED_NO_STOCK:
            self._update_accumulated_times(current_time)
            self.status = StationStatus.STOPPED_NO_STOCK
            self.line_stops_count += 1
            if self.current_order:
                self.current_order.status = OrderStatus.BLOCKED_NO_STOCK
                self.current_order.delayed_due_to_stock = True

    def resume_line(self, current_time: float) -> None:
        """Reanuda la línea tras recibir procesadores."""
        if self.status == StationStatus.STOPPED_NO_STOCK:
            self._update_accumulated_times(current_time)
            if self.current_order:
                self.status = StationStatus.BUSY
                self.current_order.status = OrderStatus.IN_ASSEMBLY
            else:
                self.status = StationStatus.IDLE

    def _update_accumulated_times(self, current_time: float) -> None:
        """Actualiza los acumuladores de tiempo según el estado previo."""
        delta = max(0.0, current_time - self.last_state_change)
        if self.status == StationStatus.IDLE:
            self.total_idle_time += delta
        elif self.status == StationStatus.BUSY:
            self.total_busy_time += delta
        elif self.status == StationStatus.STOPPED_NO_STOCK:
            self.total_stopped_time += delta
        self.last_state_change = current_time


class InventoryManager:
    """
    Gestor de inventario de procesadores de gama alta.
    Implementa política de revisión continua (s, Q):
    Cuando el stock cae por debajo del umbral crítico (< 10), se solicita un lote de 50 procesadores.
    """
    def __init__(
        self,
        initial_stock: int = 25,
        reorder_threshold: int = 10,
        batch_size: int = 50,
        lead_time_seconds: float = 15.0 * 60.0
    ):
        self.current_stock = initial_stock
        self.reorder_threshold = reorder_threshold
        self.batch_size = batch_size
        self.lead_time_seconds = lead_time_seconds
        
        self.has_pending_order: bool = False
        self.pending_order_arrival_time: Optional[float] = None
        
        # Historial y métricas de inventario
        self.total_reorders_placed: int = 0
        self.total_batches_received: int = 0
        self.stockout_events: int = 0
        self.stock_history: List[Tuple[float, int]] = [(0.0, initial_stock)]

    def needs_reorder(self) -> bool:
        """Verifica si el stock cayó por debajo del umbral crítico y no hay orden en camino."""
        return (self.current_stock < self.reorder_threshold) and (not self.has_pending_order)

    def trigger_reorder(self, current_time: float) -> float:
        """
        Emite una orden de compra al proveedor.
        Retorna la marca de tiempo estimada de arribo del lote.
        """
        self.has_pending_order = True
        self.total_reorders_placed += 1
        arrival_time = current_time + self.lead_time_seconds
        self.pending_order_arrival_time = arrival_time
        return arrival_time

    def receive_shipment(self, current_time: float) -> int:
        """Recibe el lote entregado por el proveedor."""
        self.current_stock += self.batch_size
        self.has_pending_order = False
        self.pending_order_arrival_time = None
        self.total_batches_received += 1
        self.stock_history.append((current_time, self.current_stock))
        return self.current_stock

    def consume_processor(self, current_time: float) -> bool:
        """
        Consume 1 procesador para ensamblar una laptop.
        Retorna True si había stock disponible, False si se agotó.
        """
        if self.current_stock > 0:
            self.current_stock -= 1
            self.stock_history.append((current_time, self.current_stock))
            return True
        else:
            self.stockout_events += 1
            return False
