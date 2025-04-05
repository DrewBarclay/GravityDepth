import pygame
from game_object import GameObject
from pygame.math import Vector2
import math

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
        self.color = (255, 165, 0)  # Orange color
        self.glow_color = (255, 100, 0, 100)  # Semi-transparent orange for glow effect

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
        super().update(dt)

        # Increment lifetime and mark for removal if expired
        self.lifetime += dt
        if self.lifetime >= self.lifespan:
            self.marked_for_removal = True

    def apply_gravity_to_object(self, obj: GameObject, dt: float) -> None:
        """Apply a gravitational attraction force to the given object if within range"""
        # Don't apply gravity to objects that are tied/stuck to other objects
        if hasattr(obj, 'tied_to') and obj.tied_to is not None:
            return

        # Calculate distance between this gravity ball and the object
        obj_pos = Vector2(obj.x + obj.width/2, obj.y + obj.height/2)
        ball_pos = Vector2(self.x + self.radius, self.y + self.radius)

        distance_vec = ball_pos - obj_pos
        distance = distance_vec.length()

        # Only apply force if within attraction radius
        if distance <= self.attraction_radius and distance > 0:
            # Calculate force direction (normalized)
            force_dir = distance_vec.normalize()

            # Inverse square law for gravity (stronger when closer)
            # We use (attraction_radius - distance) to make force stronger as objects get closer
            force_strength = self.attraction_force * (1 - (distance / self.attraction_radius)) * dt

            # Create the force vector
            force = force_dir * force_strength

            # Apply the force to the object
            obj.apply_force(force)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the gravity ball with a glow effect"""
        # Calculate alpha based on remaining lifetime (fade out effect)
        alpha = int(255 * (1 - (self.lifetime / self.lifespan)))

        # Draw attraction radius (semi-transparent circle)
        glow_surf = pygame.Surface((self.attraction_radius * 2, self.attraction_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (self.glow_color[0], self.glow_color[1], self.glow_color[2],
                                      min(self.glow_color[3], alpha)),
                          (self.attraction_radius, self.attraction_radius), self.attraction_radius)

        # Draw the actual ball
        pygame.draw.circle(surface, self.color,
                          (int(self.x + self.radius), int(self.y + self.radius)),
                          self.radius)

        # Draw the glow
        surface.blit(glow_surf,
                    (int(self.x + self.radius - self.attraction_radius),
                     int(self.y + self.radius - self.attraction_radius)))


class GravityBallSystem:
    """System to manage gravity balls"""
    def __init__(self):
        self.gravity_balls = []

    def create_gravity_ball(self, x: float, y: float) -> GravityBall:
        """Create a new gravity ball at the specified position"""
        ball = GravityBall(x, y)
        self.gravity_balls.append(ball)
        return ball

    def update(self, dt: float, game_objects: list) -> None:
        """Update all gravity balls and apply gravity to objects"""
        for ball in self.gravity_balls[:]:  # Copy list to allow removal during iteration
            # Update the ball
            ball.update(dt)

            # If marked for removal, remove it
            if ball.marked_for_removal:
                self.gravity_balls.remove(ball)
                continue

            # Apply gravity to all game objects
            for obj in game_objects:
                # Skip applying gravity to other gravity balls
                if isinstance(obj, GravityBall):
                    continue

                ball.apply_gravity_to_object(obj, dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all gravity balls"""
        for ball in self.gravity_balls:
            ball.draw(surface)