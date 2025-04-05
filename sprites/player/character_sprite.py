import pygame
import numpy as np
from typing import Tuple, Optional, List
from utils.advanced_polygon_utils import create_circle_polygon, create_rect_polygon, combine_polygons

class CharacterSprite:
    """Class for generating and rendering a hooded figure character"""

    def __init__(self, width: int = 50, height: int = 50, color: Tuple[int, int, int] = (70, 70, 120)):
        self.width = width
        self.height = height
        self.color = color
        self.hood_color = (50, 50, 90)  # Darker shade for hood
        self.face_color = (20, 20, 30)  # Dark void for face
        self.surface = self.generate_sprite()

        # Generate body and hood polygons separately
        self.body_polygon = self.generate_body_polygon()
        self.hood_polygon = self.generate_hood_polygon()

        # Store the raw polygons for debugging
        self._raw_hood = self.hood_polygon
        self._raw_body = self.body_polygon

        # Combine them to form the full collision polygon
        # Use combine_polygons for proper convex hull generation
        self.collision_polygon = combine_polygons([self.body_polygon, self.hood_polygon])

    def generate_body_polygon(self) -> List[Tuple[float, float]]:
        """Generate a polygon for the body/robe part of the character"""
        # Body dimensions
        body_width = int(self.width * 0.8)
        body_height = int(self.height * 0.6)
        body_x = (self.width - body_width) // 2
        body_y = self.height - body_height

        # Create rectangular polygon for the body
        return create_rect_polygon((body_x, body_y, body_width, body_height))

    def generate_hood_polygon(self) -> List[Tuple[float, float]]:
        """Generate a polygon for the hood/head part of the character"""
        # Hood/head dimensions
        hood_radius = int(self.width * 0.4)
        hood_center_x = self.width // 2
        hood_center_y = self.height - int(self.height * 0.6)  # Same as body_y

        # Create a full elliptical polygon to completely encapsulate the hood
        hood_polygon = []

        # Use an ellipse that's wider than it is tall to better match the hood shape
        ellipse_width = hood_radius * 2.1  # Make it wider than the hood
        ellipse_height = hood_radius * 1.7  # Make it tall enough to cover the hood

        # Generate points around the full ellipse
        num_points = 24  # More points for smoother shape
        for i in range(num_points):
            angle = np.radians(i * 360 / num_points)
            # Parametric equation of ellipse
            x = hood_center_x + (ellipse_width/2) * np.cos(angle)
            y = hood_center_y + (ellipse_height/2) * np.sin(angle)
            hood_polygon.append((x, y))

        # Close the polygon
        hood_polygon.append(hood_polygon[0])

        return hood_polygon

    def generate_sprite(self) -> pygame.Surface:
        """Generate a hooded figure sprite"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Body dimensions
        body_width = int(self.width * 0.8)
        body_height = int(self.height * 0.6)
        body_x = (self.width - body_width) // 2
        body_y = self.height - body_height

        # Hood/head dimensions
        hood_radius = int(self.width * 0.4)
        hood_center = (self.width // 2, body_y)

        # Draw the body (robe)
        body_rect = pygame.Rect(body_x, body_y, body_width, body_height)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=int(body_width * 0.2))

        # Draw the hood (semi-circle)
        pygame.draw.circle(surface, self.hood_color, hood_center, hood_radius)

        # Calculate face area
        face_width = int(hood_radius * 1.2)
        face_height = int(hood_radius * 0.7)
        face_x = hood_center[0] - face_width // 2
        face_y = hood_center[1] - face_height // 3

        # Draw the dark face area inside hood
        face_rect = pygame.Rect(face_x, face_y, face_width, face_height)
        pygame.draw.ellipse(surface, self.face_color, face_rect)

        # Add some details - simple folds in the robe
        fold_y1 = body_y + body_height // 3
        fold_y2 = body_y + (body_height * 2) // 3

        pygame.draw.line(surface,
                        (self.color[0] - 20, self.color[1] - 20, self.color[2] - 20),
                        (body_x + 5, fold_y1),
                        (body_x + body_width - 5, fold_y1),
                        2)

        pygame.draw.line(surface,
                        (self.color[0] - 20, self.color[1] - 20, self.color[2] - 20),
                        (body_x + 5, fold_y2),
                        (body_x + body_width - 5, fold_y2),
                        2)

        return surface

    def render(self, surface: pygame.Surface, position: Tuple[float, float]) -> None:
        """Render the sprite at the given position"""
        surface.blit(self.surface, position)

    def get_surface(self) -> pygame.Surface:
        """Get the sprite surface"""
        return self.surface

    def get_debug_polygons(self, position: Tuple[float, float]) -> dict:
        """Get all polygons with world positions for debugging"""
        # Offset polygons by the given position
        offset_body = [(x + position[0], y + position[1]) for x, y in self._raw_body]
        offset_hood = [(x + position[0], y + position[1]) for x, y in self._raw_hood]
        offset_combined = [(x + position[0], y + position[1]) for x, y in self.collision_polygon]

        return {
            'body': offset_body,
            'hood': offset_hood,
            'combined': offset_combined
        }