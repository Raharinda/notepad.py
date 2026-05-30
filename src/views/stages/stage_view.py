"""
views/stages/stage_views.py
One View class per stage.  Each only reads model data — no logic.
"""
import math
import random
import pygame
from ..base_view import (
    WIDTH, HEIGHT,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN, PINK,
    BG, PANEL, RAINBOW,
    font_big, font_med, font_small, font_tiny,
    draw_rect_shadow, draw_text_center,
    rainbow_color, lerp_color, shake_offset,
)


# ── helpers ────────────────────────────────────────────────────────────────
def _draw_bg(surf):
    surf.fill(BG)


# ══════════════════════════════════════════════════════════════════════════
# STAGE 1 — Red Circle
# ══════════════════════════════════════════════════════════════════════════
class RedCircleView:
    def draw(self, surf: pygame.Surface, model, stage_model):
        _draw_bg(surf)
        d = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))

        # floating angry messages
        msgs = ["I SEE YOU", "COME HERE", "WHY DO YOU RUN", "HEHEHE"]
        fn   = font_small()
        for i, m in enumerate(msgs):
            alpha = int(abs(math.sin(stage_model.elapsed * 2 + i)) * 160 + 40)
            s = fn.render(m, True, RED)
            s.set_alpha(alpha)
            surf.blit(s, (40 + i * 200, HEIGHT - 70 - i * 5))

        # particles
        for p in d.get("particles", []):
            a   = p["life"] / p["max_life"]
            col = lerp_color(ORANGE, RED, 1 - a)
            pygame.draw.circle(surf, col,
                               (int(p["x"] + ox), int(p["y"] + oy)),
                               max(1, int(5 * a)))

        # the circle
        cx, cy = int(d["cx"] + ox), int(d["cy"] + oy)
        r_size = d["r"]
        pulse  = int(4 * math.sin(stage_model.elapsed * 8))
        anger  = d.get("anger", 0.0)
        col    = lerp_color(ORANGE, RED, anger)
        pygame.draw.circle(surf, col, (cx, cy), r_size + pulse)
        pygame.draw.circle(surf, WHITE, (cx, cy), r_size + pulse, 2)

        # eyes
        for ex, ey in [(-11, -9), (11, -9)]:
            pygame.draw.circle(surf, WHITE, (cx + ex, cy + ey), 6)
            pygame.draw.circle(surf, BLACK, (cx + ex + 2, cy + ey + 2), 3)

        # mouth
        pts = [(cx - 13, cy + 10),
               (cx,      cy + 16 + int(anger * 9)),
               (cx + 13, cy + 10)]
        pygame.draw.aalines(surf, WHITE, False, pts)

        # hp / survive hint
        fn2 = font_tiny()
        t   = fn2.render("Survive without getting caught!", True, YELLOW)
        surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT - 28))


