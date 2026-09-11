"""
==============================================================================
MÓDULO DE VALIDACIÓN DE ENTRADAS DE USUARIO
==============================================================================
Funciones utilitarias para la captura y validación estricta de parámetros
en consola, con soporte para valores por defecto sugeridos.
"""

from typing import List, Optional


class InputValidator:
    """Validador estricto para interacción por terminal."""

    @staticmethod
    def prompt_float(
        prompt: str,
        default: float,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> float:
        """
        Solicita un número decimal. Si el usuario presiona Enter, se usa el valor por defecto.
        Valida que esté dentro del rango especificado.
        """
        range_str = ""
        if min_val is not None and max_val is not None:
            range_str = f" [{min_val} - {max_val}]"
        elif min_val is not None:
            range_str = f" [>= {min_val}]"

        while True:
            raw = input(f"{prompt}{range_str} (por defecto: {default}): ").strip()
            if not raw:
                return default
            try:
                val = float(raw)
                if min_val is not None and val < min_val:
                    print(f"  [ERROR] El valor debe ser mayor o igual a {min_val}.")
                    continue
                if max_val is not None and val > max_val:
                    print(f"  [ERROR] El valor debe ser menor o igual a {max_val}.")
                    continue
                return val
            except ValueError:
                print("  [ERROR] Por favor ingrese un número decimal válido.")

    @staticmethod
    def prompt_int(
        prompt: str,
        default: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None
    ) -> int:
        """
        Solicita un número entero. Si el usuario presiona Enter, se usa el valor por defecto.
        """
        range_str = ""
        if min_val is not None and max_val is not None:
            range_str = f" [{min_val} - {max_val}]"
        elif min_val is not None:
            range_str = f" [>= {min_val}]"

        while True:
            raw = input(f"{prompt}{range_str} (por defecto: {default}): ").strip()
            if not raw:
                return default
            try:
                val = int(raw)
                if min_val is not None and val < min_val:
                    print(f"  [ERROR] El valor debe ser mayor o igual a {min_val}.")
                    continue
                if max_val is not None and val > max_val:
                    print(f"  [ERROR] El valor debe ser menor o igual a {max_val}.")
                    continue
                return val
            except ValueError:
                print("  [ERROR] Por favor ingrese un número entero válido.")

    @staticmethod
    def prompt_choice(
        prompt: str,
        choices: List[str],
        default: str
    ) -> str:
        """
        Solicita una selección entre opciones válidas.
        """
        choices_str = "/".join(choices)
        while True:
            raw = input(f"{prompt} ({choices_str}) [por defecto: {default}]: ").strip().lower()
            if not raw:
                return default.lower()
            if raw in [c.lower() for c in choices]:
                return raw
            print(f"  [ERROR] Opción inválida. Elija entre: {choices_str}")
