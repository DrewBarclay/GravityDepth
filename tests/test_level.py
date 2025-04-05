import pytest
import pygame
from unittest.mock import MagicMock, patch
from objects.level import Level, OrangeSquare
from objects.portal import Portal
from objects.gravity_ball import GravityBall

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

        # For level 1-1, we should have 3 blue gravity balls
        blue_balls = [obj for obj in self.level.objects if isinstance(obj, GravityBall)]
        assert len(blue_balls) == 3
        for ball in blue_balls:
            assert ball.color == (0, 0, 255)  # Blue

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

        # Level 1-2 should have 2 orange squares
        orange_squares = [obj for obj in self.level.objects if isinstance(obj, OrangeSquare)]
        assert len(orange_squares) == 2

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

    def test_orange_square(self):
        """Test the OrangeSquare class"""
        # Test basic properties of the OrangeSquare class
        square = OrangeSquare(100, 100)

        # Test initial properties
        assert square.color == (255, 165, 0)  # Orange
        assert square.marked_for_removal == False
        assert square.width == 30
        assert square.height == 30

        # Skip actual drawing and physics tests that need pygame setup