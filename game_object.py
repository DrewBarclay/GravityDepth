import pygame
from typing import Tuple, Optional, Dict, Any, List
from advanced_polygon_utils import polygons_collide, create_rect_polygon

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
        # Initialize polygon as None, will be set by subclasses or default to rect
        self._collision_polygon: Optional[List[Tuple[float, float]]] = None

    @property
    def collision_polygon(self) -> List[Tuple[float, float]]:
        """Get the collision polygon for this object in world coordinates.
        If not set, generates a rectangle polygon from the object's dimensions."""
        if self._collision_polygon is None:
            # Default to rectangle if no custom polygon is set
            self._collision_polygon = create_rect_polygon((0, 0, self.width, self.height))

        # Apply the position offset to the polygon points
        return [(self.x + point[0], self.y + point[1]) for point in self._collision_polygon]

    def set_collision_polygon(self, polygon: List[Tuple[float, float]]) -> None:
        """Set a custom collision polygon for this object.
        The provided polygon should be in local coordinates (relative to the object's position)."""
        self._collision_polygon = polygon

    def update(self, dt: float) -> None:
        """Update object physics"""
        # Update velocity with acceleration
        self.velocity += self.acceleration * dt

        # Update position with velocity
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt

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
        """Check if this object collides with another object using polygon collision detection"""
        # First do a quick AABB check using rectangles for efficiency
        if not self.get_rect().colliderect(other.get_rect()):
            return False

        # Then do precise polygon collision check using the advanced polygon collision system
        return polygons_collide(self.collision_polygon, other.collision_polygon)

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value"""
        return self.properties.get(key, default)

    def set_property(self, key: str, value: Any) -> None:
        """Set a property value"""
        self.properties[key] = value