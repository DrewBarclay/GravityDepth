import pygame
import math
from objects.game_object import GameObject
from typing import Tuple, List

class Portal(GameObject):
    """A portal that transports the player to the next level when collided with"""

    def __init__(self, x: float, y: float, width: float = 50, height: float = 50):
        super().__init__(x, y, width, height)
        self.marked_for_removal = False
        self.rotation = 0  # Current rotation angle for animation
        self.rotation_speed = 90  # Degrees per second
        self.color = (0, 0, 255)  # Start with blue color
        self.target_color = (0, 0, 255)  # Target color for transitions
        self.color_transition_speed = 5.0  # How fast color changes (units per second)
        self.spiral_points = self._generate_spiral_points()
        self.enabled = False  # Portal starts disabled

        # Set a circular collision area
        self._create_collision_polygon()

    def _create_collision_polygon(self):
        """Create a circular collision polygon"""
        num_points = 12  # Number of points to approximate circle
        radius = min(self.width, self.height) / 2
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = radius * math.cos(angle) + self.width / 2
            y = radius * math.sin(angle) + self.height / 2
            points.append((x, y))
        self.set_collision_polygon(points)

    def _generate_spiral_points(self) -> List[Tuple[float, float]]:
        """Generate points for a spiral"""
        points = []
        radius = min(self.width, self.height) / 2
        center_x = self.width / 2
        center_y = self.height / 2

        # Generate a spiral with 3 loops, 120 points
        loops = 3
        points_count = 120
        max_radius = radius * 0.9  # Slightly smaller than the full radius

        for i in range(points_count):
            # Calculate angle and radius for this point
            angle = 2 * math.pi * loops * i / points_count
            current_radius = max_radius * i / points_count

            # Convert to cartesian coordinates
            x = center_x + current_radius * math.cos(angle)
            y = center_y + current_radius * math.sin(angle)
            points.append((x, y))

        return points

    def enable(self):
        """Enable the portal, changing its color to red"""
        self.enabled = True
        self.target_color = (255, 0, 0)  # Red

    def progress_color(self, progress: float):
        """Update portal color based on enemy kill progress (0.0 to 1.0)"""
        # Interpolate between blue and red based on progress
        r = int(progress * 255)  # More red as progress increases
        g = 0
        b = int(255 * (1 - progress))  # Less blue as progress increases
        self.target_color = (r, g, b)

    def update(self, dt: float) -> None:
        """Update portal animation"""
        super().update(dt)

        # Update rotation for animation
        self.rotation += self.rotation_speed * dt
        if self.rotation >= 360:
            self.rotation -= 360

        # Gradually transition color toward target color
        for i in range(3):
            if self.color[i] < self.target_color[i]:
                self.color = tuple(
                    self.color[0:i] +
                    (min(self.color[i] + int(self.color_transition_speed * dt * 255), self.target_color[i]),) +
                    self.color[i+1:]
                )
            elif self.color[i] > self.target_color[i]:
                self.color = tuple(
                    self.color[0:i] +
                    (max(self.color[i] - int(self.color_transition_speed * dt * 255), self.target_color[i]),) +
                    self.color[i+1:]
                )

        # Apply wall bouncing if the portal has screen dimensions
        if hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
            self.bounce_off_walls(self.screen_width, self.screen_height)

    def collides_with(self, other: GameObject) -> bool:
        """Override collision to prevent collisions when disabled"""
        if not self.enabled:
            return False
        return super().collides_with(other)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the swirly portal"""
        # Create a surface for the portal
        portal_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw the spiral
        prev_point = None
        line_width = 3

        for i, point in enumerate(self.spiral_points):
            if prev_point:
                # Vary color intensity based on position in the spiral
                intensity = i / len(self.spiral_points)
                color = (int(self.color[0]),
                         int(self.color[1] * intensity),
                         int(self.color[2] * intensity),
                         255)

                pygame.draw.line(portal_surface, color, prev_point, point, line_width)
            prev_point = point

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(portal_surface, self.rotation)

        # Get the rect for the rotated surface to position it correctly
        rotated_rect = rotated_surface.get_rect(center=(self.width/2, self.height/2))

        # Draw a glow effect
        glow_radius = min(self.width, self.height) / 2 + 5
        glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 100), (self.width/2 + 5, self.height/2 + 5), glow_radius)

        # Blit the glow onto the main surface
        surface.blit(glow_surface, (self.x - 5, self.y - 5))

        # Blit the rotated spiral onto the main surface
        surface.blit(rotated_surface, (self.x + rotated_rect.x, self.y + rotated_rect.y))