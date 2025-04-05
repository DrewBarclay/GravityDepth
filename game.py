import pygame
from game_engine import GameEngine
from game_object import GameObject

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
        pygame.draw.rect(surface, self.color, self.get_rect())

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
