from game_object import GameObject
from pygame.math import Vector2
import random
import pygame

class RainDrop(GameObject):
    def __init__(self, x, y, wind_force=0):
        # Initialize with width=1 and height=length (will be set after super().__init__)
        super().__init__(x, y, width=1, height=1)
        # Base velocity (falling down and slightly right)
        self.velocity = Vector2(wind_force, 5.0)  # 5.0 is base fall speed
        self.acceleration = Vector2(0, 0.5)  # Gravity effect
        self.max_speed = 15.0  # Terminal velocity
        self.length = random.uniform(5, 15)  # Varying lengths for visual interest
        self.width = 1
        self.color = (255, 0, 0)  # Red color as requested
        self.deflection_force = 2.0  # How strongly raindrops are deflected
        self.lifetime = random.uniform(2, 5)  # How long the raindrop lives
        self.age = 0
        self.marked_for_removal = False

    def update(self, dt):
        # Update position using parent class update
        super().update(dt)

        # Apply acceleration
        self.velocity += self.acceleration * dt

        # Limit speed
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        # Age the raindrop
        self.age += dt
        if self.age >= self.lifetime:
            self.marked_for_removal = True

    def handle_collision(self, other):
        # Calculate deflection direction (away from the other object)
        other_pos = Vector2(other.x, other.y)
        my_pos = Vector2(self.x, self.y)
        deflection_dir = (my_pos - other_pos).normalize()

        # Apply deflection force
        self.velocity += deflection_dir * self.deflection_force

        # Ensure we don't exceed max speed after deflection
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

    def draw(self, surface):
        # Draw a line representing the raindrop
        start_pos = Vector2(self.x, self.y)
        end_pos = start_pos + self.velocity.normalize() * self.length
        pygame.draw.line(surface, self.color,
                        (int(start_pos.x), int(start_pos.y)),
                        (int(end_pos.x), int(end_pos.y)),
                        self.width)