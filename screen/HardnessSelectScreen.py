from config import WHITE, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT, EASY_GAME, MEDIUM_GAME, HARD_GAME, EASY_GAME_TIME, \
    EASY_GAME_BOMBS, MEDIUM_GAME_TIME, MEDIUM_GAME_BOMBS, HARD_GAME_TIME, HARD_GAME_BOMBS
from entity.ui_entity.Button import Button


class HardnessSelect:
    BUTTON_WITH = 250
    BUTTON_HEIGHT = 70
    def __init__(self,screen,font,init_game_method):
        self.screen = screen
        self.menu_title =font.render("Vyberte obtížnost hry", True, WHITE)
        self.EasyLevelButton = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 80, self.BUTTON_WITH, self.BUTTON_HEIGHT, "EASY", EASY_GAME)
        self.MediumLevelButton = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 , self.BUTTON_WITH, self.BUTTON_HEIGHT, "MEDIUM", MEDIUM_GAME)
        self.HardLevelButton = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, self.BUTTON_WITH, self.BUTTON_HEIGHT, "HARD", HARD_GAME)
        self.init_game_method = init_game_method
        self.last_game_variant = None

        self.game_variant = {
            EASY_GAME: self.InitEasyLevel,
            MEDIUM_GAME: self.InitMediumLevel,
            HARD_GAME: self.InitHardLevel,
        }

    def DrawHardnessScreen(self):
        self.screen.fill(BLACK)
        text_rect = self.menu_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(self.menu_title, text_rect)

        self.EasyLevelButton.draw(self.screen)
        self.MediumLevelButton.draw(self.screen)
        self.HardLevelButton.draw(self.screen)

    def InitEasyLevel(self):
        self.last_game_variant = EASY_GAME
        self.init_game_method(EASY_GAME_TIME,EASY_GAME_BOMBS)

    def InitMediumLevel(self):
        self.last_game_variant = MEDIUM_GAME
        self.init_game_method(MEDIUM_GAME_TIME,MEDIUM_GAME_BOMBS)

    def InitHardLevel(self):
        self.last_game_variant = HARD_GAME
        self.init_game_method(HARD_GAME_TIME,HARD_GAME_BOMBS)

    def InitByLastGame(self):
        self.game_variant.get(self.last_game_variant)()




