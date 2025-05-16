import pygame
import random
from src.constants import MOLE_SIZE, PROJECTILE_SPEED

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
