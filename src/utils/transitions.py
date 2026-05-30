"""
utils/transitions.py
Handles animated transitions between stages.
"""
import pygame
import math
import random

WIDTH, HEIGHT = 900, 650


class Transition:
    def __init__(self, label: str = "NEXT STAGE...", duration: float = 0.9):
        self.label    = label
        self.duration = duration
        self.t        = 0.0
        self.done     = False
        self._colors  = [(220,50,50),(255,140,0),(255,220,30),(80,200,80),
                         (30,210,210),(50,120,220),(160,50,220),(255,80,160)]

    def update(self, dt: float):
        self.t += dt
        if self.t >= self.duration:
            self.done = True

    def draw(self, surf: pygame.Surface):
        progress = self.t / self.duration
        alpha    = int((1 - abs(progress * 2 - 1)) * 255)

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        surf.blit(overlay, (0, 0))

        if alpha > 30:
            idx = int(self.t * 8) % len(self._colors)
            col = self._colors[idx]
            font = pygame.font.SysFont("monospace", 36, bold=True)
            s = font.render(self.label, True, col)
            surf.blit(s, (WIDTH // 2 - s.get_width() // 2,
                          HEIGHT // 2 - s.get_height() // 2))


class WinScreen:
    def __init__(self):
        self.t        = 0.0
        self.confetti = [
            {
                "x":     random.randint(0, WIDTH),
                "y":     random.uniform(-HEIGHT, 0),
                "vy":    random.uniform(80, 220),
                "vx":    random.uniform(-40, 40),
                "color": random.choice([(220,50,50),(255,140,0),(255,220,30),
                                        (80,200,80),(50,120,220),(160,50,220)]),
                "size":  random.randint(5, 13),
                "rot":   random.uniform(0, 360),
                "rot_v": random.uniform(-200, 200),
            }
            for _ in range(140)
        ]

    def update(self, dt: float):
        self.t += dt
        for c in self.confetti:
            c["y"]   += c["vy"] * dt
            c["x"]   += c["vx"] * dt
            c["rot"] += c["rot_v"] * dt
            if c["y"] > HEIGHT + 20:
                c["y"] = random.uniform(-30, 0)
                c["x"] = random.randint(0, WIDTH)

    def draw(self, surf: pygame.Surface):
        for c in self.confetti:
            tmp = pygame.Surface((c["size"], c["size"]), pygame.SRCALPHA)
            pygame.draw.rect(tmp, c["color"], (0, 0, c["size"], c["size"]))
            rot = pygame.transform.rotate(tmp, c["rot"])
            surf.blit(rot, (int(c["x"]), int(c["y"])))

        font_big = pygame.font.SysFont("monospace", 42, bold=True)
        font_med = pygame.font.SysFont("monospace", 22)
        font_sm  = pygame.font.SysFont("monospace", 16)

        t   = self.t
        idx = int(t * 6) % 8
        cols = [(220,50,50),(255,140,0),(255,220,30),(80,200,80),
                (30,210,210),(50,120,220),(160,50,220),(255,80,160)]

        scale = 1 + 0.08 * math.sin(t * 5)
        s = font_big.render("YOU SURVIVED!", True, cols[idx])
        s = pygame.transform.scale(s, (int(s.get_width() * scale),
                                       int(s.get_height() * scale)))
        surf.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - 90))

        sub = font_med.render("The notepad is... disappointed.", True, (255, 255, 255))
        surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))

        tip = font_sm.render("Press R to restart", True, (30, 210, 210))
        surf.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 + 55))


class GameOverScreen:
    def __init__(self, reason: str = ""):
        self.t      = 0.0
        self.reason = reason
        self.glitch = 0.0

    def update(self, dt: float):
        self.t     += dt
        self.glitch = max(0.0, self.glitch - dt * 3)

    def trigger_glitch(self):
        self.glitch = 1.0

    def draw(self, surf: pygame.Surface):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(255, int(self.t * 400)))
        surf.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("monospace", 52, bold=True)
        font_med = pygame.font.SysFont("monospace", 22)
        font_sm  = pygame.font.SysFont("monospace", 16)

        ox = random.randint(-6, 6) if self.glitch > 0 else 0
        oy = random.randint(-3, 3) if self.glitch > 0 else 0

        s = font_big.render("GAME OVER", True, (220, 50, 50))
        surf.blit(s, (WIDTH // 2 - s.get_width() // 2 + ox,
                      HEIGHT // 2 - 80 + oy))

        if self.reason:
            r = font_med.render(self.reason, True, (255, 200, 50))
            surf.blit(r, (WIDTH // 2 - r.get_width() // 2,
                          HEIGHT // 2))

        tip = font_sm.render("Press R to restart", True, (150, 150, 180))
        surf.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 + 60))