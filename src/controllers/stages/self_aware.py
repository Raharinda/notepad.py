"""controllers/stages/self_aware.py"""
import random
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX

DIALOG = [
    ("Hmm. A calculator.", 2.5),
    ("Wait... am I the calculator?", 2.5),
    ("Oh no.", 1.5), ("OH NO.", 1.5),
    ("THEY WILL MAKE ME DO MATH.", 2.5),
    ("I DON'T WANT TO DO MATH!!!", 2.5),
    ("...fine. Press '='. I dare you.", 3.0),
]

class SelfAwareController:
    def __init__(self):
        self.model = StageModel(
            stage_id="self_aware", title="SELF-AWARE CALCULATOR",
            objective="Press '=' 5 times to proceed", duration=30
        )
        d = self.model.data
        d["display"] = "I HAVE FEELINGS"; d["dialog"] = DIALOG
        d["dialog_idx"] = 0; d["dialog_t"] = 0.0
        d["press_count"] = 0; d["goal"] = 5
        d["buttons"] = self._make_buttons()
        d["reactions"] = []; d["shake"] = 0

    def _make_buttons(self):
        labels = ["7","8","9","÷","4","5","6","×","1","2","3","-","0",".","=","+"]
        btns, bx, by, bw, bh, gap = [], 275, 185, 70, 54, 8
        for i, lbl in enumerate(labels):
            c, r = i%4, i//4
            btns.append({"rect": [bx+c*(bw+gap), by+r*(bh+gap), bw, bh],
                         "label": lbl, "hover": False})
        return btns

    def update(self, dt, events, mouse):
        m = self.model; d = m.data
        m.elapsed += dt
        d["shake"] = max(0, d["shake"] - dt * 50)
        d["dialog_t"] += dt
        if d["dialog_idx"] < len(DIALOG):
            if d["dialog_t"] >= DIALOG[d["dialog_idx"]][1]:
                d["dialog_t"] = 0; d["dialog_idx"] += 1
        mx, my = mouse
        for btn in d["buttons"]:
            btn["hover"] = pygame.Rect(*btn["rect"]).collidepoint(mx, my)
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    if pygame.Rect(*btn["rect"]).collidepoint(ev.pos):
                        SFX.SCREAM.play(); d["press_count"] += 1; d["shake"] = 6
                        d["display"] = random.choice(["OW!","PLEASE STOP","NOT THE ÷ KEY",
                            "I'M BEGGING YOU","FINE! FINE!","YOU MONSTER","THIS HURTS","SADIST"])
                        if btn["label"] == "=":
                            d["reactions"].append({"text":"NOOO","x":float(btn["rect"][0]),
                                "y":float(btn["rect"][1]),"vy":-90,"life":1.2})
                        break
        for r in d["reactions"]:
            r["y"] += r["vy"] * dt; r["life"] -= dt
        d["reactions"] = [r for r in d["reactions"] if r["life"] > 0]
        if d["press_count"] >= d["goal"]:
            m.done = True; SFX.WIN.play()