"""
==============================================================================
ESTILOS Y UTILIDADES COMUNES DE VISUALIZACIÓN (PYGAME)
==============================================================================
Paleta de colores moderna, tipografías nítidas y funciones de dibujo geométrico.
Incluye renderizado de teclas estilo mecánico (Keycaps) de alta legibilidad.
"""

import pygame

# Paleta moderna (Dark Theme de alto contraste y legibilidad)
COLOR_BG = (15, 23, 42)          # Slate 900
COLOR_PANEL = (30, 41, 59)       # Slate 800
COLOR_PANEL_LIGHT = (51, 65, 85) # Slate 700
COLOR_CARD_BG = (11, 18, 32)     # Fondo oscuro para contraste en widgets
COLOR_TEXT_LIGHT = (248, 250, 252)
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_TEXT_MUTED = (185, 198, 218) # Alto contraste para texto secundario legible
COLOR_ACCENT = (56, 189, 248)    # Sky 400
COLOR_CYAN = (6, 182, 212)
COLOR_GREEN = (34, 197, 94)      # Emerald 500
COLOR_YELLOW = (250, 204, 21)    # Amber 400
COLOR_ORANGE = (249, 115, 22)
COLOR_RED = (239, 68, 68)        # Rose 500
COLOR_BORDER = (71, 85, 105)
COLOR_KEYCAP_BG = (45, 55, 75)
COLOR_KEYCAP_BORDER = (148, 163, 184)


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Retorna una tipografía nítida y antialiased compatible con Windows."""
    return pygame.font.SysFont(["Segoe UI", "Arial", "Verdana"], size, bold=bold)


def get_mono_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Retorna una tipografía monoespaciada para relojes y cifras numéricas."""
    return pygame.font.SysFont(["Consolas", "Courier New"], size, bold=bold)


def draw_rounded_rect(surface, rect, color, radius=10, border_color=None, border_width=1):
    """Dibuja un rectángulo con esquinas redondeadas y borde opcional."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)


def draw_keycap(surface, key_str: str, label_str: str, x: int, y: int, font_key, font_label) -> int:
    """
    Dibuja un botón de tecla interactiva estilo keycap con borde y texto nítido.
    Retorna el ancho total ocupado en píxeles.
    """
    surf_key = font_key.render(key_str, True, COLOR_TEXT_WHITE)
    key_w = surf_key.get_width() + 12
    key_h = 24
    key_rect = pygame.Rect(x, y, key_w, key_h)

    # Tecla con relieve / sombra sutil
    draw_rounded_rect(surface, key_rect, COLOR_KEYCAP_BG, radius=5, border_color=COLOR_KEYCAP_BORDER, border_width=1)
    surface.blit(surf_key, (x + 6, y + 3))

    # Etiqueta de acción al lado
    surf_lbl = font_label.render(label_str, True, (226, 232, 240))
    surface.blit(surf_lbl, (x + key_w + 5, y + 4))

    total_w = key_w + 5 + surf_lbl.get_width() + 12
    return total_w


def draw_header_hud(surface, title: str, subtitle: str, sim_time_sec: float, speed_mult: float, is_paused: bool):
    """
    Dibuja la barra de estado superior (HUD) con diseño profesional,
    reloj digital centrado y panel de atajos de teclado sin solapamientos.
    """
    w, h = surface.get_size()
    hud_rect = pygame.Rect(15, 8, w - 30, 74)
    draw_rounded_rect(surface, hud_rect, COLOR_PANEL, radius=12, border_color=COLOR_BORDER, border_width=1)

    font_title = get_font(18, bold=True)
    font_sub = get_font(12, bold=True)
    font_clock = get_mono_font(14, bold=True)
    font_key = get_mono_font(11, bold=True)
    font_lbl = get_font(11, bold=True)
    font_hud_title = get_font(10, bold=True)

    # -------------------------------------------------------------------------
    # 1. ZONA IZQUIERDA: TÍTULO DEL PROBLEMA ACTIVO
    # -------------------------------------------------------------------------
    surf_title = font_title.render(title, True, COLOR_TEXT_WHITE)
    surf_sub = font_sub.render(subtitle, True, COLOR_ACCENT)
    surface.blit(surf_title, (32, 16))
    surface.blit(surf_sub, (32, 45))

    # -------------------------------------------------------------------------
    # 2. ZONA CENTRAL: TARJETA DE TIEMPO SIMULADO Y VELOCIDAD
    # -------------------------------------------------------------------------
    clock_card = pygame.Rect(485, 14, 215, 62)
    draw_rounded_rect(surface, clock_card, COLOR_CARD_BG, radius=8, border_color=COLOR_PANEL_LIGHT, border_width=1)

    # Formato de tiempo simulado
    hours = int(sim_time_sec // 3600)
    minutes = int((sim_time_sec % 3600) // 60)
    seconds = int(sim_time_sec % 60)
    time_str = f"TIEMPO: {hours:02d}h {minutes:02d}m {seconds:02d}s"
    surf_time = font_clock.render(time_str, True, COLOR_CYAN)
    surface.blit(surf_time, (495, 20))

    # Estado y multiplicador
    if is_paused:
        status_str = "● EN PAUSA (ESPACIO)"
        status_color = COLOR_YELLOW
    else:
        status_str = f"▶ VELOCIDAD: {speed_mult:.0f}x"
        status_color = COLOR_GREEN

    surf_status = font_clock.render(status_str, True, status_color)
    surface.blit(surf_status, (495, 44))

    # -------------------------------------------------------------------------
    # 3. ZONA DERECHA: PANEL DE CONTROLES INTERACTIVOS (NÍTIDO Y VISUAL)
    # -------------------------------------------------------------------------
    controls_card = pygame.Rect(715, 14, w - 30 - 715, 62)
    draw_rounded_rect(surface, controls_card, COLOR_CARD_BG, radius=8, border_color=COLOR_PANEL_LIGHT, border_width=1)

    # Encabezado de controles
    surf_ctrl_header = font_hud_title.render("CONTROLES DE TECLADO (INTERACTIVOS):", True, COLOR_ACCENT)
    surface.blit(surf_ctrl_header, (728, 18))

    # Fila de teclas mecánicas estilizadas
    curr_x = 728
    key_y = 38
    curr_x += draw_keycap(surface, "ESPACIO", "Pausar", curr_x, key_y, font_key, font_lbl)
    curr_x += draw_keycap(surface, "TAB", "Cambiar P1/P2", curr_x, key_y, font_key, font_lbl)
    curr_x += draw_keycap(surface, "1-5", "Velocidad", curr_x, key_y, font_key, font_lbl)
    curr_x += draw_keycap(surface, "ESC", "Salir", curr_x, key_y, font_key, font_lbl)
