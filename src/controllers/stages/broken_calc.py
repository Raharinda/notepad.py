"""controllers/stages/broken_calc.py"""
import math, random
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX
from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H


class BrokenCalcController:
    def __init__(self):
        self.model = StageModel(
            stage_id="broken_calc", title="BROKEN CALCULATOR",
            objective="Find and click '=' — watch out for wrong buttons!", duration=20
        )
        d = self.model.data
        d["display"] = "ERROR_404_BRAIN"
        d["mistakes"] = 0; d["max_mistakes"] = 3
        d["buttons"] = self._scatter_buttons(); d["shake"] = 0

    def _scatter_buttons(self):
        labels = ["7","8","9","÷","4","5","6","×","1","2","3","-","0",".","=","+",
                  "C","±","%","←","sin","cos","tan","log","√"]
        btns, used = [], set()
        for lbl in labels:
            for _ in range(200):
                x = random.randint(CONTENT_X+30, CONTENT_X+CONTENT_W-80)
                y = random.randint(CONTENT_Y+50, CONTENT_Y+CONTENT_H-60)
                if all(abs(x-ux)>=68 or abs(y-uy)>=48 for ux,uy in used):
                    used.add((x,y))
                    btns.append({
                        "label": lbl, "x": float(x), "y": float(y),
                        "bw": 60, "bh": 42,
                        "color": random.choice([(220,50,50),(255,140,0),(80,200,80),
                            (50,120,220),(160,50,220),(255,80,160),(30,210,210)]),
                        "angle": random.uniform(-40,40),
                        "wobble": random.uniform(0,math.pi*2),
                        "hover": False, "is_target": lbl=="=",
                    })
                    break
        return btns

    def update(self, dt, events, mouse):
        m = self.model; d = m.data
        m.elapsed += dt
        d["shake"] = max(0, d["shake"] - dt * 50)
        mx, my = mouse
        for btn in d["buttons"]:
            r = pygame.Rect(int(btn["x"])-btn["bw"]//2, int(btn["y"])-btn["bh"]//2,
                            btn["bw"], btn["bh"])
            btn["hover"] = r.collidepoint(mx, my)
            btn["wobble"] += dt * random.uniform(1, 3)
            btn["x"] = max(CONTENT_X+20, min(CONTENT_X+CONTENT_W-20,
                                              btn["x"] + random.uniform(-0.6,0.6)))
            btn["y"] = max(CONTENT_Y+20, min(CONTENT_Y+CONTENT_H-20,
                                              btn["y"] + random.uniform(-0.6,0.6)))
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    r = pygame.Rect(int(btn["x"])-btn["bw"]//2,
                                    int(btn["y"])-btn["bh"]//2,
                                    btn["bw"], btn["bh"])
                    if r.collidepoint(ev.pos):
                        if btn["is_target"]:
                            SFX.WIN.play(); m.done = True
                        else:
                            SFX.WRONG.play(); d["mistakes"] += 1; d["shake"] = 8
                            d["display"] = random.choice(["WRONG!","NOPE","TRY AGAIN",
                                "HAHA","NOT EVEN CLOSE","SMH"])
                            if d["mistakes"] >= d["max_mistakes"]:
                                m.failed = True; m.fail_reason = "Too many wrong clicks!"
                        break