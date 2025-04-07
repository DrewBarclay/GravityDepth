import pygame
from objects.game_object import GameObject
from pygame.math import Vector2
import math
import random

class GravityBall(GameObject):
    """A gravity ball that attracts nearby rain and the player"""
    def __init__(self, x: float, y: float, radius: float = 10, attraction_radius: float = 100, lifespan: float = 2.0):
        super().__init__(x, y, radius * 2, radius * 2)
        self.radius = radius
        self.attraction_radius = attraction_radius
        self.lifespan = lifespan
        self.lifetime = 0
        self.attraction_force = 500  # Force magnitude
        self.marked_for_removal = False
        self.color = (0, 180, 0)  # Green color
        self.glow_color = (255, 100, 0, 100)  # Semi-transparent orange for glow effect
        self.rune_type = random.randint(0, 3)  # Random rune design (0-3)

        # Create a circular collision polygon
        self.create_circle_collision()

    def create_circle_collision(self):
        """Create a circular collision polygon"""
        num_points = 12  # Number of points to approximate circle
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            points.append((x, y))
        self.set_collision_polygon(points)

    def update(self, dt: float) -> None:
        """Update gravity ball lifetime"""
        # Prevent divide by zero
        if dt <= 0:
            return

        super().update(dt)

        # Increment lifetime and mark for removal if expired
        self.lifetime += dt
        if self.lifetime >= self.lifespan:
            self.marked_for_removal = True

        # Apply wall bouncing if the gravity ball has screen dimensions
        if hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
            self.bounce_off_walls(self.screen_width, self.screen_height)

    def apply_gravity_to_object(self, obj: GameObject, dt: float) -> None:
        """Apply gravitational attraction to an object within range by modifying its velocity directly."""
        # Skip objects that are tied to something else
        if hasattr(obj, 'tied_to') and obj.tied_to is not None:
            return

        # Skip applying gravity to enemies (only affect their projectiles)
        if hasattr(obj, 'is_enemy') and obj.is_enemy:
            return

        # Calculate centers and boundaries
        obj_center = Vector2(obj.x + obj.width/2, obj.y + obj.height/2)
        ball_center = Vector2(self.x + self.radius, self.y + self.radius)

        # Check if the object is within the attraction field using a better distance metric
        is_in_range = False

        # First, calculate center-to-center distance
        direction = ball_center - obj_center
        center_distance = direction.length()

        # If center is within range, object is definitely in range
        if center_distance <= self.attraction_radius:
            is_in_range = True
        else:
            # If center is outside but we might have partial overlap, do a more detailed check
            # Create a larger rect representing the attraction area
            attraction_area_rect = pygame.Rect(
                self.x + self.radius - self.attraction_radius,
                self.y + self.radius - self.attraction_radius,
                self.attraction_radius * 2,
                self.attraction_radius * 2
            )

            # Check if object's rect intersects with attraction area
            obj_rect = obj.get_rect()
            if attraction_area_rect.colliderect(obj_rect):
                # For more precise check, find closest point on object to ball center
                # Clamp ball_center to the bounds of obj_rect
                closest_x = max(obj_rect.left, min(ball_center.x, obj_rect.right))
                closest_y = max(obj_rect.top, min(ball_center.y, obj_rect.bottom))
                closest_point = Vector2(closest_x, closest_y)

                # Check if this closest point is within attraction radius
                distance_to_closest = (ball_center - closest_point).length()
                is_in_range = distance_to_closest <= self.attraction_radius

        # Only apply attraction if in range
        if is_in_range:
            # Set the object's gravity field flag if it has one
            if hasattr(obj, 'in_gravity_field'):
                obj.in_gravity_field = True

            # Use the center-to-center vector for direction of pull
            if center_distance > 0:  # Avoid division by zero
                direction = direction.normalize()

                # Calculate force strength with a modified gravity model
                strength = self.attraction_force * dt

                # Apply attraction directly to velocity
                obj.velocity += direction * strength

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the gravity ball with a glow effect and green rune"""
        # Calculate alpha based on remaining lifetime (fade out effect)
        alpha = int(255 * (1 - (self.lifetime / self.lifespan)))

        # Center point for drawing
        center_x = int(self.x + self.radius)
        center_y = int(self.y + self.radius)

        # Draw dotted green boundary for attraction radius
        green_boundary_color = (0, 200, 0, min(200, alpha))
        boundary_dots = 40  # Number of dots in the attraction radius boundary
        for i in range(boundary_dots):
            angle = 2 * math.pi * i / boundary_dots
            dot_x = center_x + int(self.attraction_radius * math.cos(angle))
            dot_y = center_y + int(self.attraction_radius * math.sin(angle))

            # Create a small surface for the semi-transparent dot
            dot_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, green_boundary_color, (2, 2), 2)
            surface.blit(dot_surf, (dot_x - 2, dot_y - 2))

        # Draw dotted green border for the ball itself
        green_border_color = (0, 200, 0)
        dots = 20  # Number of dots in the circle
        for i in range(dots):
            angle = 2 * math.pi * i / dots
            dot_x = center_x + int(self.radius * math.cos(angle))
            dot_y = center_y + int(self.radius * math.sin(angle))
            pygame.draw.circle(surface, green_border_color, (dot_x, dot_y), 2)

        # Draw the rune based on the type
        inner_radius = self.radius * 0.7

        if self.rune_type == 0:
            # Rune type 0: Cross with circle
            pygame.draw.line(surface, self.color,
                            (center_x - inner_radius, center_y),
                            (center_x + inner_radius, center_y), 2)
            pygame.draw.line(surface, self.color,
                            (center_x, center_y - inner_radius),
                            (center_x, center_y + inner_radius), 2)
            pygame.draw.circle(surface, self.color, (center_x, center_y), int(inner_radius * 0.5), 1)

        elif self.rune_type == 1:
            # Rune type 1: Triangle
            pygame.draw.polygon(surface, self.color, [
                (center_x, center_y - inner_radius),
                (center_x - inner_radius * 0.866, center_y + inner_radius * 0.5),
                (center_x + inner_radius * 0.866, center_y + inner_radius * 0.5)
            ], 2)

        elif self.rune_type == 2:
            # Rune type 2: Square with diagonals
            pygame.draw.rect(surface, self.color,
                            (center_x - inner_radius * 0.7, center_y - inner_radius * 0.7,
                             inner_radius * 1.4, inner_radius * 1.4), 2)
            pygame.draw.line(surface, self.color,
                            (center_x - inner_radius * 0.7, center_y - inner_radius * 0.7),
                            (center_x + inner_radius * 0.7, center_y + inner_radius * 0.7), 1)
            pygame.draw.line(surface, self.color,
                            (center_x + inner_radius * 0.7, center_y - inner_radius * 0.7),
                            (center_x - inner_radius * 0.7, center_y + inner_radius * 0.7), 1)

        else:
            # Rune type 3: Circle with inner star
            pygame.draw.circle(surface, self.color, (center_x, center_y), int(inner_radius * 0.8), 1)
            points = 5  # Five-pointed star
            for i in range(points * 2):
                angle = math.pi/2 + 2 * math.pi * i / (points * 2)
                radius = inner_radius * (0.4 if i % 2 == 0 else 0.7)
                point_x = center_x + int(radius * math.cos(angle))
                point_y = center_y + int(radius * math.sin(angle))

                if i == 0:
                    last_point = (point_x, point_y)
                else:
                    pygame.draw.line(surface, self.color, last_point, (point_x, point_y), 1)
                    last_point = (point_x, point_y)

            # Connect last point to first
            first_angle = math.pi/2
            first_x = center_x + int(inner_radius * 0.4 * math.cos(first_angle))
            first_y = center_y + int(inner_radius * 0.4 * math.sin(first_angle))
            pygame.draw.line(surface, self.color, last_point, (first_x, first_y), 1)


class GravityBallSystem:
    """System to manage gravity balls"""
    def __init__(self):
        self.gravity_balls = []

    def create_gravity_ball(self, x: float, y: float) -> GravityBall:
        """Create a new gravity ball at the specified position"""
        ball = GravityBall(x, y)
        self.gravity_balls.append(ball)
        return ball

    def collect_all_projectiles(self, objects: list) -> list:
        """Collect projectiles from all entities with projectiles"""
        projectiles = []

        for obj in objects:
            # Check if this is an object with projectiles (like Bat)
            if hasattr(obj, 'projectiles'):
                projectiles.extend(obj.projectiles)

        return projectiles

    def update(self, dt: float, game_objects: list) -> None:
        """Update all gravity balls and apply gravity to objects"""
        # Prevent divide by zero
        if dt <= 0:
            return

        # Collect projectiles from bats or other entities
        projectiles = self.collect_all_projectiles(game_objects)

        # Add projectiles to game objects for gravity processing
        all_objects = game_objects + projectiles

        for ball in self.gravity_balls[:]:  # Copy list to allow removal during iteration
            # Update the ball
            ball.update(dt)

            # If marked for removal, remove it
            if ball.marked_for_removal:
                self.gravity_balls.remove(ball)
                continue

            # Apply gravity to all game objects
            for obj in all_objects:
                # Skip applying gravity to other gravity balls
                if isinstance(obj, GravityBall):
                    continue

                ball.apply_gravity_to_object(obj, dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all gravity balls"""
        for ball in self.gravity_balls:
            ball.draw(surface)