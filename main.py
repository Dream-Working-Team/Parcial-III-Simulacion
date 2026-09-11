"""
==============================================================================
UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA
ESCUELA DE INGENIERÍA EN COMPUTACIÓN - MÉTODOS CUANTITATIVOS
PARCIAL III: TRABAJO PRÁCTICO DE SIMULACIÓN Y ANÁLISIS CON IA
==============================================================================
Punto de entrada principal con menú interactivo por consola.
Permite ejecutar el Problema 1 (Eventos Discretos), el Problema 2 (Simulación Continua),
el Módulo Bonus en Pygame y la generación automatizada de reportes con IA.
"""

import sys
import os
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import DiscreteSimConfig, ContinuousSimConfig, AIConfig
from core.validator import InputValidator
from core.logger import SimulationLogger
from simulation_discrete.engine import DiscreteEventSimulator
from simulation_continuous.engine import ContinuousSimulator
from ai_service.factory import AIFactory
from reports.reporter import SimulationReporter


def print_banner():
    """Imprime el encabezado oficial del examen."""
    print("\n" + "=" * 78)
    print("  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA")
    print("  SIMULACIÓN DE SISTEMAS (MÉTODOS CUANTITATIVOS) - PARCIAL III")
    print("  Stack: Python (POO) + Integración con IA + Visualización en Pygame")
    print("=" * 78)


def print_menu():
    """Muestra las opciones del menú principal."""
    print("\nMENÚ PRINCIPAL DE OPCIONES:")
    print("  [1] Problema 1: Simulación de Eventos Discretos (Fábrica de Laptops) + IA")
    print("  [2] Problema 2: Simulación Continua (Clúster Térmico de Servidores) + IA")
    print("  [3] Pregunta Bonus: Animación Gráfica Interactiva en Pygame (2 Puntos)")
    print("  [4] Diagnóstico y Prueba de Conexión de API de IA")
    print("  [5] Explorar Historial de Reportes y Trazas Generadas")
    print("  [6] Salir del Programa")
    print("-" * 78)


