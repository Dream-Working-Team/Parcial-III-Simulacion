"""
==============================================================================
RECOPILADOR Y CALCULADOR DE MÉTRICAS - SIMULACIÓN CONTINUA
==============================================================================
Clase encargada de integrar temporalmente el tráfico procesado (Terabytes),
evaluar la variabilidad térmica y diagnosticar la estabilidad del clúster.
"""

import math
from typing import List, Dict, Any


class ContinuousMetricsCollector:
    """Consolidador de estadísticas de rendimiento y térmicas del clúster."""
    def __init__(self):
        self.temperature_samples: List[float] = []
        self.traffic_samples: List[float] = []
        self.throughput_samples: List[float] = []
        
        # Acumuladores de datos (en Gigabit-segundos)
        self.total_traffic_gigabits: float = 0.0
        self.total_processed_gigabits: float = 0.0
        
        # Tiempos de estrangulamiento
        self.total_throttled_seconds: float = 0.0
        self.throttling_events_count: int = 0
        self._was_throttled_prev: bool = False

    def record_step(
        self,
        dt_seconds: float,
        temperature: float,
        incoming_gbps: float,
        processed_gbps: float,
        is_throttled: bool
    ) -> None:
        """Registra un paso de integración numérica continua."""
        self.temperature_samples.append(temperature)
        self.traffic_samples.append(incoming_gbps)
        self.throughput_samples.append(processed_gbps)
        
        self.total_traffic_gigabits += incoming_gbps * dt_seconds
        self.total_processed_gigabits += processed_gbps * dt_seconds
        
        if is_throttled:
            self.total_throttled_seconds += dt_seconds
            if not self._was_throttled_prev:
                self.throttling_events_count += 1
        self._was_throttled_prev = is_throttled

    def calculate_summary(self, total_sim_seconds: float) -> Dict[str, Any]:
        """Calcula el consolidado final de métricas en Terabytes y estabilidad térmica."""
        # 1 Byte = 8 bits -> 1 Terabyte = 8,000 Gigabits (o 8,192 Gb en base 2, usamos estándar 8,000 Gb = 1 TB de red)
        total_traffic_tb = self.total_traffic_gigabits / 8000.0
        total_processed_tb = self.total_processed_gigabits / 8000.0
        
        # Eficiencia global de la red
        global_efficiency_pct = (
            (self.total_processed_gigabits / self.total_traffic_gigabits * 100.0)
            if self.total_traffic_gigabits > 0 else 0.0
        )
        
        # Estadísticas de temperatura
        n = len(self.temperature_samples)
        if n > 0:
            mean_temp = sum(self.temperature_samples) / n
            variance = sum((t - mean_temp) ** 2 for t in self.temperature_samples) / n
            std_temp = math.sqrt(variance)
            min_temp = min(self.temperature_samples)
            max_temp = max(self.temperature_samples)
        else:
            mean_temp = std_temp = min_temp = max_temp = 0.0

        # Porcentaje de tiempo bajo estrangulamiento
        throttled_pct = (
            (self.total_throttled_seconds / total_sim_seconds * 100.0)
            if total_sim_seconds > 0 else 0.0
        )
        
        # Diagnóstico de viabilidad operativa
        is_viable = max_temp <= 85.0 and throttled_pct < 25.0
        stability_status = (
            "ESTABLE Y VIABLE" if is_viable else "RIESGO TÉRMICO / DEGRADACIÓN SEVERA"
        )

        return {
            "duracion_simulacion_horas": round(total_sim_seconds / 3600.0, 2),
            "total_trafico_entrante_tb": round(total_traffic_tb, 3),
            "total_datos_procesados_tb": round(total_processed_tb, 3),
            "perdida_o_rechazo_tb": round(max(0.0, total_traffic_tb - total_processed_tb), 3),
            "eficiencia_global_red_pct": round(global_efficiency_pct, 2),
            "temperatura_promedio_c": round(mean_temp, 2),
            "temperatura_desviacion_estandar_c": round(std_temp, 2),
            "temperatura_minima_c": round(min_temp, 2),
            "temperatura_maxima_c": round(max_temp, 2),
            "eventos_estrangulamiento_termico": self.throttling_events_count,
            "tiempo_en_estrangulamiento_min": round(self.total_throttled_seconds / 60.0, 2),
            "porcentaje_tiempo_estrangulado": round(throttled_pct, 2),
            "diagnostico_viabilidad_operativa": stability_status
        }
