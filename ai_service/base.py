"""
==============================================================================
INTERFAZ BASE PARA PROVEEDORES DE INTELIGENCIA ARTIFICIAL
==============================================================================
Contrato POO abstracto que deben implementar los conectores de IA.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAIProvider(ABC):
    """Interfaz abstracta para conectores de servicios LLM."""

    @abstractmethod
    def generate_analysis(
        self,
        problem_type: str,
        metrics: Dict[str, Any],
        trace_samples: List[str]
    ) -> str:
        """
        Envía las métricas y trazas a la API de IA para obtener el análisis automatizado.
        problem_type: 'discrete' o 'continuous'
        """
        pass
