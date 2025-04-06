from pygame.math import Vector2

# RainDrop constants
DEFAULT_VELOCITY_Y = 200.0
GRAVITY_ACCELERATION = Vector2(0, 128000.0)
MAX_VELOCITY_MAGNITUDE = 400.0
MAX_UPWARD_VELOCITY = 200.0
DEFAULT_WIDTH = 2
MIN_LENGTH = 4
MAX_LENGTH = 7
DEFAULT_COLOR = (255, 0, 0)
# Repulsion should be at least as strong as gravity
REPULSION_FORCE = 100
# Damping factor applied to velocity during collision
RAIN_COLLISION_FRICTION = 200
# Multiplier for increasing repulsion based on depth inside object
DEPTH_REPULSION_MULTIPLIER = 10.0
# Friction coefficient for air
RAIN_AIR_FRICTION = 1.5