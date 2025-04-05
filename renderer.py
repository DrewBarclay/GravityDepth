import pygame
from typing import List, Dict, Any, Optional
from game_object import GameObject

class Renderer:
    """Handles all rendering logic for the game"""
    def __init__(self, width: int, height: int, title: str = "Game"):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        # Colors
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0)
        }

    def clear(self, color: Optional[tuple] = None) -> None:
        """Clear the screen with the specified color"""
        if color is None:
            color = self.colors['white']
        self.screen.fill(color)

    def draw_rect(self, rect: pygame.Rect, color: tuple) -> None:
        """Draw a rectangle on the screen"""
        pygame.draw.rect(self.screen, color, rect)

    def draw_circle(self, center: tuple, radius: int, color: tuple) -> None:
        """Draw a circle on the screen"""
        pygame.draw.circle(self.screen, color, center, radius)

    def draw_polygon(self, points: List[tuple], color: tuple) -> None:
        """Draw a polygon on the screen"""
        pygame.draw.polygon(self.screen, color, points)

    def draw_text(self, text: str, position: tuple, color: tuple,
                 font_size: int = 24, font_name: Optional[str] = None) -> None:
        """Draw text on the screen"""
        font = pygame.font.SysFont(font_name, font_size) if font_name else pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def draw_game_object(self, obj: GameObject, color: Optional[tuple] = None) -> None:
        """Draw a game object on the screen"""
        if color is None:
            color = self.colors['blue']
        self.draw_rect(obj.get_rect(), color)

    def draw_game_objects(self, objects: List[GameObject],
                         color_map: Optional[Dict[str, tuple]] = None) -> None:
        """Draw multiple game objects on the screen"""
        for obj in objects:
            color = None
            if color_map and obj.get_property('type') in color_map:
                color = color_map[obj.get_property('type')]
            self.draw_game_object(obj, color)

    def update(self) -> None:
        """Update the display"""
        pygame.display.flip()

    def get_screen(self) -> pygame.Surface:
        """Get the screen surface"""
        return self.screen

    def get_dimensions(self) -> tuple[int, int]:
        """Get the screen dimensions"""
        return (self.width, self.height)