"""
==============================================================================
CONECTOR DE OLLAMA (LLM LOCAL)
==============================================================================
Implementación para ejecutar modelos de código abierto localmente (Llama 3, Mistral, etc.)
sin requerir conexión a internet ni claves de pago.
"""

import requests
import json
from typing import Dict, Any, List
from .base import BaseAIProvider
from .prompts import AIPromptBuilder
from config import AIConfig


class OllamaProvider(BaseAIProvider):
    """Proveedor para servidor local Ollama."""

    def __init__(self, host: str = "", model: str = ""):
        self.host = (host or AIConfig.OLLAMA_HOST or "http://localhost:11434").rstrip("/")
        self.model = model or AIConfig.OLLAMA_MODEL or "llama3"

    def generate_analysis(
        self,
        problem_type: str,
        metrics: Dict[str, Any],
        trace_samples: List[str]
    ) -> str:
        """Envía el prompt al daemon local de Ollama."""
        if problem_type == "discrete":
            user_prompt = AIPromptBuilder.build_discrete_prompt(metrics, trace_samples)
        else:
            user_prompt = AIPromptBuilder.build_continuous_prompt(metrics, trace_samples)

        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "system": AIPromptBuilder.SYSTEM_ROLE,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": AIConfig.TEMPERATURE,
                "num_predict": AIConfig.MAX_TOKENS
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"No se pudo conectar con Ollama en {self.host}: {str(e)}")
