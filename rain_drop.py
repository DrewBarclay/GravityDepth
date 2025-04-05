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
        self.max_velocity_magnitude = 400.0  # Max velocity magnitude for limiting forces
        self.max_upward_velocity = 200.0  # Max upward velocity for limiting forces
        self.length = random.uniform(5, 15)
        self.width = 1
        self.color = (255, 0, 0)
        self.repulsion_force = 10000.0  # Gravity (8000) plus moderate boost (2000)
        self.marked_for_removal = False
        # Keep track of objects we're currently colliding with
        self.colliding_objects = set()

    def update(self, dt):
        # Only apply gravity and wind if not colliding with any objects
        if not self.colliding_objects:
            # Apply both gravity and wind acceleration
            total_acceleration = self.acceleration + self.wind_acceleration

            # Apply acceleration with small random variation for more natural motion
            variation = Vector2(
                random.uniform(-50, 50),
                random.uniform(-50, 50)
            )

            # Compute the force to be applied
            force = (total_acceleration + variation) * dt

            # Limit the force if it would exceed velocity thresholds
            self._limit_applied_force(force)

            # Apply the force to velocity
            self.velocity += force

        # Update position
        super().update(dt)

    def _limit_applied_force(self, force):
        """
        Limit the force so it doesn't cause velocity to exceed thresholds.
        Modifies the force vector in place.
        """
        # Predict new velocity after applying force
        predicted_velocity = self.velocity + force

        # Check if we're going upward (negative y velocity)
        if predicted_velocity.y < 0:
            max_allowed = self.max_upward_velocity
        else:
            max_allowed = self.max_velocity_magnitude

        # If predicted velocity exceeds the threshold, scale down the force
        if predicted_velocity.length() > max_allowed:
            # Calculate what the force should be to exactly reach max velocity
            target_velocity = predicted_velocity.normalize() * max_allowed
            # Force should be difference between target and current velocity
            limited_force = target_velocity - self.velocity

            # Copy the limited force values back to the original force vector
            force.x = limited_force.x
            force.y = limited_force.y

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

            # Scale down current velocity almost completely to eliminate previous momentum
            self.velocity *= 0.01  # Nearly complete energy loss on collision

            # Create force vector from impulse
            force = repulsion_impulse

            # Limit the force to prevent excessive velocity
            self._limit_applied_force(force)

            # Apply the limited force
            self.velocity += force

            # Ensure velocity is actually moving away from the object
            # Dot product of velocity and repulsion_dir should be positive
            # for velocity to be moving away from the object
            dot_product = self.velocity.dot(repulsion_dir)
            if dot_product < 0:
                # If velocity is not moving away, reflect it to ensure escape
                self.velocity = self.velocity.reflect(repulsion_dir)

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