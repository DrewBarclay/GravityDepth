from rain_drop import RainDrop
import random
import pygame
from pygame.math import Vector2

class RainSystem:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.raindrops = []
        self.spawn_rate = 70  # Increased spawn rate
        self.spawn_timer = 0
        self.wind_force = 0
        self.wind_change_timer = 0
        self.wind_change_interval = 1.0  # Faster wind changes (was 2.0)
        self.max_wind_force = 10.0  # Stronger maximum wind (was 3.0)
        self.min_wind_force = -10.0  # Stronger minimum wind (was -3.0)
        self.target_wind = 0  # Target wind force to drift toward
        self.wind_change_speed = 0.2  # How quickly wind changes (was 0.1)

    def update(self, dt: float, game_objects: list) -> None:
        # Update wind force
        self.update_wind(dt)

        # Update spawn timer
        self.spawn_timer += dt
        if self.spawn_timer >= 1.0 / self.spawn_rate:
            self.spawn_timer = 0
            self.spawn_raindrop()

        # Update all raindrops
        for raindrop in self.raindrops:
            # Apply wind as an acceleration, not direct velocity
            raindrop.wind_acceleration = Vector2(self.wind_force * 10, 0)  # Scale wind for better effect

            # Update raindrop
            raindrop.update(dt)

            # Check for collisions with game objects
            raindrop.check_and_handle_collisions(game_objects, dt)

            # Mark for removal if below screen
            if raindrop.y > self.screen_height:
                raindrop.marked_for_removal = True

        # Remove marked raindrops
        self.raindrops = [r for r in self.raindrops if not r.marked_for_removal]

    def spawn_raindrop(self) -> None:
        # Spawn across a wider area to account for stronger wind
        x = random.randint(-100, self.screen_width + 100)
        raindrop = RainDrop(x, -20)
        # Give each new raindrop some initial wind variation
        raindrop.velocity.x = self.wind_force + random.uniform(-2.0, 2.0)
        self.raindrops.append(raindrop)

    def draw(self, surface: pygame.Surface) -> None:
        for raindrop in self.raindrops:
            raindrop.draw(surface)

    def set_wind_force(self, force):
        """Update wind force for all existing and new raindrops"""
        self.wind_force = force
        for raindrop in self.raindrops:
            raindrop.velocity.x = force

    def update_wind(self, dt: float) -> None:
        # Update wind direction
        self.wind_change_timer += dt
        if self.wind_change_timer >= self.wind_change_interval:
            self.wind_change_timer = 0
            # Set a new random target for wind
            self.target_wind = random.uniform(self.min_wind_force, self.max_wind_force)

        # Gradually change wind force towards the target (smoother transitions)
        self.wind_force += (self.target_wind - self.wind_force) * self.wind_change_speed * dt