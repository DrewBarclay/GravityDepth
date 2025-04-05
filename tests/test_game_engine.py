import pytest
from unittest.mock import MagicMock, patch
from game_engine import GameEngine
from game_object import GameObject

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

class TestGameObject(GameObject):
    """Test game object that tracks update calls"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40, 40)
        self.update_called = False
        self.input_handled = False

    def update(self, dt: float) -> None:
        super().update(dt)
        self.update_called = True

    def handle_input(self, keys) -> None:
        self.input_handled = True

class MockRenderer:
    """Mock renderer for testing"""
    def __init__(self, width: int, height: int, title: str):
        self.width = width
        self.height = height
        self.screen = MagicMock()
        self.clear_called = False
        self.draw_called = False
        self.update_called = False

    def clear(self):
        self.clear_called = True

    def draw_game_objects(self, objects):
        self.draw_called = True

    def update(self):
        self.update_called = True

    def get_screen(self):
        return self.screen

    def get_dimensions(self):
        return (self.width, self.height)

@pytest.fixture
def engine():
    """Create a game engine with a mock renderer"""
    engine = GameEngine(800, 600, "Test Game")
    engine.renderer = MockRenderer(800, 600, "Test Game")
    return engine

@pytest.fixture
def test_obj():
    return TestGameObject(100, 100)

def test_initialization(engine):
    """Test engine initialization"""
    assert not engine.running
    assert len(engine.game_objects) == 0
    assert engine.get_dimensions() == (800, 600)

def test_object_management(engine, test_obj):
    """Test adding and removing objects"""
    # Add object
    engine.add_object(test_obj)
    assert len(engine.game_objects) == 1
    assert test_obj in engine.game_objects

    # Remove object
    engine.remove_object(test_obj)
    assert len(engine.game_objects) == 0
    assert test_obj not in engine.game_objects

def test_update(engine, test_obj):
    """Test game object updates"""
    engine.add_object(test_obj)
    assert not test_obj.update_called

    engine.update(1/60)
    assert test_obj.update_called

def test_handle_input(engine, test_obj):
    """Test input handling"""
    engine.add_object(test_obj)
    assert not test_obj.input_handled

    engine.handle_input()
    assert test_obj.input_handled

def test_draw(engine):
    """Test drawing calls"""
    engine.draw()

    # Verify that all rendering methods were called
    assert engine.renderer.clear_called
    assert engine.renderer.draw_called
    assert engine.renderer.update_called

def test_get_screen(engine):
    """Test getting the game screen"""
    screen = engine.get_screen()
    assert screen == engine.renderer.screen

def test_get_dimensions(engine):
    """Test getting game dimensions"""
    width, height = engine.get_dimensions()
    assert width == 800
    assert height == 600