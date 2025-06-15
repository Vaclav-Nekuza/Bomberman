import pygame
# Importujeme TILE_SIZE a GRAY z configu
from config import TILE_SIZE, GRAY


# --- Třída Demoliční nálože ---
class DemolitionCharge(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # --- Načtení obrázku bomby ---
        try:
            original_image = pygame.image.load("images/bomb.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            print(f"Chyba při načítání obrázku bomby: {e}. Používám fallback šedou kostku.")
            self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
            self.image.fill(GRAY)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.timer = 2000  # Doba do výbuchu (v ms)
        self.explosion_time = pygame.time.get_ticks() + self.timer
        self.exploded = False
        self.explosion_duration = 500
        self.explosion_start_time = 0
        self.explosion_range = 2
