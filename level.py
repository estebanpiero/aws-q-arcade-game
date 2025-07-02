"""
Level management for AWS Breakout Game
Handles loading AWS service logo layouts and managing game levels
"""

import json
import os
import random
from typing import List, Dict, Optional, Tuple
from brick import Brick

class Level:
    """Represents a single game level with AWS service logo layout"""
    
    def __init__(self, level_data: Dict):
        """
        Initialize a level from level data
        
        Args:
            level_data: Dictionary containing level information
        """
        self.name = level_data.get('name', 'Unknown')
        self.description = level_data.get('description', '')
        self.grid_width = level_data.get('grid_width', 20)
        self.grid_height = level_data.get('grid_height', 15)
        self.source_image = level_data.get('source_image', '')
        
        # Game area dimensions
        self.game_area_width = 800
        self.game_area_height = 600
        self.brick_area_height = 400  # Top portion for bricks
        
        # Calculate brick dimensions
        self.brick_width = self.game_area_width // self.grid_width
        self.brick_height = self.brick_area_height // self.grid_height
        
        # Create bricks from level data
        self.bricks: List[Brick] = []
        self.original_brick_count = 0
        self._create_bricks_from_data(level_data.get('bricks', []))
        
        # Level state
        self.completed = False
        self.bricks_destroyed = 0
    
    def _create_bricks_from_data(self, brick_data: List[Dict]):
        """
        Create brick objects from level data
        
        Args:
            brick_data: List of brick dictionaries
        """
        self.bricks.clear()
        
        for brick_info in brick_data:
            grid_x = brick_info.get('x', 0)
            grid_y = brick_info.get('y', 0)
            color = brick_info.get('color', 'blue')
            durability = brick_info.get('durability', 1)
            
            # Convert grid coordinates to pixel coordinates
            pixel_x = grid_x * self.brick_width
            pixel_y = grid_y * self.brick_height + 50  # Offset from top
            
            # Create brick
            brick = Brick(
                x=pixel_x,
                y=pixel_y,
                width=self.brick_width - 2,  # Small gap between bricks
                height=self.brick_height - 2,
                color=color,
                durability=durability
            )
            
            self.bricks.append(brick)
        
        self.original_brick_count = len(self.bricks)
    
    def update(self, dt: float):
        """
        Update all bricks in the level
        
        Args:
            dt: Delta time in seconds
        """
        for brick in self.bricks:
            brick.update(dt)
        
        # Remove completely destroyed bricks
        destroyed_bricks = [brick for brick in self.bricks if brick.is_destroyed()]
        for brick in destroyed_bricks:
            self.bricks.remove(brick)
            self.bricks_destroyed += 1
        
        # Check if level is completed
        active_bricks = [brick for brick in self.bricks if brick.active]
        self.completed = len(active_bricks) == 0
    
    def draw(self, screen):
        """Draw all bricks in the level"""
        for brick in self.bricks:
            brick.draw(screen)
    
    def get_active_bricks(self) -> List[Brick]:
        """Get list of active (not destroyed) bricks"""
        return [brick for brick in self.bricks if brick.active]
    
    def get_completion_percentage(self) -> float:
        """Get level completion percentage (0.0 to 1.0)"""
        if self.original_brick_count == 0:
            return 1.0
        return self.bricks_destroyed / self.original_brick_count
    
    def rebuild_random_bricks(self, percentage: float = 0.3):
        """
        Rebuild a percentage of destroyed bricks (CloudFormation power-up)
        
        Args:
            percentage: Percentage of destroyed bricks to rebuild (0.0 to 1.0)
        """
        destroyed_count = self.bricks_destroyed
        rebuild_count = int(destroyed_count * percentage)
        
        if rebuild_count == 0:
            return
        
        # This is a simplified implementation
        # In a full implementation, you'd store destroyed brick data and restore it
        print(f"CloudFormation: Rebuilding {rebuild_count} bricks!")

