"""controllers/stages/gravity.py"""
import random
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX
from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H


class GravityController:
    def __init__(self):
        self.model = StageModel(
            stage_id="gravity", title="GRAVITY CALCULATOR",
            objective="Click '=' before all buttons hit the floor!", duration=22
        )
        d = self.model.data
        d["buttons"] = self._make_buttons()
        d["display"] = "HELP IM FALLING"
        d["gravity"] = 80.0
        d["floor"] = CONTENT_Y + CONTENT_H - 20
        d["eq_clicks"] = 0; d["goal"] = 3; d["shake"] = 0

    def _make_buttons(self):
        labels = ["7","8","9","÷","4","5","6","×","1","2","3","-","0",".","=","+"]
        btns = []
        bw, bh, gap = 62, 46, 6
        bx = CONTENT_X + 60; by = CONTENT_Y + 60
        for i, lbl in enumerate(labels):
            c, r = i%4, i//4
            btns.append({
                "label": lbl,
                "x": float(bx+c*(bw+gap)), "y": float(by+r*(bh+gap)),
                "vy": random.uniform(-15,5), "bw": bw, "bh": bh,
                "on_floor": False,
                "color": random.choice([(220,50,50),(255,140,0),(80,200,80),
                    (50,120,220),(160,50,220),(255,80,160),(30,210,210)]),
                "bounce": random.uniform(0.3,0.65),
            })
        return btns

    def update(self, dt, events, mouse):
        m = self.model; d = m.data
        m.elapsed += dt
        d["shake"] = max(0, d["shake"]-dt*50)
        d["gravity"] += dt*6
        all_fallen = True
        for btn in d["buttons"]:
            if not btn["on_floor"]:
                all_fallen = False
                btn["vy"] += d["gravity"]*dt
                btn["y"]  += btn["vy"]*dt*60
                floor_y = d["floor"]-btn["bh"]
                if btn["y"] >= floor_y:
                    btn["y"] = floor_y
                    btn["vy"] = -btn["vy"]*btn["bounce"]
                    if abs(btn["vy"]) < 4:
                        btn["on_floor"] = True; btn["vy"] = 0
                    SFX.BLOOP.play()
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    if pygame.Rect(int(btn["x"]),int(btn["y"]),btn["bw"],btn["bh"]).collidepoint(ev.pos):
                        if btn["label"] == "=":
                            d["eq_clicks"] += 1; d["shake"] = 5; SFX.CORRECT.play()
                            d["display"] = random.choice(["WHEEE","I'M FLYING","OH NO","GRAVITY++","ZOOM"])
                            btn["vy"] = -320; btn["on_floor"] = False
                        else:
                            SFX.CLICK.play(); btn["vy"] = -200; btn["on_floor"] = False
                        break
        if d["eq_clicks"] >= d["goal"]:
            m.done = True; SFX.WIN.play()
        if all_fallen and not m.done:
            m.failed = True; m.fail_reason = "All buttons fell! No more '=' to click."