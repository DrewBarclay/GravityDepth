import pytest
import pygame
import math
from objects.bat import Bat
from objects.game_object import GameObject
from objects.projectile import Projectile

# Setup pygame for testing
pygame.init()

class MockPlayer(GameObject):
    """Mock player for testing bat targeting"""
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50)
        self.marked_for_removal = False
        # Ensure collision detection works
        self.width = 50
        self.height = 50

def test_bat_initialization():
    """Test that a bat can be created properly"""
    bat = Bat(100, 100)
    assert bat.x == 100
    assert bat.y == 100
    assert not bat.marked_for_removal
    assert len(bat.projectiles) == 0

def test_bat_update():
    """Test that the bat updates position correctly"""
    bat = Bat(100, 100)

    # Store initial position
    initial_x = bat.x
    initial_y = bat.y

    # Update with a time delta
    bat.update(0.1)

    # Position should change due to hover and movement
    assert bat.x != initial_x  # Should move horizontally
    assert abs(bat.y - initial_y) < 30  # Should hover but not move too far vertically

def test_bat_update_zero_dt():
    """Test that update handles dt=0 correctly"""
    bat = Bat(100, 100)

    # Store initial state
    initial_x = bat.x
    initial_y = bat.y
    initial_velocity_x = bat.velocity.x
    initial_velocity_y = bat.velocity.y

    # Call update with zero dt
    bat.update(0)

    # Position and velocity should remain unchanged
    assert bat.x == initial_x
    assert bat.y == initial_y
    assert bat.velocity.x == initial_velocity_x
    assert bat.velocity.y == initial_velocity_y

    # Try with negative dt too
    bat.update(-0.1)

    # Position and velocity should still remain unchanged
    assert bat.x == initial_x
    assert bat.y == initial_y
    assert bat.velocity.x == initial_velocity_x
    assert bat.velocity.y == initial_velocity_y

def test_mock_player():
    """Test that our mock player class is properly configured"""
    player = MockPlayer(100, 100)
    assert player.x == 100
    assert player.y == 100
    assert player.width == 50
    assert player.height == 50

    # Test that the collision polygon is properly set
    assert hasattr(player, 'collision_polygon')
    assert len(player.collision_polygon) > 0

def test_find_target_player_directly():
    """Test the find_target_player method directly with properly positioned players"""
    bat = Bat(100, 100, width=40, height=30)

    # Create a player at the exact same level
    player = MockPlayer(200, 100 + (bat.height - 50)/2)  # Adjust to align centers

    # Debug output
    print(f"\nBat height: {bat.height}, center: {bat.y + bat.height/2}")
    print(f"Player height: {player.height}, center: {player.y + player.height/2}")
    print(f"Vertical distance: {abs((bat.y + bat.height/2) - (player.y + player.height/2))}")
    print(f"Threshold: {bat.height * 2}")

    # Check directly if player is in range
    target = bat.find_target_player([player])
    assert target is not None, "Player should be found as a valid target"
    assert target == player

    # Now test with a player that's too far away vertically
    far_player = MockPlayer(200, 300)
    target = bat.find_target_player([far_player])
    assert target is None, "Player too far vertically should not be found"

def test_find_target_player():
    """Test finding a target player on the same level"""
    bat = Bat(100, 100)

    # Create players at different positions
    player1 = MockPlayer(200, 100)  # Same level
    player2 = MockPlayer(150, 300)  # Different level
    player3 = MockPlayer(300, 105)  # Same level but further away

    # Test with a single player on same level
    target = bat.find_target_player([player1])
    assert target == player1

    # Test with multiple players, should find the closest one on same level
    target = bat.find_target_player([player1, player2, player3])
    assert target == player1

    # Test with a player that's too far vertically
    target = bat.find_target_player([player2])
    assert target is None

def test_bat_shoot_at_player():
    """Test shooting at a player"""
    bat = Bat(100, 100)
    player = MockPlayer(200, 100)  # Player to the right

    # Set screen dimensions
    bat.screen_width = 800
    bat.screen_height = 600

    # Make the bat shoot at the player
    bat.shoot_at_player(player)

    # Should create a projectile
    assert len(bat.projectiles) == 1

    # Verify projectile has velocity
    projectile = bat.projectiles[0]
    assert projectile.velocity.length() > 0  # Should have some velocity

    # Should be shooting generally towards the player (x component should be positive)
    assert projectile.velocity.x > 0

def test_player_at_same_position():
    """Test edge case where player is at the exact same position as the bat"""
    bat = Bat(100, 100)
    player = MockPlayer(100, 100)  # Same position

    # Set screen dimensions
    bat.screen_width = 800
    bat.screen_height = 600

    # Should not cause divide by zero
    bat.shoot_at_player(player)

    # Should still create a projectile
    assert len(bat.projectiles) == 1

    # The projectile should have some velocity (not zero)
    projectile = bat.projectiles[0]
    assert projectile.velocity.length() > 0

    # Velocity magnitude should match attack speed
    assert abs(projectile.velocity.length() - bat.attack_speed) < 0.1

