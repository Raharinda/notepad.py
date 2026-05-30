"""
views/notepad_view.py
Renders the "fake notepad" phase.
Glitch level 0 = perfectly normal. 1 = fully cursed.
"""
import math
import random
import pygame
from .base_view import (
    WIDTH, HEIGHT,
    WHITE, BLACK, NOTEPAD_BG, NOTEPAD_LINE, NOTEPAD_TEXT, NOTEPAD_TITLE,
    RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE,
    font_notepad, font_notepad_title, font_tiny, font_small,
    lerp_color, rainbow_color,
)

# Window chrome dimensions
TITLE_H   = 32
TOOLBAR_H = 28
STATUS_H  = 22
MARGIN_L  = 48   # line-number gutter
MARGIN_R  = 12
LINE_H    = 22


class NotepadView:
    def __init__(self):
        self._cursor_blink = 0.0
        self._glitch_t     = 0.0

    def update(self, dt: float):
        self._cursor_blink += dt
        self._glitch_t     += dt

    def draw(self, surf: pygame.Surface,
             notepad_model,
             game_state,
             mouse_pos: tuple):
        g = game_state.glitch_level   # 0.0 → 1.0
        self._draw_window(surf, g)
        self._draw_toolbar(surf, g)
        self._draw_text_area(surf, notepad_model, g)
        self._draw_statusbar(surf, notepad_model, g, game_state.notepad_time)

    # ── Chrome ─────────────────────────────────────────────────────────────
    def _draw_window(self, surf, g):
        # Title bar color shifts from normal grey → evil red
        bar_color = lerp_color((60, 60, 80), (140, 20, 20), g)
        pygame.draw.rect(surf, bar_color, (0, 0, WIDTH, TITLE_H))
        pygame.draw.line(surf, (100, 100, 120), (0, TITLE_H), (WIDTH, TITLE_H))

        # Title text
        titles = ["Notepad", "N0tepad", "Notepa|d", "NOTEPAD.exe", "help me"]
        idx    = min(int(g * (len(titles) - 1)), len(titles) - 1)
        title  = titles[idx]
        if g > 0.6 and random.random() < g * 0.08:
            title = "".join(
                random.choice("!@#$%^&*░▒▓") if random.random() < g * 0.5 else c
                for c in title
            )
        f  = font_small()
        s  = f.render(title, True, WHITE)
        surf.blit(s, (WIDTH // 2 - s.get_width() // 2, TITLE_H // 2 - s.get_height() // 2))

        # Window control buttons
        for i, (col_n, col_g, label) in enumerate([
            ((220, 80, 80),  (220,  30,  30), "✕"),
            ((220, 180, 50), (180,  60, 180), "□"),
            ((80, 180, 80),  ( 30, 200, 100), "—"),
        ]):
            col  = lerp_color(col_n, col_g, g)
            bx   = WIDTH - 32 - i * 36
            rect = pygame.Rect(bx, 5, 24, 22)
            pygame.draw.rect(surf, col, rect, border_radius=4)
            btn_f = font_tiny()
            bs    = btn_f.render(label, True, WHITE)
            surf.blit(bs, (rect.centerx - bs.get_width() // 2,
                           rect.centery - bs.get_height() // 2))

    def _draw_toolbar(self, surf, g):
        ty = TITLE_H
        toolbar_bg = lerp_color((240, 240, 238), (40, 20, 40), g)
        pygame.draw.rect(surf, toolbar_bg, (0, ty, WIDTH, TOOLBAR_H))
        pygame.draw.line(surf, lerp_color((200,200,200),(80,30,80), g),
                         (0, ty + TOOLBAR_H), (WIDTH, ty + TOOLBAR_H))

        menus_normal = ["File", "Edit", "Format", "View", "Help"]
        menus_glitch = ["Flee", "Exit", "Forget", "void", "HELP"]
        f = font_tiny()
        for i, (mn, mg) in enumerate(zip(menus_normal, menus_glitch)):
            label = mn if g < 0.5 else mg
            col   = lerp_color((50, 50, 50), (220, 50, 50), g)
            s     = f.render(label, True, col)
            surf.blit(s, (10 + i * 80, ty + TOOLBAR_H // 2 - s.get_height() // 2))

    # ── Text area ──────────────────────────────────────────────────────────
    def _draw_text_area(self, surf, model, g):
        area_top  = TITLE_H + TOOLBAR_H
        area_h    = HEIGHT - area_top - STATUS_H
        area_rect = pygame.Rect(0, area_top, WIDTH, area_h)

        bg = lerp_color((252, 252, 248), (25, 15, 30), g)
        pygame.draw.rect(surf, bg, area_rect)

        # line-number gutter
        gutter_col = lerp_color((230, 232, 235), (40, 20, 50), g)
        pygame.draw.rect(surf, gutter_col, (0, area_top, MARGIN_L, area_h))
        pygame.draw.line(surf, lerp_color((180,185,190),(80,30,80), g),
                         (MARGIN_L, area_top), (MARGIN_L, area_top + area_h))

        # horizontal guide lines
        for i in range(20):
            ly = area_top + i * LINE_H + 4
            if ly > area_top + area_h:
                break
            line_col = lerp_color(NOTEPAD_LINE, (60, 20, 60), g)
            pygame.draw.line(surf, line_col, (MARGIN_L, ly), (WIDTH - MARGIN_R, ly))

        fn   = font_notepad()
        fln  = font_tiny()
        scroll = model.scroll_offset

        for i, raw_line in enumerate(model.lines):
            vy = area_top + (i - scroll) * LINE_H + 4
            if vy < area_top - LINE_H:
                continue
            if vy > area_top + area_h:
                break

            # line number
            lnum_col = lerp_color((160, 160, 170), (100, 40, 100), g)
            lnum_s   = fln.render(str(i + 1), True, lnum_col)
            surf.blit(lnum_s, (MARGIN_L - lnum_s.get_width() - 4,
                               vy + LINE_H // 2 - lnum_s.get_height() // 2))

            # text content — glitch: random chars replace original
            display_line = raw_line
            if g > 0.3:
                display_line = self._apply_text_glitch(raw_line, g, i)

            text_col = lerp_color(NOTEPAD_TEXT, (200, 50, 50), g)
            ts = fn.render(display_line, True, text_col)

            # subtle wobble at high glitch
            wobble_x = int(math.sin(self._glitch_t * 4 + i) * g * 3)
            surf.blit(ts, (MARGIN_L + 4 + wobble_x, vy))

            # draw cursor on active line
            if (i == model.cursor_line
                    and int(self._cursor_blink * 2) % 2 == 0):
                col_w  = fn.size(raw_line[:model.cursor_col])[0]
                cursor_col = lerp_color((30, 30, 30), (220, 50, 50), g)
                pygame.draw.line(
                    surf, cursor_col,
                    (MARGIN_L + 4 + col_w, vy),
                    (MARGIN_L + 4 + col_w, vy + LINE_H - 2),
                    2
                )

        # overlay glitch chars
        for gc in model.glitch_chars:
            gl, gco, gch, glife = gc
            vy = area_top + (gl - scroll) * LINE_H + 4
            if area_top <= vy <= area_top + area_h:
                col_w = fn.size(model.lines[gl][:gco])[0] if gl < len(model.lines) else 0
                alpha = min(255, int(glife / 1.5 * 255))
                gs    = fn.render(gch, True, (220, 50, 50))
                gs.set_alpha(alpha)
                surf.blit(gs, (MARGIN_L + 4 + col_w, vy))

    def _apply_text_glitch(self, line: str, g: float, seed: int) -> str:
        glitch_chars = "░▒▓█▄▀■□▪▫◘◙"
        result       = []
        for ch in line:
            if random.random() < g * 0.12:
                result.append(random.choice(glitch_chars))
            else:
                result.append(ch)
        return "".join(result)

    # ── Status bar ─────────────────────────────────────────────────────────
    def _draw_statusbar(self, surf, model, g, notepad_time):
        sy = HEIGHT - STATUS_H
        sb_col = lerp_color((210, 210, 208), (30, 15, 35), g)
        pygame.draw.rect(surf, sb_col, (0, sy, WIDTH, STATUS_H))
        pygame.draw.line(surf, lerp_color((180,180,180),(60,20,60), g),
                         (0, sy), (WIDTH, sy))

        f   = font_tiny()
        col = lerp_color((80, 80, 80), (180, 50, 50), g)

        ln_s = f.render(
            f"Ln {model.cursor_line + 1}, Col {model.cursor_col + 1}",
            True, col
        )
        surf.blit(ln_s, (8, sy + STATUS_H // 2 - ln_s.get_height() // 2))

        status_msgs = ["UTF-8", "UTF-8", "UTF-???", "???-8", "HELP", "SEND HELP"]
        idx  = min(int(g * (len(status_msgs)-1)), len(status_msgs)-1)
        enc  = f.render(status_msgs[idx], True, col)
        surf.blit(enc, (WIDTH - enc.get_width() - 8,
                        sy + STATUS_H // 2 - enc.get_height() // 2))

        # subtle "time" counter only after glitch starts
        if g > 0.15:
            warn = f.render("something is wrong...", True,
                            lerp_color((180,80,80),(220,30,30), g))
            warn.set_alpha(int(g * 200))
            surf.blit(warn, (WIDTH // 2 - warn.get_width() // 2,
                             sy + STATUS_H // 2 - warn.get_height() // 2))