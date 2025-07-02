"""
Brick class for AWS Breakout Game
Represents individual bricks that form AWS service logos
"""

import pygame
import random
from typing import Tuple, Dict, Optional

class Brick:
    """Individual brick that can be destroyed by the ball"""
    
    def __init__(self, x: int, y: int, width: int = 40, height: int = 20, 
                 color: str = 'blue', durability: int = 1):
        """
        Initialize a brick
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            width: Brick width in pixels
            height: Brick height in pixels
            color: Brick color name
            durability: Number of hits required to destroy (1-3)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_name = color
        self.max_durability = durability
        self.current_durability = durability
        self.active = True
        
        # Visual properties
        self.color = self._get_color_rgb(color)
        self.border_color = self._get_border_color()
        
        # Animation properties
        self.hit_animation_timer = 0.0
        self.destruction_animation_timer = 0.0
        self.is_being_destroyed = False
        
        # Particle effects
        self.particles = []
        
        # Create collision rectangle
        self.rect = pygame.Rect(x, y, width, height)
    
    def _get_color_rgb(self, color_name: str) -> Tuple[int, int, int]:
        """
        Get RGB color values for a color name
        
        Args:
            color_name: Name of the color
            
        Returns:
            RGB tuple
        """
        color_map = {
            'orange': (255, 153, 0),      # EC2 orange
            'green': (46, 125, 50),       # S3 green
            'blue': (25, 118, 210),       # AWS blue
            'purple': (146, 43, 140),     # Lambda purple
            'red': (214, 51, 132),        # Error red
            'yellow': (255, 204, 0),      # Warning yellow
            'light_blue': (135, 206, 235), # Light blue
            'dark_blue': (25, 25, 112),   # Dark blue
            'gray': (128, 128, 128),      # Neutral gray
        }
        return color_map.get(color_name, (25, 118, 210))  # Default to AWS blue
    
    def _get_border_color(self) -> Tuple[int, int, int]:
        """Get border color (slightly darker than main color)"""
        r, g, b = self.color
        return (max(0, r - 30), max(0, g - 30), max(0, b - 30))
    
    def hit(self) -> bool:
        """
        Handle brick being hit by ball
        
        Returns:
            True if brick was destroyed, False otherwise
        """
        if not self.active:
            return False
        
        self.current_durability -= 1
        self.hit_animation_timer = 0.3  # 300ms hit animation
        
        # Create hit particles
        self._create_hit_particles()
        
        if self.current_durability <= 0:
            self.is_being_destroyed = True
            self.destruction_animation_timer = 0.5  # 500ms destruction animation
            self._create_destruction_particles()
            return True
        
        # Update color based on remaining durability
        self._update_color_for_durability()
        return False
    
    def _create_hit_particles(self):
        """Create particle effects when brick is hit"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Create 3-5 particles
        for _ in range(random.randint(3, 5)):
            particle = {
                'x': center_x + random.randint(-10, 10),
                'y': center_y + random.randint(-10, 10),
                'vx': random.uniform(-50, 50),
                'vy': random.uniform(-100, -20),
                'life': 0.5,
                'max_life': 0.5,
                'color': self.color
            }
            self.particles.append(particle)
    
    def _create_destruction_particles(self):
        """Create particle effects when brick is destroyed"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Create more particles for destruction
        for _ in range(random.randint(8, 12)):
            particle = {
                'x': center_x + random.randint(-self.width//2, self.width//2),
                'y': center_y + random.randint(-self.height//2, self.height//2),
                'vx': random.uniform(-100, 100),
                'vy': random.uniform(-150, -50),
                'life': 1.0,
                'max_life': 1.0,
                'color': self.color
            }
            self.particles.append(particle)
    
    def _update_color_for_durability(self):
        """Update brick color based on remaining durability"""
        if self.max_durability == 1:
            return  # Single-hit bricks don't change color
        
        # Fade color as durability decreases
        durability_ratio = self.current_durability / self.max_durability
        base_color = self._get_color_rgb(self.color_name)
        
        # Darken the color as durability decreases
        self.color = (
            int(base_color[0] * (0.5 + 0.5 * durability_ratio)),
            int(base_color[1] * (0.5 + 0.5 * durability_ratio)),
            int(base_color[2] * (0.5 + 0.5 * durability_ratio))
        )
        self.border_color = self._get_border_color()
    
    def update(self, dt: float):
        """
        Update brick animations and particles
        
        Args:
            dt: Delta time in seconds
        """
        # Update hit animation
        if self.hit_animation_timer > 0:
            self.hit_animation_timer -= dt
        
        # Update destruction animation
        if self.is_being_destroyed:
            self.destruction_animation_timer -= dt
            if self.destruction_animation_timer <= 0:
                self.active = False
        
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            # Update particle position
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 200 * dt  # Gravity
    
    def draw(self, screen: pygame.Surface):
        """Draw the brick with animations and effects"""
        if not self.active and not self.is_being_destroyed:
            return
        
        # Calculate animation effects
        shake_x = 0
        shake_y = 0
        alpha = 255
        
        if self.hit_animation_timer > 0:
            # Shake effect when hit
            shake_intensity = self.hit_animation_timer / 0.3
            shake_x = random.randint(-2, 2) * shake_intensity
            shake_y = random.randint(-2, 2) * shake_intensity
        
        if self.is_being_destroyed:
            # Fade out during destruction
            alpha = int(255 * (self.destruction_animation_timer / 0.5))
        
        # Draw main brick
        brick_rect = pygame.Rect(
            self.x + shake_x,
            self.y + shake_y,
            self.width,
            self.height
        )
        
        # Apply alpha if needed
        if alpha < 255:
            # Create surface with alpha for fading effect
            brick_surface = pygame.Surface((self.width, self.height))
            brick_surface.set_alpha(alpha)
            brick_surface.fill(self.color)
            screen.blit(brick_surface, (brick_rect.x, brick_rect.y))
            
            # Draw border with alpha
            border_surface = pygame.Surface((self.width, self.height))
            border_surface.set_alpha(alpha)
            pygame.draw.rect(border_surface, self.border_color, 
                           pygame.Rect(0, 0, self.width, self.height), 2)
            screen.blit(border_surface, (brick_rect.x, brick_rect.y))
        else:
            pygame.draw.rect(screen, self.color, brick_rect)
            pygame.draw.rect(screen, self.border_color, brick_rect, 2)
        
        # Draw durability indicator for multi-hit bricks
        if self.max_durability > 1 and self.active and not self.is_being_destroyed:
            self._draw_durability_indicator(screen, brick_rect)
        
        # Draw particles
        self._draw_particles(screen)
    
    def _draw_durability_indicator(self, screen: pygame.Surface, brick_rect: pygame.Rect):
        """Draw durability indicator on multi-hit bricks"""
        if self.current_durability <= 1:
            return
        
        # Draw small dots to indicate remaining hits
        dot_size = 3
        dot_spacing = 6
        start_x = brick_rect.centerx - ((self.current_durability - 1) * dot_spacing) // 2
        
        for i in range(self.current_durability):
            dot_x = start_x + i * dot_spacing
            dot_y = brick_rect.centery
            pygame.draw.circle(screen, (255, 255, 255), (dot_x, dot_y), dot_size)
    
    def _draw_particles(self, screen: pygame.Surface):
        """Draw particle effects"""
        for particle in self.particles:
            life_ratio = particle['life'] / particle['max_life']
            alpha = int(255 * life_ratio)
            size = max(1, int(3 * life_ratio))
            
            # Create particle surface with alpha
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)
            pygame.draw.circle(particle_surface, particle['color'], (size, size), size)
            screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
    
    def get_score_value(self) -> int:
        """
        Get the score value for destroying this brick
        
        Returns:
            Score points for this brick
        """
        base_score = 10
        durability_multiplier = self.max_durability
        
        # Color-based score multipliers
        color_multipliers = {
            'red': 3,
            'orange': 2,
            'yellow': 2,
            'purple': 2,
            'blue': 1,
            'green': 1,
            'light_blue': 1,
            'dark_blue': 1,
            'gray': 1
        }
        
        color_multiplier = color_multipliers.get(self.color_name, 1)
        return base_score * durability_multiplier * color_multiplier
    
    def is_destroyed(self) -> bool:
        """Check if brick is completely destroyed"""
        return not self.active and not self.is_being_destroyed
