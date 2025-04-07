import pygame
import numpy as np
from typing import Tuple, List
from utils.advanced_polygon_utils import create_circle_polygon

class BatSprite:
    """Class for generating and rendering a bat sprite"""

    def __init__(self, width: int = 55, height: int = 42, color: Tuple[int, int, int] = (80, 40, 100)):
        # Increased width from 50 to 55 and height from 38 to 42 (10% increase)
        self.width = width
        self.height = height
        self.color = color
        self.wing_color = (100, 60, 120)
        self.eye_color = (255, 0, 0)  # Red eyes
        # Store the wing points for collision polygon
        self.body_points = []
        self.left_wing_points = []
        self.right_wing_points = []
        # Generate the sprite
        self.surface = self.generate_sprite()
        # Generate collision polygon
        self.collision_polygon = self.generate_collision_polygon()

    def generate_collision_polygon(self) -> List[Tuple[float, float]]:
        """Generate a bat-shaped collision polygon using body and wing points"""
        # Combine all points from body and wings
        all_points = []
        # Add wing tips and parts of the body to create the bat silhouette
        all_points.extend(self.left_wing_points)
        all_points.extend(self.right_wing_points)

        # Add body points to complete the shape
        body_x = (self.width - int(self.width * 0.625)) // 2
        body_width = int(self.width * 0.625)
        body_height = int(self.height * 0.875)

        # Include key body points if not already included
        body_top_left = (body_x, self.height * 0.15)
        body_top_right = (body_x + body_width, self.height * 0.15)
        body_bottom_left = (body_x, self.height * 0.85)
        body_bottom_right = (body_x + body_width, self.height * 0.85)

        all_points.append(body_top_left)
        all_points.append(body_top_right)
        all_points.append(body_bottom_left)
        all_points.append(body_bottom_right)

        return all_points

    def generate_sprite(self) -> pygame.Surface:
        """Generate the bat sprite with wings"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Body dimensions - increased by 25%
        body_width = int(self.width * 0.625)
        body_height = int(self.height * 0.875)
        body_x = (self.width - body_width) // 2
        body_y = (self.height - body_height) // 2

        # Store body points for collision polygon
        self.body_points = [
            (body_x, body_y),
            (body_x + body_width, body_y),
            (body_x + body_width, body_y + body_height),
            (body_x, body_y + body_height)
        ]

        # Draw more detailed wings - wing span increased
        # Left wing with membrane segments
        left_wing_points = [
            (body_x, body_y + body_height * 0.3),  # Upper connection to body
            (body_x - self.width * 0.38, body_y),  # Upper wing tip - wider
            (body_x - self.width * 0.44, body_y + body_height * 0.3),  # Middle finger tip - wider
            (body_x - self.width * 0.38, body_y + body_height * 0.6),  # Lower finger tip - wider
            (body_x, body_y + body_height * 0.7),  # Lower connection to body
        ]
        self.left_wing_points = left_wing_points

        # Right wing with membrane segments
        right_wing_points = [
            (body_x + body_width, body_y + body_height * 0.3),  # Upper connection to body
            (body_x + body_width + self.width * 0.38, body_y),  # Upper wing tip - wider
            (body_x + body_width + self.width * 0.44, body_y + body_height * 0.3),  # Middle finger tip - wider
            (body_x + body_width + self.width * 0.38, body_y + body_height * 0.6),  # Lower finger tip - wider
            (body_x + body_width, body_y + body_height * 0.7),  # Lower connection to body
        ]
        self.right_wing_points = right_wing_points

        # Draw body (darker color)
        body_rect = pygame.Rect(body_x, body_y, body_width, body_height)
        pygame.draw.ellipse(surface, (20, 10, 30), body_rect)

        # Draw detailed wings
        # Left wing
        pygame.draw.polygon(surface, (40, 20, 60), left_wing_points)

        # Right wing
        pygame.draw.polygon(surface, (40, 20, 60), right_wing_points)

        # Draw wing structure (bones)
        # Left wing bones
        pygame.draw.line(surface, (20, 10, 30), left_wing_points[0], left_wing_points[1], 2)  # Upper bone
        pygame.draw.line(surface, (20, 10, 30), left_wing_points[0], left_wing_points[2], 2)  # Middle bone
        pygame.draw.line(surface, (20, 10, 30), left_wing_points[0], left_wing_points[3], 2)  # Lower bone

        # Right wing bones
        pygame.draw.line(surface, (20, 10, 30), right_wing_points[0], right_wing_points[1], 2)  # Upper bone
        pygame.draw.line(surface, (20, 10, 30), right_wing_points[0], right_wing_points[2], 2)  # Middle bone
        pygame.draw.line(surface, (20, 10, 30), right_wing_points[0], right_wing_points[3], 2)  # Lower bone

        # Draw glowing red eyes - smaller size
        eye_radius = int(body_width * 0.12)
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

        # Draw small ears
        ear_width = int(body_width * 0.2)
        ear_height = int(body_height * 0.4)

        # Left ear
        pygame.draw.polygon(surface, (20, 10, 30), [
            (body_x + body_width // 3 - ear_width//2, body_y),  # Base left
            (body_x + body_width // 3 + ear_width//2, body_y),  # Base right
            (body_x + body_width // 3, body_y - ear_height),  # Tip
        ])

        # Right ear
        pygame.draw.polygon(surface, (20, 10, 30), [
            (body_x + 2 * body_width // 3 - ear_width//2, body_y),  # Base left
            (body_x + 2 * body_width // 3 + ear_width//2, body_y),  # Base right
            (body_x + 2 * body_width // 3, body_y - ear_height),  # Tip
        ])

        return surface

    def render(self, surface: pygame.Surface, position: Tuple[float, float], debug_mode: bool = False) -> None:
        """Render the sprite at the given position"""
        if debug_mode:
            # In debug mode, show the full sprite
            surface.blit(self.surface, position)
        else:
            # In normal mode, draw the bat with silhouette
            # Draw a slightly transparent silhouette of the bat
            silhouette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            # Draw body silhouette
            body_width = int(self.width * 0.625)
            body_height = int(self.height * 0.875)
            body_x = (self.width - body_width) // 2
            body_y = (self.height - body_height) // 2
            body_rect = pygame.Rect(body_x, body_y, body_width, body_height)
            pygame.draw.ellipse(silhouette, (10, 5, 15, 60), body_rect)

            # Draw left wing silhouette
            pygame.draw.polygon(silhouette, (10, 5, 15, 40), self.left_wing_points)

            # Draw right wing silhouette
            pygame.draw.polygon(silhouette, (10, 5, 15, 40), self.right_wing_points)

            # Draw the silhouette on the main surface
            surface.blit(silhouette, position)

            # Extract the body dimensions and eye positions for eyes
            body_x = (self.width - body_width) // 2
            body_y = (self.height - body_height) // 2
            eye_radius = int(body_width * 0.12)
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

        # Also offset body and wing polygons for visualization
        offset_body = [(x + position[0], y + position[1]) for x, y in self.body_points]
        offset_left_wing = [(x + position[0], y + position[1]) for x, y in self.left_wing_points]
        offset_right_wing = [(x + position[0], y + position[1]) for x, y in self.right_wing_points]

        return {
            'combined': offset_collision,
            'body': offset_body,
            'left_wing': offset_left_wing,
            'right_wing': offset_right_wing
        }