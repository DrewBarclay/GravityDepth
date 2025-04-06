import pygame
import random
from typing import List, Optional
from objects.game_object import GameObject
from objects.gravity_ball import GravityBall
from sprites.player.character_sprite import CharacterSprite
from objects.portal import Portal
from objects.bat import Bat

class Level:
    """Manages a game level and the objects in it"""

    def __init__(self, engine, level_number: int, world_number: int = 1):
        self.engine = engine
        self.level_number = level_number
        self.world_number = world_number
        self.objects: List[GameObject] = []
        self.player = None
        self.portal = None
        self.enemies: List[GameObject] = []
        self.players: List[GameObject] = []

        # Set up the level
        self.setup_level()

    def setup_level(self):
        """Set up the level with appropriate objects"""
        width, height = self.engine.get_dimensions()

        # Create the player
        self.player = self.create_player(width//2 - 25, height//2 - 25)
        self.players.append(self.player)

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
                    ball = BlueBall(x, y)
                    self.add_object(ball)

                # Add two bats to level 1-1
                # First bat in the upper left area
                bat1 = Bat(
                    random.randint(50, width//3),
                    random.randint(50, height//3)
                )
                self.add_enemy(bat1)

                # Second bat in the upper right area
                bat2 = Bat(
                    random.randint(2*width//3, width - 90),
                    random.randint(50, height//3)
                )
                self.add_enemy(bat2)

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

        # Set screen dimensions for wall detection on all objects
        width, height = self.engine.get_dimensions()
        obj.screen_width = width
        obj.screen_height = height

    def add_enemy(self, enemy: GameObject):
        """Add an enemy to the level and track it in the enemies list"""
        self.enemies.append(enemy)
        self.add_object(enemy)

    def update(self, dt: float):
        """Update level-specific logic"""
        # Update enemy AI
        for enemy in self.enemies:
            if isinstance(enemy, Bat):
                enemy.try_attack(self.players)

        # Check for player-projectile collisions
        for enemy in self.enemies:
            if isinstance(enemy, Bat):
                for projectile in enemy.projectiles[:]:  # Use a copy of the list to safely remove while iterating
                    for player in self.players:
                        if projectile.collides_with(player):
                            # Handle player hit by projectile
                            # For now, just remove the projectile
                            projectile.marked_for_removal = True
                            break

    def clear_level(self):
        """Mark all objects for removal to clear the level"""
        for obj in self.objects:
            obj.marked_for_removal = True
        self.enemies.clear()
        self.players.clear()

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
        self.enemies = []
        self.players = []
        self.setup_level()

class OrangeSquare(GameObject):
    """A simple orange square for level 1-2"""

    def __init__(self, x: float, y: float, size: float = 30):
        super().__init__(x, y, size, size)
        self.color = (255, 165, 0)  # Orange
        self.marked_for_removal = False
        # Initialize screen dimensions (will be set properly when added to level)
        self.screen_width = 800
        self.screen_height = 600

    def update(self, dt: float) -> None:
        """Update square physics with wall bouncing"""
        super().update(dt)
        self.bounce_off_walls(self.screen_width, self.screen_height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the orange square"""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

class BlueBall(GameObject):
    """A simple blue ball for level 1-1"""

    def __init__(self, x: float, y: float, size: float = 30):
        super().__init__(x, y, size, size)
        self.color = (0, 0, 255)  # Blue
        self.marked_for_removal = False
        # Initialize screen dimensions (will be set properly when added to level)
        self.screen_width = 800
        self.screen_height = 600

    def update(self, dt: float) -> None:
        """Update ball physics with wall bouncing"""
        super().update(dt)
        self.bounce_off_walls(self.screen_width, self.screen_height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the blue ball"""
        pygame.draw.circle(surface, self.color,
                          (int(self.x + self.width/2), int(self.y + self.height/2)),
                          int(self.width/2))