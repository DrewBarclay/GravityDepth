import pygame
import numpy as np
from typing import Tuple, Optional, List

class CharacterSprite:
    """Class for generating and rendering a hooded figure character"""

    def __init__(self, width: int = 50, height: int = 50, color: Tuple[int, int, int] = (70, 70, 120)):
        self.width = width
        self.height = height
        self.color = color
        self.hood_color = (50, 50, 90)  # Darker shade for hood
        self.face_color = (20, 20, 30)  # Dark void for face
        self.surface = self.generate_sprite()

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