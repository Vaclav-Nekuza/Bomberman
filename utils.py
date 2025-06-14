import pygame
import numpy as np
import random
import json
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, HUD_HEIGHT,
    TILE_WALL, TILE_BREAKABLE, TILE_EMPTY, TILE_PLAYER_START, TILE_EXIT, TILE_COLLECTIBLE,
    HIGHSCORE_FILE, BLACK, WHITE, GREEN
)


# --- Funkce pro správu výsledků ---
def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            data = json.load(f)
            return data.get("highscores", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_highscores(new_score_entry):
    scores = load_highscores()
    scores.append(new_score_entry)

    scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    scores = scores[:10]

    data = {"highscores": scores}
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --- Funkce pro generování mapy bludiště ---
def generate_map(width_tiles, height_tiles):
    game_map = np.ones((height_tiles, width_tiles), dtype=int) * TILE_WALL

    stack = []
    start_x_gen, start_y_gen = random.randrange(1, width_tiles - 1, 2), random.randrange(1, height_tiles - 1, 2)
    game_map[start_y_gen, start_x_gen] = TILE_EMPTY
    stack.append(((start_x_gen, start_y_gen), (start_x_gen, start_y_gen)))

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

    empty_positions = [(x, y) for y in range(height_tiles) for x in range(width_tiles) if game_map[y, x] == TILE_EMPTY]

    if not empty_positions:
        game_map[1, 1] = TILE_PLAYER_START
        game_map[height_tiles - 2, width_tiles - 2] = TILE_EXIT
        return game_map

    start_pos = random.choice(empty_positions)
    game_map[start_pos[1], start_pos[0]] = TILE_PLAYER_START

    for dy_clean in [-1, 0, 1]:
        for dx_clean in [-1, 0, 1]:
            cx, cy = start_pos[0] + dx_clean, start_pos[1] + dy_clean
            if 0 <= cx < width_tiles and 0 <= cy < height_tiles:
                if game_map[cy, cx] == TILE_WALL or game_map[cy, cx] == TILE_BREAKABLE:
                    game_map[cy, cx] = TILE_EMPTY
                    if (cx, cy) not in empty_positions:
                        empty_positions.append((cx, cy))

    if start_pos in empty_positions:
        empty_positions.remove(start_pos)

    exit_candidates = [p for p in empty_positions if p != start_pos and (
                abs(p[0] - start_pos[0]) > width_tiles / 3 or abs(p[1] - start_pos[1]) > height_tiles / 3)]
    if not exit_candidates:
        exit_candidates = [p for p in empty_positions if p != start_pos]
        if not exit_candidates:
            exit_pos = (start_pos[0] + 1 if start_pos[0] + 1 < width_tiles else start_pos[0] - 1, start_pos[1])
            if 0 <= exit_pos[0] < width_tiles and 0 <= exit_pos[1] < height_tiles:
                if game_map[exit_pos[1], exit_pos[0]] != TILE_EMPTY:
                    game_map[exit_pos[1], exit_pos[0]] = TILE_EMPTY
            else:
                exit_pos = (random.randrange(1, width_tiles - 1), random.randrange(1, height_tiles - 1))
                if game_map[exit_pos[1], exit_pos[0]] == TILE_WALL: game_map[exit_pos[1], exit_pos[0]] = TILE_EMPTY

        else:
            exit_pos = random.choice(exit_candidates)
    else:
        exit_pos = random.choice(exit_candidates)

    game_map[exit_pos[1], exit_pos[0]] = TILE_EXIT
    if exit_pos in empty_positions: empty_positions.remove(exit_pos)

    for y in range(1, height_tiles - 1):
        for x in range(1, width_tiles - 1):
            if game_map[y, x] == TILE_EMPTY and (x, y) != start_pos and (x, y) != exit_pos:
                is_near_player = abs(x - start_pos[0]) <= 1 and abs(y - start_pos[1]) <= 1
                is_near_exit = abs(x - exit_pos[0]) <= 1 and abs(y - exit_pos[1]) <= 1

                if not is_near_player and not is_near_exit:
                    if random.random() < 0.35:
                        game_map[y, x] = TILE_BREAKABLE
                    elif random.random() < 0.08:
                        game_map[y, x] = TILE_COLLECTIBLE
                elif game_map[y, x] == TILE_EMPTY and random.random() < 0.08:
                    game_map[y, x] = TILE_COLLECTIBLE

    return game_map


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