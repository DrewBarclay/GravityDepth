import pygame
from game_engine import GameEngine
from game_object import GameObject
from character_sprite import CharacterSprite

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

class Player(GameObject):
    """Player class extending the base GameObject"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 50, 50)  # Fixed size for now
        self.movement_speed = 300  # pixels per second
        self.set_property('type', 'player')  # For custom rendering
        self.marked_for_removal = False  # Add marked_for_removal attribute
        self.color = (0, 0, 255)  # Blue color for the player
        self.character_sprite = CharacterSprite(width=50, height=50)

        # Use the character sprite's collision polygon
        self.set_collision_polygon(self.character_sprite.collision_polygon)

        # Debug mode for showing collision polygon
        self.debug_mode = False
        self._last_d_state = False  # Store last state of D key

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

        # Toggle debug mode with 'D' key
        if keys[pygame.K_d] and not self._last_d_state:
            self.debug_mode = not self.debug_mode
        self._last_d_state = keys[pygame.K_d]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player on the screen"""
        self.character_sprite.render(surface, (self.x, self.y))

        # Draw collision polygon in debug mode
        if self.debug_mode:
            # Draw using the real collision points (which include position offset)
            points = self.collision_polygon
            pygame.draw.polygon(surface, (255, 0, 0), points, 1)

def main():
    print("Starting game")
    # Create game engine
    engine = GameEngine(800, 600, "Arrow Key Movement Demo")
    print("Game engine created")

    # Create player at center of screen
    width, height = engine.get_dimensions()
    print(f"Screen dimensions: {width}x{height}")
    player = Player(width//2 - 25, height//2 - 25)
    print("Player created")
    engine.add_object(player)
    print("Player added to engine")

    # Start the game engine
    print("Starting game engine")
    engine.run()
    print("Game engine finished")

if __name__ == "__main__":
    main()
