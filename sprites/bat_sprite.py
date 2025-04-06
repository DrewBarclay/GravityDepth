import pygame
import numpy as np
from typing import Tuple, List
from utils.advanced_polygon_utils import create_circle_polygon

class BatSprite:
    """Class for generating and rendering a bat sprite"""

    def __init__(self, width: int = 40, height: int = 30, color: Tuple[int, int, int] = (80, 40, 100)):
        self.width = width
        self.height = height
        self.color = color
        self.wing_color = (100, 60, 120)
        self.eye_color = (255, 0, 0)  # Red eyes
        self.surface = self.generate_sprite()

        # Generate collision polygon
        self.collision_polygon = self.generate_collision_polygon()

    def generate_collision_polygon(self) -> List[Tuple[float, float]]:
        """Generate a simple collision polygon for the bat"""
        # Create a simple oval-shaped collision polygon
        num_points = 12
        polygon = []
        center_x = self.width / 2
        center_y = self.height / 2

        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            x = center_x + (self.width / 2 * 0.8) * np.cos(angle)
            y = center_y + (self.height / 2 * 0.9) * np.sin(angle)
            polygon.append((x, y))

        return polygon

    def generate_sprite(self) -> pygame.Surface:
        """Generate the bat sprite"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Body dimensions
        body_width = int(self.width * 0.5)
        body_height = int(self.height * 0.7)
        body_x = (self.width - body_width) // 2
        body_y = (self.height - body_height) // 2

        # Draw the body (oval) - completely black now
        body_rect = pygame.Rect(body_x, body_y, body_width, body_height)
        pygame.draw.ellipse(surface, (0, 0, 0), body_rect)

        # Draw wings - completely black now
        # Left wing
        left_wing_points = [
            (body_x, body_y + body_height // 2),  # Connect to body
            (body_x - self.width * 0.25, body_y + body_height * 0.2),  # Wing tip upper
            (body_x - self.width * 0.3, body_y + body_height * 0.5),  # Wing tip middle
            (body_x - self.width * 0.25, body_y + body_height * 0.8),  # Wing tip lower
        ]
        pygame.draw.polygon(surface, (0, 0, 0), left_wing_points)

        # Right wing
        right_wing_points = [
            (body_x + body_width, body_y + body_height // 2),  # Connect to body
            (body_x + body_width + self.width * 0.25, body_y + body_height * 0.2),  # Wing tip upper
            (body_x + body_width + self.width * 0.3, body_y + body_height * 0.5),  # Wing tip middle
            (body_x + body_width + self.width * 0.25, body_y + body_height * 0.8),  # Wing tip lower
        ]
        pygame.draw.polygon(surface, (0, 0, 0), right_wing_points)

        # Draw glowing red eyes
        eye_radius = int(body_width * 0.2)
        eye_distance = int(body_width * 0.3)
        eye_y = body_y + int(body_height * 0.3)

        # Draw glowing eyes with a glow effect
        for i in range(3):
            glow_radius = eye_radius * (1 + (i * 0.5))
            glow_alpha = 150 - (i * 50)  # Fade the outer glow

            # Left eye glow
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface,
                         (body_x + body_width // 2 - eye_distance - glow_radius,
                          eye_y - glow_radius))

            # Right eye glow
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface,
                         (body_x + body_width // 2 + eye_distance - glow_radius,
                          eye_y - glow_radius))

        # Solid eye centers
        pygame.draw.circle(surface, self.eye_color,
                          (body_x + body_width // 2 - eye_distance, eye_y),
                          eye_radius)
        pygame.draw.circle(surface, self.eye_color,
                          (body_x + body_width // 2 + eye_distance, eye_y),
                          eye_radius)

        # Draw small fangs - white
        fang_length = int(body_height * 0.2)

        # Left fang
        pygame.draw.line(surface, (255, 255, 255),
                        (body_x + body_width // 3, body_y + body_height),
                        (body_x + body_width // 3, body_y + body_height + fang_length),
                        2)

        # Right fang
        pygame.draw.line(surface, (255, 255, 255),
                        (body_x + 2 * body_width // 3, body_y + body_height),
                        (body_x + 2 * body_width // 3, body_y + body_height + fang_length),
                        2)

        return surface

    def render(self, surface: pygame.Surface, position: Tuple[float, float], debug_mode: bool = False) -> None:
        """Render the sprite at the given position - only fully show in debug mode"""
        if debug_mode:
            surface.blit(self.surface, position)
        else:
            # Only draw the eyes when not in debug mode
            # Extract the body dimensions and eye positions
            body_width = int(self.width * 0.5)
            body_height = int(self.height * 0.7)
            body_x = (self.width - body_width) // 2
            body_y = (self.height - body_height) // 2

            eye_radius = int(body_width * 0.2)
            eye_distance = int(body_width * 0.3)
            eye_y = body_y + int(body_height * 0.3)

            # Draw glowing eyes at the correct world position
            for i in range(3):
                glow_radius = eye_radius * (1 + (i * 0.5))
                glow_alpha = 150 - (i * 50)  # Fade the outer glow

                # Left eye glow
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha), (glow_radius, glow_radius), glow_radius)
                surface.blit(glow_surface,
                            (position[0] + body_x + body_width // 2 - eye_distance - glow_radius,
                             position[1] + eye_y - glow_radius))

                # Right eye glow
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha), (glow_radius, glow_radius), glow_radius)
                surface.blit(glow_surface,
                            (position[0] + body_x + body_width // 2 + eye_distance - glow_radius,
                             position[1] + eye_y - glow_radius))

            # Solid eye centers
            pygame.draw.circle(surface, (255, 0, 0),
                              (int(position[0] + body_x + body_width // 2 - eye_distance),
                               int(position[1] + eye_y)),
                              eye_radius)
            pygame.draw.circle(surface, (255, 0, 0),
                              (int(position[0] + body_x + body_width // 2 + eye_distance),
                               int(position[1] + eye_y)),
                              eye_radius)

    def get_surface(self) -> pygame.Surface:
        """Get the sprite surface"""
        return self.surface

    def get_debug_polygons(self, position: Tuple[float, float]) -> dict:
        """Get all polygons with world positions for debugging"""
        # Offset polygons by the given position
        offset_collision = [(x + position[0], y + position[1]) for x, y in self.collision_polygon]

        return {
            'combined': offset_collision
        }