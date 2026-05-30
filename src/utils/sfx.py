"""
utils/sfx.py
Generates all sound effects procedurally (no external files needed).
"""
import math
import random
import pygame


def _make_sound(samples: bytearray) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(buffer=bytes(samples))


def _buf(duration: float, fn) -> bytearray:
    sr = 44100
    n = int(sr * duration)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sr
        fade = min(1.0, (n - i) / (sr * 0.015))
        val = int(fn(t) * 32767 * fade)
        val = max(-32768, min(32767, val))
        buf[i * 2] = val & 0xFF
        buf[i * 2 + 1] = (val >> 8) & 0xFF
    return buf


def square(freq: float, dur: float, vol: float = 0.35) -> pygame.mixer.Sound:
    return _make_sound(_buf(dur, lambda t: vol * (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0)))


def noise(dur: float, vol: float = 0.25) -> pygame.mixer.Sound:
    return _make_sound(_buf(dur, lambda t: vol * random.uniform(-1, 1)))


def sine(freq: float, dur: float, vol: float = 0.3) -> pygame.mixer.Sound:
    return _make_sound(_buf(dur, lambda t: vol * math.sin(2 * math.pi * freq * t)))


# ── Pre-built SFX ──────────────────────────────────────────────────────────
class SFX:
    CLICK   = square(800,  0.06, 0.35)
    EVIL    = square(140,  0.35, 0.45)
    SCREAM  = noise(0.18,  0.55)
    POP     = square(1200, 0.04, 0.28)
    BLOOP   = square(320,  0.12, 0.38)
    WIN     = square(660,  0.18, 0.45)
    TYPE    = square(900,  0.03, 0.15)   # subtle typewriter
    GLITCH  = noise(0.06,  0.30)
    WRONG   = square(200,  0.25, 0.40)
    CORRECT = square(880,  0.10, 0.40)