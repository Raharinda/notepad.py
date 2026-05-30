"""
controllers/input_controller.py
Collects and exposes raw pygame events each frame.
Other controllers pull from this.
"""
import pygame
import sys


class InputController:
    def __init__(self):
        self.events:     list  = []
        self.mouse_pos:  tuple = (0, 0)
        self.quit:       bool  = False
        self.restart:    bool  = False

    def pump(self):
        """Call once per frame to refresh events."""
        self.events    = pygame.event.get()
        self.mouse_pos = pygame.mouse.get_pos()
        self.quit      = False
        self.restart   = False

        for ev in self.events:
            if ev.type == pygame.QUIT:
                self.quit = True
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.quit = True
                if ev.key == pygame.K_r:
                    self.restart = True