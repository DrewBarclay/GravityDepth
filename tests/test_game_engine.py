import pytest
import pygame
from unittest.mock import MagicMock, patch
from engine.game_engine import GameEngine
from objects.game_object import GameObject
from engine.renderer import Renderer
from objects.level import Level

# Mock for pygame modules
@pytest.fixture(autouse=True)
def setup_pygame_mock(monkeypatch):
    # Create a mock for pygame.Surface
    surface_mock = MagicMock()

    # Create a mock for pygame.display
    display_mock = MagicMock()
    display_mock.set_mode.return_value = surface_mock
    display_mock.set_caption = MagicMock()

    # Create a mock for pygame.time.Clock
    clock_mock = MagicMock()

    # Patch pygame modules
    monkeypatch.setattr("pygame.init", MagicMock())
    monkeypatch.setattr("pygame.display", display_mock)
    monkeypatch.setattr("pygame.Surface", MagicMock(return_value=surface_mock))
    monkeypatch.setattr("pygame.time.Clock", MagicMock(return_value=clock_mock))
    monkeypatch.setattr("pygame.font.SysFont", MagicMock())
    monkeypatch.setattr("pygame.draw", MagicMock())

# Mock Vector2 class that matches pygame.math.Vector2
class MockVector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, MockVector2):
            return MockVector2(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, MockVector2):
            return MockVector2(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, scalar):
        return MockVector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __eq__(self, other):
        if isinstance(other, MockVector2):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def length(self):
        return (self.x**2 + self.y**2)**0.5

    def normalize(self):
        length = self.length()
        if length > 0:
            return MockVector2(self.x / length, self.y / length)
        return MockVector2()

    def copy(self):
        return MockVector2(self.x, self.y)

# Mock Rect class that matches pygame.Rect
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
    """A test game object for input handling tests"""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.input_handled = False

    def handle_input(self, keys):
        self.input_handled = True

@pytest.fixture
def engine():
    """Create a mock game engine"""
    with patch('pygame.math.Vector2', MockVector2), \
         patch('pygame.Rect', MockRect):
        engine = GameEngine(800, 600, "Test Game")
        return engine

@pytest.fixture
def test_obj():
    """Create a test game object"""
    return TestGameObject(100, 100, 10, 10)

def test_init():
    """Test game engine initialization"""
    engine = GameEngine(800, 600, "Test Window")
    assert engine.renderer is not None
    assert engine.clock is not None
    assert engine.running is False
    assert len(engine.game_objects) == 0

def test_add_remove_object():
    """Test adding and removing game objects"""
    engine = GameEngine(800, 600, "Test Window")

    # Create a test object
    obj = GameObject(0, 0, 10, 10)

    # Add the object
    engine.add_object(obj)
    assert obj in engine.game_objects

    # Remove the object
    engine.remove_object(obj)
    assert obj not in engine.game_objects

def test_handle_input():
    """Test input handling for game objects"""
    engine = GameEngine(800, 600, "Test Window")

    # Create a test object with input handling
    obj = TestGameObject(0, 0, 10, 10)

    # Add the object
    engine.add_object(obj)

    # Handle input
    engine.handle_input()

    # Verify input was handled
    assert obj.input_handled

def test_renderer_api():
    """Test renderer API calls from game engine"""
    # Create a mock renderer
    renderer_mock = MagicMock()
    renderer_mock.get_screen.return_value = MagicMock()
    renderer_mock.get_dimensions.return_value = (640, 480)

    # Patch the Renderer class
    with patch('engine.game_engine.Renderer', return_value=renderer_mock):
        # Create engine with mocked renderer
        engine = GameEngine(640, 480, "Test")

        # Test get_screen API
        screen = engine.get_screen()
        assert screen is not None
        assert renderer_mock.get_screen.called

        # Test get_dimensions API
        width, height = engine.get_dimensions()
        assert width == 640
        assert height == 480

@patch('objects.level.Level')
def test_game_over_state(MockLevel):
    """Test that game over state is correctly set when player dies"""
    # Set up mocks
    mock_player = MagicMock()
    mock_player.marked_for_removal = False

    mock_level = MagicMock()
    mock_level.player = mock_player
    MockLevel.return_value = mock_level

    # Create engine with mocked level
    engine = GameEngine(800, 600, "Test Window")
    engine.current_level = mock_level

    # Ensure game is not over initially
    assert not engine.game_over

    # Mark player for removal (death)
    mock_player.marked_for_removal = True

    # Update the engine to detect player death
    engine.update(0.1)

    # Game should now be over
    assert engine.game_over

@patch('objects.level.Level')
def test_restart_game(MockLevel):
    """Test that restart_game resets the game state properly"""
    # Set up mocks
    mock_level = MagicMock()
    mock_level.world_number = 2
    mock_level.level_number = 3
    MockLevel.return_value = mock_level

    # Create engine with mocked level
    engine = GameEngine(800, 600, "Test Window")
    engine.current_level = mock_level

    # Set game over
    engine.game_over = True

    # Restart game
    engine.restart_game()

    # Verify game state is reset
    assert not engine.game_over

    # Verify level was reset
    assert mock_level.world_number == 1
    assert mock_level.level_number == 1
    assert mock_level.setup_level.called