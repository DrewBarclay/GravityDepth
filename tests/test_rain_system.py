import pytest
from pygame.math import Vector2
from rain_drop import RainDrop
from rain_system import RainSystem
from game_object import GameObject
from game import Player
import pygame
from raindrop_constants import (
    DEFAULT_VELOCITY_Y,
    GRAVITY_ACCELERATION,
    MAX_VELOCITY_MAGNITUDE,
    MAX_UPWARD_VELOCITY,
    DEFAULT_WIDTH,
    MIN_LENGTH,
    MAX_LENGTH,
    DEFAULT_COLOR,
    REPULSION_FORCE
)

class TestGameObject(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, width=20, height=20)
        self.marked_for_removal = False

@pytest.fixture
def raindrop():
    return RainDrop(100, 100)

@pytest.fixture
def rain_system():
    return RainSystem(800, 600)

@pytest.fixture
def player():
    return Player(400, 300)  # Center of screen

def test_raindrop_initialization(raindrop):
    assert raindrop.x == 100
    assert raindrop.y == 100
    assert raindrop.velocity.y == DEFAULT_VELOCITY_Y
    assert raindrop.velocity.x == 0.0  # No initial wind
    assert raindrop.acceleration == GRAVITY_ACCELERATION  # Much stronger gravity
    assert raindrop.max_upward_velocity < raindrop.max_velocity_magnitude  # Upward speed should be less than downward
    assert raindrop.color == DEFAULT_COLOR
    assert raindrop.width == DEFAULT_WIDTH
    assert MIN_LENGTH <= raindrop.length <= MAX_LENGTH
    assert not raindrop.marked_for_removal
    assert hasattr(raindrop, 'draw')
    assert hasattr(raindrop, 'check_and_handle_collisions')
    assert hasattr(raindrop, 'apply_repulsion_force')
    assert isinstance(raindrop.colliding_objects, set)
    assert raindrop.repulsion_force == REPULSION_FORCE

def test_raindrop_update(raindrop):
    initial_x = raindrop.x
    initial_y = raindrop.y
    initial_vel = raindrop.velocity.copy()

    # Update for 1 second
    raindrop.update(1.0)

    # Position should change based on velocity
    assert (raindrop.x != initial_x or raindrop.y != initial_y)
    assert raindrop.y > initial_y  # Should move down

    # Velocity should increase due to acceleration
    assert raindrop.velocity.y > initial_vel.y