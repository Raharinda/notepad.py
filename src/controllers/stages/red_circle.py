"""controllers/stages/red_circle.py"""
import math, random, time
import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX


class RedCircleController:
    def __init__(self):
        self.model = StageModel(
            stage_id="red_circle", title="RED CIRCLE CHASING CURSOR",
            objective="Survive without getting caught!", duration=14
        )
        d = self.model.data
        d["cx"] = float(450); d["cy"] = float(380)
        d["r"] = 34; d["speed"] = 115; d["anger"] = 0.0
        d["particles"] = []; d["shake"] = 0
        self._last_sfx = 0.0

    def update(self, dt, events, mouse):
        m = self.model; d = m.data
        m.elapsed += dt
        d["shake"] = max(0, d["shake"] - dt * 50)
        mx, my = mouse
        dx = mx - d["cx"]; dy = my - d["cy"]
        dist = math.hypot(dx, dy)
        d["anger"] = max(0.0, 1.0 - dist / 400)
        spd = d["speed"] + d["anger"] * 190
        if dist > 1:
            d["cx"] += (dx / dist) * spd * dt
            d["cy"] += (dy / dist) * spd * dt
        if dist < d["r"] + 6:
            d["shake"] = 10
            now = time.time()
            if now - self._last_sfx > 0.28:
                SFX.EVIL.play(); self._last_sfx = now
            m.elapsed += dt * 1.5
            if m.elapsed >= m.duration + 2:
                m.failed = True; m.fail_reason = "The circle caught you!"; return
        if random.random() < 0.25:
            d["particles"].append({
                "x": d["cx"] + random.randint(-d["r"], d["r"]),
                "y": d["cy"] + random.randint(-d["r"], d["r"]),
                "vx": random.uniform(-55, 55), "vy": random.uniform(-55, 55),
                "life": random.uniform(0.4, 1.0), "max_life": 1.0,
            })
        for p in d["particles"]:
            p["x"] += p["vx"] * dt; p["y"] += p["vy"] * dt; p["life"] -= dt
        d["particles"] = [p for p in d["particles"] if p["life"] > 0]
        if m.elapsed >= m.duration:
            m.done = True