def execute_discrete_simulation():
    """Ejecuta el Problema 1: Eventos Discretos."""
    print("\n" + "=" * 78)
    print("  EJECUTANDO PROBLEMA 1: SIMULACIÓN DE EVENTOS DISCRETOS")
    print("  Fábrica de Laptops - Ensamble con Inventario Crítico de Procesadores")
    print("=" * 78)

    # 1. Captura de parámetros con valores por defecto (Pautas de Evaluación)
    print("\n[CONFIGURACIÓN DE PARÁMETROS] (Presione Enter para tomar datos de prueba):")
    hours = InputValidator.prompt_float("Duración de la simulación en horas", default=DiscreteSimConfig.DEFAULT_HOURS, min_val=0.5, max_val=168.0)
    arrival_rate = InputValidator.prompt_float("Tasa de llegada Poisson (órdenes/hora)", default=DiscreteSimConfig.ARRIVAL_RATE_HOURLY, min_val=1.0)
    service_mean = InputValidator.prompt_float("Tiempo medio de ensamble Exponencial (minutos)", default=DiscreteSimConfig.SERVICE_TIME_MEAN_MIN, min_val=0.5)
    initial_stock = InputValidator.prompt_int("Stock inicial de procesadores", default=DiscreteSimConfig.INITIAL_STOCK, min_val=1)

    print("\n  [INICIANDO MOTOR] Ejecutando simulación de eventos discretos...")
    logger = SimulationLogger("Problema_1_Discreto", print_to_console=False)
    sim = DiscreteEventSimulator(
        duration_hours=hours,
        arrival_rate_hourly=arrival_rate,
        service_mean_minutes=service_mean,
        initial_stock=initial_stock,
        reorder_threshold=DiscreteSimConfig.REORDER_THRESHOLD,
        batch_size=DiscreteSimConfig.REORDER_BATCH_SIZE,
        lead_time_minutes=DiscreteSimConfig.RESTOCK_LEAD_TIME_MIN,
        logger=logger
    )

    metrics = sim.run_until_completion()

    # 2. Despliegue de métricas en consola
    print("\n" + "-" * 78)
    print("  RESULTADOS Y MÉTRICAS DE OPERACIÓN (FÁBRICA DE LAPTOPS):")
    print("-" * 78)
    print(f"  • Tiempo simulado:                        {metrics['duracion_simulacion_horas']} horas ({metrics['duracion_simulacion_minutos']} min)")
    print(f"  • Total órdenes recibidas:                {metrics['total_ordenes_recibidas']}")
    print(f"  • Total órdenes completadas y despachadas: {metrics['total_ordenes_completadas']}")
    print(f"  • Órdenes en cola final:                  {metrics['ordenes_en_cola_final']}")
    print(f"  • Tiempo de espera promedio:              {metrics['tiempo_espera_promedio_min']} minutos")
    print(f"  • Tiempo de espera máximo:                {metrics['tiempo_espera_maximo_min']} minutos")
    print(f"  • Tiempo total en sistema promedio:       {metrics['tiempo_sistema_promedio_min']} minutos")
    print(f"  • Tiempo promedio de despacho por lote:   {metrics['tiempo_despacho_lote_promedio_min']} minutos")
    print(f"  • Paradas de línea por falta de stock:    {metrics['paradas_linea_por_falta_stock']} veces")
    print(f"  • Tiempo total de línea detenida:         {metrics['tiempo_total_linea_detenida_min']} min ({metrics['porcentaje_tiempo_linea_detenida']}%)")
    print(f"  • Utilización de la estación de ensamble: {metrics['utilizacion_estacion_ensamblaje_pct']}%")
    print(f"  • Órdenes retrasadas por falta de CPU:    {metrics['ordenes_retrasadas_por_stock']} ({metrics['porcentaje_ordenes_retrasadas']}%)")
    print(f"  • Eficiencia en el reabastecimiento:      {metrics['eficiencia_reabastecimiento_pct']}%")
    print(f"  • Lotes recibidos del proveedor (+50):    {metrics['total_lotes_recibidos']}")
    print(f"  • Stock final de procesadores:            {metrics['stock_final_procesadores']} unidades")
    print("-" * 78)

    # 3. Consulta automatizada a la API de Inteligencia Artificial
    print("\n  [CONECTANDO CON IA] Enviando métricas y trazas para análisis automatizado...")
    ai_provider = AIFactory.get_provider()
    trace_samples = logger.get_sample_traces(max_items=30)
    ai_conclusion = ai_provider.generate_analysis("discrete", metrics, trace_samples)

    print("\n" + "=" * 78)
    print("  CONCLUSIÓN Y RECOMENDACIÓN AUTOMATIZADA (IA):")
    print("=" * 78)
    print(ai_conclusion)
    print("=" * 78)

    # 4. Guardado en archivos de texto
    reporter = SimulationReporter()
    report_file = reporter.save_discrete_report(metrics, ai_conclusion, logger.get_traces_as_strings())
    print(f"\n  [REPORTE GUARDADO] Archivo generado exitosamente en:\n  -> {report_file.resolve()}")


