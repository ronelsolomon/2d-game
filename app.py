import os
import pygame
import random
import math
import sys
from enum import Enum, auto, IntEnum
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

# Initialize Pygame first
pygame.init()

# Game constants
TILE_SIZE = 64  # Size of each tile in pixels
VIEWPORT_WIDTH = 16
VIEWPORT_HEIGHT = 12
SCREEN_WIDTH = VIEWPORT_WIDTH * TILE_SIZE
SCREEN_HEIGHT = VIEWPORT_HEIGHT * TILE_SIZE + 150  # Extra for HUD

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Infinite Exploration Game")
pygame.display.flip()

# Initialize fonts
font = pygame.font.SysFont('Arial', 20)
small_font = pygame.font.SysFont('Arial', 16)
pixel_font = pygame.font.Font(None, 16)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Tile Types
class Tile(Enum):
    GRASS = auto()
    DIRT = auto()
    STONE = auto()
    WATER = auto()
    TREE = auto()
    FLOWER = auto()
    TREASURE = auto()
    KEY_ITEM = 11
    BRICK = 12
    QUESTION_BLOCK = 13
    ICE = 14
    SNOW = 15
    SAND = 16
    CACTUS = 17
    LAVA = 18
    OBSIDIAN = 19
    PORTAL = 20
    CRYSTAL = 22
    MUSHROOM_BLOCK = 23
    LILY_PAD = 24
    VINE = 25
    DARK_STONE = 26
    CORAL = 27
    NPC = 28
    MUSHROOM_RED = 29
    MUSHROOM_BLUE = 30
    BUSH = 31
    CRATE = 32
    SIGN = 33
    STONE_BLOCK = 34
    TREE_PINE = 35
    TREE_OAK = 36
    TREE_MUSHROOM = 37
    SNOWMAN = 38
    IGLOO = 39
    ICE_BOX = 40
    SNOW_TREE_1 = 41
    SNOW_TREE_2 = 42
    MUSHROOM_TREE_1 = 43
    MUSHROOM_TREE_2 = 44
    MUSHROOM_TREE_3 = 45
    MUSHROOM_1 = 46
    MUSHROOM_2 = 47
    MUSHROOM_BUSH_1 = 48
    MUSHROOM_BUSH_2 = 50
    MUSHROOM_BUSH_3 = 51
    MUSHROOM_BUSH_4 = 52
    
    # Factory biome tiles
    FACTORY_FLOOR = 53
    FACTORY_WALL = 54
    FACTORY_PIPE = 55
    FACTORY_GEAR = 56
    FACTORY_BOX = 57
    FACTORY_CRATE = 58
    FACTORY_BARREL = 59
    FACTORY_ACID = 60
    FACTORY_SAW = 61
    FACTORY_SWITCH = 62
    FACTORY_DOOR_OPEN = 63
    FACTORY_DOOR_CLOSED = 64
    
    # Dessert biome tiles
    DESSERT_SAND = 65
    DESSERT_GRASS_1 = 66
    DESSERT_GRASS_2 = 67
    DESSERT_BUSH_1 = 68
    DESSERT_BUSH_2 = 69
    DESSERT_TREE = 70
    DESSERT_CACTUS_1 = 71
    DESSERT_CACTUS_2 = 72
    DESSERT_CACTUS_3 = 73
    DESSERT_ROCK = 74
    DESSERT_SKELETON = 75
    DESSERT_SIGN = 76
    DESSERT_SIGN_ARROW = 77

# Item Types
class ItemType(IntEnum):
    # Tools
    AXE = 1
    PICKAXE = 2
    HOE = 3
    WATERING_CAN = 4
    SWORD = 5
    SHOVEL = 6
    
    # Resources
    WOOD = 50
    STONE = 51
    IRON = 52
    GOLD = 53
    DIAMOND = 54
    MUSHROOM_RED = 55
    MUSHROOM_BLUE = 56
    FLOWER = 57
    
    # Consumables
    APPLE = 100
    BREAD = 101
    HEALTH_POTION = 102
    SPEED_POTION = 103
    
    # Special
    KEY = 200
    TREASURE = 201
    CRYSTAL = 202

@dataclass
class Item:
    item_type: ItemType
    quantity: int = 1
    max_stack: int = 99
    
    def can_stack(self, other: 'Item') -> bool:
        return (self.item_type == other.item_type and 
                self.quantity < self.max_stack)
    
    def __str__(self) -> str:
        return f"{self.quantity}x {self.item_type.name.replace('_', ' ').title()}"

class Inventory:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.items: List[Item] = []
        self.selected_slot: int = 0
    
    def add_item(self, item_type: ItemType, quantity: int = 1) -> bool:
        """Add an item to the inventory. Returns True if successful."""
        # Try to stack with existing items first
        for item in self.items:
            if item.item_type == item_type and item.quantity < item.max_stack:
                add_amount = min(quantity, item.max_stack - item.quantity)
                item.quantity += add_amount
                quantity -= add_amount
                if quantity <= 0:
                    return True
        
        # If there's still items to add and we have space, add new stack
        while quantity > 0 and len(self.items) < self.capacity:
            stack_size = min(quantity, 99)  # Default max stack size
            self.items.append(Item(item_type, stack_size))
            quantity -= stack_size
        
        return quantity == 0  # Return True if all items were added
    
    def remove_item(self, item_type: ItemType, quantity: int = 1) -> bool:
        """Remove items from inventory. Returns True if successful."""
        # Find all stacks of this item type
        stacks = [i for i, item in enumerate(self.items) 
                 if item.item_type == item_type]
        
        # Calculate total available
        total = sum(self.items[i].quantity for i in stacks)
        if total < quantity:
            return False  # Not enough items
        
        # Remove items from stacks (last to first)
        for i in reversed(stacks):
            if quantity <= 0:
                break
            item = self.items[i]
            remove = min(quantity, item.quantity)
            item.quantity -= remove
            quantity -= remove
            if item.quantity <= 0:
                self.items.pop(i)
        
        return True
    
    def get_selected_item(self) -> Optional[Item]:
        """Get the currently selected item."""
        if 0 <= self.selected_slot < len(self.items):
            return self.items[self.selected_slot]
        return None
    
    def select_slot(self, slot: int) -> None:
        """Select an inventory slot (0-based)."""
        if 0 <= slot < self.capacity:
            self.selected_slot = slot
    
    def get_item_count(self, item_type: ItemType) -> int:
        """Get total count of a specific item type."""
        return sum(item.quantity for item in self.items 
                  if item.item_type == item_type)
    
    def has_item(self, item_type: ItemType, quantity: int = 1) -> bool:
        """Check if inventory has at least 'quantity' of item_type."""
        return self.get_item_count(item_type) >= quantity

# Map tile types to item types
TILE_TO_ITEM = {
    Tile.TREE: ItemType.WOOD,
    Tile.TREE_PINE: ItemType.WOOD,
    Tile.STONE: ItemType.STONE,
    Tile.IRON_ORE: ItemType.IRON,
    Tile.GOLD_ORE: ItemType.GOLD,
    Tile.DIAMOND_ORE: ItemType.DIAMOND,
    Tile.MUSHROOM_RED: ItemType.MUSHROOM_RED,
    Tile.MUSHROOM_BLUE: ItemType.MUSHROOM_BLUE,
    Tile.FLOWER: ItemType.FLOWER,
    Tile.TREASURE: ItemType.TREASURE,
    Tile.CRYSTAL: ItemType.CRYSTAL,
    Tile.KEY_ITEM: ItemType.KEY
}

WALKABLE = [
    Tile.GRASS, Tile.DIRT, Tile.FLOWER, Tile.TREASURE, Tile.KEY_ITEM,
    Tile.QUESTION_BLOCK, Tile.SNOW, Tile.SAND, Tile.PORTAL, Tile.CRYSTAL,
    Tile.ICE, Tile.MUSHROOM_BLOCK, Tile.LILY_PAD, Tile.DARK_STONE, Tile.NPC,
    Tile.BRICK, Tile.OBSIDIAN, Tile.MUSHROOM_RED, Tile.MUSHROOM_BLUE, 
    Tile.BUSH, Tile.CRATE, Tile.SIGN, Tile.STONE_BLOCK, Tile.IGLOO, 
    Tile.ICE_BOX, Tile.SNOW_TREE_1, Tile.SNOW_TREE_2, Tile.SNOWMAN,
    Tile.MUSHROOM_1, Tile.MUSHROOM_2, Tile.MUSHROOM_BUSH_1, Tile.MUSHROOM_BUSH_2,
    Tile.MUSHROOM_BUSH_3, Tile.MUSHROOM_BUSH_4,
    # Factory walkable tiles
    Tile.FACTORY_FLOOR, Tile.FACTORY_BOX, Tile.FACTORY_CRATE, Tile.FACTORY_SWITCH,
    Tile.FACTORY_DOOR_OPEN,
    # Dessert walkable tiles
    Tile.DESSERT_SAND, Tile.DESSERT_GRASS_1, Tile.DESSERT_GRASS_2, 
    Tile.DESSERT_BUSH_1, Tile.DESSERT_BUSH_2, Tile.DESSERT_SIGN, 
    Tile.DESSERT_SIGN_ARROW
]

# Asset Loading Functions
def load_image(path, scale=1, colorkey=None, required=False, max_size=None):
    """Load an image with optional scaling and transparency handling."""
    try:
        if not path or not isinstance(path, str):
            raise ValueError(f"Invalid image path: {path}")
            
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
            
        # Load the image
        image = pygame.image.load(path)
        if image is None:
            raise RuntimeError(f"Failed to load image (returned None): {path}")
        
        # Convert to a surface with per-pixel alpha for transparency
        if image.get_alpha():
            image = image.convert_alpha()
        else:
            image = image.convert()
            # If no colorkey is specified, use the color of the top-left pixel
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)
            
            # For images without alpha, convert to surface with per-pixel alpha
            # This helps with smooth edges when scaling
            alpha_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            alpha_surface.blit(image, (0, 0))
            image = alpha_surface
        
        # Apply max_size constraint if specified
        if max_size is not None:
            width, height = image.get_size()
            max_width, max_height = max_size
            
            if width > max_width or height > max_height:
                # Calculate scale to fit within max_size while maintaining aspect ratio
                scale_w = max_width / width
                scale_h = max_height / height
                scale = min(scale_w, scale_h, scale)
        
        # Apply scaling
        if scale != 1:
            width, height = image.get_size()
            # Use smoothscale for better quality when scaling down
            if scale < 1:
                image = pygame.transform.smoothscale(image, (int(width * scale), int(height * scale)))
            else:
                image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        
        return image
        
    except Exception as e:
        if required:
            raise RuntimeError(f"Failed to load required image '{path}': {str(e)}")
            
        # Create placeholder
        size = max_size[0] if max_size else int(TILE_SIZE * scale)
        return create_error_surface(f"ERR: {os.path.basename(path)[:8]}", size)

