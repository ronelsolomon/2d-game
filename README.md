# 2D Infinite Exploration Game

A 2D sandbox exploration game built with Python and Pygame. Explore procedurally generated worlds, gather resources, craft items, and interact with NPCs in this open-ended adventure.

![Game Screenshot](assets/screenshots/gameplay.png)

## Features

- **Procedural World Generation**: Explore infinite, procedurally generated worlds with different biomes
- **Resource Gathering**: Mine resources like wood, stone, and various ores including iron, gold, and diamonds
- **Crafting System**: Craft tools, weapons, and items from gathered resources
- **NPC Interactions**: Meet and interact with various NPCs throughout the world
- **Inventory System**: Manage your collected items with a grid-based inventory and hotbar
- **Multiple Biomes**: Discover different environments including:
  - **Plains**: Lush green landscapes with trees and grass
  - **Desert**: Sandy terrain with cacti and unique resources
  - **Snow**: Icy tundras with special winter-themed items
  - **Forest**: Dense woodlands with abundant resources
  - **Mountains**: Challenging terrain with valuable ores
- **Day/Night Cycle**: Experience dynamic lighting and time-based events
- **NPC System**: Interact with various NPCs including:
  - **Merchant**: Buy and sell items
  - **Farmer**: Trade for food and farming supplies
  - **Wizard**: Unlock magical abilities and items
  - **Blacksmith**: Upgrade your tools and weapons
  - **Adventurer**: Get quests and valuable information

## Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - pip (Python package installer)

2. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/2d-game.git
   cd 2d-game
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. **Running the game**:
   ```bash
   python app.py
   ```
   Or use the modular version:
   ```bash
   python -m src.main
   ```

2. **Controls**:
   - **WASD or Arrow Keys**: Move character
   - **E**: Interact with objects/NPCs
   - **Space**: Jump
   - **Left Click**: Use equipped item/attack
   - **Right Click**: Place block (if applicable)
   - **1-8**: Select hotbar slot
   - **I**: Toggle inventory
   - **M**: Toggle map
   - **ESC**: Pause game/Close menus
   - **F**: Toggle fullscreen
   - **R**: Reload resources (debug)

3. **Gameplay Tips**:
   - Collect resources during the day when it's safer
   - Different tools are more effective on different materials
   - Talk to NPCs for quests and trading opportunities
   - Keep an eye on your health and energy levels
   - Some resources only appear in specific biomes

## Project Structure

```
2d-game/
├── assets/                 # Game assets
│   ├── sprites/            # Character and tile sprites
│   │   ├── characters/     # Player and NPC sprites
│   │   └── tiles/          # Tile and environment sprites
│   └── sounds/             # Sound effects and music
├── src/                    # Source code
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Main game loop
│   ├── npc_types.py        # NPC type definitions
│   ├── world/              # World generation
│   └── entities/           # Game entities
├── app.py                  # Monolithic game implementation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Dependencies

- **Python 3.8+**: Core programming language
- **Pygame 2.0+**: Game development and rendering
- **NumPy**: Efficient numerical operations
- **Pillow**: Advanced image processing
- **PyYAML**: Configuration management

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Game assets from various open-source sprite packs
- Inspired by classic 2D exploration and sandbox games
- Built with the amazing Pygame library

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/2d-game/issues).
