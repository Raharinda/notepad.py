"""views/stages/broken_calc.py"""
import math, random
import pygame
from ..base_view import (WHITE, RED, GREEN, YELLOW, font_small, font_tiny,
    lerp_color, shake_offset)
from ..notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect
CX=CONTENT_X; CY=CONTENT_Y; CW=CONTENT_W; CB=CY+CONTENT_H
def _clip(s): s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)

class BrokenCalcView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        ox, oy = shake_offset(d.get("shake",0))
        _clip(surf)
        pygame.draw.rect(surf,(245,242,240),get_content_rect())
        disp = pygame.Rect(CX+10+ox,CY+8+oy,CW-20,38)
        pygame.draw.rect(surf,(30,30,30),disp,border_radius=4)
        pygame.draw.rect(surf,RED,disp,2,border_radius=4)
        txt = d.get("display","ERROR")
        if random.random()<0.12:
            txt="".join(random.choice("!@#$░▒▓") if random.random()<0.3 else c for c in txt)
        ds = font_small().render(txt,True,GREEN)
        surf.blit(ds,(disp.right-ds.get_width()-6,disp.centery-ds.get_height()//2))
        mistakes,maxm = d.get("mistakes",0),d.get("max_mistakes",3)
        ms = font_tiny().render(f"Wrong: {mistakes}/{maxm}",True,
            lerp_color(YELLOW,RED,mistakes/max(1,maxm)))
        surf.blit(ms,(CX+10,CY+52))
        for btn in d.get("buttons",[]):
            tmp = pygame.Surface((btn["bw"]+4,btn["bh"]+4),pygame.SRCALPHA)
            col = btn["color"]
            if btn.get("hover"): col=tuple(min(255,c+80) for c in col)
            if btn.get("is_target"):
                col=lerp_color(col,WHITE,0.35+0.25*math.sin(stage_model.elapsed*7))
            pygame.draw.rect(tmp,col,(2,2,btn["bw"],btn["bh"]),border_radius=4)
            ls=font_tiny().render(btn["label"],True,WHITE)
            tmp.blit(ls,(tmp.get_width()//2-ls.get_width()//2,tmp.get_height()//2-ls.get_height()//2))
            rot=pygame.transform.rotate(tmp,btn.get("angle",0)+math.sin(btn.get("wobble",0))*4)
            surf.blit(rot,(int(btn["x"]+ox)-rot.get_width()//2,int(btn["y"]+oy)-rot.get_height()//2))
        hs=font_tiny().render("Find '=' and click it!",True,(100,100,100))
        surf.blit(hs,(CX+8,CB-18))
        _unclip(surf)