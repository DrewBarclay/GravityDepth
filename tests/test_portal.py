import pytest
import pygame
from unittest.mock import MagicMock
from objects.portal import Portal
from objects.game_object import GameObject

class TestPortal:
    """Tests for the Portal class"""

    def setup_method(self):
        """Set up test fixtures"""
        # Initialize pygame for surface operations
        pygame.init()

        # Create a portal for testing
        self.portal = Portal(100, 100)

    def test_portal_initialization(self):
        """Test that the portal initializes correctly"""
        # Check position and dimensions
        assert self.portal.x == 100
        assert self.portal.y == 100
        assert self.portal.width == 50
        assert self.portal.height == 50

        # Check color is red
        assert self.portal.color == (255, 0, 0)

        # Check portal has a collision polygon
        assert self.portal._collision_polygon is not None

        # Check spiral points were generated
        assert len(self.portal.spiral_points) > 0

    def test_portal_update(self):
        """Test portal animation update"""
        # Initial rotation
        initial_rotation = self.portal.rotation

        # Update with 1 second delta time
        self.portal.update(1.0)

        # Rotation should increase by rotation_speed (90 degrees)
        assert self.portal.rotation == initial_rotation + 90

        # Update with another 3 seconds (should wrap around 360)
        self.portal.update(3.0)

        # 90 + 270 = 360, should wrap to 0
        assert 0 <= self.portal.rotation < 360

    def test_portal_draw(self):
        """Test that the portal can be drawn without errors"""
        # Create a surface for drawing
        surface = pygame.Surface((200, 200))

        # Should not raise an exception
        self.portal.draw(surface)

    def test_portal_collision(self):
        """Test portal collision detection"""
        # Create a test object that will collide with the portal
        test_object = GameObject(100, 100, 30, 30)

        # Check collision detection works
        assert self.portal.collides_with(test_object)

        # Move object away from portal
        test_object.set_position(300, 300)

        # Should no longer collide
        assert not self.portal.collides_with(test_object)