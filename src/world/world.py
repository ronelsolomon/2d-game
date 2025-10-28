import random
from typing import Dict, List, Optional, Tuple
import pygame
from .tile import Tile, TILE_TYPES
from ..utils.constants import (
    VIEWPORT_WIDTH, VIEWPORT_HEIGHT, TILE_SIZE,
    SCREEN_WIDTH, SCREEN_HEIGHT
)

class World:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.entities = []
        self.generate_terrain()
    
    def generate_terrain(self):
        """Generate a simple terrain for testing."""
        for y in range(self.height):
            for x in range(self.width):
                # Simple terrain generation
                if y > self.height // 2 + random.randint(-2, 2):
                    # Bottom half is mostly dirt with some stone
                    if random.random() < 0.1:
                        self.tiles[(x, y)] = Tile('stone')
                    else:
                        self.tiles[(x, y)] = Tile('dirt')
                else:
                    # Top half is mostly grass with some flowers
                    if random.random() < 0.05:
                        self.tiles[(x, y)] = Tile('flower')
                    else:
                        self.tiles[(x, y)] = Tile('grass')
        
        # Add some trees
        for _ in range(50):
            x = random.randint(0, self.width - 1)
            y = random.randint(5, self.height // 2 - 1)
            if (x, y) in self.tiles and self.tiles[(x, y)].type == 'grass':
                self.tiles[(x, y)] = Tile('tree')
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get the tile at the given coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles.get((x, y), Tile('empty'))
        return Tile('empty')  # Out of bounds is empty space
    
    def set_tile(self, x: int, y: int, tile_type: str) -> bool:
        """Set the tile at the given coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[(x, y)] = Tile(tile_type)
            return True
        return False
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is walkable."""
        tile = self.get_tile(x, y)
        return tile.is_walkable()
    
    def render(self, surface: pygame.Surface, player_x: float, player_y: float):
        """Render the world centered on the player."""
        # Calculate the top-left tile to start rendering from
        start_x = int(player_x - VIEWPORT_WIDTH // 2)
        start_y = int(player_y - VIEWPORT_HEIGHT // 2)
        
        # Render tiles
        for y in range(VIEWPORT_HEIGHT + 1):
            for x in range(VIEWPORT_WIDTH + 1):
                world_x = start_x + x
                world_y = start_y + y
                
                # Get the tile and render it
                tile = self.get_tile(world_x, world_y)
                if tile:
                    # Calculate screen position
                    screen_x = x * TILE_SIZE
                    screen_y = y * TILE_SIZE
                    
                    # Draw the tile
                    tile_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, tile.color, tile_rect)
                    
                    # Draw a grid (optional)
                    pygame.draw.rect(surface, (50, 50, 50), tile_rect, 1)
    
    def update(self, dt: float):
        """Update the world state.
        
        Args:
            dt: Time elapsed since the last update in seconds.
        """
        # Update all entities in the world
        for entity in self.entities:
            if hasattr(entity, 'update'):
                entity.update(dt)
        
        # Here you can add any world-specific updates, like:
        # - Time of day changes
        # - Weather effects
        # - Tile updates (e.g., growing plants)
        # - Spawning/despawning entities
    
    def render_minimap(self, surface: pygame.Surface):
        """Render a minimap in the corner of the screen."""
        minimap_width = 100
        minimap_height = 100
        minimap_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
        
        # Draw a semi-transparent background
        pygame.draw.rect(minimap_surface, (0, 0, 0, 180), (0, 0, minimap_width, minimap_height))
        
        # Draw tiles
        cell_width = minimap_width / self.width
        cell_height = minimap_height / self.height
        
        for (x, y), tile in self.tiles.items():
            if tile.type != 'empty':
                rect = pygame.Rect(
                    x * cell_width,
                    y * cell_height,
                    cell_width + 1,  # +1 to avoid gaps
                    cell_height + 1
                )
                pygame.draw.rect(minimap_surface, tile.color, rect)
        
        # Draw the minimap on the main surface
        surface.blit(minimap_surface, (10, 10))
