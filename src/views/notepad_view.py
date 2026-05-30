"""
views/notepad_view.py
Renders the notepad shell — always visible.
During stages, the content area is handed off to the stage view.
glitch_level 0.0 = perfectly normal, 1.0 = fully cursed frame.
"""
import math
import random
import pygame
from .base_view import (
    WIDTH, HEIGHT,
    WHITE, BLACK, NOTEPAD_BG, NOTEPAD_LINE, NOTEPAD_TEXT,
    RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PANEL,
    font_notepad, font_notepad_title, font_tiny, font_small,
    lerp_color, rainbow_color,
)

# ── Chrome dimensions (exported so stage views can clip to content area) ───
TITLE_H   = 32
TOOLBAR_H = 28
STATUS_H  = 22
MARGIN_L  = 48
MARGIN_R  = 12
LINE_H    = 22

# Content area rect (inside the notepad frame)
CONTENT_X = MARGIN_L
CONTENT_Y = TITLE_H + TOOLBAR_H
CONTENT_W = WIDTH  - MARGIN_L - MARGIN_R
CONTENT_H = HEIGHT - TITLE_H - TOOLBAR_H - STATUS_H


def get_content_rect() -> pygame.Rect:
    return pygame.Rect(CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H)


class NotepadView:
    def __init__(self):
        self._cursor_blink = 0.0
        self._glitch_t     = 0.0

    def update(self, dt: float):
        self._cursor_blink += dt
        self._glitch_t     += dt

    # ── Public draw calls ──────────────────────────────────────────────────

    def draw_notepad_phase(self, surf, notepad_model, game_state, mouse_pos):
        """Full draw for the fake notepad phase (editable text)."""
        g = game_state.glitch_level
        surf.fill(lerp_color((200, 200, 198), (15, 10, 25), g))
        self._draw_title_bar(surf, g, hud_text=None)
        self._draw_toolbar(surf, g)
        self._draw_content_bg(surf, g)
        self._draw_text(surf, notepad_model, g)
        self._draw_statusbar(surf, notepad_model, g, game_state.notepad_time, hud_text=None)

    def draw_stage_shell(self, surf, game_state, stage_model):
        """
        Draw only the notepad chrome during a stage.
        glitch_level is derived from stage index (0 → 1 over all stages).
        Content area is left for the stage view to fill.
        """
        total  = max(1, game_state.total_stages - 1)
        g      = min(1.0, game_state.stage_index / total)
        elapsed = stage_model.elapsed

        surf.fill(lerp_color((200, 200, 198), (10, 5, 20), g))
        self._draw_content_bg(surf, g)
        self._draw_title_bar(surf, g, hud_text=stage_model.title, elapsed=elapsed)
        self._draw_toolbar(surf, g, stage_index=game_state.stage_index,
                           total=game_state.total_stages)
        self._draw_statusbar(surf, None, g, elapsed,
                             hud_text=stage_model.objective,
                             remaining=stage_model.remaining,
                             duration=stage_model.duration)
        self._draw_frame_cracks(surf, g)

    # ── Chrome pieces ──────────────────────────────────────────────────────

    def _draw_title_bar(self, surf, g, hud_text=None, elapsed=0.0):
        bar_col = lerp_color((58, 58, 78), (120, 15, 15), g)
        pygame.draw.rect(surf, bar_col, (0, 0, WIDTH, TITLE_H))

        # wobble the bar at high glitch
        if g > 0.5:
            wobble = int(math.sin(elapsed * 12) * g * 3)
            pygame.draw.rect(surf, bar_col,
                             (0, TITLE_H - 2 + wobble, WIDTH, 4))

        pygame.draw.line(surf, lerp_color((90,90,110),(80,10,10), g),
                         (0, TITLE_H), (WIDTH, TITLE_H))

        # title text
        if hud_text:
            titles = [hud_text,
                      hud_text.replace('A','4').replace('E','3'),
                      "N0T3PAD.exe",
                      "pl3as3 h3lp",
                      "AAAAAAAAAA"]
            idx   = min(int(g * (len(titles)-1)), len(titles)-1)
            title = titles[idx]
        else:
            titles = ["Notepad", "N0tepad", "Notepa|d", "NOTEPAD.exe", "help me"]
            idx    = min(int(g * (len(titles)-1)), len(titles)-1)
            title  = titles[idx]

        if g > 0.6 and random.random() < g * 0.07:
            title = "".join(
                random.choice("!@#$░▒▓") if random.random() < g * 0.4 else c
                for c in title
            )

        f = font_small()
        s = f.render(title, True, WHITE)
        surf.blit(s, (WIDTH//2 - s.get_width()//2,
                      TITLE_H//2 - s.get_height()//2))

        # window control buttons
        for i, (cn, cg, lbl) in enumerate([
            ((210,70,70),  (220,20,20), "✕"),
            ((210,170,40), (170,50,170),"□"),
            ((70,170,70),  (20,190,90), "—"),
        ]):
            col  = lerp_color(cn, cg, g)
            bx   = WIDTH - 30 - i*34
            rect = pygame.Rect(bx, 5, 22, 21)
            pygame.draw.rect(surf, col, rect, border_radius=4)
            bs = font_tiny().render(lbl, True, WHITE)
            surf.blit(bs, (rect.centerx - bs.get_width()//2,
                           rect.centery - bs.get_height()//2))

    def _draw_toolbar(self, surf, g, stage_index=None, total=None):
        ty     = TITLE_H
        tb_col = lerp_color((235, 235, 232), (32, 16, 36), g)
        pygame.draw.rect(surf, tb_col, (0, ty, WIDTH, TOOLBAR_H))
        pygame.draw.line(surf, lerp_color((195,195,195),(70,25,70), g),
                         (0, ty+TOOLBAR_H), (WIDTH, ty+TOOLBAR_H))

        menus_n = ["File", "Edit", "Format", "View", "Help"]
        menus_g = ["Flee", "Exit", "Forget", "void",  "HELP"]
        f = font_tiny()
        for i, (mn, mg) in enumerate(zip(menus_n, menus_g)):
            label = mn if g < 0.45 else mg
            col   = lerp_color((45,45,45),(210,40,40), g)
            s     = f.render(label, True, col)
            surf.blit(s, (10 + i*82, ty + TOOLBAR_H//2 - s.get_height()//2))

        # stage pill on right side of toolbar
        if stage_index is not None:
            col  = rainbow_color(self._glitch_t)
            pill = f.render(f"STAGE {stage_index+1}/{total}", True, col)
            surf.blit(pill, (WIDTH - pill.get_width() - 10,
                             ty + TOOLBAR_H//2 - pill.get_height()//2))

    def _draw_content_bg(self, surf, g):
        area  = get_content_rect()
        bg    = lerp_color((252,252,248),(18,10,28), g)
        pygame.draw.rect(surf, bg, area)

        # gutter
        gc = lerp_color((228,230,233),(32,16,40), g)
        pygame.draw.rect(surf, gc, (0, CONTENT_Y, MARGIN_L, CONTENT_H))
        pygame.draw.line(surf, lerp_color((175,180,188),(72,28,72), g),
                         (MARGIN_L, CONTENT_Y), (MARGIN_L, CONTENT_Y+CONTENT_H))

        # horizontal guide lines
        for i in range(CONTENT_H // LINE_H + 1):
            ly  = CONTENT_Y + i * LINE_H
            col = lerp_color(NOTEPAD_LINE, (55,18,55), g)
            pygame.draw.line(surf, col, (MARGIN_L, ly), (WIDTH-MARGIN_R, ly))

    def _draw_text(self, surf, model, g):
        fn     = font_notepad()
        fln    = font_tiny()
        scroll = model.scroll_offset
        area   = get_content_rect()

        for i, raw_line in enumerate(model.lines):
            vy = CONTENT_Y + (i - scroll) * LINE_H + 3
            if vy < CONTENT_Y - LINE_H:
                continue
            if vy > CONTENT_Y + CONTENT_H:
                break

            # line number
            lnum_col = lerp_color((155,158,165),(95,38,95), g)
            lnum_s   = fln.render(str(i+1), True, lnum_col)
            surf.blit(lnum_s, (MARGIN_L - lnum_s.get_width() - 4,
                               vy + LINE_H//2 - lnum_s.get_height()//2))

            # text with optional glitch
            display = self._apply_text_glitch(raw_line, g, i) if g > 0.25 else raw_line
            tc = lerp_color(NOTEPAD_TEXT, (195,45,45), g)
            ts = fn.render(display, True, tc)
            ox = int(math.sin(self._glitch_t * 4 + i) * g * 2)
            surf.blit(ts, (MARGIN_L + 4 + ox, vy))

            # cursor
            if i == model.cursor_line and int(self._cursor_blink * 2) % 2 == 0:
                cw  = fn.size(raw_line[:model.cursor_col])[0]
                cc  = lerp_color((25,25,25),(215,45,45), g)
                pygame.draw.line(surf, cc,
                                 (MARGIN_L+4+cw, vy),
                                 (MARGIN_L+4+cw, vy+LINE_H-2), 2)

        # glitch overlay chars
        for gc_item in model.glitch_chars:
            gl, gco, gch, glife = gc_item
            vy = CONTENT_Y + (gl - scroll) * LINE_H + 3
            if CONTENT_Y <= vy <= CONTENT_Y + CONTENT_H:
                cw  = fn.size(model.lines[gl][:gco])[0] if gl < len(model.lines) else 0
                gs2 = fn.render(gch, True, (215, 45, 45))
                gs2.set_alpha(int(min(1.0, glife/1.5)*255))
                surf.blit(gs2, (MARGIN_L+4+cw, vy))

    def _apply_text_glitch(self, line, g, seed):
        chars = "░▒▓█▄▀■□"
        return "".join(
            random.choice(chars) if random.random() < g * 0.10 else c
            for c in line
        )

    def _draw_statusbar(self, surf, model, g, elapsed,
                        hud_text=None, remaining=None, duration=None):
        sy     = HEIGHT - STATUS_H
        sb_col = lerp_color((205,205,202),(22,12,28), g)
        pygame.draw.rect(surf, sb_col, (0, sy, WIDTH, STATUS_H))
        pygame.draw.line(surf, lerp_color((175,175,175),(55,18,55), g),
                         (0, sy), (WIDTH, sy))
        f   = font_tiny()
        col = lerp_color((75,75,75),(175,45,45), g)

        # left: objective or cursor pos
        if hud_text:
            obj = f.render(f"► {hud_text}", True, lerp_color(CYAN,(220,50,50),g))
            surf.blit(obj, (8, sy + STATUS_H//2 - obj.get_height()//2))
        elif model:
            ln_s = f.render(f"Ln {model.cursor_line+1}, Col {model.cursor_col+1}",
                            True, col)
            surf.blit(ln_s, (8, sy + STATUS_H//2 - ln_s.get_height()//2))

        # right: timer bar or encoding
        if remaining is not None and duration:
            bar_w  = 150
            bar_h  = 8
            bx     = WIDTH - bar_w - 8
            by     = sy + STATUS_H//2 - bar_h//2
            filled = int(remaining / duration * bar_w)
            pygame.draw.rect(surf, PANEL, (bx, by, bar_w, bar_h), border_radius=4)
            if filled > 0:
                urgency = 1.0 - remaining / duration
                tc      = rainbow_color(elapsed) if urgency < 0.6 \
                          else lerp_color(YELLOW, RED, (urgency-0.6)/0.4)
                pygame.draw.rect(surf, tc, (bx, by, filled, bar_h), border_radius=4)
            pygame.draw.rect(surf, WHITE, (bx, by, bar_w, bar_h), 1, border_radius=4)
        else:
            encs = ["UTF-8","UTF-8","UTF-???","???-8","HELP","SEND HELP"]
            idx  = min(int(g*(len(encs)-1)), len(encs)-1)
            es   = f.render(encs[idx], True, col)
            surf.blit(es, (WIDTH - es.get_width() - 8,
                           sy + STATUS_H//2 - es.get_height()//2))

        # center warning
        if g > 0.12:
            warn = f.render("something is wrong...", True,
                            lerp_color((170,70,70),(215,25,25), g))
            warn.set_alpha(int(g * 190))
            surf.blit(warn, (WIDTH//2 - warn.get_width()//2,
                             sy + STATUS_H//2 - warn.get_height()//2))

    def _draw_frame_cracks(self, surf, g):
        """Progressively crack/corrupt the notepad border."""
        if g < 0.3:
            return
        intensity = (g - 0.3) / 0.7
        random.seed(int(g * 10))   # stable cracks per glitch level
        for _ in range(int(intensity * 18)):
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            x2 = x1 + random.randint(-60, 60)
            y2 = y1 + random.randint(-40, 40)
            col = random.choice([(220,30,30),(255,100,0),(180,0,180),(0,200,200)])
            pygame.draw.line(surf, col, (x1,y1), (x2,y2),
                             random.randint(1, max(1, int(intensity*3))))
        random.seed()  # restore randomness