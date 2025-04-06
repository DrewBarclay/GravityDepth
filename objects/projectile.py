import pygame
import math
from typing import Tuple
from objects.game_object import GameObject

class Projectile(GameObject):
    """A projectile that can be fired by enemies or players"""

    def __init__(self, x: float, y: float, velocity: pygame.math.Vector2,
                 radius: float = 5, color: Tuple[int, int, int] = (255, 0, 0),
                 lifespan: float = 3.0):
        super().__init__(x, y, radius * 2, radius * 2)
        self.radius = radius
        self.velocity = velocity
        self.color = color
        self.lifespan = lifespan
        self.lifetime = 0
        self.marked_for_removal = False

        # Flag to track if this projectile is in a gravity field
        self.in_gravity_field = False

        # Create a circular collision polygon
        self.create_circle_collision()

    def create_circle_collision(self):
        """Create a circular collision polygon"""
        num_points = 8  # Number of points to approximate circle
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            points.append((x, y))
        self.set_collision_polygon(points)

    def update(self, dt: float) -> None:
        """Update projectile position and lifetime"""
        # Reset the gravity field flag each frame
        self.in_gravity_field = False

        # Update the position using velocity
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt

        # Increment lifetime and mark for removal if expired
        self.lifetime += dt
        if self.lifetime >= self.lifespan:
            self.marked_for_removal = True

        # Check if projectile is outside screen bounds and mark for removal if it is
        if hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
            if (self.x < -self.width or self.x > self.screen_width or
                self.y < -self.height or self.y > self.screen_height):
                self.marked_for_removal = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the projectile"""
        # Change color slightly if in gravity field
        color = self.color
        if self.in_gravity_field:
            # Add a bit of orange tint to show it's affected by gravity
            color = (
                min(255, self.color[0] + 40),
                min(255, self.color[1] + 20),
                self.color[2]
            )

        pygame.draw.circle(
            surface,
            color,
            (int(self.x + self.radius), int(self.y + self.radius)),
            int(self.radius)
        )

        # Draw a small white dot in the center for effect
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.x + self.radius), int(self.y + self.radius)),
            int(self.radius * 0.3)
        )