"""
Ball class for AWS Breakout Game
Handles ball physics, collision detection, and power-up effects
"""

import pygame
import math
import random
from typing import Tuple, List, Optional

class Ball:
    """Ball object with physics and collision detection"""
    
    def __init__(self, x: float, y: float, radius: int = 8):
        """
        Initialize the ball
        
        Args:
            x: Starting x position
            y: Starting y position
            radius: Ball radius in pixels
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = 300.0  # Base speed in pixels per second
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.active = True
        self.launched = False
        
        # Visual properties
        self.color = (255, 255, 255)
        self.trail_positions = []  # For visual trail effect
        self.max_trail_length = 8
        
        # Power-up effects
        self.frozen = False
        self.freeze_timer = 0.0
        
        # Create rect for collision detection
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    
    def launch(self, angle_degrees: float = None):
        """
        Launch the ball at a specific angle
        
        Args:
            angle_degrees: Launch angle in degrees (None for random)
        """
        if angle_degrees is None:
            # Random angle between 45 and 135 degrees (upward)
            angle_degrees = random.uniform(45, 135)
        
        # Convert to radians
        angle_radians = math.radians(angle_degrees)
        
        # Set velocity components
        self.velocity_x = self.speed * math.cos(angle_radians)
        self.velocity_y = -self.speed * math.sin(angle_radians)  # Negative for upward
        
        self.launched = True
    
    def update(self, dt: float, screen_width: int, screen_height: int, 
               time_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        """
        Update ball position and handle screen boundaries
        
        Args:
            dt: Delta time in seconds
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            time_multiplier: Time multiplier for slow-motion effects
            speed_multiplier: Speed multiplier for boost effects
        """
        if not self.active or not self.launched:
            return
        
        # Handle freeze effect
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False
            return
        
        # Apply time and speed multipliers
        effective_dt = dt * time_multiplier
        effective_speed = self.speed * speed_multiplier
        
        # Update trail positions
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Update position
        self.x += self.velocity_x * effective_dt
        self.y += self.velocity_y * effective_dt
        
        # Update collision rect
        self.rect.center = (self.x, self.y)
        
        # Handle screen boundaries
        self._handle_screen_collision(screen_width, screen_height)
    
    def _handle_screen_collision(self, screen_width: int, screen_height: int):
        """Handle collision with screen boundaries"""
        # Left and right walls
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.velocity_x = abs(self.velocity_x)  # Bounce right
        elif self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.velocity_x = -abs(self.velocity_x)  # Bounce left
        
        # Top wall
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.velocity_y = abs(self.velocity_y)  # Bounce down
        
        # Bottom wall (ball lost)
        if self.y - self.radius >= screen_height:
            self.active = False
    
    def bounce_off_paddle(self, paddle_x: float, paddle_y: float, paddle_width: float):
        """
        Handle collision with paddle
        
        Args:
            paddle_x: Paddle center x position
            paddle_y: Paddle top y position
            paddle_width: Paddle width
        """
        # Calculate hit position relative to paddle center (-1 to 1)
        hit_pos = (self.x - paddle_x) / (paddle_width / 2)
        hit_pos = max(-1, min(1, hit_pos))  # Clamp to [-1, 1]
        
        # Calculate new angle based on hit position
        # Center hit: 90 degrees, edge hits: 30-150 degrees
        base_angle = 90  # Straight up
        angle_variation = 60  # +/- 60 degrees
        new_angle = base_angle + (hit_pos * angle_variation)
        
        # Convert to radians and set new velocity
        angle_radians = math.radians(new_angle)
        current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        
        self.velocity_x = current_speed * math.cos(angle_radians)
        self.velocity_y = -current_speed * math.sin(angle_radians)
        
        # Ensure ball is above paddle
        self.y = paddle_y - self.radius - 1
    
    def bounce_off_brick(self, brick_rect: pygame.Rect) -> str:
        """
        Handle collision with a brick
        
        Args:
            brick_rect: Rectangle of the brick that was hit
            
        Returns:
            String indicating which side was hit ('top', 'bottom', 'left', 'right')
        """
        # Calculate overlap on each side
        overlap_left = (self.x + self.radius) - brick_rect.left
        overlap_right = brick_rect.right - (self.x - self.radius)
        overlap_top = (self.y + self.radius) - brick_rect.top
        overlap_bottom = brick_rect.bottom - (self.y - self.radius)
        
        # Find the smallest overlap (that's the side we hit)
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
        
        if min_overlap == overlap_left:
            # Hit left side of brick
            self.velocity_x = -abs(self.velocity_x)
            self.x = brick_rect.left - self.radius - 1
            return 'left'
        elif min_overlap == overlap_right:
            # Hit right side of brick
            self.velocity_x = abs(self.velocity_x)
            self.x = brick_rect.right + self.radius + 1
            return 'right'
        elif min_overlap == overlap_top:
            # Hit top side of brick
            self.velocity_y = -abs(self.velocity_y)
            self.y = brick_rect.top - self.radius - 1
            return 'top'
        else:
            # Hit bottom side of brick
            self.velocity_y = abs(self.velocity_y)
            self.y = brick_rect.bottom + self.radius + 1
            return 'bottom'
    
    def freeze(self, duration: float):
        """
        Freeze the ball for a specified duration
        
        Args:
            duration: Freeze duration in seconds
        """
        self.frozen = True
        self.freeze_timer = duration
    
    def redirect(self, target_x: float, target_y: float):
        """
        Redirect ball towards a target position (Route 53 power-up)
        
        Args:
            target_x: Target x position
            target_y: Target y position
        """
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize and apply current speed
            current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            self.velocity_x = (dx / distance) * current_speed
            self.velocity_y = (dy / distance) * current_speed
    
    def draw(self, screen: pygame.Surface):
        """Draw the ball with trail effect"""
        if not self.active:
            return
        
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail_positions):
            alpha = (i + 1) / len(self.trail_positions)
            trail_radius = int(self.radius * alpha * 0.7)
            trail_color = (
                int(self.color[0] * alpha),
                int(self.color[1] * alpha),
                int(self.color[2] * alpha)
            )
            if trail_radius > 0:
                pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), trail_radius)
        
        # Draw main ball
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw freeze effect
        if self.frozen:
            # Draw ice effect around ball
            ice_color = (173, 216, 230, 128)  # Light blue with transparency
            pygame.draw.circle(screen, (173, 216, 230), (int(self.x), int(self.y)), self.radius + 3, 2)
    
    def reset(self, x: float, y: float):
        """
        Reset ball to initial position
        
        Args:
            x: Reset x position
            y: Reset y position
        """
        self.x = x
        self.y = y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.active = True
        self.launched = False
        self.frozen = False
        self.freeze_timer = 0.0
        self.trail_positions.clear()
        self.rect.center = (x, y)

class MultiBall:
    """Manages multiple balls for Lambda power-up effect"""
    
    def __init__(self):
        """Initialize the multi-ball manager"""
        self.balls: List[Ball] = []
        self.main_ball_index = 0
    
    def add_ball(self, ball: Ball):
        """Add a ball to the collection"""
        self.balls.append(ball)
    
    def create_additional_balls(self, main_ball: Ball, count: int = 2):
        """
        Create additional balls from the main ball (Lambda effect)
        
        Args:
            main_ball: The main ball to clone
            count: Number of additional balls to create
        """
        for i in range(count):
            new_ball = Ball(main_ball.x, main_ball.y, main_ball.radius)
            new_ball.speed = main_ball.speed
            new_ball.active = True
            new_ball.launched = True
            
            # Launch at different angles
            angle = 45 + (i * 45)  # Spread balls at different angles
            new_ball.launch(angle)
            
            self.balls.append(new_ball)
    
    def update_all(self, dt: float, screen_width: int, screen_height: int,
                   time_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        """Update all balls"""
        for ball in self.balls[:]:
            ball.update(dt, screen_width, screen_height, time_multiplier, speed_multiplier)
            if not ball.active:
                self.balls.remove(ball)
    
    def draw_all(self, screen: pygame.Surface):
        """Draw all balls"""
        for ball in self.balls:
            ball.draw(screen)
    
    def get_active_balls(self) -> List[Ball]:
        """Get list of active balls"""
        return [ball for ball in self.balls if ball.active]
    
    def has_active_balls(self) -> bool:
        """Check if any balls are still active"""
        return any(ball.active for ball in self.balls)
    
    def clear_all(self):
        """Remove all balls"""
        self.balls.clear()
