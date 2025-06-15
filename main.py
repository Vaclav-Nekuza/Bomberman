import pygame

# Importování všeho potřebného z našich modulů
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, HUD_HEIGHT,
    WHITE, BLACK, RED, GRAY, TILE_SIZE, GAME_STATE_INTRO, GAME_STATE_MENU, GAME_STATE_PLAYING,
    GAME_STATE_GAME_OVER, GAME_STATE_HIGHSCORES, GAME_STATE_PAUSED,
    TILE_WALL, TILE_BREAKABLE, TILE_PLAYER_START, TILE_EXIT, TILE_COLLECTIBLE, GAME_STATE_HARDNESS_CHOOSE, EASY_GAME,
    MEDIUM_GAME, HARD_GAME, GAME_STATE_HINT
)
from entity.game_entity.Collectible import Collectible
from entity.game_entity.DomolitionCharge import DemolitionCharge
from entity.game_entity.Exit import Exit
from entity.game_entity.Explosion import Explosion
from entity.game_entity.Player import Player
from entity.game_entity.Wall import Wall
from entity.ui_entity.Button import Button
from screen.HardnessSelectScreen import HardnessSelect
from screen.HintScreen import HintScreen
from utils import load_highscores, save_highscores, generate_map


class Game:
    """
    Třída zapouzdřující veškerou herní logiku a stav.
    """

    def __init__(self):
        """
        Inicializuje Pygame, herní okno, fonty, a všechny herní proměnné.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.hud_font = pygame.font.Font(None, 40)
        self.running = True
        self.current_game_state = GAME_STATE_INTRO
        self.intro_start_time = pygame.time.get_ticks()

        self._load_assets()
        self._initialize_game_variables()
        self._create_ui_elements()

    def _load_assets(self):
        """
        Načte herní assety, jako jsou obrázky a zvuky.
        """
        try:
            loaded_image = pygame.image.load("images/background.png").convert()
            self.background_image = pygame.transform.scale(loaded_image, (SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT))
        except pygame.error as e:
            print(f"Chyba při načítání obrázku pozadí: {e}. Pozadí bude bílé.")
            self.background_image = None

    def _initialize_game_variables(self):
        """
        Inicializuje nebo resetuje proměnné pro novou hru.
        """
        self.player = None
        self.all_sprites = pygame.sprite.Group()
        self.solid_walls = pygame.sprite.Group()
        self.breakable_walls = pygame.sprite.Group()
        self.demolition_charges = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.exits = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()

        self.score = 0
        self.game_timer = 120
        self.start_game_time = 0
        self.finish_time = 0
        self.message = ""
        self.message_timer = 0
        self.player_name_input = ""
        self.asking_for_name = False
        self.remaining_time_seconds = 0
        self.last_unpaused_time = 0
        pygame.key.set_repeat(0)

    def _create_ui_elements(self):
        """
        Vytvoří všechny UI prvky, jako jsou tlačítka a obrazovky.
        """
        # Společné obrazovky a selektory
        self.hint_screen = HintScreen(self.screen, self.font)
        self.hardness_selector = HardnessSelect(self.screen, self.font, self._initialize_game_level)

        # Tlačítka pro menu
        self.play_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 70, "HRÁT",
                                  GAME_STATE_HARDNESS_CHOOSE)
        self.highscores_button = Button(SCREEN_WIDTH // 2 - 290, SCREEN_HEIGHT // 2 + 20, 540, 70, "NEJLEPŠÍ VÝSLEDKY",
                                        GAME_STATE_HIGHSCORES)
        self.hint_button = Button(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 100, 340, 70, "NÁPOVĚDA",
                                  GAME_STATE_HINT)
        self.quit_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 200, 280, 70, "UKONČIT", pygame.QUIT)

        # Tlačítka pro obrazovku GAME OVER
        self.restart_button_game_over = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 70, "RESTART",
                                               GAME_STATE_PLAYING, font_size=50)
        self.menu_button_game_over = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 180, 200, 70, "MENU",
                                            GAME_STATE_MENU, font_size=50)

        # Tlačítka pro PAUSE menu
        self.resume_button_pause = Button(SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 - 40, 350, 70, "POKRAČOVAT",
                                          GAME_STATE_PLAYING, font_size=50)
        self.restart_game_pause = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 70, "RESTART",
                                         GAME_STATE_PLAYING, font_size=50)
        self.quit_game_pause = Button(SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 + 120, 350, 70, "UKONČIT HRU",
                                      GAME_STATE_MENU, font_size=50)

    def _initialize_game_level(self, time_in_seconds, bombs):
        """
        Nastaví herní mapu, hráče a všechny herní entity pro novou úroveň.
        """
        self._initialize_game_variables()
        self.game_timer = time_in_seconds
        self.remaining_time_seconds = self.game_timer

        map_width_tiles = SCREEN_WIDTH // TILE_SIZE
        map_height_tiles = (SCREEN_HEIGHT - HUD_HEIGHT) // TILE_SIZE
        game_map_array = generate_map(map_width_tiles, map_height_tiles)

        player_start_pos = (0, 0)

        for y in range(map_height_tiles):
            for x in range(map_width_tiles):
                tile_type = game_map_array[y, x]
                pos_x, pos_y = x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT
                if tile_type == TILE_WALL:
                    wall = Wall(pos_x, pos_y, TILE_WALL)
                    self.solid_walls.add(wall)
                    self.all_sprites.add(wall)
                elif tile_type == TILE_BREAKABLE:
                    breakable_wall = Wall(pos_x, pos_y, TILE_BREAKABLE)
                    self.breakable_walls.add(breakable_wall)
                    self.all_sprites.add(breakable_wall)
                elif tile_type == TILE_PLAYER_START:
                    player_start_pos = (pos_x, pos_y)
                elif tile_type == TILE_EXIT:
                    exit_tile = Exit(pos_x, pos_y)
                    self.exits.add(exit_tile)
                    self.all_sprites.add(exit_tile)
                elif tile_type == TILE_COLLECTIBLE:
                    collectible = Collectible(pos_x, pos_y, 20)
                    self.collectibles.add(collectible)
                    self.all_sprites.add(collectible)

        self.player = Player(player_start_pos[0], player_start_pos[1], bombs)
        self.all_sprites.add(self.player)

        self.start_game_time = pygame.time.get_ticks()
        self.last_unpaused_time = self.start_game_time

    def run(self):
        """
        Hlavní herní smyčka.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_events(self):
        """
        Zpracovává všechny uživatelské vstupy a události.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Zpracování událostí podle aktuálního stavu hry
            if self.current_game_state == GAME_STATE_MENU:
                self._handle_menu_events(event)
            elif self.current_game_state == GAME_STATE_HARDNESS_CHOOSE:
                self._handle_hardness_choose_events(event)
            elif self.current_game_state == GAME_STATE_HINT:
                if self.hint_screen.btn_back.handle_event(event) == GAME_STATE_MENU:
                    self.current_game_state = GAME_STATE_MENU
            elif self.current_game_state == GAME_STATE_PLAYING:
                self._handle_playing_events(event)
            elif self.current_game_state == GAME_STATE_GAME_OVER:
                self._handle_game_over_events(event)
            elif self.current_game_state == GAME_STATE_HIGHSCORES:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.current_game_state = GAME_STATE_MENU
            elif self.current_game_state == GAME_STATE_PAUSED:
                self._handle_paused_events(event)

    def _handle_menu_events(self, event):
        """Zpracování událostí v hlavním menu."""
        if self.play_button.handle_event(event):
            self.current_game_state = GAME_STATE_HARDNESS_CHOOSE
        if self.highscores_button.handle_event(event):
            self.current_game_state = GAME_STATE_HIGHSCORES
        if self.hint_button.handle_event(event):
            self.current_game_state = GAME_STATE_HINT
        if self.quit_button.handle_event(event):
            self.running = False

    def _handle_hardness_choose_events(self, event):
        """Zpracování událostí na obrazovce výběru obtížnosti."""
        if self.hardness_selector.EasyLevelButton.handle_event(event) == EASY_GAME:
            self.current_game_state = GAME_STATE_PLAYING
            self.hardness_selector.InitEasyLevel()
        elif self.hardness_selector.MediumLevelButton.handle_event(event) == MEDIUM_GAME:
            self.current_game_state = GAME_STATE_PLAYING
            self.hardness_selector.InitMediumLevel()
        elif self.hardness_selector.HardLevelButton.handle_event(event) == HARD_GAME:
            self.current_game_state = GAME_STATE_PLAYING
            self.hardness_selector.InitHardLevel()

    def _handle_playing_events(self, event):
        """Zpracování událostí během hraní."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_game_state = GAME_STATE_PAUSED
                self.last_unpaused_time = pygame.time.get_ticks()
            elif event.key == pygame.K_SPACE and self.player.demolition_charges > 0:
                self._place_demolition_charge()

    def _place_demolition_charge(self):
        """Položí demoliční nálož na mapu, pokud je to možné."""
        charge_x = (self.player.rect.x + TILE_SIZE // 2) // TILE_SIZE * TILE_SIZE
        charge_y = (self.player.rect.y + TILE_SIZE // 2 - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE
        charge_pos_world = (charge_x, charge_y + HUD_HEIGHT)

        # Zkontroluje, zda na dané pozici již není nálož
        can_place = not any(charge.rect.topleft == charge_pos_world for charge in self.demolition_charges)

        if can_place:
            charge = DemolitionCharge(charge_pos_world[0], charge_pos_world[1])
            self.demolition_charges.add(charge)
            self.all_sprites.add(charge)
            self.player.demolition_charges -= 1

    def _handle_game_over_events(self, event):
        """Zpracování událostí na obrazovce konce hry."""
        if self.asking_for_name:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.player_name_input:
                        save_highscores({"name": self.player_name_input, "score": self.score})
                        self.asking_for_name = False
                        self.player_name_input = ""
                        pygame.key.set_repeat(0)
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name_input = self.player_name_input[:-1]
                elif len(self.player_name_input) < 10 and (event.unicode.isalnum() or event.unicode == " "):
                    self.player_name_input += event.unicode
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.current_game_state = GAME_STATE_PLAYING
                    self.hardness_selector.InitByLastGame()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            if self.menu_button_game_over.handle_event(event):
                self.current_game_state = GAME_STATE_MENU
            if self.restart_button_game_over.handle_event(event):
                self.current_game_state = GAME_STATE_PLAYING
                self.hardness_selector.InitByLastGame()

    def _handle_paused_events(self, event):
        """Zpracování událostí v pauze."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._resume_game()

        if self.resume_button_pause.handle_event(event):
            self._resume_game()
        if self.restart_game_pause.handle_event(event):
            self.current_game_state = GAME_STATE_PLAYING
            self.hardness_selector.InitByLastGame()  # Restart s poslední obtížností
        if self.quit_game_pause.handle_event(event):
            self.current_game_state = GAME_STATE_MENU

    def _resume_game(self):
        """Obnoví hru z pauzy."""
        self.current_game_state = GAME_STATE_PLAYING
        self.start_game_time += (pygame.time.get_ticks() - self.last_unpaused_time)

    def update(self):
        """
        Aktualizuje stav hry na základě aktuálního herního stavu.
        """
        state_updaters = {
            GAME_STATE_INTRO: self._update_intro,
            GAME_STATE_PLAYING: self._update_playing
        }
        updater = state_updaters.get(self.current_game_state)
        if updater:
            updater()

    def _update_intro(self):
        """Aktualizace pro intro obrazovku."""
        if pygame.time.get_ticks() - self.intro_start_time > 3000:
            self.current_game_state = GAME_STATE_MENU

    def _update_playing(self):
        """Hlavní herní logika a aktualizace entit."""
        self.player.update(self.solid_walls, self.breakable_walls)
        self.demolition_charges.update()
        self.explosions.update()

        self._update_timer()
        self._check_charge_explosions()
        self._check_game_over_conditions()
        self._check_collectibles()

    def _update_timer(self):
        """Aktualizuje herní časovač."""
        elapsed_time_ms = pygame.time.get_ticks() - self.start_game_time
        self.remaining_time_seconds = self.game_timer - (elapsed_time_ms // 1000)
        if self.remaining_time_seconds < 0:
            self.remaining_time_seconds = 0

    def _check_charge_explosions(self):
        """Kontroluje a zpracovává výbuchy náloží."""
        for charge in list(self.demolition_charges):
            if not charge.exploded and pygame.time.get_ticks() >= charge.explosion_time:
                self._trigger_explosion(charge)
                charge.kill()

    def _trigger_explosion(self, charge):
        """Spustí výbuch a jeho efekty na okolí."""
        charge.exploded = True
        charge_tile_x = charge.rect.x // TILE_SIZE
        charge_tile_y = (charge.rect.y - HUD_HEIGHT) // TILE_SIZE

        explosion_tiles = self._calculate_explosion_tiles(charge_tile_x, charge_tile_y, charge.explosion_range)

        # Vytvoření vizuálních efektů exploze
        for ex, ey in explosion_tiles:
            explosion_effect = Explosion(ex * TILE_SIZE, ey * TILE_SIZE + HUD_HEIGHT, charge.explosion_duration, 100)
            self.explosions.add(explosion_effect)
            self.all_sprites.add(explosion_effect)
            # Kontrola kolize s hráčem
            if self.player.rect.colliderect(explosion_effect.rect):
                self.player.take_damage()

    def _calculate_explosion_tiles(self, start_x, start_y, aoe_range):
        """Vypočítá dlaždice zasažené výbuchem a zničí zdi."""
        explosion_tiles = {(start_x, start_y)}
        map_width_tiles = SCREEN_WIDTH // TILE_SIZE
        map_height_tiles = (SCREEN_HEIGHT - HUD_HEIGHT) // TILE_SIZE

        for dir_x, dir_y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, aoe_range + 1):
                tx, ty = start_x + i * dir_x, start_y + i * dir_y
                if not (0 <= tx < map_width_tiles and 0 <= ty < map_height_tiles):
                    break

                # Kolize s pevnou zdí
                if any(w.rect.x // TILE_SIZE == tx and (w.rect.y - HUD_HEIGHT) // TILE_SIZE == ty for w in
                       self.solid_walls):
                    explosion_tiles.add((tx, ty))
                    break

                # Kolize s rozbitnou zdí
                breakable_wall_hit = next((w for w in self.breakable_walls if
                                           w.rect.x // TILE_SIZE == tx and (w.rect.y - HUD_HEIGHT) // TILE_SIZE == ty),
                                          None)
                if breakable_wall_hit:
                    explosion_tiles.add((tx, ty))
                    breakable_wall_hit.kill()  # Zničí zeď
                    break

                explosion_tiles.add((tx, ty))
        return explosion_tiles

    def _check_game_over_conditions(self):
        """Kontroluje, zda hra neskončila."""
        player_on_exit = pygame.sprite.spritecollideany(self.player, self.exits)
        time_up = self.remaining_time_seconds <= 0
        no_lives = self.player.lives <= 0

        if player_on_exit or time_up or no_lives:
            self.current_game_state = GAME_STATE_GAME_OVER
            if player_on_exit and not time_up and not no_lives:
                self.finish_time = pygame.time.get_ticks()
                self.asking_for_name = True
                pygame.key.set_repeat(500, 50)
            else:
                self.asking_for_name = False
                pygame.key.set_repeat(0)

    def _check_collectibles(self):
        """Kontroluje sbírání předmětů."""
        collected_items = pygame.sprite.spritecollide(self.player, self.collectibles, True)
        for item in collected_items:
            self.score += item.value
            self.message = f"+{item.value} Bodů!"
            self.message_timer = pygame.time.get_ticks() + 1000

    def draw(self):
        """
        Vykreslí vše na obrazovku na základě aktuálního stavu hry.
        """
        # Slovník mapující stavy na vykreslovací funkce
        state_drawers = {
            GAME_STATE_INTRO: self._draw_intro,
            GAME_STATE_MENU: self._draw_menu,
            GAME_STATE_HARDNESS_CHOOSE: self.hardness_selector.DrawHardnessScreen,
            GAME_STATE_HINT: self.hint_screen.DrawHintScreen,
            GAME_STATE_PLAYING: self._draw_playing,
            GAME_STATE_GAME_OVER: self._draw_game_over,
            GAME_STATE_HIGHSCORES: self._draw_highscores,
            GAME_STATE_PAUSED: self._draw_paused,
        }

        drawer = state_drawers.get(self.current_game_state)
        if drawer:
            drawer()

        pygame.display.flip()

    def _draw_intro(self):
        self.screen.fill(BLACK)
        intro_text = self.font.render(TITLE, True, WHITE)
        self.screen.blit(intro_text, intro_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
        subtitle_text = self.font.render("Proklestěte si cestu k cíli!", True, GRAY)
        self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))

    def _draw_menu(self):
        self.screen.fill(BLACK)
        menu_text = self.font.render("MENU", True, WHITE)
        self.screen.blit(menu_text, menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)))
        self.play_button.draw(self.screen)
        self.highscores_button.draw(self.screen)
        self.hint_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def _draw_playing(self):
        # Vykreslení pozadí
        if self.background_image:
            self.screen.blit(self.background_image, (0, HUD_HEIGHT))
        else:
            self.screen.fill(WHITE)

        self.all_sprites.draw(self.screen)
        self._draw_hud()

        if self.message and pygame.time.get_ticks() < self.message_timer:
            msg_surface = self.font.render(self.message, True, RED)
            self.screen.blit(msg_surface, msg_surface.get_rect(center=(SCREEN_WIDTH // 2, HUD_HEIGHT + 20)))
        elif pygame.time.get_ticks() >= self.message_timer:
            self.message = ""

    def _draw_hud(self):
        """Vykreslí Head-Up Display (skóre, životy, atd.)."""
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))

        score_text = self.hud_font.render(f"Skóre: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, (HUD_HEIGHT - score_text.get_height()) // 2))

        lives_text = self.hud_font.render(f"Životy: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, lives_text.get_rect(centerx=SCREEN_WIDTH // 2, centery=HUD_HEIGHT // 2))

        charges_text = self.hud_font.render(f"Nálože: {self.player.demolition_charges}", True, WHITE)
        charges_rect = charges_text.get_rect(right=SCREEN_WIDTH - 10, centery=HUD_HEIGHT // 2)
        self.screen.blit(charges_text, charges_rect)

        timer_text = self.hud_font.render(f"Čas: {max(0, self.remaining_time_seconds)}s", True, WHITE)
        timer_rect = timer_text.get_rect(right=charges_rect.left - 20, centery=HUD_HEIGHT // 2)
        self.screen.blit(timer_text, timer_rect)

    def _draw_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("KONEC HRY!", True, WHITE)
        self.screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))

        score_text = self.font.render(f"Vaše skóre: {self.score}", True, WHITE)
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))

        if self.finish_time > 0 and (
                self.player.lives > 0 and (self.finish_time - self.start_game_time) // 1000 < self.game_timer):
            time_taken = (self.finish_time - self.start_game_time) // 1000
            time_text = self.font.render(f"Čas dokončení: {time_taken}s", True, WHITE)
        else:
            reason = "Čas vypršel!" if self.player.lives > 0 else "Životy vypršely!"
            time_text = self.font.render(reason, True, RED)
        self.screen.blit(time_text, time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        if self.asking_for_name:
            name_prompt = self.font.render(f"Zadejte své jméno: {self.player_name_input}_", True, WHITE)
            self.screen.blit(name_prompt, name_prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))
        else:
            self.restart_button_game_over.draw(self.screen)
            self.menu_button_game_over.draw(self.screen)
            esc_text = self.font.render("ESC pro ukončení", True, GRAY)
            self.screen.blit(esc_text, esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 270)))

    def _draw_highscores(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("NEJLEPŠÍ VÝSLEDKY", True, WHITE)
        self.screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))

        scores_list = load_highscores()
        if scores_list:
            for i, entry in enumerate(scores_list):
                line = f"{i + 1}. {entry.get('name', 'N/A')} - {entry.get('score', 0)}"
                score_text = self.hud_font.render(line, True, WHITE)
                self.screen.blit(score_text, score_text.get_rect(centerx=SCREEN_WIDTH // 2, y=120 + i * 40))
        else:
            no_scores_text = self.hud_font.render("Zatím nejsou žádné výsledky.", True, GRAY)
            self.screen.blit(no_scores_text, no_scores_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        back_text = self.font.render("Stiskněte 'ESC' pro návrat do menu", True, GRAY)
        self.screen.blit(back_text, back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

    def _draw_paused(self):
        # Nejdříve vykreslíme herní scénu, abychom ji měli pod pauzou
        self._draw_playing()
        # Přidáme ztmavující vrstvu
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        self.screen.blit(s, (0, 0))

        pause_text = self.font.render("PAUZA", True, WHITE)
        self.screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)))

        self.resume_button_pause.draw(self.screen)
        self.restart_game_pause.draw(self.screen)
        self.quit_game_pause.draw(self.screen)


if __name__ == "__main__":
    game = Game()
    game.run()