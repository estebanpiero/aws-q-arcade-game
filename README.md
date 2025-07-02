# AWS Breakout Arcade Game

A Breakout-style arcade game where bricks are arranged to form AWS service logos! Built for the AWS Build Games Challenge using **Amazon Q Developer CLI**.

## 🎮 Game Concept

Instead of generic brick layouts, each level features bricks arranged to visually represent different AWS service logos (EC2, S3, Lambda, etc.). As you break the bricks, you're literally "breaking apart" the AWS service logos! Collect AWS-themed power-ups that provide special abilities inspired by actual AWS services.

## ✨ Features

- **Classic Breakout gameplay** with paddle and ball physics
- **AWS service logo brick patterns** - each level represents a different AWS service
- **AWS-themed power-ups** with abilities inspired by real AWS services:
  - ⏰ **CloudWatch**: Slows down time for better reaction
  - 🛡️ **IAM**: Protective shield that saves you from losing a life
  - λ **Lambda**: Creates multiple balls (serverless scaling!)
  - 📦 **S3**: Expands paddle size (more storage space!)
  - ⚡ **EC2**: Speed boost for the ball (more compute power!)
  - 🔄 **Route 53**: Control ball direction (traffic routing!)
  - ❄️ **ElastiCache**: Temporarily freezes the ball
  - 🔧 **CloudFormation**: Rebuilds some destroyed bricks
- **Multiple levels** with different AWS services
- **Scoring system** with combo multipliers
- **Sound effects** and visual particle effects
- **High score tracking**
- **Image-to-grid conversion** using PIL to create levels from actual AWS logos

## 🏗️ File Structure

```
aws-q-arcade-game/
├── main.py                  # Main game loop and initialization
├── paddle.py                # Paddle class and movement logic
├── ball.py                  # Ball physics and collision detection
├── brick.py                 # Brick class with color and durability
├── level.py                 # Level management and brick layout loading
├── game_state.py            # Game state management and scoring
├── powerup.py               # AWS-themed power-up system
├── image_processor.py       # Convert AWS logo images to brick grids
├── requirements.txt         # Python dependencies
├── images/                  # Place AWS service logo images here
├── assets/
│   ├── levels/
│   │   ├── ec2_logo.json    # EC2 logo brick layout
│   │   ├── s3_logo.json     # S3 logo brick layout
│   │   └── lambda_logo.json # Lambda logo brick layout
│   └── sounds/              # Sound effects (optional)
└── README.md                # This file
```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pygame Pillow numpy
```

### 2. Run the Game

```bash
python main.py
```

### 3. (Optional) Convert AWS Logo Images to Levels

1. Place AWS service logo images (PNG, JPG, etc.) in the `images/` directory
2. Run the image processor:
   ```bash
   python image_processor.py
   ```
3. This will generate new level files in `assets/levels/` based on your images

## 🎯 Controls

- **Left Arrow** or **A**: Move paddle left
- **Right Arrow** or **D**: Move paddle right
- **Space**: Launch ball / Continue to next level
- **P**: Pause/Resume game
- **R**: Restart game (when game over)
- **Mouse + R**: Redirect ball (when Route 53 power-up is active)

## 🏆 Scoring System

- **Base points**: 10 points per brick
- **Color multipliers**: Red/Orange/Purple bricks worth more points
- **Durability multipliers**: Multi-hit bricks worth more points
- **Combo system**: Consecutive hits increase score multiplier
- **Power-up bonus**: 50 points for collecting power-ups

## 🔧 Level Design

Each AWS service logo is represented as a JSON file in the `assets/levels/` directory. The JSON format defines:

- Grid dimensions (20x15 by default)
- Brick positions and colors
- Service name and description

Example level structure:
```json
{
  "name": "EC2",
  "description": "Elastic Compute Cloud",
  "grid_width": 20,
  "grid_height": 15,
  "bricks": [
    {"x": 5, "y": 3, "color": "orange", "durability": 1},
    {"x": 6, "y": 3, "color": "orange", "durability": 1}
  ]
}
```

## 🖼️ Image Processing

The game includes an advanced image processor that can convert actual AWS service logo images into playable brick layouts:

1. **Automatic color detection**: Analyzes image colors and maps them to appropriate brick colors
2. **Smart brick placement**: Uses alpha channel and pixel density to determine brick positions
3. **Aspect ratio preservation**: Maintains logo proportions within the game grid
4. **Batch processing**: Convert multiple logo images at once

## 🎵 Sound Effects (Optional)

Place sound files in `assets/sounds/`:
- `paddle_hit.wav` - Ball hits paddle
- `brick_break.wav` - Brick is destroyed
- `powerup_collect.wav` - Power-up collected
- `level_complete.wav` - Level completed

The game will work without sound files.

## 🏅 AWS Services Featured

- **EC2 (Elastic Compute Cloud)**: Orange bricks in server-like patterns
- **S3 (Simple Storage Service)**: Green bricks forming bucket shapes
- **Lambda**: Purple bricks in lambda (λ) symbol patterns
- **CloudWatch**: Monitoring-themed power-up (time control)
- **IAM**: Security-themed power-up (protective shield)
- **Route 53**: DNS-themed power-up (traffic routing)
- **ElastiCache**: Caching-themed power-up (freeze effect)
- **CloudFormation**: Infrastructure-themed power-up (rebuild bricks)

## 🤖 Built with Amazon Q Developer CLI

This entire game was created using **Amazon Q Developer CLI**, AWS's AI-powered coding assistant. The development process showcased how AI can accelerate game development while maintaining code quality and best practices:

### What Amazon Q Developer CLI Generated:
- **Complete game architecture** with modular, object-oriented design
- **Physics calculations** for ball movement and collision detection
- **Advanced power-up system** with AWS service-themed abilities
- **Image processing pipeline** using PIL for logo-to-grid conversion
- **Comprehensive game state management** with scoring and UI
- **Sound integration** and particle effects
- **Level management system** with JSON-based level definitions
- **Detailed documentation** and setup instructions

### Development Highlights:
- **Conversational development**: Entire codebase generated through natural language prompts
- **Best practices**: Clean code structure, proper error handling, and comprehensive comments
- **Feature completeness**: Fully functional game with no placeholders or TODO items
- **Educational value**: Well-commented code suitable for learning and documentation

## 🎮 Gameplay Tips

1. **Aim for the edges** of the paddle to control ball angle
2. **Collect power-ups strategically** - some are more useful in certain situations
3. **Use Route 53 power-up** to redirect balls toward remaining bricks
4. **IAM shield** is great insurance when you have few lives left
5. **Lambda multi-ball** can quickly clear levels but is harder to control
6. **CloudWatch slow-time** is perfect for precise paddle positioning

## 🔮 Future Enhancements

- Additional AWS service logos (RDS, DynamoDB, CloudFormation visual patterns)
- Multiplayer support with AWS GameLift integration
- Leaderboards using DynamoDB
- More complex power-up combinations
- Animated logo reveals when levels start
- Boss levels with moving AWS architecture diagrams

## 🤝 Contributing

Feel free to add new AWS service logo patterns by:
1. Adding images to the `images/` directory
2. Running `python image_processor.py` to generate levels
3. Or manually creating JSON files in `assets/levels/`

## 📄 License

This project is created for the AWS Build Games Challenge and demonstrates the capabilities of Amazon Q Developer CLI in game development.

---

**Built with ❤️ using Amazon Q Developer CLI for the AWS Build Games Challenge**

*Experience the power of AI-assisted development - this entire game, from concept to completion, was generated through conversational prompting with Amazon Q Developer CLI!*
