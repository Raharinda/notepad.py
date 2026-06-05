"""controllers/stages/red_circle.py
Stage 1 — RED CIRCLE(S) CHASING CURSOR

Mechanics:
  - Survive AND hover over the Safe Zone for 3 cumulative seconds to clear
  - Circles spawn over time (1 → 4), each with unique personality
  - Every 4s a speed surge hits all circles briefly
  - If a circle gets too far (>550px) it teleports closer — no kiting forever
  - Getting touched adds "panic time" (elapsed accelerates)
"""
import math
import random
import time

import pygame
from ...models.stage_model import StageModel
from ...utils.sfx import SFX
from ...views.notepad_view import CONTENT_X, CONTENT_Y, CONTENT_W, CONTENT_H

# Safe zone spawns inside the content area
SAFE_W, SAFE_H = 90, 60
HOLD_REQUIRED  = 3.0    # seconds to hold safe zone
MAX_CIRCLES    = 4
SPAWN_INTERVAL = 5.0    # seconds between new circle spawns
TELEPORT_DIST  = 560    # if circle farther than this, teleport closer

TAUNTS = [
    "COME HERE", "WHY DO YOU RUN", "HEHEHE", "I SEE YOU",
    "YOU CAN'T HIDE", "ALMOST GOT YOU", "STAY STILL",
    "THERE YOU ARE", "GOTCHA SOON", "I'M GETTING FASTER",
    "TELEPORTING...", "SURPRISE!", "PEEK A BOO",
]

def _rand_pos():
    """Random position inside content area with margin."""
    m = 50
    return (
        float(random.randint(CONTENT_X + m, CONTENT_X + CONTENT_W - m)),
        float(random.randint(CONTENT_Y + m, CONTENT_Y + CONTENT_H - m)),
    )


def _make_circle(idx: int) -> dict:
    personalities = [
        {"speed": 118, "r": 34, "color_bias": 1.0, "teleport": True},   # leader — fast, teleports
        {"speed":  95, "r": 28, "color_bias": 0.7, "teleport": False},  # follower — medium
        {"speed":  80, "r": 40, "color_bias": 0.5, "teleport": False},  # big slow one
        {"speed": 145, "r": 22, "color_bias": 0.9, "teleport": True},   # tiny speedster
    ]
    p = personalities[idx % len(personalities)]
    cx, cy = _rand_pos()
    # spawn away from center
    cx = CONTENT_X + (CONTENT_W - 80) if idx % 2 == 0 else CONTENT_X + 40
    cy = CONTENT_Y + (CONTENT_H - 60) if idx < 2 else CONTENT_Y + 40
    return {
        "id":          idx,
        "cx":          float(cx),
        "cy":          float(cy),
        "speed":       p["speed"],
        "r":           p["r"],
        "anger":       0.0,
        "color_bias":  p["color_bias"],
        "teleport":    p["teleport"],
        "particles":   [],
        "surge_speed": 0.0,   # temporary boost
        "last_taunt_t": 0.0,
    }


