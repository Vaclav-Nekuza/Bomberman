import pygame

from config import GREEN, BLACK, WHITE

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
