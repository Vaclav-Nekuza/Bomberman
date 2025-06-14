import pygame

from config import TILE_SIZE, BLACK, BROWN

# --- Třída Zdi (pevné a rozbitelné) ---
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.tile_type = tile_type
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        if self.tile_type == 1:  # TILE_WALL
            self.image.fill(BLACK)
        elif self.tile_type == 2:  # TILE_BREAKABLE
            self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
