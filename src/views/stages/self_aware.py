"""views/stages/self_aware.py"""
import math
import pygame
from ..base_view import (WHITE, BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE,
    font_small, font_tiny, draw_rect_shadow, lerp_color, shake_offset)
from ..notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect
CX=CONTENT_X; CY=CONTENT_Y; CW=CONTENT_W; CH=CONTENT_H; CB=CY+CH
def _clip(s): s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)

class SelfAwareView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        ox, oy = shake_offset(d.get("shake",0))
        _clip(surf)
        pygame.draw.rect(surf, (245,245,242), get_content_rect())
        pw,ph = 340,370
        px = CX+CW//2-pw//2+ox; py = CY+10+oy
        pygame.draw.rect(surf,(220,220,218),(px,py,pw,ph),border_radius=8)
        pygame.draw.rect(surf,(160,160,158),(px,py,pw,ph),2,border_radius=8)
        disp = pygame.Rect(px+8,py+8,pw-16,44)
        pygame.draw.rect(surf,(30,30,30),disp,border_radius=4)
        ds = font_small().render(d.get("display",""),True,GREEN)
        surf.blit(ds,(disp.right-ds.get_width()-6,disp.centery-ds.get_height()//2))
        for btn in d.get("buttons",[]):
            lbl = btn["label"]
            col = ORANGE if lbl=="=" else (PURPLE if lbl in "÷×-+" else BLUE)
            if btn.get("hover"): col = tuple(min(255,c+55) for c in col)
            br = pygame.Rect(*btn["rect"])
            rel = br.move(px-(CX+CW//2-pw//2), py-CY-10).move(ox,oy)
            draw_rect_shadow(surf,col,rel,radius=4)
            bs = font_tiny().render(lbl,True,WHITE)
            surf.blit(bs,(rel.centerx-bs.get_width()//2,rel.centery-bs.get_height()//2))
        fx,fy = CX+60+ox, CY+CH//2-20+oy
        press = d.get("press_count",0)
        pygame.draw.circle(surf,YELLOW,(fx,fy),44)
        for ex in [-13,13]:
            if press>4:
                for sign in [-1,1]:
                    pygame.draw.line(surf,BLACK,(fx+ex-6*sign,fy-12-6),(fx+ex+6*sign,fy-12+6),2)
            else:
                pygame.draw.circle(surf,BLACK,(fx+ex,fy-12),6)
        pygame.draw.aalines(surf,BLACK,False,
            [(fx-16,fy+12),(fx,fy+(22+press*2 if press<5 else 4)),(fx+16,fy+12)])
        DIALOG = d.get("dialog",[]); di = d.get("dialog_idx",0)
        if di < len(DIALOG):
            txt = DIALOG[di][0]; bw2 = max(160,len(txt)*9+16)
            bx2,by2 = fx-bw2//2, fy-90
            pygame.draw.rect(surf,WHITE,(bx2,by2,bw2,32),border_radius=6)
            pygame.draw.polygon(surf,WHITE,[(bx2+14,by2+32),(bx2+6,by2+44),(bx2+28,by2+32)])
            ts = font_tiny().render(txt,True,BLACK)
            surf.blit(ts,(bx2+bw2//2-ts.get_width()//2,by2+8))
        for r in d.get("reactions",[]):
            a = r["life"]/1.2
            s = font_small().render(r["text"],True,RED); s.set_alpha(int(a*255))
            surf.blit(s,(int(r["x"]+ox),int(r["y"]+oy)))
        pc,goal = d.get("press_count",0), d.get("goal",5)
        ps = font_tiny().render(f"Press '=' {goal-pc} more times",True,(100,100,100))
        surf.blit(ps,(CX+8,CB-18))
        _unclip(surf)