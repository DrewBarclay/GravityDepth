"""
Game constants module that defines various constants used throughout the game.
This allows for easy tweaking of game parameters in one central location.
"""

# Bat enemy constants
BAT_PROJECTILE_LIFESPAN = 30.0  # seconds
BAT_ATTACK_COOLDOWN_MIN = 1.5   # seconds
BAT_ATTACK_COOLDOWN_MAX = 3.0   # seconds
BAT_ATTACK_SPEED = 187          # pixels per second (increased by 25% from 150)
BAT_MOVEMENT_SPEED = 100        # pixels per second
BAT_HOVER_AMPLITUDE = 20        # pixels
BAT_HOVER_FREQUENCY = 2         # oscillations per second
BAT_PROJECTILE_IMMUNE_TIME = 1.2  # seconds (increased from 0.2 for extra immunity)

# Player constants
PLAYER_SPEED = 200              # pixels per second
PLAYER_MAX_HEALTH = 3           # player's starting/maximum health
PLAYER_INVULNERABILITY_TIME = 1.0  # seconds of invulnerability after being hit
PLAYER_FLASH_INTERVAL = 0.15    # seconds between visibility toggles when hit

# Projectile constants
DEFAULT_PROJECTILE_LIFESPAN = 3.0  # seconds
