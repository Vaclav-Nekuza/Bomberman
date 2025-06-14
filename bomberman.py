import pygame
import numpy as np
import random

# --- Konfigurace hry ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Průzkumník bludiště"
FPS = 60

# Výška HUD (Head-Up Display) oblasti nahoře
HUD_HEIGHT = 70

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
EXPLOSION_COLOR = (255, 100, 0)

# Velikost dlaždice/bloku
TILE_SIZE = 40

# Stav hry
GAME_STATE_INTRO = 0
GAME_STATE_MENU = 1
GAME_STATE_PLAYING = 2
GAME_STATE_GAME_OVER = 3

# Typy dlaždic v mapě
TILE_EMPTY = 0
TILE_WALL = 1
TILE_BREAKABLE = 2
TILE_PLAYER_START = 3
TILE_EXIT = 4
TILE_COLLECTIBLE = 5


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
        if self.tile_type == TILE_WALL:
            self.image.fill(BLACK)
        elif self.tile_type == TILE_BREAKABLE:
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


# --- Třída tlačítka pro menu ---
class Button:
    def __init__(self, x, y, width, height, text, action, font_size=74):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, font_size)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, GREEN, self.rect, border_radius=5)
        else:
            pygame.draw.rect(screen, BLACK, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=5)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None


