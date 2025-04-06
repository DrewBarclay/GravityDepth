import pygame
from typing import List, Dict, Type, Optional
from objects.game_object import GameObject
from engine.renderer import Renderer
from rain.rain_system import RainSystem
from objects.gravity_ball import GravityBallSystem
from objects.portal import Portal

class GameEngine:
    """Basic game engine for managing game objects and game state"""
    def __init__(self, width: int, height: int, title: str = "Game"):
        pygame.init()
        self.renderer = Renderer(width, height, title)
        self.clock = pygame.time.Clock()
        self.running = False
        self.game_objects: List[GameObject] = []
        self.last_time = 0

        # Initialize rain system
        self.rain_system = RainSystem(width, height)

        # Initialize gravity ball system
        self.gravity_ball_system = GravityBallSystem()

        # Mouse state variables
        self.mouse_pressed = False

        # Level management
        self.current_level = None
        self.font = pygame.font.SysFont('Arial', 24)

    def add_object(self, obj: GameObject) -> None:
        """Add a game object to the engine"""
        self.game_objects.append(obj)

    def remove_object(self, obj: GameObject) -> None:
        """Remove a game object from the engine"""
        if obj in self.game_objects:
            self.game_objects.remove(obj)

    def update(self, dt: float) -> None:
        """Update all game objects"""
        # Create a copy of the objects for iteration
        objects_to_process = self.game_objects.copy()

        # Check for player-portal collisions
        if self.current_level:
            player = self.current_level.player
            portal = self.current_level.portal

            if player and portal and portal.enabled and player.collides_with(portal):
                # Player has entered the portal, go to next level
                self.current_level.next_level()

            # Update level-specific logic
            self.current_level.update(dt)

        # Process removals and updates
        for obj in objects_to_process:
            if obj.marked_for_removal:
                self.remove_object(obj)
            else:
                obj.update(dt)

        # Update rain system
        self.rain_system.update(dt, self.game_objects)

        # Update gravity ball system
        self.gravity_ball_system.update(dt, self.game_objects + self.rain_system.raindrops)

    def draw(self) -> None:
        """Draw all game objects"""
        self.renderer.clear(self.renderer.colors['black'])

        # Draw game objects
        for obj in self.game_objects:
            obj.draw(self.renderer.get_screen())

        # Draw rain
        self.rain_system.draw(self.renderer.get_screen())

        # Draw gravity balls
        self.gravity_ball_system.draw(self.renderer.get_screen())

        # Draw level text in top right corner
        if self.current_level:
            level_text = f"{self.current_level.world_number}-{self.current_level.level_number}"
            text_surface = self.font.render(level_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(topright=(self.renderer.width - 20, 20))
            self.renderer.get_screen().blit(text_surface, text_rect)

            # Draw player health bar under the level indicator
            if self.current_level.player and hasattr(self.current_level.player, 'health'):
                player = self.current_level.player
                # Health bar background
                health_bar_width = 100
                health_bar_height = 20
                health_bar_x = self.renderer.width - 20 - health_bar_width
                health_bar_y = 50  # Position it under the level text

                # Draw background
                pygame.draw.rect(
                    self.renderer.get_screen(),
                    (100, 100, 100),  # Dark gray background
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height)
                )

                # Draw health bar (filled portion)
                health_percentage = player.health / player.max_health
                current_health_width = int(health_bar_width * health_percentage)

                # Color changes based on health: green > yellow > red
                if health_percentage > 0.6:
                    health_color = (0, 255, 0)  # Green
                elif health_percentage > 0.3:
                    health_color = (255, 255, 0)  # Yellow
                else:
                    health_color = (255, 0, 0)  # Red

                pygame.draw.rect(
                    self.renderer.get_screen(),
                    health_color,
                    (health_bar_x, health_bar_y, current_health_width, health_bar_height)
                )

                # Draw health text
                health_text = f"HP: {player.health}/{player.max_health}"
                health_text_surface = self.font.render(health_text, True, (255, 255, 255))
                health_text_rect = health_text_surface.get_rect(
                    center=(health_bar_x + health_bar_width//2, health_bar_y + health_bar_height//2)
                )
                self.renderer.get_screen().blit(health_text_surface, health_text_rect)

        self.renderer.update()

    def handle_events(self) -> bool:
        """Handle pygame events, return False if game should quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            # Handle mouse button events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.mouse_pressed = True
                    # Create a gravity ball at the mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.gravity_ball_system.create_gravity_ball(mouse_x, mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.mouse_pressed = False
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