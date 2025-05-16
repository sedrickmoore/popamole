import pygame
from constants import PLAYER_RADIUS

# Display the top players' scores on the screen
def show_leaderboard(screen, font, leaderboard):
    title = font.render("Top Scores", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))
    for i, (name, score) in enumerate(leaderboard):
        line = font.render(f"{i+1}. {name}: {score}", True, (255, 255, 255))
        screen.blit(line, (screen.get_width() // 2 - line.get_width() // 2, 150 + i * 50))
    pygame.display.update()
    pygame.time.delay(4000)

# Draw all game elements: background, moles, player, projectiles, and UI
def draw_game(screen, mole_image, projectile_image, moles, projectiles, player_pos, player_color, font, score, start_time, time_left):
    """
    Renders all visible elements of the game:
    - Forest green background
    - Active moles
    - Player avatar (a circle)
    - Projectiles
    - Score and timer (if game has started)
    """
    screen.fill("forestgreen")
    for mole_pos in moles:
        mole_rect = mole_image.get_rect(center=mole_pos["pos"])
        screen.blit(mole_image, mole_rect)
    pygame.draw.circle(screen, player_color, player_pos, PLAYER_RADIUS)
    for projectile in projectiles:
        rect = projectile_image.get_rect(center=projectile["pos"])
        screen.blit(projectile_image, rect)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    if start_time is not None and time_left > 0:
        time_text = font.render(f"Time: {time_left}s", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        screen.blit(time_text, (20, 70))
    pygame.display.update()

# Display a list of controls
def display_controls(screen, font):
    """
    Displays the control instructions on screen and waits for the player to press ENTER to start.
    Allows quitting with ESC or window close.
    """
    screen.fill("forestgreen")
    title = font.render("Pop-A-Mole", True, (255, 255, 255))
    controls = [
        "Controls:",
        "Move Left: A or Left Arrow",
        "Move Right: D or Right Arrow",
        "Shoot: E, Up Arrow, or Space",
        "Quit: ESC",
        " ",
        "Press ENTER to Start"
    ]
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
    for i, line in enumerate(controls):
        rendered = font.render(line, True, (255, 255, 255))
        screen.blit(rendered, (screen.get_width() // 2 - rendered.get_width() // 2, 200 + i * 50))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
