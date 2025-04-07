import pygame
import random
import math
from typing import List, Optional
from objects.game_object import GameObject
from objects.gravity_ball import GravityBall
from sprites.player.character_sprite import CharacterSprite
from objects.portal import Portal
from objects.bat import Bat
from objects.projectile import Projectile

# Add Player class reference to fix circular import
_PlayerClass = None

def set_player_class(player_class):
    """Set the Player class from outside to avoid circular imports"""
    global _PlayerClass
    _PlayerClass = player_class

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
        self.projectiles: List[Projectile] = []  # Track all projectiles separately for easier collision handling
        self.initial_enemy_count = 0  # Track initial number of enemies for progress calculation

        # Visual effects for projectile destruction
        self.destruction_flashes = []  # List of [x, y, radius, lifetime]

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

        # Add bats based on level number (1 on level 1, 2 on level 2, 3 on level 3+)
        num_bats = min(self.level_number, 3)  # Cap at 3 bats
        for i in range(num_bats):
            # Determine bat position: spread them around the top of the screen
            bat_x = width // (num_bats + 1) * (i + 1) - 20
            bat_y = random.randint(50, height // 3)

            bat = Bat(bat_x, bat_y)
            self.add_enemy(bat)

        # Add one circle or square to each level
        # The shape starts with momentum from level 2-1 onwards
        # Momentum increases with each new level (3-1, 4-1, etc.)
        if random.choice([True, False]):
            # Add circle
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 150)  # Keep some distance from portal
            ball = Circle(x, y)

            # Add momentum if world number > 1 or (world number = 2 and level number >= 1)
            if self.world_number > 2 or (self.world_number == 2 and self.level_number >= 1):
                # Base speed increases with world number
                base_speed = 50 + (self.world_number - 2) * 25
                angle = random.uniform(0, 2 * math.pi)
                ball.velocity = pygame.math.Vector2(
                    math.cos(angle) * base_speed,
                    math.sin(angle) * base_speed
                )

            self.add_object(ball)
        else:
            # Add square
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 150)
            square = Square(x, y)

            # Add momentum if world number > 1 or (world number = 2 and level number >= 1)
            if self.world_number > 2 or (self.world_number == 2 and self.level_number >= 1):
                # Base speed increases with world number
                base_speed = 50 + (self.world_number - 2) * 25
                angle = random.uniform(0, 2 * math.pi)
                square.velocity = pygame.math.Vector2(
                    math.cos(angle) * base_speed,
                    math.sin(angle) * base_speed
                )

            self.add_object(square)

        # Store initial enemy count for progress calculation
        self.initial_enemy_count = len(self.enemies)
        # Initial portal update based on enemies
        self.update_portal_state()

    def create_player(self, x: float, y: float):
        """Create and initialize the player character"""
        # Use the globally set Player class instead of importing
        if _PlayerClass is None:
            raise RuntimeError("Player class not set. Call set_player_class() first.")

        player = _PlayerClass(x, y)

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

    def collect_all_projectiles(self) -> List[Projectile]:
        """Gather all projectiles from all bats for collision detection"""
        all_projectiles = []
        for enemy in self.enemies:
            if isinstance(enemy, Bat):
                all_projectiles.extend(enemy.projectiles)
        return all_projectiles

    def update_portal_state(self):
        """Update portal state based on remaining enemies"""
        if not self.portal:
            return

        if len(self.enemies) == 0 and self.initial_enemy_count > 0:
            # All enemies are dead
            self.portal.enable()
        elif self.initial_enemy_count > 0:
            # Some enemies still alive, calculate progress
            progress = 1.0 - (len(self.enemies) / self.initial_enemy_count)
            self.portal.progress_color(progress)

    def update(self, dt: float):
        """Update level-specific logic"""
        # First, update enemy AI
        for enemy in self.enemies:
            if isinstance(enemy, Bat):
                enemy.try_attack(self.players)

        # Collect all projectiles for collision detection
        all_projectiles = self.collect_all_projectiles()

        # Check for projectile-bat collisions
        for enemy in self.enemies:
            if isinstance(enemy, Bat):
                for projectile in all_projectiles:
                    # Skip if bat has projectile immunity
                    if enemy.projectile_immunity_timer > 0:
                        continue

                    # Simplified logic: Allow bats to be hit by any projectile
                    # The immunity timer is enough to protect bats from their own recently fired projectiles
                    if enemy.collides_with(projectile):
                        # Mark projectile for removal
                        projectile.marked_for_removal = True
                        # Mark bat for removal
                        enemy.marked_for_removal = True
                        # Play enemy hit sound
                        self.engine.audio_system.play_enemy_hit_sound()

                # We don't need to call check_projectile_collisions anymore as we're handling it above

        # Check for player-projectile collisions
        for player in self.players:
            for projectile in all_projectiles:
                if projectile.collides_with(player):
                    # Play player hit sound
                    self.engine.audio_system.play_player_hit_sound()

                    # Call player's take_damage method when hit by projectile
                    if hasattr(player, 'take_damage'):
                        player.take_damage()

                    # Remove the projectile
                    projectile.marked_for_removal = True

        # Check for environmental object collisions with players and enemies
        for obj in self.objects:
            # Skip non-environmental objects or Portal objects
            if not (isinstance(obj, Circle) or isinstance(obj, Square)) or isinstance(obj, Portal):
                continue

            # Check collisions with players
            for player in self.players:
                if obj.collides_with(player):
                    # Play player hit sound
                    self.engine.audio_system.play_player_hit_sound()

                    # Bounce the environmental object off the player
                    obj.bounce_off_object(player)

                    # Damage the player
                    if hasattr(player, 'take_damage'):
                        player.take_damage()

            # Check collisions with enemies
            for enemy in self.enemies:
                if obj.collides_with(enemy):
                    # Play enemy hit sound
                    self.engine.audio_system.play_enemy_hit_sound()

                    # Bounce the environmental object off the enemy
                    obj.bounce_off_object(enemy)

                    # Mark the enemy for removal (kill them)
                    enemy.marked_for_removal = True

            # Check collisions with projectiles
            for projectile in all_projectiles:
                if obj.collides_with(projectile):
                    # Play environment collision sound (now louder)
                    self.engine.audio_system.play_env_collision_sound()

                    # Add a visual flash effect at the projectile's position
                    projectile_center_x = projectile.x + projectile.radius
                    projectile_center_y = projectile.y + projectile.radius
                    self.destruction_flashes.append([
                        projectile_center_x,
                        projectile_center_y,
                        projectile.radius * 2,  # Initial radius of flash
                        0.2  # Lifetime in seconds
                    ])

                    # Mark the projectile for removal
                    projectile.marked_for_removal = True

            # Check collisions with other environmental objects
            for other_obj in self.objects:
                # Skip non-environmental objects, Portal objects, and self
                if (not (isinstance(other_obj, Circle) or isinstance(other_obj, Square))
                        or isinstance(other_obj, Portal) or other_obj is obj):
                    continue

                if obj.collides_with(other_obj):
                    # Play environment collision sound (quiet)
                    self.engine.audio_system.play_env_collision_sound()

                    # Bounce objects off each other
                    obj.bounce_off_object(other_obj)

        # Update destruction flash effects
        for flash in self.destruction_flashes[:]:
            flash[3] -= dt  # Decrease lifetime
            if flash[3] <= 0:
                self.destruction_flashes.remove(flash)

        # Store enemy count before removal
        prev_enemy_count = len(self.enemies)

        # Remove any bats that have been marked for removal
        self.enemies = [enemy for enemy in self.enemies if not enemy.marked_for_removal]

        # Update portal state if enemy count changed
        if prev_enemy_count != len(self.enemies):
            self.update_portal_state()

    def clear_level(self):
        """Mark all objects for removal to clear the level"""
        # Mark all objects for removal except the player
        for obj in self.objects:
            if obj != self.player:  # Don't mark the player for removal during level transition
                obj.marked_for_removal = True

        # Clear enemies list but don't clear players list
        self.enemies.clear()

    def next_level(self):
        """Transition to the next level"""
        # Clear the level without removing player from players list
        self.clear_level()

        # Increment level number and possibly world number
        self.level_number += 1
        if self.level_number > 3:
            self.level_number = 1
            self.world_number += 1

        # Get reference to current player to remove it from engine
        old_player = self.player
        if old_player:
            self.engine.remove_object(old_player)

        # Setup the new level with empty lists
        self.objects = []
        self.enemies = []
        self.players = []
        self.player = None  # Clear player reference so a new one will be created

        # Set up the new level (which will add player, portal, and level objects)
        self.setup_level()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw level-specific visual effects"""
        # Draw destruction flashes
        for flash in self.destruction_flashes:
            x, y, radius, lifetime = flash

            # Calculate alpha based on remaining lifetime (fade out)
            alpha = int(255 * (lifetime / 0.2))

            # Create a semi-transparent surface for the flash
            flash_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

            # White-blue flash color with fading alpha
            flash_color = (200, 230, 255, alpha)

            # Draw the flash
            pygame.draw.circle(flash_surf, flash_color, (radius, radius), radius)

            # Blit to the main surface
            surface.blit(flash_surf, (x - radius, y - radius))

class Square(GameObject):
    """A simple square shape for gameplay"""

    def __init__(self, x: float, y: float, size: float = 37.5):  # 25% larger (30 * 1.25 = 37.5)
        super().__init__(x, y, size, size)
        self.color = (0, 0, 0)  # Black
        self.marked_for_removal = False
        # Initialize screen dimensions (will be set properly when added to level)
        self.screen_width = 800
        self.screen_height = 600
        self.damage = 1  # Amount of damage to deal when colliding
        self.debug_mode = False  # Add debug mode flag

    def update(self, dt: float) -> None:
        """Update square physics with wall bouncing"""
        super().update(dt)
        self.bounce_off_walls(self.screen_width, self.screen_height)

    def bounce_off_object(self, other: GameObject) -> None:
        """Bounce off another object"""
        # Calculate center points
        self_center = pygame.math.Vector2(self.x + self.width/2, self.y + self.height/2)
        other_center = pygame.math.Vector2(other.x + other.width/2, other.y + other.height/2)

        # Calculate bounce direction
        direction = self_center - other_center
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            # If centers are at the same position, use a random direction
            angle = random.uniform(0, 2 * math.pi)
            direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))

        # Set velocity in the direction away from the collision
        # Preserve the magnitude of velocity but change direction
        speed = self.velocity.length()
        if speed == 0:
            speed = 100  # Default speed if object was stationary

        # Set the new velocity direction with the original speed
        self.velocity = direction * speed

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the square"""
        # In normal mode, draw as black
        if not self.debug_mode:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        else:
            # In debug mode, draw with fill color and outline
            # Create a semi-transparent surface for fills
            s = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

            # Draw with transparent yellow fill
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(s, (200, 200, 0, 40), rect, 0)  # Fill with transparent yellow
            pygame.draw.rect(surface, (200, 200, 0), rect, 2)  # Yellow outline with 2px width

            # Add the transparent fill to the main surface
            surface.blit(s, (0, 0))

            # Draw corner points
            corners = [
                (self.x, self.y),  # Top-left
                (self.x + self.width, self.y),  # Top-right
                (self.x + self.width, self.y + self.height),  # Bottom-right
                (self.x, self.y + self.height)  # Bottom-left
            ]

            for point in corners:
                pygame.draw.circle(surface, (0, 255, 0), (int(point[0]), int(point[1])), 3)  # Green dots

