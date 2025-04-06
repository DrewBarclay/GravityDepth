"""
Game constants module that defines various constants used throughout the game.
This allows for easy tweaking of game parameters in one central location.
"""

# Bat enemy constants
BAT_PROJECTILE_LIFESPAN = 30.0  # seconds
BAT_ATTACK_COOLDOWN_MIN = 1.5   # seconds
BAT_ATTACK_COOLDOWN_MAX = 3.0   # seconds
BAT_ATTACK_SPEED = 150          # pixels per second
BAT_MOVEMENT_SPEED = 100        # pixels per second
BAT_HOVER_AMPLITUDE = 20        # pixels
BAT_HOVER_FREQUENCY = 2         # oscillations per second
BAT_PROJECTILE_IMMUNE_TIME = 0.2  # seconds

# Player constants
PLAYER_SPEED = 200              # pixels per second

# Projectile constants
DEFAULT_PROJECTILE_LIFESPAN = 3.0  # seconds
