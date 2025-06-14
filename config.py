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
GAME_STATE_HIGHSCORES = 4

# Typy dlaždic v mapě
TILE_EMPTY = 0
TILE_WALL = 1
TILE_BREAKABLE = 2
TILE_PLAYER_START = 3
TILE_EXIT = 4
TILE_COLLECTIBLE = 5

# Název souboru pro ukládání highscores
HIGHSCORE_FILE = "highscores.json"