"""
controllers/stages/stage_controllers.py
One Controller class per stage.
Each controller owns the StageModel it creates and mutates it each frame.
"""
import math
import random
import time
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX
from ...views.base_view import WIDTH, HEIGHT


def _make_model(stage_id, title, objective, duration) -> StageModel:
    return StageModel(
        stage_id  = stage_id,
        title     = title,
        objective = objective,
        duration  = duration,
    )


# ══════════════════════════════════════════════════════════════════════════
# STAGE 1 — Red Circle
# ══════════════════════════════════════════════════════════════════════════
class RedCircleController:
    def __init__(self):
        self.model = _make_model(
            "red_circle", "RED CIRCLE CHASING CURSOR",
            "Survive without getting caught!", 14
        )
        d = self.model.data
        d["cx"]        = float(450)
        d["cy"]        = float(380)
        d["r"]         = 34
        d["speed"]     = 115
        d["anger"]     = 0.0
        d["particles"] = []
        d["shake"]     = 0
        self._last_sfx = 0.0

    def update(self, dt: float, events, mouse: tuple):
        m  = self.model
        d  = m.data
        m.elapsed += dt
        d["shake"] = max(0, d["shake"] - dt * 50)

        mx, my = mouse
        dx = mx - d["cx"]
        dy = my - d["cy"]
        dist = math.hypot(dx, dy)

        d["anger"] = max(0.0, 1.0 - dist / 400)
        spd = d["speed"] + d["anger"] * 190
        if dist > 1:
            d["cx"] += (dx / dist) * spd * dt
            d["cy"] += (dy / dist) * spd * dt

        # caught?
        if dist < d["r"] + 6:
            d["shake"] = 10
            now = time.time()
            if now - self._last_sfx > 0.28:
                SFX.EVIL.play()
                self._last_sfx = now
            m.elapsed += dt * 1.5   # speed timer up as punishment
            if m.elapsed >= m.duration + 2:
                m.failed     = True
                m.fail_reason = "The circle caught you!"
                return

        # particles
        if random.random() < 0.25:
            d["particles"].append({
                "x":        d["cx"] + random.randint(-d["r"], d["r"]),
                "y":        d["cy"] + random.randint(-d["r"], d["r"]),
                "vx":       random.uniform(-55, 55),
                "vy":       random.uniform(-55, 55),
                "life":     random.uniform(0.4, 1.0),
                "max_life": 1.0,
            })
        for p in d["particles"]:
            p["x"]    += p["vx"] * dt
            p["y"]    += p["vy"] * dt
            p["life"] -= dt
        d["particles"] = [p for p in d["particles"] if p["life"] > 0]

        if m.elapsed >= m.duration:
            m.done = True


# ══════════════════════════════════════════════════════════════════════════
# STAGE 2 — Self-Aware Calculator
# ══════════════════════════════════════════════════════════════════════════
DIALOG = [
    ("Hmm. A calculator.",            2.5),
    ("Wait... am I the calculator?",  2.5),
    ("Oh no.",                        1.5),
    ("OH NO.",                        1.5),
    ("THEY WILL MAKE ME DO MATH.",    2.5),
    ("I DON'T WANT TO DO MATH!!!",    2.5),
    ("...fine. Press '='. I dare you.",3.0),
]

