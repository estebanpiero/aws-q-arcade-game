"""
Game State Management for AWS Breakout Game
Handles scoring, lives, game states, and UI elements
"""

import pygame
from enum import Enum
from typing import Dict, List, Tuple, Optional

class GameState(Enum):
    """Different states the game can be in"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    GAME_WON = "game_won"

class GameStateManager:
    """Manages game state, scoring, and UI elements"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        """
        Initialize the game state manager
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Game state
        self.current_state = GameState.MENU
        self.previous_state = GameState.MENU
        
        # Player stats
        self.score = 0
        self.lives = 3
        self.max_lives = 3
        self.level_score = 0
        self.combo_multiplier = 1
        self.combo_count = 0
        self.combo_timer = 0.0
        
        # High score tracking
        self.high_score = 0
        self.high_score_file = "high_score.txt"
        self._load_high_score()
        
        # UI elements
        self.fonts = {}
        self.ui_elements = {}
        self.messages = []
        
        # Game statistics
        self.total_bricks_destroyed = 0
        self.total_powerups_collected = 0
        self.levels_completed = 0
        self.game_start_time = 0.0
        self.level_start_time = 0.0
        
        # Initialize fonts (will be set properly when pygame is initialized)
        self._init_fonts()
    
    def _init_fonts(self):
        """Initialize fonts for UI rendering"""
        try:
            self.fonts = {
                'large': pygame.font.Font(None, 48),
                'medium': pygame.font.Font(None, 32),
                'small': pygame.font.Font(None, 24),
                'tiny': pygame.font.Font(None, 16)
            }
        except:
            # Fallback if pygame not initialized yet
            self.fonts = {}
    
    def _load_high_score(self):
        """Load high score from file"""
        try:
            with open(self.high_score_file, 'r') as f:
                self.high_score = int(f.read().strip())
        except:
            self.high_score = 0
    
    def _save_high_score(self):
        """Save high score to file"""
        try:
            with open(self.high_score_file, 'w') as f:
                f.write(str(self.high_score))
        except Exception as e:
            print(f"Error saving high score: {e}")
    
    def change_state(self, new_state: GameState):
        """
        Change the current game state
        
        Args:
            new_state: The new state to transition to
        """
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Handle state-specific initialization
        if new_state == GameState.PLAYING:
            if self.previous_state == GameState.MENU:
                self.start_new_game()
            elif self.previous_state == GameState.LEVEL_COMPLETE:
                self.start_new_level()
        elif new_state == GameState.GAME_OVER:
            self._handle_game_over()
    
    def start_new_game(self):
        """Initialize a new game"""
        self.score = 0
        self.lives = self.max_lives
        self.level_score = 0
        self.combo_multiplier = 1
        self.combo_count = 0
        self.combo_timer = 0.0
        self.total_bricks_destroyed = 0
        self.total_powerups_collected = 0
        self.levels_completed = 0
        self.game_start_time = pygame.time.get_ticks() / 1000.0
        self.level_start_time = self.game_start_time
        self.messages.clear()
        
        self.add_message("New Game Started!", 2.0, (0, 255, 0))
    
    def start_new_level(self):
        """Initialize a new level"""
        self.level_score = 0
        self.combo_multiplier = 1
        self.combo_count = 0
        self.combo_timer = 0.0
        self.level_start_time = pygame.time.get_ticks() / 1000.0
        self.levels_completed += 1
        
        self.add_message(f"Level {self.levels_completed} Started!", 2.0, (255, 255, 0))
    
    def _handle_game_over(self):
        """Handle game over state"""
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
            self.add_message("NEW HIGH SCORE!", 5.0, (255, 215, 0))
        
        game_time = pygame.time.get_ticks() / 1000.0 - self.game_start_time
        self.add_message(f"Game Over! Time: {game_time:.1f}s", 5.0, (255, 0, 0))
    
    def add_score(self, points: int, brick_color: str = None):
        """
        Add points to the score with combo system
        
        Args:
            points: Base points to add
            brick_color: Color of the brick for bonus calculation
        """
        # Apply combo multiplier
        final_points = int(points * self.combo_multiplier)
        
        # Color-based bonuses
        color_bonuses = {
            'red': 1.5,
            'orange': 1.3,
            'purple': 1.3,
            'yellow': 1.2,
            'blue': 1.0,
            'green': 1.0,
            'light_blue': 1.0
        }
        
        if brick_color:
            bonus = color_bonuses.get(brick_color, 1.0)
            final_points = int(final_points * bonus)
        
        self.score += final_points
        self.level_score += final_points
        
        # Update combo system
        self.combo_count += 1
        self.combo_timer = 3.0  # 3 seconds to maintain combo
        
        if self.combo_count >= 5:
            self.combo_multiplier = min(4.0, 1.0 + (self.combo_count - 5) * 0.1)
        
        # Show score popup
        if final_points > points:
            self.add_message(f"+{final_points} (x{self.combo_multiplier:.1f})", 1.0, (255, 255, 0))
        else:
            self.add_message(f"+{final_points}", 1.0, (255, 255, 255))
    
    def lose_life(self):
        """
        Player loses a life
        
        Returns:
            True if game over, False if lives remaining
        """
        self.lives -= 1
        self.combo_multiplier = 1.0
        self.combo_count = 0
        self.combo_timer = 0.0
        
        if self.lives <= 0:
            self.change_state(GameState.GAME_OVER)
            return True
        else:
            self.add_message(f"Lives remaining: {self.lives}", 2.0, (255, 100, 100))
            return False
    
    def collect_powerup(self, powerup_type: str):
        """
        Handle power-up collection
        
        Args:
            powerup_type: Type of power-up collected
        """
        self.total_powerups_collected += 1
        self.add_score(50)  # Bonus points for power-up
        
        # Power-up specific messages
        powerup_messages = {
            'cloudwatch_slow': "CloudWatch: Time Slowed!",
            'iam_shield': "IAM: Shield Activated!",
            'lambda_multi': "Lambda: Multi-Ball!",
            's3_expand': "S3: Paddle Expanded!",
            'ec2_boost': "EC2: Speed Boost!",
            'route53_redirect': "Route 53: Ball Control!",
            'elasticache_freeze': "ElastiCache: Ball Frozen!",
            'cloudformation_rebuild': "CloudFormation: Bricks Rebuilt!"
        }
        
        message = powerup_messages.get(powerup_type, "Power-up Collected!")
        self.add_message(message, 2.0, (0, 255, 255))
    
    def brick_destroyed(self, brick_color: str, brick_score: int):
        """
        Handle brick destruction
        
        Args:
            brick_color: Color of the destroyed brick
            brick_score: Score value of the brick
        """
        self.total_bricks_destroyed += 1
        self.add_score(brick_score, brick_color)
    
    def update(self, dt: float):
        """
        Update game state timers and systems
        
        Args:
            dt: Delta time in seconds
        """
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_multiplier = 1.0
                self.combo_count = 0
        
        # Update messages
        for message in self.messages[:]:
            message['duration'] -= dt
            if message['duration'] <= 0:
                self.messages.remove(message)
    
    def add_message(self, text: str, duration: float, color: Tuple[int, int, int]):
        """
        Add a temporary message to display
        
        Args:
            text: Message text
            duration: How long to display the message
            color: RGB color tuple
        """
        message = {
            'text': text,
            'duration': duration,
            'color': color,
            'y_offset': len(self.messages) * 25
        }
        self.messages.append(message)
    
    def draw_ui(self, screen: pygame.Surface, level_info: Dict = None):
        """
        Draw the game UI
        
        Args:
            screen: Pygame surface to draw on
            level_info: Information about the current level
        """
        if not self.fonts:
            self._init_fonts()
        
        # Draw based on current state
        if self.current_state == GameState.MENU:
            self._draw_menu(screen)
        elif self.current_state == GameState.PLAYING:
            self._draw_game_ui(screen, level_info)
        elif self.current_state == GameState.PAUSED:
            self._draw_game_ui(screen, level_info)
            self._draw_pause_overlay(screen)
        elif self.current_state == GameState.LEVEL_COMPLETE:
            self._draw_level_complete(screen, level_info)
        elif self.current_state == GameState.GAME_OVER:
            self._draw_game_over(screen)
        elif self.current_state == GameState.GAME_WON:
            self._draw_game_won(screen)
        
        # Draw messages
        self._draw_messages(screen)
    
    def _draw_menu(self, screen: pygame.Surface):
        """Draw the main menu"""
        # Title
        title_text = self.fonts['large'].render("AWS Breakout", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.fonts['medium'].render("Break AWS Service Logos!", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions
        instructions = [
            "Press SPACE to start",
            "Use Arrow Keys or A/D to move paddle",
            "Collect AWS power-ups for special abilities!",
            "",
            f"High Score: {self.high_score}"
        ]
        
        y_offset = 280
        for instruction in instructions:
            if instruction:
                text = self.fonts['small'].render(instruction, True, (150, 150, 150))
                text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
                screen.blit(text, text_rect)
            y_offset += 30
    
    def _draw_game_ui(self, screen: pygame.Surface, level_info: Dict):
        """Draw the in-game UI"""
        # Score
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.fonts['medium'].render(f"Lives: {self.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (10, 45))
        
        # Level info
        if level_info:
            level_text = self.fonts['small'].render(
                f"Level {level_info.get('level_number', 1)}: {level_info.get('name', 'Unknown')}", 
                True, (200, 200, 200)
            )
            screen.blit(level_text, (10, 80))
        
        # Combo multiplier
        if self.combo_multiplier > 1.0:
            combo_text = self.fonts['small'].render(
                f"Combo x{self.combo_multiplier:.1f} ({self.combo_count})", 
                True, (255, 255, 0)
            )
            screen.blit(combo_text, (self.screen_width - 200, 10))
        
        # High score
        high_score_text = self.fonts['small'].render(f"High: {self.high_score}", True, (200, 200, 200))
        screen.blit(high_score_text, (self.screen_width - 150, 45))
    
    def _draw_pause_overlay(self, screen: pygame.Surface):
        """Draw pause overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.fonts['large'].render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(pause_text, pause_rect)
        
        # Instructions
        instruction_text = self.fonts['small'].render("Press P to resume", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        screen.blit(instruction_text, instruction_rect)
    
    def _draw_level_complete(self, screen: pygame.Surface, level_info: Dict):
        """Draw level complete screen"""
        # Background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 50, 0))
        screen.blit(overlay, (0, 0))
        
        # Level complete text
        complete_text = self.fonts['large'].render("LEVEL COMPLETE!", True, (0, 255, 0))
        complete_rect = complete_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(complete_text, complete_rect)
        
        # Level info
        if level_info:
            level_text = self.fonts['medium'].render(f"{level_info.get('name', 'Unknown')} Destroyed!", True, (255, 255, 255))
            level_rect = level_text.get_rect(center=(self.screen_width // 2, 250))
            screen.blit(level_text, level_rect)
        
        # Score info
        level_score_text = self.fonts['medium'].render(f"Level Score: {self.level_score}", True, (255, 255, 0))
        level_score_rect = level_score_text.get_rect(center=(self.screen_width // 2, 300))
        screen.blit(level_score_text, level_score_rect)
        
        total_score_text = self.fonts['medium'].render(f"Total Score: {self.score}", True, (255, 255, 255))
        total_score_rect = total_score_text.get_rect(center=(self.screen_width // 2, 330))
        screen.blit(total_score_text, total_score_rect)
        
        # Instructions
        instruction_text = self.fonts['small'].render("Press SPACE for next level", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, 400))
        screen.blit(instruction_text, instruction_rect)
    
    def _draw_game_over(self, screen: pygame.Surface):
        """Draw game over screen"""
        # Background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((50, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.fonts['large'].render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.fonts['medium'].render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 250))
        screen.blit(score_text, score_rect)
        
        # High score
        if self.score == self.high_score:
            high_score_text = self.fonts['medium'].render("NEW HIGH SCORE!", True, (255, 215, 0))
        else:
            high_score_text = self.fonts['medium'].render(f"High Score: {self.high_score}", True, (200, 200, 200))
        high_score_rect = high_score_text.get_rect(center=(self.screen_width // 2, 300))
        screen.blit(high_score_text, high_score_rect)
        
        # Statistics
        stats = [
            f"Levels Completed: {self.levels_completed}",
            f"Bricks Destroyed: {self.total_bricks_destroyed}",
            f"Power-ups Collected: {self.total_powerups_collected}"
        ]
        
        y_offset = 350
        for stat in stats:
            stat_text = self.fonts['small'].render(stat, True, (150, 150, 150))
            stat_rect = stat_text.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(stat_text, stat_rect)
            y_offset += 25
        
        # Instructions
        instruction_text = self.fonts['small'].render("Press R to restart", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, 450))
        screen.blit(instruction_text, instruction_rect)
    
    def _draw_game_won(self, screen: pygame.Surface):
        """Draw game won screen"""
        # Background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((50, 50, 0))
        screen.blit(overlay, (0, 0))
        
        # Victory text
        victory_text = self.fonts['large'].render("CONGRATULATIONS!", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(victory_text, victory_rect)
        
        # Subtitle
        subtitle_text = self.fonts['medium'].render("All AWS Services Conquered!", True, (255, 255, 255))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 250))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Final score
        score_text = self.fonts['medium'].render(f"Final Score: {self.score}", True, (255, 255, 0))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 300))
        screen.blit(score_text, score_rect)
        
        # Instructions
        instruction_text = self.fonts['small'].render("Press R to play again", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, 400))
        screen.blit(instruction_text, instruction_rect)
    
    def _draw_messages(self, screen: pygame.Surface):
        """Draw temporary messages"""
        for i, message in enumerate(self.messages):
            # Calculate alpha based on remaining duration
            alpha = min(255, int(255 * message['duration']))
            
            # Create text surface
            text_surface = self.fonts['small'].render(message['text'], True, message['color'])
            
            # Apply alpha
            if alpha < 255:
                text_surface.set_alpha(alpha)
            
            # Position message
            x = self.screen_width // 2 - text_surface.get_width() // 2
            y = 150 + i * 25
            
            screen.blit(text_surface, (x, y))
