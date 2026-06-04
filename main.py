"""
main.py — entry point for Freak Notepad
Run with: python3 main.py
"""
import os
import pygame
from src.controllers.game_controller import GameController
import os
os.environ["SDL_VIDEODRIVER"] = "x11"   # force standalone window
os.environ["DISPLAY"] = ":0"

INTERNAL_W, INTERNAL_H = 900, 650
FPS = 60

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    info   = pygame.display.Info()
    MON_W  = info.current_w
    MON_H  = info.current_h

    # hitung scale supaya muat di monitor dengan margin 80px
    SCALE  = min((MON_W - 80) / INTERNAL_W, (MON_H - 80) / INTERNAL_H)
    SCALE  = round(min(SCALE, 1.0), 2)   # tidak lebih besar dari 1:1

    WIN_W  = int(INTERNAL_W * SCALE)
    WIN_H  = int(INTERNAL_H * SCALE)

    # spawn window di tengah layar
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    window = pygame.display.set_mode((WIN_W, WIN_H))
    screen = pygame.Surface((INTERNAL_W, INTERNAL_H))

    pygame.display.set_caption("Notepad")

    icon = pygame.Surface((32, 32))
    icon.fill((255, 255, 255))
    pygame.display.set_icon(icon)

    print(f"Monitor : {MON_W} x {MON_H}")
    print(f"Scale   : {SCALE}")
    print(f"Window  : {WIN_W} x {WIN_H}")

    clock = pygame.time.Clock()
    game  = GameController(screen, clock)

    import sys
    while True:
        dt = clock.tick(FPS) / 1000.0

        game.input_ctrl.pump()
        if game.input_ctrl.quit:
            pygame.quit()
            sys.exit()
        if game.input_ctrl.restart:
            game._init_game()
            continue

        events    = game.input_ctrl.events
        mouse_raw = game.input_ctrl.mouse_pos

        # scale balik posisi mouse ke koordinat internal
        mouse = (
            int(mouse_raw[0] / SCALE),
            int(mouse_raw[1] / SCALE),
        )
        game.input_ctrl.mouse_pos = mouse

        game._update(dt, events, mouse)
        game._draw(dt)

        scaled = pygame.transform.smoothscale(screen, (WIN_W, WIN_H))
        window.blit(scaled, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    main()