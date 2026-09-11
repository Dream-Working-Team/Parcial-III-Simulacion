"""
==============================================================================
CONTROLADOR PRINCIPAL DE LA INTERFAZ GRÁFICA (PYGAME)
==============================================================================
Orquestador de la ventana gráfica interactiva para la Pregunta Bonus.
Permite alternar entre los dos problemas, controlar la velocidad de ejecución,
pausar/reanudar y renderizar en tiempo real manteniendo estricta sincronización POO.
"""

import pygame
import sys
from config import GUIConfig, DiscreteSimConfig, ContinuousSimConfig
from simulation_discrete.engine import DiscreteEventSimulator
from simulation_continuous.engine import ContinuousSimulator
from .common import COLOR_BG, draw_header_hud
from .discrete_view import DiscreteViewRenderer
from .continuous_view import ContinuousViewRenderer


class SimulationVisualizer:
    """
    Controlador de la ventana de animación interactiva en Pygame.
    """
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.width = GUIConfig.WINDOW_WIDTH
        self.height = GUIConfig.WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GUIConfig.TITLE)
        
        self.clock = pygame.time.Clock()
        self.fps = GUIConfig.FPS
        
        # Modo activo: 'discrete' o 'continuous'
        self.active_mode = "discrete"
        self.is_paused = False
        self.speed_multiplier = 5.0  # 5x por defecto para visualización dinámica fluida
        self.running = True
        
        # Instancias de simulación sincronizadas
        self._init_simulations()
        
        # Renderizadores de vistas
        self.discrete_renderer = DiscreteViewRenderer()
        self.continuous_renderer = ContinuousViewRenderer()

    def _init_simulations(self):
        """Inicializa los motores de simulación con parámetros por defecto."""
        self.discrete_sim = DiscreteEventSimulator(
            duration_hours=DiscreteSimConfig.DEFAULT_HOURS,
            arrival_rate_hourly=DiscreteSimConfig.ARRIVAL_RATE_HOURLY,
            service_mean_minutes=DiscreteSimConfig.SERVICE_TIME_MEAN_MIN,
            initial_stock=DiscreteSimConfig.INITIAL_STOCK,
            reorder_threshold=DiscreteSimConfig.REORDER_THRESHOLD,
            batch_size=DiscreteSimConfig.REORDER_BATCH_SIZE,
            lead_time_minutes=DiscreteSimConfig.RESTOCK_LEAD_TIME_MIN
        )
        self.continuous_sim = ContinuousSimulator(
            duration_hours=ContinuousSimConfig.DEFAULT_HOURS,
            dt_seconds=ContinuousSimConfig.DT_SECONDS,
            mean_traffic_gbps=ContinuousSimConfig.TRAFFIC_MEAN_GBPS,
            std_traffic_gbps=ContinuousSimConfig.TRAFFIC_STD_GBPS,
            target_temp_c=ContinuousSimConfig.TARGET_TEMP_C,
            ambient_temp_c=ContinuousSimConfig.AMBIENT_TEMP_C
        )

    def run(self, initial_mode: str = "discrete"):
        """Bucle principal de renderizado y eventos de Pygame."""
        self.active_mode = initial_mode
        self.running = True

        while self.running:
            dt_raw = self.clock.tick(self.fps) / 1000.0  # Delta time en segundos reales
            
            # 1. Gestión de eventos de teclado y ventana
            self._handle_events()

            # 2. Cómputo lógico del modelo de simulación
            if not self.is_paused:
                self._advance_simulation(dt_raw)

            # 3. Renderizado gráfico de la vista
            self._draw_frame(dt_raw)

            pygame.display.flip()

        pygame.quit()

    def _handle_events(self):
        """Procesa entradas de usuario por teclado."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Salir con Escape
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # Pausa / Reanudación interactiva (Requisito del Parcial)
                elif event.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused

                # Alternar vista entre Problema 1 y Problema 2
                elif event.key == pygame.K_TAB:
                    self.active_mode = "continuous" if self.active_mode == "discrete" else "discrete"

                # Reiniciar simulación activa
                elif event.key == pygame.K_r:
                    self._init_simulations()

                # Selector de velocidad interactiva
                elif event.key == pygame.K_1:
                    self.speed_multiplier = 1.0
                elif event.key == pygame.K_2:
                    self.speed_multiplier = 5.0
                elif event.key == pygame.K_3:
                    self.speed_multiplier = 20.0
                elif event.key == pygame.K_4:
                    self.speed_multiplier = 50.0
                elif event.key == pygame.K_5:
                    self.speed_multiplier = 150.0

    def _advance_simulation(self, dt_real: float):
        """Avanza los pasos de simulación según el multiplicador de velocidad."""
        sim_delta = dt_real * self.speed_multiplier

        if self.active_mode == "discrete":
            # Para eventos discretos, avanzamos el reloj procesando eventos pendientes
            target_time = self.discrete_sim.current_time + sim_delta
            while self.discrete_sim.event_queue and self.discrete_sim.event_queue[0].timestamp <= target_time:
                if not self.discrete_sim.step():
                    break
            self.discrete_sim.current_time = min(target_time, self.discrete_sim.duration_seconds)
            if self.discrete_sim.current_time >= self.discrete_sim.duration_seconds:
                self.discrete_sim._finalize_simulation()

        else: # continuous
            # Para simulación continua, avanzamos la integración numérica EDO
            steps = max(1, int(self.speed_multiplier))
            step_dt = (sim_delta / steps)
            for _ in range(steps):
                if not self.continuous_sim.step(custom_dt=step_dt):
                    break

    def _draw_frame(self, dt_real: float):
        """Dibuja el fondo, la vista seleccionada y el HUD superior."""
        self.screen.fill(COLOR_BG)

        if self.active_mode == "discrete":
            draw_header_hud(
                self.screen,
                title="PROBLEMA 1: SIMULACIÓN DE EVENTOS DISCRETOS",
                subtitle="Fábrica de Laptops & Gestión de Procesadores",
                sim_time_sec=self.discrete_sim.current_time,
                speed_mult=self.speed_multiplier,
                is_paused=self.is_paused
            )
            self.discrete_renderer.render(self.screen, self.discrete_sim, dt_real)

        else: # continuous
            draw_header_hud(
                self.screen,
                title="PROBLEMA 2: SIMULACIÓN CONTINUA (EDO TÉRMICA)",
                subtitle="Balance Térmico del Clúster & Thermal Throttling",
                sim_time_sec=self.continuous_sim.current_time,
                speed_mult=self.speed_multiplier,
                is_paused=self.is_paused
            )
            self.continuous_renderer.render(self.screen, self.continuous_sim, dt_real)
