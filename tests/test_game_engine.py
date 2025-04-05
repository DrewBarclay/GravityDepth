import pytest
import pygame
from unittest.mock import MagicMock, patch
from game_engine import GameEngine
from game_object import GameObject
from renderer import Renderer

# Mock pygame modules
class MockVector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return MockVector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return MockVector2(self.x * scalar, self.y * scalar)

class MockRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def colliderect(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

# Patch pygame modules
@pytest.fixture(autouse=True)
def mock_pygame():
    with patch('pygame.math.Vector2', MockVector2), \
         patch('pygame.Rect', MockRect), \
         patch('pygame.init'), \
         patch('pygame.quit'), \
         patch('pygame.time.Clock'), \
         patch('pygame.time.get_ticks', return_value=0), \
         patch('pygame.event.get', return_value=[]), \
         patch('pygame.key.get_pressed', return_value={}), \
         patch('pygame.display.set_mode'), \
         patch('pygame.display.set_caption'), \
         patch('pygame.display.flip'):
        yield

class MockRenderer:
    """Mock renderer for testing"""
    def __init__(self, width=800, height=600, title="Test"):
        self.width = width
        self.height = height
        self.title = title
        self.clear_called = False
        self.draw_called = False
        self.update_called = False
        self.screen = pygame.Surface((width, height))

    def clear(self):
        self.clear_called = True

    def draw_game_objects(self, objects):
        self.draw_called = True

    def update(self):
        self.update_called = True

    def get_screen(self):
        self.draw_called = True  # Drawing happens when getting the screen
        return self.screen

    def get_dimensions(self):
        return (self.width, self.height)

class TestGameObject(GameObject):
    """Test game object for testing"""
    def __init__(self, x=0, y=0):
        super().__init__(x, y, width=10, height=10)
        self.update_called = False
        self.draw_called = False
        self.marked_for_removal = False

    def update(self, dt):
        self.update_called = True

    def draw(self, surface):
        self.draw_called = True

@pytest.fixture
def engine():
    """Create a game engine for testing"""
    engine = GameEngine(800, 600, "Test")
    engine.renderer = MockRenderer()
    return engine

@pytest.fixture
def test_obj():
    """Create a test game object"""
    return TestGameObject()

def test_initialization(engine):
    """Test engine initialization"""
    assert engine.renderer is not None
    assert not engine.running
    assert len(engine.game_objects) == 0

def test_add_object(engine, test_obj):
    """Test adding game objects"""
    engine.add_object(test_obj)
    assert test_obj in engine.game_objects

def test_remove_object(engine, test_obj):
    """Test removing game objects"""
    engine.add_object(test_obj)
    engine.remove_object(test_obj)
    assert test_obj not in engine.game_objects

def test_update(engine, test_obj):
    """Test game object updates"""
    engine.add_object(test_obj)
    assert not test_obj.update_called
    engine.update(1/60)
    assert test_obj.update_called

def test_draw(engine):
    """Test drawing calls"""
    engine.draw()
    assert engine.renderer.clear_called
    assert engine.renderer.draw_called
    assert engine.renderer.update_called

def test_get_screen(engine):
    """Test getting screen surface"""
    assert isinstance(engine.get_screen(), pygame.Surface)

def test_get_dimensions(engine):
    """Test getting window dimensions"""
    width, height = engine.get_dimensions()
    assert width == 800
    assert height == 600