"""controllers/stages/shy_buttons.py"""
import math, random
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX
from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H


class ShyButtonsController:
    def __init__(self):
        self.model = StageModel(
            stage_id="shy_buttons", title="SHY BUTTONS",
            objective="Click all 12 buttons!", duration=22
        )
        d = self.model.data
        d["buttons"] = self._make_buttons()
        d["clicked_set"] = set()

    def _make_buttons(self):
        btns = []
        for i, lbl in enumerate(list("ABCDEFGHIJKL")):
            bx = CONTENT_X + 50 + (i%4)*195
            by = CONTENT_Y + 40 + (i//4)*110
            btns.append({"id":i,"label":lbl,"base_x":float(bx),"base_y":float(by),
                         "x":float(bx),"y":float(by),"vx":0.0,"vy":0.0,
                         "blushing":0.0,"clicked":False})
        return btns

    def update(self, dt, events, mouse):
        m = self.model; d = m.data
        m.elapsed += dt
        mx, my = mouse
        for btn in d["buttons"]:
            if btn["clicked"]: continue
            dx = btn["x"]-mx; dy = btn["y"]-my
            dist = math.hypot(dx, dy)
            if dist < 130 and dist > 1:
                force = (130-dist)/130*620
                btn["vx"] += (dx/dist)*force*dt; btn["vy"] += (dy/dist)*force*dt
                btn["blushing"] = min(1.0, btn["blushing"]+dt*3)
            else:
                btn["blushing"] = max(0.0, btn["blushing"]-dt*2)
            btn["vx"] += (btn["base_x"]-btn["x"])*4*dt
            btn["vy"] += (btn["base_y"]-btn["y"])*4*dt
            btn["vx"] *= 0.84; btn["vy"] *= 0.84
            btn["x"] += btn["vx"]*dt*60; btn["y"] += btn["vy"]*dt*60
            btn["x"] = max(CONTENT_X+35, min(CONTENT_X+CONTENT_W-35, btn["x"]))
            btn["y"] = max(CONTENT_Y+20, min(CONTENT_Y+CONTENT_H-20, btn["y"]))
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    if btn["clicked"]: continue
                    if pygame.Rect(int(btn["x"])-35,int(btn["y"])-20,70,40).collidepoint(ev.pos):
                        btn["clicked"] = True; d["clicked_set"].add(btn["id"])
                        SFX.POP.play(); break
        if len(d["clicked_set"]) >= len(d["buttons"]):
            m.done = True; SFX.WIN.play()
        if m.elapsed >= m.duration and not m.done:
            m.failed = True; m.fail_reason = "The buttons were too shy!"