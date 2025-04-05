from game_object import GameObject
from pygame.math import Vector2
import random
import pygame

class RainDrop(GameObject):
    def __init__(self, x, y, wind_force=0):
        # Initialize with width=1 and height=length (will be set after super().__init__)
        super().__init__(x, y, width=1, height=1)
        # Base velocity (falling down and slightly right)
        self.velocity = Vector2(wind_force, 200.0)
        self.acceleration = Vector2(0, 8000.0)  # Much stronger gravity
        self.wind_acceleration = Vector2(0, 0)  # Wind will be applied as acceleration
        self.max_speed = 400.0  # Max speed for any motion
        self.max_upward_speed = 200.0  # Max speed when moving upward
        self.length = random.uniform(5, 15)
        self.width = 1
        self.color = (255, 0, 0)
        self.repulsion_force = 300.0  # Increased repulsion force
        self.marked_for_removal = False
        # Keep track of objects we're currently colliding with
        self.colliding_objects = set()

    def update(self, dt):
        # Apply both gravity and wind acceleration
        total_acceleration = self.acceleration + self.wind_acceleration

        # Apply acceleration with small random variation for more natural motion
        variation = Vector2(
            random.uniform(-50, 50),
            random.uniform(-50, 50)
        )
        self.velocity += (total_acceleration + variation) * dt

        # Apply speed limits based on direction
        self._limit_speed()

        # Update position
        super().update(dt)

    def _limit_speed(self):
        """Limit speed differently based on direction of motion"""
        # If moving upward, use stricter speed limit
        if self.velocity.y < 0:
            max_allowed = self.max_upward_speed
        else:
            max_allowed = self.max_speed

        speed = self.velocity.length()
        if speed > max_allowed:
            scale_factor = max_allowed / speed
            self.velocity.x *= scale_factor
            self.velocity.y *= scale_factor

    def check_and_handle_collisions(self, game_objects, dt):
        # Check each object for collision
        currently_colliding = set()

        for obj in game_objects:
            if obj is self:
                continue

            # Test if we're actually colliding
            # Use Rect objects to test collision
            raindrop_rect = pygame.Rect(self.x, self.y, self.width, self.length)
            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            if raindrop_rect.colliderect(obj_rect):
                currently_colliding.add(obj)
                # Apply more forceful repulsion to escape the object quickly
                self.apply_repulsion_force(obj, dt * 3.0)  # Apply stronger force with multiplier

        # Update the set of objects we're colliding with
        self.colliding_objects = currently_colliding

    def apply_repulsion_force(self, obj, dt):
        # Calculate vector from object center to raindrop
        obj_center = Vector2(obj.x + obj.width/2, obj.y + obj.height/2)
        my_pos = Vector2(self.x, self.y)

        # Direction vector pointing away from the object's center
        repulsion_dir = my_pos - obj_center

        # Only apply force if we have a non-zero direction
        if repulsion_dir.length() > 0:
            repulsion_dir = repulsion_dir.normalize()

            # For near-horizontal collisions, ensure upward component
            if abs(repulsion_dir.y) < 0.2:
                repulsion_dir.y -= 0.8  # Stronger upward component
                repulsion_dir = repulsion_dir.normalize()

            # Calculate repulsion impulse with some randomness
            random_factor = random.uniform(0.8, 1.2)  # 20% variation
            repulsion_impulse = repulsion_dir * self.repulsion_force * random_factor

            # Scale down current velocity more aggressively
            self.velocity *= 0.05  # Even more energy loss on collision

            # Add repulsion impulse
            self.velocity += repulsion_impulse

            # Ensure minimum upward velocity after collision
            if self.velocity.y > -100:  # If not moving up fast enough
                self.velocity.y = -200   # Strong upward bounce

            # Apply speed limits immediately after collision
            self._limit_speed()

    def handle_collision(self, other):
        # This is for backward compatibility
        # Real collision handling is now done in check_and_handle_collisions
        self.apply_repulsion_force(other, 0.016)  # Use a small default dt value

    def collides_with(self, other):
        """Check if this object collides with another"""
        raindrop_rect = pygame.Rect(self.x, self.y, self.width, self.length)
        other_rect = pygame.Rect(other.x, other.y, other.width, other.height)
        return raindrop_rect.colliderect(other_rect)

    def draw(self, surface):
        # Draw a line from the current position downward based on velocity
        end_pos = (
            int(self.x),
            int(self.y + self.length)
        )
        pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), end_pos, 1)