"""views/stages/gravity.py"""
import pygame
from ..base_view import (WHITE, RED, GREEN, ORANGE, font_small, font_tiny,
    draw_rect_shadow, shake_offset)
from ..notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect
CX=CONTENT_X; CY=CONTENT_Y; CW=CONTENT_W; CB=CY+CONTENT_H; CR=CX+CW
def _clip(s): s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)

class GravityView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        ox,oy = shake_offset(d.get("shake",0))
        _clip(surf)
        pygame.draw.rect(surf,(242,245,242),get_content_rect())
        floor_y = d.get("floor",CB-10)
        pygame.draw.line(surf,ORANGE,(CX,floor_y+oy),(CR,floor_y+oy),2)
        disp = pygame.Rect(CX+10+ox,CY+8+oy,CW-20,36)
        pygame.draw.rect(surf,(30,30,30),disp,border_radius=4)
        pygame.draw.rect(surf,GREEN,disp,1,border_radius=4)
        ds = font_small().render(d.get("display",""),True,GREEN)
        surf.blit(ds,(disp.right-ds.get_width()-5,disp.centery-ds.get_height()//2))
        grav_s = font_tiny().render(f"GRAVITY: {int(d.get('gravity',80))} (rising...)",True,RED)
        surf.blit(grav_s,(CX+8,CB-18))
        eq_left = d.get("goal",3)-d.get("eq_clicks",0)
        ps = font_tiny().render(f"Click '=' {eq_left}x before it falls!",True,(80,80,80))
        surf.blit(ps,(CX+CW//2-ps.get_width()//2,CY+50))
        for btn in d.get("buttons",[]):
            r = pygame.Rect(int(btn["x"]+ox),int(btn["y"]+oy),btn["bw"],btn["bh"])
            draw_rect_shadow(surf,btn["color"],r,radius=4,shadow_offset=2)
            bs = font_tiny().render(btn["label"],True,WHITE)
            surf.blit(bs,(r.centerx-bs.get_width()//2,r.centery-bs.get_height()//2))
        _unclip(surf)