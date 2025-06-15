import pygame
# Importujeme TILE_SIZE a GREEN z configu
from config import TILE_SIZE, GREEN
# --- Třída Cíle (výstup z bludiště) ---
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # ---Načtení obrázku dveří ---
        try:
            original_image = pygame.image.load("images/door.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            print(f"Chyba při načítání obrázku dveří: {e}. Používám fallback zelenou kostku.")
            self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)