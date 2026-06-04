"""views/stages/teleport.py"""
import math
import pygame
from ..base_view import (WHITE, RED, CYAN, PURPLE, font_small, font_tiny,
    lerp_color, shake_offset)
from ..notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect
CX=CONTENT_X; CY=CONTENT_Y; CW=CONTENT_W; CH=CONTENT_H; CB=CY+CH
def _clip(s): s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)

class TeleportView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        ox,oy = shake_offset(d.get("shake",0))
        _clip(surf)
        pygame.draw.rect(surf,(242,242,248),get_content_rect())
        for t in d.get("trail",[]):
            a = t["life"]
            pygame.draw.circle(surf,lerp_color((242,242,248),CYAN,a),
                (int(t["x"]+ox),int(t["y"]+oy)),int(24*a))
        btn = d.get("btn_rect",[CX+CW//2-60,CY+CH//2-25,120,50])
        r = pygame.Rect(*btn).move(ox,oy)
        pulse = int(3*math.sin(stage_model.elapsed*10))
        rp = r.inflate(pulse*2,pulse*2)
        pygame.draw.rect(surf,PURPLE,rp,border_radius=10)
        pygame.draw.rect(surf,(180,180,180),rp,1,border_radius=10)
        bs = font_small().render("CLICK ME",True,WHITE)
        surf.blit(bs,(rp.centerx-bs.get_width()//2,rp.centery-bs.get_height()//2))
        clicks,goal = d.get("clicks",0),d.get("goal",3)
        cs = font_tiny().render(f"Clicks: {clicks}/{goal}",True,(80,80,80))
        surf.blit(cs,(CX+8,CB-18))
        taunt,tl = d.get("last_taunt",""),d.get("taunt_life",0)
        if tl > 0:
            a = tl/1.5
            ts = font_small().render(taunt,True,RED); ts.set_alpha(int(a*255))
            tp = d.get("taunt_pos",(CX+CW//2,CY+CH//2))
            surf.blit(ts,(int(tp[0]+ox)-ts.get_width()//2,int(tp[1]+oy)))
        _unclip(surf)