# ══════════════════════════════════════════════════════════════════════════
# STAGE 2 — Self-Aware Calculator
# ══════════════════════════════════════════════════════════════════════════
class SelfAwareView:
    def draw(self, surf: pygame.Surface, model, stage_model):
        _draw_bg(surf)
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))

        # panel
        panel = pygame.Rect(260 + ox, 110 + oy, 390, 420)
        pygame.draw.rect(surf, PANEL, panel, border_radius=10)
        pygame.draw.rect(surf, CYAN,  panel, 2,  border_radius=10)

        # display
        disp = pygame.Rect(270 + ox, 120 + oy, 370, 52)
        pygame.draw.rect(surf, BLACK, disp, border_radius=6)
        fn = font_med()
        ds = fn.render(d.get("display", ""), True, GREEN)
        surf.blit(ds, (disp.right - ds.get_width() - 6,
                       disp.centery - ds.get_height() // 2))

        # buttons
        for btn in d.get("buttons", []):
            lbl = btn["label"]
            col = ORANGE if lbl == "=" else (PURPLE if lbl in "÷×-+" else BLUE)
            if btn.get("hover"):
                col = tuple(min(255, c + 60) for c in col)
            r = pygame.Rect(*btn["rect"]).move(ox, oy)
            draw_rect_shadow(surf, col, r, radius=5)
            bs = font_small().render(lbl, True, WHITE)
            surf.blit(bs, (r.centerx - bs.get_width()  // 2,
                           r.centery - bs.get_height() // 2))

        # face (left of panel)
        fx, fy = 150, 240
        press  = d.get("press_count", 0)
        pygame.draw.circle(surf, YELLOW, (fx, fy), 52)
        for ex in [-16, 16]:
            if press > 4:
                for sign in [-1, 1]:
                    pygame.draw.line(surf, BLACK,
                                     (fx+ex - 7*sign, fy-15 - 7),
                                     (fx+ex + 7*sign, fy-15 + 7), 3)
            else:
                pygame.draw.circle(surf, BLACK, (fx+ex, fy-15), 7)
        mouth = [(fx-20, fy+15),
                 (fx,    fy + (25 + press*2 if press < 5 else 5)),
                 (fx+20, fy+15)]
        pygame.draw.aalines(surf, BLACK, False, mouth)

        # dialog bubble
        dialog_idx = d.get("dialog_idx", 0)
        DIALOG     = d.get("dialog", [])
        if dialog_idx < len(DIALOG):
            txt     = DIALOG[dialog_idx][0]
            bub_w   = max(180, len(txt) * 10 + 20)
            bub_x   = 155 - bub_w // 2
            bub_y   = 320
            pygame.draw.rect(surf, WHITE, (bub_x, bub_y, bub_w, 38), border_radius=8)
            pygame.draw.polygon(surf, WHITE,
                                [(bub_x+18, bub_y+38),
                                 (bub_x+8,  bub_y+52),
                                 (bub_x+34, bub_y+38)])
            ts = font_tiny().render(txt, True, BLACK)
            surf.blit(ts, (bub_x + bub_w//2 - ts.get_width()//2, bub_y + 10))

        # floating reactions
        for r in d.get("reactions", []):
            a  = r["life"] / 1.2
            s  = font_med().render(r["text"], True, RED)
            s.set_alpha(int(a * 255))
            surf.blit(s, (int(r["x"] + ox), int(r["y"] + oy)))

        # objective progress
        pc = d.get("press_count", 0)
        goal = d.get("goal", 5)
        fn2  = font_tiny()
        prog = fn2.render(f"Press '=' {goal - pc} more times to proceed", True, YELLOW)
        surf.blit(prog, (WIDTH//2 - prog.get_width()//2, HEIGHT - 28))


# ══════════════════════════════════════════════════════════════════════════
# STAGE 3 — Broken Calculator
# ══════════════════════════════════════════════════════════════════════════
class BrokenCalcView:
    def draw(self, surf: pygame.Surface, model, stage_model):
        _draw_bg(surf)
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))

        # glitchy display
        disp = pygame.Rect(100 + ox, 58 + oy, WIDTH - 200, 48)
        pygame.draw.rect(surf, BLACK, disp, border_radius=6)
        pygame.draw.rect(surf, RED,   disp, 2, border_radius=6)
        txt = d.get("display", "ERROR")
        if random.random() < 0.12:
            txt = "".join(
                random.choice("!@#$░▒▓") if random.random() < 0.3 else c
                for c in txt
            )
        ds = font_med().render(txt, True, GREEN)
        surf.blit(ds, (disp.right - ds.get_width() - 8,
                       disp.centery - ds.get_height() // 2))

        # mistakes counter
        mistakes = d.get("mistakes", 0)
        max_m    = d.get("max_mistakes", 3)
        fn  = font_small()
        ms  = fn.render(f"Wrong clicks: {mistakes}/{max_m}", True,
                        lerp_color(YELLOW, RED, mistakes / max(1, max_m)))
        surf.blit(ms, (10, 62))

        # scattered buttons
        for btn in d.get("buttons", []):
            tmp = pygame.Surface((btn["bw"] + 4, btn["bh"] + 4), pygame.SRCALPHA)
            col = btn["color"]
            if btn.get("hover"):
                col = tuple(min(255, c + 80) for c in col)
            if btn.get("is_target"):
                pulse = int(4 * math.sin(stage_model.elapsed * 8))
                col   = lerp_color(col, WHITE, 0.4 + 0.3 * math.sin(stage_model.elapsed * 6))
                pygame.draw.rect(tmp, col,
                                 (2, 2, btn["bw"] + pulse, btn["bh"] + pulse),
                                 border_radius=5)
            else:
                pygame.draw.rect(tmp, col, (2, 2, btn["bw"], btn["bh"]), border_radius=5)
            ls = font_tiny().render(btn["label"], True, WHITE)
            tmp.blit(ls, (tmp.get_width()//2 - ls.get_width()//2,
                          tmp.get_height()//2 - ls.get_height()//2))
            rot = pygame.transform.rotate(tmp, btn.get("angle", 0)
                                          + math.sin(btn.get("wobble", 0)) * 4)
            cx  = int(btn["x"] + ox) - rot.get_width() // 2
            cy  = int(btn["y"] + oy) - rot.get_height() // 2
            surf.blit(rot, (cx, cy))

        fn2 = font_tiny()
        hint = fn2.render("Find and click '=' to proceed!", True, CYAN)
        surf.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))


# ══════════════════════════════════════════════════════════════════════════
# STAGE 4 — Teleporting Button
# ══════════════════════════════════════════════════════════════════════════
class TeleportView:
    def draw(self, surf: pygame.Surface, model, stage_model):
        _draw_bg(surf)
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))

        for t in d.get("trail", []):
            a   = t["life"]
            col = lerp_color(BG, CYAN, a)
            pygame.draw.circle(surf, col, (int(t["x"]+ox), int(t["y"]+oy)),
                                int(28 * a))

        btn = d.get("btn_rect", (WIDTH//2-70, HEIGHT//2-30, 140, 60))
        r   = pygame.Rect(*btn).move(ox, oy)
        pulse = int(4 * math.sin(stage_model.elapsed * 10))
        rp    = r.inflate(pulse * 2, pulse * 2)
        pygame.draw.rect(surf, PURPLE, rp, border_radius=12)
        pygame.draw.rect(surf, WHITE,  rp, 2, border_radius=12)
        bs = font_med().render("CLICK ME", True, WHITE)
        surf.blit(bs, (rp.centerx - bs.get_width()//2,
                       rp.centery - bs.get_height()//2))

        clicks = d.get("clicks", 0)
        goal   = d.get("goal", 3)
        cs = font_small().render(f"Clicks: {clicks}/{goal}", True, YELLOW)
        surf.blit(cs, (WIDTH//2 - cs.get_width()//2, HEIGHT - 50))

        taunt      = d.get("last_taunt", "")
        taunt_life = d.get("taunt_life", 0)
        if taunt_life > 0:
            a   = taunt_life / 1.5
            ts  = font_med().render(taunt, True, ORANGE)
            ts.set_alpha(int(a * 255))
            tp  = d.get("taunt_pos", (WIDTH//2, HEIGHT//2))
            surf.blit(ts, (int(tp[0]+ox) - ts.get_width()//2, int(tp[1]+oy)))


# ══════════════════════════════════════════════════════════════════════════
# STAGE 5 — Shy Buttons
# ══════════════════════════════════════════════════════════════════════════
class ShyButtonsView:
    def draw(self, surf: pygame.Surface, model, stage_model):
        _draw_bg(surf)
        d = stage_model.data

        hint = font_small().render("Click all the buttons... if you can.", True, PINK)
        surf.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 46))

        clicked    = d.get("clicked_set", set())
        total_btns = len(d.get("buttons", []))
        prog = font_tiny().render(
            f"Clicked: {len(clicked)}/{total_btns}", True, YELLOW)
        surf.blit(prog, (WIDTH//2 - prog.get_width()//2, HEIGHT - 28))

        for btn in d.get("buttons", []):
            b   = btn.get("blushing", 0.0)
            col = lerp_color(BLUE, PINK, b)
            if btn.get("clicked"):
                col = GREEN
            r   = pygame.Rect(int(btn["x"]) - 35, int(btn["y"]) - 20, 70, 40)
            draw_rect_shadow(surf, col, r, radius=8)
            if b > 0.3 and not btn.get("clicked"):
                for bx2 in [r.left + 8, r.right - 8]:
                    pygame.draw.circle(surf, (255, 100, 100), (bx2, r.centery + 4), 5)
            bs = font_tiny().render(btn["label"], True, WHITE)
            surf.blit(bs, (r.centerx - bs.get_width()//2,
                           r.centery - bs.get_height()//2))


# ══════════════════════════════════════════════════════════════════════════
# STAGE 6 — Screaming Notepad
# ══════════════════════════════════════════════════════════════════════════
class ScreamView:
    def draw(self, surf: pygame.Surface, model, stage_model):
        d  = stage_model.data
        bg = d.get("bg_color", BG)
        surf.fill(bg)

        ns    = d.get("notepad_shake", 0)
        t     = stage_model.elapsed
        ox    = int(math.sin(t * 22) * ns)
        oy    = int(math.cos(t * 18) * ns)

        pad   = pygame.Rect(100 + ox, 100 + oy, WIDTH - 200, HEIGHT - 200)
        pygame.draw.rect(surf, WHITE, pad, border_radius=8)
        pygame.draw.rect(surf, BLACK, pad, 2, border_radius=8)

        for i in range(9):
            ly = pad.top + 50 + i * 40
            pygame.draw.line(surf, (180, 200, 220),
                             (pad.left + 10, ly), (pad.right - 10, ly))

        typed = d.get("typed", "")
        goal  = d.get("goal_word", "SORRY")
        ts    = font_small().render(
            typed[-55:] + ("|" if int(t * 4) % 2 == 0 else ""), True, BLACK)
        surf.blit(ts, (pad.left + 14, pad.top + 54))

        # progress hint
        matched = sum(1 for i, c in enumerate(typed.upper())
                      if i < len(goal) and c == goal[i])
        hint = font_tiny().render(
            f"Type '{goal}' to calm it down ({matched}/{len(goal)})", True, (100,100,120))
        surf.blit(hint, (pad.left + 14, pad.bottom - 20))

        for m in d.get("scream_msgs", []):
            a  = m["life"] / 1.8
            ss = m["font_size"].render(m["text"], True, m["color"])
            ss.set_alpha(int(a * 255))
            surf.blit(ss, (int(m["x"]), int(m["y"])))


# ══════════════════════════════════════════════════════════════════════════
# STAGE 7 — Gravity Calculator
# ══════════════════════════════════════════════════════════════════════════
class GravityView:
    def draw(self, surf: pygame.Surface, model, stage_model):
        _draw_bg(surf)
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))

        floor_y = d.get("floor", HEIGHT - 30)
        pygame.draw.line(surf, ORANGE,
                         (0, floor_y + oy), (WIDTH, floor_y + oy), 3)

        disp = pygame.Rect(260 + ox, 100 + oy, 380, 44)
        pygame.draw.rect(surf, BLACK, disp, border_radius=6)
        pygame.draw.rect(surf, GREEN, disp, 2, border_radius=6)
        ds = font_med().render(d.get("display", ""), True, GREEN)
        surf.blit(ds, (disp.right - ds.get_width() - 6,
                       disp.centery - ds.get_height() // 2))

        grav_text = font_tiny().render(
            f"GRAVITY: {int(d.get('gravity', 80))} (and rising...)", True, RED)
        surf.blit(grav_text, (10, HEIGHT - 25))

        clicks_left = d.get("goal", 1) - d.get("eq_clicks", 0)
        prog = font_small().render(
            f"Click '=' {clicks_left} more time(s) before it falls!", True, YELLOW)
        surf.blit(prog, (WIDTH//2 - prog.get_width()//2, HEIGHT - 46))

        for btn in d.get("buttons", []):
            r = pygame.Rect(int(btn["x"] + ox), int(btn["y"] + oy),
                            btn["bw"], btn["bh"])
            draw_rect_shadow(surf, btn["color"], r, radius=5, shadow_offset=3)
            bs = font_small().render(btn["label"], True, WHITE)
            surf.blit(bs, (r.centerx - bs.get_width()//2,
                           r.centery - bs.get_height()//2))