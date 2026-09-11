"""
==============================================================================
VISTA GRÁFICA - PROBLEMA 1: EVENTOS DISCRETOS (FÁBRICA DE LAPTOPS)
==============================================================================
Renderizador Pygame conectado en tiempo real a los atributos del simulador discreto:
cola de órdenes entrantes, estación de ensamblaje (cambio dinámico de color)
y medidor de nivel de inventario de procesadores con umbral crítico.
"""

import pygame
import math
from .common import (
    COLOR_BG, COLOR_PANEL, COLOR_PANEL_LIGHT, COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_CYAN, COLOR_GREEN,
    COLOR_YELLOW, COLOR_RED, COLOR_BORDER, draw_rounded_rect
)
from simulation_discrete.engine import DiscreteEventSimulator
from simulation_discrete.models import StationStatus


class DiscreteViewRenderer:
    """Renderizador para la simulación de eventos discretos."""

    def __init__(self):
        self.pulse_timer: float = 0.0

    def render(self, surface: pygame.Surface, sim: DiscreteEventSimulator, dt_frame: float):
        """Dibuja todos los componentes de la fábrica según el estado del simulador."""
        self.pulse_timer += dt_frame * 5.0
        w, h = surface.get_size()

        # Fuentes
        font_header = pygame.font.SysFont("Segoe UI", 16, bold=True)
        font_body = pygame.font.SysFont("Segoe UI", 13)
        font_large = pygame.font.SysFont("Segoe UI", 22, bold=True)
        font_mono = pygame.font.SysFont("Consolas", 14)

        # ---------------------------------------------------------------------
        # 1. PANEL IZQUIERDO: COLA DE ÓRDENES EN ESPERA (CINTA TRANSPORTADORA)
        # ---------------------------------------------------------------------
        queue_rect = pygame.Rect(25, 90, 310, 480)
        draw_rounded_rect(surface, queue_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)
        
        surf_q_title = font_header.render("COLA DE PRODUCCIÓN (FIFO)", True, COLOR_TEXT_LIGHT)
        surface.blit(surf_q_title, (40, 105))
        
        q_len = len(sim.order_queue)
        surf_q_sub = font_body.render(f"Órdenes en espera: {q_len}", True, COLOR_ACCENT)
        surface.blit(surf_q_sub, (40, 130))

        # Dibujar cinta de laptops
        conveyor_y = 165
        visible_orders = sim.order_queue[:8]
        for i, order in enumerate(visible_orders):
            box_rect = pygame.Rect(45, conveyor_y + (i * 42), 270, 34)
            draw_rounded_rect(surface, box_rect, COLOR_PANEL_LIGHT, radius=6, border_color=COLOR_BORDER)
            
            label = f"Laptop #{order.order_id} (Serv: {order.service_duration/60.0:.1f}m)"
            surf_box = font_mono.render(label, True, COLOR_TEXT_LIGHT)
            surface.blit(surf_box, (55, conveyor_y + (i * 42) + 8))

        if q_len > 8:
            surf_more = font_body.render(f"+ {q_len - 8} órdenes adicionales en cola...", True, COLOR_TEXT_MUTED)
            surface.blit(surf_more, (45, conveyor_y + (8 * 42) + 8))
        elif q_len == 0:
            surf_empty = font_body.render("Cola vacía (Sin órdenes esperando)", True, COLOR_TEXT_MUTED)
            surface.blit(surf_empty, (55, 200))

        # ---------------------------------------------------------------------
        # 2. PANEL CENTRAL: ESTACIÓN PRINCIPAL DE ENSAMBLAJE
        # ---------------------------------------------------------------------
        station_rect = pygame.Rect(355, 90, 480, 480)
        draw_rounded_rect(surface, station_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

        surf_st_title = font_header.render("ESTACIÓN DE ENSAMBLAJE", True, COLOR_TEXT_LIGHT)
        surface.blit(surf_st_title, (375, 105))

        # Determinar color según estado especificado en el parcial
        status = sim.station.status
        if status == StationStatus.IDLE:
            st_color = COLOR_GREEN
            st_text = "ESTACIÓN LIBRE"
            desc_text = "Esperando nueva orden de laptop"
        elif status == StationStatus.BUSY:
            st_color = COLOR_YELLOW
            order_id = sim.station.current_order.order_id if sim.station.current_order else "?"
            st_text = f"ENSAMBLANDO ORDEN #{order_id}"
            desc_text = "Procesador integrado - Ensamble en curso"
        else: # STOPPED_NO_STOCK
            # Efecto pulsante rojo para alerta visual impactante
            pulse = int(200 + 55 * math.sin(self.pulse_timer))
            st_color = (pulse, 40, 40)
            st_text = "¡LÍNEA DETENIDA!"
            desc_text = "SIN PROCESADORES EN STOCK (BLOQUEADA)"

        # Caja central de la máquina
        machine_rect = pygame.Rect(385, 155, 420, 240)
        draw_rounded_rect(surface, machine_rect, COLOR_PANEL_LIGHT, radius=12, border_color=st_color, border_width=3)

        # Indicador de luz de estado
        pygame.draw.circle(surface, st_color, (420, 195), 16)
        surf_state = font_large.render(st_text, True, st_color)
        surface.blit(surf_state, (450, 180))

        surf_desc = font_body.render(desc_text, True, COLOR_TEXT_MUTED)
        surface.blit(surf_desc, (450, 215))

        # Barra de progreso de ensamblaje si está ocupada
        if status == StationStatus.BUSY and sim.station.current_order:
            order = sim.station.current_order
            elapsed = max(0.0, sim.current_time - (order.start_service_time or sim.current_time))
            total_duration = max(1.0, order.service_duration)
            progress = min(1.0, elapsed / total_duration)

            bar_bg = pygame.Rect(415, 270, 360, 20)
            draw_rounded_rect(surface, bar_bg, COLOR_PANEL, radius=6)
            bar_fill = pygame.Rect(415, 270, int(360 * progress), 20)
            draw_rounded_rect(surface, bar_fill, COLOR_CYAN, radius=6)

            surf_prog = font_mono.render(f"Progreso de ensamble: {progress * 100:.0f}%", True, COLOR_TEXT_LIGHT)
            surface.blit(surf_prog, (415, 300))

        elif status == StationStatus.STOPPED_NO_STOCK:
            surf_warn = font_body.render("Se reanudará automáticamente al recibir lote del proveedor", True, COLOR_RED)
            surface.blit(surf_warn, (410, 280))

        # Métricas de estación en la parte inferior del panel central
        stops_str = f"Detenciones por stock: {sim.station.line_stops_count}"
        stopped_time_min = sim.station.total_stopped_time / 60.0
        stops_time_str = f"Tiempo detenida: {stopped_time_min:.1f} min"
        util_pct = (sim.station.total_busy_time / max(1.0, sim.current_time)) * 100.0
        util_str = f"Utilización: {util_pct:.1f}%"

        surface.blit(font_mono.render(stops_str, True, COLOR_TEXT_LIGHT), (385, 420))
        surface.blit(font_mono.render(stops_time_str, True, COLOR_TEXT_LIGHT), (385, 445))
        surface.blit(font_mono.render(util_str, True, COLOR_CYAN), (385, 470))

        # ---------------------------------------------------------------------
        # 3. PANEL DERECHO: NIVEL DE INVENTARIO DE PROCESADORES
        # ---------------------------------------------------------------------
        inv_rect = pygame.Rect(855, 90, 320, 480)
        draw_rounded_rect(surface, inv_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

        surf_inv_title = font_header.render("STOCK DE PROCESADORES", True, COLOR_TEXT_LIGHT)
        surface.blit(surf_inv_title, (875, 105))

        stock = sim.inventory.current_stock
        threshold = sim.inventory.reorder_threshold
        max_display = 75

        # Tanque medidor vertical
        gauge_x = 885
        gauge_y = 150
        gauge_w = 70
        gauge_h = 300

        # Fondo del tanque
        draw_rounded_rect(surface, pygame.Rect(gauge_x, gauge_y, gauge_w, gauge_h), COLOR_PANEL_LIGHT, radius=10, border_color=COLOR_BORDER)

        # Llenado de stock
        fill_ratio = min(1.0, max(0.0, stock / max_display))
        fill_h = int(gauge_h * fill_ratio)
        fill_y = gauge_y + (gauge_h - fill_h)

        fill_color = COLOR_RED if stock < threshold else COLOR_GREEN
        if fill_h > 0:
            draw_rounded_rect(surface, pygame.Rect(gauge_x + 4, fill_y, gauge_w - 8, fill_h), fill_color, radius=6)

        # Línea de umbral crítico (< 10)
        thresh_y = gauge_y + gauge_h - int(gauge_h * (threshold / max_display))
        pygame.draw.line(surface, COLOR_RED, (gauge_x - 10, thresh_y), (gauge_x + gauge_w + 10, thresh_y), 3)

        # Etiquetas numéricas del medidor
        surf_stock_val = font_large.render(f"{stock} CPUs", True, fill_color)
        surface.blit(surf_stock_val, (975, 170))

        surf_thresh_lbl = font_body.render(f"Umbral crítico: < {threshold}", True, COLOR_RED)
        surface.blit(surf_thresh_lbl, (975, thresh_y - 10))

        # Estado del proveedor
        if sim.inventory.has_pending_order:
            time_left_sec = max(0.0, (sim.inventory.pending_order_arrival_time or 0) - sim.current_time)
            mins_left = time_left_sec / 60.0
            p_rect = pygame.Rect(875, 470, 280, 80)
            draw_rounded_rect(surface, p_rect, COLOR_PANEL_LIGHT, radius=8, border_color=COLOR_YELLOW)
            surface.blit(font_header.render("REABASTECIMIENTO ACTIVO", True, COLOR_YELLOW), (890, 480))
            surface.blit(font_body.render(f"Lote en camino: +{sim.inventory.batch_size} procesadores", True, COLOR_TEXT_LIGHT), (890, 505))
            surface.blit(font_mono.render(f"Llegada estimada: {mins_left:.1f} min", True, COLOR_ACCENT), (890, 525))
        else:
            p_rect = pygame.Rect(875, 470, 280, 80)
            draw_rounded_rect(surface, p_rect, COLOR_PANEL_LIGHT, radius=8, border_color=COLOR_BORDER)
            surface.blit(font_body.render("Proveedor en espera (Stock OK)", True, COLOR_TEXT_MUTED), (890, 500))

        # ---------------------------------------------------------------------
        # 4. PANEL INFERIOR: HUD DE MÉTRICAS GLOBALES
        # ---------------------------------------------------------------------
        bottom_rect = pygame.Rect(25, 590, w - 50, 130)
        draw_rounded_rect(surface, bottom_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

        col_w = (w - 50) // 5
        metrics_display = [
            ("ÓRDENES RECIBIDAS", f"{sim.order_counter}", COLOR_TEXT_LIGHT),
            ("ÓRDENES DESPACHADAS", f"{len(sim.metrics.completed_orders)}", COLOR_GREEN),
            ("ESPERA PROMEDIO", f"{((sum(o.waiting_time for o in sim.metrics.completed_orders) / max(1, len(sim.metrics.completed_orders))) / 60.0):.2f} min", COLOR_CYAN),
            ("ÓRDENES RETRASADAS", f"{len(sim.metrics.delayed_by_stock_orders)}", COLOR_RED if sim.metrics.delayed_by_stock_orders else COLOR_TEXT_LIGHT),
            ("EFICIENCIA REABASTECE", f"{max(0.0, 100.0 - (len(sim.metrics.delayed_by_stock_orders) / max(1, len(sim.metrics.completed_orders)) * 100.0)):.1f}%", COLOR_ACCENT)
        ]

        for i, (label, val, col) in enumerate(metrics_display):
            bx = 35 + (i * col_w)
            surface.blit(font_body.render(label, True, COLOR_TEXT_MUTED), (bx, 615))
            surface.blit(font_large.render(val, True, col), (bx, 645))
