"""
==============================================================================
SISTEMA DE REGISTRO DE TRAZAS (LOGGER)
==============================================================================
Clase encargada de emitir y almacenar trazas cronológicas detalladas de la
simulación, permitiendo auditoría temporal y exportación a archivos de texto.
"""

from typing import List, Optional
from datetime import timedelta
from pathlib import Path


class SimulationTrace:
    """Representa una línea individual de traza en la simulación."""
    def __init__(self, sim_time_seconds: float, category: str, message: str):
        self.sim_time_seconds = sim_time_seconds
        self.category = category
        self.message = message

    @property
    def formatted_time(self) -> str:
        """Retorna el tiempo simulado en formato [HH:MM:SS]."""
        td = timedelta(seconds=int(self.sim_time_seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def __str__(self) -> str:
        return f"[{self.formatted_time}] [{self.category.upper():<12}] {self.message}"


class SimulationLogger:
    """
    Gestor centralizado de trazas para simulación continua o discreta.
    Almacena las trazas en memoria y permite imprimirlas o guardarlas en archivo.
    """
    def __init__(self, name: str, print_to_console: bool = True):
        self.name = name
        self.print_to_console = print_to_console
        self.traces: List[SimulationTrace] = []

    def log(self, sim_time_seconds: float, category: str, message: str) -> None:
        """Registra una traza con su respectiva marca temporal."""
        trace = SimulationTrace(sim_time_seconds, category, message)
        self.traces.append(trace)
        if self.print_to_console:
            print(str(trace))

    def clear(self) -> None:
        """Limpia el registro de trazas acumuladas."""
        self.traces.clear()

    def get_traces_as_strings(self) -> List[str]:
        """Retorna la lista de trazas en formato texto."""
        return [str(t) for t in self.traces]

    def get_sample_traces(self, max_items: int = 40) -> List[str]:
        """
        Retorna una muestra representativa de trazas (inicio, medio y final)
        para optimizar tokens al enviarlo a la API de IA.
        """
        total = len(self.traces)
        if total <= max_items:
            return [str(t) for t in self.traces]
        
        # Tomar 15 iniciales, 10 intermedias y 15 finales
        head = self.traces[:15]
        mid_idx = total // 2
        mid = self.traces[mid_idx - 5 : mid_idx + 5]
        tail = self.traces[-15:]
        
        sample = [str(t) for t in head]
        sample.append(f"... [{total - 40} trazas intermedias omitidas por optimización de tokens] ...")
        sample.extend(str(t) for t in mid)
        sample.append(f"...")
        sample.extend(str(t) for t in tail)
        return sample

    def save_to_file(self, file_path: Path) -> None:
        """Guarda todas las trazas en un archivo de texto en disco."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=== REPORTE DE TRAZAS: {self.name} ===\n")
            f.write(f"Total de eventos registrados: {len(self.traces)}\n\n")
            for trace in self.traces:
                f.write(f"{str(trace)}\n")
