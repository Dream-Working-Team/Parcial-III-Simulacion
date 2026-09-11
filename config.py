"""
==============================================================================
MÓDULO DE CONFIGURACIÓN GLOBAL
==============================================================================
Carga de variables de entorno (.env) y parámetros predeterminados para las
simulaciones de eventos discretos, continua, visualización e inteligencia artificial.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar automáticamente las variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)


class AIConfig:
    """Configuración del servicio de Inteligencia Artificial."""
    PROVIDER: str = os.getenv("AI_PROVIDER", "gemini").lower().strip()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3").strip()
    TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.3"))
    MAX_TOKENS: int = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "1024"))


class DiscreteSimConfig:
    """
    Parámetros para el Problema 1: Simulación de Eventos Discretos.
    Fábrica de ensamblaje de laptops con inventario crítico de procesadores.
    """
    DEFAULT_HOURS: float = 8.0              # Turno de trabajo por defecto (horas)
    ARRIVAL_RATE_HOURLY: float = 10.0       # Tasa promedio Poisson (órdenes por hora)
    SERVICE_TIME_MEAN_MIN: float = 5.0      # Media exponencial de ensamblaje (minutos)
    INITIAL_STOCK: int = 25                 # Inventario inicial de procesadores
    REORDER_THRESHOLD: int = 10             # Umbral crítico de reabastecimiento (< 10)
    REORDER_BATCH_SIZE: int = 50            # Lote de entrega del proveedor
    RESTOCK_LEAD_TIME_MIN: float = 15.0     # Tiempo de entrega del proveedor (minutos)


class ContinuousSimConfig:
    """
    Parámetros para el Problema 2: Simulación Continua.
    Clúster de servidores de alto rendimiento con balance térmico y estrangulamiento.
    """
    DEFAULT_HOURS: float = 24.0             # Duración por defecto (horas)
    DT_SECONDS: float = 2.0                 # Paso de integración numérica (segundos)
    TRAFFIC_MEAN_GBPS: float = 3.0          # Media de tráfico entrante (Gbps)
    TRAFFIC_STD_GBPS: float = 1.0           # Desviación estándar (Gbps)
    TRAFFIC_MIN_GBPS: float = 1.0           # Límite inferior de demanda (Gbps)
    TRAFFIC_MAX_GBPS: float = 5.0           # Límite superior de demanda (Gbps)
    
    TARGET_TEMP_C: float = 70.0             # Temperatura operativa nominal (°C)
    AMBIENT_TEMP_C: float = 25.0            # Temperatura del refrigerante líquido (°C)
    COOLING_COEFFICIENT: float = 0.08       # Tasa de disipación de calor por minuto (k_cool)
    # Calibración: en equilibrio a 3 Gbps: Heat = Cool -> k_heat * 3.0 = 0.08 * (70 - 25) = 3.6 -> k_heat = 1.2
    HEAT_COEFFICIENT: float = 1.2           # Generación de calor por Gbps por minuto (k_heat)
    
    NORMAL_EFFICIENCY: float = 0.90         # Eficiencia cuando T <= 70°C (90%)
    THROTTLING_RATE: float = 0.06           # Reducción de eficiencia por cada °C sobre 70°C
    MIN_EFFICIENCY: float = 0.20            # Eficiencia mínima bajo estrangulamiento severo


class GUIConfig:
    """Configuración de la ventana y visualización en Pygame."""
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 750
    FPS: int = 60
    TITLE: str = "Simulación Avanzada POO - Métodos Cuantitativos (Parcial III)"
