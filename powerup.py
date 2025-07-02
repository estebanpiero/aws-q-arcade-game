"""
AWS-Themed Power-ups for Breakout Game
Each power-up is inspired by an AWS service with appropriate effects
"""

import pygame
import random
import math
from typing import List, Tuple, Dict, Optional
from enum import Enum

class PowerUpType(Enum):
    """AWS service-inspired power-up types"""
    CLOUDWATCH_SLOW = "cloudwatch_slow"      # CloudWatch - Slows down time
    IAM_SHIELD = "iam_shield"                # IAM - Protective shield
    LAMBDA_MULTI = "lambda_multi"            # Lambda - Multiple balls
    S3_EXPAND = "s3_expand"                  # S3 - Expand paddle (more storage)
    EC2_BOOST = "ec2_boost"                  # EC2 - Speed boost for ball
    ROUTE53_REDIRECT = "route53_redirect"    # Route 53 - Ball direction control
    ELASTICACHE_FREEZE = "elasticache_freeze" # ElastiCache - Freeze ball briefly
    CLOUDFORMATION_REBUILD = "cloudformation_rebuild" # CloudFormation - Rebuild broken bricks

class PowerUp:
    """Individual power-up object that falls from destroyed bricks"""
    
    def __init__(self, x: float, y: float, powerup_type: PowerUpType):
        """
        Initialize a power-up
        
        Args:
            x: Starting x position
            y: Starting y position
            powerup_type: Type of power-up
        """
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = 30
        self.height = 20
        self.speed = 2.0
        self.active = True
        
        # Visual properties
        self.color = self._get_color()
        self.icon = self._get_icon()
        self.pulse_timer = 0
        
        # Create rect for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def _get_color(self) -> Tuple[int, int, int]:
        """Get the color associated with this power-up type"""
        color_map = {
            PowerUpType.CLOUDWATCH_SLOW: (255, 153, 0),      # Orange
            PowerUpType.IAM_SHIELD: (35, 47, 62),            # Dark blue
            PowerUpType.LAMBDA_MULTI: (146, 43, 140),        # Purple
            PowerUpType.S3_EXPAND: (35, 47, 62),             # Green-ish
            PowerUpType.EC2_BOOST: (255, 204, 0),            # Yellow
            PowerUpType.ROUTE53_REDIRECT: (135, 206, 235),   # Light blue
            PowerUpType.ELASTICACHE_FREEZE: (173, 216, 230), # Light blue
            PowerUpType.CLOUDFORMATION_REBUILD: (255, 69, 0) # Red-orange
        }
        return color_map.get(self.type, (255, 255, 255))
    
    def _get_icon(self) -> str:
        """Get the text icon for this power-up type"""
        icon_map = {
            PowerUpType.CLOUDWATCH_SLOW: "⏰",
            PowerUpType.IAM_SHIELD: "🛡️",
            PowerUpType.LAMBDA_MULTI: "λ",
            PowerUpType.S3_EXPAND: "📦",
            PowerUpType.EC2_BOOST: "⚡",
            PowerUpType.ROUTE53_REDIRECT: "🔄",
            PowerUpType.ELASTICACHE_FREEZE: "❄️",
            PowerUpType.CLOUDFORMATION_REBUILD: "🔧"
        }
        return icon_map.get(self.type, "?")
    
    def update(self, dt: float):
        """Update power-up position and animation"""
        if not self.active:
            return
        
        # Move downward
        self.y += self.speed
        self.rect.y = self.y
        
        # Update pulse animation
        self.pulse_timer += dt * 5
        
        # Deactivate if off screen
        if self.y > 600:  # Assuming screen height of 600
            self.active = False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the power-up with pulsing effect"""
        if not self.active:
            return
        
        # Calculate pulse effect
        pulse = math.sin(self.pulse_timer) * 0.2 + 1.0
        current_width = int(self.width * pulse)
        current_height = int(self.height * pulse)
        
        # Draw background
        bg_rect = pygame.Rect(
            self.x - (current_width - self.width) // 2,
            self.y - (current_height - self.height) // 2,
            current_width,
            current_height
        )
        pygame.draw.rect(screen, self.color, bg_rect)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
        
        # Draw icon text
        text_surface = font.render(self.icon, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

class PowerUpEffect:
    """Manages active power-up effects"""
    
    def __init__(self, effect_type: PowerUpType, duration: float):
        """
        Initialize a power-up effect
        
        Args:
            effect_type: Type of power-up effect
            duration: How long the effect lasts in seconds
        """
        self.type = effect_type
        self.duration = duration
        self.remaining_time = duration
        self.active = True
        
        # Effect-specific properties
        self.intensity = 1.0
        self.data = {}  # For storing effect-specific data
    
    def update(self, dt: float):
        """Update the effect timer"""
        if not self.active:
            return
        
        self.remaining_time -= dt
        if self.remaining_time <= 0:
            self.active = False
        
        # Calculate intensity (fade out in last second)
        if self.remaining_time < 1.0:
            self.intensity = self.remaining_time
        else:
            self.intensity = 1.0

class PowerUpManager:
    """Manages all power-ups and their effects"""
    
    def __init__(self):
        """Initialize the power-up manager"""
        self.powerups: List[PowerUp] = []
        self.active_effects: List[PowerUpEffect] = []
        self.font = None
        
        # Power-up spawn chances (percentage)
        self.spawn_chances = {
            PowerUpType.CLOUDWATCH_SLOW: 15,
            PowerUpType.IAM_SHIELD: 12,
            PowerUpType.LAMBDA_MULTI: 10,
            PowerUpType.S3_EXPAND: 15,
            PowerUpType.EC2_BOOST: 12,
            PowerUpType.ROUTE53_REDIRECT: 8,
            PowerUpType.ELASTICACHE_FREEZE: 10,
            PowerUpType.CLOUDFORMATION_REBUILD: 5
        }
    
    def set_font(self, font: pygame.font.Font):
        """Set the font for rendering power-up icons"""
        self.font = font
    
    def maybe_spawn_powerup(self, x: float, y: float) -> bool:
        """
        Maybe spawn a power-up at the given position (when brick is destroyed)
        
        Args:
            x: X position to spawn power-up
            y: Y position to spawn power-up
            
        Returns:
            True if a power-up was spawned
        """
        # 25% chance to spawn any power-up
        if random.random() > 0.25:
            return False
        
        # Choose which power-up to spawn based on weights
        powerup_types = list(self.spawn_chances.keys())
        weights = list(self.spawn_chances.values())
        
        chosen_type = random.choices(powerup_types, weights=weights)[0]
        
        # Create and add the power-up
        powerup = PowerUp(x, y, chosen_type)
        self.powerups.append(powerup)
        
        return True
    
    def update(self, dt: float):
        """Update all power-ups and effects"""
        # Update falling power-ups
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if not powerup.active:
                self.powerups.remove(powerup)
        
        # Update active effects
        for effect in self.active_effects[:]:
            effect.update(dt)
            if not effect.active:
                self.active_effects.remove(effect)
    
    def check_paddle_collision(self, paddle_rect: pygame.Rect) -> Optional[PowerUpType]:
        """
        Check if any power-up collides with the paddle
        
        Args:
            paddle_rect: Paddle's collision rectangle
            
        Returns:
            PowerUpType if collision occurred, None otherwise
        """
        for powerup in self.powerups[:]:
            if powerup.active and powerup.rect.colliderect(paddle_rect):
                powerup.active = False
                self.powerups.remove(powerup)
                return powerup.type
        
        return None
    
    def activate_powerup(self, powerup_type: PowerUpType):
        """
        Activate a power-up effect
        
        Args:
            powerup_type: Type of power-up to activate
        """
        # Define effect durations
        durations = {
            PowerUpType.CLOUDWATCH_SLOW: 8.0,
            PowerUpType.IAM_SHIELD: 10.0,
            PowerUpType.LAMBDA_MULTI: 0.1,  # Instant effect
            PowerUpType.S3_EXPAND: 12.0,
            PowerUpType.EC2_BOOST: 6.0,
            PowerUpType.ROUTE53_REDIRECT: 5.0,
            PowerUpType.ELASTICACHE_FREEZE: 3.0,
            PowerUpType.CLOUDFORMATION_REBUILD: 0.1  # Instant effect
        }
        
        duration = durations.get(powerup_type, 5.0)
        
        # Remove existing effect of the same type (no stacking)
        self.active_effects = [e for e in self.active_effects if e.type != powerup_type]
        
        # Add new effect
        effect = PowerUpEffect(powerup_type, duration)
        self.active_effects.append(effect)
    
    def has_effect(self, effect_type: PowerUpType) -> bool:
        """Check if a specific effect is currently active"""
        return any(e.type == effect_type and e.active for e in self.active_effects)
    
    def get_effect_intensity(self, effect_type: PowerUpType) -> float:
        """Get the intensity of a specific effect (0.0 to 1.0)"""
        for effect in self.active_effects:
            if effect.type == effect_type and effect.active:
                return effect.intensity
        return 0.0
    
    def get_time_multiplier(self) -> float:
        """Get the current time multiplier (for CloudWatch slow effect)"""
        if self.has_effect(PowerUpType.CLOUDWATCH_SLOW):
            return 0.3  # 30% of normal speed
        return 1.0
    
    def has_shield(self) -> bool:
        """Check if IAM shield is active"""
        return self.has_effect(PowerUpType.IAM_SHIELD)
    
    def get_paddle_size_multiplier(self) -> float:
        """Get paddle size multiplier (for S3 expand effect)"""
        if self.has_effect(PowerUpType.S3_EXPAND):
            return 1.5  # 50% larger
        return 1.0
    
    def get_ball_speed_multiplier(self) -> float:
        """Get ball speed multiplier (for EC2 boost effect)"""
        if self.has_effect(PowerUpType.EC2_BOOST):
            return 1.4  # 40% faster
        return 1.0
    
    def should_freeze_ball(self) -> bool:
        """Check if ball should be frozen (ElastiCache effect)"""
        return self.has_effect(PowerUpType.ELASTICACHE_FREEZE)
    
    def can_redirect_ball(self) -> bool:
        """Check if ball direction can be controlled (Route 53 effect)"""
        return self.has_effect(PowerUpType.ROUTE53_REDIRECT)
    
    def draw(self, screen: pygame.Surface):
        """Draw all power-ups"""
        if not self.font:
            return
        
        for powerup in self.powerups:
            powerup.draw(screen, self.font)
    
    def draw_effect_indicators(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw indicators for active effects"""
        y_offset = 10
        
        for effect in self.active_effects:
            if not effect.active:
                continue
            
            # Get effect info
            effect_names = {
                PowerUpType.CLOUDWATCH_SLOW: "CloudWatch: Slow Time",
                PowerUpType.IAM_SHIELD: "IAM: Shield Active",
                PowerUpType.LAMBDA_MULTI: "Lambda: Multi-Ball",
                PowerUpType.S3_EXPAND: "S3: Expanded Paddle",
                PowerUpType.EC2_BOOST: "EC2: Speed Boost",
                PowerUpType.ROUTE53_REDIRECT: "Route 53: Ball Control",
                PowerUpType.ELASTICACHE_FREEZE: "ElastiCache: Freeze",
                PowerUpType.CLOUDFORMATION_REBUILD: "CloudFormation: Rebuild"
            }
            
            effect_name = effect_names.get(effect.type, "Unknown Effect")
            time_left = int(effect.remaining_time) + 1
            
            # Create text with time remaining
            text = f"{effect_name} ({time_left}s)"
            
            # Fade color based on remaining time
            alpha = int(255 * effect.intensity)
            color = (255, 255, 255) if alpha > 128 else (128, 128, 128)
            
            # Render text
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (10, y_offset))
            
            y_offset += 25
    
    def clear_all_effects(self):
        """Clear all active effects (for game reset)"""
        self.active_effects.clear()
    
    def clear_all_powerups(self):
        """Clear all falling power-ups (for game reset)"""
        self.powerups.clear()

def get_powerup_descriptions() -> Dict[PowerUpType, str]:
    """Get descriptions for all power-up types"""
    return {
        PowerUpType.CLOUDWATCH_SLOW: "CloudWatch monitors and slows down time, giving you more reaction time",
        PowerUpType.IAM_SHIELD: "IAM provides identity protection - shields you from losing a life once",
        PowerUpType.LAMBDA_MULTI: "Lambda functions scale instantly - creates multiple balls",
        PowerUpType.S3_EXPAND: "S3 provides scalable storage - expands your paddle size",
        PowerUpType.EC2_BOOST: "EC2 provides compute power - boosts ball speed for more impact",
        PowerUpType.ROUTE53_REDIRECT: "Route 53 manages traffic routing - lets you control ball direction",
        PowerUpType.ELASTICACHE_FREEZE: "ElastiCache provides fast access - temporarily freezes the ball",
        PowerUpType.CLOUDFORMATION_REBUILD: "CloudFormation rebuilds infrastructure - restores some destroyed bricks"
    }
