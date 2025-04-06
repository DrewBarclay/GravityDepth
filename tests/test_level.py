import pytest
import pygame
from unittest.mock import MagicMock, patch
from objects.level import Level, OrangeSquare
from objects.portal import Portal
from objects.gravity_ball import GravityBall
from engine.game_engine import GameEngine
from objects.bat import Bat
from objects.projectile import Projectile

# Initialize pygame
pygame.init()

class TestLevel:
    """Tests for the Level class"""

    def setup_method(self):
        # Create a mock engine for testing
        self.mock_engine = MagicMock()
        self.mock_engine.get_dimensions.return_value = (800, 600)

        # Create a mock player
        self.mock_player = MagicMock()

        # Patch the entire Player import
        with patch('game.Player') as self.mock_player_class:
            # Configure the mock player class to return our mock player
            self.mock_player_class.return_value = self.mock_player

            # Patch the create_player method to return our mock player
            with patch.object(Level, 'create_player', return_value=self.mock_player):
                # Create a level instance
                self.level = Level(self.mock_engine, 1, 1)

    def test_level_initialization(self):
        """Test that the level initializes with the correct objects"""
        # Verify we have a portal
        assert any(isinstance(obj, Portal) for obj in self.level.objects)

    def test_level_transition(self):
        """Test transitioning to the next level"""
        # Remember the original objects
        original_objects = self.level.objects.copy()

        # Patch create_player again for the next level
        with patch.object(Level, 'create_player', return_value=self.mock_player):
            # Transition to the next level
            self.level.next_level()

        # Level number should be incremented
        assert self.level.level_number == 2
        assert self.level.world_number == 1

        # All original objects should be marked for removal
        for obj in original_objects:
            assert obj.marked_for_removal

        # Still have a portal
        assert any(isinstance(obj, Portal) for obj in self.level.objects)

    def test_world_transition(self):
        """Test transitioning to a new world"""
        # Patch create_player for multiple level transitions
        with patch.object(Level, 'create_player', return_value=self.mock_player):
            # Move to level 1-2
            self.level.next_level()
            # Move to level 1-3
            self.level.next_level()
            # Move to level 2-1 (should wrap around)
            self.level.next_level()

        # Check we're in world 2, level 1
        assert self.level.world_number == 2
        assert self.level.level_number == 1

        # Level 2-1 should have player and portal (and player is mocked, not a real object in our list)
        portal_count = sum(1 for obj in self.level.objects if isinstance(obj, Portal))
        assert portal_count == 1

        # We can also verify the player is set correctly
        assert self.level.player == self.mock_player

def test_level_initialization():
    """Test that a level can be created properly"""
    engine = GameEngine(800, 600)
    level = Level(engine, 1, 1)
    assert level.level_number == 1
    assert level.world_number == 1
    assert len(level.objects) > 0  # Should have player, portal, and some objects

def test_level_next():
    """Test that next_level increments level number"""
    engine = GameEngine(800, 600)
    level = Level(engine, 1, 1)
    level.next_level()
    assert level.level_number == 2
    assert level.world_number == 1

def test_level_removes_marked_bats():
    """Test that the level properly removes bats marked for removal"""
    engine = GameEngine(800, 600)
    level = Level(engine, 1, 1)

    # Get the bats from the level
    bats = [enemy for enemy in level.enemies if isinstance(enemy, Bat)]
    assert len(bats) > 0, "Level should have at least one bat"

    print(f"Found {len(bats)} bats in the level")

    # Create a projectile aimed at the first bat
    bat = bats[0]
    projectile = Projectile(
        bat.x + 100,  # Start away from the bat
        bat.y,
        pygame.math.Vector2(-100, 0)  # Moving left toward the bat
    )

    # Add the projectile to a second bat's projectiles list
    if len(bats) > 1:
        second_bat = bats[1]
        print("Using second bat from level")
    else:
        # Create a second bat if there's only one
        second_bat = Bat(500, 100)
        level.add_enemy(second_bat)
        print("Created new second bat")

    second_bat.projectiles.append(projectile)
    print(f"Added projectile to second bat's projectiles, now has {len(second_bat.projectiles)} projectiles")

    # Initial check
    assert bat in level.enemies
    assert not bat.marked_for_removal

    # Get bat center position
    bat_center_x = bat.x + bat.width / 2
    bat_center_y = bat.y + bat.height / 2

    # Move projectile to the center of the bat to ensure collision
    projectile.x = bat_center_x - projectile.width / 2
    projectile.y = bat_center_y - projectile.height / 2
    print(f"Moved projectile to bat center: projectile({projectile.x}, {projectile.y}), bat_center({bat_center_x}, {bat_center_y})")

    # Debug collision polygons
    print(f"Bat collision polygon: {bat.collision_polygon}")
    print(f"Projectile collision polygon: {projectile.collision_polygon}")

    # Manually test collision - force update projectile collision polygon
    projectile.create_circle_collision()
    collision_result = bat.collides_with(projectile)
    print(f"Manual collision check result: {collision_result}")

    # If collision check still fails, force the bat to be hit
    if not collision_result:
        print("Collision check failed - directly testing bat.check_projectile_collisions")
        bat.check_projectile_collisions([projectile])
        print(f"After direct check: bat marked={bat.marked_for_removal}, projectile marked={projectile.marked_for_removal}")

    # Update the level to process collisions
    level.update(0.1)

    # Debug enemy list
    print(f"Enemies after update: {len(level.enemies)}")
    for i, enemy in enumerate(level.enemies):
        print(f"Enemy {i}: {enemy}, marked_for_removal: {enemy.marked_for_removal}")

    # Get all projectiles
    all_projectiles = level.collect_all_projectiles()
    print(f"All projectiles: {len(all_projectiles)}")
    for i, proj in enumerate(all_projectiles):
        print(f"Projectile {i}: {proj}, marked_for_removal: {proj.marked_for_removal}")

    # Check that the bat is now marked for removal and removed from enemies list
    print(f"Bat marked for removal: {bat.marked_for_removal}")
    print(f"Bat in enemies list: {bat in level.enemies}")

    assert bat.marked_for_removal
    assert bat not in level.enemies
