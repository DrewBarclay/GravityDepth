from objects.game_object import GameObject
from pygame.math import Vector2
import random
import pygame
import math
from rain.raindrop_constants import (
    DEFAULT_VELOCITY_Y,
    GRAVITY_ACCELERATION,
    MAX_VELOCITY_MAGNITUDE,
    MAX_UPWARD_VELOCITY,
    DEFAULT_WIDTH,
    MIN_LENGTH,
    MAX_LENGTH,
    DEFAULT_COLOR,
    REPULSION_FORCE,
    RAIN_COLLISION_FRICTION,
    DEPTH_REPULSION_MULTIPLIER,
    RAIN_AIR_FRICTION,
)

class RainDrop(GameObject):
    def __init__(self, x, y, wind_force=0):
        # Initialize with width=1 and height=length (will be set after super().__init__)
        self.length = random.uniform(MIN_LENGTH, MAX_LENGTH)
        super().__init__(x, y, width=DEFAULT_WIDTH, height=self.length)
        # Base velocity (falling down and slightly right)
        self.velocity = Vector2(wind_force, DEFAULT_VELOCITY_Y)
        self.acceleration = GRAVITY_ACCELERATION  # Much stronger gravity
        self.wind_acceleration = Vector2(0, 0)  # Wind will be applied as acceleration
        self.max_velocity_magnitude = MAX_VELOCITY_MAGNITUDE  # Max velocity magnitude for limiting forces
        self.max_upward_velocity = MAX_UPWARD_VELOCITY  # Max upward velocity for limiting forces
        self.width = DEFAULT_WIDTH
        self.color = DEFAULT_COLOR
        self.repulsion_force = REPULSION_FORCE  # Strong repulsion force for bouncing
        self.marked_for_removal = False
        # Keep track of objects we're currently colliding with
        self.colliding_objects = set()
        # Track object the raindrop is tied to and its last position
        self.tied_to = None
        self.tied_to_last_pos = None
        self.relative_position = Vector2(0, 0)
        # Flag to track if raindrop is affected by a gravity ball
        self.in_gravity_field = False
        # Flag to track if colliding with player
        self.colliding_with_player = False
        # Track previous collision state for sound effects
        self.was_colliding_with_player = False
        self.was_colliding = False

        # Set a custom line-shaped collision polygon for the raindrop
        self.set_collision_polygon([
            (0, 0),  # Top point
            (DEFAULT_WIDTH, 0),  # Top right
            (DEFAULT_WIDTH, self.length),  # Bottom right
            (0, self.length)  # Bottom left
        ])

    def update(self, dt):
        # If tied to an object, update position based on object movement
        if self.tied_to:
            current_obj_pos = Vector2(self.tied_to.x, self.tied_to.y)

            # If the object has moved, adjust our position by the same amount
            if self.tied_to_last_pos:
                obj_movement = current_obj_pos - self.tied_to_last_pos
                # Apply the object's movement to our position
                self.x += obj_movement.x
                self.y += obj_movement.y

            # Update the last position for next frame
            self.tied_to_last_pos = current_obj_pos.copy()

        # Only apply gravity if NOT colliding with objects and NOT in a gravity field
        if not self.colliding_objects:
            # Apply wind acceleration always
            wind_acc = self.wind_acceleration * dt

            # Only apply gravity if not in a gravity field
            if not self.in_gravity_field:
                # Apply both gravity and wind acceleration
                self.acceleration = (GRAVITY_ACCELERATION + self.wind_acceleration) * dt
            else:
                # Only apply wind, no gravity when in a gravity field
                self.acceleration = wind_acc

            DAMPING_FORCE = (self.velocity.length() ** 2 * RAIN_AIR_FRICTION) * dt
            # Apply damping force proprotionate on x and y
            if self.velocity.length() > 0:  # Check for zero length
                self.acceleration -= DAMPING_FORCE * self.velocity.normalize()

            # Apply acceleration with small random variation for more natural motion
            variation = Vector2(
                random.uniform(-50, 50),
                random.uniform(-50, 50)
            )

            self.acceleration += variation
        else:
            # Inside an object - cancel all velocity and apply strong upward force
            self.acceleration = Vector2(0, 0)

            # Almost completely stop the raindrop
            # Physics damping: 1/2 * p * v^2 * c_D * a
            # Simplify to v^2 * constant
            DAMPING_FORCE = (self.velocity.length() ** 2 * RAIN_COLLISION_FRICTION) * dt
            # Apply damping force proprotionate on x and y
            if self.velocity.length() > 0:  # Check for zero length
                self.acceleration -= DAMPING_FORCE * self.velocity.normalize()

            # Apply strong repulsion forces from all colliding objects
            for obj in self.colliding_objects:
                self.acceleration += self.get_repulsion_force(obj, dt)

        # Reset the gravity field flag for next frame
        self.in_gravity_field = False

        # Update position
        super().update(dt)

        # After updating position, if we're tied to an object, ensure we stay within its horizontal bounds
        # and only allow exiting through the bottom
        if self.tied_to:
            self.constrain_to_tied_object()

    def _limit_applied_force(self, force):
        """
        Limit the force so it doesn't cause velocity to exceed thresholds.
        Modifies the force vector in place.
        """
        # Predict new velocity after applying force
        predicted_velocity = self.velocity + force

        # Check if we're going upward (negative y velocity)
        if predicted_velocity.y < 0:
            max_allowed = self.max_upward_velocity
        else:
            max_allowed = self.max_velocity_magnitude

        # If predicted velocity exceeds the threshold, scale down the force
        if predicted_velocity.length() > max_allowed:
            # Calculate what the force should be to exactly reach max velocity
            target_velocity = predicted_velocity.normalize() * max_allowed
            # Force should be difference between target and current velocity
            limited_force = target_velocity - self.velocity

            # Copy the limited force values back to the original force vector
            force.x = limited_force.x
            force.y = limited_force.y

    def constrain_to_tied_object(self):
        """Ensure raindrop stays within the horizontal bounds of the object it's tied to"""
        if not self.tied_to:
            return

        obj = self.tied_to
        obj_left = obj.x
        obj_right = obj.x + obj.width
        obj_bottom = obj.y + obj.height

        # Calculate raindrop center X position
        raindrop_center_x = self.x + self.width / 2

        # If the raindrop is trying to move outside horizontally, constrain it
        if raindrop_center_x < obj_left:
            # Moved outside left edge - constrain and add downward velocity
            self.x = obj_left - self.width / 2
            # Increase downward velocity to simulate sliding down
            self.velocity.y = max(self.velocity.y, 100)
            # Reduce horizontal velocity
            self.velocity.x = 0
        elif raindrop_center_x > obj_right:
            # Moved outside right edge - constrain and add downward velocity
            self.x = obj_right - self.width / 2
            # Increase downward velocity to simulate sliding down
            self.velocity.y = max(self.velocity.y, 100)
            # Reduce horizontal velocity
            self.velocity.x = 0

        # Check if raindrop has exited through the bottom
        if self.y > obj_bottom:
            # Allow raindrop to detach and continue falling
            self.untie_from_object()

    def check_and_handle_collisions(self, game_objects, dt):
        # Check each object for collision
        currently_colliding = set()
        was_colliding = bool(self.colliding_objects)  # Remember if we were previously colliding
        was_colliding_with_player = self.colliding_with_player  # Remember if we were colliding with player
        self.colliding_with_player = False  # Reset player collision flag

        for obj in game_objects:
            if obj is self:
                continue

            # Use polygon-based collision detection
            if self.collides_with(obj):
                currently_colliding.add(obj)

                # Check if this is a player object
                if hasattr(obj, 'get_property') and obj.get_property('type') == 'player':
                    self.colliding_with_player = True

                # If we're not already tied to an object, tie to this one
                if not self.tied_to:
                    self.tie_to_object(obj)

        # Check for new collisions to play sound effects
        # Only if we have access to the game engine
        if hasattr(game_objects[0], 'engine') and hasattr(game_objects[0].engine, 'audio_system'):
            audio_system = game_objects[0].engine.audio_system

            # New collision with player
            if self.colliding_with_player and not was_colliding_with_player:
                # Only play player hit sound if velocity is significant
                if self.velocity.length() > 100:
                    audio_system.play_player_hit_sound()

            # New collision with any object, but not player
            elif currently_colliding and not was_colliding:
                # Only play environment collision sound if velocity is significant
                if self.velocity.length() > 200:
                    audio_system.play_env_collision_sound()

        # If we were colliding but aren't anymore, untie
        if self.tied_to and self.tied_to not in currently_colliding:
            self.untie_from_object()

        # Update the set of objects we're currently colliding with
        self.colliding_objects = currently_colliding

        # Remember collision state for next frame
        self.was_colliding = bool(currently_colliding)
        self.was_colliding_with_player = self.colliding_with_player

    def tie_to_object(self, obj):
        """Tie this raindrop to a game object"""
        self.tied_to = obj
        # Store the object's current position
        self.tied_to_last_pos = Vector2(obj.x, obj.y)
        # We don't stop movement completely anymore
        # Instead, reduce velocity to simulate sticking to the object
        self.velocity *= 0.1

    def untie_from_object(self):
        """Untie this raindrop from its object"""
        self.tied_to = None
        self.tied_to_last_pos = None
        # Give the raindrop a small random velocity
        self.velocity = Vector2(random.uniform(-20, 20), random.uniform(50, 100))

    def get_repulsion_force(self, obj, dt):
        """Apply a repulsion force that primarily directs the raindrop downward along the object's sides"""
        # Calculate direction from object center to raindrop
        obj_center = Vector2(obj.x + obj.width/2, obj.y + obj.height/2)
        my_pos = Vector2(self.x, self.y)

        # Direction vector pointing away from the object's center
        repulsion_dir = my_pos - obj_center

        # Only apply force if we have a non-zero direction
        if repulsion_dir.length() > 0:
            repulsion_dir = repulsion_dir.normalize()

            # Use the rect for depth calculation as an approximation
            # Create rectangle for the object
            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            # For points inside the rectangle, we need to calculate the distance to the nearest edge
            # Calculate distance to each edge
            dist_left = self.x - obj_rect.left
            dist_right = obj_rect.right - self.x
            dist_top = self.y - obj_rect.top
            dist_bottom = obj_rect.bottom - self.y

            # Find the nearest edge
            nearest_distances = [
                (dist_left, Vector2(-1, 0), "left"),    # Left edge
                (dist_right, Vector2(1, 0), "right"),   # Right edge
                (dist_top, Vector2(0, -1), "top"),      # Top edge
                (dist_bottom, Vector2(0, 1), "bottom")  # Bottom edge
            ]

            nearest_dist, nearest_dir, edge_name = min(nearest_distances, key=lambda x: x[0])

            # Modify repulsion direction to favor downward movement:
            # - For left/right edges: add strong downward component
            # - For top edge: mostly random horizontal
            # - For bottom edge: keep normal direction

            if edge_name in ["left", "right"]:
                # Add a strong downward component when near side edges
                # 80% downward, 20% outward from the edge
                repulsion_dir = nearest_dir * 0.2 + Vector2(0, 1) * 0.8
            elif edge_name == "top":
                # On top, add some random horizontal movement but mainly downward along sides
                horiz_component = random.uniform(-0.3, 0.3)  # Random slight horizontal direction
                # 70% downward, 30% random horizontal
                repulsion_dir = Vector2(horiz_component, 0.7).normalize()
            # Bottom edge keeps the natural repulsion direction

            # Ensure depth is positive and at least 1.0 for minimum effect
            depth = max(1.0, nearest_dist)

            # Scale force based on depth - deeper means stronger force
            depth_multiplier = 1.0 + (depth * DEPTH_REPULSION_MULTIPLIER)

            # Create force in the modified direction, scaled by depth
            repulsion_force = repulsion_dir * self.repulsion_force * depth_multiplier * dt

            return repulsion_force
        return Vector2(0, 0)

    def apply_repulsion_force(self, obj, dt):
        """Legacy method for tests - redirects to get_repulsion_force"""
        return self.get_repulsion_force(obj, dt)

    def draw(self, surface):
        # Draw a line from the current position downward based on velocity
        end_pos = (
            int(self.x),
            int(self.y + self.length)
        )

        # Change color based on collision state
        if self.colliding_objects:
            if self.colliding_with_player:
                # Green when colliding with player
                draw_color = (0, 255, 0)
            else:
                # More intense red when colliding with other objects
                draw_color = (255, 40, 40)
        else:
            # Default color when not colliding
            draw_color = self.color

        # Draw the raindrop as a line (original shape)
        pygame.draw.line(surface, draw_color, (int(self.x), int(self.y)), end_pos, self.width)