def execute_continuous_simulation():
    """Ejecuta el Problema 2: Simulación Continua."""
    print("\n" + "=" * 78)
    print("  EJECUTANDO PROBLEMA 2: SIMULACIÓN CONTINUA (BALANCE TÉRMICO EDO)")
    print("  Clúster de Servidores - Rendimiento y Estrangulamiento Térmico (70°C)")
    print("=" * 78)

    # 1. Captura de parámetros con valores por defecto
    print("\n[CONFIGURACIÓN DE PARÁMETROS] (Presione Enter para tomar datos de prueba):")
    hours = InputValidator.prompt_float("Duración de la simulación en horas", default=ContinuousSimConfig.DEFAULT_HOURS, min_val=1.0, max_val=720.0)
    traffic_mean = InputValidator.prompt_float("Media del tráfico entrante (Gbps)", default=ContinuousSimConfig.TRAFFIC_MEAN_GBPS, min_val=1.0, max_val=5.0)
    traffic_std = InputValidator.prompt_float("Desviación estándar del tráfico (Gbps)", default=ContinuousSimConfig.TRAFFIC_STD_GBPS, min_val=0.1, max_val=2.0)
    target_temp = InputValidator.prompt_float("Temperatura límite operativa nominal (°C)", default=ContinuousSimConfig.TARGET_TEMP_C, min_val=40.0, max_val=95.0)

    print("\n  [INICIANDO MOTOR CONTINUO] Resolviendo ecuaciones diferenciales (Runge-Kutta 4)...")
    logger = SimulationLogger("Problema_2_Continuo", print_to_console=False)
    sim = ContinuousSimulator(
        duration_hours=hours,
        dt_seconds=ContinuousSimConfig.DT_SECONDS,
        mean_traffic_gbps=traffic_mean,
        std_traffic_gbps=traffic_std,
        target_temp_c=target_temp,
        ambient_temp_c=ContinuousSimConfig.AMBIENT_TEMP_C,
        logger=logger
    )

    metrics = sim.run_until_completion()

    # 2. Despliegue de métricas en consola
    print("\n" + "-" * 78)
    print("  RESULTADOS Y MÉTRICAS DE OPERACIÓN (CLÚSTER TÉRMICO):")
    print("-" * 78)
    print(f"  • Tiempo simulado:                        {metrics['duracion_simulacion_horas']} horas")
    print(f"  • Total tráfico entrante recibido:        {metrics['total_trafico_entrante_tb']} Terabytes")
    print(f"  • Total datos procesados (Throughput):    {metrics['total_datos_procesados_tb']} Terabytes")
    print(f"  • Datos degradados o retrasados:          {metrics['perdida_o_rechazo_tb']} Terabytes")
    print(f"  • Eficiencia global de la red:            {metrics['eficiencia_global_red_pct']}%")
    print(f"  • Temperatura promedio del servidor:      {metrics['temperatura_promedio_c']} °C")
    print(f"  • Desviación estándar térmica:            {metrics['temperatura_desviacion_estandar_c']} °C")
    print(f"  • Rango de temperatura:                   [{metrics['temperatura_minima_c']} °C - {metrics['temperatura_maxima_c']} °C]")
    print(f"  • Activaciones de Thermal Throttling:     {metrics['eventos_estrangulamiento_termico']} ciclos")
    print(f"  • Tiempo acumulado en estrangulamiento:   {metrics['tiempo_en_estrangulamiento_min']} min ({metrics['porcentaje_tiempo_estrangulado']}%)")
    print(f"  • Viabilidad de operación continua:       {metrics['diagnostico_viabilidad_operativa']}")
    print("-" * 78)

    # 3. Consulta automatizada a la API de Inteligencia Artificial
    print("\n  [CONECTANDO CON IA] Enviando métricas y trazas para análisis automatizado...")
    ai_provider = AIFactory.get_provider()
    trace_samples = logger.get_sample_traces(max_items=30)
    ai_conclusion = ai_provider.generate_analysis("continuous", metrics, trace_samples)

    print("\n" + "=" * 78)
    print("  CONCLUSIÓN Y RECOMENDACIÓN AUTOMATIZADA (IA):")
    print("=" * 78)
    print(ai_conclusion)
    print("=" * 78)

    # 4. Guardado en archivos de texto
    reporter = SimulationReporter()
    report_file = reporter.save_continuous_report(metrics, ai_conclusion, logger.get_traces_as_strings())
    print(f"\n  [REPORTE GUARDADO] Archivo generado exitosamente en:\n  -> {report_file.resolve()}")


