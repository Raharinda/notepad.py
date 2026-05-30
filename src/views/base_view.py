"""
views/base_view.py
Shared drawing helpers, fonts, and color palette.
All views inherit or import from here.
"""
import math
import random
import pygame

WIDTH,  HEIGHT = 900, 650

# ── Palette ────────────────────────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
RED     = (220,  50,  50)
GREEN   = ( 80, 200,  80)
BLUE    = ( 50, 120, 220)
YELLOW  = (255, 220,  30)
ORANGE  = (255, 140,   0)
PURPLE  = (160,  50, 220)
CYAN    = ( 30, 210, 210)
PINK    = (255,  80, 160)
BG      = ( 20,  20,  35)
PANEL   = ( 35,  35,  55)
NOTEPAD_BG    = (252, 252, 248)
NOTEPAD_LINE  = (180, 200, 220)
NOTEPAD_TEXT  = ( 30,  30,  30)
NOTEPAD_TITLE = ( 50,  50,  80)

RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]

# ── Fonts (lazy init so we can import before pygame.init) ──────────────────
_fonts: dict = {}

def get_font(name: str = "monospace", size: int = 16, bold: bool = False):
    key = (name, size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]

def font_big():   return get_font("monospace", 32, True)
def font_med():   return get_font("monospace", 22)
def font_small(): return get_font("monospace", 16)
def font_tiny():  return get_font("monospace", 12)
def font_notepad(): return get_font("monospace", 17)
def font_notepad_title(): return get_font("monospace", 13)


# ── Drawing helpers ────────────────────────────────────────────────────────
def draw_rect_shadow(surf, color, rect, radius=6, shadow_offset=4):
    shadow = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset,
                         rect.width, rect.height)
    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 90),
                     shadow_surf.get_rect(), border_radius=radius)
    surf.blit(shadow_surf, (shadow.x, shadow.y))
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def draw_text_center(surf, text: str, font, color, cx: int, cy: int):
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))


def rainbow_color(t: float, speed: float = 2.0):
    idx = (t * speed) % len(RAINBOW)
    a   = RAINBOW[int(idx) % len(RAINBOW)]
    b   = RAINBOW[(int(idx) + 1) % len(RAINBOW)]
    f   = idx - int(idx)
    return tuple(int(a[i] * (1 - f) + b[i] * f) for i in range(3))


def lerp_color(c1, c2, t: float):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


def shake_offset(amount: float = 5):
    """Return a random (ox, oy) offset for screen shake."""
    if amount <= 0:
        return (0, 0)
    a = int(amount)
    return (random.randint(-a, a), random.randint(-a, a))