class SelfAwareController:
    def __init__(self):
        self.model = _make_model(
            "self_aware", "SELF-AWARE CALCULATOR",
            "Press '=' 5 times to proceed", 30
        )
        d = self.model.data
        d["display"]    = "I HAVE FEELINGS"
        d["dialog"]     = DIALOG
        d["dialog_idx"] = 0
        d["dialog_t"]   = 0.0
        d["press_count"]= 0
        d["goal"]       = 5
        d["buttons"]    = self._make_buttons()
        d["reactions"]  = []
        d["shake"]      = 0

    def _make_buttons(self):
        labels = ["7","8","9","÷","4","5","6","×","1","2","3","-","0",".","=","+"]
        btns, bx, by, bw, bh, gap = [], 275, 185, 70, 54, 8
        for i, lbl in enumerate(labels):
            c, r = i%4, i//4
            btns.append({
                "rect":  [bx + c*(bw+gap), by + r*(bh+gap), bw, bh],
                "label": lbl, "hover": False,
            })
        return btns

    def update(self, dt: float, events, mouse: tuple):
        m = self.model
        d = m.data
        m.elapsed   += dt
        d["shake"]   = max(0, d["shake"] - dt * 50)
        d["dialog_t"] += dt

        if d["dialog_idx"] < len(DIALOG):
            if d["dialog_t"] >= DIALOG[d["dialog_idx"]][1]:
                d["dialog_t"]   = 0
                d["dialog_idx"] += 1

        mx, my = mouse
        for btn in d["buttons"]:
            r = pygame.Rect(*btn["rect"])
            btn["hover"] = r.collidepoint(mx, my)

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    if pygame.Rect(*btn["rect"]).collidepoint(ev.pos):
                        SFX.SCREAM.play()
                        d["press_count"] += 1
                        d["shake"]        = 6
                        quips = ["OW!", "PLEASE STOP", "NOT THE ÷ KEY",
                                 "I'M BEGGING YOU", "FINE! FINE!", "YOU MONSTER",
                                 "THIS HURTS", "SADIST"]
                        d["display"] = random.choice(quips)
                        if btn["label"] == "=":
                            d["reactions"].append({
                                "text": "NOOO", "x": float(btn["rect"][0]),
                                "y": float(btn["rect"][1]), "vy": -90, "life": 1.2,
                            })
                        break

        for r in d["reactions"]:
            r["y"]    += r["vy"] * dt
            r["life"] -= dt
        d["reactions"] = [r for r in d["reactions"] if r["life"] > 0]

        if d["press_count"] >= d["goal"]:
            m.done = True
            SFX.WIN.play()


# ══════════════════════════════════════════════════════════════════════════
# STAGE 3 — Broken Calculator
# ══════════════════════════════════════════════════════════════════════════
class BrokenCalcController:
    def __init__(self):
        self.model = _make_model(
            "broken_calc", "BROKEN CALCULATOR",
            "Find and click '=' — watch out for wrong buttons!", 20
        )
        d = self.model.data
        d["display"]      = "ERROR_404_BRAIN"
        d["mistakes"]     = 0
        d["max_mistakes"] = 3
        d["buttons"]      = self._scatter_buttons()
        d["shake"]        = 0

    def _scatter_buttons(self):
        labels = ["7","8","9","÷","4","5","6","×","1","2","3","-","0",".","=","+",
                  "C","±","%","←","sin","cos","tan","log","√"]
        btns, used = [], set()
        target = "="
        for lbl in labels:
            from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H
        for _ in range(200):
                x = random.randint(CONTENT_X+30, CONTENT_X+CONTENT_W-80)
                y = random.randint(CONTENT_Y+50, CONTENT_Y+CONTENT_H-60)
                ok = all(abs(x-ux) >= 68 or abs(y-uy) >= 48 for ux,uy in used)
                if ok:
                    used.add((x, y))
                    btns.append({
                        "label":     lbl,
                        "x":         float(x),
                        "y":         float(y),
                        "bw":        60, "bh": 42,
                        "color":     random.choice([
                            (220,50,50),(255,140,0),(80,200,80),
                            (50,120,220),(160,50,220),(255,80,160),(30,210,210)
                        ]),
                        "angle":     random.uniform(-40, 40),
                        "wobble":    random.uniform(0, math.pi*2),
                        "hover":     False,
                        "is_target": lbl == target,
                    })
                    break
        return btns

    def update(self, dt: float, events, mouse: tuple):
        m = self.model
        d = m.data
        m.elapsed  += dt
        d["shake"]  = max(0, d["shake"] - dt * 50)

        mx, my = mouse
        for btn in d["buttons"]:
            r = pygame.Rect(int(btn["x"])-btn["bw"]//2,
                            int(btn["y"])-btn["bh"]//2,
                            btn["bw"], btn["bh"])
            btn["hover"] = r.collidepoint(mx, my)
            btn["wobble"] += dt * random.uniform(1, 3)
            btn["x"] += random.uniform(-0.6, 0.6)
            btn["y"] += random.uniform(-0.6, 0.6)
            from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H
            btn["x"]  = max(CONTENT_X+20, min(CONTENT_X+CONTENT_W-20, btn["x"]))
            btn["y"]  = max(CONTENT_Y+20, min(CONTENT_Y+CONTENT_H-20, btn["y"]))

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    r = pygame.Rect(int(btn["x"])-btn["bw"]//2,
                                    int(btn["y"])-btn["bh"]//2,
                                    btn["bw"], btn["bh"])
                    if r.collidepoint(ev.pos):
                        if btn["is_target"]:
                            SFX.WIN.play()
                            m.done = True
                        else:
                            SFX.WRONG.play()
                            d["mistakes"] += 1
                            d["shake"]     = 8
                            d["display"]   = random.choice([
                                "WRONG!", "NOPE", "TRY AGAIN", "HAHA",
                                "NOT EVEN CLOSE", "SMH",
                            ])
                            if d["mistakes"] >= d["max_mistakes"]:
                                m.failed     = True
                                m.fail_reason = "Too many wrong clicks!"
                        break


