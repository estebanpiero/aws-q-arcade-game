"""
Paddle class for AWS Breakout Game
Handles paddle movement, collision detection, and power-up effects
"""

import pygame
from typing import Tuple

class Paddle:
    """Player-controlled paddle at the bottom of the screen"""
    
    def __init__(self, x: float, y: float, width: int = 100, height: int = 15):
        """
        Initialize the paddle
        
        Args:
            x: Starting x position (center)
            y: Starting y position (top)
            width: Paddle width in pixels
            height: Paddle height in pixels
        """
        self.base_width = width
        self.base_height = height
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.speed = 400.0  # Movement speed in pixels per second
        
        # Visual properties
        self.color = (255, 255, 255)
        self.border_color = (200, 200, 200)
        
        # Power-up effects
        self.size_multiplier = 1.0
        self.glow_effect = False
        self.glow_timer = 0.0
        
        # Create collision rectangle
        self.rect = pygame.Rect(x - width // 2, y, width, height)
    
    def update(self, dt: float, screen_width: int, size_multiplier: float = 1.0):
        """
        Update paddle properties and position constraints
        
        Args:
            dt: Delta time in seconds
            screen_width: Screen width for boundary checking
            size_multiplier: Size multiplier from power-ups (S3 expand effect)
        """
        # Update size based on power-ups
        self.size_multiplier = size_multiplier
        self.width = int(self.base_width * size_multiplier)
        
        # Update glow effect timer
        if self.glow_effect:
            self.glow_timer += dt * 10  # Fast pulsing
        
        # Constrain paddle to screen boundaries
        half_width = self.width // 2
        if self.x - half_width < 0:
            self.x = half_width
        elif self.x + half_width > screen_width:
            self.x = screen_width - half_width
        
        # Update collision rectangle
        self.rect = pygame.Rect(self.x - half_width, self.y, self.width, self.height)
    
    def move_left(self, dt: float):
        """
        Move paddle left
        
        Args:
            dt: Delta time in seconds
        """
        self.x -= self.speed * dt
    
    def move_right(self, dt: float):
        """
        Move paddle right
        
        Args:
            dt: Delta time in seconds
        """
        self.x += self.speed * dt
    
    def handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float):
        """
        Handle keyboard input for paddle movement
        
        Args:
            keys: Pygame keys state
            dt: Delta time in seconds
        """
        # Left movement (Left arrow or A key)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_left(dt)
        
        # Right movement (Right arrow or D key)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_right(dt)
    
    def check_ball_collision(self, ball_x: float, ball_y: float, ball_radius: int) -> bool:
        """
        Check if a ball collides with the paddle
        
        Args:
            ball_x: Ball x position
            ball_y: Ball y position
            ball_radius: Ball radius
            
        Returns:
            True if collision detected
        """
        # Create ball rect for collision detection
        ball_rect = pygame.Rect(
            ball_x - ball_radius,
            ball_y - ball_radius,
            ball_radius * 2,
            ball_radius * 2
        )
        
        return self.rect.colliderect(ball_rect)
    
    def activate_glow(self, duration: float = 2.0):
        """
        Activate glow effect (for power-up feedback)
        
        Args:
            duration: Glow duration in seconds
        """
        self.glow_effect = True
        self.glow_timer = 0.0
        # Could add a timer to turn off glow after duration
    
    def draw(self, screen: pygame.Surface):
        """Draw the paddle with visual effects"""
        # Draw glow effect if active
        if self.glow_effect:
            import math
            glow_intensity = (math.sin(self.glow_timer) + 1) / 2  # 0 to 1
            glow_color = (
                int(255 * glow_intensity),
                int(255 * glow_intensity),
                int(100 + 155 * glow_intensity)
            )
            
            # Draw glow outline
            glow_rect = pygame.Rect(
                self.rect.x - 2,
                self.rect.y - 2,
                self.rect.width + 4,
                self.rect.height + 4
            )
            pygame.draw.rect(screen, glow_color, glow_rect, 2)
        
        # Draw main paddle
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw size indicator if expanded
        if self.size_multiplier > 1.0:
            # Draw S3 expansion indicator
            center_x = self.rect.centerx
            center_y = self.rect.centery
            
            # Draw small S3 icon
            font = pygame.font.Font(None, 16)
            text = font.render("S3", True, (0, 255, 0))
            text_rect = text.get_rect(center=(center_x, center_y))
            screen.blit(text, text_rect)
    
    def get_center_x(self) -> float:
        """Get the center x position of the paddle"""
        return self.x
    
    def get_top_y(self) -> float:
        """Get the top y position of the paddle"""
        return self.y
    
    def get_width(self) -> float:
        """Get the current width of the paddle"""
        return self.width
    
    def reset(self, x: float, y: float):
        """
        Reset paddle to initial position and state
        
        Args:
            x: Reset x position
            y: Reset y position
        """
        self.x = x
        self.y = y
        self.width = self.base_width
        self.height = self.base_height
        self.size_multiplier = 1.0
        self.glow_effect = False
        self.glow_timer = 0.0
        self.rect = pygame.Rect(x - self.base_width // 2, y, self.base_width, self.base_height)
