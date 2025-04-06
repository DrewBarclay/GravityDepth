import pygame
import random
import math
from typing import List, Optional
from objects.game_object import GameObject
from sprites.bat_sprite import BatSprite
from objects.projectile import Projectile
from config.game_constants import (
    BAT_PROJECTILE_LIFESPAN,
    BAT_ATTACK_COOLDOWN_MIN,
    BAT_ATTACK_COOLDOWN_MAX,
    BAT_ATTACK_SPEED,
    BAT_MOVEMENT_SPEED,
    BAT_HOVER_AMPLITUDE,
    BAT_HOVER_FREQUENCY,
    BAT_PROJECTILE_IMMUNE_TIME
)

class Bat(GameObject):
    """A bat enemy that shoots projectiles at the player"""

    def __init__(self, x: float, y: float, width: int = 40, height: int = 30):
        super().__init__(x, y, width, height)
        self.bat_sprite = BatSprite(width=width, height=height)
        self.set_collision_polygon(self.bat_sprite.collision_polygon)

        # Movement parameters
        self.movement_speed = BAT_MOVEMENT_SPEED
        self.hover_amplitude = BAT_HOVER_AMPLITUDE
        self.hover_frequency = BAT_HOVER_FREQUENCY
        self.hover_time = 0

        # Horizontal movement parameters
        self.direction = 1  # 1 for right, -1 for left
        self.direction_change_timer = 0
        self.direction_change_interval = random.uniform(2.0, 4.0)  # seconds

        # Attack parameters
        self.attack_cooldown = random.uniform(BAT_ATTACK_COOLDOWN_MIN, BAT_ATTACK_COOLDOWN_MAX)
        self.attack_timer = random.uniform(0, 1.0)  # start with a random timer
        self.attack_speed = BAT_ATTACK_SPEED
        self.projectiles: List[Projectile] = []
        self.projectile_lifespan = BAT_PROJECTILE_LIFESPAN

        # Debug mode
        self.debug_mode = False

        # Marked for removal flag
        self.marked_for_removal = False

        # Projectile immunity - don't let bats be hit by their own just-fired projectiles
        self.projectile_immune_time = BAT_PROJECTILE_IMMUNE_TIME
        self.projectile_immunity_timer = 0

    def update(self, dt: float) -> None:
        """Update bat position, hovering movement, and attack cooldown"""
        # Prevent divide by zero
        if dt <= 0:
            return

        # Update hover time
        self.hover_time += dt

        # Calculate hover offset
        hover_offset = self.hover_amplitude * math.sin(2 * math.pi * self.hover_frequency * self.hover_time)

        # Update direction change timer
        self.direction_change_timer += dt
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction *= -1  # Reverse direction
            self.direction_change_timer = 0
            self.direction_change_interval = random.uniform(2.0, 4.0)  # new random interval

        # Calculate horizontal movement
        horizontal_movement = self.direction * self.movement_speed * dt

        # Update position with hover effect and horizontal movement
        self.y += hover_offset - self.velocity.y  # Apply hover offset (subtract previous velocity.y to get the delta)
        self.x += horizontal_movement

        # Store the hover velocity for the next frame
        self.velocity.y = hover_offset
        self.velocity.x = horizontal_movement / dt  # Store as velocity rather than displacement

        # Handle wall bouncing
        if hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
            # Only bounce off the side walls, allow free vertical movement
            if self.x <= 0:
                self.x = 0
                self.direction = 1  # Move right
            elif self.x + self.width >= self.screen_width:
                self.x = self.screen_width - self.width
                self.direction = -1  # Move left

        # Update attack cooldown
        self.attack_timer += dt

        # Update projectile immunity timer
        if self.projectile_immunity_timer > 0:
            self.projectile_immunity_timer -= dt

        # Update all projectiles
        for projectile in self.projectiles[:]:  # Make a copy of the list to safely remove while iterating
            projectile.update(dt)
            if projectile.marked_for_removal:
                self.projectiles.remove(projectile)

    def check_projectile_collisions(self, projectiles: List[Projectile]) -> None:
        """Check collisions with projectiles (from other bats)"""
        # Skip if we have immunity
        if self.projectile_immunity_timer > 0:
            return

        for projectile in projectiles:
            # Skip our own projectiles
            if projectile in self.projectiles:
                continue

            # Check for collision
            if self.collides_with(projectile):
                # Mark projectile for removal
                projectile.marked_for_removal = True
                # Mark bat for removal too
                self.marked_for_removal = True

    def find_target_player(self, players: List[GameObject]) -> Optional[GameObject]:
        """Find a player on the same vertical level as the bat"""
        # Ensure we have players to check
        if not players:
            return None

        # Sort players by vertical distance from the bat
        same_level_players = []
        bat_center_y = self.y + self.height/2

        for player in players:
            # Check if player is roughly on the same vertical level
            player_center_y = player.y + player.height/2
            vertical_distance = abs(bat_center_y - player_center_y)

            # Check if player is within vertical targeting range
            if vertical_distance < self.height * 2:  # Allow some leeway for targeting
                same_level_players.append(player)

        if same_level_players:
            # Return the closest player horizontally
            return min(same_level_players,
                       key=lambda p: abs((self.x + self.width/2) - (p.x + p.width/2)))

        return None

    def shoot_at_player(self, player: GameObject) -> None:
        """Create a projectile aimed at the player"""
        # Reset attack timer
        self.attack_timer = 0
        self.attack_cooldown = random.uniform(BAT_ATTACK_COOLDOWN_MIN, BAT_ATTACK_COOLDOWN_MAX)

        # Set projectile immunity temporarily
        self.projectile_immunity_timer = self.projectile_immune_time

        # Calculate center positions
        bat_center_x = self.x + self.width / 2
        bat_center_y = self.y + self.height / 2
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2

        # Calculate direction vector to player
        dx = player_center_x - bat_center_x
        dy = player_center_y - bat_center_y
        distance = math.sqrt(dx**2 + dy**2)

        # Normalize and scale to attack speed
        if distance > 0:
            dx = dx / distance * self.attack_speed
            dy = dy / distance * self.attack_speed
        else:
            # Handle edge case where player is at the exact same position
            # In this case, shoot in a random direction
            angle = random.uniform(0, math.pi * 2)
            dx = math.cos(angle) * self.attack_speed
            dy = math.sin(angle) * self.attack_speed

        # Create a projectile with velocity aimed at player and a longer lifespan
        projectile = Projectile(
            bat_center_x - 5,  # Offset by projectile radius
            bat_center_y - 5,  # Offset by projectile radius
            pygame.math.Vector2(dx, dy),
            lifespan=self.projectile_lifespan
        )

        # Set the screen dimensions for the projectile
        if hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
            projectile.screen_width = self.screen_width
            projectile.screen_height = self.screen_height

        # Add to projectiles list
        self.projectiles.append(projectile)

    def try_attack(self, players: List[GameObject]) -> None:
        """Try to attack if cooldown is over and there's a player to target"""
        # Check cooldown first
        if self.attack_timer >= self.attack_cooldown:
            target_player = self.find_target_player(players)

            if target_player:
                # We have a target, shoot at it
                self.shoot_at_player(target_player)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bat and its projectiles"""
        # Draw the bat sprite
        self.bat_sprite.render(surface, (self.x, self.y))

        # Draw all projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

        # Draw debug info if enabled
        if self.debug_mode:
            # Draw collision polygon
            polygon = [(x, y) for x, y in self.collision_polygon]
            pygame.draw.polygon(surface, (0, 255, 0), polygon, 1)

            # Draw attack range indicator (horizontal line at bat's level)
            pygame.draw.line(
                surface,
                (255, 0, 0),
                (0, self.y + self.height/2),
                (self.screen_width if hasattr(self, 'screen_width') else 800, self.y + self.height/2),
                1
            )