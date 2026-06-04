"""views/stages/red_circle.py"""
import math, random
import pygame
from ..base_view import (WHITE, BLACK, RED, ORANGE, font_tiny,
    lerp_color, shake_offset)
from ..notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect
CX=CONTENT_X; CY=CONTENT_Y; CW=CONTENT_W; CH=CONTENT_H; CB=CY+CH
def _clip(s): s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)

class RedCircleView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        ox, oy = shake_offset(d.get("shake",0))
        _clip(surf)
        pygame.draw.rect(surf, (245,245,242), get_content_rect())
        fn = font_tiny()
        for i, m in enumerate(["I SEE YOU","COME HERE","WHY DO YOU RUN","HEHEHE"]):
            s = fn.render(m, True, RED)
            s.set_alpha(int(abs(math.sin(stage_model.elapsed*2+i))*150+40))
            surf.blit(s, (CX+10+i*170, CB-60+i*4))
        for p in d.get("particles",[]):
            a = p["life"]/p["max_life"]
            pygame.draw.circle(surf, lerp_color(ORANGE,RED,1-a),
                (int(p["x"]+ox),int(p["y"]+oy)), max(1,int(5*a)))
        cx2,cy2 = int(d["cx"]+ox), int(d["cy"]+oy)
        r = d["r"]; pulse = int(4*math.sin(stage_model.elapsed*8))
        anger = d.get("anger",0.0)
        pygame.draw.circle(surf, lerp_color(ORANGE,RED,anger), (cx2,cy2), r+pulse)
        pygame.draw.circle(surf, (80,80,80), (cx2,cy2), r+pulse, 2)
        for ex,ey in [(-11,-9),(11,-9)]:
            pygame.draw.circle(surf, WHITE, (cx2+ex,cy2+ey), 6)
            pygame.draw.circle(surf, BLACK, (cx2+ex+2,cy2+ey+2), 3)
        pygame.draw.aalines(surf,(50,50,50),False,
            [(cx2-13,cy2+10),(cx2,cy2+16+int(anger*9)),(cx2+13,cy2+10)])
        _unclip(surf)