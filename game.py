import pygame
import os
from constants import *
from db import init_db, get_nickname, save_score, get_leaderboard
from assets import init_assets
from ui import draw_game, display_controls, show_leaderboard
from events import handle_events, check_collisions

# Main game function containing initialization, the game loop, and end of game logic
def play_pop_a_mole():
    """
    - Initializes Pygame, screen, clock, and background music
    - Connects to the database and retrieves the player's nickname
    - Displays control instructions on first run
    - Runs the main game loop:
        - Handles events and player input
        - Spawns and updates moles and projectiles
        - Since mole spawn to music gradually
        - Detects collisions and updates score and bonus time
        - Changes player color based on movement or boundary collisions
        - Draws all game elements each frame
        - Ends the game when time runs out
    - After game ends:
        - Displays final score and leaderboard
        - Allows the player to replay or quit
    """
    pygame.init()
    screen = pygame.display.set_mode((1280,720), pygame.FULLSCREEN)
    pygame.display.set_caption("Pop-A-Mole")
    game_clock = pygame.time.Clock()

    SONGS = {
        "PopAMole.mp3": 123
    }
    song_file = "PopAMole.mp3"
    bpm = SONGS[song_file]

    pygame.mixer.music.load(os.path.join("Media", song_file))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    font, _, _, _, _ = init_assets()

    first_run = True
    replay = True

    conn = init_db()
    nickname = get_nickname(screen, font)

    while replay:
        if first_run:
            font, _, _, _, _ = init_assets()
            display_controls(screen, font)
            first_run = False

        dt = 0
        running = True

        font, projectile_image, mole_image, projectile_sound, mole_hit = init_assets()

        score = 0
        start_time = None
        bonus_time = 0
        last_shot_time = 0
        cooldown = 300

        player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 1.15)
        player_moving = False

        projectiles = []
        moles = []

        mole_spawn_delay = 2000
        mole_min_delay = int(60_000 / bpm)

        pygame.time.set_timer(pygame.USEREVENT, mole_spawn_delay)
        pygame.time.set_timer(pygame.USEREVENT + 1, MOLE_SHRINK_INTERVAL)

        while running:
            running, start_time, mole_spawn_delay = handle_events(
                start_time, moles, mole_spawn_delay, mole_min_delay, screen
            )

            now = pygame.time.get_ticks()
            moles[:] = [m for m in moles if now - m["spawn"] <= MOLE_LIFETIME]

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                if player_pos.x > PLAYER_RADIUS:
                    player_pos.x -= PLAYER_SPEED * dt
                    player_moving = True
                else:
                    player_pos.x += PLAYER_COLLISION * dt
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                if player_pos.x < screen.get_width() - PLAYER_RADIUS:
                    player_pos.x += PLAYER_SPEED * dt
                    player_moving = True
                else:
                    player_pos.x -= PLAYER_COLLISION * dt
            else:
                player_moving = False

            if keys[pygame.K_e] or keys[pygame.K_UP] or keys[pygame.K_SPACE]:
                if now - last_shot_time >= cooldown:
                    projectile = {"pos": pygame.Vector2(player_pos.x, player_pos.y)}
                    projectiles.append(projectile)
                    projectile_sound.play()
                    last_shot_time = now

            score_delta, bonus_delta = check_collisions(projectiles, moles, mole_hit, dt, score)
            score += score_delta
            bonus_time += bonus_delta

            if player_pos.x >= screen.get_width() - PLAYER_RADIUS or player_pos.x <= PLAYER_RADIUS:
                player_color = "red"
            elif player_moving:
                player_color = "green"
            else:
                player_color = "cyan"

            if start_time is not None:
                elapsed = (pygame.time.get_ticks() - start_time) // 1000
                time_left = max(0, GAME_DURATION + bonus_time - elapsed)
                if time_left <= 0:
                    running = False
            else:
                time_left = GAME_DURATION

            draw_game(screen, mole_image, projectile_image, moles, projectiles,
                      player_pos, player_color, font, score, start_time, time_left)

            dt = game_clock.tick(60) / 1000

        final_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        prompt_text = font.render("Press R to play again or ESC to quit", True, (255, 255, 255))
        screen.blit(final_text, (screen.get_width() // 2 - final_text.get_width() // 2,
                                 screen.get_height() // 2 - final_text.get_height() // 2 - 20))
        screen.blit(prompt_text, (screen.get_width() // 2 - prompt_text.get_width() // 2,
                                  screen.get_height() // 2 + 20))
        pygame.display.update()

        save_score(conn, nickname, score)
        leaderboard = get_leaderboard(conn)
        show_leaderboard(screen, font, leaderboard)

        waiting = True
        replay = False
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif event.key == pygame.K_r:
                        replay = True
                        waiting = False

