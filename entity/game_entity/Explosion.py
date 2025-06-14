import pygame
from config import TILE_SIZE, EXPLOSION_COLOR, ORANGE


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, explosion_duration, frame_duration):
        super().__init__()

        # --- ZMĚNA ZDE: Načítání a příprava animace ---
        # Obrázek je nyní ve STEJNÉ SLOŽCE jako tento soubor, takže stačí jen název souboru.
        try:
            self.spritesheet = pygame.image.load(
                "entity/game_entity/explosion-sheet.png").convert_alpha()  # <--- OPRAVENÁ CESTA
        except pygame.error as e:
            print(f"Chyba při načítání spritesheetu exploze: {e}. Používám fallback barvu.")
            self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
            self.image.fill(EXPLOSION_COLOR)
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)
            self.has_animation = False
            self.kill_timer = pygame.time.get_ticks() + explosion_duration
            return

        self.frame_width = 32
        self.frame_height = 32
        self.num_frames = self.spritesheet.get_width() // self.frame_width

        self.frames = []
        for i in range(self.num_frames):
            frame_rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame_image = self.spritesheet.subsurface(frame_rect)

            frame_image = pygame.transform.scale(frame_image, (TILE_SIZE, TILE_SIZE))
            self.frames.append(frame_image)

        self.current_frame_index = 0
        self.image = self.frames[self.current_frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.start_time = pygame.time.get_ticks()
        self.explosion_duration = explosion_duration
        self.frame_duration = self.explosion_duration // self.num_frames
        if self.frame_duration == 0: self.frame_duration = 1

        self.last_frame_update = pygame.time.get_ticks()
        self.damage_dealt = False
        self.has_animation = True

    def update(self):
        if not self.has_animation:
            if pygame.time.get_ticks() > self.kill_timer:
                self.kill()
            return

        now = pygame.time.get_ticks()

        if now - self.start_time > self.explosion_duration:
            self.kill()
        else:
            if now - self.last_frame_update > self.frame_duration:
                self.current_frame_index = (self.current_frame_index + 1)
                if self.current_frame_index < self.num_frames:
                    self.image = self.frames[self.current_frame_index]
                    self.last_frame_update = now
                else:
                    self.kill()