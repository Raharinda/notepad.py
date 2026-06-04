"""controllers/stages/teleport.py"""
import random
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX
from ...views.base_view import WIDTH, HEIGHT
from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H


class TeleportController:
    TAUNTS = ["TOO SLOW","HAHA","MISS!","NOPE","TRY AGAIN",
              "PATHETIC","LOL","ZOOM!","BYE!",":)","WHEEE"]

    def __init__(self):
        self.model = StageModel(
            stage_id="teleport", title="TELEPORTING BUTTON",
            objective="Click the button 3 times!", duration=25
        )
        d = self.model.data
        d["btn_rect"] = [WIDTH//2-60, 350, 120, 50]
        d["clicks"] = 0; d["goal"] = 3; d["trail"] = []
        d["last_taunt"] = ""; d["taunt_pos"] = (WIDTH//2, HEIGHT//2)
        d["taunt_life"] = 0.0; d["shake"] = 0

    def _teleport(self):
        d = self.model.data; r = d["btn_rect"]
        d["trail"].append({"x": r[0]+r[2]//2, "y": r[1]+r[3]//2, "life": 1.0})
        margin = 20
        d["btn_rect"] = [
            random.randint(CONTENT_X+margin, CONTENT_X+CONTENT_W-margin-r[2]),
            random.randint(CONTENT_Y+margin, CONTENT_Y+CONTENT_H-margin-r[3]),
            r[2], r[3],
        ]
        d["last_taunt"] = random.choice(self.TAUNTS)
        d["taunt_pos"] = (d["btn_rect"][0]+r[2]//2, d["btn_rect"][1]-25)
        d["taunt_life"] = 1.5
        SFX.POP.play()

    def update(self, dt, events, mouse):
        m = self.model; d = m.data
        m.elapsed += dt
        d["shake"] = max(0, d["shake"] - dt*50)
        d["taunt_life"] = max(0, d["taunt_life"] - dt)
        for t in d["trail"]:
            t["life"] -= dt * 2
        d["trail"] = [t for t in d["trail"] if t["life"] > 0]
        if pygame.Rect(*d["btn_rect"]).collidepoint(mouse):
            self._teleport()
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(*d["btn_rect"]).collidepoint(ev.pos):
                    d["clicks"] += 1; SFX.WIN.play()
                    if d["clicks"] >= d["goal"]:
                        m.done = True
        if m.elapsed >= m.duration and not m.done:
            m.failed = True; m.fail_reason = "The button was too fast for you!"