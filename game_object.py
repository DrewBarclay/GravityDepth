import pygame
from typing import Tuple, Optional, Dict, Any

class GameObject:
    """Base class for all game objects with physics and state, but no rendering"""
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.properties: Dict[str, Any] = {}

    def update(self, dt: float) -> None:
        """Update object physics"""
        # Update velocity with acceleration
        self.velocity += self.acceleration * dt

        # Update position with velocity
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt

        # Reset acceleration
        self.acceleration = pygame.math.Vector2(0, 0)

    def apply_force(self, force: pygame.math.Vector2) -> None:
        """Apply a force to the object"""
        self.acceleration += force

    def get_position(self) -> Tuple[float, float]:
        """Get the current position of the object"""
        return (self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """Set the position of the object"""
        self.x = x
        self.y = y

    def get_rect(self) -> pygame.Rect:
        """Get the rectangle representing this object"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with(self, other: 'GameObject') -> bool:
        """Check if this object collides with another object"""
        return self.get_rect().colliderect(other.get_rect())

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value"""
        return self.properties.get(key, default)

    def set_property(self, key: str, value: Any) -> None:
        """Set a property value"""
        self.properties[key] = value