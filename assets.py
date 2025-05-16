import os
import pygame
from constants import MOLE_SIZE


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
