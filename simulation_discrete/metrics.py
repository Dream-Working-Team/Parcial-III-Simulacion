"""
==============================================================================
RECOPILADOR Y CALCULADOR DE MÉTRICAS - EVENTOS DISCRETOS
==============================================================================
Clase encargada de consolidar los datos de ejecución, calcular promedios,
porcentajes de eficiencia y generar resúmenes estadísticos listos para análisis.
"""

from typing import List, Dict, Any
from .models import LaptopOrder, AssemblyStation, InventoryManager


class DiscreteMetricsCollector:
    """Consolidador de estadísticas de la fábrica de laptops."""
    def __init__(self):
        self.completed_orders: List[LaptopOrder] = []
        self.delayed_by_stock_orders: List[LaptopOrder] = []

    def register_completed_order(self, order: LaptopOrder) -> None:
        """Registra una orden finalizada."""
        self.completed_orders.append(order)
        if order.delayed_due_to_stock:
            self.delayed_by_stock_orders.append(order)

    def calculate_summary(
        self,
        sim_duration_seconds: float,
        station: AssemblyStation,
        inventory: InventoryManager,
        queue_len: int,
        total_arrivals: int
    ) -> Dict[str, Any]:
        """Calcula el diccionario completo de indicadores requeridos por el parcial."""
        total_completed = len(self.completed_orders)
        
        # Tiempos de espera (en minutos)
        wait_times_min = [o.waiting_time / 60.0 for o in self.completed_orders]
        avg_wait_min = (sum(wait_times_min) / total_completed) if total_completed > 0 else 0.0
        max_wait_min = max(wait_times_min) if wait_times_min else 0.0
        
        # Tiempos en sistema (espera + servicio)
        system_times_min = [o.total_system_time / 60.0 for o in self.completed_orders]
        avg_system_min = (sum(system_times_min) / total_completed) if total_completed > 0 else 0.0
        
        # Duración de simulación en horas y minutos
        sim_duration_hours = sim_duration_seconds / 3600.0
        sim_duration_min = sim_duration_seconds / 60.0
        
        # Detención de línea
        stopped_min = station.total_stopped_time / 60.0
        stopped_pct = (station.total_stopped_time / sim_duration_seconds * 100.0) if sim_duration_seconds > 0 else 0.0
        busy_min = station.total_busy_time / 60.0
        idle_min = station.total_idle_time / 60.0
        station_utilization = (station.total_busy_time / sim_duration_seconds * 100.0) if sim_duration_seconds > 0 else 0.0
        
        # Tiempo promedio para despachar un lote de 50 laptops
        # Si se produjeron lotes, calculamos el tiempo promedio por cada bloque de 50
        batch_size = inventory.batch_size
        batch_dispatch_times_min = []
        if total_completed >= batch_size:
            for i in range(batch_size - 1, total_completed, batch_size):
                lot_time = (self.completed_orders[i].completion_time - self.completed_orders[i - (batch_size - 1)].arrival_time) / 60.0
                batch_dispatch_times_min.append(lot_time)
        avg_batch_dispatch_min = (sum(batch_dispatch_times_min) / len(batch_dispatch_times_min)) if batch_dispatch_times_min else (avg_system_min * batch_size)

        # Eficiencia en el reabastecimiento:
        # Porcentaje de órdenes que se ensamblaron sin sufrir retraso por falta de stock (Fill Rate)
        orders_delayed_count = len(self.delayed_by_stock_orders)
        orders_delayed_pct = (orders_delayed_count / total_completed * 100.0) if total_completed > 0 else 0.0
        replenishment_efficiency_pct = max(0.0, 100.0 - orders_delayed_pct)

        return {
            "duracion_simulacion_horas": round(sim_duration_hours, 2),
            "duracion_simulacion_minutos": round(sim_duration_min, 2),
            "total_ordenes_recibidas": total_arrivals,
            "total_ordenes_completadas": total_completed,
            "ordenes_en_cola_final": queue_len,
            "tiempo_espera_promedio_min": round(avg_wait_min, 2),
            "tiempo_espera_maximo_min": round(max_wait_min, 2),
            "tiempo_sistema_promedio_min": round(avg_system_min, 2),
            "tiempo_despacho_lote_promedio_min": round(avg_batch_dispatch_min, 2),
            "paradas_linea_por_falta_stock": station.line_stops_count,
            "tiempo_total_linea_detenida_min": round(stopped_min, 2),
            "porcentaje_tiempo_linea_detenida": round(stopped_pct, 2),
            "utilizacion_estacion_ensamblaje_pct": round(station_utilization, 2),
            "ordenes_retrasadas_por_stock": orders_delayed_count,
            "porcentaje_ordenes_retrasadas": round(orders_delayed_pct, 2),
            "eficiencia_reabastecimiento_pct": round(replenishment_efficiency_pct, 2),
            "total_reordenes_emitidas": inventory.total_reorders_placed,
            "total_lotes_recibidos": inventory.total_batches_received,
            "stock_final_procesadores": inventory.current_stock
        }
