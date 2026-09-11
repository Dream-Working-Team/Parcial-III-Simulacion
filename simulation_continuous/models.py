"""
==============================================================================
MODELOS DE DOMINIO - SIMULACIÓN CONTINUA (CLÚSTER TÉRMICO)
==============================================================================
Clases POO que modelan la física del sistema continuo:
generador de tráfico de red, balance térmico diferencial y clúster de servidores con estrangulamiento.
"""

import math
import random
from typing import Tuple


class TrafficGenerator:
    """
    Generador estocástico de tráfico de red continuo.
    Sigue una distribución Normal(mu=3 Gbps, sigma=1 Gbps), acotada en [1, 5] Gbps.
    Implementa un proceso con correlación temporal suave (Ornstein-Uhlenbeck)
    para evitar saltos bruscos no físicos entre pasos de tiempo continuos.
    """
    def __init__(
        self,
        mean_gbps: float = 3.0,
        std_gbps: float = 1.0,
        min_gbps: float = 1.0,
        max_gbps: float = 5.0,
        correlation_time_sec: float = 60.0
    ):
        self.mean_gbps = mean_gbps
        self.std_gbps = std_gbps
        self.min_gbps = min_gbps
        self.max_gbps = max_gbps
        self.correlation_time_sec = correlation_time_sec
        self.current_traffic = mean_gbps

    def sample_traffic(self, dt_seconds: float) -> float:
        """
        Calcula la tasa instantánea de tráfico en Gbps para el paso dt.
        Combina retorno a la media con perturbación estocástica gaussiana.
        """
        # Coeficiente de reversión a la media
        theta = 1.0 / max(1.0, self.correlation_time_sec)
        drift = theta * (self.mean_gbps - self.current_traffic) * dt_seconds
        diffusion = self.std_gbps * math.sqrt(2 * theta * dt_seconds) * random.gauss(0, 1)
        
        raw_traffic = self.current_traffic + drift + diffusion
        # Acotar estrictamente según especificación del parcial: entre 1 y 5 Gbps
        self.current_traffic = max(self.min_gbps, min(self.max_gbps, raw_traffic))
        return self.current_traffic


class ThermalModel:
    """
    Modelo de balance térmico basado en una Ecuación Diferencial Ordinaria (EDO) de primer orden:
    dT/dt = Q_gen(t) - Q_diss(t)
    donde:
      Q_gen(t) = k_heat * Throughput_procesado(t)
      Q_diss(t) = k_cool * (T(t) - T_ambiente)
    """
    def __init__(
        self,
        initial_temp_c: float = 70.0,
        ambient_temp_c: float = 25.0,
        k_cool_per_min: float = 0.08,
        k_heat_per_min: float = 1.2
    ):
        self.temperature = initial_temp_c
        self.ambient_temp = ambient_temp_c
        # Convertir coeficientes a unidades por segundo para integración exacta
        self.k_cool = k_cool_per_min / 60.0
        self.k_heat = k_heat_per_min / 60.0

    def calculate_derivative(self, temp: float, processed_gbps: float) -> float:
        """
        Retorna la derivada temporal instantánea dT/dt (°C / segundo).
        """
        q_gen = self.k_heat * processed_gbps
        q_diss = self.k_cool * (temp - self.ambient_temp)
        return q_gen - q_diss

    def step_rk4(self, processed_gbps: float, dt_seconds: float) -> float:
        """
        Avanza la temperatura usando integración numérica Runge-Kutta de 4to Orden (RK4).
        Garantiza alta precisión y estabilidad numérica.
        """
        k1 = self.calculate_derivative(self.temperature, processed_gbps)
        k2 = self.calculate_derivative(self.temperature + 0.5 * dt_seconds * k1, processed_gbps)
        k3 = self.calculate_derivative(self.temperature + 0.5 * dt_seconds * k2, processed_gbps)
        k4 = self.calculate_derivative(self.temperature + dt_seconds * k3, processed_gbps)
        
        self.temperature += (dt_seconds / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return self.temperature


class ServerCluster:
    """
    Representa el clúster de servidores de alto rendimiento del centro de datos.
    Gestiona el estrangulamiento térmico (thermal throttling) y la eficiencia de procesamiento.
    """
    def __init__(
        self,
        target_temp_c: float = 70.0,
        normal_efficiency: float = 0.90,
        throttling_penalty_rate: float = 0.06,
        min_efficiency: float = 0.20
    ):
        self.target_temp_c = target_temp_c
        self.normal_efficiency = normal_efficiency
        self.throttling_penalty_rate = throttling_penalty_rate
        self.min_efficiency = min_efficiency
        
        self.is_throttled: bool = False
        self.current_efficiency: float = normal_efficiency

    def evaluate_efficiency(self, current_temperature: float) -> float:
        """
        Determina la eficiencia de procesamiento según la temperatura del servidor.
        Si T <= 70°C, opera al 90% (0.90).
        Si T > 70°C, se activa estrangulamiento térmico reduciendo drásticamente la capacidad.
        """
        if current_temperature <= self.target_temp_c:
            self.is_throttled = False
            self.current_efficiency = self.normal_efficiency
        else:
            self.is_throttled = True
            excess_temp = current_temperature - self.target_temp_c
            degraded_eff = self.normal_efficiency - (self.throttling_penalty_rate * excess_temp)
            self.current_efficiency = max(self.min_efficiency, degraded_eff)

        return self.current_efficiency

    def process_traffic(self, incoming_gbps: float, current_temperature: float) -> Tuple[float, float, bool]:
        """
        Procesa el flujo de red entrante.
        Retorna: (throughput_procesado_gbps, eficiencia_actual, esta_estrangulado)
        """
        efficiency = self.evaluate_efficiency(current_temperature)
        processed_gbps = incoming_gbps * efficiency
        return processed_gbps, efficiency, self.is_throttled
