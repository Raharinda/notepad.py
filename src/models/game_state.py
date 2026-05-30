"""
models/game_state.py
Central source of truth for the entire game.
No pygame imports here — pure data.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class Phase(Enum):
    NOTEPAD   = auto()   # fake notepad, player doesn't know it's a game
    STAGE     = auto()   # active stage
    TRANSITION= auto()   # between stages
    WIN       = auto()
    GAME_OVER = auto()


@dataclass
class GameState:
    phase:          Phase  = Phase.NOTEPAD
    stage_index:    int    = 0
    total_stages:   int    = 7
    lives:          int    = 3          # unused for now (game over on fail)
    score:          int    = 0
    time_alive:     float  = 0.0        # total seconds survived

    # Notepad-phase fields
    notepad_time:   float  = 0.0        # how long user has been in fake notepad
    glitch_level:   float  = 0.0        # 0.0 → 1.0, how "broken" the notepad looks

    # set when game over happens
    game_over_reason: str  = ""

    def advance_stage(self):
        self.stage_index += 1
        if self.stage_index >= self.total_stages:
            self.phase = Phase.WIN
        else:
            self.phase = Phase.TRANSITION

    def trigger_game_over(self, reason: str = ""):
        self.phase            = Phase.GAME_OVER
        self.game_over_reason = reason

    def reset(self):
        self.phase            = Phase.NOTEPAD
        self.stage_index      = 0
        self.lives            = 3
        self.score            = 0
        self.time_alive       = 0.0
        self.notepad_time     = 0.0
        self.glitch_level     = 0.0
        self.game_over_reason = ""