# ══════════════════════════════════════════════════════════════════════════
# STAGE 4 — Teleporting Button
# ══════════════════════════════════════════════════════════════════════════
class TeleportController:
    TAUNTS = ["TOO SLOW", "HAHA", "MISS!", "NOPE", "TRY AGAIN",
              "PATHETIC", "LOL", "ZOOM!", "BYE!", ":)", "WHEEE"]

    def __init__(self):
        self.model = _make_model(
            "teleport", "TELEPORTING BUTTON",
            "Click the button 3 times!", 25
        )
        d = self.model.data
        d["btn_rect"]   = [WIDTH//2-60, 350, 120, 50]
        d["clicks"]     = 0
        d["goal"]       = 3
        d["trail"]      = []
        d["last_taunt"] = ""
        d["taunt_pos"]  = (WIDTH//2, HEIGHT//2)
        d["taunt_life"] = 0.0
        d["shake"]      = 0



    def _teleport(self):
        d = self.model.data
        r = d["btn_rect"]
        d["trail"].append({"x": r[0]+r[2]//2, "y": r[1]+r[3]//2, "life": 1.0})
        from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H
        margin = 20
        d["btn_rect"] = [
            random.randint(CONTENT_X + margin, CONTENT_X + CONTENT_W - margin - r[2]),
            random.randint(CONTENT_Y + margin, CONTENT_Y + CONTENT_H - margin - r[3]),
            r[2], r[3],
        ]
        d["last_taunt"] = random.choice(self.TAUNTS)
        d["taunt_pos"]  = (d["btn_rect"][0]+r[2]//2, d["btn_rect"][1]-25)
        d["taunt_life"] = 1.5
        SFX.POP.play()

    def update(self, dt: float, events, mouse: tuple):
        m = self.model
        d = m.data
        m.elapsed    += dt
        d["shake"]    = max(0, d["shake"] - dt * 50)
        d["taunt_life"] = max(0, d["taunt_life"] - dt)

        for t in d["trail"]:
            t["life"] -= dt * 2
        d["trail"] = [t for t in d["trail"] if t["life"] > 0]

        mx, my = mouse
        btn_r = pygame.Rect(*d["btn_rect"])
        if btn_r.collidepoint(mx, my):
            self._teleport()

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(*d["btn_rect"]).collidepoint(ev.pos):
                    d["clicks"] += 1
                    SFX.WIN.play()
                    if d["clicks"] >= d["goal"]:
                        m.done = True

        if m.elapsed >= m.duration and not m.done:
            m.failed     = True
            m.fail_reason = "The button was too fast for you!"


# ══════════════════════════════════════════════════════════════════════════
# STAGE 5 — Shy Buttons
# ══════════════════════════════════════════════════════════════════════════
class ShyButtonsController:
    def __init__(self):
        self.model = _make_model(
            "shy_buttons", "SHY BUTTONS",
            "Click all 12 buttons!", 22
        )
        d = self.model.data
        d["buttons"]     = self._make_buttons()
        d["clicked_set"] = set()

    def _make_buttons(self):
        labels = list("ABCDEFGHIJKL")
        btns   = []
        from ...views.notepad_view import CONTENT_X, CONTENT_Y
        for i, lbl in enumerate(labels):
            bx = CONTENT_X + 50 + (i % 4) * 195
            by = CONTENT_Y + 40 + (i // 4) * 110
            btns.append({
                "id":       i,
                "label":    lbl,
                "base_x":   float(bx),
                "base_y":   float(by),
                "x":        float(bx),
                "y":        float(by),
                "vx":       0.0, "vy": 0.0,
                "blushing": 0.0,
                "clicked":  False,
            })
        return btns

    def update(self, dt: float, events, mouse: tuple):
        m = self.model
        d = m.data
        m.elapsed += dt

        mx, my = mouse
        for btn in d["buttons"]:
            if btn["clicked"]:
                continue
            dx   = btn["x"] - mx
            dy   = btn["y"] - my
            dist = math.hypot(dx, dy)
            flee_r = 130

            if dist < flee_r and dist > 1:
                force       = (flee_r - dist) / flee_r * 620
                btn["vx"]  += (dx / dist) * force * dt
                btn["vy"]  += (dy / dist) * force * dt
                btn["blushing"] = min(1.0, btn["blushing"] + dt * 3)
            else:
                btn["blushing"] = max(0.0, btn["blushing"] - dt * 2)

            btn["vx"] += (btn["base_x"] - btn["x"]) * 4 * dt
            btn["vy"] += (btn["base_y"] - btn["y"]) * 4 * dt
            btn["vx"] *= 0.84
            btn["vy"] *= 0.84
            btn["x"]  += btn["vx"] * dt * 60
            btn["y"]  += btn["vy"] * dt * 60
            from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H
            btn["x"]   = max(CONTENT_X+35, min(CONTENT_X+CONTENT_W-35, btn["x"]))
            btn["y"]   = max(CONTENT_Y+20, min(CONTENT_Y+CONTENT_H-20, btn["y"]))

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    if btn["clicked"]:
                        continue
                    r = pygame.Rect(int(btn["x"])-35, int(btn["y"])-20, 70, 40)
                    if r.collidepoint(ev.pos):
                        btn["clicked"] = True
                        d["clicked_set"].add(btn["id"])
                        SFX.POP.play()
                        break

        if len(d["clicked_set"]) >= len(d["buttons"]):
            m.done = True
            SFX.WIN.play()

        if m.elapsed >= m.duration and not m.done:
            m.failed     = True
            m.fail_reason = "The buttons were too shy!"


# ══════════════════════════════════════════════════════════════════════════
# STAGE 6 — Screaming Notepad
# ══════════════════════════════════════════════════════════════════════════
SCREAMS = ["AAAAAAAA","NOOOOOO","WHY ARE YOU TYPING","THE LETTERS HURT",
           "STOOOOOP","I CAN'T TAKE IT","PLEASE","HELP",
           "NOT THE ENTER KEY","AAAAAAAAAAA","OH THE HUMANITY"]

class ScreamController:
    def __init__(self):
        self.model = _make_model(
            "scream", "SCREAMING NOTEPAD",
            "Type the word 'SORRY' to calm it down", 20
        )
        d = self.model.data
        d["typed"]          = ""
        d["goal_word"]      = "SORRY"
        d["scream_msgs"]    = []
        d["notepad_shake"]  = 0
        d["bg_color"]       = (20, 20, 35)

        # pre-build font refs for view (can't pass font objects across easily,
        # so store size keys and let view resolve)
        from ...views.base_view import font_med, font_big, font_small
        d["_font_choices"]  = [font_small(), font_med(), font_big()]

    def update(self, dt: float, events, mouse: tuple):
        m  = self.model
        d  = m.data
        m.elapsed += dt
        d["notepad_shake"] = max(0, d["notepad_shake"] - dt * 8)
        d["bg_color"]      = tuple(int(c * (1 - min(1.0, dt*3)))
                                   + int(bg * min(1.0, dt*3))
                                   for c, bg in zip(d["bg_color"], (20,20,35)))

        for sm in d["scream_msgs"]:
            sm["y"]    -= 58 * dt
            sm["life"] -= dt
            sm["t"]    += dt
        d["scream_msgs"] = [sm for sm in d["scream_msgs"] if sm["life"] > 0]

        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    d["typed"] = d["typed"][:-1]
                elif ev.unicode and ev.unicode.isprintable():
                    d["typed"] += ev.unicode
                d["notepad_shake"] = 5
                SFX.SCREAM.play()
                d["bg_color"] = random.choice([
                    (200,40,40),(40,40,200),(40,200,40),(200,100,20),(100,20,200)
                ])
                d["scream_msgs"].append({
                    "text":      random.choice(SCREAMS),
                    "x":         float(random.randint(100, WIDTH-200)),
                    "y":         float(random.randint(200, HEIGHT-200)),
                    "life":      1.8, "t": 0.0,
                    "color":     random.choice([
                        (220,50,50),(255,140,0),(255,220,30),
                        (80,200,80),(50,120,220),(160,50,220)
                    ]),
                    "font_size": random.choice(d["_font_choices"]),
                })

        goal = d["goal_word"]
        if d["typed"].upper().endswith(goal):
            m.done = True
            SFX.WIN.play()

        if m.elapsed >= m.duration and not m.done:
            m.failed     = True
            m.fail_reason = "The notepad couldn't take it anymore!"


# ══════════════════════════════════════════════════════════════════════════
# STAGE 7 — Gravity Calculator
# ══════════════════════════════════════════════════════════════════════════
class GravityController:
    def __init__(self):
        self.model = _make_model(
            "gravity", "GRAVITY CALCULATOR",
            "Click '=' before all buttons hit the floor!", 22
        )
        d = self.model.data
        d["buttons"]   = self._make_buttons()
        d["display"]   = "HELP IM FALLING"
        d["gravity"]   = 80.0
        from ...views.notepad_view import CONTENT_Y, CONTENT_H
        d["floor"]     = CONTENT_Y + CONTENT_H - 20
        d["eq_clicks"] = 0
        d["goal"]      = 3
        d["shake"]     = 0



    def _make_buttons(self):
        labels = ["7","8","9","÷","4","5","6","×","1","2","3","-","0",".","=","+"]
        btns   = []
        from ...views.notepad_view import CONTENT_X, CONTENT_Y
        bw, bh = 62, 46
        bx     = CONTENT_X + 60
        by     = CONTENT_Y + 60
        gap    = 6
        for i, lbl in enumerate(labels):
            c, r = i%4, i//4
            btns.append({
                "label":    lbl,
                "x":        float(bx + c*(bw+gap)),
                "y":        float(by + r*(bh+gap)),
                "vy":       random.uniform(-15, 5),
                "bw":       bw, "bh": bh,
                "on_floor": False,
                "color":    random.choice([
                    (220,50,50),(255,140,0),(80,200,80),
                    (50,120,220),(160,50,220),(255,80,160),(30,210,210)
                ]),
                "bounce":   random.uniform(0.3, 0.65),
            })
        return btns

    def update(self, dt: float, events, mouse: tuple):
        m = self.model
        d = m.data
        m.elapsed  += dt
        d["shake"]  = max(0, d["shake"] - dt * 50)
        d["gravity"] += dt * 6

        all_fallen = True
        for btn in d["buttons"]:
            if not btn["on_floor"]:
                all_fallen = False
                btn["vy"] += d["gravity"] * dt
                btn["y"]  += btn["vy"] * dt * 60
                floor_y    = d["floor"] - btn["bh"]
                if btn["y"] >= floor_y:
                    btn["y"]   = floor_y
                    btn["vy"]  = -btn["vy"] * btn["bounce"]
                    if abs(btn["vy"]) < 4:
                        btn["on_floor"] = True
                        btn["vy"]       = 0
                    SFX.BLOOP.play()

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for btn in d["buttons"]:
                    r = pygame.Rect(int(btn["x"]), int(btn["y"]),
                                    btn["bw"], btn["bh"])
                    if r.collidepoint(ev.pos):
                        if btn["label"] == "=":
                            d["eq_clicks"] += 1
                            d["shake"]      = 5
                            SFX.CORRECT.play()
                            d["display"]    = random.choice(
                                ["WHEEE","I'M FLYING","OH NO","GRAVITY++","ZOOM"])
                            btn["vy"] = -320
                            btn["on_floor"] = False
                        else:
                            SFX.CLICK.play()
                            btn["vy"] = -200
                            btn["on_floor"] = False
                        break

        if d["eq_clicks"] >= d["goal"]:
            m.done = True
            SFX.WIN.play()

        if all_fallen and not m.done:
            m.failed     = True
            m.fail_reason = "All buttons fell! No more '=' to click."