class Circle(GameObject):
    """A simple circle shape for gameplay"""

    def __init__(self, x: float, y: float, size: float = 37.5):  # 25% larger (30 * 1.25 = 37.5)
        super().__init__(x, y, size, size)
        self.color = (0, 0, 0)  # Black
        self.marked_for_removal = False
        # Initialize screen dimensions (will be set properly when added to level)
        self.screen_width = 800
        self.screen_height = 600
        self.damage = 1  # Amount of damage to deal when colliding
        self.debug_mode = False  # Add debug mode flag

    def update(self, dt: float) -> None:
        """Update circle physics with wall bouncing"""
        super().update(dt)
        self.bounce_off_walls(self.screen_width, self.screen_height)

    def bounce_off_object(self, other: GameObject) -> None:
        """Bounce off another object"""
        # Calculate center points
        self_center = pygame.math.Vector2(self.x + self.width/2, self.y + self.height/2)
        other_center = pygame.math.Vector2(other.x + other.width/2, other.y + other.height/2)

        # Calculate bounce direction
        direction = self_center - other_center
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            # If centers are at the same position, use a random direction
            angle = random.uniform(0, 2 * math.pi)
            direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))

        # Set velocity in the direction away from the collision
        # Preserve the magnitude of velocity but change direction
        speed = self.velocity.length()
        if speed == 0:
            speed = 100  # Default speed if object was stationary

        # Set the new velocity direction with the original speed
        self.velocity = direction * speed

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the circle"""
        center = (int(self.x + self.width/2), int(self.y + self.height/2))
        radius = int(self.width/2)

        # In normal mode, draw as black
        if not self.debug_mode:
            pygame.draw.circle(surface, self.color, center, radius)
        else:
            # In debug mode, draw with fill color and outline
            # Create a semi-transparent surface for fills
            s = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

            # Draw with transparent blue fill
            pygame.draw.circle(s, (0, 0, 255, 40), center, radius, 0)  # Fill with transparent blue
            pygame.draw.circle(surface, (0, 0, 255), center, radius, 2)  # Blue outline with 2px width

            # Add the transparent fill to the main surface
            surface.blit(s, (0, 0))

            # Draw center point
            pygame.draw.circle(surface, (0, 255, 0), center, 3)  # Green dot

            # Draw a few points along the circumference to visualize the collision boundary
            num_points = 8
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                point_x = center[0] + radius * math.cos(angle)
                point_y = center[1] + radius * math.sin(angle)
                pygame.draw.circle(surface, (0, 255, 0), (int(point_x), int(point_y)), 3)  # Green dots