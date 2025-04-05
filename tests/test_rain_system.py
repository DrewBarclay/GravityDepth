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
    assert raindrop.velocity.y == 200.0
    assert raindrop.velocity.x == 0.0  # No initial wind
    assert raindrop.acceleration == Vector2(0, 8000.0)  # Much stronger gravity
    assert raindrop.max_upward_velocity < raindrop.max_velocity_magnitude  # Upward speed should be less than downward
    assert raindrop.color == (255, 0, 0)
    assert raindrop.width == 1
    assert 5 <= raindrop.length <= 15
    assert not raindrop.marked_for_removal
    assert hasattr(raindrop, 'draw')
    assert hasattr(raindrop, 'check_and_handle_collisions')
    assert hasattr(raindrop, 'apply_repulsion_force')
    assert isinstance(raindrop.colliding_objects, set)
    assert raindrop.repulsion_force >= raindrop.acceleration.y  # Repulsion should be at least as strong as gravity

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

def test_raindrop_max_speed(raindrop):
    """Test that velocity is properly capped based on direction"""
    # Test downward motion (higher speed cap)
    initial_velocity = raindrop.velocity.copy()
    # Apply a large force that would normally exceed the max speed
    force = Vector2(0, raindrop.max_velocity_magnitude * 2)

    # Test force limiting
    raindrop._limit_applied_force(force)

    # Apply the force
    raindrop.velocity += force

    # Velocity should be limited
    assert raindrop.velocity.length() <= raindrop.max_velocity_magnitude + 0.01  # Allow small floating point error

    # Reset and test upward motion
    raindrop.velocity = initial_velocity
    force = Vector2(0, -raindrop.max_velocity_magnitude * 2)

    # Test force limiting
    raindrop._limit_applied_force(force)

    # Apply the force
    raindrop.velocity += force

    # Velocity should be limited based on direction
    assert raindrop.velocity.length() <= raindrop.max_upward_velocity + 0.01  # Allow small floating point error

def test_raindrop_repulsion(raindrop):
    other = TestGameObject(120, 100)  # Place the other object slightly to the right
    initial_velocity = raindrop.velocity.copy()

    # Apply repulsion force
    raindrop.apply_repulsion_force(other, 0.1)

    # Velocity should change due to repulsion
    assert raindrop.velocity != initial_velocity
    assert raindrop.velocity.length() <= raindrop.max_velocity_magnitude + 0.01  # Allow small floating point error
    # Velocity should have a component pointing away from the object
    # Since the object is to the right, velocity should have negative x component
    assert raindrop.velocity.x < 0

def test_raindrop_collision_handling(raindrop):
    # Create a game object that overlaps with the raindrop
    # The raindrop is at (100, 100) with width=1 and some length
    overlapping_obj = TestGameObject(99, 99)  # This will definitely overlap
    game_objects = [overlapping_obj]
    initial_velocity = raindrop.velocity.copy()

    # Check and handle collisions
    raindrop.check_and_handle_collisions(game_objects, 0.1)

    # Should detect collision with the object
    assert len(raindrop.colliding_objects) == 1

    # Velocity should change from repulsion
    assert raindrop.velocity != initial_velocity

def test_rain_system_initialization(rain_system):
    assert rain_system.screen_width == 800
    assert rain_system.screen_height == 600
    assert rain_system.spawn_rate == 70  # Increased spawn rate
    assert rain_system.wind_force == 0
    assert rain_system.spawn_timer == 0
    assert len(rain_system.raindrops) == 0
    assert rain_system.wind_change_timer == 0
    assert rain_system.wind_change_interval == 1.0  # Faster changes
    assert rain_system.max_wind_force == 10.0  # Stronger wind
    assert rain_system.min_wind_force == -10.0  # Stronger wind
    assert rain_system.target_wind == 0
    assert rain_system.wind_change_speed == 0.2

def test_rain_system_spawn(rain_system):
    initial_count = len(rain_system.raindrops)

    # Update for enough time to spawn at least one raindrop
    rain_system.update(0.1, [])

    assert len(rain_system.raindrops) > initial_count
    # New raindrops should have some wind variation
    new_raindrop = rain_system.raindrops[0]
    assert -12.0 <= new_raindrop.velocity.x <= 12.0  # Account for randomness

def test_rain_system_wind_changes(rain_system):
    initial_wind = rain_system.wind_force

    # Update past the wind change interval
    rain_system.update(rain_system.wind_change_interval + 0.1, [])

    # The target wind should have changed
    assert rain_system.target_wind != 0
    assert rain_system.min_wind_force <= rain_system.target_wind <= rain_system.max_wind_force
    # The actual wind force should have moved toward the target
    assert rain_system.wind_force != initial_wind

