# --- Třída Sbíratelného předmětu ---
import pygame

from config import TILE_SIZE, YELLOW


class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        self.image = pygame.Surface([TILE_SIZE // 2, TILE_SIZE // 2])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)