import pytest
import pygame
from pygame.math import Vector2
from game import Player

@pytest.fixture
def player():
    return Player(100, 100)

def test_initialization(player):
    """Test player initialization"""
    assert player.x == 100
    assert player.y == 100
    assert player.width == 50
    assert player.height == 50
    assert player.movement_speed == 300
    assert player.get_property('type') == 'player'
    assert player.marked_for_removal is False
    assert player.color == (0, 0, 255)
    assert hasattr(player, 'draw')

def test_input_handling(player):
    """Test player input handling"""
    # Create a mock keys dictionary with pygame key constants
    mock_keys = {
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False
    }

    # Test no movement when no keys pressed
    player.handle_input(mock_keys)
    assert player.acceleration.x == 0
    assert player.acceleration.y == 0

    # Test left movement
    mock_keys[pygame.K_LEFT] = True
    player.handle_input(mock_keys)
    assert player.acceleration.x == -player.movement_speed
    assert player.acceleration.y == 0

    # Test right movement
    mock_keys[pygame.K_LEFT] = False
    mock_keys[pygame.K_RIGHT] = True
    player.handle_input(mock_keys)
    assert player.acceleration.x == player.movement_speed
    assert player.acceleration.y == 0

    # Test up movement
    mock_keys[pygame.K_RIGHT] = False
    mock_keys[pygame.K_UP] = True
    player.handle_input(mock_keys)
    assert player.acceleration.x == 0
    assert player.acceleration.y == -player.movement_speed

    # Test down movement
    mock_keys[pygame.K_UP] = False
    mock_keys[pygame.K_DOWN] = True
    player.handle_input(mock_keys)
    assert player.acceleration.x == 0
    assert player.acceleration.y == player.movement_speed

    # Test diagonal movement
    mock_keys[pygame.K_RIGHT] = True
    mock_keys[pygame.K_DOWN] = True
    player.handle_input(mock_keys)
    assert player.acceleration.x == player.movement_speed
    assert player.acceleration.y == player.movement_speed

def test_movement_physics(player):
    """Test player movement physics"""
    # Apply movement and update
    player.acceleration = Vector2(player.movement_speed, 0)
    player.update(1.0)  # Update for 1 second

    # Check that velocity was affected by acceleration
    assert player.velocity.x == player.movement_speed
    assert player.velocity.y == 0

    # Check that position was affected by velocity
    assert player.x == 100 + player.movement_speed
    assert player.y == 100

    # Acceleration remains until we explicitly reset it - just check it exists
    assert hasattr(player, 'acceleration')
    assert isinstance(player.acceleration, Vector2)

def test_draw(player):
    """Test player drawing"""
    surface = pygame.Surface((200, 200))
    player.draw(surface)
    color = surface.get_at((100, 100))[:3]  # Ignore alpha channel
    assert color == player.color