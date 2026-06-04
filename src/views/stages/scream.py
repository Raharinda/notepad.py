"""views/stages/scream.py"""
import math
import pygame
from ..base_view import (WHITE, font_small, font_tiny)
from ..notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect
CX=CONTENT_X; CY=CONTENT_Y; CW=CONTENT_W; CH=CONTENT_H; CR=CX+CW; CB=CY+CH
def _clip(s): s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)

class ScreamView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        ns = d.get("notepad_shake",0); t = stage_model.elapsed
        ox = int(math.sin(t*22)*ns); oy = int(math.cos(t*18)*ns)
        _clip(surf)
        bg = d.get("bg_color",(245,245,242))
        bg = tuple(min(255,int(c*0.7+245*0.3)) for c in bg)
        pygame.draw.rect(surf,bg,get_content_rect())
        pad = pygame.Rect(CX+10+ox,CY+10+oy,CW-20,CH-20)
        pygame.draw.rect(surf,WHITE,pad,border_radius=4)
        pygame.draw.rect(surf,(180,180,180),pad,1,border_radius=4)
        for i in range(8):
            ly = pad.top+30+i*32
            pygame.draw.line(surf,(200,215,230),(pad.left+8,ly),(pad.right-8,ly))
        typed = d.get("typed","")
        ts = font_small().render(typed[-45:]+("|" if int(t*4)%2==0 else ""),True,(30,30,30))
        surf.blit(ts,(pad.left+10,pad.top+32))
        goal = d.get("goal_word","SORRY")
        matched = sum(1 for i,c in enumerate(typed.upper()) if i<len(goal) and c==goal[i])
        hs = font_tiny().render(f"Type '{goal}' ({matched}/{len(goal)})",True,(120,120,130))
        surf.blit(hs,(pad.left+10,pad.bottom-18))
        for m in d.get("scream_msgs",[]):
            a = m["life"]/1.8
            ss = m["font_size"].render(m["text"],True,m["color"]); ss.set_alpha(int(a*255))
            sx = max(CX,min(CR-ss.get_width(),int(m["x"])))
            sy2= max(CY,min(CB-ss.get_height(),int(m["y"])))
            surf.blit(ss,(sx,sy2))
        _unclip(surf)