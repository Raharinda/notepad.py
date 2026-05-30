"""
controllers/notepad_controller.py
Handles the "fake notepad" phase.
Gradually increases glitch_level over time until it triggers Stage 1.
"""
import random
import pygame
from ..models.game_state import GameState, Phase
from ..models.notepad_model import NotepadModel
from ..utils.sfx import SFX

# How many seconds of "normal" notepad before glitch starts creeping in
CALM_DURATION   = 8.0
# Total notepad phase before hard-switching to stages
TOTAL_DURATION  = 18.0


class NotepadController:
    def __init__(self, game_state: GameState, notepad_model: NotepadModel):
        self.gs  = game_state
        self.nm  = notepad_model
        self._last_glitch_insert = 0.0

    def update(self, dt: float, events: list, mouse: tuple):
        gs = self.gs
        nm = self.nm

        gs.notepad_time += dt
        gs.time_alive   += dt

        # compute glitch level (0 → 1)
        if gs.notepad_time < CALM_DURATION:
            gs.glitch_level = 0.0
        else:
            raw = (gs.notepad_time - CALM_DURATION) / (TOTAL_DURATION - CALM_DURATION)
            gs.glitch_level = min(1.0, raw ** 1.4)

        # occasionally inject ghost chars into text at high glitch
        self._last_glitch_insert += dt
        if gs.glitch_level > 0.4 and self._last_glitch_insert > 0.8:
            self._last_glitch_insert = 0.0
            if nm.lines:
                li  = random.randint(0, len(nm.lines)-1)
                col = random.randint(0, max(0, len(nm.lines[li])))
                nm.add_glitch_char(li, col,
                                   random.choice("░▒▓█▄▀■□"), 1.4)

        nm.update_glitches(dt)

        # handle keyboard input
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                SFX.TYPE.play()
                if ev.key == pygame.K_RETURN:
                    nm.newline()
                elif ev.key == pygame.K_BACKSPACE:
                    nm.backspace()
                elif ev.key == pygame.K_LEFT:
                    nm.move_cursor(-1, 0)
                elif ev.key == pygame.K_RIGHT:
                    nm.move_cursor(1, 0)
                elif ev.key == pygame.K_UP:
                    nm.move_cursor(0, -1)
                elif ev.key == pygame.K_DOWN:
                    nm.move_cursor(0, 1)
                elif ev.unicode and ev.unicode.isprintable():
                    nm.insert_char(ev.unicode)

        # transition to stages when time is up
        if gs.notepad_time >= TOTAL_DURATION:
            gs.phase       = Phase.STAGE
            gs.glitch_level = 0.0   # reset — stages handle their own visuals