def execute_pygame_animation():
    """Ejecuta el Módulo Bonus de Animación en Pygame."""
    print("\n" + "=" * 78)
    print("  PREGUNTA BONUS (2 PUNTOS): ANIMACIÓN GRÁFICA INTERACTIVA EN PYGAME")
    print("=" * 78)
    print("  Abriendo ventana interactiva de simulación...")
    print("  Controles en la ventana de Pygame:")
    print("    • [ESPACIO]: Pausar o reanudar animación")
    print("    • [TAB]:     Alternar entre Problema 1 (Fábrica) y Problema 2 (Clúster)")
    print("    • [1 - 5]:   Ajustar velocidad de simulación (1x a 150x)")
    print("    • [R]:       Reiniciar simulación activa")
    print("    • [ESC]:     Cerrar animación y regresar a este menú de consola")
    print("-" * 78)

    try:
        from visualization.visualizer import SimulationVisualizer
        vis = SimulationVisualizer()
        vis.run(initial_mode="discrete")
        print("\n  [PYGAME] Ventana gráfica cerrada correctamente.")
    except Exception as e:
        print(f"\n  [ERROR AL INICIAR PYGAME]: {str(e)}")


def test_ai_connection():
    """Prueba la conectividad del proveedor de IA activo."""
    print("\n" + "=" * 78)
    print("  DIAGNÓSTICO DE CONEXIÓN DE INTELIGENCIA ARTIFICIAL")
    print("=" * 78)
    print(f"  Proveedor configurado en .env: {AIConfig.PROVIDER}")
    print(f"  Modelo Gemini configurado:     {AIConfig.GEMINI_MODEL}")
    print(f"  API Key presente:              {'Sí (Configurada)' if AIConfig.GEMINI_API_KEY else 'No (Modo Offline activo)'}")
    print("-" * 78)
    print("  Enviando consulta de prueba...")

    provider = AIFactory.get_provider()
    dummy_metrics = {"tiempo_espera_promedio_min": 5.2, "paradas_linea_por_falta_stock": 1, "eficiencia_reabastecimiento_pct": 94.0}
    dummy_traces = ["[00:01:00] [TEST] Prueba de comunicación con el modelo"]

    try:
        res = provider.generate_analysis("discrete", dummy_metrics, dummy_traces)
        print("\n  [ESTADO: CONEXIÓN EXITOSA]")
        print("  Respuesta obtenida del modelo:\n")
        print(res[:350] + "\n  [... texto completo recibido correctamente ...]")
    except Exception as e:
        print(f"\n  [ERROR DE CONEXIÓN]: {str(e)}")


def browse_reports():
    """Muestra el historial de reportes generados en disco."""
    output_dir = SimulationReporter.OUTPUT_DIR
    files = list(output_dir.glob("*.txt"))
    print("\n" + "=" * 78)
    print(f"  HISTORIAL DE REPORTES Y TRAZAS EN DISCO ({output_dir})")
    print("=" * 78)
    if not files:
        print("  No hay reportes generados aún. Ejecute el Problema 1 o 2 para generarlos.")
        return

    for idx, f in enumerate(sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:15], start=1):
        size_kb = f.stat().st_size / 1024.0
        print(f"  [{idx:02d}] {f.name} ({size_kb:.1f} KB)")


def main():
    """Bucle principal de la aplicación."""
    print_banner()
    while True:
        print_menu()
        choice = InputValidator.prompt_choice("Seleccione una opción", ["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            execute_discrete_simulation()
        elif choice == "2":
            execute_continuous_simulation()
        elif choice == "3":
            execute_pygame_animation()
        elif choice == "4":
            test_ai_connection()
        elif choice == "5":
            browse_reports()
        elif choice == "6":
            print("\n  ¡Gracias por utilizar el Simulador de Métodos Cuantitativos! Saliendo...\n")
            break

        input("\nPresione [Enter] para volver al Menú Principal...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Programa interrumpido por el usuario. Saliendo limpiamente...")
        sys.exit(0)