class RedCircleController:
    def __init__(self):
        self.model = StageModel(
            stage_id="red_circle",
            title="RED CIRCLE(S) CHASING CURSOR",
            objective="Hold the GREEN ZONE for 3s — don't get caught!",
            duration=22,
        )
        d = self.model.data

        # Circles — start with 1, more spawn over time
        d["circles"]         = [_make_circle(0)]
        d["next_spawn_t"]    = SPAWN_INTERVAL
        d["circle_count"]    = 1

        # Safe zone
        safe_x = CONTENT_X + CONTENT_W // 2 - SAFE_W // 2
        safe_y = CONTENT_Y + CONTENT_H // 2 - SAFE_H // 2
        d["safe_rect"]       = [safe_x, safe_y, SAFE_W, SAFE_H]
        d["safe_hold"]       = 0.0     # cumulative hover time
        d["safe_active"]     = False   # player currently hovering
        d["safe_move_t"]     = 0.0    # cooldown before zone can move
        d["safe_blink"]      = 0.0

        # Surge
        d["surge_t"]         = 0.0
        d["next_surge"]      = 4.0
        d["surging"]         = False

        # Feedback
        d["shake"]           = 0
        d["taunt"]           = ""
        d["taunt_life"]      = 0.0
        d["taunt_pos"]       = (CONTENT_X + CONTENT_W // 2, CONTENT_Y + 40)
        d["warning_flash"]   = 0.0   # red flash when caught

        self._last_sfx = 0.0

    # ── helpers ────────────────────────────────────────────────────────────

    def _show_taunt(self, d, text, pos=None):
        d["taunt"]      = text
        d["taunt_life"] = 1.6
        if pos:
            d["taunt_pos"] = pos

    def _move_safe_zone(self, d, mouse):
        """Teleport safe zone to a new random spot far from mouse."""
        mx, my = mouse
        for _ in range(30):
            nx = random.randint(CONTENT_X + 10, CONTENT_X + CONTENT_W - SAFE_W - 10)
            ny = random.randint(CONTENT_Y + 10, CONTENT_Y + CONTENT_H - SAFE_H - 10)
            if math.hypot(nx - mx, ny - my) > 160:
                d["safe_rect"][0] = nx
                d["safe_rect"][1] = ny
                d["safe_move_t"]  = 2.5
                return

    # ── main update ────────────────────────────────────────────────────────

    def update(self, dt, events, mouse):
        m = self.model
        d = m.data

        m.elapsed += dt
        d["shake"]       = max(0, d["shake"] - dt * 55)
        d["taunt_life"]  = max(0, d["taunt_life"] - dt)
        d["warning_flash"] = max(0, d["warning_flash"] - dt * 3)
        d["safe_move_t"] = max(0, d["safe_move_t"] - dt)
        d["safe_blink"]  += dt

        mx, my = mouse

        # ── spawn new circles ────────────────────────────────────────────
        if (d["circle_count"] < MAX_CIRCLES
                and m.elapsed >= d["next_spawn_t"]):
            idx = d["circle_count"]
            d["circles"].append(_make_circle(idx))
            d["circle_count"] += 1
            d["next_spawn_t"]  = m.elapsed + SPAWN_INTERVAL
            SFX.EVIL.play()
            self._show_taunt(d, f"CIRCLE #{idx+1} JOINS THE HUNT!", (CONTENT_X + CONTENT_W//2, CONTENT_Y + 30))

        # ── speed surge ─────────────────────────────────────────────────
        d["surge_t"] += dt
        if not d["surging"] and d["surge_t"] >= d["next_surge"]:
            d["surging"]    = True
            d["surge_t"]    = 0.0
            d["next_surge"] = random.uniform(4.5, 7.0)
            for c in d["circles"]:
                c["surge_speed"] = c["speed"] * 1.8
            SFX.SCREAM.play()
            self._show_taunt(d, "SPEED SURGE!!",
                             (CONTENT_X + CONTENT_W//2, CONTENT_Y + 25))

        if d["surging"]:
            for c in d["circles"]:
                c["surge_speed"] = max(0, c["surge_speed"] - dt * c["speed"] * 3)
            if all(c["surge_speed"] <= 0 for c in d["circles"]):
                d["surging"] = False

        # ── move circles ─────────────────────────────────────────────────
        caught = False
        for c in d["circles"]:
            dx = mx - c["cx"]
            dy = my - c["cy"]
            dist = math.hypot(dx, dy)
            c["anger"] = max(0.0, 1.0 - dist / 380)

            effective_speed = c["speed"] + c["surge_speed"] + c["anger"] * 150

            if dist > 1:
                c["cx"] += (dx / dist) * effective_speed * dt
                c["cy"] += (dy / dist) * effective_speed * dt

            # teleport if too far (only teleporters)
            if c["teleport"] and dist > TELEPORT_DIST:
                # teleport to a point 200px from mouse
                angle = math.atan2(dy, dx) + random.uniform(-0.8, 0.8)
                c["cx"] = mx - math.cos(angle) * 200
                c["cy"] = my - math.sin(angle) * 200
                c["cx"] = max(CONTENT_X + c["r"], min(CONTENT_X + CONTENT_W - c["r"], c["cx"]))
                c["cy"] = max(CONTENT_Y + c["r"], min(CONTENT_Y + CONTENT_H - c["r"], c["cy"]))
                SFX.POP.play()
                self._show_taunt(d, random.choice(["SURPRISE!", "TELEPORTED!", "GOTCHA SOON"]),
                                 (int(c["cx"]), int(c["cy"] - 40)))

            # particle trail
            if random.random() < 0.3:
                c["particles"].append({
                    "x": c["cx"] + random.randint(-c["r"], c["r"]),
                    "y": c["cy"] + random.randint(-c["r"], c["r"]),
                    "vx": random.uniform(-50, 50),
                    "vy": random.uniform(-50, 50),
                    "life": random.uniform(0.3, 0.9),
                    "max_life": 0.9,
                })
            for p in c["particles"]:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["life"] -= dt
            c["particles"] = [p for p in c["particles"] if p["life"] > 0]

            # collision check
            if dist < c["r"] + 8:
                caught = True

        if caught:
            d["shake"]         = 12
            d["warning_flash"] = 1.0
            m.elapsed         += dt * 2.0   # panic time
            now = time.time()
            if now - self._last_sfx > 0.3:
                SFX.EVIL.play()
                self._last_sfx = now
            if random.random() < 0.08:
                self._show_taunt(d, random.choice(TAUNTS))

        # ── safe zone hover ──────────────────────────────────────────────
        sr = d["safe_rect"]
        in_safe = (sr[0] <= mx <= sr[0] + sr[2]) and (sr[1] <= my <= sr[1] + sr[3])

        # safe zone runs away if a circle is too close
        for c in d["circles"]:
            if math.hypot(c["cx"] - (sr[0] + sr[2]//2), c["cy"] - (sr[1] + sr[3]//2)) < 80:
                if d["safe_move_t"] <= 0:
                    self._move_safe_zone(d, mouse)
                    SFX.BLOOP.play()
                    self._show_taunt(d, "ZONE MOVED!", (sr[0] + sr[2]//2, sr[1] - 20))
                break

        d["safe_active"] = in_safe and not caught
        if d["safe_active"]:
            d["safe_hold"] += dt
            if int(d["safe_hold"] * 4) % 2 == 0:
                SFX.TYPE.play() if random.random() < 0.05 else None
        else:
            # drain slowly when not holding
            d["safe_hold"] = max(0, d["safe_hold"] - dt * 0.4)

        # ── win / lose ───────────────────────────────────────────────────
        if d["safe_hold"] >= HOLD_REQUIRED:
            m.done = True
            SFX.WIN.play()

        if m.elapsed >= m.duration and not m.done:
            m.failed     = True
            m.fail_reason = "The circles caught up with you!"