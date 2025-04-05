import pytest
import pygame
from pygame.math import Vector2
from objects.gravity_ball import GravityBall, GravityBallSystem
from objects.game_object import GameObject

class TestObject(GameObject):
    """Test object class for testing gravity ball interaction"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 20, 20)

class TestGravityBall:
    """Tests for the GravityBall class"""

    def test_gravity_ball_initialization(self):
        """Test that a gravity ball initializes with the correct properties"""
        ball = GravityBall(100, 100, radius=15, attraction_radius=150, lifespan=3.0)

        assert ball.x == 100
        assert ball.y == 100
        assert ball.radius == 15
        assert ball.attraction_radius == 150
        assert ball.lifespan == 3.0
        assert ball.lifetime == 0
        assert ball.marked_for_removal == False

    def test_gravity_ball_lifetime(self):
        """Test that a gravity ball expires after its lifespan"""
        ball = GravityBall(100, 100, lifespan=2.0)

        # Update with half the lifespan
        ball.update(1.0)
        assert ball.lifetime == 1.0
        assert ball.marked_for_removal == False

        # Update with the remaining lifespan
        ball.update(1.0)
        assert ball.lifetime == 2.0
        assert ball.marked_for_removal == True

    def test_gravity_attraction(self):
        """Test that a gravity ball attracts objects within its attraction radius"""
        ball = GravityBall(100, 100, radius=10, attraction_radius=50)

        # Object inside attraction radius
        obj_near = TestObject(120, 120)
        obj_near.velocity = Vector2(0, 0)

        # Object outside attraction radius
        obj_far = TestObject(200, 200)
        obj_far.velocity = Vector2(0, 0)

        # Apply gravity to both objects
        ball.apply_gravity_to_object(obj_near, 0.1)
        ball.apply_gravity_to_object(obj_far, 0.1)

        # Near object should have non-zero acceleration (attraction)
        assert obj_near.acceleration.length() > 0

        # Far object should have zero acceleration (no attraction)
        assert obj_far.acceleration.length() == 0

    def test_ignores_tied_objects(self):
        """Test that gravity balls ignore objects that are tied to other objects"""
        ball = GravityBall(100, 100, radius=10, attraction_radius=50)

        # Create an object with a tied_to property
        obj = TestObject(120, 120)
        obj.velocity = Vector2(0, 0)
        obj.acceleration = Vector2(0, 0)
        obj.tied_to = "something"  # Just needs to be non-None

        # Apply gravity to the tied object
        ball.apply_gravity_to_object(obj, 0.1)

        # The tied object should not be affected (zero acceleration)
        assert obj.acceleration.length() == 0


class TestGravityBallSystem:
    """Tests for the GravityBallSystem class"""

    def test_create_gravity_ball(self):
        """Test creating a gravity ball via the system"""
        system = GravityBallSystem()

        # Create a gravity ball
        ball = system.create_gravity_ball(150, 150)

        assert ball in system.gravity_balls
        assert len(system.gravity_balls) == 1
        assert ball.x == 150
        assert ball.y == 150

    def test_update_removes_expired_balls(self):
        """Test that expired gravity balls are removed during update"""
        system = GravityBallSystem()

        # Create two gravity balls, one with very short lifespan
        ball1 = GravityBall(100, 100, lifespan=0.1)
        ball2 = GravityBall(200, 200, lifespan=5.0)

        system.gravity_balls = [ball1, ball2]

        # Update with time > ball1 lifespan
        system.update(0.2, [])

        # Only ball2 should remain
        assert len(system.gravity_balls) == 1
        assert ball1 not in system.gravity_balls
        assert ball2 in system.gravity_balls

    def test_gravity_applied_to_objects(self):
        """Test that gravity is applied to objects during system update"""
        system = GravityBallSystem()
        ball = GravityBall(100, 100, radius=10, attraction_radius=50)
        system.gravity_balls = [ball]

        # Create test object within attraction radius
        obj = TestObject(120, 120)
        obj.velocity = Vector2(0, 0)
        obj.acceleration = Vector2(0, 0)

        # Update system with the test object
        system.update(0.1, [obj])

        # Object should have non-zero acceleration (gravity was applied)
        assert obj.acceleration.length() > 0