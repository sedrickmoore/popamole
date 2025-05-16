import pygame
import random
import sqlite3
import re
import os

# Constants
PLAYER_RADIUS = 30
PLAYER_SPEED = 1000
PLAYER_COLLISION = 2000
PROJECTILE_SPEED = 750
MOLE_SIZE = 40
MOLE_LIFETIME = 2000
MOLE_SHRINK_INTERVAL = 3000
GAME_DURATION = 30

# Database setup
def init_db():
    """
    Connects to or creates the database and creates the 'scores' table if it doesn't exist.
    Returns the database connection object.
    """
    conn = sqlite3.connect("scores.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            nickname TEXT PRIMARY KEY,
            high_score INTEGER
        )
    ''')
    conn.commit()
    return conn

# Save player's new highest score
def save_score(conn, nickname, score):
    """
    Inserts a new score into the table for the player (identified by their nickname).
    If the nickname already exists, updates the score only if the new score is higher than the saved score.
    """
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO scores (nickname, high_score)
        VALUES (?, ?)
        ON CONFLICT(nickname) DO UPDATE SET high_score = 
        CASE WHEN excluded.high_score > scores.high_score THEN excluded.high_score ELSE scores.high_score END
    ''', (nickname, score))
    conn.commit()

# Retrieve the top player scores (default limit to 5)
def get_leaderboard(conn, limit=5):
    """
    Returns a list of tuples (nickname, high_score) sorted by the highest score.
    Limits results to a specified number (default is 5).
    """
    cur = conn.cursor()
    cur.execute('''
        SELECT nickname, MAX(high_score) as score
        FROM scores
        GROUP BY nickname
        ORDER BY score DESC
        LIMIT ?
    ''', (limit,))
    return cur.fetchall()

# Ask the player to enter a valid nickname using regex
def get_nickname(screen, font):
    """
    Asks the player to enter a nickname (3–12 characters).
    Accepts only letters, digits, and underscores using regex validation.
    Returns the nickname when Enter is pressed and input is valid.
    """
    nickname = ""
    input_active = True
    pattern = re.compile(r"^[A-Za-z0-9_]{3,12}$")

    while input_active:
        screen.fill("forestgreen")
        prompt = font.render("Enter your nickname:", True, (255, 255, 255))
        input_display = font.render(nickname, True, (0, 255, 0))
        screen.blit(prompt, (screen.get_width() // 2 - prompt.get_width() // 2, 200))
        screen.blit(input_display, (screen.get_width() // 2 - input_display.get_width() // 2, 300))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and pattern.fullmatch(nickname):
                    return nickname
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif len(nickname) < 12 and event.unicode.isprintable():
                    nickname += event.unicode

# Display the top players' scores on the screen
def show_leaderboard(screen, font, leaderboard):
    title = font.render("Top Scores", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))
    for i, (name, score) in enumerate(leaderboard):
        line = font.render(f"{i+1}. {name}: {score}", True, (255, 255, 255))
        screen.blit(line, (screen.get_width() // 2 - line.get_width() // 2, 150 + i * 50))
    pygame.display.update()
    pygame.time.delay(4000)

# Load and return font, images, and sound effects
def init_assets():
    font = pygame.font.Font(None, 48)
    projectile_image = pygame.image.load(os.path.join("Media", "water-squirt.png")).convert_alpha()
    projectile_image = pygame.transform.scale(projectile_image,(MOLE_SIZE * 1.5,MOLE_SIZE * 1.5))
    mole_image = pygame.image.load(os.path.join("Media", "mole.png")).convert_alpha()
    mole_image = pygame.transform.scale(mole_image, (MOLE_SIZE * 2, MOLE_SIZE * 2))
    projectile_sound = pygame.mixer.Sound(os.path.join("Media", "PopAMole-WaterShot.mp3"))
    mole_hit = pygame.mixer.Sound(os.path.join("Media", "PopAMole-MoleHit.mp3"))
    return font, projectile_image, mole_image, projectile_sound, mole_hit

# Handle game events: quitting, setting start time, spawning moles, and adjusting spawn delay
def handle_events(start_time, moles, mole_spawn_delay, mole_min_delay, screen):
    """
    Processes game events during the game loop:
    - Quits the game if the window is closed or Escape is pressed
    - Starts the game timer on first mole spawn (so the user has the full timer)
    - Spawns moles at random positions
    - Gradually increases difficulty by decreasing spawn delay over time

    Returns:
    - continue_game (bool): False if quit triggered
    - start_time (int or None): Updated game start time
    - mole_spawn_delay (int): Updated delay for mole spawning
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, start_time, mole_spawn_delay
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False, start_time, mole_spawn_delay
        elif event.type == pygame.USEREVENT:
            now = pygame.time.get_ticks()
            if start_time is None:
                start_time = now
            mole_x = random.randint(MOLE_SIZE, screen.get_width() - MOLE_SIZE)
            mole_y = random.randint(MOLE_SIZE, int(screen.get_height() / 3))
            mole_pos = pygame.Vector2(mole_x, mole_y)
            moles.append({"pos": mole_pos, "spawn": now})
        elif event.type == pygame.USEREVENT + 1:
            if mole_spawn_delay > mole_min_delay:
                mole_spawn_delay = max(mole_min_delay, mole_spawn_delay - 200)
                pygame.time.set_timer(pygame.USEREVENT, mole_spawn_delay)
    return True, start_time, mole_spawn_delay

# Handle collisions between projectiles and moles, update score and bonus time
def check_collisions(projectiles, moles, mole_hit, dt, score):
    """
    Checks for collisions between projectiles and moles.

    - If a projectile hits a mole:
        - Removes the mole and the projectile
        - Plays a sound effect
        - Increases score by 1
        - Adds bonus time:
            - +5 seconds if new score is divisible by 10
            - +2 seconds if divisible by 5 (but not 10)
            - +1 second otherwise

    - Also removes projectiles that go off-screen

    Returns score increase and bonus time increase
    """
    score_increase = 0
    bonus_time_increase = 0
    for projectile in projectiles[:]:
        projectile["pos"].y -= PROJECTILE_SPEED * dt
        if projectile["pos"].y < 0:
            projectiles.remove(projectile)
        for mole in moles[:]:
            if projectile["pos"].distance_to(mole["pos"]) < MOLE_SIZE:
                moles.remove(mole)
                mole_hit.play()
                projectiles.remove(projectile)
                score_increase += 1
                if (score + score_increase) % 10 == 0:
                    bonus_time_increase += 5
                elif (score + score_increase) % 5 == 0:
                    bonus_time_increase += 2
                else:
                    bonus_time_increase += 1
                break
    return score_increase, bonus_time_increase

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

if __name__ == "__main__":
    play_pop_a_mole()