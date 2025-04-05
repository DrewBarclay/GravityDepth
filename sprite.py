import pygame
import numpy as np
from typing import Tuple

class Sprite:
    """Base class for all game sprites"""
    def __init__(self, x: float, y: float, size: int = 40):
        self.x = x
        self.y = y
        self.size = size
        self.surface = self.generate_sprite()
        self.rect = pygame.Rect(x, y, size, size)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

    def generate_sprite(self) -> pygame.Surface:
        """Generate the sprite's visual representation"""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # Create a triangular sprite using numpy for coordinate calculation
        points = np.array([
            [self.size//2, 0],  # Top
            [0, self.size],     # Bottom left
            [self.size, self.size]  # Bottom right
        ])

        # Draw the triangle
        pygame.draw.polygon(surface, (0, 0, 255), points)

        # Add a red circle in the center
        center = (self.size//2, self.size//2)
        pygame.draw.circle(surface, (255, 0, 0), center, self.size//4)

        return surface

    def update(self, dt: float) -> None:
        """Update sprite physics"""
        # Update velocity with acceleration
        self.velocity += self.acceleration * dt

        # Update position with velocity
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt

        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y

        # Reset acceleration
        self.acceleration = pygame.math.Vector2(0, 0)

    def apply_force(self, force: pygame.math.Vector2) -> None:
        """Apply a force to the sprite"""
        self.acceleration += force

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the sprite on the screen"""
        screen.blit(self.surface, (self.x, self.y))

    def get_position(self) -> Tuple[float, float]:
        """Get the current position of the sprite"""
        return (self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """Set the position of the sprite"""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y