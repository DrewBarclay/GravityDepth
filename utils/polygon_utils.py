import pygame
import numpy as np
from typing import List, Tuple

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Determine if a point is inside a polygon using the ray casting algorithm.

    Args:
        point: A (x, y) point to check
        polygon: A list of (x, y) points forming a polygon

    Returns:
        True if the point is inside the polygon, False otherwise
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def polygons_collide(poly1: List[Tuple[float, float]], poly2: List[Tuple[float, float]]) -> bool:
    """
    Check if two polygons are colliding using the Separating Axis Theorem (SAT).

    Args:
        poly1: A list of (x, y) points forming the first polygon
        poly2: A list of (x, y) points forming the second polygon

    Returns:
        True if the polygons are colliding, False otherwise
    """
    # Check if any point of poly1 is inside poly2
    for point in poly1:
        if point_in_polygon(point, poly2):
            return True

    # Check if any point of poly2 is inside poly1
    for point in poly2:
        if point_in_polygon(point, poly1):
            return True

    # Check for edge intersections
    for i in range(len(poly1)):
        p1 = poly1[i]
        p2 = poly1[(i + 1) % len(poly1)]

        for j in range(len(poly2)):
            p3 = poly2[j]
            p4 = poly2[(j + 1) % len(poly2)]

            if line_segments_intersect(p1, p2, p3, p4):
                return True

    return False

def line_segments_intersect(p1: Tuple[float, float], p2: Tuple[float, float],
                           p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """
    Check if two line segments intersect.

    Args:
        p1, p2: Points defining the first line segment
        p3, p4: Points defining the second line segment

    Returns:
        True if the line segments intersect, False otherwise
    """
    # Extract coordinates
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    # Calculate the direction vectors
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3

    # Calculate the denominator and numerator for the equations
    denominator = (dy2 * dx1 - dx2 * dy1)

    # If denominator is 0, lines are parallel
    if denominator == 0:
        return False

    ua = ((dx2 * (y1 - y3)) - (dy2 * (x1 - x3))) / denominator
    ub = ((dx1 * (y1 - y3)) - (dy1 * (x1 - x3))) / denominator

    # Check if the intersection is within both line segments
    return (0 <= ua <= 1) and (0 <= ub <= 1)

def generate_polygon_from_rect(rect: pygame.Rect) -> List[Tuple[float, float]]:
    """
    Generate a simple rectangle polygon from a pygame Rect.

    Args:
        rect: A pygame Rect

    Returns:
        A list of (x, y) points forming a rectangle
    """
    return [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.right, rect.bottom),
        (rect.left, rect.bottom)
    ]

def generate_convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Generate a convex hull from a set of points using Graham scan.

    Args:
        points: A list of (x, y) points

    Returns:
        A list of (x, y) points forming the convex hull
    """
    if len(points) <= 3:
        return points

    # Find the point with the lowest y-coordinate (and leftmost if tied)
    start_idx = 0
    for i in range(1, len(points)):
        if points[i][1] < points[start_idx][1] or (points[i][1] == points[start_idx][1] and points[i][0] < points[start_idx][0]):
            start_idx = i

    start_point = points[start_idx]

    # Sort points by polar angle relative to start point
    def polar_angle(p):
        return np.arctan2(p[1] - start_point[1], p[0] - start_point[0])

    sorted_points = sorted(points, key=polar_angle)

    # Graham scan algorithm
    hull = [sorted_points[0], sorted_points[1]]

    for i in range(2, len(sorted_points)):
        while len(hull) > 1 and not is_counter_clockwise(hull[-2], hull[-1], sorted_points[i]):
            hull.pop()
        hull.append(sorted_points[i])

    return hull

def is_counter_clockwise(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
    """
    Check if three points form a counter-clockwise angle.

    Args:
        p1, p2, p3: Three points to check

    Returns:
        True if the points are in counter-clockwise order, False otherwise
    """
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]) > 0

def get_polygon_centroid(polygon: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the centroid of a polygon.

    Args:
        polygon: A list of (x, y) points forming a polygon

    Returns:
        The (x, y) coordinates of the centroid
    """
    x = [p[0] for p in polygon]
    y = [p[1] for p in polygon]
    return sum(x) / len(polygon), sum(y) / len(polygon)