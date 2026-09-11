"""
==============================================================================
CONECTOR DE GOOGLE GEMINI (REST API)
==============================================================================
Implementación del proveedor Gemini utilizando llamadas directas a la API REST v1beta.
Optimizado para modelos rápidos y eficientes como gemini-2.5-flash y gemini-1.5-flash.
"""

import requests
import json
from typing import Dict, Any, List
from .base import BaseAIProvider
from .prompts import AIPromptBuilder
from config import AIConfig


class GeminiProvider(BaseAIProvider):
    """Proveedor para la API oficial de Google Gemini."""

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key or AIConfig.GEMINI_API_KEY
        self.model = model or AIConfig.GEMINI_MODEL or "gemini-2.5-flash"
        self.temperature = AIConfig.TEMPERATURE
        self.max_tokens = AIConfig.MAX_TOKENS

    def generate_analysis(
        self,
        problem_type: str,
        metrics: Dict[str, Any],
        trace_samples: List[str]
    ) -> str:
        """Envía la solicitud a la API de Gemini."""
        if not self.api_key:
            raise ValueError("No se ha configurado la GEMINI_API_KEY en el archivo .env")

        if problem_type == "discrete":
            user_prompt = AIPromptBuilder.build_discrete_prompt(metrics, trace_samples)
        else:
            user_prompt = AIPromptBuilder.build_continuous_prompt(metrics, trace_samples)

        # Modelos compatibles ordenados por prioridad de disponibilidad
        candidate_models = []
        if self.model:
            candidate_models.append(self.model)
        for m in ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-pro", "gemini-pro-latest"]:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for model_name in candidate_models:
            clean_name = model_name.replace("models/", "")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_name}:generateContent?key={self.api_key}"
            payload = {
                "system_instruction": {
                    "parts": [{"text": AIPromptBuilder.SYSTEM_ROLE}]
                },
                "contents": [
                    {
                        "parts": [{"text": user_prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens
                }
            }

            try:
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=35
                )

                if response.status_code == 400 and "system_instruction" in response.text:
                    fallback_payload = {
                        "contents": [
                            {
                                "parts": [{"text": f"{AIPromptBuilder.SYSTEM_ROLE}\n\n{user_prompt}"}]
                            }
                        ],
                        "generationConfig": {
                            "temperature": self.temperature,
                            "maxOutputTokens": self.max_tokens
                        }
                    }
                    response = requests.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(fallback_payload),
                        timeout=35
                    )

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        # Buscar partes que contengan texto (ignorando firmas de pensamiento u otros metadatos)
                        text_parts = [p.get("text", "") for p in parts if "text" in p and p.get("text")]
                        if text_parts:
                            return "\n".join(text_parts).strip()
                    return "El modelo Gemini procesó la solicitud pero no retornó texto explícito."
                
                last_error = f"HTTP {response.status_code}: {response.text}"
            except requests.exceptions.RequestException as e:
                last_error = str(e)

        raise RuntimeError(f"Error de comunicación con la API de Gemini ({last_error})")
