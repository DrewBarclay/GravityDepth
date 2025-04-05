import pytest
import pygame
import numpy as np
from utils.advanced_polygon_utils import (
    create_circle_polygon,
    create_rect_polygon,
    combine_polygons,
    is_counter_clockwise,
    polygons_collide
)

class TestPolygonUtils:
    def test_create_circle_polygon(self):
        """Test creating a circle polygon"""
        # Test full circle
        circle = create_circle_polygon((50, 50), 10, steps=4)
        assert len(circle) == 5  # 4 steps + 1 point to close the circle

        # First and last points should be the same (or very close)
        assert np.isclose(circle[0][0], circle[-1][0])
        assert np.isclose(circle[0][1], circle[-1][1])

        # Test semi-circle
        semi = create_circle_polygon((50, 50), 10, 0, 180, steps=4)
        assert len(semi) == 5  # 4 steps + 1 point to close the arc

        # First point should be at angle 0
        assert np.isclose(semi[0][0], 60)  # center_x + radius
        assert np.isclose(semi[0][1], 50)  # center_y

        # Last point should be at angle 180
        assert np.isclose(semi[-1][0], 40)  # center_x - radius
        assert np.isclose(semi[-1][1], 50)  # center_y

    def test_create_rect_polygon(self):
        """Test creating a rectangle polygon"""
        # Test with a pygame Rect
        rect = pygame.Rect(10, 20, 30, 40)
        poly = create_rect_polygon(rect)

        assert len(poly) == 4
        assert poly[0] == (10, 20)  # Top-left
        assert poly[1] == (40, 20)  # Top-right
        assert poly[2] == (40, 60)  # Bottom-right
        assert poly[3] == (10, 60)  # Bottom-left

        # Test with a tuple
        poly = create_rect_polygon((10, 20, 30, 40))

        assert len(poly) == 4
        assert poly[0] == (10, 20)  # Top-left
        assert poly[1] == (40, 20)  # Top-right
        assert poly[2] == (40, 60)  # Bottom-right
        assert poly[3] == (10, 60)  # Bottom-left

    def test_combine_polygons(self):
        """Test combining multiple polygons"""
        # Test with two rectangles
        rect1 = [(0, 0), (10, 0), (10, 10), (0, 10)]
        rect2 = [(5, 5), (15, 5), (15, 15), (5, 15)]

        combined = combine_polygons([rect1, rect2])

        # The combined polygon should be a convex hull
        assert len(combined) >= 4

        # It should contain all extreme points
        assert (0, 0) in combined
        assert (15, 5) in combined or (15, 15) in combined
        assert (5, 15) in combined or (15, 15) in combined

        # Test combining a rect and a circle
        rect = [(0, 0), (10, 0), (10, 10), (0, 10)]
        circle = create_circle_polygon((15, 15), 5, steps=8)

        combined = combine_polygons([rect, circle])

        # The combined polygon should encompass both shapes
        assert len(combined) >= 4

        # Test empty list
        assert combine_polygons([]) == []

        # Test single polygon
        assert combine_polygons([rect1]) == rect1

    def test_is_counter_clockwise(self):
        """Test counter-clockwise detection"""
        # Counter-clockwise triangle
        assert is_counter_clockwise((0, 0), (1, 1), (0, 1))

        # Clockwise triangle
        assert not is_counter_clockwise((0, 0), (0, 1), (1, 1))

        # Collinear points
        assert not is_counter_clockwise((0, 0), (1, 1), (2, 2))

    def test_polygons_collide(self):
        """Test polygon collision detection"""
        # Overlapping rectangles
        rect1 = [(0, 0), (10, 0), (10, 10), (0, 10)]
        rect2 = [(5, 5), (15, 5), (15, 15), (5, 15)]

        assert polygons_collide(rect1, rect2)

        # Non-overlapping rectangles
        rect3 = [(20, 20), (30, 20), (30, 30), (20, 30)]

        assert not polygons_collide(rect1, rect3)

        # Rectangle and circle that overlap
        rect = [(0, 0), (10, 0), (10, 10), (0, 10)]
        circle = create_circle_polygon((7, 7), 5, steps=8)

        assert polygons_collide(rect, circle)

        # Rectangle and circle that don't overlap
        far_circle = create_circle_polygon((20, 20), 5, steps=8)

        assert not polygons_collide(rect, far_circle)