import pytest
from pygame.math import Vector2
from rain_drop import RainDrop
from rain_system import RainSystem
from game_object import GameObject
from game import Player
import pygame

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
    assert raindrop.velocity.y == 5.0  # Base fall speed
    assert raindrop.velocity.x == 0.0  # No initial wind
    assert raindrop.acceleration == Vector2(0, 0.5)
    assert raindrop.max_speed == 15.0
    assert raindrop.color == (255, 0, 0)
    assert raindrop.width == 1
    assert 5 <= raindrop.length <= 15
    assert 2 <= raindrop.lifetime <= 5
    assert raindrop.age == 0
    assert not raindrop.marked_for_removal
    assert hasattr(raindrop, 'draw')

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
    assert raindrop.age == 1.0

def test_raindrop_max_speed(raindrop):
    # Update for enough time to exceed max speed
    raindrop.update(30.0)

    # Velocity should be capped at max_speed
    assert raindrop.velocity.length() <= raindrop.max_speed

def test_raindrop_lifetime(raindrop):
    # Update past lifetime
    raindrop.update(raindrop.lifetime + 0.1)

    assert raindrop.marked_for_removal

def test_raindrop_collision(raindrop):
    other = TestGameObject(120, 100)  # Place the other object slightly to the right
    initial_velocity = raindrop.velocity.copy()

    raindrop.handle_collision(other)

    # Velocity should change due to deflection
    assert raindrop.velocity != initial_velocity
    assert raindrop.velocity.length() <= raindrop.max_speed

def test_rain_system_initialization(rain_system):
    assert rain_system.screen_width == 800
    assert rain_system.screen_height == 600
    assert rain_system.spawn_rate == 50
    assert rain_system.wind_force == 0
    assert rain_system.spawn_timer == 0
    assert len(rain_system.raindrops) == 0

def test_rain_system_spawn(rain_system):
    initial_count = len(rain_system.raindrops)

    # Update for enough time to spawn at least one raindrop
    rain_system.update(0.1, [])

    assert len(rain_system.raindrops) > initial_count

def test_rain_system_wind(rain_system):
    # Set wind force
    wind_force = 2.0
    rain_system.set_wind_force(wind_force)

    assert rain_system.wind_force == wind_force

    # Spawn a new raindrop
    rain_system.spawn_raindrop()

    # Check that the new raindrop has the correct wind force
    assert rain_system.raindrops[-1].velocity.x == wind_force

def test_rain_system_cleanup(rain_system):
    # Add a raindrop that's out of bounds
    raindrop = RainDrop(-100, -100)
    rain_system.raindrops.append(raindrop)

    # Update the system
    rain_system.update(0.1, [])

    # The out-of-bounds raindrop should be removed
    assert raindrop not in rain_system.raindrops

def test_rain_system_with_player(rain_system, player):
    """Integration test with player interaction"""
    # Add a raindrop directly above the player
    raindrop = RainDrop(player.x, player.y - 10)
    rain_system.raindrops.append(raindrop)

    # Update the system with the player
    rain_system.update(0.1, [player])

    # Verify collision was detected and handled
    assert raindrop.velocity != Vector2(0, 5.0)  # Velocity should have changed
    assert raindrop.velocity.length() <= raindrop.max_speed

def test_raindrop_draw(raindrop):
    """Test raindrop drawing"""
    # Create a surface to draw on
    surface = pygame.Surface((200, 200))

    # Ensure draw method exists and can be called
    assert hasattr(raindrop, 'draw')
    raindrop.draw(surface)

    # Get the color at the raindrop's position
    color = surface.get_at((100, 100))[:3]  # Ignore alpha channel
    assert color == raindrop.color

def test_rain_system_draw(rain_system):
    """Test rain system drawing"""
    # Create a surface to draw on
    surface = pygame.Surface((800, 600))

    # Add a raindrop and draw
    rain_system.spawn_raindrop()
    rain_system.draw(surface)

    # Verify the system can draw without errors
    assert len(rain_system.raindrops) > 0