# --- Funkce pro generování mapy bludiště ---
def generate_map(width_tiles, height_tiles):
    game_map = np.ones((height_tiles, width_tiles), dtype=int) * TILE_WALL

    stack = []
    start_x, start_y = random.randrange(1, width_tiles - 1, 2), random.randrange(1, height_tiles - 1, 2)
    game_map[start_y, start_x] = TILE_EMPTY
    stack.append(((start_x, start_y), (start_x, start_y)))

    while stack:
        (cx, cy), (px, py) = stack.pop()
        game_map[cy, cx] = TILE_EMPTY
        if cx != px:
            game_map[cy, cx - (cx - px) // 2] = TILE_EMPTY
        if cy != py:
            game_map[cy - (cy - py) // 2, cx] = TILE_EMPTY

        neighbors = []
        for nx, ny in [(cx + 2, cy), (cx - 2, cy), (cx, cy + 2), (cx, cy - 2)]:
            if 0 < nx < width_tiles - 1 and 0 < ny < height_tiles - 1 and game_map[ny, nx] == TILE_WALL:
                neighbors.append(((nx, ny), (cx, cy)))

        random.shuffle(neighbors)
        stack.extend(neighbors)

    for y in range(1, height_tiles - 1):
        for x in range(1, width_tiles - 1):
            if game_map[y, x] == TILE_EMPTY:
                if random.random() < 0.3:
                    game_map[y, x] = TILE_BREAKABLE
                elif random.random() < 0.05:
                    game_map[y, x] = TILE_COLLECTIBLE

    empty_positions = [(x, y) for y in range(height_tiles) for x in range(width_tiles) if game_map[y, x] == TILE_EMPTY]

    if not empty_positions:
        game_map[1, 1] = TILE_PLAYER_START
        game_map[height_tiles - 2, width_tiles - 2] = TILE_EXIT
        return game_map

    start_pos = random.choice(empty_positions)
    game_map[start_pos[1], start_pos[0]] = TILE_PLAYER_START
    empty_positions.remove(start_pos)

    exit_pos = random.choice(empty_positions) if empty_positions else (1, 1)
    game_map[exit_pos[1], exit_pos[0]] = TILE_EXIT

    return game_map


# --- Hlavní herní smyčka ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    hud_font = pygame.font.Font(None, 40)

    current_game_state = GAME_STATE_INTRO
    intro_start_time = pygame.time.get_ticks()

    player = None
    all_sprites = pygame.sprite.Group()
    solid_walls = pygame.sprite.Group()
    breakable_walls = pygame.sprite.Group()
    demolition_charges = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    exits = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()

    score = 0
    game_timer = 120
    start_game_time = 0
    finish_time = 0  # Nová proměnná pro uložení času dokončení
    message = ""
    message_timer = 0

    play_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 70, "HRÁT", GAME_STATE_PLAYING)
    quit_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 80, 280, 70, "UKONČIT", pygame.QUIT)

    def draw_intro_screen():
        screen.fill(BLACK)
        intro_text = font.render(TITLE, True, WHITE)
        text_rect = intro_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(intro_text, text_rect)
        subtitle_text = font.render("Proklestěte si cestu k cíli!", True, GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(subtitle_text, subtitle_rect)

    def draw_menu_screen():
        screen.fill(BLACK)
        menu_text = font.render("MENU", True, WHITE)
        text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(menu_text, text_rect)
        play_button.draw(screen)
        quit_button.draw(screen)

    def draw_game_over_screen():
        screen.fill(BLACK)
        game_over_text = font.render("KONEC HRY!", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, text_rect)

        score_text = font.render(f"Vaše skóre: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, score_rect)

        # Zobrazení času dokončení
        if finish_time > 0:  # Zobrazit čas jen pokud hra byla dokončena cílem
            time_taken = (finish_time - start_game_time) // 1000
            time_text = font.render(f"Čas dokončení: {time_taken}s", True, WHITE)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(time_text, time_rect)
        else:  # Jinak se zobrazí, že čas vypršel nebo že hráč zemřel
            time_text = font.render("Čas vypršel!" if player.lives > 0 else "Životy vypršely!", True, RED)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(time_text, time_rect)

        restart_text = font.render("Stiskněte 'R' pro restart nebo 'ESC' pro ukončení", True, GRAY)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    def initialize_game_level():
        nonlocal player, score, game_timer, start_game_time, finish_time, message, message_timer
        all_sprites.empty()
        solid_walls.empty()
        breakable_walls.empty()
        demolition_charges.empty()
        explosions.empty()
        exits.empty()
        collectibles.empty()
        score = 0
        game_timer = 120
        message = ""
        message_timer = 0
        finish_time = 0  # Reset času dokončení

        map_width_tiles = SCREEN_WIDTH // TILE_SIZE
        map_height_tiles = (SCREEN_HEIGHT - HUD_HEIGHT) // TILE_SIZE
        game_map_array = generate_map(map_width_tiles, map_height_tiles)

        player_start_pos = (0, 0)

        for y in range(map_height_tiles):
            for x in range(map_width_tiles):
                tile_type = game_map_array[y, x]
                if tile_type == TILE_WALL:
                    wall = Wall(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT, TILE_WALL)
                    solid_walls.add(wall)
                    all_sprites.add(wall)
                elif tile_type == TILE_BREAKABLE:
                    breakable_wall = Wall(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT, TILE_BREAKABLE)
                    breakable_walls.add(breakable_wall)
                    all_sprites.add(breakable_wall)
                elif tile_type == TILE_PLAYER_START:
                    player_start_pos = (x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT)
                elif tile_type == TILE_EXIT:
                    exit_tile = Exit(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT)
                    exits.add(exit_tile)
                    all_sprites.add(exit_tile)
                elif tile_type == TILE_COLLECTIBLE:
                    collectible = Collectible(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT, 20)
                    collectibles.add(collectible)
                    all_sprites.add(collectible)

        player = Player(player_start_pos[0], player_start_pos[1])
        all_sprites.add(player)

        start_game_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_game_state == GAME_STATE_INTRO:
                pass
            elif current_game_state == GAME_STATE_MENU:
                action = play_button.handle_event(event)
                if action == GAME_STATE_PLAYING:
                    current_game_state = action
                    initialize_game_level()

                action_quit = quit_button.handle_event(event)
                if action_quit == pygame.QUIT:
                    running = False
            elif current_game_state == GAME_STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        charge_x = (player.rect.x + TILE_SIZE // 2) // TILE_SIZE * TILE_SIZE
                        charge_y = (player.rect.y + TILE_SIZE // 2 - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE

                        charge_x_world = charge_x
                        charge_y_world = charge_y + HUD_HEIGHT

                        if player.demolition_charges > 0:
                            can_place = True
                            for existing_charge in demolition_charges:
                                if existing_charge.rect.topleft == (charge_x_world, charge_y_world):
                                    can_place = False
                                    break
                            if can_place:
                                charge = DemolitionCharge(charge_x_world, charge_y_world)
                                demolition_charges.add(charge)
                                all_sprites.add(charge)
                                player.demolition_charges -= 1
            elif current_game_state == GAME_STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        current_game_state = GAME_STATE_MENU
                    if event.key == pygame.K_ESCAPE:
                        running = False

        # --- Aktualizace herního stavu ---
        if current_game_state == GAME_STATE_INTRO:
            if pygame.time.get_ticks() - intro_start_time > 3000:
                current_game_state = GAME_STATE_MENU
            draw_intro_screen()

        elif current_game_state == GAME_STATE_MENU:
            draw_menu_screen()

        elif current_game_state == GAME_STATE_PLAYING:
            player.update(solid_walls, breakable_walls)

            for charge in list(demolition_charges):
                if not charge.exploded and pygame.time.get_ticks() >= charge.explosion_time:
                    charge.exploded = True
                    charge_tile_x = charge.rect.x // TILE_SIZE
                    charge_tile_y = (charge.rect.y - HUD_HEIGHT) // TILE_SIZE

                    explosion_tiles_to_create = set()
                    tiles_to_destroy = []

                    explosion_tiles_to_create.add((charge_tile_x, charge_tile_y))

                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    map_width_tiles = SCREEN_WIDTH // TILE_SIZE
                    map_height_tiles = (SCREEN_HEIGHT - HUD_HEIGHT) // TILE_SIZE

                    for dir_x, dir_y in directions:
                        for i in range(1, charge.explosion_range + 1):
                            tx = charge_tile_x + i * dir_x
                            ty = charge_tile_y + i * dir_y

                            if not (0 <= tx < map_width_tiles and 0 <= ty < map_height_tiles):
                                break

                            current_tile_is_solid_wall = False
                            current_tile_is_breakable_wall = False
                            current_breakable_wall_obj = None

                            for sw in solid_walls:
                                if sw.rect.x // TILE_SIZE == tx and (sw.rect.y - HUD_HEIGHT) // TILE_SIZE == ty:
                                    current_tile_is_solid_wall = True
                                    break

                            if current_tile_is_solid_wall:
                                explosion_tiles_to_create.add((tx, ty))
                                break

                            for bw in breakable_walls:
                                if bw.rect.x // TILE_SIZE == tx and (bw.rect.y - HUD_HEIGHT) // TILE_SIZE == ty:
                                    current_tile_is_breakable_wall = True
                                    current_breakable_wall_obj = bw
                                    break

                            if current_tile_is_breakable_wall:
                                explosion_tiles_to_create.add((tx, ty))
                                tiles_to_destroy.append(current_breakable_wall_obj)
                                break

                            explosion_tiles_to_create.add((tx, ty))

                    for ex, ey in explosion_tiles_to_create:
                        explosion_effect = Explosion(ex * TILE_SIZE, ey * TILE_SIZE + HUD_HEIGHT,
                                                     charge.explosion_duration, 100)
                        explosions.add(explosion_effect)
                        all_sprites.add(explosion_effect)

                        if player.rect.colliderect(explosion_effect.rect):
                            player.take_damage()
                            if player.lives <= 0:
                                current_game_state = GAME_STATE_GAME_OVER

                    for wall_to_destroy in tiles_to_destroy:
                        breakable_walls.remove(wall_to_destroy)
                        all_sprites.remove(wall_to_destroy)

                    charge.kill()

            demolition_charges.update()
            explosions.update()

            if player.lives <= 0:
                current_game_state = GAME_STATE_GAME_OVER

            # Detekce dosažení cíle
            if pygame.sprite.spritecollideany(player, exits):
                if current_game_state == GAME_STATE_PLAYING:  # Zajistíme, že se čas zaznamená jen jednou
                    finish_time = pygame.time.get_ticks()
                message = "Cíl nalezen! Skóre +100!"
                score += 100
                message_timer = pygame.time.get_ticks() + 2000
                current_game_state = GAME_STATE_GAME_OVER

            collected_items = pygame.sprite.spritecollide(player, collectibles, True)
            for item in collected_items:
                score += item.value
                message = f"+{item.value} Bodů!"
                message_timer = pygame.time.get_ticks() + 1000

            elapsed_time_ms = pygame.time.get_ticks() - start_game_time
            remaining_time_seconds = game_timer - (elapsed_time_ms // 1000)
            if remaining_time_seconds <= 0:
                current_game_state = GAME_STATE_GAME_OVER

            screen.fill(WHITE)

            pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))

            all_sprites.draw(screen)

            score_text_surface = hud_font.render(f"Skóre: {score}", True, WHITE)
            screen.blit(score_text_surface, (10, (HUD_HEIGHT - score_text_surface.get_height()) // 2))

            lives_text_surface = hud_font.render(f"Životy: {player.lives}", True, WHITE)
            screen.blit(lives_text_surface, (SCREEN_WIDTH // 2 - lives_text_surface.get_width() // 2,
                                             (HUD_HEIGHT - lives_text_surface.get_height()) // 2))

            charges_text_surface = hud_font.render(f"Nálože: {player.demolition_charges}", True, WHITE)
            screen.blit(charges_text_surface, (SCREEN_WIDTH - charges_text_surface.get_width() - 10,
                                               (HUD_HEIGHT - charges_text_surface.get_height()) // 2))

            timer_text_surface = hud_font.render(f"Čas: {max(0, remaining_time_seconds)}s", True, WHITE)
            screen.blit(timer_text_surface,
                        (SCREEN_WIDTH - charges_text_surface.get_width() - 10 - timer_text_surface.get_width() - 20,
                         (HUD_HEIGHT - timer_text_surface.get_height()) // 2))

            if message and pygame.time.get_ticks() < message_timer:
                msg_surface = font.render(message, True, RED)
                msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, HUD_HEIGHT + 20))
                screen.blit(msg_surface, msg_rect)
            elif pygame.time.get_ticks() >= message_timer:
                message = ""

        elif current_game_state == GAME_STATE_GAME_OVER:
            draw_game_over_screen()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
