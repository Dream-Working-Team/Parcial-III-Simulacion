"""
==============================================================================
FÁBRICA DE PROVEEDORES DE IA (FACTORY PATTERN)
==============================================================================
Instanciación desacoplada del proveedor de Inteligencia Artificial según
la configuración activa en .env, con tolerancia a fallos y fallback automático.
"""

from typing import Optional
from config import AIConfig
from .base import BaseAIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .fallback_provider import FallbackExpertProvider


class RobustAIWrapper(BaseAIProvider):
    """
    Envoltura de alta resiliencia. Intenta consultar el proveedor remoto (Gemini / OpenAI / Ollama);
    si este falla temporalmente por saturación de cuota (503), error de red o timeout,
    genera de inmediato el informe con el motor analista cuantitativo offline sin interrumpir al usuario.
    """
    def __init__(self, primary_provider: BaseAIProvider, fallback_provider: BaseAIProvider):
        self.primary = primary_provider
        self.fallback = fallback_provider

    def generate_analysis(
        self,
        problem_type: str,
        metrics: Dict[str, Any],
        trace_samples: List[str]
    ) -> str:
        try:
            return self.primary.generate_analysis(problem_type, metrics, trace_samples)
        except Exception as e:
            print(f"\n  [ADVERTENCIA API] El proveedor en la nube no pudo responder ({str(e)}).")
            print("  [TRANSICIÓN AUTOMÁTICA] Activando motor analista experto local de contingencia...\n")
            return self.fallback.generate_analysis(problem_type, metrics, trace_samples)


class AIFactory:
    """Fábrica de conectores de Inteligencia Artificial."""

    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> BaseAIProvider:
        """
        Retorna la instancia del proveedor solicitado o el configurado en .env.
        Envuelto en RobustAIWrapper para garantizar ejecución ininterrumpida.
        """
        choice = (provider_name or AIConfig.PROVIDER or "gemini").lower().strip()
        fallback = FallbackExpertProvider()

        if choice == "gemini":
            if AIConfig.GEMINI_API_KEY:
                return RobustAIWrapper(GeminiProvider(), fallback)
            print("\n  [AVISO IA] GEMINI_API_KEY no detectada en .env. Usando motor analista experto offline.")
            return fallback

        elif choice == "openai":
            if AIConfig.OPENAI_API_KEY:
                return RobustAIWrapper(OpenAIProvider(), fallback)
            print("\n  [AVISO IA] OPENAI_API_KEY no detectada en .env. Usando motor analista experto offline.")
            return fallback

        elif choice == "ollama":
            return RobustAIWrapper(OllamaProvider(), fallback)

        elif choice == "offline":
            return fallback

        return fallback
