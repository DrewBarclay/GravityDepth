import pygame
from engine.game_engine import GameEngine
from objects.game_object import GameObject
from sprites.player.character_sprite import CharacterSprite
from utils.advanced_polygon_utils import draw_polygon
from objects.level import Level, set_player_class
from config.game_constants import PLAYER_MAX_HEALTH, PLAYER_INVULNERABILITY_TIME, PLAYER_FLASH_INTERVAL

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SPRITE_SIZE = 40
MOVEMENT_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (200, 100, 255)

class Player(GameObject):
    """Player class extending the base GameObject"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 50, 50)  # Fixed size for now
        self.movement_speed = 300  # pixels per second
        self.set_property('type', 'player')  # For custom rendering
        self.marked_for_removal = False  # Add marked_for_removal attribute
        self.color = (0, 0, 255)  # Blue color for the player
        self.character_sprite = CharacterSprite(width=50, height=50)

        # Health properties
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.is_invulnerable = False
        self.invulnerability_time = PLAYER_INVULNERABILITY_TIME
        self.invulnerability_timer = 0
        self.flash_interval = PLAYER_FLASH_INTERVAL
        self.flash_timer = 0
        self.visible = True  # used for flashing effect

        # Use the character sprite's collision polygon
        self.set_collision_polygon(self.character_sprite.collision_polygon)

        # Debug mode for showing collision polygon
        self.debug_mode = False
        self._last_d_state = False  # Store last state of D key

        # Store screen dimensions for wall detection
        self.screen_width = WINDOW_WIDTH
        self.screen_height = WINDOW_HEIGHT

    def take_damage(self):
        """Reduce player health when hit by a projectile"""
        if not self.is_invulnerable:
            self.health -= 1
            self.is_invulnerable = True
            self.invulnerability_timer = self.invulnerability_time
            self.flash_timer = 0
            self.visible = False

            if self.health <= 0:
                # Player is out of health
                self.marked_for_removal = True

    def update(self, dt: float) -> None:
        """Update player physics and handle wall bouncing"""
        # Call the parent class update method to update position
        super().update(dt)

        # Update invulnerability timer
        if self.is_invulnerable:
            self.invulnerability_timer -= dt

            # Update flash timer
            self.flash_timer += dt
            if self.flash_timer >= self.flash_interval:
                self.flash_timer = 0
                self.visible = not self.visible

            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                self.visible = True

        # Use the bounce_off_walls method for wall collisions
        self.bounce_off_walls(self.screen_width, self.screen_height)

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle player input"""
        # Reset acceleration
        self.acceleration = pygame.math.Vector2(0, 0)

        # Apply forces based on input
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -self.movement_speed
        if keys[pygame.K_RIGHT]:
            self.acceleration.x = self.movement_speed
        if keys[pygame.K_UP]:
            self.acceleration.y = -self.movement_speed
        if keys[pygame.K_DOWN]:
            self.acceleration.y = self.movement_speed

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player on the screen"""
        # Skip drawing if invisible during invulnerability flashing
        if not self.visible:
            return

        # Draw the character with debug_mode parameter
        self.character_sprite.render(surface, (self.x, self.y), self.debug_mode)

        # Draw collision polygons in debug mode
        if self.debug_mode:
            # Get debug polygons in world coordinates
            debug_polygons = self.character_sprite.get_debug_polygons((self.x, self.y))

            # Create a semi-transparent surface for fills
            s = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

            # Draw body polygon (blue)
            draw_polygon(s, debug_polygons['body'], (0, 0, 255, 40), 0)  # Fill with transparent blue
            draw_polygon(surface, debug_polygons['body'], BLUE, 2)  # Blue outline

            # Draw hood polygon (purple)
            draw_polygon(s, debug_polygons['hood'], (200, 0, 255, 40), 0)  # Fill with transparent purple
            draw_polygon(surface, debug_polygons['hood'], PURPLE, 2)  # Purple outline

            # Draw combined polygon (yellow)
            draw_polygon(s, debug_polygons['combined'], (255, 255, 0, 40), 0)  # Fill with transparent yellow
            draw_polygon(surface, debug_polygons['combined'], YELLOW, 2)  # Yellow outline

            # Add the transparent fills to the main surface
            surface.blit(s, (0, 0))

            # Draw points at each vertex of the combined polygon
            for point in debug_polygons['combined']:
                pygame.draw.circle(surface, GREEN, (int(point[0]), int(point[1])), 3)  # Green dots

def main():
    print("Starting game")
    # Create game engine
    engine = GameEngine(800, 600, "Level-Based Game")
    print("Game engine created")

    # Register the Player class with the level module to avoid circular imports
    set_player_class(Player)

    # Create the first level (1-1)
    level = Level(engine, 1, 1)
    engine.current_level = level
    print("Level 1-1 created")

    # Start the game engine
    print("Starting game engine")
    engine.run()
    print("Game engine finished")

if __name__ == "__main__":
    main()
