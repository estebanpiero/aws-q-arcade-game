"""
Test script to verify all game components work correctly
"""

import pygame
import sys
import os

def test_imports():
    """Test that all game modules can be imported"""
    print("Testing imports...")
    
    try:
        from paddle import Paddle
        from ball import Ball, MultiBall
        from brick import Brick
        from level import Level, LevelManager
        from game_state import GameStateManager, GameState
        from powerup import PowerUpManager, PowerUpType
        from image_processor import ImageProcessor
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_pygame_init():
    """Test pygame initialization"""
    print("Testing pygame initialization...")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Test")
        print("✓ Pygame initialized successfully")
        pygame.quit()
        return True
    except Exception as e:
        print(f"✗ Pygame error: {e}")
        return False

def test_level_loading():
    """Test level loading"""
    print("Testing level loading...")
    
    try:
        from level import LevelManager
        manager = LevelManager()
        
        if len(manager.levels) > 0:
            print(f"✓ Loaded {len(manager.levels)} levels")
            
            # Test current level
            current = manager.get_current_level()
            if current:
                print(f"✓ Current level: {current.name} with {len(current.bricks)} bricks")
                return True
            else:
                print("✗ No current level set")
                return False
        else:
            print("✗ No levels loaded")
            return False
    except Exception as e:
        print(f"✗ Level loading error: {e}")
        return False

def test_game_components():
    """Test basic game component creation"""
    print("Testing game components...")
    
    try:
        from paddle import Paddle
        from ball import Ball
        from brick import Brick
        from powerup import PowerUpManager, PowerUpType
        
        # Test paddle
        paddle = Paddle(400, 550)
        print("✓ Paddle created")
        
        # Test ball
        ball = Ball(400, 300)
        print("✓ Ball created")
        
        # Test brick
        brick = Brick(100, 100, color='orange')
        print("✓ Brick created")
        
        # Test power-up manager
        powerup_manager = PowerUpManager()
        print("✓ PowerUp manager created")
        
        return True
    except Exception as e:
        print(f"✗ Component creation error: {e}")
        return False

def test_image_processor():
    """Test image processor (without actual images)"""
    print("Testing image processor...")
    
    try:
        from image_processor import ImageProcessor
        processor = ImageProcessor()
        print("✓ Image processor created")
        
        # Test color mapping
        color = processor._get_dominant_color.__func__(processor, [[255, 0, 0, 255]])
        print("✓ Color processing works")
        
        return True
    except Exception as e:
        print(f"✗ Image processor error: {e}")
        return False

def main():
    """Run all tests"""
    print("AWS Breakout Game - Component Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_pygame_init,
        test_level_loading,
        test_game_components,
        test_image_processor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The game should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
