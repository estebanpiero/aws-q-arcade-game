# AWS Breakout Game - Usage Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install pygame Pillow numpy
   ```

2. **Run the game:**
   ```bash
   python3 main.py
   ```

3. **Play the game:**
   - Use arrow keys or A/D to move the paddle
   - Press Space to launch the ball
   - Break all the bricks to complete each level!

## Game Features

### AWS Service Levels
The game includes three pre-built levels representing AWS services:
- **EC2**: Orange bricks in a server rack pattern
- **S3**: Green bricks forming a storage bucket shape  
- **Lambda**: Purple bricks in a lambda (λ) symbol

### Power-ups
Collect AWS-themed power-ups that fall from destroyed bricks:

| Power-up | Effect | Description |
|----------|--------|-------------|
| ⏰ CloudWatch | Slow Time | Slows down game time for better control |
| 🛡️ IAM | Shield | Protects you from losing a life once |
| λ Lambda | Multi-Ball | Creates additional balls |
| 📦 S3 | Expand Paddle | Makes your paddle larger |
| ⚡ EC2 | Speed Boost | Increases ball speed |
| 🔄 Route 53 | Ball Control | Press R + mouse to redirect ball |
| ❄️ ElastiCache | Freeze Ball | Temporarily stops the ball |
| 🔧 CloudFormation | Rebuild | Restores some destroyed bricks |

### Scoring System
- **Base points**: 10 per brick
- **Color bonuses**: Red/Orange/Purple bricks worth more
- **Combo multiplier**: Consecutive hits increase your score
- **Power-up bonus**: 50 points for each power-up collected

## Controls

| Key | Action |
|-----|--------|
| ← → or A/D | Move paddle left/right |
| Space | Launch ball / Continue to next level |
| P | Pause/Resume game |
| R | Restart game (when game over) |
| R + Mouse | Redirect ball (with Route 53 power-up) |

## Adding Custom Levels

### Method 1: Using Images (Recommended)
1. Place AWS service logo images (PNG, JPG, etc.) in the `images/` folder
2. Run the image processor:
   ```bash
   python3 image_processor.py
   ```
3. New level files will be created in `assets/levels/`

### Method 2: Manual JSON Creation
Create a JSON file in `assets/levels/` with this structure:

```json
{
  "name": "ServiceName",
  "description": "Service Description",
  "grid_width": 20,
  "grid_height": 15,
  "bricks": [
    {
      "x": 5,
      "y": 3,
      "color": "orange",
      "durability": 1
    }
  ]
}
```

**Available colors**: orange, green, blue, purple, red, yellow, light_blue, dark_blue

## Troubleshooting

### Game won't start
- Make sure you have Python 3.6+ installed
- Install required dependencies: `pip install pygame Pillow numpy`
- Try running: `python3 main.py` instead of `python main.py`

### No sound
- Sound files are optional - the game works without them
- To add sounds, place WAV files in `assets/sounds/`:
  - `paddle_hit.wav`
  - `brick_break.wav` 
  - `powerup_collect.wav`
  - `level_complete.wav`

### Performance issues
- The game is designed to run at 60 FPS
- If experiencing lag, try closing other applications
- The game should run smoothly on most modern computers

## Development Notes

This game was created entirely using **Amazon Q Developer CLI**, demonstrating:
- Complete game architecture with modular design
- Physics-based collision detection
- Advanced power-up system with AWS service themes
- Image processing for converting logos to playable levels
- Comprehensive game state management
- Sound integration and visual effects

The entire codebase, from concept to completion, was generated through conversational prompting with Amazon Q Developer CLI, showcasing the power of AI-assisted development.

## Tips for Best Experience

1. **Strategic power-up use**: Save IAM shields for when you have few lives left
2. **Combo building**: Try to hit bricks consecutively to build up your score multiplier
3. **Ball control**: Hit the ball with different parts of the paddle to control its angle
4. **Route 53 power-up**: Use mouse positioning to guide the ball toward remaining bricks
5. **Lambda multi-ball**: Great for clearing levels quickly, but harder to control

Enjoy breaking the cloud! 🎮☁️
