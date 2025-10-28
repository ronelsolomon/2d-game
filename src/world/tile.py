from dataclasses import dataclass
from typing import Dict, Any
import random
from ..utils.constants import (
    TILE_EMPTY, TILE_GRASS, TILE_DIRT, TILE_STONE, TILE_WATER,
    TILE_SAND, TILE_LAVA, TILE_WOOD, TILE_LEAVES, TILE_FLOWER,
    TILE_MUSHROOM, TILE_CRYSTAL, TILE_TREASURE, TILE_DOOR,
    TILE_CHEST, TILE_SPAWN,
    BLACK, WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
    GRAY, DARK_GRAY, LIGHT_GRAY, BROWN, LIGHT_BLUE
)

@dataclass
class Tile:
    """Represents a single tile in the game world."""
    type: str = 'empty'
    variant: int = 0
    is_walkable: bool = True
    is_collectible: bool = False
    is_interactive: bool = False
    
    def __post_init__(self):
        """Initialize tile properties based on type."""
        if self.type not in TILE_PROPERTIES:
            self.type = 'empty'
        
        # Apply properties from the TILE_PROPERTIES dictionary
        self._color = None  # Initialize _color to store the color value
        props = TILE_PROPERTIES[self.type]
        for key, value in props.items():
            if key == 'color':
                self._color = value
            else:
                setattr(self, key, value)
        
        # Set random variant if there are multiple variants
        if 'variants' in props and props['variants'] > 1:
            self.variant = random.randint(0, props['variants'] - 1)
    
    @property
    def color(self) -> tuple:
        """Get the color of the tile."""
        if self._color is not None:
            return self._color
        return TILE_COLORS.get(self.type, (0, 0, 0))
    
    def is_walkable(self) -> bool:
        """Check if the tile can be walked on."""
        return self.is_walkable
    
    def is_collectible(self) -> bool:
        """Check if the tile can be collected."""
        return self.is_collectible
    
    def is_interactive(self) -> bool:
        """Check if the tile is interactive."""
        return self.is_interactive
    
    def get_item(self):
        """Get the item this tile drops when collected."""
        return TILE_ITEMS.get(self.type)
    
    def interact(self, player) -> str:
        """Handle interaction with the tile."""
        if self.type == 'chest':
            return "You found a treasure chest!"
        elif self.type == 'door':
            return "The door is locked."
        return ""

# Tile properties
TILE_PROPERTIES = {
    'empty': {
        'color': BLACK,
        'is_walkable': True,
        'is_collectible': False,
        'is_interactive': False
    },
    'grass': {
        'color': (34, 139, 34),  # Forest Green
        'is_walkable': True,
        'is_collectible': False,
        'is_interactive': False,
        'variants': 3
    },
    'dirt': {
        'color': (101, 67, 33),  # Brown
        'is_walkable': True,
        'is_collectible': False,
        'is_interactive': False
    },
    'stone': {
        'color': (169, 169, 169),  # Dark Gray
        'is_walkable': False,
        'is_collectible': True,
        'is_interactive': False
    },
    'water': {
        'color': (30, 144, 255),  # Dodger Blue
        'is_walkable': False,
        'is_collectible': False,
        'is_interactive': False
    },
    'tree': {
        'color': (0, 100, 0),  # Dark Green
        'is_walkable': False,
        'is_collectible': True,
        'is_interactive': False
    },
    'flower': {
        'color': (255, 0, 255),  # Magenta
        'is_walkable': True,
        'is_collectible': True,
        'is_interactive': False,
        'variants': 3
    },
    'chest': {
        'color': (160, 82, 45),  # Sienna
        'is_walkable': False,
        'is_collectible': False,
        'is_interactive': True
    },
    'door': {
        'color': (139, 69, 19),  # Saddle Brown
        'is_walkable': False,
        'is_collectible': False,
        'is_interactive': True
    }
}

# Map tile types to colors
TILE_COLORS = {
    'empty': (0, 0, 0, 0),  # Transparent
    'grass': (34, 139, 34),  # Forest Green
    'dirt': (101, 67, 33),  # Brown
    'stone': (169, 169, 169),  # Dark Gray
    'water': (30, 144, 255),  # Dodger Blue
    'tree': (0, 100, 0),  # Dark Green
    'flower': (255, 0, 255),  # Magenta
    'chest': (160, 82, 45),  # Sienna
    'door': (139, 69, 19)  # Saddle Brown
}

# Map tile types to items they drop when collected
TILE_ITEMS = {
    'grass': 'grass',
    'dirt': 'dirt',
    'stone': 'stone',
    'tree': 'wood',
    'flower': 'flower'
}

# Tile type constants for easier reference
TILE_TYPES = {
    'EMPTY': 'empty',
    'GRASS': 'grass',
    'DIRT': 'dirt',
    'STONE': 'stone',
    'WATER': 'water',
    'TREE': 'tree',
    'FLOWER': 'flower',
    'CHEST': 'chest',
    'DOOR': 'door'
}
