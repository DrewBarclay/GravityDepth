import pytest
import pygame
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def pygame_init():
    """Initialize pygame for all tests"""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def mock_surface():
    """Create a mock pygame surface"""
    return MagicMock(spec=pygame.Surface)

@pytest.fixture
def mock_renderer(mock_surface):
    """Create a mock renderer"""
    renderer = MagicMock()
    renderer.width = 800
    renderer.height = 600
    renderer.screen = mock_surface
    renderer.get_screen.return_value = mock_surface
    renderer.get_dimensions.return_value = (800, 600)
    return renderer

@pytest.fixture
def mock_keys():
    """Create a mock key state dictionary"""
    return {
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False
    }