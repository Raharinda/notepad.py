"""views/stages/shy_buttons.py"""
import pygame
from ..base_view import (WHITE, BLUE, GREEN, PINK, font_tiny,
    draw_rect_shadow, lerp_color)
from ..notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H, get_content_rect
CX=CONTENT_X; CB=CONTENT_Y+CONTENT_H
def _clip(s): s.set_clip(get_content_rect())
def _unclip(s): s.set_clip(None)

class ShyButtonsView:
    def draw(self, surf, model, stage_model):
        d = stage_model.data
        _clip(surf)
        pygame.draw.rect(surf,(245,242,248),get_content_rect())
        clicked = d.get("clicked_set",set())
        total   = len(d.get("buttons",[]))
        ps = font_tiny().render(f"Clicked: {len(clicked)}/{total}",True,(80,80,80))
        surf.blit(ps,(CX+8,CB-18))
        for btn in d.get("buttons",[]):
            b = btn.get("blushing",0.0)
            col = lerp_color(BLUE,PINK,b) if not btn.get("clicked") else GREEN
            r = pygame.Rect(int(btn["x"])-32,int(btn["y"])-18,64,36)
            draw_rect_shadow(surf,col,r,radius=6)
            if b>0.3 and not btn.get("clicked"):
                for bx2 in [r.left+7,r.right-7]:
                    pygame.draw.circle(surf,(255,110,110),(bx2,r.centery+3),4)
            bs = font_tiny().render(btn["label"],True,WHITE)
            surf.blit(bs,(r.centerx-bs.get_width()//2,r.centery-bs.get_height()//2))
        _unclip(surf)