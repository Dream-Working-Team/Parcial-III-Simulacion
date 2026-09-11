"""
==============================================================================
PROVEEDOR ANALISTA EXPERTO OFFLINE (FALLBACK HEURÍSTICO)
==============================================================================
Motor analítico cuantitativo que opera de forma 100% autónoma y offline.
Garantiza que el sistema siempre genere conclusiones y recomendaciones técnicas
incluso si se agota la cuota de la API o no hay conexión a internet durante la defensa.
"""

from typing import Dict, Any, List
from .base import BaseAIProvider


class FallbackExpertProvider(BaseAIProvider):
    """
    Analista cuantitativo offline basado en reglas formales de simulación.
    """

    def generate_analysis(
        self,
        problem_type: str,
        metrics: Dict[str, Any],
        trace_samples: List[str]
    ) -> str:
        if problem_type == "discrete":
            return self._analyze_discrete(metrics)
        else:
            return self._analyze_continuous(metrics)

    def _analyze_discrete(self, m: Dict[str, Any]) -> str:
        stops = m.get("paradas_linea_por_falta_stock", 0)
        avg_wait = m.get("tiempo_espera_promedio_min", 0.0)
        util = m.get("utilizacion_estacion_ensamblaje_pct", 0.0)
        eff = m.get("eficiencia_reabastecimiento_pct", 100.0)
        delayed = m.get("ordenes_retrasadas_por_stock", 0)

        diag = (
            f"La estación de ensamblaje operó con una utilización del {util}%. "
            f"El tiempo promedio de espera en cola fue de {avg_wait} minutos. "
        )
        if stops > 0:
            diag += (
                f"Se registraron {stops} eventos de detención total de la línea debido al agotamiento de procesadores, "
                f"retrasando {delayed} órdenes de producción ({100.0 - eff:.1f}% del total)."
            )
        else:
            diag += "No se presentaron paradas de línea; la política de inventario mantuvo disponibilidad ininterrumpida."

        reab = (
            f"La eficiencia de reabastecimiento alcanzó el {eff}%. "
            f"El umbral crítico de 10 procesadores frente a un tiempo de entrega de 15 minutos del proveedor "
            f"{'resultó insuficiente durante ráfagas de llegada.' if stops > 0 else 'fue suficiente para amortiguar la demanda.'}"
        )

        conclusion = (
            f"El sistema presenta {'vulnerabilidad logística crítica que afecta el throughput de producción' if stops > 0 else 'un comportamiento estable y equilibrado'}. "
            f"La tasa de arribo Poisson de 10 ord/h demanda una sincronización más precisa con el ciclo de reposición."
        )

        recs = [
            f"1. Incrementar el punto de reorden (ROP) de 10 a {max(15, int(stops * 3 + 12))} unidades para absorber el Lead Time de 15 min.",
            "2. Negociar con el proveedor una reducción del tiempo de entrega de 15 a 8-10 minutos o entregas fraccionadas JIT.",
            "3. Implementar una política de stock de seguridad dinámico que anticipe colas crecientes antes de alcanzar el umbral."
        ]

        return (
            "=== INFORME DE ANÁLISIS AUTOMATIZADO (MOTOR CUANTITATIVO) ===\n\n"
            "1. DIAGNÓSTICO DEL SISTEMA:\n" + diag + "\n\n"
            "2. EFICIENCIA DE REABASTECIMIENTO:\n" + reab + "\n\n"
            "3. CONCLUSIÓN:\n" + conclusion + "\n\n"
            "4. RECOMENDACIONES TÉCNICAS:\n" + "\n".join(recs)
        )

    def _analyze_continuous(self, m: Dict[str, Any]) -> str:
        avg_temp = m.get("temperatura_promedio_c", 70.0)
        max_temp = m.get("temperatura_maxima_c", 70.0)
        throttled_pct = m.get("porcentaje_tiempo_estrangulado", 0.0)
        eff_red = m.get("eficiencia_global_red_pct", 90.0)
        tb_proc = m.get("total_datos_procesados_tb", 0.0)
        tb_lost = m.get("perdida_o_rechazo_tb", 0.0)

        diag = (
            f"El clúster procesó {tb_proc} TB con una eficiencia global de red del {eff_red}%. "
            f"La temperatura media se situó en {avg_temp}°C con picos térmicos de hasta {max_temp}°C. "
            f"El sistema permaneció bajo estrangulamiento térmico durante el {throttled_pct}% del tiempo simulado."
        )

        impacto = (
            f"El estrangulamiento térmico generó un déficit de procesamiento de {tb_lost} TB. "
            f"Durante las ráfagas superiores a 3.5 Gbps, la generación de calor superó la capacidad de absorción "
            f"del sistema de refrigeración líquida."
        )

        conclusion = (
            f"La operación continua {'presenta riesgo térmico moderado a alto, degradando el SLA de red' if throttled_pct > 10 else 'es técnicamente viable con estabilidad aceptable'}. "
            f"La temperatura de 70°C actúa como un cuello de botella térmico activo bajo la carga actual."
        )

        recs = [
            "1. Elevar el caudal del sistema de refrigeración líquida para aumentar el coeficiente de disipación k_cool en un 25%.",
            "2. Configurar balanceo de carga predictivo (Traffic Shaping) que restrinja picos sostenidos de tráfico por encima de 4.0 Gbps.",
            "3. Reducir la temperatura ambiente del líquido refrigerante a 20°C para ampliar el gradiente térmico de enfriamiento."
        ]

        return (
            "=== INFORME DE ANÁLISIS AUTOMATIZADO (MOTOR CUANTITATIVO) ===\n\n"
            "1. EVALUACIÓN DE ESTABILIDAD TÉRMICA:\n" + diag + "\n\n"
            "2. IMPACTO EN THROUGHPUT:\n" + impacto + "\n\n"
            "3. CONCLUSIÓN:\n" + conclusion + "\n\n"
            "4. RECOMENDACIONES DE INGENIERÍA:\n" + "\n".join(recs)
        )