class LevelManager:
    """Manages multiple levels and level progression"""
    
    def __init__(self, levels_directory: str = "assets/levels"):
        """
        Initialize the level manager
        
        Args:
            levels_directory: Directory containing level JSON files
        """
        self.levels_directory = levels_directory
        self.level_files: List[str] = []
        self.levels: List[Level] = []
        self.current_level_index = 0
        self.current_level: Optional[Level] = None
        
        # Load available levels
        self._discover_level_files()
        self._load_all_levels()
        
        # Set first level as current
        if self.levels:
            self.current_level = self.levels[0]
    
    def _discover_level_files(self):
        """Discover all level JSON files in the levels directory"""
        self.level_files.clear()
        
        if not os.path.exists(self.levels_directory):
            print(f"Levels directory '{self.levels_directory}' not found!")
            return
        
        for filename in os.listdir(self.levels_directory):
            if filename.endswith('.json'):
                file_path = os.path.join(self.levels_directory, filename)
                self.level_files.append(file_path)
        
        # Sort level files for consistent ordering
        self.level_files.sort()
        print(f"Found {len(self.level_files)} level files")
    
    def _load_all_levels(self):
        """Load all level data from JSON files"""
        self.levels.clear()
        
        for level_file in self.level_files:
            try:
                with open(level_file, 'r') as f:
                    level_data = json.load(f)
                
                level = Level(level_data)
                self.levels.append(level)
                print(f"Loaded level: {level.name} ({len(level.bricks)} bricks)")
                
            except Exception as e:
                print(f"Error loading level file {level_file}: {e}")
        
        if not self.levels:
            # Create a default level if no levels were loaded
            self._create_default_level()
    
    def _create_default_level(self):
        """Create a default level if no level files are found"""
        print("Creating default EC2 level...")
        
        # Create a simple EC2-inspired brick pattern
        default_bricks = []
        
        # Create a server rack pattern for EC2
        for row in range(3, 8):  # 5 rows
            for col in range(6, 14):  # 8 columns
                # Create server-like pattern
                if (row % 2 == 0 and col % 2 == 0) or (row % 2 == 1 and col % 2 == 1):
                    default_bricks.append({
                        "x": col,
                        "y": row,
                        "color": "orange",
                        "durability": 1
                    })
        
        default_level_data = {
            "name": "EC2",
            "description": "Default EC2 Server Pattern",
            "grid_width": 20,
            "grid_height": 15,
            "bricks": default_bricks
        }
        
        level = Level(default_level_data)
        self.levels.append(level)
        print(f"Created default level with {len(level.bricks)} bricks")
    
    def get_current_level(self) -> Optional[Level]:
        """Get the current active level"""
        return self.current_level
    
    def next_level(self) -> bool:
        """
        Advance to the next level
        
        Returns:
            True if there is a next level, False if all levels completed
        """
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            self.current_level = self.levels[self.current_level_index]
            return True
        return False
    
    def restart_current_level(self):
        """Restart the current level"""
        if self.current_level:
            # Reload the level data to reset all bricks
            level_file = self.level_files[self.current_level_index]
            try:
                with open(level_file, 'r') as f:
                    level_data = json.load(f)
                
                self.current_level = Level(level_data)
                self.levels[self.current_level_index] = self.current_level
                
            except Exception as e:
                print(f"Error restarting level: {e}")
    
    def restart_game(self):
        """Restart the entire game from the first level"""
        self.current_level_index = 0
        if self.levels:
            self.current_level = self.levels[0]
            self.restart_current_level()
    
    def get_level_info(self) -> Dict:
        """
        Get information about the current level
        
        Returns:
            Dictionary with level information
        """
        if not self.current_level:
            return {}
        
        return {
            'name': self.current_level.name,
            'description': self.current_level.description,
            'level_number': self.current_level_index + 1,
            'total_levels': len(self.levels),
            'completion_percentage': self.current_level.get_completion_percentage(),
            'bricks_remaining': len(self.current_level.get_active_bricks()),
            'total_bricks': self.current_level.original_brick_count
        }
    
    def is_game_completed(self) -> bool:
        """Check if all levels have been completed"""
        return (self.current_level_index >= len(self.levels) - 1 and 
                self.current_level and self.current_level.completed)
    
    def get_random_level(self) -> Optional[Level]:
        """Get a random level (for variety)"""
        if not self.levels:
            return None
        return random.choice(self.levels)

def create_sample_levels():
    """Create sample level files for testing"""
    levels_dir = "assets/levels"
    os.makedirs(levels_dir, exist_ok=True)
    
    # EC2 Level - Server rack pattern
    ec2_bricks = []
    for row in range(2, 10):
        for col in range(4, 16):
            if (row - 2) % 3 == 0 or col in [4, 15]:  # Horizontal lines and vertical edges
                ec2_bricks.append({
                    "x": col,
                    "y": row,
                    "color": "orange",
                    "durability": 1
                })
    
    ec2_level = {
        "name": "EC2",
        "description": "Elastic Compute Cloud - Server Infrastructure",
        "grid_width": 20,
        "grid_height": 15,
        "bricks": ec2_bricks
    }
    
    # S3 Level - Bucket pattern
    s3_bricks = []
    # Create bucket shape
    for row in range(3, 12):
        for col in range(6, 14):
            if (row == 3 or row == 11 or  # Top and bottom
                col == 6 or col == 13 or  # Sides
                (row >= 7 and row <= 9 and col >= 8 and col <= 11)):  # Handle
                s3_bricks.append({
                    "x": col,
                    "y": row,
                    "color": "green",
                    "durability": 1
                })
    
    s3_level = {
        "name": "S3",
        "description": "Simple Storage Service - Scalable Storage",
        "grid_width": 20,
        "grid_height": 15,
        "bricks": s3_bricks
    }
    
    # Lambda Level - Lambda symbol
    lambda_bricks = []
    # Create lambda (λ) shape
    for row in range(2, 13):
        for col in range(7, 13):
            if ((col == 7 and row >= 2) or  # Left vertical line
                (col == 8 and row == 7) or  # Middle diagonal
                (col == 9 and row == 8) or
                (col == 10 and row == 9) or
                (col == 11 and row == 10) or
                (col == 12 and row >= 11)):  # Right diagonal
                lambda_bricks.append({
                    "x": col,
                    "y": row,
                    "color": "purple",
                    "durability": 1
                })
    
    lambda_level = {
        "name": "Lambda",
        "description": "AWS Lambda - Serverless Computing",
        "grid_width": 20,
        "grid_height": 15,
        "bricks": lambda_bricks
    }
    
    # Save level files
    levels = [
        ("ec2_logo.json", ec2_level),
        ("s3_logo.json", s3_level),
        ("lambda_logo.json", lambda_level)
    ]
    
    for filename, level_data in levels:
        file_path = os.path.join(levels_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(level_data, f, indent=2)
        print(f"Created sample level: {file_path}")

if __name__ == "__main__":
    # Create sample levels for testing
    create_sample_levels()
    
    # Test level manager
    manager = LevelManager()
    print(f"Loaded {len(manager.levels)} levels")
    
    if manager.current_level:
        print(f"Current level: {manager.current_level.name}")
        print(f"Bricks: {len(manager.current_level.bricks)}")