def create_error_surface(text, size=64):
    """Create a placeholder surface with error pattern."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Checkerboard pattern
    for x in range(0, size, 8):
        for y in range(0, size, 8):
            color = (255, 0, 255, 128) if (x + y) // 8 % 2 == 0 else (0, 255, 255, 128)
            pygame.draw.rect(surf, color, (x, y, 8, 8))
    
    # Error text
    font = pygame.font.SysFont('Arial', 8)
    text_surface = font.render(text, True, (255, 0, 0))
    surf.blit(text_surface, (2, 2))
    
    return surf

def load_animation_frames(folder_path, pattern='*.png', scale=1, colorkey=None, required=False):
    """Load all images from a folder as animation frames with transparency handling."""
    try:
        import re
        import glob
        
        # If pattern contains wildcards, use glob to find matching files
        if '*' in pattern or '?' in pattern:
            search_path = os.path.join(folder_path, pattern)
            image_files = glob.glob(search_path)
            # Extract just the filenames for consistent processing
            image_files = [os.path.basename(f) for f in image_files]
        else:
            # Fallback to directory listing if no wildcards in pattern
            if not os.path.isdir(folder_path):
                if required:
                    raise FileNotFoundError(f"Animation folder not found: {folder_path}")
                return [create_error_surface(f"Missing: {os.path.basename(folder_path)}", int(TILE_SIZE * scale))]
            
            image_files = [f for f in os.listdir(folder_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        # Natural sort to ensure frames are in the right order
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower()
                   for text in re.split(r'(\d+)', s)]
        
        image_files.sort(key=natural_sort_key)
        
        if not image_files:
            if required:
                raise FileNotFoundError(f"No matching images found in: {os.path.join(folder_path, pattern)}")
            return [create_error_surface("No Frames", int(TILE_SIZE * scale))]
        
        frames = []
        for file in image_files:
            try:
                frame_path = os.path.join(folder_path, file)
                # For the ninja sprites, use colorkey to remove the blue background
                # We'll use the top-left pixel color as the colorkey
                frame = load_image(frame_path, scale, colorkey=-1, required=required)
                
                if frame is not None:
                    # If the image still has a colored background, we'll try to remove it
                    if frame.get_at((0, 0)) in [(0, 0, 255, 255), (0, 0, 0, 255)]:  # Blue or black
                        # Create a new surface with per-pixel alpha
                        new_surface = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                        # Copy pixels that aren't the background color
                        for x in range(frame.get_width()):
                            for y in range(frame.get_height()):
                                pixel = frame.get_at((x, y))
                                if pixel not in [(0, 0, 255, 255), (0, 0, 0, 255)]:
                                    new_surface.set_at((x, y), pixel)
                        frame = new_surface
                    
                    frames.append(frame)
            except Exception as e:
                if required:
                    raise
                print(f"Warning: Could not load {file}: {str(e)}")
        
        if not frames and required:
            raise RuntimeError(f"No valid frames loaded from {os.path.join(folder_path, pattern)}")
            
        return frames if frames else [create_error_surface("Load Error", int(TILE_SIZE * scale))]
        
    except Exception as e:
        if required:
            raise RuntimeError(f"Failed to load animation from {os.path.join(folder_path, pattern)}: {str(e)}")
        error_msg = f"Error: {str(e)[:30]}..." if len(str(e)) > 30 else str(e)
        return [create_error_surface(error_msg, int(TILE_SIZE * scale))]

# Player Animations
import math

def ease_in_out_quad(t):
    """Easing function for smooth acceleration and deceleration"""
    return 2 * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 2) / 2

class PlayerAnimations:
    def __init__(self):
        base_path = 'assets/sprites/characters/player/Ninja'
        self.load_successful = False
        
        # Animation configurations
        self.animation_config = {
            'idle': {'speed': 0.15, 'loop': True, 'next_anim': None},
            'walk': {'speed': 0.1, 'loop': True, 'next_anim': 'idle'},
            'run': {'speed': 0.08, 'loop': True, 'next_anim': 'idle'},
            'jump': {'speed': 0.12, 'loop': False, 'next_anim': 'idle'},
            'attack': {'speed': 0.07, 'loop': False, 'next_anim': 'idle'},
            'dead': {'speed': 0.2, 'loop': False, 'next_anim': None}
        }
        
        # Animation state
        self.current_animation_name = 'idle'
        self.previous_animation = 'idle'
        self.animation_frame = 0.0  # Using float for sub-frame precision
        self.current_time = 0.0
        self.animation_complete = False
        self.facing_right = True
        self.transition_time = 0.0
        self.transition_duration = 0.15  # seconds for transition between animations
        
        # Load animations
        try:
            # Try to load actual sprites
            self.animations = {
                'idle': self.load_and_clean_frames(os.path.join(base_path, 'Idle'), '*.png', 1.5) or self.create_player_idle_animation(),
                'walk': self.load_and_clean_frames(os.path.join(base_path, 'Run'), '*.png', 1.5) or self.create_player_walk_animation(),
                'run': self.load_and_clean_frames(os.path.join(base_path, 'Run'), '*.png', 1.5) or self.create_player_walk_animation(),
                'jump': self.load_and_clean_frames(os.path.join(base_path, 'Jump'), '*.png', 1.5) or self.create_player_jump_animation(),
                'attack': self.load_and_clean_frames(os.path.join(base_path, 'Attack1'), '*.png', 1.5) or self.create_player_attack_animation(),
                'dead': self.load_and_clean_frames(os.path.join(base_path, 'Dead'), '*.png', 1.5) or self.create_player_dead_animation()
            }
            self.load_successful = all(self.animations.values())
        except Exception as e:
            print(f"Error loading animations: {e}")
            self.load_successful = False
        
        # If loading failed, create fallback animations
        if not self.load_successful:
            self.animations = {
                'idle': self.create_player_idle_animation(),
                'walk': self.create_player_walk_animation(),
                'run': self.create_player_walk_animation(),
                'jump': self.create_player_jump_animation(),
                'attack': self.create_player_attack_animation(),
                'dead': self.create_player_dead_animation()
            }
        
        # Set initial animation
        self.current_animation = self.animations['idle']
        
    def set_animation(self, animation_name, force=False):
        """Switch to a different animation"""
        if animation_name not in self.animations or animation_name == self.current_animation_name:
            return False
            
        # Don't interrupt non-looping animations unless forced
        if not force and not self.animation_config[self.current_animation_name]['loop'] and not self.animation_complete:
            return False
            
        self.previous_animation = self.current_animation_name
        self.current_animation_name = animation_name
        self.animation_frame = 0.0
        self.animation_complete = False
        self.transition_time = 0.0
        self.current_animation = self.animations[animation_name]
        return True
        
    def get_animation_progress(self):
        """Get the current animation progress (0.0 to 1.0)"""
        if not self.current_animation:
            return 0.0
        return (self.animation_frame % len(self.current_animation)) / len(self.current_animation)
        
    def update(self, dt):
        """Update animation state"""
        if not self.current_animation:
            return
            
        config = self.animation_config[self.current_animation_name]
        
        # Update transition time
        if self.transition_time < self.transition_duration:
            self.transition_time = min(self.transition_time + dt, self.transition_duration)
        
        # Update animation frame
        if not self.animation_complete:
            frame_count = len(self.current_animation)
            frame_delta = dt / config['speed']
            self.animation_frame += frame_delta
            
            # Handle end of animation
            if self.animation_frame >= frame_count:
                if config['loop']:
                    self.animation_frame %= frame_count
                else:
                    self.animation_frame = frame_count - 0.001  # Stay on last frame
                    self.animation_complete = True
                    if config['next_anim']:
                        self.set_animation(config['next_anim'])
    
    def get_current_frame(self, alpha=1.0):
        """Get the current animation frame with optional alpha blending"""
        if not self.current_animation:
            return create_error_surface("Player", 64)
            
        # Get current and next frame indices
        frame_count = len(self.current_animation)
        frame_idx = int(self.animation_frame) % frame_count
        next_frame_idx = (frame_idx + 1) % frame_count
        
        # Get interpolation factor (0.0 to 1.0)
        t = self.animation_frame - int(self.animation_frame)
        
        # Apply easing for smoother transitions
        t = ease_in_out_quad(t)
        
        # Get current and next frames
        current_frame = self.current_animation[frame_idx]
        next_frame = self.current_animation[next_frame_idx]
        
        # If we're not interpolating or at the last frame of a non-looping animation
        if t < 0.01 or (not self.animation_config[self.current_animation_name]['loop'] and 
                        frame_idx == frame_count - 1):
            return current_frame
            
        # Create interpolated frame
        width = max(current_frame.get_width(), next_frame.get_width())
        height = max(current_frame.get_height(), next_frame.get_height())
        result = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Blend between current and next frame
        current_frame.set_alpha(int(255 * (1 - t) * alpha))
        next_frame.set_alpha(int(255 * t * alpha))
        
        result.blit(current_frame, (0, 0))
        result.blit(next_frame, (0, 0))
        
        return result
    
    def load_and_clean_frames(self, folder_path, pattern='*.png', scale=1):
        """Load animation frames and remove backgrounds."""
        import glob
        import re
        
        try:
            search_path = os.path.join(folder_path, pattern)
            image_files = glob.glob(search_path)
            
            if not image_files:
                return None
            
            # Natural sort
            def natural_sort_key(s):
                return [int(text) if text.isdigit() else text.lower()
                       for text in re.split(r'(\d+)', s)]
            
            image_files.sort(key=natural_sort_key)
            
            frames = []
            for img_path in image_files:
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    
                    # Remove background (blue or black)
                    clean_img = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    
                    # Get the background color from top-left corner
                    bg_color = img.get_at((0, 0))
                    
                    for x in range(img.get_width()):
                        for y in range(img.get_height()):
                            pixel = img.get_at((x, y))
                            
                            # Calculate color difference from background
                            diff = abs(pixel[0] - bg_color[0]) + abs(pixel[1] - bg_color[1]) + abs(pixel[2] - bg_color[2])
                            
                            # If pixel is significantly different from background, keep it
                            if diff > 50:  # Threshold for color difference
                                clean_img.set_at((x, y), pixel)
                    
                    # Scale if needed
                    if scale != 1:
                        width, height = clean_img.get_size()
                        new_size = (int(width * scale), int(height * scale))
                        
                        if scale < 1:
                            clean_img = pygame.transform.smoothscale(clean_img, new_size)
                        else:
                            clean_img = pygame.transform.scale(clean_img, new_size)
                    
                    frames.append(clean_img)
                except Exception as e:
                    print(f"Error loading frame {img_path}: {e}")
                    pass
            
            return frames if frames else None
        except Exception as e:
            print(f"Error loading frames: {e}")
            return None
    
    def create_player_idle_animation(self):
        """Create a simple player idle animation."""
        frames = []
        for i in range(4):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            # Body
            body_y = TILE_SIZE // 2
            
            # Head
            pygame.draw.circle(surf, (255, 220, 177), (TILE_SIZE//2, body_y - 15), 10)
            
            # Body
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 8, body_y - 5, 16, 20), border_radius=3)
            
            # Arms
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 16, body_y, 8, 15), border_radius=2)
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 + 8, body_y, 8, 15), border_radius=2)
            
            # Legs
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 - 6, body_y + 15, 5, 15), border_radius=2)
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 + 1, body_y + 15, 5, 15), border_radius=2)
            
            # Eyes
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 - 3, body_y - 17), 2)
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 + 3, body_y - 17), 2)
            
            frames.append(surf)
        return frames
    
    def create_player_walk_animation(self):
        """Create a simple walking animation."""
        frames = []
        for i in range(6):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            body_y = TILE_SIZE // 2
            leg_swing = int(5 * math.sin(i * math.pi / 3))
            arm_swing = int(4 * math.cos(i * math.pi / 3))
            
            # Head
            pygame.draw.circle(surf, (255, 220, 177), (TILE_SIZE//2, body_y - 15), 10)
            
            # Body
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 8, body_y - 5, 16, 20), border_radius=3)
            
            # Arms (swinging)
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 16, body_y + arm_swing, 8, 15), border_radius=2)
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 + 8, body_y - arm_swing, 8, 15), border_radius=2)
            
            # Legs (walking)
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 - 6, body_y + 15 + leg_swing, 5, 15), border_radius=2)
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 + 1, body_y + 15 - leg_swing, 5, 15), border_radius=2)
            
            # Eyes
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 - 3, body_y - 17), 2)
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 + 3, body_y - 17), 2)
            
            frames.append(surf)
        return frames
    
    def create_player_jump_animation(self):
        """Create a simple jump animation."""
        frames = []
        for i in range(3):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            body_y = TILE_SIZE // 2 - 5  # Slightly raised
            
            # Head
            pygame.draw.circle(surf, (255, 220, 177), (TILE_SIZE//2, body_y - 15), 10)
            
            # Body
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 8, body_y - 5, 16, 20), border_radius=3)
            
            # Arms (raised)
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 16, body_y - 8, 8, 15), border_radius=2)
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 + 8, body_y - 8, 8, 15), border_radius=2)
            
            # Legs (tucked)
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 - 6, body_y + 10, 5, 12), border_radius=2)
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 + 1, body_y + 10, 5, 12), border_radius=2)
            
            # Eyes
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 - 3, body_y - 17), 2)
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 + 3, body_y - 17), 2)
            
            frames.append(surf)
        return frames
    
    def create_player_attack_animation(self):
        """Create a simple attack animation."""
        frames = []
        for i in range(4):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            body_y = TILE_SIZE // 2
            
            # Head
            pygame.draw.circle(surf, (255, 220, 177), (TILE_SIZE//2, body_y - 15), 10)
            
            # Body
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 8, body_y - 5, 16, 20), border_radius=3)
            
            # Arms (one extended for attack)
            pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 - 16, body_y, 8, 15), border_radius=2)
            if i < 2:
                # Arm extending
                arm_extend = i * 8
                pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 + 8 + arm_extend, body_y - 2, 12, 8), border_radius=2)
                # Attack effect
                if i == 1:
                    pygame.draw.circle(surf, (255, 255, 0), (TILE_SIZE//2 + 24, body_y + 2), 6)
            else:
                pygame.draw.rect(surf, (50, 150, 255), (TILE_SIZE//2 + 8, body_y, 8, 15), border_radius=2)
            
            # Legs
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 - 6, body_y + 15, 5, 15), border_radius=2)
            pygame.draw.rect(surf, (40, 40, 100), (TILE_SIZE//2 + 1, body_y + 15, 5, 15), border_radius=2)
            
            # Eyes
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 - 3, body_y - 17), 2)
            pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2 + 3, body_y - 17), 2)
            
            frames.append(surf)
        return frames
    
    def create_player_dead_animation(self):
        """Create a simple death animation."""
        frames = []
        for i in range(3):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            body_y = TILE_SIZE // 2 + i * 5  # Falling down
            opacity = max(100, 255 - i * 50)
            
            # Head
            color = (255, 220, 177, opacity)
            temp_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, color, (10, 10), 10)
            surf.blit(temp_surf, (TILE_SIZE//2 - 10, body_y - 15))
            
            # Body (lying down in later frames)
            body_color = (50, 150, 255, opacity)
            temp_surf = pygame.Surface((16, 20), pygame.SRCALPHA)
            pygame.draw.rect(temp_surf, body_color, (0, 0, 16, 20), border_radius=3)
            surf.blit(temp_surf, (TILE_SIZE//2 - 8, body_y - 5))
            
            frames.append(surf)
        return frames

    def update(self, dt):
        if not self.current_animation:
            return
        self.current_time += dt
        frame_duration = 1.0 / len(self.current_animation)
        self.animation_frame = int(self.current_time / frame_duration) % len(self.current_animation)
    
    def get_current_frame(self):
        if not self.current_animation:
            return create_error_surface("Player", 64)
        return self.current_animation[self.animation_frame]


# NPC Sprites
class NPCSprites:
    def __init__(self):
        self.sprites = {}
        self.animations = {}
        self.placeholder = create_error_surface("NPC", 32)
        self.npc_base_path = 'assets/sprites/characters/npcs/'
        self.load_npcs()
        
    def create_emoji_sprite(self, emoji, color, size=64):
        """Create a sprite from an emoji with a colored background circle."""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw colored circle background
        pygame.draw.circle(surf, color, (size//2, size//2), size//2 - 4)
        pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//2 - 4, 3)
        
        # Render emoji
        try:
            emoji_font = pygame.font.SysFont('Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji', int(size * 0.6))
            emoji_surf = emoji_font.render(emoji, True, (255, 255, 255))
            emoji_rect = emoji_surf.get_rect(center=(size//2, size//2))
            surf.blit(emoji_surf, emoji_rect)
        except:
            # Fallback to default font if emoji font not available
            fallback_font = pygame.font.Font(None, int(size * 0.6))
            text_surf = fallback_font.render(emoji, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(size//2, size//2))
            surf.blit(text_surf, text_rect)
        
        return surf
        
    def load_npcs(self):
        # Map of NPC types to their corresponding sprite folders
        npc_folders = {
            'MERCHANT': 'merchant',
            'EXPLORER': 'explorer',
            'WIZARD': 'wizard',
            'FARMER': 'farmer',
        }
        
        for npc_type in NPC_TYPES.keys():
            folder = npc_folders.get(npc_type, npc_type.lower())
            npc_path = os.path.join(self.npc_base_path, folder)
            
            # Try to load idle animation frames
            idle_frames = []
            
            try:
                if os.path.exists(npc_path):
                    # Look for any image files in the NPC's folder
                    image_files = []
                    # Check for common animation subdirectories
                    possible_subdirs = ['idle', 'Idle', 'IDLE', '']
                    
                    for subdir in possible_subdirs:
                        check_path = os.path.join(npc_path, subdir) if subdir else npc_path
                        if os.path.exists(check_path):
                            image_files = [os.path.join(check_path, f) for f in os.listdir(check_path) 
                                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                            if image_files:
                                break
                    
                    if image_files:
                        # Sort files to maintain consistent order
                        import re
                        image_files.sort(key=lambda x: [int(t) if t.isdigit() else t.lower() 
                                                     for t in re.split('(\d+)', x)])
                        
                        # Load and scale each image
                        for img_file in image_files:
                            try:
                                img = pygame.image.load(img_file).convert_alpha()
                                
                                # Remove black/dark background if present
                                clean_img = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                                
                                # Copy all non-black pixels
                                for x in range(img.get_width()):
                                    for y in range(img.get_height()):
                                        pixel = img.get_at((x, y))
                                        # Keep pixels that aren't pure black or very dark
                                        if pixel[0] > 15 or pixel[1] > 15 or pixel[2] > 15:
                                            clean_img.set_at((x, y), pixel)
                                
                                # Scale image to fit within 1.5x tile size
                                width, height = clean_img.get_size()
                                scale = min(1.0, (TILE_SIZE * 1.5) / max(width, height))
                                new_size = (int(width * scale), int(height * scale))
                                
                                if scale < 1.0:
                                    clean_img = pygame.transform.smoothscale(clean_img, new_size)
                                else:
                                    clean_img = pygame.transform.scale(clean_img, new_size)
                                    
                                idle_frames.append(clean_img)
                            except Exception as e:
                                pass
            except Exception as e:
                pass
            
            # If no images were loaded, create fallback sprites
            if not idle_frames:
                npc_data = NPC_TYPES.get(npc_type, {})
                emoji = npc_data.get('icon', '👤')
                color = npc_data.get('color', (100, 100, 200))
                
                # Create 3 slightly different frames for animation
                for i in range(3):
                    sprite = self.create_emoji_sprite(emoji, color, size=int(TILE_SIZE * 1.2))
                    # Add slight variation for animation (bobbing effect)
                    if i == 1:
                        temp_surf = pygame.Surface((sprite.get_width(), sprite.get_height()), pygame.SRCALPHA)
                        temp_surf.blit(sprite, (0, -2))
                        sprite = temp_surf
                    idle_frames.append(sprite)
            
            # Initialize animation data
            self.animations[npc_type] = {
                'idle': idle_frames,
                'current_frame': 0,
                'animation_speed': 0.3,
                'current_time': 0
            }
            self.sprites[npc_type] = idle_frames[0]
    
    def update(self, dt):
        """Update NPC animations."""
        for npc_type, anim in self.animations.items():
            if not anim['idle']:
                continue
                
            anim['current_time'] += dt
            if anim['current_time'] >= anim['animation_speed']:
                anim['current_time'] = 0
                anim['current_frame'] = (anim['current_frame'] + 1) % len(anim['idle'])
                self.sprites[npc_type] = anim['idle'][anim['current_frame']]
        
    def get(self, npc_type):
        """Get NPC sprite, creating fallback if needed."""
        if npc_type not in self.sprites:
            npc_data = NPC_TYPES.get(npc_type, {})
            emoji = npc_data.get('icon', '👤')
            color = npc_data.get('color', (100, 100, 200))
            
            # Create 3 slightly different frames for animation
            for i in range(3):
                # Try emoji sprite first
                sprite = self.create_emoji_sprite(emoji, color, size=int(TILE_SIZE * 1.2))
                # Add slight variation for animation (bobbing effect)
                if i == 1:
                    # Slightly raised
                    temp_surf = pygame.Surface((sprite.get_width(), sprite.get_height()), pygame.SRCALPHA)
                    temp_surf.blit(sprite, (0, -2))
                    sprite = temp_surf
                idle_frames.append(sprite)
            
            # Initialize animation data
            self.animations[npc_type] = {
                'idle': idle_frames,
                'current_frame': 0,
                'animation_speed': 0.3,  # Slower animation for NPCs
                'current_time': 0
            }
            self.sprites[npc_type] = idle_frames[0]
        
        # Try to get the sprite, fallback to creating one if not found
        return self.sprites[npc_type]

# NPC Sprites
# NPC Sprites
class NPCSprites:
    def __init__(self):
        self.sprites = {}
        self.animations = {}
        self.placeholder = create_error_surface("NPC", 32)
        self.npc_base_path = 'assets/sprites/characters/npcs/'
        self.load_npcs()
        
    def create_emoji_sprite(self, emoji, color, size=64):
        """Create a sprite from an emoji with a colored background circle."""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw colored circle background
        pygame.draw.circle(surf, color, (size//2, size//2), size//2 - 4)
        pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//2 - 4, 3)
        
        # Render emoji
        try:
            emoji_font = pygame.font.SysFont('Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji', int(size * 0.6))
            emoji_surf = emoji_font.render(emoji, True, (255, 255, 255))
            emoji_rect = emoji_surf.get_rect(center=(size//2, size//2))
            surf.blit(emoji_surf, emoji_rect)
        except:
            # Fallback to default font if emoji font not available
            fallback_font = pygame.font.Font(None, int(size * 0.6))
            text_surf = fallback_font.render(emoji, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(size//2, size//2))
            surf.blit(text_surf, text_rect)
        
        return surf
    
    def create_simple_character_sprite(self, npc_type, size=64):
        """Create a simple character sprite using shapes and colors."""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Get NPC data for color
        npc_data = NPC_TYPES.get(npc_type, {})
        primary_color = npc_data.get('color', (100, 100, 200))
        
        # Draw simple character
        # Head
        head_y = size // 3
        pygame.draw.circle(surf, (255, 220, 177), (size//2, head_y), size//6)
        
        # Body
        body_color = primary_color
        pygame.draw.rect(surf, body_color, (size//2 - size//8, head_y + size//8, size//4, size//3), border_radius=4)
        
        # Arms
        pygame.draw.rect(surf, body_color, (size//2 - size//4, head_y + size//6, size//8, size//5), border_radius=2)
        pygame.draw.rect(surf, body_color, (size//2 + size//8, head_y + size//6, size//8, size//5), border_radius=2)
        
        # Legs
        pygame.draw.rect(surf, (50, 50, 100), (size//2 - size//12, head_y + size//2, size//12, size//4), border_radius=2)
        pygame.draw.rect(surf, (50, 50, 100), (size//2, head_y + size//2, size//12, size//4), border_radius=2)
        
        # Eyes
        pygame.draw.circle(surf, (0, 0, 0), (size//2 - size//12, head_y - size//24), 2)
        pygame.draw.circle(surf, (0, 0, 0), (size//2 + size//12, head_y - size//24), 2)
        
        # Special accessories based on type
        if npc_type == 'MERCHANT':
            # Add a hat
            pygame.draw.rect(surf, (139, 69, 19), (size//2 - size//5, head_y - size//4, size//2.5, size//12), border_radius=2)
        elif npc_type == 'WIZARD':
            # Add a wizard hat
            points = [(size//2, head_y - size//3), (size//2 - size//6, head_y - size//6), (size//2 + size//6, head_y - size//6)]
            pygame.draw.polygon(surf, (138, 43, 226), points)
        elif npc_type == 'FARMER':
            # Add a straw hat
            pygame.draw.ellipse(surf, (210, 180, 140), (size//2 - size//4, head_y - size//4, size//2, size//8))
        elif npc_type == 'EXPLORER':
            # Add a backpack
            pygame.draw.rect(surf, (139, 69, 19), (size//2 - size//10, head_y + size//5, size//5, size//6), border_radius=2)
        
        return surf
        
    def load_npcs(self):
        # Map of NPC types to their corresponding sprite folders
        npc_folders = {
            'MERCHANT': 'merchant',
            'EXPLORER': 'explorer',
            'WIZARD': 'wizard',
            'FARMER': 'farmer',
            'KNIGHT': 'knight',
            'SCIENTIST': 'scientist',
            'NINJA_GIRL': 'Ninja Girl',
            'ROBOT': 'Robot'
        }
        
        for npc_type in NPC_TYPES.keys():
            folder = npc_folders.get(npc_type, npc_type.lower())
            npc_path = os.path.join(self.npc_base_path, folder)
            
            # Try to load idle animation frames
            idle_frames = []
            loaded_from_file = False
            
            try:
                if os.path.exists(npc_path):
                    # Look for any image files in the NPC's folder
                    image_files = []
                    # Check for common animation subdirectories
                    possible_subdirs = ['idle', 'Idle', 'IDLE', '']
                    
                    for subdir in possible_subdirs:
                        check_path = os.path.join(npc_path, subdir) if subdir else npc_path
                        if os.path.exists(check_path):
                            image_files = [os.path.join(check_path, f) for f in os.listdir(check_path) 
                                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                            if image_files:
                                break
                    
                    if image_files:
                        # Sort files to maintain consistent order
                        import re
                        image_files.sort(key=lambda x: [int(t) if t.isdigit() else t.lower() 
                                                     for t in re.split('(\d+)', x)])
                        
                        # Load and scale each image
                        for img_file in image_files:
                            try:
                                img = pygame.image.load(img_file).convert_alpha()
                                
                                # Remove black background if present
                                # Create a new surface with transparency
                                clean_img = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                                
                                # Copy all non-black pixels
                                for x in range(img.get_width()):
                                    for y in range(img.get_height()):
                                        pixel = img.get_at((x, y))
                                        # Keep pixels that aren't pure black or very dark
                                        if pixel[0] > 15 or pixel[1] > 15 or pixel[2] > 15:
                                            clean_img.set_at((x, y), pixel)
                                
                                # Scale image to fit within 1.5x tile size
                                width, height = clean_img.get_size()
                                scale = min(1.0, (TILE_SIZE * 1.5) / max(width, height))
                                new_size = (int(width * scale), int(height * scale))
                                
                                if scale < 1.0:
                                    clean_img = pygame.transform.smoothscale(clean_img, new_size)
                                else:
                                    clean_img = pygame.transform.scale(clean_img, new_size)
                                    
                                idle_frames.append(clean_img)
                                loaded_from_file = True
                            except Exception as e:
                                pass
            except Exception as e:
                pass
            
            # If no images were loaded, create fallback sprites
            if not idle_frames:
                npc_data = NPC_TYPES.get(npc_type, {})
                emoji = npc_data.get('icon', '👤')
                color = npc_data.get('color', (100, 100, 200))
                
                # Create 3 slightly different frames for animation
                for i in range(3):
                    # Try emoji sprite first
                    sprite = self.create_emoji_sprite(emoji, color, size=int(TILE_SIZE * 1.2))
                    # Add slight variation for animation (bobbing effect)
                    if i == 1:
                        # Slightly raised
                        temp_surf = pygame.Surface((sprite.get_width(), sprite.get_height()), pygame.SRCALPHA)
                        temp_surf.blit(sprite, (0, -2))
                        sprite = temp_surf
                    idle_frames.append(sprite)
            
            # Initialize animation data
            self.animations[npc_type] = {
                'idle': idle_frames,
                'current_frame': 0,
                'animation_speed': 0.3,  # Slower animation for NPCs
                'current_time': 0
            }
            self.sprites[npc_type] = idle_frames[0]
    
    def update(self, dt):
        """Update NPC animations."""
        for npc_type, anim in self.animations.items():
            if not anim['idle']:  # Skip if no frames
                continue
                
            anim['current_time'] += dt
            if anim['current_time'] >= anim['animation_speed']:
                anim['current_time'] = 0
                anim['current_frame'] = (anim['current_frame'] + 1) % len(anim['idle'])
                self.sprites[npc_type] = anim['idle'][anim['current_frame']]
        
    def get(self, npc_type):
        """Get NPC sprite, creating fallback if needed."""
        # Try to get the sprite, fallback to creating one if not found
        if npc_type not in self.sprites:
            # Create fallback sprite on demand
            npc_data = NPC_TYPES.get(npc_type, {'icon': '👤', 'color': (100, 100, 200)})
            sprite = self.create_emoji_sprite(npc_data['icon'], npc_data['color'], size=int(TILE_SIZE * 1.2))
            self.sprites[npc_type] = sprite
            self.animations[npc_type] = {
                'idle': [sprite],
                'current_frame': 0,
                'animation_speed': 0.3,
                'current_time': 0
            }
        return self.sprites[npc_type]

# Tile Sprites
class TileSprites:
    def __init__(self):
        self.sprites = {}
        self.max_tile_size = (int(TILE_SIZE * 1.2), int(TILE_SIZE * 1.2))
        self.setup_fallback_tiles()
    
    def setup_fallback_tiles(self):
        """Create graphical tiles for all tile types."""
        tile_definitions = {
            # Basic tiles
            Tile.GRASS: self.create_grass_tile,
            Tile.DIRT: self.create_dirt_tile,
            Tile.STONE: self.create_stone_tile,
            Tile.WATER: self.create_water_tile,
            Tile.TREE: self.create_tree_tile,
            Tile.FLOWER: self.create_flower_tile,
            Tile.TREASURE: self.create_treasure_tile,
            Tile.KEY_ITEM: self.create_key_tile,
            Tile.BRICK: self.create_brick_tile,
            Tile.QUESTION_BLOCK: self.create_question_tile,
            Tile.ICE: self.create_ice_tile,
            Tile.SNOW: self.create_snow_tile,
            Tile.SAND: self.create_sand_tile,
            Tile.CACTUS: self.create_cactus_tile,
            Tile.LAVA: self.create_lava_tile,
            Tile.OBSIDIAN: self.create_obsidian_tile,
            Tile.PORTAL: self.create_portal_tile,
            Tile.CRYSTAL: self.create_crystal_tile,
            
            # Mushroom biome
            Tile.MUSHROOM_RED: self.create_mushroom_red_tile,
            Tile.MUSHROOM_BLUE: self.create_mushroom_blue_tile,
            Tile.BUSH: self.create_bush_tile,
            Tile.CRATE: self.create_crate_tile,
            Tile.SIGN: self.create_sign_tile,
            Tile.STONE_BLOCK: self.create_stone_block_tile,
            Tile.TREE_PINE: self.create_tree_pine_tile,
            Tile.TREE_OAK: self.create_tree_tile,
            Tile.TREE_MUSHROOM: self.create_mushroom_tree_tile,
            Tile.LILY_PAD: self.create_lily_pad_tile,
            Tile.VINE: self.create_vine_tile,
            Tile.DARK_STONE: self.create_dark_stone_tile,
            Tile.CORAL: self.create_coral_tile,
            Tile.MUSHROOM_BLOCK: self.create_mushroom_block_tile,
            
            # Snow biome
            Tile.SNOWMAN: self.create_snowman_tile,
            Tile.IGLOO: self.create_igloo_tile,
            Tile.ICE_BOX: self.create_ice_box_tile,
            Tile.SNOW_TREE_1: self.create_snow_tree_1_tile,
            Tile.SNOW_TREE_2: self.create_snow_tree_2_tile,
            
            # Mushroom forest
            Tile.MUSHROOM_TREE_1: self.create_mushroom_tree_1_tile,
            Tile.MUSHROOM_TREE_2: self.create_mushroom_tree_2_tile,
            Tile.MUSHROOM_TREE_3: self.create_mushroom_tree_3_tile,
            Tile.MUSHROOM_1: self.create_mushroom_1_tile,
            Tile.MUSHROOM_2: self.create_mushroom_2_tile,
            Tile.MUSHROOM_BUSH_1: self.create_mushroom_bush_1_tile,
            Tile.MUSHROOM_BUSH_2: self.create_mushroom_bush_2_tile,
            Tile.MUSHROOM_BUSH_3: self.create_mushroom_bush_3_tile,
            Tile.MUSHROOM_BUSH_4: self.create_mushroom_bush_4_tile,
            
            # Factory biome
            Tile.FACTORY_FLOOR: self.create_factory_floor_tile,
            Tile.FACTORY_WALL: self.create_factory_wall_tile,
            Tile.FACTORY_PIPE: self.create_factory_pipe_tile,
            Tile.FACTORY_GEAR: self.create_factory_gear_tile,
            Tile.FACTORY_BOX: self.create_factory_box_tile,
            Tile.FACTORY_CRATE: self.create_factory_crate_tile,
            Tile.FACTORY_BARREL: self.create_factory_barrel_tile,
            Tile.FACTORY_ACID: self.create_factory_acid_tile,
            Tile.FACTORY_SAW: self.create_factory_saw_tile,
            Tile.FACTORY_SWITCH: self.create_factory_switch_tile,
            Tile.FACTORY_DOOR_OPEN: self.create_factory_door_open_tile,
            Tile.FACTORY_DOOR_CLOSED: self.create_factory_door_closed_tile,
            
            # Dessert biome
            Tile.DESSERT_SAND: self.create_dessert_sand_tile,
            Tile.DESSERT_GRASS_1: self.create_dessert_grass_1_tile,
            Tile.DESSERT_GRASS_2: self.create_dessert_grass_2_tile,
            Tile.DESSERT_BUSH_1: self.create_dessert_bush_1_tile,
            Tile.DESSERT_BUSH_2: self.create_dessert_bush_2_tile,
            Tile.DESSERT_TREE: self.create_dessert_tree_tile,
            Tile.DESSERT_CACTUS_1: self.create_dessert_cactus_1_tile,
            Tile.DESSERT_CACTUS_2: self.create_dessert_cactus_2_tile,
            Tile.DESSERT_CACTUS_3: self.create_dessert_cactus_3_tile,
            Tile.DESSERT_ROCK: self.create_dessert_rock_tile,
            Tile.DESSERT_SKELETON: self.create_dessert_skeleton_tile,
            Tile.DESSERT_SIGN: self.create_dessert_sign_tile,
            Tile.DESSERT_SIGN_ARROW: self.create_dessert_sign_arrow_tile,
        }
        
        for tile_type, create_func in tile_definitions.items():
            self.sprites[tile_type] = create_func()
    
    def create_grass_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Add grass texture
        for _ in range(20):
            x, y = random.randint(0, TILE_SIZE), random.randint(0, TILE_SIZE)
            pygame.draw.line(surf, (22, 163, 74), (x, y), (x, y-5), 1)
        return surf
    
    def create_dirt_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((146, 64, 14))
        # Add dirt texture
        for _ in range(15):
            x, y = random.randint(0, TILE_SIZE), random.randint(0, TILE_SIZE)
            pygame.draw.circle(surf, (120, 50, 10), (x, y), 2)
        return surf
    
    def create_stone_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((156, 163, 175))
        pygame.draw.rect(surf, (107, 114, 128), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        return surf
    
    def create_water_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((59, 130, 246))
        # Wave pattern
        for i in range(0, TILE_SIZE, 8):
            pygame.draw.line(surf, (96, 165, 250), (i, TILE_SIZE//2), (i+4, TILE_SIZE//2+2), 2)
        return surf
    
    def create_tree_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((34, 197, 94))
        # Tree trunk
        pygame.draw.rect(surf, (101, 67, 33), (TILE_SIZE//2-6, TILE_SIZE//2, 12, 20))
        # Tree foliage
        pygame.draw.circle(surf, (0, 128, 0), (TILE_SIZE//2, TILE_SIZE//2-5), 18)
        pygame.draw.circle(surf, (34, 139, 34), (TILE_SIZE//2, TILE_SIZE//2-5), 15)
        return surf
    
    def create_flower_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Flower
        colors = [(255, 192, 203), (255, 0, 255), (255, 255, 0)]
        color = random.choice(colors)
        center = (TILE_SIZE//2, TILE_SIZE//2)
        for angle in range(0, 360, 60):
            x = center[0] + int(8 * math.cos(math.radians(angle)))
            y = center[1] + int(8 * math.sin(math.radians(angle)))
            pygame.draw.circle(surf, color, (x, y), 6)
        pygame.draw.circle(surf, (255, 255, 0), center, 5)
        return surf
    
    def create_treasure_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Treasure chest
        pygame.draw.rect(surf, (139, 69, 19), (TILE_SIZE//2-12, TILE_SIZE//2-8, 24, 16))
        pygame.draw.rect(surf, (255, 215, 0), (TILE_SIZE//2-10, TILE_SIZE//2-6, 20, 12))
        pygame.draw.rect(surf, (184, 134, 11), (TILE_SIZE//2-10, TILE_SIZE//2-6, 20, 12), 2)
        return surf
    
    def create_key_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Key shape
        pygame.draw.circle(surf, (255, 215, 0), (TILE_SIZE//2-8, TILE_SIZE//2), 6)
        pygame.draw.rect(surf, (255, 215, 0), (TILE_SIZE//2-2, TILE_SIZE//2-2, 16, 4))
        pygame.draw.line(surf, (255, 215, 0), (TILE_SIZE//2+10, TILE_SIZE//2), (TILE_SIZE//2+10, TILE_SIZE//2+4), 3)
        return surf
    
    def create_brick_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((217, 119, 6))
        # Brick pattern
        for y in range(0, TILE_SIZE, 16):
            offset = 16 if (y // 16) % 2 else 0
            for x in range(-16 + offset, TILE_SIZE, 32):
                pygame.draw.rect(surf, (139, 69, 19), (x, y, 30, 14), 2)
        return surf
    
    def create_question_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((251, 191, 36))
        pygame.draw.rect(surf, (217, 119, 6), (0, 0, TILE_SIZE, TILE_SIZE), 3)
        # Question mark
        question_font = pygame.font.Font(None, 48)
        text = question_font.render('?', True, WHITE)
        surf.blit(text, text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2)))
        return surf
    
    def create_ice_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((173, 216, 230))
        # Ice cracks
        pygame.draw.line(surf, (147, 197, 253), (5, 5), (TILE_SIZE-5, TILE_SIZE-5), 2)
        pygame.draw.line(surf, (147, 197, 253), (TILE_SIZE-5, 5), (5, TILE_SIZE-5), 2)
        return surf
    
    def create_snow_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((255, 250, 250))
        # Snow dots
        for _ in range(10):
            x, y = random.randint(0, TILE_SIZE), random.randint(0, TILE_SIZE)
            pygame.draw.circle(surf, (240, 248, 255), (x, y), 2)
        return surf
    
    def create_sand_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((238, 214, 175))
        # Sand texture
        for _ in range(20):
            x, y = random.randint(0, TILE_SIZE), random.randint(0, TILE_SIZE)
            pygame.draw.circle(surf, (222, 184, 135), (x, y), 1)
        return surf
    
    def create_cactus_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((238, 214, 175))
        # Cactus
        pygame.draw.rect(surf, (34, 139, 34), (TILE_SIZE//2-6, TILE_SIZE//2-10, 12, 25))
        pygame.draw.rect(surf, (0, 100, 0), (TILE_SIZE//2-15, TILE_SIZE//2), 9, 8)
        pygame.draw.rect(surf, (0, 100, 0), (TILE_SIZE//2+6, TILE_SIZE//2+3), 9, 8)
        return surf
    
    def create_lava_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((255, 69, 0))
        # Lava bubbles
        for _ in range(5):
            x, y = random.randint(0, TILE_SIZE), random.randint(0, TILE_SIZE)
            pygame.draw.circle(surf, (255, 140, 0), (x, y), 6)
            pygame.draw.circle(surf, (255, 215, 0), (x, y), 3)
        return surf
    
    def create_obsidian_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((20, 20, 20))
        pygame.draw.rect(surf, (60, 60, 60), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        return surf
    
    def create_portal_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((138, 43, 226))
        # Portal swirl
        for r in range(5, 25, 5):
            pygame.draw.circle(surf, (147, 51, 234), (TILE_SIZE//2, TILE_SIZE//2), r, 2)
        return surf
    
    def create_crystal_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((107, 114, 128))
        # Crystal
        points = [(TILE_SIZE//2, TILE_SIZE//2-15), (TILE_SIZE//2-10, TILE_SIZE//2+10),
                  (TILE_SIZE//2+10, TILE_SIZE//2+10)]
        pygame.draw.polygon(surf, (147, 112, 219), points)
        pygame.draw.polygon(surf, (186, 85, 211), points, 2)
        return surf
    
    def create_mushroom_red_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Mushroom stem
        pygame.draw.rect(surf, (245, 245, 220), (TILE_SIZE//2-5, TILE_SIZE//2, 10, 15))
        # Mushroom cap
        pygame.draw.ellipse(surf, (220, 38, 38), (TILE_SIZE//2-15, TILE_SIZE//2-10, 30, 20))
        # White dots
        pygame.draw.circle(surf, WHITE, (TILE_SIZE//2-7, TILE_SIZE//2-3), 3)
        pygame.draw.circle(surf, WHITE, (TILE_SIZE//2+5, TILE_SIZE//2-5), 3)
        return surf
    
    def create_mushroom_blue_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Mushroom stem
        pygame.draw.rect(surf, (245, 245, 220), (TILE_SIZE//2-5, TILE_SIZE//2, 10, 15))
        # Mushroom cap
        pygame.draw.ellipse(surf, (59, 130, 246), (TILE_SIZE//2-15, TILE_SIZE//2-10, 30, 20))
        # White dots
        pygame.draw.circle(surf, WHITE, (TILE_SIZE//2-7, TILE_SIZE//2-3), 3)
        pygame.draw.circle(surf, WHITE, (TILE_SIZE//2+5, TILE_SIZE//2-5), 3)
        return surf
    
    def create_bush_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Bush
        pygame.draw.circle(surf, (0, 100, 0), (TILE_SIZE//2-8, TILE_SIZE//2+5), 10)
        pygame.draw.circle(surf, (0, 100, 0), (TILE_SIZE//2+8, TILE_SIZE//2+5), 10)
        pygame.draw.circle(surf, (0, 128, 0), (TILE_SIZE//2, TILE_SIZE//2), 12)
        return surf
    
    def create_crate_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Crate
        pygame.draw.rect(surf, (139, 69, 19), (TILE_SIZE//2-15, TILE_SIZE//2-12, 30, 30))
        pygame.draw.rect(surf, (101, 67, 33), (TILE_SIZE//2-15, TILE_SIZE//2-12, 30, 30), 2)
        # Wood planks
        pygame.draw.line(surf, (101, 67, 33), (TILE_SIZE//2-15, TILE_SIZE//2+3), (TILE_SIZE//2+15, TILE_SIZE//2+3), 2)
        pygame.draw.line(surf, (101, 67, 33), (TILE_SIZE//2, TILE_SIZE//2-12), (TILE_SIZE//2, TILE_SIZE//2+18), 2)
        return surf
    
    def create_sign_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Sign post
        pygame.draw.rect(surf, (101, 67, 33), (TILE_SIZE//2-2, TILE_SIZE//2, 4, 15))
        # Sign board
        pygame.draw.rect(surf, (139, 69, 19), (TILE_SIZE//2-12, TILE_SIZE//2-10, 24, 12))
        pygame.draw.rect(surf, (101, 67, 33), (TILE_SIZE//2-12, TILE_SIZE//2-10, 24, 12), 2)
        return surf
    
    def create_stone_block_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((107, 114, 128))
        # Stone blocks
        pygame.draw.rect(surf, (75, 85, 99), (0, 0, TILE_SIZE//2, TILE_SIZE//2), 2)
        pygame.draw.rect(surf, (75, 85, 99), (TILE_SIZE//2, 0, TILE_SIZE//2, TILE_SIZE//2), 2)
        pygame.draw.rect(surf, (75, 85, 99), (0, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//2), 2)
        pygame.draw.rect(surf, (75, 85, 99), (TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//2), 2)
        return surf
    
    def create_tree_pine_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((34, 197, 94))
        # Pine tree trunk
        pygame.draw.rect(surf, (101, 67, 33), (TILE_SIZE//2-4, TILE_SIZE//2+5, 8, 15))
        # Pine tree triangles
        points1 = [(TILE_SIZE//2, TILE_SIZE//2-15), (TILE_SIZE//2-15, TILE_SIZE//2),
                   (TILE_SIZE//2+15, TILE_SIZE//2)]
        points2 = [(TILE_SIZE//2, TILE_SIZE//2-5), (TILE_SIZE//2-12, TILE_SIZE//2+8),
                   (TILE_SIZE//2+12, TILE_SIZE//2+8)]
        pygame.draw.polygon(surf, (0, 100, 0), points1)
        pygame.draw.polygon(surf, (0, 128, 0), points2)
        return surf
    
    def create_mushroom_tree_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((34, 197, 94))
        # Mushroom tree trunk
        pygame.draw.rect(surf, (245, 245, 220), (TILE_SIZE//2-6, TILE_SIZE//2, 12, 20))
        # Large mushroom cap
        pygame.draw.ellipse(surf, (147, 51, 234), (TILE_SIZE//2-20, TILE_SIZE//2-15, 40, 25))
        pygame.draw.circle(surf, (186, 85, 211), (TILE_SIZE//2-10, TILE_SIZE//2-5), 4)
        pygame.draw.circle(surf, (186, 85, 211), (TILE_SIZE//2+8, TILE_SIZE//2-7), 4)
        return surf
    
    def create_lily_pad_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((59, 130, 246))
        # Lily pad
        pygame.draw.ellipse(surf, (0, 128, 0), (TILE_SIZE//2-15, TILE_SIZE//2-10, 30, 20))
        pygame.draw.circle(surf, (255, 192, 203), (TILE_SIZE//2, TILE_SIZE//2), 5)
        return surf
    
    def create_vine_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 197, 94))
        # Vine
        for i in range(0, TILE_SIZE, 8):
            pygame.draw.circle(surf, (0, 128, 0), (TILE_SIZE//2 + random.randint(-3, 3), i), 4)
        return surf
    
    def create_dark_stone_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((55, 65, 81))
        pygame.draw.rect(surf, (31, 41, 55), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        return surf
    
    def create_coral_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((59, 130, 246))
        # Coral branches
        pygame.draw.line(surf, (255, 127, 80), (TILE_SIZE//2, TILE_SIZE-5), (TILE_SIZE//2, TILE_SIZE//2), 3)
        pygame.draw.line(surf, (255, 127, 80), (TILE_SIZE//2, TILE_SIZE//2+5), (TILE_SIZE//2-8, TILE_SIZE//2-5), 2)
        pygame.draw.line(surf, (255, 127, 80), (TILE_SIZE//2, TILE_SIZE//2+5), (TILE_SIZE//2+8, TILE_SIZE//2-5), 2)
        pygame.draw.circle(surf, (255, 99, 71), (TILE_SIZE//2-8, TILE_SIZE//2-5), 3)
        pygame.draw.circle(surf, (255, 99, 71), (TILE_SIZE//2+8, TILE_SIZE//2-5), 3)
        return surf
    
    def create_mushroom_block_tile(self):
        # Create a surface with per-pixel alpha for transparency
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base color with subtle variation
        base_hue = random.randint(-5, 5)  # Small hue variation
        base_color = (
            min(255, max(180, 200 + base_hue)),
            min(255, max(30, 30 + base_hue//2)),
            min(255, max(30, 30 + base_hue//3))
        )
        
        # Draw the main block with rounded corners
        pygame.draw.rect(surf, base_color, (1, 1, TILE_SIZE-2, TILE_SIZE-2), 
                        border_radius=3)
        
        # Create a pattern that will connect with adjacent mushroom blocks
        # Draw connecting edges that will align with neighboring blocks
        edge_width = 2
        edge_color = (base_color[0] + 20, base_color[1] + 10, base_color[2] + 10)
        
        # Top edge (connects with block above)
        pygame.draw.rect(surf, edge_color, (edge_width, 0, TILE_SIZE-2*edge_width, edge_width))
        # Bottom edge (connects with block below)
        pygame.draw.rect(surf, edge_color, (edge_width, TILE_SIZE-edge_width, TILE_SIZE-2*edge_width, edge_width))
        # Left edge (connects with block to the left)
        pygame.draw.rect(surf, edge_color, (0, edge_width, edge_width, TILE_SIZE-2*edge_width))
        # Right edge (connects with block to the right)
        pygame.draw.rect(surf, edge_color, (TILE_SIZE-edge_width, edge_width, edge_width, TILE_SIZE-2*edge_width))
        
        # Add a consistent texture pattern that tiles well
        # Create a grid of small circles for texture
        grid_size = 4  # Number of cells in the grid
        cell_size = TILE_SIZE // grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                # Calculate center of each grid cell
                x = i * cell_size + cell_size // 2
                y = j * cell_size + cell_size // 2
                
                # Create a consistent shade based on grid position
                shade = ((i * 7 + j * 13) % 30) - 15  # Pseudo-random but consistent
                color = (
                    min(255, max(180, base_color[0] + shade)),
                    min(255, max(30, base_color[1] + shade//2)),
                    min(255, max(30, base_color[2] + shade//3))
                )
                # Draw a subtle circle in each grid cell
                pygame.draw.circle(surf, color, (x, y), 1)
        
        # Define consistent spot positions using a fixed pattern
        spot_radius = 2
        spot_positions = [
            # Center of each quadrant
            (TILE_SIZE//4, TILE_SIZE//4, spot_radius),
            (3*TILE_SIZE//4, TILE_SIZE//4, spot_radius),
            (TILE_SIZE//4, 3*TILE_SIZE//4, spot_radius),
            (3*TILE_SIZE//4, 3*TILE_SIZE//4, spot_radius),
            # Center
            (TILE_SIZE//2, TILE_SIZE//2, spot_radius+1),
            # Edge centers (for better tiling)
            (TILE_SIZE//2, TILE_SIZE//4, spot_radius-1),
            (TILE_SIZE//2, 3*TILE_SIZE//4, spot_radius-1),
            (TILE_SIZE//4, TILE_SIZE//2, spot_radius-1),
            (3*TILE_SIZE//4, TILE_SIZE//2, spot_radius-1)
        ]
        
        for x, y, size in spot_positions:
            # Add a subtle glow behind the white spots
            glow = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, 80), (size*1.5, size*1.5), size*1.5)
            surf.blit(glow, (x - size*1.5, y - size*1.5), special_flags=pygame.BLEND_ALPHA_SDL2)
            # Draw the actual spot
            pygame.draw.circle(surf, (255, 255, 255), (x, y), size)
        
        # Add a subtle inner border that will connect with adjacent blocks
        border_color = (255, 220, 220, 120)
        pygame.draw.rect(surf, border_color, (1, 1, TILE_SIZE-2, TILE_SIZE-2), 
                        1, border_radius=3)
        
        return surf
    
    def create_snowman_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/SnowMan.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Simple snowman
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Body
        pygame.draw.circle(surf, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE-15), 15)
        pygame.draw.circle(surf, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE-35), 12)
        pygame.draw.circle(surf, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE-55), 10)
        # Eyes and buttons
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2-3, TILE_SIZE-57), 2)
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2+3, TILE_SIZE-57), 2)
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2, TILE_SIZE-48), 2)
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2, TILE_SIZE-28), 2)
        return surf
        
    def create_igloo_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/Igloo.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Simple igloo
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Igloo dome
        pygame.draw.arc(surf, (200, 230, 255), 
                       (TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//2), 
                       3.14, 0, 3)
        # Door
        pygame.draw.rect(surf, (100, 150, 200), 
                        (TILE_SIZE//2-5, TILE_SIZE-20, 10, 15))
        return surf
        
    def create_ice_box_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/IceBox.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Simple ice box
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 240, 255), 
                        (TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//3))
        pygame.draw.rect(surf, (150, 200, 255), 
                        (TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//3), 1)
        return surf
        
    def create_snow_tree_1_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/Tree_1.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Snowy tree 1
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Trunk
        pygame.draw.rect(surf, (139, 69, 19), 
                        (TILE_SIZE//2-3, TILE_SIZE-20, 6, 20))
        # Top
        pygame.draw.polygon(surf, (200, 230, 255), 
                          [(TILE_SIZE//2, 10), (10, TILE_SIZE-15), 
                           (TILE_SIZE-10, TILE_SIZE-15)])
        return surf
        
    def create_snow_tree_2_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/Tree_2.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Snowy tree 2
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Trunk
        pygame.draw.rect(surf, (101, 67, 33), 
                        (TILE_SIZE//2-4, TILE_SIZE-25, 8, 25))
        # Layers
        pygame.draw.polygon(surf, (200, 230, 255), 
                          [(TILE_SIZE//2, 15), (15, TILE_SIZE-20), 
                           (TILE_SIZE-15, TILE_SIZE-20)])
        pygame.draw.polygon(surf, (200, 230, 255), 
                          [(TILE_SIZE//2, 5), (20, TILE_SIZE-30), 
                           (TILE_SIZE-20, TILE_SIZE-30)])
        return surf
        
    def create_snowman_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/SnowMan.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Simple snowman
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Body
        pygame.draw.circle(surf, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE-15), 15)
        pygame.draw.circle(surf, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE-35), 12)
        pygame.draw.circle(surf, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE-55), 10)
        # Eyes and buttons
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2-3, TILE_SIZE-57), 2)
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2+3, TILE_SIZE-57), 2)
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2, TILE_SIZE-48), 2)
        pygame.draw.circle(surf, (0, 0, 0), (TILE_SIZE//2, TILE_SIZE-28), 2)
        return surf

    def create_igloo_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/Igloo.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Simple igloo
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Igloo dome
        pygame.draw.arc(surf, (200, 230, 255),
                      (TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//2),
                      3.14, 0, 3)
        # Door
        pygame.draw.rect(surf, (100, 150, 200),
                       (TILE_SIZE//2-5, TILE_SIZE-20, 10, 15))
        return surf

    def create_ice_box_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/IceBox.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Simple ice box
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Box
        pygame.draw.rect(surf, (200, 230, 255), (TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//3))
        pygame.draw.rect(surf, (150, 200, 255), (TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//3), 2)
        # Lid
        pygame.draw.rect(surf, (180, 220, 255), (TILE_SIZE//4-5, TILE_SIZE//2-5, TILE_SIZE//2+10, 5))
        return surf

    def create_snow_tree_1_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/Tree_1.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Snowy tree 1
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Trunk
        pygame.draw.rect(surf, (139, 69, 19), (TILE_SIZE//2-4, TILE_SIZE-20, 8, 20))
        # Snowy foliage
        pygame.draw.polygon(surf, (200, 230, 255), [
            (TILE_SIZE//2, TILE_SIZE-60),
            (TILE_SIZE//2-20, TILE_SIZE-20),
            (TILE_SIZE//2+20, TILE_SIZE-20)
        ])
        return surf

    def create_snow_tree_2_tile(self):
        path = 'assets/sprites/tiles/snow ice biome/Tree_2.png'
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Snowy tree 2
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Trunk
        pygame.draw.rect(surf, (139, 69, 19), (TILE_SIZE//2-3, TILE_SIZE-25, 6, 25))
        # Snowy foliage layers
        pygame.draw.circle(surf, (220, 240, 255), (TILE_SIZE//2, TILE_SIZE-30), 15)
        pygame.draw.circle(surf, (220, 240, 255), (TILE_SIZE//2, TILE_SIZE-45), 12)
        pygame.draw.circle(surf, (220, 240, 255), (TILE_SIZE//2, TILE_SIZE-60), 10)
        return surf
        
    def create_mushroom_tree_1_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Tree_1.png'
        if os.path.exists(path):
            image = load_image(path, scale=TILE_SIZE/64, required=True)
            if image:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                x = (TILE_SIZE - image.get_width()) // 2
                y = TILE_SIZE - image.get_height()
                surf.blit(image, (x, y))
                return surf
        return self.create_tree_tile()
        
    def create_mushroom_tree_2_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Tree_2.png'
        if os.path.exists(path):
            # Load the image with proper scaling
            image = load_image(path, scale=TILE_SIZE/64, required=True)
            if image:
                # Create a new surface the size of a tile
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                # Position the image so it's centered in the tile
                x = (TILE_SIZE - image.get_width()) // 2
                y = TILE_SIZE - image.get_height()  # Align to bottom of tile
                surf.blit(image, (x, y))
                return surf
        # Fallback to regular tree if loading fails
        return self.create_tree_tile()
        
    def create_mushroom_tree_3_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Tree_3.png'
        if os.path.exists(path):
            image = load_image(path, scale=TILE_SIZE/64, required=True)
            if image:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                x = (TILE_SIZE - image.get_width()) // 2
                y = TILE_SIZE - image.get_height()
                surf.blit(image, (x, y))
                return surf
        return self.create_tree_tile()
        
    def create_mushroom_1_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Mushroom_1.png'
        if os.path.exists(path):
            # Load at a smaller scale and position naturally
            image = load_image(path, scale=TILE_SIZE/48, required=True)  # Smaller scale
            if image:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                # Position randomly within the bottom half of the tile for natural look
                x = random.randint(TILE_SIZE//4, TILE_SIZE//2)
                y = TILE_SIZE - image.get_height() - random.randint(0, TILE_SIZE//4)
                # Add slight rotation for natural variation
                angle = random.uniform(-5, 5)
                if angle != 0:
                    image = pygame.transform.rotate(image, angle)
                surf.blit(image, (x, y))
                return surf
        # Fallback to a simple red mushroom
        return self.create_mushroom_red_tile()
        
    def create_mushroom_2_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Mushroom_2.png'
        if os.path.exists(path):
            # Load at a smaller scale and position naturally
            image = load_image(path, scale=TILE_SIZE/48, required=True)  # Smaller scale
            if image:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                # Position randomly within the bottom half of the tile for natural look
                x = random.randint(TILE_SIZE//4, TILE_SIZE//2)
                y = TILE_SIZE - image.get_height() - random.randint(0, TILE_SIZE//4)
                # Add slight rotation for natural variation
                angle = random.uniform(-5, 5)
                if angle != 0:
                    image = pygame.transform.rotate(image, angle)
                surf.blit(image, (x, y))
                return surf
        # Fallback to a simple blue mushroom
        return self.create_mushroom_blue_tile()
        
    def create_mushroom_bush_1_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Bush_1.png'
        if os.path.exists(path):
            # Load at a smaller scale for more natural look
            image = load_image(path, scale=TILE_SIZE/40, required=True)
            if image:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                # Position randomly within the bottom half of the tile
                x = random.randint(0, TILE_SIZE - image.get_width())
                y = TILE_SIZE - image.get_height() - random.randint(0, TILE_SIZE//8)
                surf.blit(image, (x, y))
                return surf
        return self.create_bush_tile()
        
    def create_mushroom_bush_2_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Bush_2.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        
        
    def create_mushroom_bush_3_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Bush_3.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        
    def create_mushroom_bush_4_tile(self):
        path = 'assets/sprites/tiles/mushroom_forest/Bush_4.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        
    # Factory biome tile creation methods
    def create_factory_floor_tile(self):
        path = 'assets/sprites/tiles/factory/box.png'  # Using box as floor texture
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=False)
        # Fallback: Metal floor
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((180, 180, 190))
        pygame.draw.rect(surf, (160, 160, 170), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        return surf
        
    def create_factory_wall_tile(self):
        path = 'assets/sprites/tiles/factory/box2.png'  # Using box2 as wall texture
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=False)
        # Fallback: Metal wall
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((150, 150, 160))
        pygame.draw.rect(surf, (130, 130, 140), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        return surf
        
    def create_factory_pipe_tile(self):
        path = 'assets/sprites/tiles/factory/vox5.png'  # Using vox5 as pipe texture
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=False)
        # Fallback: Pipe
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 110), (TILE_SIZE//2-5, 0, 10, TILE_SIZE))
        return surf
        
    def create_factory_gear_tile(self):
        # Fallback: Gear
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surf, (150, 150, 160), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2-2)
        pygame.draw.circle(surf, (180, 180, 190), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//4)
        # Gear teeth
        for i in range(8):
            angle = i * (2 * 3.14159 / 8)
            x = TILE_SIZE//2 + int(math.cos(angle) * (TILE_SIZE//2-4))
            y = TILE_SIZE//2 + int(math.sin(angle) * (TILE_SIZE//2-4))
            pygame.draw.rect(surf, (150, 150, 160), (x-3, y-3, 6, 6))
        return surf
        
    def create_factory_box_tile(self):
        path = 'assets/sprites/tiles/factory/box.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Crate
        return self.create_crate_tile()
        
    def create_factory_crate_tile(self):
        path = 'assets/sprites/tiles/factory/Box copy.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Crate
        return self.create_crate_tile()
        
    def create_factory_barrel_tile(self):
        path = 'assets/sprites/tiles/factory/Barrel (1).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Barrel
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (120, 80, 50), (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))
        pygame.draw.ellipse(surf, (80, 50, 30), (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2), 2)
        return surf
        
    def create_factory_acid_tile(self):
        path = 'assets/sprites/tiles/factory/Acid (2).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Acid
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 0, 150), (0, 0, TILE_SIZE, TILE_SIZE))
        return surf
        
    def create_factory_saw_tile(self):
        path = 'assets/sprites/tiles/factory/Saw.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Saw
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surf, (150, 150, 150), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2-2)
        pygame.draw.circle(surf, (200, 200, 200), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//4)
        return surf
        
    def create_factory_switch_tile(self):
        path = 'assets/sprites/tiles/factory/Switch (1).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Switch
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 100), (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))
        pygame.draw.rect(surf, (200, 0, 0), (TILE_SIZE//3, TILE_SIZE//3, TILE_SIZE//3, TILE_SIZE//3))
        return surf
        
    def create_factory_door_open_tile(self):
        path = 'assets/sprites/tiles/factory/DoorOpen.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Open door
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (120, 80, 50), (0, 0, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surf, (100, 60, 30), (TILE_SIZE//4, 0, TILE_SIZE//2, TILE_SIZE))
        return surf
        
    def create_factory_door_closed_tile(self):
        path = 'assets/sprites/tiles/factory/DoorLocked.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/64, required=True)
        # Fallback: Closed door
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 60, 30), (0, 0, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surf, (80, 40, 10), (TILE_SIZE//4, 0, TILE_SIZE//2, TILE_SIZE))
        return surf
        
    # Dessert biome tile creation methods
    def create_dessert_sand_tile(self):
        path = 'assets/sprites/tiles/dessert/Stone.png'  # Using stone as sand texture
        if os.path.exists(path):
            img = load_image(path, scale=TILE_SIZE/64, required=False)
            if img:
                return img
        # Fallback: Sand - using a light sandy beige color
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        # A more desert-like sand color (light beige)
        surf.fill((244, 222, 179))  # This is a sandy beige color
        
        # Add some subtle noise to make it look more natural
        for _ in range(10):
            x = random.randint(0, TILE_SIZE-1)
            y = random.randint(0, TILE_SIZE-1)
            brightness = random.randint(-10, 10)
            r = min(255, max(200, 244 + brightness))
            g = min(235, max(200, 222 + brightness))
            b = min(200, max(150, 179 + brightness))
            surf.set_at((x, y), (r, g, b))
            
        return surf
        
    def create_dessert_grass_1_tile(self):
        path = 'assets/sprites/tiles/dessert/Grass (1).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Grass 1
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((200, 200, 100))
        return surf
        
    def create_dessert_grass_2_tile(self):
        path = 'assets/sprites/tiles/dessert/Grass (2).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Grass 2
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((190, 190, 90))
        return surf
        
    def create_dessert_bush_1_tile(self):
        path = 'assets/sprites/tiles/dessert/Bush (1).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Bush 1
        return self.create_bush_tile()
        
    def create_dessert_bush_2_tile(self):
        path = 'assets/sprites/tiles/dessert/Bush (2).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Bush 2
        return self.create_bush_tile()
        
    def create_dessert_tree_tile(self):
        path = 'assets/sprites/tiles/dessert/Tree.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Tree
        return self.create_tree_tile()
        
    def create_dessert_cactus_1_tile(self):
        path = 'assets/sprites/tiles/dessert/Cactus (1).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Cactus 1
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 150, 0), (TILE_SIZE//2-2, TILE_SIZE-20, 4, 20))
        pygame.draw.rect(surf, (0, 100, 0), (TILE_SIZE//2-2, TILE_SIZE-20, 4, 20), 1)
        return surf
        
    def create_dessert_cactus_2_tile(self):
        path = 'assets/sprites/tiles/dessert/Cactus (2).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Cactus 2
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 160, 0), (TILE_SIZE//2-3, TILE_SIZE-25, 6, 25))
        pygame.draw.rect(surf, (0, 120, 0), (TILE_SIZE//2-3, TILE_SIZE-25, 6, 25), 1)
        return surf
        
    def create_dessert_cactus_3_tile(self):
        path = 'assets/sprites/tiles/dessert/Cactus (3).png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Cactus 3
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 140, 0), (TILE_SIZE//2-4, TILE_SIZE-30, 8, 30))
        pygame.draw.rect(surf, (0, 100, 0), (TILE_SIZE//2-4, TILE_SIZE-30, 8, 30), 1)
        return surf
        
    def create_dessert_rock_tile(self):
        path = 'assets/sprites/tiles/dessert/StoneBlock.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Rock
        return self.create_stone_tile()
        
    def create_dessert_skeleton_tile(self):
        path = 'assets/sprites/tiles/dessert/Skeleton.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Skeleton
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Simple skeleton shape
        pygame.draw.circle(surf, (220, 220, 220), (TILE_SIZE//2, TILE_SIZE//3), 5)  # Head
        pygame.draw.line(surf, (220, 220, 220), (TILE_SIZE//2, TILE_SIZE//3+5), (TILE_SIZE//2, TILE_SIZE*2//3), 2)  # Body
        pygame.draw.line(surf, (220, 220, 220), (TILE_SIZE//2-10, TILE_SIZE//2), (TILE_SIZE//2+10, TILE_SIZE//2), 2)  # Arms
        pygame.draw.line(surf, (220, 220, 220), (TILE_SIZE//2, TILE_SIZE*2//3), (TILE_SIZE//2-8, TILE_SIZE-10), 2)  # Leg 1
        pygame.draw.line(surf, (220, 220, 220), (TILE_SIZE//2, TILE_SIZE*2//3), (TILE_SIZE//2+8, TILE_SIZE-10), 2)  # Leg 2
        return surf
        
    def create_dessert_sign_tile(self):
        path = 'assets/sprites/tiles/dessert/Sign.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Sign
        return self.create_sign_tile()
        
    def create_dessert_sign_arrow_tile(self):
        path = 'assets/sprites/tiles/dessert/SignArrow.png'
        if os.path.exists(path):
            return load_image(path, scale=TILE_SIZE/32, required=True)
        # Fallback: Sign with arrow
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Post
        pygame.draw.rect(surf, (139, 69, 19), (TILE_SIZE//2-2, TILE_SIZE-10, 4, 10))
        # Sign
        pygame.draw.rect(surf, (200, 150, 100), (TILE_SIZE//2-10, TILE_SIZE-25, 20, 15))
        pygame.draw.rect(surf, (150, 100, 50), (TILE_SIZE//2-10, TILE_SIZE-25, 20, 15), 1)
        # Arrow
        pygame.draw.polygon(surf, (255, 0, 0), [
            (TILE_SIZE//2-5, TILE_SIZE-15),
            (TILE_SIZE//2+5, TILE_SIZE-15),
            (TILE_SIZE//2, TILE_SIZE-5)
        ])
        return surf
        
    def get_tile_image(self, tile_type, variant=0):
        """Get a tile image with fallback."""
        if tile_type is None:
            return create_error_surface("NONE", TILE_SIZE)
        
        if tile_type in self.sprites:
            tile = self.sprites[tile_type]
            if isinstance(tile, list) and tile:
                return tile[variant % len(tile)]
            return tile
        
        return create_error_surface(f"{tile_type.name}", TILE_SIZE)

# Initialize sprites
player_animations = PlayerAnimations()
npc_sprites = NPCSprites()
tile_sprites = TileSprites()

# Biome Definitions
BIOMES = {
    'GRASSLAND': {'name': 'Grassland', 'color': (34, 197, 94), 'icon': '🌱', 'bg': (100, 150, 255)},
    'DESERT':    {'name': 'Desert',    'color': (245, 158, 11), 'icon': '🏜️', 'bg': (255, 200, 100)},
    'SNOW':      {'name': 'Tundra',    'color': (147, 197, 253), 'icon': '❄️', 'bg': (200, 230, 255)},
    'FOREST':    {'name': 'Forest',    'color': (22, 163, 74), 'icon': '🌲', 'bg': (50, 150, 50)},
    'LAVA':      {'name': 'Volcanic',  'color': (234, 88, 12), 'icon': '🌋', 'bg': (180, 50, 50)},
    'OCEAN':     {'name': 'Ocean',     'color': (59, 130, 246), 'icon': '🌊', 'bg': (50, 100, 200)},
    'SWAMP':     {'name': 'Swamp',     'color': (101, 163, 13), 'icon': '🐸', 'bg': (80, 120, 80)},
    'MOUNTAIN':  {'name': 'Mountain',  'color': (107, 114, 128), 'icon': '⛰️', 'bg': (100, 100, 100)},
    'JUNGLE':    {'name': 'Jungle',    'color': (21, 128, 61), 'icon': '🦜', 'bg': (30, 100, 30)},
    'MUSHROOM':  {'name': 'Mushroom',  'color': (168, 85, 247), 'icon': '🍄', 'bg': (150, 50, 150)},
    'CRYSTAL':   {'name': 'Crystal Cave','color': (139, 92, 246), 'icon': '💎', 'bg': (80, 50, 120)},
    'WASTELAND': {'name': 'Wasteland', 'color': (120, 113, 108), 'icon': '💀', 'bg': (90, 80, 70)}
}

# Game State
class Game:
    def __init__(self):
        # Player state
        self.player_x = 0
        self.player_y = 0
        self.coins = 50
        self.health = 3
        self.max_health = 3
        self.energy = 100
        self.max_energy = 100
        self.score = 0
        self.has_key = False
        
        # Game state
        self.current_dimension = 'overworld'
        self.biomes_discovered = ['GRASSLAND']
        self.npcs_met = set()
        self.messages = []
        self.show_map = False
        self.show_inventory = False
        self.active_npc = None
        self.dialogue_index = 0
        self.anim_frame = 0
        self.world_cache = {}
        self.npc_cache = {}
        self.game_time = 0
        
        # Inventory system
        self.inventory = Inventory(capacity=24)  # 6x4 grid
        self.hotbar_size = 8
        self.hotbar_slot = 0
        
        # Initialize with some starting items
        self.inventory.add_item(ItemType.WOOD, 10)
        self.inventory.add_item(ItemType.STONE, 5)
        self.inventory.add_item(ItemType.APPLE, 3)

    def add_message(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 5:
            self.messages.pop(0)

    def seeded_random(self, x, y, seed=0):
        n = math.sin(x * 12.9898 + y * 78.233 + seed) * 43758.5453
        return n - math.floor(n)

    def get_biome(self, x, y):
        if self.current_dimension != 'overworld':
            if self.current_dimension == 'crystal_cave': return 'CRYSTAL'
            if self.current_dimension == 'nether': return 'LAVA'
            if self.current_dimension == 'mushroom': return 'MUSHROOM'

        bx = x // 30
        by = y // 30
        r = self.seeded_random(bx, by, 12345)
        if r < 0.10: return 'DESERT'
        if r < 0.20: return 'SNOW'
        if r < 0.35: return 'FOREST'
        if r < 0.40: return 'LAVA'
        if r < 0.50: return 'OCEAN'
        if r < 0.60: return 'SWAMP'
        if r < 0.70: return 'MOUNTAIN'
        if r < 0.80: return 'JUNGLE'
        if r < 0.85: return 'MUSHROOM'
        if r < 0.90: return 'WASTELAND'
        if abs(x) > 50 and abs(y) > 50 and abs(x) < 150 and abs(y) < 150 and self.seeded_random(x, y, 3) > 0.7:
            return 'MUSHROOM_FOREST'
        return 'GRASSLAND'

    def get_npc_type(self, x, y):
        r = self.seeded_random(x, y, 7777)
        npc_list = list(NPC_TYPES.keys())
        idx = int(r * len(npc_list))
        return npc_list[idx % len(npc_list)]
    
    def generate_tile(self, x, y, biome):
        r = self.seeded_random(x, y)
        
        # Use noise-like patterns for organic terrain
        noise1 = self.seeded_random(x // 3, y // 3, 111)
        noise2 = self.seeded_random(x // 5, y // 5, 222)
        noise3 = self.seeded_random(x // 2, y // 2, 333)
        if biome == 'GRASSLAND':
            # Water bodies with organic shapes
            if noise1 < 0.15 and noise2 < 0.4:
                return Tile.WATER
            # Tree clusters
            if noise1 > 0.7 and r < 0.4:
                return Tile.TREE
            if noise3 > 0.8 and r < 0.3:
                return Tile.FLOWER
            # Dirt paths - create more natural, connected paths
            # Use multiple noise layers to create winding paths
            path_noise1 = math.sin(x * 0.2) * math.cos(y * 0.2)
            path_noise2 = math.sin(x * 0.1) * math.cos(y * 0.15)
            path_noise3 = self.seeded_random(x // 2, y // 2, 123) * 0.3
            
            # Create main paths (more common near the center of the map)
            path_strength = 0.4 - (abs(x) + abs(y)) / 1000  # Paths are more common near center
            path_strength = max(0.1, min(0.6, path_strength))  # Clamp the value
            
            if (abs(path_noise1 + path_noise2 + path_noise3) < 0.2 + path_strength):
                # Add some randomness to make the path edges more natural
                if self.seeded_random(x, y, 456) < 0.9:
                    return Tile.DIRT
                # Occasionally add some grass or flowers near the path edges
                if self.seeded_random(x, y, 789) < 0.1:
                    return Tile.FLOWER if self.seeded_random(x, y, 101) < 0.3 else Tile.GRASS
            if r < 0.005: return Tile.TREASURE
            if r < 0.008: return Tile.QUESTION_BLOCK
            if r < 0.010: return Tile.PORTAL
            if r < 0.011: return Tile.KEY_ITEM
            return Tile.GRASS
        elif biome == 'FOREST':
            # Create winding paths using noise functions
            path_noise = (math.sin(x * 0.15) + math.cos(y * 0.15) + 
                         math.sin(x * 0.05 + y * 0.03) * 0.5) / 2.5
            
            # Create mushroom patches that follow the paths
            mushroom_noise = (math.sin(x * 0.1) * math.cos(y * 0.12) + 
                            math.sin(x * 0.2) * 0.5 + 
                            math.cos(y * 0.2) * 0.5) / 2
            
            # Main path - dirt with mushroom edges
            path_width = 0.2  # Width of the main path
            mushroom_zone = 0.1  # How far from path mushrooms can appear
            
            # Check if we're in a path area
            if abs(path_noise) < path_width:
                # Add some variation to the path edges
                if abs(path_noise) > path_width * 0.7 and self.seeded_random(x, y, 123) < 0.3:
                    return Tile.MUSHROOM_RED
                return Tile.DIRT
            # Mushroom zone near paths
            elif abs(path_noise) < path_width + mushroom_zone:
                if self.seeded_random(x, y, 456) < 0.7:  # 70% chance of mushroom in this zone
                    return Tile.MUSHROOM_RED
            
            # Regular forest generation outside paths
            if r < 0.20: return Tile.TREE
            if r < 0.35: return Tile.TREE_PINE
            if r < 0.45: return Tile.BUSH
            if r < 0.50: return Tile.FLOWER
            if r < 0.52: return Tile.TREASURE
            if r < 0.54: return Tile.PORTAL
            return Tile.GRASS
        elif biome == 'MOUNTAIN':
            if r < 0.40: return Tile.STONE
            if r < 0.50: return Tile.DARK_STONE
            if r < 0.51: return Tile.CRYSTAL
            if r < 0.53: return Tile.TREASURE
            if r < 0.55: return Tile.PORTAL
            return Tile.STONE_BLOCK
        elif biome in ['MUSHROOM', 'MUSHROOM_FOREST']:
            # Create a more vibrant and diverse mushroom forest
            
            # Use noise for more natural distribution
            noise_val = (math.sin(x * 0.2) * math.cos(y * 0.2) + 1) / 2  # 0-1 range
            
            # Special features (rarer items first)
            if r < 0.01: return Tile.TREASURE
            if r < 0.02: return Tile.CRYSTAL
            if r < 0.03: return Tile.PORTAL
            
            # Mushroom trees - more common near noise peaks
            if noise_val > 0.7:
                if r < 0.12: return Tile.MUSHROOM_TREE_1
                if r < 0.24: return Tile.MUSHROOM_TREE_2
                if r < 0.36: return Tile.MUSHROOM_TREE_3
            
            # Mushroom clusters - more common in certain areas
            if 0.3 < noise_val < 0.8:
                if r < 0.10: return Tile.MUSHROOM_1
                if r < 0.20: return Tile.MUSHROOM_2
                if r < 0.25: return Tile.MUSHROOM_RED
                if r < 0.30: return Tile.MUSHROOM_BLUE
            
            # Mushroom bushes - more common in certain areas
            if noise_val > 0.4:
                if r < 0.35: return Tile.MUSHROOM_BUSH_1
                if r < 0.40: return Tile.MUSHROOM_BUSH_2
                if r < 0.45: return Tile.MUSHROOM_BUSH_3
                if r < 0.50: return Tile.MUSHROOM_BUSH_4
            
            # Decorative elements
            if r < 0.55: return Tile.STONE_BLOCK
            if r < 0.60: return Tile.BUSH
            if r < 0.62: return Tile.CRATE
            if r < 0.64: return Tile.SIGN
            if r < 0.66: return Tile.STONE
            
            # Ground cover - use noise to create patches of different ground types
            if noise_val > 0.6:
                return Tile.MUSHROOM_BLOCK
            elif noise_val > 0.3:
                return Tile.DIRT if r < 0.7 else Tile.MUSHROOM_BLOCK
            else:
                return Tile.MUSHROOM_BLOCK if r < 0.6 else Tile.DIRT
        elif biome == 'SNOW':
            if r < 0.15: return Tile.SNOW_TREE_1
            if r < 0.30: return Tile.SNOW_TREE_2
            if r < 0.35: return Tile.SNOWMAN
            if r < 0.38: return Tile.IGLOO
            if r < 0.41: return Tile.ICE_BOX
            if r < 0.44: return Tile.CRATE
            if r < 0.46: return Tile.SIGN
            if r < 0.48: return Tile.ICE
            if r < 0.50: return Tile.TREASURE
            if r < 0.52: return Tile.PORTAL
            if r < 0.54: return Tile.CRYSTAL
            if r < 0.56: return Tile.STONE
            return Tile.SNOW
        elif biome == 'LAVA':
            if r < 0.30: return Tile.LAVA
            if r < 0.40: return Tile.OBSIDIAN
            if r < 0.45: return Tile.DARK_STONE
            if r < 0.47: return Tile.TREASURE
            if r < 0.48: return Tile.PORTAL
            if r < 0.50: return Tile.CRYSTAL
            return Tile.STONE
        elif biome == 'OCEAN':
            if r < 0.40: return Tile.WATER
            if r < 0.50: return Tile.CORAL
            if r < 0.55: return Tile.LILY_PAD
            if r < 0.57: return Tile.TREASURE
            if r < 0.58: return Tile.PORTAL
            if r < 0.60: return Tile.SAND
            return Tile.WATER
        elif biome == 'SWAMP':
            if r < 0.15: return Tile.VINE
            if r < 0.30: return Tile.LILY_PAD
            if r < 0.40: return Tile.MUSHROOM_BLUE
            if r < 0.50: return Tile.WATER
            if r < 0.52: return Tile.TREASURE
            if r < 0.54: return Tile.PORTAL
            if r < 0.59: return Tile.DIRT
            if r < 0.69: return Tile.GRASS
            return Tile.WATER
            
        elif biome == 'JUNGLE':
            if r < 0.20: return Tile.TREE
            if r < 0.35: return Tile.VINE
            if r < 0.45: return Tile.BUSH
            if r < 0.50: return Tile.FLOWER
            if r < 0.52: return Tile.TREASURE
            if r < 0.54: return Tile.PORTAL
            if r < 0.56: return Tile.CRYSTAL
            if r < 0.61: return Tile.GRASS
            return Tile.DIRT
            
        elif biome == 'WASTELAND':
            if r < 0.40: return Tile.DARK_STONE
            if r < 0.50: return Tile.STONE
            if r < 0.55: return Tile.OBSIDIAN
            if r < 0.57: return Tile.TREASURE
            if r < 0.59: return Tile.PORTAL
            if r < 0.61: return Tile.CRYSTAL
            if r < 0.71: return Tile.STONE_BLOCK
            return Tile.DIRT
        
        elif biome == 'FACTORY':
            # Factory biome with industrial elements
            if r < 0.10: return Tile.FACTORY_PIPE
            if r < 0.20: return Tile.FACTORY_GEAR
            if r < 0.30: return Tile.FACTORY_BOX
            if r < 0.35: return Tile.FACTORY_CRATE
            if r < 0.40: return Tile.FACTORY_BARREL
            if r < 0.45: return Tile.FACTORY_SAW
            if r < 0.50: return Tile.FACTORY_SWITCH
            if r < 0.55: return Tile.FACTORY_DOOR_OPEN
            if r < 0.56: return Tile.FACTORY_DOOR_CLOSED
            if r < 0.57: return Tile.TREASURE
            if r < 0.58: return Tile.PORTAL
            if r < 0.65: return Tile.FACTORY_WALL
            if r < 0.90: return Tile.FACTORY_FLOOR
            return Tile.FACTORY_ACID
            
        elif biome == 'DESSERT':
            # Dessert biome with sweet treats
            if r < 0.10: return Tile.DESSERT_GRASS_1
            if r < 0.20: return Tile.DESSERT_GRASS_2
            if r < 0.30: return Tile.DESSERT_BUSH_1
            if r < 0.40: return Tile.DESSERT_BUSH_2
            if r < 0.45: return Tile.DESSERT_TREE
            if r < 0.50: return Tile.DESSERT_CACTUS_1
            if r < 0.55: return Tile.DESSERT_CACTUS_2
            if r < 0.60: return Tile.DESSERT_CACTUS_3
            if r < 0.65: return Tile.DESSERT_ROCK
            if r < 0.70: return Tile.DESSERT_SKELETON
            if r < 0.75: return Tile.DESSERT_SIGN
            if r < 0.80: return Tile.DESSERT_SIGN_ARROW
            if r < 0.85: return Tile.TREASURE
            if r < 0.90: return Tile.PORTAL
            return Tile.DESSERT_SAND
            
        # Default fallback for any unhandled biomes
        return Tile.GRASS

    def get_tile(self, x, y):
        key = (x, y, self.current_dimension)
        if key not in self.world_cache:
            biome = self.get_biome(x, y)
            tile = self.generate_tile(x, y, biome)
            self.world_cache[key] = tile
        return self.world_cache[key]

    def set_tile(self, x, y, tile):
        key = (x, y, self.current_dimension)
        self.world_cache[key] = tile

    def get_npc(self, x, y):
        key = (x, y, self.current_dimension)
        if key not in self.npc_cache and self.get_tile(x, y) == Tile.NPC:
            npc_type = self.get_npc_type(x, y)
            self.npc_cache[key] = {**NPC_TYPES[npc_type], 'type': npc_type}
        return self.npc_cache.get(key)

    def use_item(self, item: Item) -> bool:
        """Use an item from the inventory. Returns True if the item was used."""
        if item.item_type == ItemType.HEALTH_POTION:
            if self.health < self.max_health:
                self.health = min(self.health + 2, self.max_health)
                self.add_message("Healed by health potion!")
                return True
            else:
                self.add_message("Health is already full!")
                return False
                
        elif item.item_type == ItemType.SPEED_POTION:
            # Implement speed boost effect
            self.add_message("Speed increased temporarily!")
            return True
            
        elif item.item_type == ItemType.APPLE:
            self.health = min(self.health + 1, self.max_health)
            self.energy = min(self.energy + 20, self.max_energy)
            self.add_message("Ate an apple. Yum!")
            return True
            
        elif item.item_type == ItemType.BREAD:
            self.health = min(self.health + 2, self.max_health)
            self.energy = min(self.energy + 40, self.max_energy)
            self.add_message("Ate some bread. Tasty!")
            return True
            
        # Add more item uses here...
        
        return False

    def mine_tile(self, x: int, y: int) -> bool:
        """Mine a tile and add its resources to inventory. Returns True if successful."""
        tile = self.get_tile(x, y)
        
        # Check if tile is mineable and player has the right tool
        if tile in [Tile.TREE, Tile.TREE_PINE]:
            # Check for axe in hotbar
            has_axe = any(item.item_type == ItemType.AXE 
                         for item in self.inventory.items[:self.hotbar_size] 
                         if item is not None)
            
            if not has_axe:
                self.add_message("You need an axe to chop trees!")
                return False
                
            self.inventory.add_item(ItemType.WOOD, 1)
            self.set_tile(x, y, Tile.GRASS)
            self.add_message("Chopped wood +1")
            return True
            
        elif tile in [Tile.STONE, Tile.IRON_ORE, Tile.GOLD_ORE, Tile.DIAMOND_ORE]:
            # Check for pickaxe in hotbar
            has_pickaxe = any(item.item_type == ItemType.PICKAXE 
                             for item in self.inventory.items[:self.hotbar_size] 
                             if item is not None)
            
            if not has_pickaxe:
                self.add_message("You need a pickaxe to mine stone!")
                return False
                
            if tile == Tile.STONE:
                self.inventory.add_item(ItemType.STONE, 1)
                self.add_message("Mined stone +1")
            elif tile == Tile.IRON_ORE:
                self.inventory.add_item(ItemType.IRON, 1)
                self.add_message("Mined iron ore +1")
            elif tile == Tile.GOLD_ORE:
                self.inventory.add_item(ItemType.GOLD, 1)
                self.add_message("Mined gold ore +1")
            elif tile == Tile.DIAMOND_ORE:
                self.inventory.add_item(ItemType.DIAMOND, 1)
                self.add_message("Mined diamond +1")
                
            self.set_tile(x, y, Tile.STONE)  # Turn to regular stone after mining
            return True
            
        return False

    def move_player(self, dx, dy):
        if self.active_npc:
            return False
            
        nx, ny = self.player_x + dx, self.player_y + dy
        tile = self.get_tile(nx, ny)
        biome = self.get_biome(nx, ny)
        
        # Update animation state based on movement
        is_moving = dx != 0 or dy != 0
        
        if is_moving:
            # Set walking animation
            player_animations.set_animation('walk')
            
            # Update facing direction
            if dx != 0:  # Only update facing if moving horizontally
                player_animations.facing_right = dx > 0
        else:
            # Only set to idle if not already in the middle of another animation
            if player_animations.current_animation_name in ['idle', 'walk', 'run']:
                player_animations.set_animation('idle')
                
        # Get movement speed based on terrain
        move_speed = 1
        if tile in [Tile.ICE, Tile.WATER]:
            move_speed = 0.7  # Slower movement on ice/water
        
        # Update animation speed based on movement speed
        if is_moving:
            player_animations.animation_config['walk']['speed'] = 0.1 * move_speed
            
        # Biome discovery
        if biome not in self.biomes_discovered:
            self.biomes_discovered.append(biome)
            self.add_message(f"Discovered {BIOMES[biome]['name']}!")
            self.score += 500

        # Portal handling
        if tile == Tile.PORTAL:
            r = self.seeded_random(nx, ny, 9999)
            if r < 0.33:
                self.current_dimension = 'crystal_cave'
                self.add_message("Entered Crystal Cave!")
            elif r < 0.66:
                self.current_dimension = 'nether'
                self.add_message("Entered The Nether!")
            else:
                self.current_dimension = 'mushroom'
                self.add_message("Entered Mushroom Realm!")
            self.player_x = self.player_y = 0
            self.score += 3000
            return False

        # NPC interaction
        if tile == Tile.NPC:
            npc = self.get_npc(nx, ny)
            if npc:
                npc_key = f"{npc['type']}-{nx}-{ny}"
                if npc_key not in self.npcs_met:
                    self.npcs_met.add(npc_key)
                    self.score += 150
                self.active_npc = npc['type']
                self.dialogue_index = 0
                player_animations.set_animation('idle')  # Reset to idle when talking to NPC
            return False

        # Handle walkable tiles
        if tile in WALKABLE:
            # Check if we're trying to collect an item
            if tile in TILE_TO_ITEM:
                item_type = TILE_TO_ITEM[tile]
                if self.inventory.add_item(item_type, 1):
                    self.add_message(f"Collected {item_type.name.replace('_', ' ').lower()}")
                    
                    # Remove the tile if it's a collectible
                    if tile in [Tile.FLOWER, Tile.MUSHROOM_RED, Tile.MUSHROOM_BLUE, 
                              Tile.TREASURE, Tile.CRYSTAL, Tile.KEY_ITEM]:
                        self.set_tile(nx, ny, Tile.GRASS)
            
            # Move the player
            self.player_x, self.player_y = nx, ny
            
            # Handle special tiles
            if tile == Tile.TREASURE:
                self.coins += 10
                self.score += 100
                self.set_tile(nx, ny, Tile.GRASS)
                self.add_message("+10 Coins!")
            elif tile == Tile.CRYSTAL:
                self.coins += 25
                self.score += 250
                self.set_tile(nx, ny, Tile.GRASS)
                self.add_message("+25 Coins!")
            elif tile == Tile.QUESTION_BLOCK:
                r = self.seeded_random(nx, ny, 777)
                if r < 0.5:
                    self.coins += 5
                    self.score += 50
                    self.add_message("+5 Coins!")
                else:
                    self.health = min(3, self.health + 1)
                    self.add_message("+1 Life!")
                self.set_tile(nx, ny, Tile.BRICK)
            elif tile == Tile.KEY_ITEM:
                self.has_key = True
                self.score += 200
                self.set_tile(nx, ny, Tile.GRASS)
                self.add_message("Got Key!")
                
            return True
                
        # Handle hazardous tiles
        elif tile in [Tile.WATER, Tile.LAVA]:
            self.health = max(0, self.health - 1)
            self.add_message("Burning!" if tile == Tile.LAVA else "Ouch!")
            return False
            
        return False

        if biome not in self.biomes_discovered:
            self.biomes_discovered.append(biome)
            self.add_message(f"Discovered {BIOMES[biome]['name']}!")
            self.score += 500

        if tile == Tile.PORTAL:
            r = self.seeded_random(nx, ny, 9999)
            if r < 0.33:
                self.current_dimension = 'crystal_cave'
                self.add_message("Entered Crystal Cave!")
            elif r < 0.66:
                self.current_dimension = 'nether'
                self.add_message("Entered The Nether!")
            else:
                self.current_dimension = 'mushroom'
                self.add_message("Entered Mushroom Realm!")
            self.player_x = self.player_y = 0
            self.score += 3000
            return

        if tile == Tile.NPC:
            npc = self.get_npc(nx, ny)
            if npc:
                npc_key = f"{npc['type']}-{nx}-{ny}"
                if npc_key not in self.npcs_met:
                    self.npcs_met.add(npc_key)
                    self.score += 150
                self.active_npc = npc['type']
                self.dialogue_index = 0
            return

        if tile in WALKABLE:
            self.player_x, self.player_y = nx, ny
            
            if tile == Tile.TREASURE:
                self.coins += 10
                self.score += 100
                self.set_tile(nx, ny, Tile.GRASS)
                self.add_message("+10 Coins!")
            elif tile == Tile.CRYSTAL:
                self.coins += 25
                self.score += 250
                self.set_tile(nx, ny, Tile.GRASS)
                self.add_message("+25 Coins!")
            elif tile == Tile.QUESTION_BLOCK:
                r = self.seeded_random(nx, ny, 777)
                if r < 0.5:
                    self.coins += 5
                    self.score += 50
                    self.add_message("+5 Coins!")
                else:
                    self.health = min(3, self.health + 1)
                    self.add_message("+1 Life!")
                self.set_tile(nx, ny, Tile.BRICK)
            elif tile == Tile.KEY_ITEM:
                self.has_key = True
                self.score += 200
                self.set_tile(nx, ny, Tile.GRASS)
                self.add_message("Got Key!")
                
        elif tile in [Tile.WATER, Tile.LAVA]:
            self.health = max(0, self.health - 1)
            self.add_message("Burning!" if tile == Tile.LAVA else "Ouch!")

    def draw_tile(self, surface, tile, screen_x, screen_y, is_player):
        rect = pygame.Rect(screen_x * TILE_SIZE, screen_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        
        if is_player:
            player_frame = player_animations.get_current_frame()
            if player_frame:
                scaled_frame = pygame.transform.scale(player_frame, (TILE_SIZE, TILE_SIZE))
                if not player_animations.facing_right:
                    scaled_frame = pygame.transform.flip(scaled_frame, True, False)
                surface.blit(scaled_frame, rect)
            else:
                pygame.draw.rect(surface, (220, 50, 50), rect)
            return

        if tile == Tile.NPC:
            world_x = self.player_x - (VIEWPORT_WIDTH // 2) + screen_x
            world_y = self.player_y - (VIEWPORT_HEIGHT // 2) + screen_y
            npc = self.get_npc(world_x, world_y)
            if npc:
                # Draw grass background
                pygame.draw.rect(surface, (34, 197, 94), rect)
                # Try to get NPC sprite
                npc_sprite = npc_sprites.get(npc['type'])
                if npc_sprite and npc_sprite != npc_sprites.placeholder:
                    # Scale sprite to fit the tile while maintaining aspect ratio
                    sprite_rect = npc_sprite.get_rect()
                    scale = min(rect.width / sprite_rect.width, rect.height / sprite_rect.height) * 0.9
                    new_size = (int(sprite_rect.width * scale), int(sprite_rect.height * scale))
                    scaled_sprite = pygame.transform.scale(npc_sprite, new_size)
                    sprite_rect = scaled_sprite.get_rect(center=rect.center)
                    surface.blit(scaled_sprite, sprite_rect)
                else:
                    # Fallback to icon if no sprite is loaded
                    icon_surf = font.render(npc['icon'], True, WHITE)
                    icon_rect = icon_surf.get_rect(center=rect.center)
                    surface.blit(icon_surf, icon_rect)
            return

        # Get and draw tile
        tile_image = tile_sprites.get_tile_image(tile, screen_x + screen_y)
        if tile_image:
            surface.blit(tile_image, rect)

    def draw_npc_dialogue(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_rect = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 180)
        pygame.draw.rect(screen, (40, 40, 60), dialog_rect, border_radius=10)
        pygame.draw.rect(screen, (80, 80, 120), dialog_rect, 2, border_radius=10)

        # Get NPC data
        npc = NPC_TYPES.get(self.active_npc, {})
        
        # NPC name
        name_surf = font.render(npc.get('name', 'NPC'), True, npc.get('color', WHITE))
        screen.blit(name_surf, (dialog_rect.x + 20, dialog_rect.y + 20))
        
        # Dialogue
        dialogue = npc.get('dialogue', ["Hello!"])
        text = dialogue[self.dialogue_index % len(dialogue)]
        
        # Word wrap
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if small_font.size(test_line)[0] < dialog_rect.width - 40:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw dialogue lines
        for i, line in enumerate(lines):
            text_surf = small_font.render(line, True, (240, 240, 240))
            screen.blit(text_surf, (dialog_rect.x + 20, dialog_rect.y + 60 + i * 25))
        
        # Continue prompt
        prompt_surf = small_font.render('Press SPACE to continue... (ESC to close)', True, (200, 200, 200))
        prompt_rect = prompt_surf.get_rect(bottomright=(dialog_rect.right - 15, dialog_rect.bottom - 15))
        screen.blit(prompt_surf, prompt_rect)

    def draw_map(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(50, 100, SCREEN_WIDTH - 100, 400)
        pygame.draw.rect(screen, (30, 30, 30), box, border_radius=15)
        pygame.draw.rect(screen, (80, 80, 120), box, 2, border_radius=15)

        title = font.render(f"Discovered Biomes ({len(self.biomes_discovered)}/{len(BIOMES)})", True, WHITE)
        screen.blit(title, (box.x + 20, box.y + 20))

        y = box.y + 60
        col = 0
        for key, biome in BIOMES.items():
            x_pos = box.x + 20 + (col * 300)
            
            if key in self.biomes_discovered:
                color = biome['color']
                name = f"{biome['icon']} {biome['name']}"
            else:
                color = (100, 100, 100)
                name = f"??? ???"
            
            text_surf = small_font.render(name, True, color)
            screen.blit(text_surf, (x_pos, y))
            
            col += 1
            if col >= 2:
                col = 0
                y += 30

        # Instructions
        inst = small_font.render('Press M to close', True, (150, 150, 150))
        screen.blit(inst, (box.x + 20, box.bottom - 40))

    def draw_inventory(self):
        """Draw the inventory UI."""
        if not self.show_inventory:
            return
            
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Inventory panel
        panel_width = 600
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Draw panel background
        pygame.draw.rect(screen, (50, 50, 80), 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 140), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw title
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("INVENTORY", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, 
                                  top=panel_y + 20)
        screen.blit(title, title_rect)
        
        # Draw inventory grid (6x4)
        cell_size = 80
        cell_padding = 10
        grid_width = 6
        grid_height = 4
        
        start_x = panel_x + (panel_width - (grid_width * (cell_size + cell_padding) - cell_padding)) // 2
        start_y = panel_y + 80
        
        # Draw items
        for i, item in enumerate(self.inventory.items):
            row = i // grid_width
            col = i % grid_width
            x = start_x + col * (cell_size + cell_padding)
            y = start_y + row * (cell_size + cell_padding)
            
            # Draw item slot
            pygame.draw.rect(screen, (80, 80, 110), (x, y, cell_size, cell_size))
            pygame.draw.rect(screen, (120, 120, 150), (x, y, cell_size, cell_size), 2)
            
            # Draw item (placeholder - you'd add proper item sprites)
            item_text = FONT_SMALL.render(item.item_type.name[:3], True, (255, 255, 255))
            screen.blit(item_text, (x + 5, y + 5))
            
            # Draw quantity
            if item.quantity > 1:
                qty_text = FONT_SMALL.render(str(item.quantity), True, (255, 255, 255))
                screen.blit(qty_text, (x + cell_size - qty_text.get_width() - 5, 
                                     y + cell_size - qty_text.get_height() - 5))
        
        # Draw hotbar
        hotbar_y = start_y + (grid_height * (cell_size + cell_padding)) + 40
        hotbar_width = self.hotbar_size * (cell_size + cell_padding) - cell_padding
        hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
        
        pygame.draw.rect(screen, (70, 70, 100), 
                        (hotbar_x - 10, hotbar_y - 10, 
                         hotbar_width + 20, cell_size + 20))
        
        for i in range(self.hotbar_size):
            x = hotbar_x + i * (cell_size + cell_padding)
            
            # Draw slot
            color = (100, 100, 140) if i == self.hotbar_slot else (70, 70, 100)
            pygame.draw.rect(screen, color, (x, hotbar_y, cell_size, cell_size))
            pygame.draw.rect(screen, (120, 120, 150), (x, hotbar_y, cell_size, cell_size), 2)
            
            # Draw item if exists
            if i < len(self.inventory.items):
                item = self.inventory.items[i]
                item_text = FONT_SMALL.render(item.item_type.name[:3], True, (255, 255, 255))
                screen.blit(item_text, (x + 5, hotbar_y + 5))
                
                if item.quantity > 1:
                    qty_text = FONT_SMALL.render(str(item.quantity), True, (255, 255, 255))
                    screen.blit(qty_text, (x + cell_size - qty_text.get_width() - 5, 
                                         hotbar_y + cell_size - qty_text.get_height() - 5))
    
    def draw_hud(self):
        """Draw the heads-up display."""
        # Health
        for i in range(self.max_health):
            x = 20 + i * 30
            color = (255, 50, 50) if i < self.health else (80, 80, 80)
            pygame.draw.rect(screen, color, (x, 20, 25, 25))
        
        # Energy
        energy_width = 200
        energy_height = 10
        energy_fill = (energy_width * self.energy) // self.max_energy
        pygame.draw.rect(screen, (80, 80, 80), (20, 60, energy_width, energy_height))
        pygame.draw.rect(screen, (50, 150, 255), (20, 60, energy_fill, energy_height))
        
        # Coins
        coin_text = FONT_SMALL.render(f"Coins: {self.coins}", True, (255, 255, 0))
        screen.blit(coin_text, (20, 80))
        
        # Hotbar
        hotbar_width = self.hotbar_size * 40 + (self.hotbar_size - 1) * 5
        hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
        
        for i in range(self.hotbar_size):
            x = hotbar_x + i * 45
            color = (200, 200, 200) if i == self.hotbar_slot else (100, 100, 100)
            pygame.draw.rect(screen, color, (x, SCREEN_HEIGHT - 50, 40, 40), 2)
            
            if i < len(self.inventory.items):
                item = self.inventory.items[i]
                item_text = FONT_TINY.render(item.item_type.name[:3], True, (255, 255, 255))
                screen.blit(item_text, (x + 5, SCREEN_HEIGHT - 45))
    
    def draw(self):
        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw the game world
        for y in range(VIEWPORT_HEIGHT):
            for x in range(VIEWPORT_WIDTH):
                world_x = self.player_x - (VIEWPORT_WIDTH // 2) + x
                world_y = self.player_y - (VIEWPORT_HEIGHT // 2) + y
        
        viewport_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - 80))
        viewport_surface.fill(bg_color)

        # Draw tiles
        for row in range(VIEWPORT_HEIGHT):
            for col in range(VIEWPORT_WIDTH):
                wx = start_x + col
                wy = start_y + row
                tile = self.get_tile(wx, wy)
                is_player = (wx == self.player_x and wy == self.player_y)
                self.draw_tile(viewport_surface, tile, col, row, is_player)

        screen.blit(viewport_surface, (0, 80))
        
        # HUD
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 70), border_radius=0)
        
        score_surf = font.render(f"SCORE: {self.score:06d}", True, YELLOW)
        screen.blit(score_surf, (20, 10))
        
        coin_surf = font.render(f"💰 {self.coins}", True, YELLOW)
        screen.blit(coin_surf, (200, 10))
        
        npc_surf = font.render(f"👥 {len(self.npcs_met)}", True, GREEN)
        screen.blit(npc_surf, (320, 10))

        # Health hearts
        for i in range(3):
            color = RED if i < self.health else (60, 60, 60)
            pygame.draw.circle(screen, color, (470 + i*35, 25), 12)
            pygame.draw.circle(screen, color, (490 + i*35, 25), 12)
            points = [(480 + i*35, 35), (460 + i*35, 18), (480 + i*35, 15), (500 + i*35, 18)]
            pygame.draw.polygon(screen, color, points)

        if self.has_key:
            key_surf = font.render('🔑', True, YELLOW)
            screen.blit(key_surf, (600, 10))

        # Biome indicator
        biome_text = small_font.render(f"{BIOMES[current_biome]['icon']} {BIOMES[current_biome]['name']}", True, WHITE)
        screen.blit(biome_text, (20, 45))
        
        # Dimension indicator
        if self.current_dimension != 'overworld':
            dim_text = small_font.render(f"Press E to return", True, (255, 200, 0))
            screen.blit(dim_text, (SCREEN_WIDTH - 180, 45))

        # Messages
        if self.messages:
            msg_y = 90
            for msg in self.messages[-3:]:  # Show last 3 messages
                msg_surf = small_font.render(msg, True, WHITE)
                msg_rect = msg_surf.get_rect()
                bg_rect = msg_rect.inflate(20, 10)
                bg_rect.topleft = (10, msg_y)
                
                bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 180))
                screen.blit(bg_surface, bg_rect)
                screen.blit(msg_surf, (bg_rect.x + 10, bg_rect.y + 5))
                msg_y += 30

        # NPC Dialogue
        if self.active_npc:
            self.draw_npc_dialogue()

        # Map
        if self.show_map:
            self.draw_map()
        
        # Controls hint
        controls = small_font.render('WASD/Arrows: Move | M: Map | E: Return | Space: Talk', True, (150, 150, 150))
        screen.blit(controls, (10, SCREEN_HEIGHT - 25))

# Main Game Loop
game = Game()
running = True

while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    # Update animations
    npc_sprites.update(dt)
    player_animations.update(dt)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game.active_npc:
                    game.active_npc = None
                    game.dialogue_index = 0
                elif game.show_map:
                    game.show_map = False
                else:
                    running = False
                    
            elif event.key == pygame.K_m:
                game.show_map = not game.show_map
                
            elif event.key == pygame.K_SPACE and game.active_npc:
                npc = NPC_TYPES.get(game.active_npc, {})
                game.dialogue_index += 1
                if game.dialogue_index >= len(npc.get('dialogue', [])):
                    game.dialogue_index = 0
                    
            elif event.key == pygame.K_e:
                if game.current_dimension != 'overworld':
                    game.current_dimension = 'overworld'
                    game.add_message("Returned to Overworld!")
            
            # Toggle inventory with 'I' key
            elif event.key == pygame.K_i:
                game.show_inventory = not game.show_inventory
                
            # Hotbar selection with number keys
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                             pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8):
                if not game.show_inventory:  # Only change hotbar when inventory is closed
                    game.hotbar_slot = event.key - pygame.K_1  # Convert key to 0-7
                
            elif not game.active_npc and not game.show_map:
                # Movement
                if event.key in (pygame.K_w, pygame.K_UP):
                    game.move_player(0, -1)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    game.move_player(0, 1)
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    game.move_player(-1, 0)
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    game.move_player(1, 0)

    # Draw everything
    game.draw()
    pygame.display.flip()

pygame.quit()
sys.exit()