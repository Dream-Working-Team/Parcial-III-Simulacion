"""
==============================================================================
VISTA GRÁFICA - PROBLEMA 2: SIMULACIÓN CONTINUA (CLÚSTER TÉRMICO)
==============================================================================
Renderizador Pygame conectado en tiempo real a los atributos del simulador continuo:
nodo servidor estilizado, barra térmica dinámica (degradado azul a rojo crítico),
gráfico osciloscopio en tiempo real de temperatura vs 70°C y medidores de tráfico.
"""

import pygame
import math
from typing import List
from .common import (
    COLOR_BG, COLOR_PANEL, COLOR_PANEL_LIGHT, COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_CYAN, COLOR_GREEN,
    COLOR_YELLOW, COLOR_ORANGE, COLOR_RED, COLOR_BORDER, draw_rounded_rect
)
from simulation_continuous.engine import ContinuousSimulator


class ContinuousViewRenderer:
    """Renderizador para la simulación continua de clúster térmico."""

    def __init__(self):
        self.fan_angle: float = 0.0
        self.pulse_timer: float = 0.0
        self.temp_history: List[float] = []
        self.traffic_history: List[float] = []
        self.max_history_points = 140
        # Tipografías cacheadas para nitidez y rendimiento
        self.font_header = pygame.font.SysFont(["Segoe UI", "Arial"], 16, bold=True)
        self.font_body = pygame.font.SysFont(["Segoe UI", "Arial"], 13, bold=False)
        self.font_large = pygame.font.SysFont(["Segoe UI", "Arial"], 24, bold=True)
        self.font_mono = pygame.font.SysFont(["Consolas", "Courier New"], 14, bold=True)

    def render(self, surface: pygame.Surface, sim: ContinuousSimulator, dt_frame: float):
        """Dibuja el servidor, la barra térmica y las gráficas dinámicas."""
        self.pulse_timer += dt_frame * 6.0
        # Velocidad del ventilador proporcional a la temperatura
        fan_speed = max(2.0, (sim.thermal_model.temperature - 25.0) * 0.4)
        self.fan_angle = (self.fan_angle + dt_frame * fan_speed * 100.0) % 360.0

        w, h = surface.get_size()

        # Almacenar puntos de historial para el osciloscopio
        current_temp = sim.thermal_model.temperature
        self.temp_history.append(current_temp)
        self.traffic_history.append(sim.current_incoming_gbps)
        if len(self.temp_history) > self.max_history_points:
            self.temp_history.pop(0)
            self.traffic_history.pop(0)

        font_header = self.font_header
        font_body = self.font_body
        font_large = self.font_large
        font_mono = self.font_mono

        # ---------------------------------------------------------------------
        # 1. PANEL IZQUIERDO: RACK DE SERVIDORES Y REFRIGERACIÓN
        # ---------------------------------------------------------------------
        rack_rect = pygame.Rect(25, 90, 360, 480)
        draw_rounded_rect(surface, rack_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

        surf_r_title = font_header.render("NODO SERVIDOR DE ALTO RENDIMIENTO", True, COLOR_TEXT_LIGHT)
        surface.blit(surf_r_title, (40, 105))

        # Indicador de estado del clúster
        is_throttled = sim.is_throttled
        if is_throttled:
            pulse = int(210 + 45 * math.sin(self.pulse_timer))
            status_col = (pulse, 30, 30)
            status_txt = "¡ESTRANGULAMIENTO TÉRMICO!"
            status_desc = f"Downclocking activo - Eficiencia reducida ({sim.current_efficiency*100:.1f}%)"
        else:
            status_col = COLOR_GREEN
            status_txt = "OPERACIÓN NOMINAL ESTABLE"
            status_desc = f"Eficiencia de diseño: 90% (T <= 70°C)"

        draw_rounded_rect(surface, pygame.Rect(40, 140, 330, 60), COLOR_PANEL_LIGHT, radius=8, border_color=status_col, border_width=2)
        surface.blit(font_header.render(status_txt, True, status_col), (50, 148))
        surface.blit(font_body.render(status_desc, True, COLOR_TEXT_MUTED), (50, 172))

        # Dibujo esquemático de Servidor Blade
        server_box = pygame.Rect(40, 220, 330, 200)
        draw_rounded_rect(surface, server_box, (20, 28, 45), radius=10, border_color=COLOR_BORDER)

        # Bahías de servidores con LEDs parpadeantes de actividad
        for b in range(4):
            blade_rect = pygame.Rect(55, 235 + (b * 45), 300, 35)
            draw_rounded_rect(surface, blade_rect, COLOR_PANEL_LIGHT, radius=6)
            
            # LED de encendido
            pygame.draw.circle(surface, COLOR_CYAN, (75, 252 + (b * 45)), 5)
            
            # LED de actividad (parpadeo según tráfico)
            led_active = (math.sin(self.pulse_timer * (b + 1) * sim.current_incoming_gbps) > 0)
            led_col = COLOR_GREEN if led_active else (30, 80, 40)
            if is_throttled and led_active:
                led_col = COLOR_RED
            pygame.draw.circle(surface, led_col, (95, 252 + (b * 45)), 5)

            blade_lbl = f"CPU Blade #{b+1} (Núcleos Xeon/EPYC)"
            surface.blit(font_mono.render(blade_lbl, True, COLOR_TEXT_LIGHT), (115, 244 + (b * 45)))

        # Simulación visual de ventiladores de refrigeración líquida
        surface.blit(font_body.render("Sistema de Refrigeración Líquida:", True, COLOR_TEXT_MUTED), (40, 435))
        fan_center = (90, 485)
        pygame.draw.circle(surface, COLOR_PANEL_LIGHT, fan_center, 25)
        # Aspas girando
        for k in range(3):
            angle_rad = math.radians(self.fan_angle + (k * 120))
            end_x = fan_center[0] + 20 * math.cos(angle_rad)
            end_y = fan_center[1] + 20 * math.sin(angle_rad)
            pygame.draw.line(surface, COLOR_CYAN, fan_center, (end_x, end_y), 3)

        surface.blit(font_mono.render(f"Disipación k_cool: {sim.thermal_model.k_cool * 60:.2f}/min", True, COLOR_CYAN), (130, 475))
        surface.blit(font_mono.render(f"T_refrigerante: {sim.thermal_model.ambient_temp:.0f}°C", True, COLOR_TEXT_LIGHT), (130, 495))

        # ---------------------------------------------------------------------
        # 2. PANEL CENTRAL: BARRA TÉRMICA DINÁMICA (TERMÓMETRO)
        # ---------------------------------------------------------------------
        therm_rect = pygame.Rect(405, 90, 260, 480)
        draw_rounded_rect(surface, therm_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

        surf_t_title = font_header.render("MONITOR TÉRMICO", True, COLOR_TEXT_LIGHT)
        surface.blit(surf_t_title, (425, 105))

        # Rango visual: de 20°C a 90°C
        min_temp_scale = 20.0
        max_temp_scale = 90.0
        scale_range = max_temp_scale - min_temp_scale

        bar_x = 445
        bar_y = 150
        bar_w = 45
        bar_h = 320

        # Fondo del termómetro
        draw_rounded_rect(surface, pygame.Rect(bar_x, bar_y, bar_w, bar_h), COLOR_PANEL_LIGHT, radius=12, border_color=COLOR_BORDER)

        # Altura de llenado según temperatura actual
        ratio = min(1.0, max(0.0, (current_temp - min_temp_scale) / scale_range))
        fill_h = int(bar_h * ratio)
        fill_y = bar_y + (bar_h - fill_h)

        # Gradiente dinámico de color: Azul (<60) -> Verde (60-70) -> Amarillo/Naranja (70-75) -> Rojo (>75)
        if current_temp < 60.0:
            therm_color = (60, 160, 255) # Azul frío
        elif current_temp <= 70.0:
            # Interpolación suave azul-verde a verde
            factor = (current_temp - 60.0) / 10.0
            therm_color = (int(34 * factor), int(197 * factor + 160 * (1 - factor)), int(94 * factor + 255 * (1 - factor)))
        elif current_temp <= 75.0:
            therm_color = COLOR_YELLOW
        else:
            therm_color = COLOR_RED

        if fill_h > 0:
            draw_rounded_rect(surface, pygame.Rect(bar_x + 3, fill_y, bar_w - 6, fill_h), therm_color, radius=10)

        # Línea de referencia del umbral nominal (70.0°C)
        thresh_ratio = (70.0 - min_temp_scale) / scale_range
        thresh_y = bar_y + bar_h - int(bar_h * thresh_ratio)
        pygame.draw.line(surface, COLOR_RED, (bar_x - 15, thresh_y), (bar_x + bar_w + 15, thresh_y), 3)

        # Lectura digital de temperatura
        surface.blit(font_large.render(f"{current_temp:.2f} °C", True, therm_color), (505, 170))
        surface.blit(font_body.render(f"Límite seguro: 70.0 °C", True, COLOR_RED), (505, thresh_y - 12))

        # Indicador de estado del calor
        q_gen_min = sim.thermal_model.k_heat * 60.0 * sim.current_processed_gbps
        q_diss_min = sim.thermal_model.k_cool * 60.0 * (current_temp - sim.thermal_model.ambient_temp)
        net_rate = q_gen_min - q_diss_min

        surface.blit(font_mono.render(f"Calor gen: +{q_gen_min:.2f} °C/m", True, COLOR_TEXT_LIGHT), (425, 485))
        surface.blit(font_mono.render(f"Disipación: -{q_diss_min:.2f} °C/m", True, COLOR_CYAN), (425, 510))
        net_col = COLOR_RED if net_rate > 0.05 else (COLOR_GREEN if net_rate < -0.05 else COLOR_TEXT_MUTED)
        surface.blit(font_mono.render(f"dT/dt neto: {net_rate:+.2f} °C/m", True, net_col), (425, 535))

        # ---------------------------------------------------------------------
        # 3. PANEL DERECHO: GRÁFICO DINÁMICO EN TIEMPO REAL (HISTORIAL)
        # ---------------------------------------------------------------------
        graph_rect = pygame.Rect(685, 90, 490, 480)
        draw_rounded_rect(surface, graph_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

        surf_g_title = font_header.render("EVOLUCIÓN TÉRMICA Y TRÁFICO (TIEMPO REAL)", True, COLOR_TEXT_LIGHT)
        surface.blit(surf_g_title, (705, 105))

        # Cuadro de osciloscopio
        plot_box = pygame.Rect(705, 140, 450, 240)
        draw_rounded_rect(surface, plot_box, (10, 15, 30), radius=8, border_color=COLOR_BORDER)

        # Línea de umbral 70°C en el gráfico
        plot_thresh_y = plot_box.bottom - int(plot_box.height * ((70.0 - min_temp_scale) / scale_range))
        pygame.draw.line(surface, (180, 50, 50), (plot_box.left, plot_thresh_y), (plot_box.right, plot_thresh_y), 1)
        surface.blit(font_mono.render("70°C (Umbral)", True, (180, 80, 80)), (plot_box.left + 10, plot_thresh_y - 18))

        # Trazar curva de temperatura
        if len(self.temp_history) >= 2:
            points = []
            dx = plot_box.width / (self.max_history_points - 1)
            for i, temp_val in enumerate(self.temp_history):
                r = (temp_val - min_temp_scale) / scale_range
                r = min(1.0, max(0.0, r))
                px = plot_box.left + (i * dx)
                py = plot_box.bottom - (r * plot_box.height)
                points.append((px, py))
            
            pygame.draw.lines(surface, COLOR_ACCENT, False, points, 2)

        # Medidores de tráfico entrante y Throughput
        surface.blit(font_header.render("FLUJO DE TRÁFICO Y THROUGHPUT:", True, COLOR_TEXT_LIGHT), (705, 400))
        
        # Barra tráfico
        surface.blit(font_body.render(f"Demanda entrante: {sim.current_incoming_gbps:.2f} Gbps", True, COLOR_TEXT_LIGHT), (705, 430))
        bar_traf_bg = pygame.Rect(705, 450, 450, 14)
        draw_rounded_rect(surface, bar_traf_bg, COLOR_PANEL_LIGHT, radius=4)
        traf_ratio = min(1.0, max(0.0, sim.current_incoming_gbps / 5.0))
        draw_rounded_rect(surface, pygame.Rect(705, 450, int(450 * traf_ratio), 14), COLOR_CYAN, radius=4)

        # Barra throughput procesado
        surface.blit(font_body.render(f"Throughput procesado: {sim.current_processed_gbps:.2f} Gbps ({sim.current_efficiency*100:.1f}%)", True, COLOR_GREEN if not is_throttled else COLOR_RED), (705, 480))
        bar_proc_bg = pygame.Rect(705, 500, 450, 14)
        draw_rounded_rect(surface, bar_proc_bg, COLOR_PANEL_LIGHT, radius=4)
        proc_ratio = min(1.0, max(0.0, sim.current_processed_gbps / 5.0))
        proc_col = COLOR_GREEN if not is_throttled else COLOR_ORANGE
        draw_rounded_rect(surface, pygame.Rect(705, 500, int(450 * proc_ratio), 14), proc_col, radius=4)

        # ---------------------------------------------------------------------
        # 4. PANEL INFERIOR: HUD DE MÉTRICAS CONTINUAS
        # ---------------------------------------------------------------------
        bottom_rect = pygame.Rect(25, 590, w - 50, 130)
        draw_rounded_rect(surface, bottom_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

        metrics = sim.get_summary_metrics()
        col_w = (w - 50) // 5
        metrics_display = [
            ("TRÁFICO TOTAL", f"{metrics.get('total_trafico_entrante_tb')} TB", COLOR_TEXT_LIGHT),
            ("DATOS PROCESADOS", f"{metrics.get('total_datos_procesados_tb')} TB", COLOR_GREEN),
            ("EFICIENCIA GLOBAL", f"{metrics.get('eficiencia_global_red_pct')} %", COLOR_CYAN),
            ("TIEMPO EN THROTTLING", f"{metrics.get('porcentaje_tiempo_estrangulado')} %", COLOR_RED if is_throttled else COLOR_TEXT_LIGHT),
            ("ESTABILIDAD TÉRMICA", f"{metrics.get('diagnostico_viabilidad_operativa')[:14]}", COLOR_ACCENT)
        ]

        for i, (label, val, col) in enumerate(metrics_display):
            bx = 35 + (i * col_w)
            surface.blit(font_body.render(label, True, COLOR_TEXT_MUTED), (bx, 615))
            surface.blit(font_large.render(val, True, col), (bx, 645))
