"""
==============================================================================
MOTOR DE SIMULACIÓN DE EVENTOS DISCRETOS (DES)
==============================================================================
Orquestador basado en cola de prioridad (heapq) para la fábrica de laptops.
Controla el reloj de simulación, la gestión estocástica de eventos y las trazas.
"""

import heapq
import random
from typing import List, Optional, Dict, Any
from .models import LaptopOrder, AssemblyStation, InventoryManager, StationStatus, OrderStatus
from .events import Event, OrderArrivalEvent, AssemblyCompleteEvent, RestockArrivalEvent
from .metrics import DiscreteMetricsCollector
from core.logger import SimulationLogger


class DiscreteEventSimulator:
    """
    Simulador de eventos discretos para la fábrica de ensamblaje de laptops.
    """
    def __init__(
        self,
        duration_hours: float = 8.0,
        arrival_rate_hourly: float = 10.0,
        service_mean_minutes: float = 5.0,
        initial_stock: int = 25,
        reorder_threshold: int = 10,
        batch_size: int = 50,
        lead_time_minutes: float = 15.0,
        seed: Optional[int] = None,
        logger: Optional[SimulationLogger] = None
    ):
        if seed is not None:
            random.seed(seed)

        self.duration_seconds = duration_hours * 3600.0
        self.arrival_rate_per_second = arrival_rate_hourly / 3600.0
        self.service_mean_seconds = service_mean_minutes * 60.0
        
        # Componentes del sistema
        self.station = AssemblyStation()
        self.inventory = InventoryManager(
            initial_stock=initial_stock,
            reorder_threshold=reorder_threshold,
            batch_size=batch_size,
            lead_time_seconds=lead_time_minutes * 60.0
        )
        self.metrics = DiscreteMetricsCollector()
        self.logger = logger or SimulationLogger("Simulacion_Discreta", print_to_console=False)
        
        # Cola de espera de órdenes (FIFO)
        self.order_queue: List[LaptopOrder] = []
        
        # Cola de prioridad de eventos futuros (min-heap)
        self.event_queue: List[Event] = []
        
        # Estado del simulador
        self.current_time: float = 0.0
        self.order_counter: int = 0
        self.batch_counter: int = 0
        self.is_finished: bool = False
        
        # Programar primer arribo
        self._schedule_first_arrival()

    def _schedule_first_arrival(self) -> None:
        """Programa la llegada de la primera orden."""
        first_arrival_delta = random.expovariate(self.arrival_rate_per_second)
        self.order_counter += 1
        heapq.heappush(self.event_queue, OrderArrivalEvent(first_arrival_delta, self.order_counter))
        self.logger.log(0.0, "INICIO", f"Simulador iniciado. Primera orden programada en {first_arrival_delta/60.0:.2f} min.")

    def step(self) -> bool:
        """
        Avanza la simulación al siguiente evento programado.
        Retorna True si procesó un evento, False si no hay más eventos o superó el tiempo.
        """
        if not self.event_queue:
            self._finalize_simulation()
            return False

        # Extraer el evento más próximo en el tiempo
        event = heapq.heappop(self.event_queue)
        
        if event.timestamp > self.duration_seconds:
            self.current_time = self.duration_seconds
            self._finalize_simulation()
            return False

        self.current_time = event.timestamp

        # Despachar según tipo de evento
        if isinstance(event, OrderArrivalEvent):
            self._handle_order_arrival(event)
        elif isinstance(event, AssemblyCompleteEvent):
            self._handle_assembly_complete(event)
        elif isinstance(event, RestockArrivalEvent):
            self._handle_restock_arrival(event)

        return True

    def run_until_completion(self) -> Dict[str, Any]:
        """Ejecuta la simulación completa hasta alcanzar el tiempo configurado."""
        while self.step():
            pass
        return self.get_summary_metrics()

    def _handle_order_arrival(self, event: OrderArrivalEvent) -> None:
        """Procesa el arribo de una orden de producción."""
        order_id = event.data["order_id"]
        # Tiempo de servicio exponencial: media de 5 minutos
        service_duration = random.expovariate(1.0 / self.service_mean_seconds)
        new_order = LaptopOrder(order_id, self.current_time, service_duration)
        
        self.logger.log(
            self.current_time,
            "LLEGADA",
            f"Orden #{order_id} recibida. Servicio estimado: {service_duration/60.0:.2f} min. Stock actual: {self.inventory.current_stock}"
        )

        # Programar próxima llegada si no supera la duración
        next_arrival_time = self.current_time + random.expovariate(self.arrival_rate_per_second)
        if next_arrival_time <= self.duration_seconds:
            self.order_counter += 1
            heapq.heappush(self.event_queue, OrderArrivalEvent(next_arrival_time, self.order_counter))

        # Evaluar atención en la estación de ensamblaje
        if self.station.status == StationStatus.IDLE and len(self.order_queue) == 0:
            self._attempt_start_assembly(new_order)
        else:
            self.order_queue.append(new_order)
            self.logger.log(
                self.current_time,
                "EN_COLA",
                f"Orden #{order_id} entra a cola de espera. Longitud de cola: {len(self.order_queue)}"
            )

    def _attempt_start_assembly(self, order: LaptopOrder) -> None:
        """Intenta iniciar el ensamblaje verificando disponibilidad de stock."""
        if self.inventory.current_stock > 0:
            # Consumir 1 procesador
            self.inventory.consume_processor(self.current_time)
            self.station.assign_order(order, self.current_time)
            
            # Programar fin de ensamble
            finish_time = self.current_time + order.service_duration
            heapq.heappush(self.event_queue, AssemblyCompleteEvent(finish_time, order.order_id))
            
            self.logger.log(
                self.current_time,
                "SERVICIO",
                f"Orden #{order.order_id} inicia ensamble. Procesador asignado. Stock restante: {self.inventory.current_stock}"
            )

            # Verificar si se debe activar reorden automática (< 10)
            self._check_and_trigger_reorder()
        else:
            # Línea detenida por falta de stock
            self.station.assign_order(order, self.current_time)
            self.station.stop_line(self.current_time)
            self.logger.log(
                self.current_time,
                "PARADA_LINEA",
                f"¡ALERTA! Stock en CERO. Orden #{order.order_id} bloqueada. Línea de ensamblaje DETENIDA."
            )
            # Asegurar que se haya pedido reorden si no estaba en camino
            self._check_and_trigger_reorder()

    def _handle_assembly_complete(self, event: AssemblyCompleteEvent) -> None:
        """Procesa la finalización de un ensamblaje."""
        completed_order = self.station.complete_order(self.current_time)
        if completed_order:
            self.metrics.register_completed_order(completed_order)
            self.logger.log(
                self.current_time,
                "FINALIZADO",
                f"Orden #{completed_order.order_id} completada. Espera: {completed_order.waiting_time/60.0:.2f} min, Total: {completed_order.total_system_time/60.0:.2f} min."
            )

        # Si hay órdenes en cola, atender la siguiente
        if self.order_queue:
            next_order = self.order_queue.pop(0)
            self._attempt_start_assembly(next_order)
        else:
            self.logger.log(self.current_time, "ESTACION", "Estación queda LIBRE en espera de nuevas órdenes.")

    def _handle_restock_arrival(self, event: RestockArrivalEvent) -> None:
        """Procesa la entrega de un lote de procesadores por el proveedor."""
        new_stock = self.inventory.receive_shipment(self.current_time)
        batch_id = event.data["batch_id"]
        self.logger.log(
            self.current_time,
            "REABASTECE",
            f"Lote #{batch_id} (+{self.inventory.batch_size} CPUs) entregado por proveedor. Stock actualizado: {new_stock} unidades."
        )

        # Si la estación estaba detenida por falta de procesadores, se reanuda
        if self.station.status == StationStatus.STOPPED_NO_STOCK:
            blocked_order = self.station.current_order
            if blocked_order and self.inventory.consume_processor(self.current_time):
                self.station.resume_line(self.current_time)
                # Programar fin de ensamblaje desde el momento que se reanuda
                finish_time = self.current_time + blocked_order.service_duration
                heapq.heappush(self.event_queue, AssemblyCompleteEvent(finish_time, blocked_order.order_id))
                self.logger.log(
                    self.current_time,
                    "REANUDACION",
                    f"Línea reanudada con Orden #{blocked_order.order_id}. CPU asignado. Stock: {self.inventory.current_stock}"
                )
                self._check_and_trigger_reorder()

    def _check_and_trigger_reorder(self) -> None:
        """Comprueba el umbral crítico y emite orden de reabastecimiento si corresponde."""
        if self.inventory.needs_reorder():
            self.batch_counter += 1
            arrival_time = self.inventory.trigger_reorder(self.current_time)
            heapq.heappush(self.event_queue, RestockArrivalEvent(arrival_time, self.batch_counter))
            self.logger.log(
                self.current_time,
                "ORDEN_COMPRA",
                f"Stock ({self.inventory.current_stock}) cayó bajo el umbral ({self.inventory.reorder_threshold}). Pedido de lote #{self.batch_counter} emitido. Entrega en 15 min."
            )

    def _finalize_simulation(self) -> None:
        """Cierra el cómputo de tiempos al término del periodo de simulación."""
        if not self.is_finished:
            self.station._update_accumulated_times(self.current_time)
            self.is_finished = True
            self.logger.log(
                self.current_time,
                "FIN_SIM",
                f"Simulación finalizada a las {self.current_time/3600.0:.2f} horas. Generando métricas finales."
            )

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calcula y devuelve las métricas consolidadas del sistema."""
        self._finalize_simulation()
        return self.metrics.calculate_summary(
            sim_duration_seconds=self.duration_seconds,
            station=self.station,
            inventory=self.inventory,
            queue_len=len(self.order_queue),
            total_arrivals=self.order_counter
        )
