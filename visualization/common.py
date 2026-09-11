"""
==============================================================================
ESTILOS Y UTILIDADES COMUNES DE VISUALIZACIÓN (PYGAME)
==============================================================================
Paleta de colores moderna, tipografías y funciones de dibujo geométrico.
"""

import pygame

# Paleta moderna (Dark Glassmorphism Theme)
COLOR_BG = (15, 23, 42)          # Slate 900
COLOR_PANEL = (30, 41, 59)       # Slate 800
COLOR_PANEL_LIGHT = (51, 65, 85) # Slate 700
COLOR_TEXT_LIGHT = (241, 245, 249)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_ACCENT = (56, 189, 248)    # Sky 400
COLOR_CYAN = (6, 182, 212)
COLOR_GREEN = (34, 197, 94)      # Emerald 500
COLOR_YELLOW = (234, 179, 8)     # Amber 500
COLOR_ORANGE = (249, 115, 22)
COLOR_RED = (239, 68, 68)        # Rose 500
COLOR_BORDER = (71, 85, 105)


def draw_rounded_rect(surface, rect, color, radius=10, border_color=None, border_width=1):
    """Dibuja un rectángulo con esquinas redondeadas y borde opcional."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)


def draw_header_hud(surface, title: str, subtitle: str, sim_time_sec: float, speed_mult: float, is_paused: bool):
    """Dibuja la barra de estado superior (HUD) con controles y reloj."""
    w, h = surface.get_size()
    hud_rect = pygame.Rect(15, 10, w - 30, 65)
    draw_rounded_rect(surface, hud_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER)

    font_title = pygame.font.SysSearchPath if False else pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_sub = pygame.font.SysFont("Segoe UI", 13)
    font_hud = pygame.font.SysFont("Consolas", 15, bold=True)

    # Título y subtítulo
    surf_title = font_title.render(title, True, COLOR_TEXT_LIGHT)
    surf_sub = font_sub.render(subtitle, True, COLOR_ACCENT)
    surface.blit(surf_title, (30, 18))
    surface.blit(surf_sub, (30, 44))

    # Formatear tiempo simulado
    hours = int(sim_time_sec // 3600)
    minutes = int((sim_time_sec % 3600) // 60)
    seconds = int(sim_time_sec % 60)
    time_str = f"TIEMPO: {hours:02d}h {minutes:02d}m {seconds:02d}s"
    
    surf_time = font_hud.render(time_str, True, COLOR_CYAN)
    surface.blit(surf_time, (w - 530, 22))

    # Velocidad y estado de pausa
    status_str = "PAUSADO" if is_paused else f"VELOCIDAD: {speed_mult:.0f}x"
    status_color = COLOR_YELLOW if is_paused else COLOR_GREEN
    surf_status = font_hud.render(status_str, True, status_color)
    surface.blit(surf_status, (w - 530, 44))

    # Guía de teclas
    font_keys = pygame.font.SysFont("Segoe UI", 12)
    keys_str = "[ESPACIO]: Pausar | [1-5]: Velocidad | [TAB]: Alternar Problema | [ESC]: Salir"
    surf_keys = font_keys.render(keys_str, True, COLOR_TEXT_MUTED)
    surface.blit(surf_keys, (w - 470, 33))
