"""
==============================================================================
PRUEBAS UNITARIAS Y DE INTEGRACIÓN (PYTEST)
==============================================================================
Verifica la corrección de los modelos de simulación de eventos discretos,
simulación continua EDO, cálculo de métricas e integración con IA.
"""

import pytest
from pathlib import Path
from simulation_discrete.engine import DiscreteEventSimulator
from simulation_continuous.engine import ContinuousSimulator
from ai_service.factory import AIFactory
from ai_service.fallback_provider import FallbackExpertProvider
from reports.reporter import SimulationReporter


def test_discrete_simulation_execution():
    """Prueba que la simulación de eventos discretos complete y calcule métricas requeridas."""
    sim = DiscreteEventSimulator(
        duration_hours=2.0,
        arrival_rate_hourly=10.0,
        service_mean_minutes=5.0,
        initial_stock=15,
        reorder_threshold=10,
        batch_size=50,
        lead_time_minutes=15.0,
        seed=42
    )
    metrics = sim.run_until_completion()

    assert metrics["duracion_simulacion_horas"] == 2.0
    assert metrics["total_ordenes_recibidas"] > 0
    assert metrics["total_ordenes_completadas"] > 0
    assert "tiempo_espera_promedio_min" in metrics
    assert "paradas_linea_por_falta_stock" in metrics
    assert "eficiencia_reabastecimiento_pct" in metrics
    assert metrics["eficiencia_reabastecimiento_pct"] >= 0.0


def test_continuous_simulation_execution():
    """Prueba que el integrador Runge-Kutta 4 resuelva el balance térmico y calcule TB."""
    sim = ContinuousSimulator(
        duration_hours=1.0,
        dt_seconds=2.0,
        mean_traffic_gbps=3.0,
        std_traffic_gbps=1.0,
        target_temp_c=70.0,
        ambient_temp_c=25.0,
        seed=42
    )
    metrics = sim.run_until_completion()

    assert metrics["duracion_simulacion_horas"] == 1.0
    assert metrics["total_trafico_entrante_tb"] > 0.0
    assert metrics["total_datos_procesados_tb"] > 0.0
    assert metrics["eficiencia_global_red_pct"] > 0.0
    assert 40.0 < metrics["temperatura_promedio_c"] < 95.0
    assert "eventos_estrangulamiento_termico" in metrics


def test_ai_fallback_expert_provider():
    """Verifica que el motor analista cuantitativo offline genere informes consistentes."""
    fallback = FallbackExpertProvider()
    
    # Prueba con métricas discretas
    dummy_discrete = {
        "tiempo_espera_promedio_min": 4.5,
        "paradas_linea_por_falta_stock": 2,
        "eficiencia_reabastecimiento_pct": 91.5,
        "utilizacion_estacion_ensamblaje_pct": 82.0
    }
    report_discrete = fallback.generate_analysis("discrete", dummy_discrete, [])
    assert "DIAGNÓSTICO DEL SISTEMA" in report_discrete
    assert "RECOMENDACIONES TÉCNICAS" in report_discrete

    # Prueba con métricas continuas
    dummy_cont = {
        "temperatura_promedio_c": 72.1,
        "temperatura_maxima_c": 76.5,
        "porcentaje_tiempo_estrangulado": 14.2,
        "eficiencia_global_red_pct": 86.4,
        "total_datos_procesados_tb": 12.5,
        "perdida_o_rechazo_tb": 1.2
    }
    report_cont = fallback.generate_analysis("continuous", dummy_cont, [])
    assert "EVALUACIÓN DE ESTABILIDAD TÉRMICA" in report_cont
    assert "RECOMENDACIONES DE INGENIERÍA" in report_cont


def test_simulation_reporter():
    """Verifica que el generador de reportes escriba correctamente en disco."""
    reporter = SimulationReporter()
    metrics = {
        "duracion_simulacion_horas": 1.0,
        "total_ordenes_recibidas": 10,
        "total_ordenes_completadas": 10,
        "tiempo_espera_promedio_min": 2.0
    }
    saved_path = reporter.save_discrete_report(metrics, "Análisis de prueba", ["[00:00:00] [INICIO] Inicio"])
    assert saved_path.exists()
    assert saved_path.stat().st_size > 0
