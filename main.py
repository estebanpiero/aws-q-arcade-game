"""
AWS Breakout Game - Main Game Loop
A Breakout-style game where bricks form AWS service logos
Built for the AWS Build Games Challenge using Amazon Q Developer CLI
"""

import pygame
import sys
import os
from typing import List, Optional

# Import game components
from paddle import Paddle
from ball import Ball, MultiBall
from level import LevelManager, create_sample_levels
from game_state import GameStateManager, GameState
from powerup import PowerUpManager, PowerUpType
from image_processor import ImageProcessor

class AWSBreakoutGame:
    """Main game class that manages the game loop and components"""
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the AWS Breakout game
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Screen setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AWS Breakout - Break the Cloud!")
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        # Game components
        self.paddle = Paddle(width // 2, height - 50, 100, 15)
        self.multi_ball = MultiBall()
        self.level_manager = LevelManager()
        self.game_state = GameStateManager(width, height)
        self.powerup_manager = PowerUpManager()
        
        # Initialize with main ball
        main_ball = Ball(width // 2, height - 100, 8)
        self.multi_ball.add_ball(main_ball)
        
        # Sound effects (placeholder - will work without actual sound files)
        self.sounds = self._load_sounds()
        
        # Game settings
        self.background_color = (20, 20, 40)  # Dark blue background
        
        # Initialize fonts for power-up manager
        try:
            font = pygame.font.Font(None, 24)
            self.powerup_manager.set_font(font)
        except:
            pass
        
        print("AWS Breakout Game initialized!")
        print(f"Loaded {len(self.level_manager.levels)} levels")
    
    def _load_sounds(self) -> dict:
        """Load sound effects (returns empty dict if files don't exist)"""
        sounds = {}
        sound_files = {
            'paddle_hit': 'assets/sounds/paddle_hit.wav',
            'brick_break': 'assets/sounds/brick_break.wav',
            'powerup_collect': 'assets/sounds/powerup_collect.wav',
            'level_complete': 'assets/sounds/level_complete.wav'
        }
        
        for sound_name, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    sounds[sound_name] = pygame.mixer.Sound(file_path)
                else:
                    sounds[sound_name] = None
            except:
                sounds[sound_name] = None
        
        return sounds
    
    def _play_sound(self, sound_name: str):
        """Play a sound effect if it exists"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
    
    def _handle_keydown(self, key):
        """Handle keyboard input"""
        if self.game_state.current_state == GameState.MENU:
            if key == pygame.K_SPACE:
                self.game_state.change_state(GameState.PLAYING)
                self._start_level()
        
        elif self.game_state.current_state == GameState.PLAYING:
            if key == pygame.K_SPACE:
                # Launch ball if not launched
                for ball in self.multi_ball.get_active_balls():
                    if not ball.launched:
                        ball.launch()
                        break
            elif key == pygame.K_p:
                self.game_state.change_state(GameState.PAUSED)
            elif key == pygame.K_r and self.powerup_manager.can_redirect_ball():
                # Route 53 power-up: redirect ball towards mouse
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for ball in self.multi_ball.get_active_balls():
                    ball.redirect(mouse_x, mouse_y)
        
        elif self.game_state.current_state == GameState.PAUSED:
            if key == pygame.K_p:
                self.game_state.change_state(GameState.PLAYING)
        
        elif self.game_state.current_state == GameState.LEVEL_COMPLETE:
            if key == pygame.K_SPACE:
                self._next_level()
        
        elif self.game_state.current_state == GameState.GAME_OVER:
            if key == pygame.K_r:
                self._restart_game()
        
        elif self.game_state.current_state == GameState.GAME_WON:
            if key == pygame.K_r:
                self._restart_game()
    
    def _start_level(self):
        """Start the current level"""
        # Reset ball position
        for ball in self.multi_ball.get_active_balls():
            ball.reset(self.width // 2, self.height - 100)
        
        # Reset paddle position
        self.paddle.reset(self.width // 2, self.height - 50)
        
        # Clear power-ups
        self.powerup_manager.clear_all_effects()
        self.powerup_manager.clear_all_powerups()
    
    def _next_level(self):
        """Advance to the next level"""
        if self.level_manager.next_level():
            self.game_state.change_state(GameState.PLAYING)
            self._start_level()
        else:
            # All levels completed
            self.game_state.change_state(GameState.GAME_WON)
    
    def _restart_game(self):
        """Restart the entire game"""
        self.level_manager.restart_game()
        self.game_state.change_state(GameState.PLAYING)
        self._start_level()
    
    def update(self, dt: float):
        """Update all game components"""
        if self.game_state.current_state != GameState.PLAYING:
            return
        
        # Get power-up effects
        time_multiplier = self.powerup_manager.get_time_multiplier()
        speed_multiplier = self.powerup_manager.get_ball_speed_multiplier()
        paddle_size_multiplier = self.powerup_manager.get_paddle_size_multiplier()
        
        # Update paddle
        keys = pygame.key.get_pressed()
        self.paddle.handle_input(keys, dt)
        self.paddle.update(dt, self.width, paddle_size_multiplier)
        
        # Update balls
        self.multi_ball.update_all(dt, self.width, self.height, time_multiplier, speed_multiplier)
        
        # Handle ball freezing (ElastiCache power-up)
        if self.powerup_manager.should_freeze_ball():
            for ball in self.multi_ball.get_active_balls():
                if not ball.frozen:
                    ball.freeze(3.0)
        
        # Check ball-paddle collisions
        for ball in self.multi_ball.get_active_balls():
            if ball.launched and self.paddle.check_ball_collision(ball.x, ball.y, ball.radius):
                ball.bounce_off_paddle(
                    self.paddle.get_center_x(),
                    self.paddle.get_top_y(),
                    self.paddle.get_width()
                )
                self._play_sound('paddle_hit')
                self.paddle.activate_glow(0.5)
        
        # Check ball-brick collisions
        current_level = self.level_manager.get_current_level()
        if current_level:
            for ball in self.multi_ball.get_active_balls():
                for brick in current_level.get_active_bricks():
                    if ball.rect.colliderect(brick.rect):
                        # Handle collision
                        ball.bounce_off_brick(brick.rect)
                        
                        # Damage brick
                        if brick.hit():
                            # Brick destroyed
                            self.game_state.brick_destroyed(brick.color_name, brick.get_score_value())
                            self._play_sound('brick_break')
                            
                            # Maybe spawn power-up
                            if self.powerup_manager.maybe_spawn_powerup(
                                brick.x + brick.width // 2,
                                brick.y + brick.height // 2
                            ):
                                pass  # Power-up spawned
                        
                        break  # Only hit one brick per ball per frame
        
        # Check power-up collisions
        collected_powerup = self.powerup_manager.check_paddle_collision(self.paddle.rect)
        if collected_powerup:
            self._handle_powerup_collection(collected_powerup)
        
        # Update power-ups
        self.powerup_manager.update(dt)
        
        # Update level
        if current_level:
            current_level.update(dt)
            
            # Check level completion
            if current_level.completed:
                self.game_state.change_state(GameState.LEVEL_COMPLETE)
                self._play_sound('level_complete')
        
        # Check if all balls are lost
        if not self.multi_ball.has_active_balls():
            if self.powerup_manager.has_shield():
                # IAM shield protects from losing life once
                self.powerup_manager.active_effects = [
                    e for e in self.powerup_manager.active_effects 
                    if e.type != PowerUpType.IAM_SHIELD
                ]
                self.game_state.add_message("IAM Shield Protected You!", 2.0, (0, 255, 255))
                
                # Respawn ball
                new_ball = Ball(self.width // 2, self.height - 100, 8)
                self.multi_ball.add_ball(new_ball)
            else:
                # Lose a life
                if self.game_state.lose_life():
                    # Game over
                    pass
                else:
                    # Respawn ball
                    new_ball = Ball(self.width // 2, self.height - 100, 8)
                    self.multi_ball.add_ball(new_ball)
        
        # Update game state
        self.game_state.update(dt)
    
    def _handle_powerup_collection(self, powerup_type: PowerUpType):
        """Handle power-up collection"""
        self.game_state.collect_powerup(powerup_type.value)
        self._play_sound('powerup_collect')
        
        # Activate power-up effect
        self.powerup_manager.activate_powerup(powerup_type)
        
        # Handle special power-ups
        if powerup_type == PowerUpType.LAMBDA_MULTI:
            # Create additional balls
            active_balls = self.multi_ball.get_active_balls()
            if active_balls:
                main_ball = active_balls[0]
                self.multi_ball.create_additional_balls(main_ball, 2)
        
        elif powerup_type == PowerUpType.CLOUDFORMATION_REBUILD:
            # Rebuild some bricks
            current_level = self.level_manager.get_current_level()
            if current_level:
                current_level.rebuild_random_bricks(0.2)  # Rebuild 20% of destroyed bricks
    
    def draw(self):
        """Draw all game components"""
        # Clear screen
        self.screen.fill(self.background_color)
        
        # Draw game components based on state
        if self.game_state.current_state in [GameState.PLAYING, GameState.PAUSED, GameState.LEVEL_COMPLETE]:
            # Draw level
            current_level = self.level_manager.get_current_level()
            if current_level:
                current_level.draw(self.screen)
            
            # Draw paddle
            self.paddle.draw(self.screen)
            
            # Draw balls
            self.multi_ball.draw_all(self.screen)
            
            # Draw power-ups
            self.powerup_manager.draw(self.screen)
            
            # Draw power-up effect indicators
            try:
                font = pygame.font.Font(None, 20)
                self.powerup_manager.draw_effect_indicators(self.screen, font)
            except:
                pass
        
        # Draw UI
        level_info = self.level_manager.get_level_info()
        self.game_state.draw_ui(self.screen, level_info)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Starting AWS Breakout Game!")
        print("Controls:")
        print("  Arrow Keys or A/D: Move paddle")
        print("  Space: Launch ball / Continue")
        print("  P: Pause/Resume")
        print("  R: Restart (when game over)")
        print("\nPower-ups:")
        print("  ⏰ CloudWatch: Slows down time")
        print("  🛡️ IAM: Protective shield")
        print("  λ Lambda: Multiple balls")
        print("  📦 S3: Expand paddle")
        print("  ⚡ EC2: Speed boost")
        print("  🔄 Route 53: Ball direction control")
        print("  ❄️ ElastiCache: Freeze ball")
        print("  🔧 CloudFormation: Rebuild bricks")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.fps) / 1000.0  # Convert to seconds
            
            # Handle events
            self.handle_events()
            
            # Update game
            self.update(dt)
            
            # Draw everything
            self.draw()
        
        # Cleanup
        pygame.quit()
        print("Thanks for playing AWS Breakout!")

def main():
    """Main entry point"""
    print("AWS Breakout Game")
    print("================")
    print("Built with Amazon Q Developer CLI for the AWS Build Games Challenge")
    print()
    
    # Create sample levels if they don't exist
    if not os.path.exists("assets/levels") or len(os.listdir("assets/levels")) == 0:
        print("Creating sample levels...")
        create_sample_levels()
    
    # Check if images directory exists for processing
    if os.path.exists("images") and len(os.listdir("images")) > 0:
        print("Found images directory. You can run image_processor.py to convert AWS logos to levels.")
    
    # Create and run the game
    try:
        game = AWSBreakoutGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
