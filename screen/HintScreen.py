import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_STATE_MENU
from entity.ui_entity.Button import Button


class HintScreen:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.btn_back = Button(SCREEN_WIDTH - 230, SCREEN_HEIGHT - 80, 200, 70, "ZPĚT", GAME_STATE_MENU)

    def DrawHintScreen(self):

        self.font = pygame.font.SysFont('Arial', 24)
        background_image = pygame.image.load('images/hint.png')
        background_scaled = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        text_lines = [
            '\u2191 - pohyb nahoru',
            '\u2190 - pohyb doleva',
            '\u2192 - pohyb doprava',
            '\u2193 - pohyb dolů',
            'mezerník - položení bomby',
            '',
           # '',

            '*šipky je možné držet současně'
        ]

        text_surfaces = [self.font.render(line, True, (255, 255, 255)) for line in text_lines]
        font_rects = [surface.get_rect() for surface in text_surfaces]
        LEFT = SCREEN_HEIGHT // 4 + 30
        TOP = SCREEN_WIDTH // 4 - 50
        for i, rect in enumerate(font_rects):
            rect.topleft = (LEFT, TOP + i * 30)

        # Vykreslení obrázku na pozadí
        self.screen.blit(background_scaled, (0, 0))

       # self.screen.fill((0, 0, 0))
        for surface, rect in zip(text_surfaces, font_rects):
            self.screen.blit(surface, rect)

        self.btn_back.draw(self.screen)
