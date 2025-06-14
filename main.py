import pygame

# Importování všeho potřebného z našich modulů
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, HUD_HEIGHT,
    WHITE, BLACK, RED, GRAY, TILE_SIZE, GAME_STATE_INTRO, GAME_STATE_MENU, GAME_STATE_PLAYING,
    GAME_STATE_GAME_OVER, GAME_STATE_HIGHSCORES, GAME_STATE_PAUSED,
    TILE_WALL, TILE_BREAKABLE, TILE_PLAYER_START, TILE_EXIT, TILE_COLLECTIBLE, GAME_STATE_HARDNESS_CHOOSE, EASY_GAME,
    MEDIUM_GAME, HARD_GAME
)
from entity.game_entity.Collectible import Collectible
from entity.game_entity.DomolitionCharge import DemolitionCharge
from entity.game_entity.Exit import Exit
from entity.game_entity.Explosion import Explosion
from entity.game_entity.Player import Player
from entity.game_entity.Wall import Wall
from entity.ui_entity.Button import Button
from screen.HardnessSelectScreen import HardnessSelect
from utils import load_highscores, save_highscores, generate_map


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
    finish_time = 0
    message = ""
    message_timer = 0
    player_name_input = ""
    asking_for_name = False
    LAST_GAME_VARIANT = None

    remaining_time_seconds = 0
    last_unpaused_time = pygame.time.get_ticks()



    # Tlačítka pro menu
    play_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 70, "HRÁT", GAME_STATE_HARDNESS_CHOOSE)
    highscores_button = Button(SCREEN_WIDTH // 2 - 290, SCREEN_HEIGHT // 2 + 40, 540, 70, "NEJLEPŠÍ VÝSLEDKY",
                               GAME_STATE_HIGHSCORES)
    quit_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 120, 280, 70, "UKONČIT", pygame.QUIT)

    # Tlačítka pro obrazovku GAME OVER
    restart_button_game_over = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 70, "RESTART",
                                      GAME_STATE_PLAYING, font_size=50)
    menu_button_game_over = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 180, 200, 70, "MENU", GAME_STATE_MENU,
                                   font_size=50)

    # Tlačítka pro PAUSE menu
    resume_button_pause = Button(SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 - 40, 350, 70, "POKRAČOVAT",
                                 GAME_STATE_PLAYING, font_size=50)
    restart_game_pause = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 70, "RESTART",
                                GAME_STATE_PLAYING, font_size=50)
    quit_game_pause = Button(SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 + 120, 350, 70, "UKONČIT HRU", GAME_STATE_MENU,
                             font_size=50)

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
        highscores_button.draw(screen)
        quit_button.draw(screen)

    def draw_game_over_screen():
        nonlocal player_name_input, asking_for_name
        screen.fill(BLACK)
        game_over_text = font.render("KONEC HRY!", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, text_rect)

        score_text = font.render(f"Vaše skóre: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, score_rect)

        if finish_time > 0 and (player.lives > 0 and (finish_time - start_game_time) // 1000 < game_timer):
            time_taken = (finish_time - start_game_time) // 1000
            time_text = font.render(f"Čas dokončení: {time_taken}s", True, WHITE)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(time_text, time_rect)
        else:
            time_text = font.render("Čas vypršel!" if player.lives > 0 else "Životy vypršely!", True, RED)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(time_text, time_rect)

        if asking_for_name:
            name_prompt = font.render(f"Zadejte své jméno: {player_name_input}_", True, WHITE)
            name_prompt_rect = name_prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(name_prompt, name_prompt_rect)
        else:
            restart_button_game_over.draw(screen)
            menu_button_game_over.draw(screen)

            esc_text = font.render("ESC pro ukončení", True, GRAY)
            esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 270))
            screen.blit(esc_text, esc_rect)

    def draw_highscores_screen():
        screen.fill(BLACK)
        title_text = font.render("NEJLEPŠÍ VÝSLEDKY", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)

        scores_list = load_highscores()
        if scores_list:
            for i, entry in enumerate(scores_list):
                player_name = entry.get('name', 'Neznámý')
                player_score = entry.get('score', 0)
                score_line = f"{i + 1}. {player_name} - {player_score}"
                score_text = hud_font.render(score_line, True, WHITE)
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 120 + i * 40))
        else:
            no_scores_text = hud_font.render("Zatím nejsou žádné výsledky.", True, GRAY)
            screen.blit(no_scores_text, (SCREEN_WIDTH // 2 - no_scores_text.get_width() // 2, SCREEN_HEIGHT // 2))

        back_text = font.render("Stiskněte 'ESC' pro návrat do menu", True, GRAY)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(back_text, back_rect)

    def draw_paused_screen():  # NOVÁ FUNKCE PRO PAUZU
        # Zatemnění obrazovky - nejprve vykreslíme celou hru (což je uděláno před voláním draw_paused_screen),
        # a pak přes ní nakreslíme průhlednou vrstvu.
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))  # Černá s 128 průhledností (z 255)
        screen.blit(s, (0, 0))

        pause_text = font.render("PAUZA", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(pause_text, pause_rect)

        # Vykreslení tlačítek pauzy
        resume_button_pause.draw(screen)
        restart_game_pause.draw(screen)
        quit_game_pause.draw(screen)

    # ... (Zde budou pokračovat definice funkcí, nebo hlavní herní smyčka) ...
    running = True  # To je jen orientační, že začíná hlavní smyčka

    def initialize_game_level(time_in_seconds,bombs):
        nonlocal player, score, game_timer, start_game_time, finish_time, message, message_timer, player_name_input, asking_for_name, remaining_time_seconds, last_unpaused_time
        all_sprites.empty()
        solid_walls.empty()
        breakable_walls.empty()
        demolition_charges.empty()
        explosions.empty()
        exits.empty()
        collectibles.empty()
        score = 0
        game_timer = time_in_seconds
        message = ""
        message_timer = 0
        finish_time = 0
        player_name_input = ""
        asking_for_name = False
        remaining_time_seconds = game_timer
        pygame.key.set_repeat(0)

        map_width_tiles = SCREEN_WIDTH // TILE_SIZE
        map_height_tiles = (SCREEN_HEIGHT - HUD_HEIGHT) // TILE_SIZE
        game_map_array = generate_map(map_width_tiles, map_height_tiles)
        start_game_time = pygame.time.get_ticks()
        last_unpaused_time = pygame.time.get_ticks()

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

        player = Player(player_start_pos[0], player_start_pos[1],bombs)
        all_sprites.add(player)

        start_game_time = pygame.time.get_ticks()

    # LeveĺScreenSelectWindow
    hardness_selector = HardnessSelect(screen, font, initialize_game_level)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_game_state == GAME_STATE_INTRO:
                pass
            elif current_game_state == GAME_STATE_MENU:
                action = play_button.handle_event(event)
                if action == GAME_STATE_HARDNESS_CHOOSE:
                    current_game_state = action
                    # initialize_game_level()
                    hardness_selector.DrawHardnessScreen()

                action_highscores = highscores_button.handle_event(event)
                if action_highscores == GAME_STATE_HIGHSCORES:
                    current_game_state = action_highscores

                action_quit = quit_button.handle_event(event)
                if action_quit == pygame.QUIT:
                    running = False
            elif current_game_state == GAME_STATE_HARDNESS_CHOOSE:

                easy_game_action = hardness_selector.EasyLevelButton.handle_event(event)
                medium_game_action = hardness_selector.MediumLevelButton.handle_event(event)
                hard_game_action = hardness_selector.HardLevelButton.handle_event(event)


                if easy_game_action == EASY_GAME:
                    current_game_state = GAME_STATE_PLAYING
                    hardness_selector.InitEasyLevel()

                if medium_game_action == MEDIUM_GAME:
                    current_game_state = GAME_STATE_PLAYING
                    hardness_selector.InitMediumLevel()

                if hard_game_action == HARD_GAME:
                    current_game_state = GAME_STATE_PLAYING
                    hardness_selector.InitHardLevel()




            elif current_game_state == GAME_STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_game_state = GAME_STATE_PAUSED
                        last_unpaused_time = pygame.time.get_ticks()
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
                if asking_for_name:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if player_name_input:
                                save_highscores({"name": player_name_input, "score": score})
                                asking_for_name = False
                                player_name_input = ""
                                pygame.key.set_repeat(0)
                        elif event.key == pygame.K_BACKSPACE:
                            player_name_input = player_name_input[:-1]
                        elif event.unicode.isalnum() or event.unicode == " ":
                            if len(player_name_input) < 10:
                                player_name_input += event.unicode
                else:  # Pokud se jméno neptá, umožní restart/ukončení
                    # Obsluha kláves 'R' a 'ESC'
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            current_game_state = GAME_STATE_PLAYING
                            hardness_selector.InitByLastGame()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                    # Obsluha kliku na nová tlačítka
                    action_menu = menu_button_game_over.handle_event(event)
                    if action_menu == GAME_STATE_MENU:
                        current_game_state = action_menu

                    action_restart_button = restart_button_game_over.handle_event(event)
                    if action_restart_button == GAME_STATE_PLAYING:
                        current_game_state = action_restart_button
                        hardness_selector.InitByLastGame()
            elif current_game_state == GAME_STATE_HIGHSCORES:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_game_state = GAME_STATE_MENU
            elif current_game_state == GAME_STATE_PAUSED:  # Obsluha událostí pro PAUZA menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_game_state = GAME_STATE_PLAYING
                        start_game_time += (pygame.time.get_ticks() - last_unpaused_time)
                # Obsluha tlačítek v pauze
                action_resume = resume_button_pause.handle_event(event)
                if action_resume == GAME_STATE_PLAYING:
                    current_game_state = action_resume
                    start_game_time += (pygame.time.get_ticks() - last_unpaused_time)

                action_restart_pause = restart_game_pause.handle_event(event)
                if action_restart_pause == GAME_STATE_PLAYING:
                    current_game_state = action_restart_pause
                    initialize_game_level()  # Inicializuje novou hru

                action_quit_game = quit_game_pause.handle_event(event)
                if action_quit_game == GAME_STATE_MENU:
                    current_game_state = action_quit_game
        # --- Aktualizace herního stavu ---
        if current_game_state == GAME_STATE_INTRO:
            if pygame.time.get_ticks() - intro_start_time > 3000:
                current_game_state = GAME_STATE_MENU
            draw_intro_screen()

        elif current_game_state == GAME_STATE_MENU:
            draw_menu_screen()

        elif current_game_state == GAME_STATE_HARDNESS_CHOOSE:
            hardness_selector.DrawHardnessScreen()

        elif current_game_state == GAME_STATE_PLAYING:
            player.update(solid_walls, breakable_walls)

            elapsed_time_ms = pygame.time.get_ticks() - start_game_time
            remaining_time_seconds = game_timer - (elapsed_time_ms // 1000)
            if remaining_time_seconds < 0:
                remaining_time_seconds = 0

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

            if player.lives <= 0 or remaining_time_seconds <= 0 or pygame.sprite.spritecollideany(player, exits):
                if current_game_state == GAME_STATE_PLAYING:
                    current_game_state = GAME_STATE_GAME_OVER
                    if pygame.sprite.spritecollideany(player,
                                                      exits) and remaining_time_seconds > 0 and player.lives > 0:
                        finish_time = pygame.time.get_ticks()
                        asking_for_name = True
                        pygame.key.set_repeat(500, 50)
                    else:
                        asking_for_name = False
                        pygame.key.set_repeat(0)

            collected_items = pygame.sprite.spritecollide(player, collectibles, True)
            for item in collected_items:
                score += item.value
                message = f"+{item.value} Bodů!"
                message_timer = pygame.time.get_ticks() + 1000

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

        elif current_game_state == GAME_STATE_HIGHSCORES:
            draw_highscores_screen()

        elif current_game_state == GAME_STATE_PAUSED:  # Vykreslení obrazovky pauzy
            draw_paused_screen()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()



if __name__ == "__main__":
    main()
