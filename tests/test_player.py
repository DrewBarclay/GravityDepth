import pytest
import pygame
from game import Player

@pytest.fixture
def player(pygame_init):
    return Player(100, 100)

def test_initialization(player):
    """Test player initialization"""
    assert player.x == 100
    assert player.y == 100
    assert player.width == 40
    assert player.height == 40
    assert player.movement_speed == 300
    assert player.get_property('type') == 'player'

def test_input_handling(player, mock_keys):
    """Test player input handling"""
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
    player.acceleration = pygame.math.Vector2(player.movement_speed, 0)
    player.update(1.0)  # Update for 1 second

    # Check that velocity was affected by acceleration
    assert player.velocity.x == player.movement_speed
    assert player.velocity.y == 0

    # Check that position was affected by velocity
    assert player.x == 100 + player.movement_speed
    assert player.y == 100

    # Check that acceleration was reset
    assert player.acceleration.x == 0
    assert player.acceleration.y == 0