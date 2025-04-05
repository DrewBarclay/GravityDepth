import pygame
from typing import List, Dict, Type, Optional
from game_object import GameObject
from renderer import Renderer

class GameEngine:
    """Basic game engine for managing game objects and game state"""
    def __init__(self, width: int, height: int, title: str = "Game"):
        pygame.init()
        self.renderer = Renderer(width, height, title)
        self.clock = pygame.time.Clock()
        self.running = False
        self.game_objects: List[GameObject] = []
        self.last_time = 0

    def add_object(self, obj: GameObject) -> None:
        """Add a game object to the engine"""
        self.game_objects.append(obj)

    def remove_object(self, obj: GameObject) -> None:
        """Remove a game object from the engine"""
        if obj in self.game_objects:
            self.game_objects.remove(obj)

    def update(self, dt: float) -> None:
        """Update all game objects"""
        for obj in self.game_objects:
            obj.update(dt)

    def draw(self) -> None:
        """Draw all game objects"""
        self.renderer.clear()
        self.renderer.draw_game_objects(self.game_objects)
        self.renderer.update()

    def handle_events(self) -> bool:
        """Handle pygame events, return False if game should quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def handle_input(self) -> None:
        """Handle input for all game objects"""
        keys = pygame.key.get_pressed()
        for obj in self.game_objects:
            if hasattr(obj, 'handle_input'):
                obj.handle_input(keys)

    def run(self) -> None:
        """Main game loop"""
        self.running = True
        self.last_time = pygame.time.get_ticks()

        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
            self.last_time = current_time

            # Handle events
            self.running = self.handle_events()

            # Handle input
            self.handle_input()

            # Update game state
            self.update(dt)

            # Draw everything
            self.draw()

            # Cap the frame rate
            self.clock.tick(60)

        pygame.quit()

    def get_screen(self) -> pygame.Surface:
        """Get the game screen surface"""
        return self.renderer.get_screen()

    def get_dimensions(self) -> tuple[int, int]:
        """Get the game window dimensions"""
        return self.renderer.get_dimensions()