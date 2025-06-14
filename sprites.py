import pygame
# Numpy není přímo potřeba pro tyto třídy, ale pokud byste jej v budoucnu přidával do sprite logiky, přidejte zde import.
from config import TILE_SIZE, BLUE, BLACK, BROWN, GRAY, EXPLOSION_COLOR, ORANGE, GREEN, YELLOW


# --- Třída Hráče ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE - 4, TILE_SIZE - 4])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 4
        self.demolition_charges = 3
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0
        self.hit_cooldown = 1000
        self.anim_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 150

    def update(self, solid_walls, breakable_walls):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.anim_frame = (self.anim_frame + 1) % 2
            self.last_update = now

        if self.invincible and now > self.invincible_timer:
            self.invincible = False
            self.image.set_alpha(255)

        if self.invincible and now % 200 < 100:
            self.image.set_alpha(100)
        elif self.image.get_alpha() != 255:
            self.image.set_alpha(255)

        self.rect.x += dx
        self.handle_collision(solid_walls, dx, 0)
        self.handle_collision(breakable_walls, dx, 0)

        self.rect.y += dy
        self.handle_collision(solid_walls, 0, dy)
        self.handle_collision(breakable_walls, 0, dy)

    def handle_collision(self, walls_group, dx, dy):
        for wall in walls_group:
            if self.rect.colliderect(wall.rect):
                if dx > 0:
                    self.rect.right = wall.rect.left
                elif dx < 0:
                    self.rect.left = wall.rect.right

                if dy > 0:
                    self.rect.bottom = wall.rect.top
                elif dy < 0:
                    self.rect.top = wall.rect.bottom

    def take_damage(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks() + self.hit_cooldown
            self.image.set_alpha(100)


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


# --- Třída Cíle (výstup z bludiště) ---
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# --- Třída Sbíratelného předmětu ---
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        self.image = pygame.Surface([TILE_SIZE // 2, TILE_SIZE // 2])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)