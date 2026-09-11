"""
==============================================================================
PLANTILLAS Y PROMPTS PREDETERMINADOS (OPTIMIZADOS EN CONSUMO DE TOKENS)
==============================================================================
Estructuras de prompt compactas y de alta densidad semántica diseñadas para
minimizar el consumo de tokens de entrada/salida y maximizar la precisión analítica.
"""

import json
from typing import Dict, Any, List


class AIPromptBuilder:
    """Constructor de prompts compactos optimizados para modelos Flash."""

    SYSTEM_ROLE = (
        "Eres un ingeniero sénior experto en Métodos Cuantitativos, Investigación de Operaciones "
        "y Simulación de Sistemas (Eventos Discretos y Modelado Continuo de balance térmico). "
        "Tu objetivo es analizar métricas de simulación y entregar conclusiones y recomendaciones técnicas de alto impacto."
    )

    @staticmethod
    def build_discrete_prompt(metrics: Dict[str, Any], trace_samples: List[str]) -> str:
        """
        Genera un prompt altamente conciso para el Problema 1 (Fábrica de Laptops).
        """
        metrics_json = json.dumps(metrics, indent=2, ensure_ascii=False)
        traces_text = "\n".join(trace_samples[:15])

        prompt = f"""[CONTEXTO]: Simulación de Eventos Discretos de Fábrica de Laptops.
Llegadas Poisson (10 ord/h), servicio Exp (5 min), umbral crítico reorden < 10 procesadores, lote 50 uds, entrega 15 min.

[MÉTRICAS CLAVE OBTENIDAS]:
{metrics_json}

[MUESTRA REPRESENTATIVA DE TRAZAS]:
{traces_text}

[INSTRUCCIÓN ESTRICTA]:
Genera un análisis técnico breve y estructurado en el siguiente formato exacto (máximo 300 palabras para economizar tokens):
1. DIAGNÓSTICO DEL SISTEMA: (Evaluar tiempos de espera, cuello de botella en ensamblaje y paradas de línea por desabastecimiento).
2. EFICIENCIA DE REABASTECIMIENTO: (Analizar si el umbral de 10 unidades y lote de 50 es adecuado frente al Lead Time de 15 min).
3. CONCLUSIÓN: (Veredicto conciso sobre el rendimiento operativo de la fábrica).
4. RECOMENDACIONES TÉCNICAS: (3 acciones cuantitativas prioritarias para optimizar el inventario y eliminar paradas de línea).
"""
        return prompt.strip()

    @staticmethod
    def build_continuous_prompt(metrics: Dict[str, Any], trace_samples: List[str]) -> str:
        """
        Genera un prompt altamente conciso para el Problema 2 (Clúster Térmico).
        """
        metrics_json = json.dumps(metrics, indent=2, ensure_ascii=False)
        traces_text = "\n".join(trace_samples[:15])

        prompt = f"""[CONTEXTO]: Simulación Continua de Clúster de Servidores.
Tráfico entrante Normal(3, 1) Gbps [1-5 Gbps], balance térmico por EDO: dT/dt = k_heat*Traffic - k_cool*(T - T_amb).
Operación nominal a 70°C (eficiencia 90%). Si T > 70°C: se activa Thermal Throttling severo.

[MÉTRICAS CLAVE OBTENIDAS]:
{metrics_json}

[MUESTRA REPRESENTATIVA DE TRAZAS]:
{traces_text}

[INSTRUCCIÓN ESTRICTA]:
Genera un análisis técnico breve y estructurado en el siguiente formato exacto (máximo 300 palabras para economizar tokens):
1. EVALUACIÓN DE ESTABILIDAD TÉRMICA: (Analizar fluctuaciones de temperatura, picos máximos y disipación de calor).
2. IMPACTO EN THROUGHPUT (TB PROCESADOS): (Evaluar pérdida de datos o degradación causada por estrangulamiento térmico).
3. CONCLUSIÓN: (Dictamen claro sobre la viabilidad de operar el clúster de forma continua).
4. RECOMENDACIONES DE INGENIERÍA: (3 medidas para optimizar refrigeración líquida y mitigación de sobrecalentamiento).
"""
        return prompt.strip()
