"""views/stages/red_circle.py"""
import math
import random

import pygame
from ..base_view import (
    WHITE, BLACK, RED, GREEN, ORANGE, YELLOW, CYAN, PURPLE,
    font_tiny, font_small,
    lerp_color, shake_offset,
)
from ..notepad_view import (
    CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect,
)

CX = CONTENT_X
CY = CONTENT_Y
CW = CONTENT_W
CH = CONTENT_H
CB = CY + CH
CR = CX + CW

SAFE_W, SAFE_H = 90, 60
HOLD_REQUIRED  = 3.0


def _clip(s):  s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)


class RedCircleView:
    def draw(self, surf, model, stage_model):
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))
        t  = stage_model.elapsed

        _clip(surf)

        # ── background (flashes red when caught) ──────────────────────
        wf  = d.get("warning_flash", 0.0)
        bg  = lerp_color((245, 245, 242), (200, 30, 30), wf * 0.35)
        pygame.draw.rect(surf, bg, get_content_rect())

        fn  = font_tiny()
        fs  = font_small()

        # ── ambient creepy text ────────────────────────────────────────
        msgs = ["I SEE YOU", "COME HERE", "WHY DO YOU RUN", "HEHEHE", "ALMOST"]
        for i, m in enumerate(msgs):
            s   = fn.render(m, True, RED)
            alpha = int(abs(math.sin(t * 2 + i * 1.3)) * 140 + 30)
            s.set_alpha(alpha)
            surf.blit(s, (CX + 6 + i * 155, CB - 52 + (i % 2) * 14))

        # ── safe zone ─────────────────────────────────────────────────
        sr    = d.get("safe_rect", [CX + CW//2 - 45, CY + CH//2 - 30, SAFE_W, SAFE_H])
        hold  = d.get("safe_hold", 0.0)
        blink = d.get("safe_blink", 0.0)
        progress = hold / HOLD_REQUIRED

        # zone color pulses green when active, muted when not
        if d.get("safe_active", False):
            zone_alpha = int(180 + math.sin(blink * 10) * 50)
            zone_col   = (40, 210, 80)
        else:
            zone_alpha = int(90 + math.sin(blink * 3) * 30)
            zone_col   = (60, 170, 100)

        zone_surf = pygame.Surface((sr[2], sr[3]), pygame.SRCALPHA)
        zone_surf.fill((*zone_col, zone_alpha))
        surf.blit(zone_surf, (sr[0] + ox, sr[1] + oy))
        pygame.draw.rect(surf, zone_col,
                         (sr[0] + ox, sr[1] + oy, sr[2], sr[3]), 2,
                         border_radius=4)

        # progress bar inside safe zone
        if hold > 0:
            bar_w = int(sr[2] * progress)
            pb_surf = pygame.Surface((bar_w, 6), pygame.SRCALPHA)
            pb_surf.fill((255, 255, 80, 200))
            surf.blit(pb_surf, (sr[0] + ox, sr[1] + sr[3] - 8 + oy))

        # label
        lbl = fn.render(f"HOLD {HOLD_REQUIRED - hold:.1f}s", True, (20, 80, 40))
        surf.blit(lbl, (sr[0] + sr[2]//2 - lbl.get_width()//2 + ox,
                        sr[1] + sr[3]//2 - lbl.get_height()//2 + oy))

        # ── particles (all circles) ────────────────────────────────────
        for c in d.get("circles", []):
            for p in c.get("particles", []):
                a   = p["life"] / p["max_life"]
                col = lerp_color(ORANGE, RED, 1 - a)
                pygame.draw.circle(
                    surf, col,
                    (int(p["x"] + ox), int(p["y"] + oy)),
                    max(1, int(5 * a)),
                )

        # ── draw each circle ──────────────────────────────────────────
        circle_list = d.get("circles", [])
        for i, c in enumerate(circle_list):
            cx2, cy2 = int(c["cx"] + ox), int(c["cy"] + oy)
            r        = c["r"]
            anger    = c.get("anger", 0.0)
            surge    = c.get("surge_speed", 0.0) > 0

            pulse = int(4 * math.sin(t * 8 + i * 1.7))

            # body color — surging circles turn bright orange-white
            if surge:
                body_col = lerp_color(ORANGE, (255, 230, 180), 0.6)
            else:
                body_col = lerp_color(ORANGE, RED, anger)

            pygame.draw.circle(surf, body_col, (cx2, cy2), r + pulse)
            pygame.draw.circle(surf, (80, 80, 80), (cx2, cy2), r + pulse, 2)

            # eyes — angrier = more furrowed
            for ex, ey in [(-11, -9), (11, -9)]:
                pygame.draw.circle(surf, WHITE, (cx2 + ex, cy2 + ey), 6)
                pygame.draw.circle(surf, BLACK, (cx2 + ex + 2, cy2 + ey + 2), 3)
                if anger > 0.5:
                    # angry eyebrow
                    sign = 1 if ex < 0 else -1
                    pygame.draw.line(
                        surf, BLACK,
                        (cx2 + ex - 5, cy2 + ey - 8 - int(anger * 4)),
                        (cx2 + ex + 5 * sign, cy2 + ey - 5),
                        2,
                    )

            # mouth — bigger smile = angrier
            pygame.draw.aalines(
                surf, (50, 50, 50), False,
                [
                    (cx2 - 13, cy2 + 10),
                    (cx2, cy2 + 16 + int(anger * 10)),
                    (cx2 + 13, cy2 + 10),
                ],
            )

            # circle ID badge for 2+
            if len(circle_list) > 1:
                id_s = fn.render(str(i + 1), True, WHITE)
                surf.blit(id_s, (cx2 - id_s.get_width()//2, cy2 - id_s.get_height()//2 - 1))

        # ── surge warning ──────────────────────────────────────────────
        if d.get("surging", False):
            ws  = fs.render("⚡ SPEED SURGE ⚡", True, YELLOW)
            ws.set_alpha(int(abs(math.sin(t * 12)) * 230 + 25))
            surf.blit(ws, (CX + CW//2 - ws.get_width()//2, CY + 8))

        # ── taunt text ─────────────────────────────────────────────────
        taunt = d.get("taunt", "")
        tlife = d.get("taunt_life", 0.0)
        if taunt and tlife > 0:
            alpha = int((tlife / 1.6) * 230)
            ts    = fs.render(taunt, True, RED)
            ts.set_alpha(alpha)
            tp = d.get("taunt_pos", (CX + CW//2, CY + 40))
            surf.blit(ts, (int(tp[0] + ox) - ts.get_width()//2, int(tp[1] + oy)))

        # ── circle count indicator (top right of content) ─────────────
        count     = len(d.get("circles", []))
        max_count = 4
        dot_x     = CR - 14
        for di in range(max_count):
            dot_y   = CY + 16 + di * 14
            dot_col = RED if di < count else (180, 180, 180)
            pygame.draw.circle(surf, dot_col, (dot_x, dot_y), 5)

        # ── hold progress hint ─────────────────────────────────────────
        hold = d.get("safe_hold", 0.0)
        hs   = fn.render(
            f"Safe zone: {hold:.1f}/{HOLD_REQUIRED:.0f}s",
            True, (60, 140, 60),
        )
        surf.blit(hs, (CX + 6, CB - 18))

        _unclip(surf)