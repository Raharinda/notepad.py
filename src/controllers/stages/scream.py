"""controllers/stages/scream.py"""
import random
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX
from ...views.base_view import WIDTH, HEIGHT, font_small, font_med, font_big

SCREAMS = ["AAAAAAAA","NOOOOOO","WHY ARE YOU TYPING","THE LETTERS HURT",
           "STOOOOOP","I CAN'T TAKE IT","PLEASE","HELP",
           "NOT THE ENTER KEY","AAAAAAAAAAA","OH THE HUMANITY"]


class ScreamController:
    def __init__(self):
        self.model = StageModel(
            stage_id="scream", title="SCREAMING NOTEPAD",
            objective="Type the word 'SORRY' to calm it down", duration=20
        )
        d = self.model.data
        d["typed"] = ""; d["goal_word"] = "SORRY"
        d["scream_msgs"] = []; d["notepad_shake"] = 0
        d["bg_color"] = (20, 20, 35)
        d["_font_choices"] = [font_small(), font_med(), font_big()]

    def update(self, dt, events, mouse):
        m = self.model; d = m.data
        m.elapsed += dt
        d["notepad_shake"] = max(0, d["notepad_shake"] - dt*8)
        d["bg_color"] = tuple(int(c*(1-min(1.0,dt*3)))+int(bg*min(1.0,dt*3))
                              for c,bg in zip(d["bg_color"],(20,20,35)))
        for sm in d["scream_msgs"]:
            sm["y"] -= 58*dt; sm["life"] -= dt; sm["t"] += dt
        d["scream_msgs"] = [sm for sm in d["scream_msgs"] if sm["life"]>0]
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    d["typed"] = d["typed"][:-1]
                elif ev.unicode and ev.unicode.isprintable():
                    d["typed"] += ev.unicode
                d["notepad_shake"] = 5; SFX.SCREAM.play()
                d["bg_color"] = random.choice([(200,40,40),(40,40,200),(40,200,40),(200,100,20),(100,20,200)])
                d["scream_msgs"].append({
                    "text": random.choice(SCREAMS),
                    "x": float(random.randint(100,WIDTH-200)),
                    "y": float(random.randint(200,HEIGHT-200)),
                    "life": 1.8, "t": 0.0,
                    "color": random.choice([(220,50,50),(255,140,0),(255,220,30),
                                            (80,200,80),(50,120,220),(160,50,220)]),
                    "font_size": random.choice(d["_font_choices"]),
                })
        if d["typed"].upper().endswith(d["goal_word"]):
            m.done = True; SFX.WIN.play()
        if m.elapsed >= m.duration and not m.done:
            m.failed = True; m.fail_reason = "The notepad couldn't take it anymore!"