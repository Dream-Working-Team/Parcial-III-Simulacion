"""
==============================================================================
GENERADOR DE REPORTES Y VOLCADO A DISCO
==============================================================================
Clase POO encargada de compilar las métricas, trazas y conclusiones de la IA,
formatearlas estéticamente y guardarlas en archivos de texto (.txt) según
las pautas de evaluación del parcial.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class SimulationReporter:
    """Generador y gestor de reportes de salida."""

    OUTPUT_DIR = Path(__file__).resolve().parent / "output"

    def __init__(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def save_discrete_report(
        self,
        metrics: Dict[str, Any],
        ai_analysis: str,
        traces: List[str]
    ) -> Path:
        """Guarda el informe consolidado y trazas del Problema 1."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.OUTPUT_DIR / f"reporte_problema_1_discreto_{timestamp_str}.txt"
        trace_path = self.OUTPUT_DIR / f"trazas_problema_1_discreto_{timestamp_str}.txt"

        # 1. Guardar trazas completas
        with open(trace_path, "w", encoding="utf-8") as f_trace:
            f_trace.write("=" * 80 + "\n")
            f_trace.write("TRAZAS DE SIMULACIÓN - PROBLEMA 1: FÁBRICA DE LAPTOPS (EVENTOS DISCRETOS)\n")
            f_trace.write(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f_trace.write("=" * 80 + "\n\n")
            for t in traces:
                f_trace.write(f"{t}\n")

        # 2. Guardar reporte ejecutivo con análisis IA
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE OFICIAL DE SIMULACIÓN - PARCIAL III\n")
            f.write("PROBLEMA 1: SIMULACIÓN DE EVENTOS DISCRETOS (FÁBRICA DE LAPTOPS)\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. PARÁMETROS DEL SISTEMA:\n")
            f.write("  - Tasa de llegada Poisson: 10 órdenes / hora (1 cada 6 minutos promedio)\n")
            f.write("  - Tiempo de ensamble Exponencial: 5 minutos / laptop\n")
            f.write("  - Política de inventario: Reorden cuando stock < 10 procesadores\n")
            f.write("  - Tamaño de lote del proveedor: 50 procesadores\n")
            f.write("  - Tiempo de entrega proveedor (Lead Time): 15 minutos\n\n")

            f.write("2. RESULTADOS CUANTITATIVOS Y MÉTRICAS CLAVE:\n")
            f.write(f"  - Duración de simulación: {metrics.get('duracion_simulacion_horas')} horas ({metrics.get('duracion_simulacion_minutos')} min)\n")
            f.write(f"  - Total órdenes recibidas: {metrics.get('total_ordenes_recibidas')}\n")
            f.write(f"  - Total órdenes ensambladas y despachadas: {metrics.get('total_ordenes_completadas')}\n")
            f.write(f"  - Órdenes remanentes en cola: {metrics.get('ordenes_en_cola_final')}\n")
            f.write(f"  - Tiempo promedio de espera en cola: {metrics.get('tiempo_espera_promedio_min')} minutos\n")
            f.write(f"  - Tiempo máximo de espera en cola: {metrics.get('tiempo_espera_maximo_min')} minutos\n")
            f.write(f"  - Tiempo total promedio en sistema (Espera + Servicio): {metrics.get('tiempo_sistema_promedio_min')} minutos\n")
            f.write(f"  - Tiempo promedio para despachar un lote de 50 laptops: {metrics.get('tiempo_despacho_lote_promedio_min')} minutos\n")
            f.write(f"  - Número de veces que la línea se detuvo por falta de stock: {metrics.get('paradas_linea_por_falta_stock')}\n")
            f.write(f"  - Tiempo total que la línea estuvo detenida: {metrics.get('tiempo_total_linea_detenida_min')} min ({metrics.get('porcentaje_tiempo_linea_detenida')} %)\n")
            f.write(f"  - Utilización de la estación de ensamble: {metrics.get('utilizacion_estacion_ensamblaje_pct')} %\n")
            f.write(f"  - Cantidad de órdenes retrasadas por falta de procesador: {metrics.get('ordenes_retrasadas_por_stock')} ({metrics.get('porcentaje_ordenes_retrasadas')} %)\n")
            f.write(f"  - Eficiencia en el reabastecimiento: {metrics.get('eficiencia_reabastecimiento_pct')} %\n")
            f.write(f"  - Reórdenes automáticas emitidas: {metrics.get('total_reordenes_emitidas')}\n")
            f.write(f"  - Lotes de 50 CPUs recibidos: {metrics.get('total_lotes_recibidos')}\n")
            f.write(f"  - Stock final en almacén: {metrics.get('stock_final_procesadores')} unidades\n\n")

            f.write("3. CONCLUSIONES Y RECOMENDACIONES DE LA INTELIGENCIA ARTIFICIAL:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{ai_analysis}\n")
            f.write("-" * 80 + "\n\n")

            f.write(f"Archivo de trazas completas asociado: {trace_path.name}\n")

        return report_path

    def save_continuous_report(
        self,
        metrics: Dict[str, Any],
        ai_analysis: str,
        traces: List[str]
    ) -> Path:
        """Guarda el informe consolidado y trazas del Problema 2."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.OUTPUT_DIR / f"reporte_problema_2_continuo_{timestamp_str}.txt"
        trace_path = self.OUTPUT_DIR / f"trazas_problema_2_continuo_{timestamp_str}.txt"

        # 1. Guardar trazas completas
        with open(trace_path, "w", encoding="utf-8") as f_trace:
            f_trace.write("=" * 80 + "\n")
            f_trace.write("TRAZAS DE SIMULACIÓN - PROBLEMA 2: CLÚSTER DE SERVIDORES (SIMULACIÓN CONTINUA)\n")
            f_trace.write(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f_trace.write("=" * 80 + "\n\n")
            for t in traces:
                f_trace.write(f"{t}\n")

        # 2. Guardar reporte ejecutivo con análisis IA
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE OFICIAL DE SIMULACIÓN - PARCIAL III\n")
            f.write("PROBLEMA 2: SIMULACIÓN CONTINUA (PROCESO TÉRMICO Y RENDIMIENTO)\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. PARÁMETROS DEL MODELO CONTINUO:\n")
            f.write("  - Tasa de entrada de tráfico: Normal(media=3 Gbps, std=1 Gbps), acotada en [1, 5] Gbps\n")
            f.write("  - Temperatura operativa nominal: 70°C (Eficiencia del 90% a T <= 70°C)\n")
            f.write("  - Modelo térmico: EDO de primer orden (dT/dt = Q_gen - Q_diss) resuelta por Runge-Kutta 4\n")
            f.write("  - Estrangulamiento térmico (Thermal Throttling): Activación automática al superar 70°C\n\n")

            f.write("2. RESULTADOS CUANTITATIVOS Y MÉTRICAS CLAVE:\n")
            f.write(f"  - Duración de simulación continua: {metrics.get('duracion_simulacion_horas')} horas\n")
            f.write(f"  - Total tráfico entrante: {metrics.get('total_trafico_entrante_tb')} Terabytes\n")
            f.write(f"  - Total datos efectivamente procesados (Throughput): {metrics.get('total_datos_procesados_tb')} Terabytes\n")
            f.write(f"  - Tráfico no procesado o degradado: {metrics.get('perdida_o_rechazo_tb')} Terabytes\n")
            f.write(f"  - Eficiencia global de la red: {metrics.get('eficiencia_global_red_pct')} %\n")
            f.write(f"  - Temperatura promedio del clúster: {metrics.get('temperatura_promedio_c')} °C\n")
            f.write(f"  - Desviación estándar de temperatura: {metrics.get('temperatura_desviacion_estandar_c')} °C\n")
            f.write(f"  - Temperatura mínima registrada: {metrics.get('temperatura_minima_c')} °C\n")
            f.write(f"  - Temperatura máxima registrada: {metrics.get('temperatura_maxima_c')} °C\n")
            f.write(f"  - Eventos de activación de Thermal Throttling: {metrics.get('eventos_estrangulamiento_termico')}\n")
            f.write(f"  - Tiempo acumulado bajo estrangulamiento térmico: {metrics.get('tiempo_en_estrangulamiento_min')} min ({metrics.get('porcentaje_tiempo_estrangulado')} %)\n")
            f.write(f"  - Diagnóstico de viabilidad operativa continua: {metrics.get('diagnostico_viabilidad_operativa')}\n\n")

            f.write("3. CONCLUSIONES Y RECOMENDACIONES DE LA INTELIGENCIA ARTIFICIAL:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{ai_analysis}\n")
            f.write("-" * 80 + "\n\n")

            f.write(f"Archivo de trazas completas asociado: {trace_path.name}\n")

        return report_path
