from pygame.math import Vector2

# RainDrop constants
DEFAULT_VELOCITY_Y = 200.0
GRAVITY_ACCELERATION = Vector2(0, 8000.0)
MAX_VELOCITY_MAGNITUDE = 400.0
MAX_UPWARD_VELOCITY = 200.0
DEFAULT_WIDTH = 1
MIN_LENGTH = 2
MAX_LENGTH = 5
DEFAULT_COLOR = (255, 0, 0)
# Repulsion should be at least as strong as gravity
REPULSION_FORCE = 100
# Damping factor applied to velocity during collision
RAIN_COLLISION_FRICTION = 10
# Multiplier for increasing repulsion based on depth inside object
DEPTH_REPULSION_MULTIPLIER = 2.0
# Friction coefficient for air
RAIN_AIR_FRICTION = 0.01