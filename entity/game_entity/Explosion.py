import pygame

from config import TILE_SIZE, EXPLOSION_COLOR, ORANGE

# --- Třída Exploze (vizuální efekt a detekce poškození hráče) ---
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, explosion_duration, frame_duration):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(EXPLOSION_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.start_time = pygame.time.get_ticks()
        self.explosion_duration = explosion_duration
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.damage_dealt = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.start_time > self.explosion_duration:
            self.kill()
        else:
            self.current_frame = (now - self.start_time) // self.frame_duration
            if self.current_frame % 2 == 0:
                self.image.fill(EXPLOSION_COLOR)
            else:
                self.image.fill(ORANGE)