def test_try_attack_cooldown():
    """Test that attacks respect the cooldown"""
    bat = Bat(100, 100)
    player = MockPlayer(200, 100)

    # Set screen dimensions to ensure players are considered on the same level
    bat.screen_width = 800
    bat.screen_height = 600

    # Print debug information
    print("\nDEBUG: Testing try_attack_cooldown")

    # Test if player in range for targeting
    target = bat.find_target_player([player])
    print(f"DEBUG: Target found: {target is not None}")
    if target:
        print(f"DEBUG: Target position: ({target.x}, {target.y})")
        print(f"DEBUG: Bat position: ({bat.x}, {bat.y})")

        # Calculate vertical distance to verify targeting works
        vertical_distance = abs((bat.y + bat.height/2) - (player.y + player.height/2))
        print(f"DEBUG: Vertical distance: {vertical_distance}")
        print(f"DEBUG: Height threshold: {bat.height * 2}")
    else:
        print("DEBUG: No target found, player might be out of vertical range")

        # Adjust player position to be exactly at bat's level
        player.y = bat.y
        print(f"DEBUG: Adjusted player position to ({player.x}, {player.y})")

        # Try finding target again
        target = bat.find_target_player([player])
        print(f"DEBUG: Target found after adjustment: {target is not None}")

    # Test for cooldown timing - SEPARATE TEST PART 1
    # ------------------------------------------------
    # Set initial cooldown and reset timer
    bat.attack_cooldown = 1.0
    bat.attack_timer = 1.1  # Already past cooldown
    print(f"DEBUG: Attack cooldown set to {bat.attack_cooldown}, timer is {bat.attack_timer}")

    # Try to attack (should succeed)
    print("DEBUG: Trying try_attack with cooldown ready")
    bat.try_attack([player])
    print(f"DEBUG: After try_attack with cooldown ready, projectiles: {len(bat.projectiles)}")
    assert len(bat.projectiles) == 1

    # Test for direct shooting - SEPARATE TEST PART 2
    # -----------------------------------------------
    # Clear projectiles for next test
    bat.projectiles.clear()

    # Directly call shoot_at_player to test if it works
    print("DEBUG: Directly calling shoot_at_player")
    bat.shoot_at_player(player)
    print(f"DEBUG: After direct shoot_at_player, projectiles: {len(bat.projectiles)}")
    assert len(bat.projectiles) == 1

    # Test cooldown prevention - SEPARATE TEST PART 3
    # -----------------------------------------------
    # Clear projectiles, set timer to 0 to ensure cooldown not ready
    bat.projectiles.clear()
    bat.attack_timer = 0
    bat.attack_cooldown = 1.0  # Reset cooldown to known value

    print("\nDEBUG: Testing cooldown prevention")
    print(f"DEBUG: Attack cooldown set to {bat.attack_cooldown}, timer is {bat.attack_timer}")

    # Try attack, should fail due to cooldown
    bat.try_attack([player])
    print(f"DEBUG: After try_attack with cooldown not ready, projectiles: {len(bat.projectiles)}")
    assert len(bat.projectiles) == 0

    # Update timer past cooldown
    bat.attack_timer = 1.1
    print(f"DEBUG: Updated timer to {bat.attack_timer}")

    # Try again, should succeed now
    bat.try_attack([player])
    print(f"DEBUG: After try_attack with timer updated, projectiles: {len(bat.projectiles)}")
    assert len(bat.projectiles) == 1

def test_projectile_cleanup():
    """Test that projectiles are cleaned up properly"""
    bat = Bat(100, 100)
    player = MockPlayer(200, 100)

    # Set screen dimensions
    bat.screen_width = 800
    bat.screen_height = 600

    # Make the bat shoot at the player
    bat.shoot_at_player(player)
    assert len(bat.projectiles) == 1

    # Mark the projectile for removal
    bat.projectiles[0].marked_for_removal = True

    # Update should remove the projectile
    bat.update(0.1)
    assert len(bat.projectiles) == 0

def test_projectile_bat_collision():
    """Test that projectiles are destroyed when they hit bats (not their source bat)"""
    # Create two bats
    bat1 = Bat(100, 100)
    bat2 = Bat(300, 100)

    # Set screen dimensions
    bat1.screen_width = 800
    bat1.screen_height = 600
    bat2.screen_width = 800
    bat2.screen_height = 600

    # Create a projectile aimed at bat2
    projectile_velocity = pygame.math.Vector2(200, 0)  # Moving right
    projectile = Projectile(
        bat1.x + bat1.width/2,
        bat1.y + bat1.height/2,
        projectile_velocity
    )

    # Add it to bat1's projectiles
    bat1.projectiles.append(projectile)

    # Make sure it's not colliding yet
    bat2.check_projectile_collisions([projectile])
    assert not projectile.marked_for_removal

    # Move projectile to collide with bat2
    projectile.x = bat2.x  # Position it at bat2's location

    # Now check collision - should mark projectile for removal
    bat2.check_projectile_collisions([projectile])
    assert projectile.marked_for_removal

    # Test projectile immunity - bat shouldn't destroy its own projectiles
    bat1.projectile_immunity_timer = 0  # Ensure no immunity

    # Create a new projectile from bat1
    projectile2 = Projectile(
        bat1.x + bat1.width/2,
        bat1.y + bat1.height/2,
        projectile_velocity
    )
    bat1.projectiles.append(projectile2)

    # Check collision with its own projectile
    bat1.check_projectile_collisions(bat1.projectiles)

    # The projectile should not be marked for removal
    assert not projectile2.marked_for_removal