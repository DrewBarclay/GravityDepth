import pygame
import numpy as np
from typing import List, Tuple, Union

def create_circle_polygon(center: Tuple[float, float], radius: float, start_angle: float = 0,
                         end_angle: float = 360, steps: int = 20) -> List[Tuple[float, float]]:
    """
    Create a polygon approximating a circle or arc.

    Args:
        center: The (x, y) center of the circle
        radius: The radius of the circle
        start_angle: Starting angle in degrees (0 = right, 90 = down, 180 = left, 270 = up)
        end_angle: Ending angle in degrees
        steps: Number of steps (points) to use for the approximation

    Returns:
        List of (x, y) points forming the polygon
    """
    points = []
    for i in range(steps + 1):
        angle = np.radians(start_angle + (end_angle - start_angle) * i / steps)
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        points.append((x, y))
    return points

def create_rect_polygon(rect: Union[pygame.Rect, Tuple[float, float, float, float]]) -> List[Tuple[float, float]]:
    """
    Create a rectangular polygon from a rect.

    Args:
        rect: A pygame.Rect or (x, y, width, height) tuple

    Returns:
        List of (x, y) points forming the rectangle corners
    """
    if isinstance(rect, pygame.Rect):
        x, y, width, height = rect.x, rect.y, rect.width, rect.height
    else:
        x, y, width, height = rect

    return [
        (x, y),  # Top-left
        (x + width, y),  # Top-right
        (x + width, y + height),  # Bottom-right
        (x, y + height)  # Bottom-left
    ]

def combine_polygons(polygons: List[List[Tuple[float, float]]]) -> List[Tuple[float, float]]:
    """
    Create a convex hull that encompasses multiple polygons.

    Args:
        polygons: List of polygons, each being a list of (x, y) points

    Returns:
        A new polygon (list of points) that encompasses all input polygons
    """
    # Combine all points from all polygons
    all_points = []
    for polygon in polygons:
        all_points.extend(polygon)

    # If we have less than 3 points, we can't create a proper convex hull
    if len(all_points) < 3:
        return all_points

    # Find the point with the lowest y-coordinate (and leftmost if tied)
    start_idx = 0
    for i in range(1, len(all_points)):
        if (all_points[i][1] < all_points[start_idx][1] or
            (all_points[i][1] == all_points[start_idx][1] and
             all_points[i][0] < all_points[start_idx][0])):
            start_idx = i

    # Sort points by polar angle relative to start point
    start_point = all_points[start_idx]

    def polar_angle(p):
        return np.arctan2(p[1] - start_point[1], p[0] - start_point[0])

    sorted_points = sorted(all_points, key=polar_angle)

    # Graham scan algorithm to find convex hull
    hull = [sorted_points[0], sorted_points[1]]

    for i in range(2, len(sorted_points)):
        while len(hull) > 1 and not is_counter_clockwise(hull[-2], hull[-1], sorted_points[i]):
            hull.pop()
        hull.append(sorted_points[i])

    return hull

def is_counter_clockwise(p1: Tuple[float, float], p2: Tuple[float, float],
                        p3: Tuple[float, float]) -> bool:
    """
    Check if three points form a counter-clockwise angle.

    Args:
        p1, p2, p3: Three points to check

    Returns:
        True if the points are in counter-clockwise order, False otherwise
    """
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]) > 0

def polygons_collide(poly1: List[Tuple[float, float]], poly2: List[Tuple[float, float]]) -> bool:
    """
    Check if two convex polygons are colliding using the Separating Axis Theorem (SAT).

    Args:
        poly1: First polygon as a list of (x, y) points
        poly2: Second polygon as a list of (x, y) points

    Returns:
        True if the polygons are colliding, False otherwise
    """
    # Helper function to project a polygon onto an axis
    def project_polygon(polygon, axis):
        dots = [axis[0] * p[0] + axis[1] * p[1] for p in polygon]
        return min(dots), max(dots)

    # Helper function to get the perpendicular vector
    def perpendicular(v):
        return (-v[1], v[0])

    # Check each edge of each polygon
    for poly in [poly1, poly2]:
        for i in range(len(poly)):
            edge = (poly[(i + 1) % len(poly)][0] - poly[i][0],
                    poly[(i + 1) % len(poly)][1] - poly[i][1])
            axis = perpendicular(edge)

            # Normalize the axis
            axis_length = np.sqrt(axis[0]**2 + axis[1]**2)
            if axis_length == 0:
                continue  # Skip zero-length edges

            axis = (axis[0] / axis_length, axis[1] / axis_length)

            # Project both polygons onto the axis
            proj1 = project_polygon(poly1, axis)
            proj2 = project_polygon(poly2, axis)

            # Check for separation
            if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
                return False  # Separation found, no collision

    # No separation found, polygons are colliding
    return True

def draw_polygon(surface: pygame.Surface, polygon: List[Tuple[float, float]],
                color: Tuple[int, int, int], width: int = 0) -> None:
    """
    Draw a polygon on a pygame surface.

    Args:
        surface: The pygame surface to draw on
        polygon: List of (x, y) points forming the polygon
        color: RGB color tuple
        width: Line width (0 = filled)
    """
    points = [(int(x), int(y)) for x, y in polygon]
    pygame.draw.polygon(surface, color, points, width)