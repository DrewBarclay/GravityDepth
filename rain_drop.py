from game_object import GameObject
from pygame.math import Vector2
import random
import pygame
from raindrop_constants import (
    DEFAULT_VELOCITY_Y,
    DEFAULT_ACCELERATION,
    MAX_VELOCITY_MAGNITUDE,
    MAX_UPWARD_VELOCITY,
    DEFAULT_WIDTH,
    MIN_LENGTH,
    MAX_LENGTH,
    DEFAULT_COLOR,
    REPULSION_FORCE,
    COLLISION_VELOCITY_DAMPING,
    DEPTH_REPULSION_MULTIPLIER
)

class RainDrop(GameObject):
    def __init__(self, x, y, wind_force=0):
        # Initialize with width=1 and height=length (will be set after super().__init__)
        super().__init__(x, y, width=DEFAULT_WIDTH, height=1)
        # Base velocity (falling down and slightly right)
        self.velocity = Vector2(wind_force, DEFAULT_VELOCITY_Y)
        self.acceleration = DEFAULT_ACCELERATION  # Much stronger gravity
        self.wind_acceleration = Vector2(0, 0)  # Wind will be applied as acceleration
        self.max_velocity_magnitude = MAX_VELOCITY_MAGNITUDE  # Max velocity magnitude for limiting forces
        self.max_upward_velocity = MAX_UPWARD_VELOCITY  # Max upward velocity for limiting forces
        self.length = random.uniform(MIN_LENGTH, MAX_LENGTH)
        self.width = DEFAULT_WIDTH
        self.color = DEFAULT_COLOR
        self.repulsion_force = REPULSION_FORCE  # Strong repulsion force for bouncing
        self.marked_for_removal = False
        # Keep track of objects we're currently colliding with
        self.colliding_objects = set()

    def update(self, dt):
        # Only apply gravity if NOT colliding with objects
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
        else:
            # Inside an object - cancel all velocity and apply strong upward force

            # Almost completely stop the raindrop
            self.velocity *= COLLISION_VELOCITY_DAMPING

            # Apply strong repulsion forces from all colliding objects
            for obj in self.colliding_objects:
                self.apply_repulsion_force(obj, dt)

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

        # Update the set of objects we're colliding with
        self.colliding_objects = currently_colliding

    def apply_repulsion_force(self, obj, dt):
        """Apply a strong repulsion force to exit the object, stronger the deeper inside"""
        # Calculate direction from object center to raindrop
        obj_center = Vector2(obj.x + obj.width/2, obj.y + obj.height/2)
        my_pos = Vector2(self.x, self.y)

        # Direction vector pointing away from the object's center
        repulsion_dir = my_pos - obj_center

        # Only apply force if we have a non-zero direction
        if repulsion_dir.length() > 0:
            repulsion_dir = repulsion_dir.normalize()

            # Calculate how deep into the object we are
            # Create rectangle for the object
            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            # Find the nearest point on the edge of the rectangle to the center
            edge_x = max(obj_rect.left, min(my_pos.x, obj_rect.right))
            edge_y = max(obj_rect.top, min(my_pos.y, obj_rect.bottom))
            edge_point = Vector2(edge_x, edge_y)

            # Calculate distance from current position to the edge (depth)
            depth = max(1.0, (edge_point - my_pos).length())

            # Scale repulsion force based on depth - deeper means stronger force
            depth_multiplier = 1.0 + (depth * DEPTH_REPULSION_MULTIPLIER)

            # Create strong force in the exit direction, scaled by depth
            repulsion_force = repulsion_dir * self.repulsion_force * depth_multiplier * dt

            # Apply the repulsion force
            self.velocity += repulsion_force

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

        # Change color based on collision state
        draw_color = self.color
        if self.colliding_objects:
            # Brighter red when inside an object
            draw_color = (255, 100, 100)

        pygame.draw.line(surface, draw_color, (int(self.x), int(self.y)), end_pos, 1)