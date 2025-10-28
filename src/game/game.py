import pygame
import os
import sys
from typing import Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entities.player import Player
from src.world.world import World
from src.ui.inventory_ui import InventoryUI
from src.ui.hud import HUD
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Game:
    def __init__(self):
        # Initialize display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Farming Game")
        
        # Initialize game components
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        # Create game world and player
        self.world = World()
        self.player = Player()
        
        # UI components
        self.inventory_ui = InventoryUI(self.player.inventory)
        self.hud = HUD(self.player)
        
        # Game state
        self.show_inventory = False
        self.show_map = False
        self.active_npc = None
    
    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.QUIT:
            self.running = False
        
        # Toggle inventory
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.show_inventory = not self.show_inventory
        
        # Toggle map
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self.show_map = not self.show_map
        
        # Handle player input
        if not self.show_inventory and not self.show_map:
            self.player.handle_input(event)
        
        # Handle UI input
        if self.show_inventory:
            self.inventory_ui.handle_event(event)
    
    def update(self, dt):
        """Update game state."""
        self.dt = dt
        
        # Update player and world
        self.player.update(dt)
        self.world.update(dt)
        
        # Update UI
        self.hud.update(dt)
        
        # Handle world interactions
        self._handle_world_interactions()
    
    def _handle_world_interactions(self):
        """Handle interactions between player and game world."""
        # Handle tile interactions
        if self.player.actions.get('interact'):
            self._handle_tile_interaction()
        
        # Handle NPC interactions
        if self.player.actions.get('talk'):
            self._handle_npc_interaction()
    
    def _handle_tile_interaction(self):
        """Handle player interaction with tiles."""
        # Get tile in front of player
        x, y = self.player.get_interaction_position()
        tile = self.world.get_tile(x, y)
        
        # Handle different tile types
        if tile.is_collectible():
            self._collect_tile(x, y, tile)
        elif tile.is_interactive():
            self._interact_with_tile(x, y, tile)
    
    def _collect_tile(self, x, y, tile):
        """Handle collecting a collectible tile."""
        item = tile.get_item()
        if item and self.player.inventory.add_item(item):
            self.world.set_tile(x, y, self.world.tile_types['empty'])
            self.hud.add_message(f"Collected {item.name}")
    
    def _interact_with_tile(self, x, y, tile):
        """Handle interaction with an interactive tile."""
        result = tile.interact(self.player)
        if result:
            self.hud.add_message(result)
    
    def _handle_npc_interaction(self):
        """Handle player interaction with NPCs."""
        x, y = self.player.get_interaction_position()
        npc = self.world.get_npc(x, y)
        
        if npc:
            self.active_npc = npc
            # Start dialogue with NPC
            self.hud.start_dialogue(npc.get_dialogue())
    
    def render(self):
        """Render the game."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render world
        self.world.render(self.screen, self.player.x, self.player.y)
        
        # Render player
        self.player.render(self.screen)
        
        # Render UI
        self.hud.render(self.screen)
        
        if self.show_inventory:
            self.inventory_ui.render(self.screen)
        
        if self.show_map:
            self.world.render_minimap(self.screen)
        
        # Render NPC dialogue if active
        if self.active_npc:
            self.hud.render_dialogue(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def quit(self):
        """Clean up and quit the game."""
        pygame.quit()
        sys.exit()