def test_rain_system_wind_gradual_change(rain_system):
    # Set a target wind force
    rain_system.target_wind = 10.0
    initial_wind = rain_system.wind_force

    # Update for a short time
    rain_system.update(0.1, [])

    # Wind force should change gradually toward the target
    assert rain_system.wind_force > initial_wind
    assert rain_system.wind_force < rain_system.target_wind  # Not reaching target immediately

def test_rain_system_cleanup(rain_system):
    # Add a raindrop that's below the bottom of the screen
    raindrop = RainDrop(400, rain_system.screen_height + 10)
    rain_system.raindrops.append(raindrop)

    # Add another raindrop that's off to the side (should NOT be removed)
    side_raindrop = RainDrop(-100, 300)
    rain_system.raindrops.append(side_raindrop)

    # Update the system
    rain_system.update(0.1, [])

    # The bottom raindrop should be removed, the side one should remain
    assert raindrop not in rain_system.raindrops
    assert side_raindrop in rain_system.raindrops

def test_rain_system_with_player(rain_system, player):
    """Integration test with player interaction"""
    # Add a raindrop directly above the player
    raindrop = RainDrop(player.x, player.y - 10)
    initial_velocity = Vector2(0, 200.0)  # Initial downward velocity
    rain_system.raindrops.append(raindrop)

    # Update the system with the player
    rain_system.update(0.1, [player])

    # Verify collision was detected and handled
    assert raindrop.velocity != initial_velocity  # Velocity should have changed

    # Let gravity take effect for a few frames
    for _ in range(5):
        raindrop.update(0.016)

    # We don't assert on exact speed limits, just that the raindrop is moving
    assert raindrop.velocity.length() > 0

    # Test that collision caused a significant change
    assert abs(raindrop.velocity.y) != 200.0  # Y velocity should be affected

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

def test_velocity_changes_after_collision(raindrop):
    """Test that velocity continues to change after collision due to physics"""
    # Create an object to collide with
    collision_object = TestGameObject(100, 105)

    # Initial collision
    raindrop.check_and_handle_collisions([collision_object], 0.016)

    # Record velocity right after collision
    post_collision_velocity = raindrop.velocity.copy()

    # Run physics for a few frames
    velocities = []
    for _ in range(5):
        raindrop.update(0.016)  # Standard 60fps timestep
        velocities.append(raindrop.velocity.copy())

    # Verify velocities are different between frames
    for i in range(1, len(velocities)):
        assert velocities[i] != velocities[i-1], f"Velocity remained constant between frames {i-1} and {i}"

    # Verify final velocity is different from post-collision
    assert velocities[-1] != post_collision_velocity, "Velocity didn't change after collision"

    # Verify gravity is affecting the velocity
    # The change in velocity should be in the downward direction
    velocity_changes = [velocities[i].y - velocities[i-1].y for i in range(1, len(velocities))]
    assert any(change > 0 for change in velocity_changes), "Gravity isn't causing any downward acceleration"

def test_raindrop_collision_and_gravity_cycle(raindrop):
    """Test that a raindrop properly cycles through collision and gravity"""
    # Create an object to collide with - position it to ensure collision
    collision_object = TestGameObject(100, 105)  # Overlapping with the raindrop

    # Initial state - moving downward
    assert raindrop.velocity.y > 0, "Should start moving downward"
    initial_downward_speed = raindrop.velocity.y

    # Trigger collision
    raindrop.check_and_handle_collisions([collision_object], 0.016)

    # Immediately after collision - should be moving upward
    assert raindrop.velocity.y < 0, "Should bounce upward after collision"
    assert abs(raindrop.velocity.y) <= raindrop.max_upward_velocity + 0.01, "Should respect upward speed limit"

    # Record the upward velocity
    upward_velocity = raindrop.velocity.y

    # Update for a while to let gravity take effect
    # We'll update until we see the raindrop moving downward again
    max_updates = 100  # Prevent infinite loop
    updates = 0
    while raindrop.velocity.y <= 0 and updates < max_updates:
        raindrop.update(0.016)  # Standard 60fps timestep
        updates += 1

    # Verify that gravity eventually won
    assert raindrop.velocity.y > 0, "Should eventually move downward due to gravity"
    assert updates < max_updates, "Gravity should take effect within a reasonable time"

    # Let it fall a bit more to verify it's really falling
    raindrop.update(0.016)
    final_velocity = raindrop.velocity.y
    assert final_velocity > 0, "Should continue moving downward"
    assert final_velocity <= raindrop.max_velocity_magnitude, "Should respect downward speed limit"