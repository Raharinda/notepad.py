"""
views/stages/stage_views.py
Each stage view draws ONLY inside the notepad content area.
The notepad shell (title bar, toolbar, statusbar) is drawn by NotepadView.
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
from ..notepad_view import (
    CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H,
    MARGIN_L, get_content_rect,
)

# Shorthand content bounds
CX = CONTENT_X   # left edge of content
CY = CONTENT_Y   # top edge of content
CW = CONTENT_W
CH = CONTENT_H
CR = CX + CW     # right edge
CB = CY + CH     # bottom edge


def _clip(surf):
    """Set clip rect to content area."""
    surf.set_clip(get_content_rect())

def _unclip(surf):
    surf.set_clip(None)

def _fill_content(surf, color):
    pygame.draw.rect(surf, color, get_content_rect())


# ══════════════════════════════════════════════════════════════════════════
# STAGE 1 — Red Circle
# ══════════════════════════════════════════════════════════════════════════
class RedCircleView:
    def draw(self, surf, model, stage_model):
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))
        _clip(surf)
        _fill_content(surf, (245, 245, 242))

        # angry messages floating
        msgs = ["I SEE YOU", "COME HERE", "WHY DO YOU RUN", "HEHEHE"]
        fn   = font_tiny()
        for i, m in enumerate(msgs):
            alpha = int(abs(math.sin(stage_model.elapsed * 2 + i)) * 150 + 40)
            s = fn.render(m, True, RED)
            s.set_alpha(alpha)
            surf.blit(s, (CX + 10 + i * 170, CB - 60 + i * 4))

        # particles
        for p in d.get("particles", []):
            a   = p["life"] / p["max_life"]
            col = lerp_color(ORANGE, RED, 1 - a)
            pygame.draw.circle(surf, col,
                               (int(p["x"] + ox), int(p["y"] + oy)),
                               max(1, int(5 * a)))

        # circle
        cx2  = int(d["cx"] + ox)
        cy2  = int(d["cy"] + oy)
        r    = d["r"]
        pulse = int(4 * math.sin(stage_model.elapsed * 8))
        anger = d.get("anger", 0.0)
        col   = lerp_color(ORANGE, RED, anger)
        pygame.draw.circle(surf, col, (cx2, cy2), r + pulse)
        pygame.draw.circle(surf, (80, 80, 80), (cx2, cy2), r + pulse, 2)

        for ex, ey in [(-11, -9), (11, -9)]:
            pygame.draw.circle(surf, WHITE, (cx2+ex, cy2+ey), 6)
            pygame.draw.circle(surf, BLACK, (cx2+ex+2, cy2+ey+2), 3)
        pts = [(cx2-13, cy2+10),
               (cx2,    cy2+16+int(anger*9)),
               (cx2+13, cy2+10)]
        pygame.draw.aalines(surf, (50, 50, 50), False, pts)

        _unclip(surf)


# ══════════════════════════════════════════════════════════════════════════
# STAGE 2 — Self-Aware Calculator
# ══════════════════════════════════════════════════════════════════════════
class SelfAwareView:
    def draw(self, surf, model, stage_model):
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))
        _clip(surf)
        _fill_content(surf, (245, 245, 242))

        # calculator panel — centered in content area
        pw, ph = 340, 370
        px = CX + CW//2 - pw//2 + ox
        py = CY + 10    + oy
        pygame.draw.rect(surf, (220, 220, 218), (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(surf, (160, 160, 158), (px, py, pw, ph), 2, border_radius=8)

        # display strip
        disp = pygame.Rect(px+8, py+8, pw-16, 44)
        pygame.draw.rect(surf, (30, 30, 30), disp, border_radius=4)
        ds = font_small().render(d.get("display",""), True, GREEN)
        surf.blit(ds, (disp.right - ds.get_width() - 6,
                       disp.centery - ds.get_height()//2))

        # buttons
        for btn in d.get("buttons", []):
            lbl = btn["label"]
            col = ORANGE if lbl=="=" else (PURPLE if lbl in "÷×-+" else BLUE)
            if btn.get("hover"):
                col = tuple(min(255,c+55) for c in col)
            # offset button rects relative to content area
            br  = pygame.Rect(*btn["rect"])
            # remap from absolute to inside panel
            rel = br.move(px - (CX + CW//2 - pw//2), py - CY - 10)
            rel = rel.move(ox, oy)
            draw_rect_shadow(surf, col, rel, radius=4)
            bs = font_tiny().render(lbl, True, WHITE)
            surf.blit(bs, (rel.centerx - bs.get_width()//2,
                           rel.centery - bs.get_height()//2))

        # face (left of panel)
        fx, fy = CX + 60 + ox, CY + CH//2 - 20 + oy
        press  = d.get("press_count", 0)
        pygame.draw.circle(surf, YELLOW, (fx, fy), 44)
        for ex in [-13, 13]:
            if press > 4:
                for sign in [-1,1]:
                    pygame.draw.line(surf, BLACK,
                                     (fx+ex-6*sign, fy-12-6),
                                     (fx+ex+6*sign, fy-12+6), 2)
            else:
                pygame.draw.circle(surf, BLACK, (fx+ex, fy-12), 6)
        mouth = [(fx-16, fy+12),
                 (fx,    fy+(22+press*2 if press<5 else 4)),
                 (fx+16, fy+12)]
        pygame.draw.aalines(surf, BLACK, False, mouth)

        # dialog bubble
        DIALOG     = d.get("dialog", [])
        dialog_idx = d.get("dialog_idx", 0)
        if dialog_idx < len(DIALOG):
            txt   = DIALOG[dialog_idx][0]
            bub_w = max(160, len(txt)*9+16)
            bub_x = fx - bub_w//2
            bub_y = fy - 90
            pygame.draw.rect(surf, WHITE, (bub_x, bub_y, bub_w, 32), border_radius=6)
            pygame.draw.polygon(surf, WHITE,
                                [(bub_x+14, bub_y+32),
                                 (bub_x+6,  bub_y+44),
                                 (bub_x+28, bub_y+32)])
            ts = font_tiny().render(txt, True, BLACK)
            surf.blit(ts, (bub_x+bub_w//2-ts.get_width()//2, bub_y+8))

        # floating reactions
        for r in d.get("reactions", []):
            a = r["life"]/1.2
            s = font_small().render(r["text"], True, RED)
            s.set_alpha(int(a*255))
            surf.blit(s, (int(r["x"]+ox), int(r["y"]+oy)))

        # progress
        pc   = d.get("press_count",0)
        goal = d.get("goal",5)
        ps   = font_tiny().render(f"Press '=' {goal-pc} more times", True, (100,100,100))
        surf.blit(ps, (CX+8, CB-18))

        _unclip(surf)


# ══════════════════════════════════════════════════════════════════════════
# STAGE 3 — Broken Calculator
# ══════════════════════════════════════════════════════════════════════════
class BrokenCalcView:
    def draw(self, surf, model, stage_model):
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake", 0))
        _clip(surf)
        _fill_content(surf, (245, 242, 240))

        # glitchy display bar
        disp = pygame.Rect(CX+10+ox, CY+8+oy, CW-20, 38)
        pygame.draw.rect(surf, (30, 30, 30), disp, border_radius=4)
        pygame.draw.rect(surf, RED, disp, 2, border_radius=4)
        txt = d.get("display","ERROR")
        if random.random() < 0.12:
            txt = "".join(random.choice("!@#$░▒▓") if random.random()<0.3 else c
                          for c in txt)
        ds = font_small().render(txt, True, GREEN)
        surf.blit(ds, (disp.right - ds.get_width()-6,
                       disp.centery - ds.get_height()//2))

        # mistake counter
        mistakes = d.get("mistakes",0)
        maxm     = d.get("max_mistakes",3)
        ms = font_tiny().render(f"Wrong: {mistakes}/{maxm}", True,
                                lerp_color(YELLOW,RED, mistakes/max(1,maxm)))
        surf.blit(ms, (CX+10, CY+52))

        # scattered buttons (coords are absolute, just clipped)
        for btn in d.get("buttons",[]):
            tmp = pygame.Surface((btn["bw"]+4, btn["bh"]+4), pygame.SRCALPHA)
            col = btn["color"]
            if btn.get("hover"):
                col = tuple(min(255,c+80) for c in col)
            if btn.get("is_target"):
                col = lerp_color(col, WHITE, 0.35+0.25*math.sin(stage_model.elapsed*7))
            pygame.draw.rect(tmp, col, (2,2,btn["bw"],btn["bh"]), border_radius=4)
            ls = font_tiny().render(btn["label"], True, WHITE)
            tmp.blit(ls, (tmp.get_width()//2-ls.get_width()//2,
                          tmp.get_height()//2-ls.get_height()//2))
            rot = pygame.transform.rotate(tmp,
                  btn.get("angle",0)+math.sin(btn.get("wobble",0))*4)
            surf.blit(rot, (int(btn["x"]+ox)-rot.get_width()//2,
                            int(btn["y"]+oy)-rot.get_height()//2))

        hs = font_tiny().render("Find '=' and click it!", True, (100,100,100))
        surf.blit(hs, (CX+8, CB-18))
        _unclip(surf)


# ══════════════════════════════════════════════════════════════════════════
# STAGE 4 — Teleporting Button
# ══════════════════════════════════════════════════════════════════════════
class TeleportView:
    def draw(self, surf, model, stage_model):
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake",0))
        _clip(surf)
        _fill_content(surf, (242, 242, 248))

        for t in d.get("trail",[]):
            a   = t["life"]
            col = lerp_color((242,242,248), CYAN, a)
            pygame.draw.circle(surf, col,
                               (int(t["x"]+ox), int(t["y"]+oy)),
                               int(24*a))

        btn  = d.get("btn_rect",[CX+CW//2-60, CY+CH//2-25, 120, 50])
        r    = pygame.Rect(*btn).move(ox,oy)
        pulse = int(3*math.sin(stage_model.elapsed*10))
        rp    = r.inflate(pulse*2, pulse*2)
        pygame.draw.rect(surf, PURPLE, rp, border_radius=10)
        pygame.draw.rect(surf, (180,180,180), rp, 1, border_radius=10)
        bs = font_small().render("CLICK ME", True, WHITE)
        surf.blit(bs, (rp.centerx-bs.get_width()//2, rp.centery-bs.get_height()//2))

        clicks = d.get("clicks",0)
        goal   = d.get("goal",3)
        cs = font_tiny().render(f"Clicks: {clicks}/{goal}", True, (80,80,80))
        surf.blit(cs, (CX+8, CB-18))

        taunt      = d.get("last_taunt","")
        taunt_life = d.get("taunt_life",0)
        if taunt_life > 0:
            a  = taunt_life/1.5
            ts = font_small().render(taunt, True, RED)
            ts.set_alpha(int(a*255))
            tp = d.get("taunt_pos",(CX+CW//2, CY+CH//2))
            surf.blit(ts, (int(tp[0]+ox)-ts.get_width()//2, int(tp[1]+oy)))

        _unclip(surf)


# ══════════════════════════════════════════════════════════════════════════
# STAGE 5 — Shy Buttons
# ══════════════════════════════════════════════════════════════════════════
class ShyButtonsView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        _clip(surf)
        _fill_content(surf, (245, 242, 248))

        clicked    = d.get("clicked_set", set())
        total_btns = len(d.get("buttons",[]))
        ps = font_tiny().render(f"Clicked: {len(clicked)}/{total_btns}", True, (80,80,80))
        surf.blit(ps, (CX+8, CB-18))

        for btn in d.get("buttons",[]):
            b   = btn.get("blushing",0.0)
            col = lerp_color(BLUE, PINK, b) if not btn.get("clicked") else GREEN
            r   = pygame.Rect(int(btn["x"])-32, int(btn["y"])-18, 64, 36)
            draw_rect_shadow(surf, col, r, radius=6)
            if b > 0.3 and not btn.get("clicked"):
                for bx2 in [r.left+7, r.right-7]:
                    pygame.draw.circle(surf, (255,110,110), (bx2, r.centery+3), 4)
            bs = font_tiny().render(btn["label"], True, WHITE)
            surf.blit(bs, (r.centerx-bs.get_width()//2, r.centery-bs.get_height()//2))

        _unclip(surf)


# ══════════════════════════════════════════════════════════════════════════
# STAGE 6 — Screaming Notepad
# ══════════════════════════════════════════════════════════════════════════
class ScreamView:
    def draw(self, surf, model, stage_model):
        d  = stage_model.data
        ns = d.get("notepad_shake", 0)
        t  = stage_model.elapsed
        ox = int(math.sin(t*22)*ns)
        oy = int(math.cos(t*18)*ns)

        _clip(surf)
        bg = d.get("bg_color", (245,245,242))
        # lerp bg toward white quickly
        bg = tuple(min(255, int(c*0.7 + 245*0.3)) for c in bg)
        _fill_content(surf, bg)

        # inner paper (slightly inset)
        pad = pygame.Rect(CX+10+ox, CY+10+oy, CW-20, CH-20)
        pygame.draw.rect(surf, WHITE, pad, border_radius=4)
        pygame.draw.rect(surf, (180,180,180), pad, 1, border_radius=4)

        for i in range(8):
            ly = pad.top + 30 + i*32
            pygame.draw.line(surf, (200,215,230),
                             (pad.left+8, ly), (pad.right-8, ly))

        typed = d.get("typed","")
        ts = font_small().render(
            typed[-45:] + ("|" if int(t*4)%2==0 else ""), True, (30,30,30))
        surf.blit(ts, (pad.left+10, pad.top+32))

        goal    = d.get("goal_word","SORRY")
        matched = sum(1 for i,c in enumerate(typed.upper())
                      if i<len(goal) and c==goal[i])
        hs = font_tiny().render(
            f"Type '{goal}' ({matched}/{len(goal)})", True, (120,120,130))
        surf.blit(hs, (pad.left+10, pad.bottom-18))

        for m in d.get("scream_msgs",[]):
            a  = m["life"]/1.8
            ss = m["font_size"].render(m["text"], True, m["color"])
            ss.set_alpha(int(a*255))
            # clamp scream positions to content area
            sx = max(CX, min(CR-ss.get_width(),  int(m["x"])))
            sy2= max(CY, min(CB-ss.get_height(), int(m["y"])))
            surf.blit(ss, (sx, sy2))

        _unclip(surf)


# ══════════════════════════════════════════════════════════════════════════
# STAGE 7 — Gravity Calculator
# ══════════════════════════════════════════════════════════════════════════
class GravityView:
    def draw(self, surf, model, stage_model):
        d  = stage_model.data
        ox, oy = shake_offset(d.get("shake",0))
        _clip(surf)
        _fill_content(surf, (242, 245, 242))

        floor_y = d.get("floor", CB - 10)
        pygame.draw.line(surf, ORANGE,
                         (CX, floor_y+oy), (CR, floor_y+oy), 2)

        # display strip
        disp = pygame.Rect(CX+10+ox, CY+8+oy, CW-20, 36)
        pygame.draw.rect(surf, (30,30,30), disp, border_radius=4)
        pygame.draw.rect(surf, GREEN, disp, 1, border_radius=4)
        ds = font_small().render(d.get("display",""), True, GREEN)
        surf.blit(ds, (disp.right-ds.get_width()-5,
                       disp.centery-ds.get_height()//2))

        grav_s = font_tiny().render(
            f"GRAVITY: {int(d.get('gravity',80))} (rising...)", True, RED)
        surf.blit(grav_s, (CX+8, CB-18))

        eq_left = d.get("goal",3) - d.get("eq_clicks",0)
        ps = font_tiny().render(f"Click '=' {eq_left}x before it falls!", True,(80,80,80))
        surf.blit(ps, (CX+CW//2-ps.get_width()//2, CY+50))

        for btn in d.get("buttons",[]):
            r = pygame.Rect(int(btn["x"]+ox), int(btn["y"]+oy),
                            btn["bw"], btn["bh"])
            draw_rect_shadow(surf, btn["color"], r, radius=4, shadow_offset=2)
            bs = font_tiny().render(btn["label"], True, WHITE)
            surf.blit(bs, (r.centerx-bs.get_width()//2, r.centery-bs.get_height()//2))

        _unclip(surf)