import pygame

from config import TILE_SIZE, GRAY

# --- Třída Demoliční nálože ---
class DemolitionCharge(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.timer = 2000
        self.explosion_time = pygame.time.get_ticks() + self.timer
        self.exploded = False
        self.explosion_duration = 500
        self.explosion_start_time = 0
        self.explosion_range = 2
