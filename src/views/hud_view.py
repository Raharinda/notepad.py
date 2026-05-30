"""
views/hud_view.py
Draws the stage HUD: timer bar, stage name, objective reminder.
Only shown during STAGE phase.
"""
import math
import pygame
from .base_view import (
    WIDTH, HEIGHT,
    WHITE, BLACK, RED, YELLOW, CYAN, PANEL,
    font_small, font_tiny,
    rainbow_color, lerp_color,
)


class HUDView:
    def draw(self, surf: pygame.Surface,
             stage_model,
             game_state):
        self._draw_timer_bar(surf, stage_model, game_state)
        self._draw_stage_label(surf, stage_model, game_state)
        self._draw_objective(surf, stage_model)

    def _draw_timer_bar(self, surf, stage_model, game_state):
        bar_w   = 400
        bar_h   = 12
        bx      = WIDTH // 2 - bar_w // 2
        by      = 8
        filled  = int(stage_model.remaining / stage_model.duration * bar_w)

        # background
        pygame.draw.rect(surf, PANEL, (bx, by, bar_w, bar_h), border_radius=6)
        # fill
        if filled > 0:
            urgency = 1.0 - stage_model.remaining / stage_model.duration
            col = rainbow_color(stage_model.elapsed) if urgency < 0.6 \
                  else lerp_color(YELLOW, RED, (urgency - 0.6) / 0.4)
            pygame.draw.rect(surf, col, (bx, by, filled, bar_h), border_radius=6)
        # border
        pygame.draw.rect(surf, WHITE, (bx, by, bar_w, bar_h), 1, border_radius=6)

    def _draw_stage_label(self, surf, stage_model, game_state):
        f   = font_small()
        idx = game_state.stage_index + 1
        tot = game_state.total_stages
        lbl = f.render(
            f"STAGE {idx}/{tot}  —  {stage_model.title}",
            True, WHITE
        )
        surf.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 24))

    def _draw_objective(self, surf, stage_model):
        f   = font_tiny()
        obj = f.render(f"► {stage_model.objective}", True, CYAN)
        surf.blit(obj, (WIDTH // 2 - obj.get_width() // 2, 42))