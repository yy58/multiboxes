"""
Player class for the multiplayer game.

This module defines the Player class which represents a player in the game.
Each player has a position, velocity, rotation, and visual representation.
"""

import pygame
import uuid
import math

class Player:
    """
    Represents a player in the multiplayer game.
    
    Each player has:
    - A unique ID (generated automatically)
    - Position (x, y coordinates)
    - Velocity (dx, dy for movement)
    - Rotation angle
    - Visual representation (a white square)
    """
    
    def __init__(self, x, y):
        """
        Initialize a new player at the given position.
        
        Args:
            x (float): Initial x-coordinate
            y (float): Initial y-coordinate
        """
        # Position coordinates
        self.x = x
        self.y = y
        
        # Velocity components (change in position per frame)
        self.dx = 0
        self.dy = 0
        
        # Rotation angle in degrees
        self.angle = 45
        
        # Visual properties
        self.size = 10
        
        # Generate a unique identifier for this player
        # UUID4 creates a random unique string
        self.id = str(uuid.uuid4())
        
        # Create the visual representation (a white square)
        self.surface = pygame.Surface((self.size, self.size))
        self.surface.fill((255, 255, 255))  # White color (RGB)

    def set_position(self, x, y):
        """
        Update the player's position.
        
        This is typically called when receiving position updates from the server.
        
        Args:
            x (float): New x-coordinate
            y (float): New y-coordinate
        """
        self.x = x
        self.y = y

    def set_rotation(self, angle):
        """
        Update the player's rotation angle.
        
        Args:
            angle (float): New angle in radians (converted to degrees for display)
        """
        # Convert from radians (physics engine) to degrees (pygame)
        self.angle = math.degrees(angle)

    def set_velocity(self, dx, dy):
        """
        Update the player's velocity.
        
        Args:
            dx (float): Change in x-coordinate per frame
            dy (float): Change in y-coordinate per frame
        """
        self.dx = dx
        self.dy = dy

    def move(self):
        """
        Update the player's position based on current velocity.
        
        This is called each frame to move the player based on their velocity.
        """
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        """
        Draw the player on the given screen.
        
        The player is drawn as a rotated white square at their current position.
        
        Args:
            screen (pygame.Surface): The screen surface to draw on
        """
        # Rotate the player's surface based on current angle
        surf = pygame.transform.rotate(self.surface.convert_alpha(), self.angle)
        
        # Get a rectangle centered on the player's position
        rect = surf.get_rect(center=(self.x, self.y))
        
        # Draw the rotated surface on the screen
        screen.blit(surf, rect)
