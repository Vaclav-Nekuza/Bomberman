import pygame
from config import TILE_SIZE, BLUE

# --- Třída Hráče ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # --- Načtení obrázku hráče ---
        try:
            original_image = pygame.image.load("images/player_character.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE - 4, TILE_SIZE - 4))
        except pygame.error as e:
            print(f"Chyba při načítání obrázku hráče: {e}. Používám fallback modrou kostku.")
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
        distance = 8
        skip = 1
        for wall in walls_group:
            if self.rect.colliderect(wall.rect):
                if dx > 0:
                    self.rect.right = wall.rect.left
                    if abs(self.rect.bottom - wall.rect.top) < distance:
                        self.rect.y -= skip
                    elif abs(self.rect.top - wall.rect.bottom) < distance:
                        self.rect.y += skip
                elif dx < 0:
                    self.rect.left = wall.rect.right
                    if abs(self.rect.bottom - wall.rect.top) < distance:
                        self.rect.y -= skip
                    elif abs(self.rect.top - wall.rect.bottom) < distance:
                        self.rect.y += skip

                if dy > 0:
                    self.rect.bottom = wall.rect.top
                    if abs(self.rect.right - wall.rect.left) < distance:
                        self.rect.x -= skip
                    elif abs(self.rect.left - wall.rect.right) < distance:
                        self.rect.x += skip
                elif dy < 0:
                    self.rect.top = wall.rect.bottom
                    if abs(self.rect.right - wall.rect.left) < distance:
                        self.rect.x -= skip
                    elif abs(self.rect.left - wall.rect.right) < distance:
                        self.rect.x += skip

    def take_damage(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks() + self.hit_cooldown
            self.image.set_alpha(100)