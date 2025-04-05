import pygame
import random
from typing import List, Optional
from objects.game_object import GameObject
from objects.gravity_ball import GravityBall
from sprites.player.character_sprite import CharacterSprite
from objects.portal import Portal

class Level:
    """Manages a game level and the objects in it"""

    def __init__(self, engine, level_number: int, world_number: int = 1):
        self.engine = engine
        self.level_number = level_number
        self.world_number = world_number
        self.objects: List[GameObject] = []
        self.player = None
        self.portal = None

        # Set up the level
        self.setup_level()

    def setup_level(self):
        """Set up the level with appropriate objects"""
        width, height = self.engine.get_dimensions()

        # Create the player
        self.player = self.create_player(width//2 - 25, height//2 - 25)

        # Create portal at the bottom middle of the screen
        self.portal = Portal(width//2 - 25, height - 80)
        self.add_object(self.portal)

        # Create level-specific objects
        if self.world_number == 1:
            if self.level_number == 1:
                # Level 1-1: Three blue balls spread randomly
                for _ in range(3):
                    x = random.randint(50, width - 50)
                    y = random.randint(50, height - 150)  # Keep some distance from portal
                    ball = GravityBall(x, y, radius=15, attraction_radius=0, lifespan=float('inf'))
                    ball.color = (0, 0, 255)  # Blue
                    self.add_object(ball)
            elif self.level_number == 2:
                # Level 1-2: Two orange squares spread randomly
                for _ in range(2):
                    x = random.randint(50, width - 50)
                    y = random.randint(50, height - 150)
                    square = OrangeSquare(x, y)
                    self.add_object(square)
            # Level 3+ are empty except for player and portal

    def create_player(self, x: float, y: float):
        """Create and initialize the player character"""
        from game import Player  # Import here to avoid circular imports
        player = Player(x, y)

        # Set screen dimensions for wall detection
        width, height = self.engine.get_dimensions()
        player.screen_width = width
        player.screen_height = height

        self.add_object(player)
        return player

    def add_object(self, obj: GameObject):
        """Add a game object to the level and the engine"""
        self.objects.append(obj)
        self.engine.add_object(obj)

    def clear_level(self):
        """Mark all objects for removal to clear the level"""
        for obj in self.objects:
            obj.marked_for_removal = True

    def next_level(self):
        """Transition to the next level"""
        self.clear_level()

        # Increment level number and possibly world number
        self.level_number += 1
        if self.level_number > 3:
            self.level_number = 1
            self.world_number += 1

        # Setup the new level
        self.objects = []
        self.setup_level()

class OrangeSquare(GameObject):
    """A simple orange square for level 1-2"""

    def __init__(self, x: float, y: float, size: float = 30):
        super().__init__(x, y, size, size)
        self.color = (255, 165, 0)  # Orange
        self.marked_for_removal = False

    def update(self, dt: float) -> None:
        """Update square physics"""
        super().update(dt)

        # Apply gravity
        self.apply_force(pygame.math.Vector2(0, 200))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the orange square"""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))