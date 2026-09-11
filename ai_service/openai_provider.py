"""
==============================================================================
CONECTOR DE OPENAI (REST API)
==============================================================================
Implementación para OpenAI ChatGPT (gpt-4o-mini, gpt-3.5-turbo, etc.).
"""

import requests
import json
from typing import Dict, Any, List
from .base import BaseAIProvider
from .prompts import AIPromptBuilder
from config import AIConfig


class OpenAIProvider(BaseAIProvider):
    """Proveedor para la API de OpenAI."""

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key or AIConfig.OPENAI_API_KEY
        self.model = model or AIConfig.OPENAI_MODEL or "gpt-4o-mini"
        self.temperature = AIConfig.TEMPERATURE
        self.max_tokens = AIConfig.MAX_TOKENS

    def generate_analysis(
        self,
        problem_type: str,
        metrics: Dict[str, Any],
        trace_samples: List[str]
    ) -> str:
        """Envía la solicitud a la API de OpenAI."""
        if not self.api_key:
            raise ValueError("No se ha configurado la OPENAI_API_KEY en el archivo .env")

        if problem_type == "discrete":
            user_prompt = AIPromptBuilder.build_discrete_prompt(metrics, trace_samples)
        else:
            user_prompt = AIPromptBuilder.build_continuous_prompt(metrics, trace_samples)

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": AIPromptBuilder.SYSTEM_ROLE},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error de comunicación con la API de OpenAI: {str(e)}")
