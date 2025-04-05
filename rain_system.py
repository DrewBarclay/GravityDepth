from rain_drop import RainDrop
import random
import pygame

class RainSystem:
    def __init__(self, screen_width, screen_height, spawn_rate=50, wind_force=0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_rate = spawn_rate  # raindrops per second
        self.wind_force = wind_force
        self.spawn_timer = 0
        self.raindrops = []

    def update(self, dt, game_objects):
        # Spawn new raindrops
        self.spawn_timer += dt
        while self.spawn_timer >= 1.0 / self.spawn_rate:
            self.spawn_raindrop()
            self.spawn_timer -= 1.0 / self.spawn_rate

        # Update existing raindrops
        for raindrop in self.raindrops[:]:  # Copy list to allow removal during iteration
            raindrop.update(dt)

            # Check collisions with other game objects
            for obj in game_objects:
                if obj != raindrop and raindrop.collides_with(obj):
                    raindrop.handle_collision(obj)

            # Remove raindrops that are marked for removal or out of bounds
            if (raindrop.marked_for_removal or
                raindrop.y > self.screen_height + 50 or
                raindrop.x < -50 or
                raindrop.x > self.screen_width + 50):
                self.raindrops.remove(raindrop)

    def spawn_raindrop(self):
        # Spawn raindrops across the top of the screen with some random offset
        x = random.uniform(-50, self.screen_width + 50)
        y = random.uniform(-50, 0)
        raindrop = RainDrop(x, y, self.wind_force)
        self.raindrops.append(raindrop)

    def draw(self, surface):
        for raindrop in self.raindrops:
            raindrop.draw(surface)

    def set_wind_force(self, force):
        """Update wind force for all existing and new raindrops"""
        self.wind_force = force
        for raindrop in self.raindrops:
            raindrop.velocity.x = force