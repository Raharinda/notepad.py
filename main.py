"""
main.py — entry point for Freak Notepad
Run with: python3 main.py
"""
import pygame
from src.controllers.game_controller import GameController

WIDTH, HEIGHT = 900, 650
FPS           = 60


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.display.set_caption("Notepad")           # looks innocent on purpose

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()

    # tiny window icon — plain white square (no pygame.image needed)
    icon = pygame.Surface((32, 32))
    icon.fill((255, 255, 255))
    pygame.display.set_icon(icon)

    game = GameController(screen, clock)
    game.run()


if __name__ == "__main__":
    main()