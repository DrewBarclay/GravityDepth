import pytest
import pygame
from game_object import GameObject

@pytest.fixture
def game_object():
    """Create a test game object"""
    return GameObject(100, 100, 40, 40)

def test_initialization(game_object):
    """Test object initialization"""
    assert game_object.x == 100
    assert game_object.y == 100
    assert game_object.width == 40
    assert game_object.height == 40
    assert game_object.velocity.x == 0
    assert game_object.velocity.y == 0
    assert game_object.acceleration.x == 0
    assert game_object.acceleration.y == 0

def test_position_methods(game_object):
    """Test position getter and setter"""
    game_object.set_position(200, 300)
    x, y = game_object.get_position()
    assert x == 200
    assert y == 300

def test_properties(game_object):
    """Test property getter and setter"""
    game_object.set_property('health', 100)
    assert game_object.get_property('health') == 100
    assert game_object.get_property('nonexistent') is None
    assert game_object.get_property('nonexistent', 'default') == 'default'

def test_physics_update(game_object):
    """Test physics updates with velocity and acceleration"""
    # Set initial velocity
    game_object.velocity = pygame.math.Vector2(10, 20)

    # Update for 1 second
    game_object.update(1.0)

    # Position should change by velocity * time
    assert game_object.x == 110  # 100 + 10 * 1
    assert game_object.y == 120  # 100 + 20 * 1

    # Acceleration should affect velocity
    game_object.apply_force(pygame.math.Vector2(5, -5))
    game_object.update(1.0)

    # Velocity should be affected by acceleration
    assert game_object.velocity.x == 15  # 10 + 5 * 1
    assert game_object.velocity.y == 15  # 20 + -5 * 1

def test_collision_detection():
    """Test collision detection between objects"""
    obj1 = GameObject(0, 0, 50, 50)
    obj2 = GameObject(25, 25, 50, 50)  # Overlapping
    obj3 = GameObject(100, 100, 50, 50)  # Not overlapping

    assert obj1.collides_with(obj2)
    assert obj2.collides_with(obj1)
    assert not obj1.collides_with(obj3)
    assert not obj3.collides_with(obj1)

def test_rect_bounds(game_object):
    """Test rectangle bounds calculation"""
    rect = game_object.get_rect()
    assert rect.x == 100
    assert rect.y == 100
    assert rect.width == 40
    assert rect.height == 40