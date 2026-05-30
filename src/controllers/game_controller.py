"""
controllers/game_controller.py
Main orchestrator. Owns all sub-controllers and drives the game loop.
"""
import pygame
import sys

from ..models.game_state   import GameState, Phase
from ..models.notepad_model import NotepadModel

from .input_controller    import InputController
from .notepad_controller  import NotepadController
from .stages.stage_controllers import (
    RedCircleController,
    SelfAwareController,
    BrokenCalcController,
    TeleportController,
    ShyButtonsController,
    ScreamController,
    GravityController,
)

from ..views.notepad_view import NotepadView
from ..views.hud_view     import HUDView
from ..views.stages.stage_views import (
    RedCircleView,
    SelfAwareView,
    BrokenCalcView,
    TeleportView,
    ShyButtonsView,
    ScreamView,
    GravityView,
)
from ..views.base_view    import BG, WIDTH, HEIGHT, rainbow_color
from ..utils.transitions  import Transition, WinScreen, GameOverScreen
from ..utils.sfx          import SFX


# Ordered list: (ControllerClass, ViewClass)
STAGE_REGISTRY = [
    (RedCircleController,   RedCircleView),
    (SelfAwareController,   SelfAwareView),
    (BrokenCalcController,  BrokenCalcView),
    (TeleportController,    TeleportView),
    (ShyButtonsController,  ShyButtonsView),
    (ScreamController,      ScreamView),
    (GravityController,     GravityView),
]


class GameController:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock  = clock
        self._init_game()

    # ── init / reset ──────────────────────────────────────────────────────
    def _init_game(self):
        self.gs  = GameState(total_stages=len(STAGE_REGISTRY))
        self.nm  = NotepadModel()

        self.input_ctrl   = InputController()
        self.notepad_ctrl = NotepadController(self.gs, self.nm)
        self.notepad_view = NotepadView()
        self.hud_view     = HUDView()

        self._load_stage(0)

        self.transition  = None
        self.win_screen  = None
        self.gameover    = None

        # background particles
        import random
        from ..views.base_view import RAINBOW
        self._bg_particles = [
            {
                "x":     random.randint(0, WIDTH),
                "y":     random.randint(0, HEIGHT),
                "vx":    random.uniform(-12, 12),
                "vy":    random.uniform(-12, 12),
                "life":  random.uniform(0, 10),
                "r":     random.randint(1, 3),
            }
            for _ in range(50)
        ]

    def _load_stage(self, idx: int):
        CtrlCls, ViewCls       = STAGE_REGISTRY[idx]
        self.stage_ctrl        = CtrlCls()
        self.stage_view        = ViewCls()
        self.gs.stage_index    = idx

    # ── main loop ─────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            # input
            self.input_ctrl.pump()
            if self.input_ctrl.quit:
                pygame.quit()
                sys.exit()
            if self.input_ctrl.restart:
                self._init_game()
                continue

            events    = self.input_ctrl.events
            mouse     = self.input_ctrl.mouse_pos

            # update
            self._update(dt, events, mouse)

            # draw
            self._draw(dt)

            pygame.display.flip()

    # ── update dispatch ───────────────────────────────────────────────────
    def _update(self, dt, events, mouse):
        phase = self.gs.phase

        if phase == Phase.NOTEPAD:
            self.notepad_ctrl.update(dt, events, mouse)
            self.notepad_view.update(dt)

        elif phase == Phase.STAGE:
            self.stage_ctrl.update(dt, events, mouse)
            sm = self.stage_ctrl.model

            if sm.failed:
                self.gameover = GameOverScreen(sm.fail_reason)
                self.gs.trigger_game_over(sm.fail_reason)
                SFX.WRONG.play()

            elif sm.done:
                next_idx = self.gs.stage_index + 1
                if next_idx >= self.gs.total_stages:
                    self.gs.phase = Phase.WIN
                    self.win_screen = WinScreen()
                    SFX.WIN.play()
                else:
                    self.gs.phase = Phase.TRANSITION
                    self.transition = Transition(
                        label    = f"STAGE {next_idx + 1} INCOMING...",
                        duration = 1.0,
                    )
                    self._pending_stage = next_idx

        elif phase == Phase.TRANSITION:
            if self.transition:
                self.transition.update(dt)
                if self.transition.done:
                    self._load_stage(self._pending_stage)
                    self.gs.phase = Phase.STAGE
                    self.transition = None

        elif phase == Phase.WIN:
            if self.win_screen:
                self.win_screen.update(dt)

        elif phase == Phase.GAME_OVER:
            if self.gameover:
                self.gameover.update(dt)

    # ── draw dispatch ─────────────────────────────────────────────────────
    def _draw(self, dt):
        phase = self.gs.phase

        if phase == Phase.NOTEPAD:
            self.screen.fill((240, 240, 238))   # OS-level bg colour
            self.notepad_view.draw_notepad_phase(
                self.screen, self.nm, self.gs,
                self.input_ctrl.mouse_pos
            )

        elif phase in (Phase.STAGE, Phase.TRANSITION):
            # notepad shell first, then stage content inside it
            self.notepad_view.draw_stage_shell(
                self.screen,
                self.gs,
                self.stage_ctrl.model,
            )
            self.stage_view.draw(
                self.screen,
                self.nm,
                self.stage_ctrl.model,
            )
            if phase == Phase.TRANSITION and self.transition:
                self.transition.draw(self.screen)

        elif phase == Phase.WIN:
            self.screen.fill(BG)
            if self.win_screen:
                self.win_screen.draw(self.screen)

        elif phase == Phase.GAME_OVER:
            self.notepad_view.draw_stage_shell(
                self.screen, self.gs, self.stage_ctrl.model)
            self.stage_view.draw(self.screen, self.nm, self.stage_ctrl.model)
            if self.gameover:
                self.gameover.draw(self.screen)

        # always-on hint
        import pygame as _pg
        f   = _pg.font.SysFont("monospace", 11)
        tip = f.render("ESC: quit  |  R: restart", True, (70, 70, 90))
        self.screen.blit(tip, (WIDTH - tip.get_width() - 6, HEIGHT - 16))

    def _draw_bg_particles(self, dt):
        import random, math
        self.screen.fill(BG)
        for p in self._bg_particles:
            p["x"]    += p["vx"] * dt
            p["y"]    += p["vy"] * dt
            p["life"] += dt
            if p["x"] < 0 or p["x"] > WIDTH:  p["vx"] *= -1
            if p["y"] < 0 or p["y"] > HEIGHT: p["vy"] *= -1
            col = rainbow_color(p["life"] * 0.4)
            import pygame as _pg
            _pg.draw.circle(self.screen, col,
                            (int(p["x"]), int(p["y"])), p["r"])