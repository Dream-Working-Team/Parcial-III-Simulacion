"""
==============================================================================
MOTOR DE SIMULACIÓN CONTINUA (RESOLUTOR TÉRMICO EDO)
==============================================================================
Orquestador de integración numérica temporal para el clúster de servidores.
Modela en tiempo continuo la dinámica térmica, el tráfico estocástico y el rendimiento.
"""

import random
from typing import Optional, Dict, Any
from .models import TrafficGenerator, ThermalModel, ServerCluster
from .metrics import ContinuousMetricsCollector
from core.logger import SimulationLogger


class ContinuousSimulator:
    """
    Simulador de tiempo continuo para el clúster de servidores y balance térmico.
    """
    def __init__(
        self,
        duration_hours: float = 24.0,
        dt_seconds: float = 2.0,
        mean_traffic_gbps: float = 3.0,
        std_traffic_gbps: float = 1.0,
        target_temp_c: float = 70.0,
        ambient_temp_c: float = 25.0,
        k_cool_per_min: float = 0.08,
        k_heat_per_min: float = 1.2,
        seed: Optional[int] = None,
        logger: Optional[SimulationLogger] = None
    ):
        if seed is not None:
            random.seed(seed)

        self.duration_seconds = duration_hours * 3600.0
        self.dt_seconds = dt_seconds
        
        # Componentes del sistema continuo
        self.traffic_gen = TrafficGenerator(
            mean_gbps=mean_traffic_gbps,
            std_gbps=std_traffic_gbps,
            min_gbps=1.0,
            max_gbps=5.0
        )
        self.thermal_model = ThermalModel(
            initial_temp_c=target_temp_c,
            ambient_temp_c=ambient_temp_c,
            k_cool_per_min=k_cool_per_min,
            k_heat_per_min=k_heat_per_min
        )
        self.cluster = ServerCluster(target_temp_c=target_temp_c)
        self.metrics = ContinuousMetricsCollector()
        self.logger = logger or SimulationLogger("Simulacion_Continua", print_to_console=False)
        
        # Variables de estado actual
        self.current_time: float = 0.0
        self.current_incoming_gbps: float = mean_traffic_gbps
        self.current_processed_gbps: float = mean_traffic_gbps * 0.90
        self.current_efficiency: float = 0.90
        self.is_throttled: bool = False
        
        # Intervalo para emisión periódica de trazas en consola (ej. cada 30 minutos simulados)
        self._last_log_time: float = -1800.0
        self._prev_throttled_state: bool = False

        self.logger.log(
            0.0,
            "INICIO",
            f"Simulación Continua iniciada. Duración: {duration_hours:.1f}h, T_inicial: {target_temp_c:.1f}°C, dt={dt_seconds:.1f}s."
        )

    def step(self, custom_dt: Optional[float] = None) -> bool:
        """
        Ejecuta un paso de integración numérica de longitud dt.
        Retorna True si avanzó, False si finalizó el tiempo estipulado.
        """
        if self.current_time >= self.duration_seconds:
            return False

        dt = custom_dt if custom_dt is not None else self.dt_seconds
        dt = min(dt, self.duration_seconds - self.current_time)
        if dt <= 0:
            return False

        # 1. Generar tasa instantánea de tráfico entrante
        self.current_incoming_gbps = self.traffic_gen.sample_traffic(dt)

        # 2. Determinar eficiencia del clúster y procesar flujo
        (
            self.current_processed_gbps,
            self.current_efficiency,
            self.is_throttled
        ) = self.cluster.process_traffic(
            self.current_incoming_gbps,
            self.thermal_model.temperature
        )

        # 3. Integrar la ecuación diferencial de balance térmico (RK4)
        current_temp = self.thermal_model.step_rk4(self.current_processed_gbps, dt)

        # 4. Registrar en recopilador de métricas
        self.metrics.record_step(
            dt,
            current_temp,
            self.current_incoming_gbps,
            self.current_processed_gbps,
            self.is_throttled
        )

        # 5. Gestionar alertas y trazas
        self._check_and_log_traces(current_temp)

        self.current_time += dt
        return True

    def _check_and_log_traces(self, current_temp: float) -> None:
        """Emite trazas periódicas y alertas inmediatas ante cambio de estado térmico."""
        # Alerta por inicio de estrangulamiento térmico
        if self.is_throttled and not self._prev_throttled_state:
            self.logger.log(
                self.current_time,
                "THROTTLING_ON",
                f"¡ALERTA TÉRMICA! Temp: {current_temp:.2f}°C > 70°C. Throttling activo. Eficiencia cae a {self.current_efficiency*100:.1f}%."
            )
        # Alerta por recuperación térmica
        elif not self.is_throttled and self._prev_throttled_state:
            self.logger.log(
                self.current_time,
                "THROTTLING_OFF",
                f"RECUPERACIÓN TÉRMICA. Temp: {current_temp:.2f}°C <= 70°C. Sistema vuelve a régimen nominal (90%)."
            )
        
        self._prev_throttled_state = self.is_throttled

        # Traza periódica cada 30 minutos simulados (1800 segundos)
        if (self.current_time - self._last_log_time) >= 1800.0:
            self.logger.log(
                self.current_time,
                "ESTADO_RED",
                f"Temp: {current_temp:.2f}°C | Tráfico: {self.current_incoming_gbps:.2f} Gbps | Proc: {self.current_processed_gbps:.2f} Gbps | Eficiencia: {self.current_efficiency*100:.1f}%"
            )
            self._last_log_time = self.current_time

    def run_until_completion(self) -> Dict[str, Any]:
        """Ejecuta la simulación numérica continua completa hasta el tiempo límite."""
        while self.step():
            pass
        self.logger.log(
            self.current_time,
            "FIN_SIM",
            f"Simulación Continua finalizada a las {self.current_time/3600.0:.2f} horas."
        )
        return self.get_summary_metrics()

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calcula y devuelve el reporte consolidado de rendimiento y estabilidad."""
        return self.metrics.calculate_summary(self.duration_seconds)
