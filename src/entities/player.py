from dataclasses import dataclass
from typing import Dict, Any, Tuple
import pygame
from ..utils.constants import TILE_SIZE, PLAYER_SPEED
from ..inventory.inventory import Inventory

@dataclass
class Player:
    x: float = 0.0
    y: float = 0.0
    speed: float = PLAYER_SPEED
    facing: str = 'down'  # 'up', 'down', 'left', 'right'
    
    def __post_init__(self):
        self.velocity_x = 0
        self.velocity_y = 0
        self.actions = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'interact': False,
            'attack': False,
            'use_item': False
        }
        self.inventory = Inventory()
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.animation_state = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()
    
    def handle_input(self, event):
        """Handle player input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.actions['up'] = True
                self.facing = 'up'
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.actions['down'] = True
                self.facing = 'down'
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                self.actions['left'] = True
                self.facing = 'left'
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.actions['right'] = True
                self.facing = 'right'
            elif event.key == pygame.K_e:
                self.actions['interact'] = True
            elif event.key == pygame.K_SPACE:
                self.actions['attack'] = True
            elif event.key == pygame.K_f:
                self.actions['use_item'] = True
        
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.actions['up'] = False
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.actions['down'] = False
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                self.actions['left'] = False
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.actions['right'] = False
            elif event.key == pygame.K_e:
                self.actions['interact'] = False
            elif event.key == pygame.K_SPACE:
                self.actions['attack'] = False
            elif event.key == pygame.K_f:
                self.actions['use_item'] = False
    
    def update(self, dt):
        """Update player state."""
        # Reset velocity
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Update position based on input
        if self.actions['up']:
            self.velocity_y = -self.speed
        if self.actions['down']:
            self.velocity_y = self.speed
        if self.actions['left']:
            self.velocity_x = -self.speed
        if self.actions['right']:
            self.velocity_x = self.speed
        
        # Normalize diagonal movement
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x *= 0.7071  # 1/sqrt(2)
            self.velocity_y *= 0.7071
        
        # Update position
        self.x += self.velocity_x * dt * 60  # Scale by dt and approximate FPS
        self.y += self.velocity_y * dt * 60
        
        # Update animation state
        self._update_animation_state()
        
        # Reset action flags
        self.actions['interact'] = False
        self.actions['attack'] = False
        self.actions['use_item'] = False
    
    def _update_animation_state(self):
        """Update the player's animation state based on movement."""
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.animation_state = 'walk'
        else:
            self.animation_state = 'idle'
        
        # Update animation frame
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:  # Update every 100ms
            self.last_update = now
            self.animation_frame = (self.animation_frame + 1) % 4  # Assuming 4-frame animations
    
    def get_interaction_position(self) -> Tuple[int, int]:
        """Get the position the player is facing for interactions."""
        x, y = int(round(self.x)), int(round(self.y))
        if self.facing == 'up':
            return x, y - 1
        elif self.facing == 'down':
            return x, y + 1
        elif self.facing == 'left':
            return x - 1, y
        else:  # right
            return x + 1, y
    
    def render(self, surface):
        """Render the player."""
        # This is a placeholder - in a real implementation, you'd use sprites
        x = int(self.x * TILE_SIZE)
        y = int(self.y * TILE_SIZE)
        
        # Draw player (simple rectangle for now)
        pygame.draw.rect(surface, (0, 0, 255), (x, y, TILE_SIZE, TILE_SIZE))
        
        # Draw facing direction indicator
        if self.facing == 'up':
            pygame.draw.polygon(surface, (255, 0, 0), [
                (x + TILE_SIZE//2, y),
                (x, y + TILE_SIZE//2),
                (x + TILE_SIZE, y + TILE_SIZE//2)
            ])
        elif self.facing == 'down':
            pygame.draw.polygon(surface, (255, 0, 0), [
                (x, y + TILE_SIZE//2),
                (x + TILE_SIZE, y + TILE_SIZE//2),
                (x + TILE_SIZE//2, y + TILE_SIZE)
            ])
        elif self.facing == 'left':
            pygame.draw.polygon(surface, (255, 0, 0), [
                (x, y + TILE_SIZE//2),
                (x + TILE_SIZE//2, y),
                (x + TILE_SIZE//2, y + TILE_SIZE)
            ])
        else:  # right
            pygame.draw.polygon(surface, (255, 0, 0), [
                (x + TILE_SIZE, y + TILE_SIZE//2),
                (x + TILE_SIZE//2, y),
                (x + TILE_SIZE//2, y + TILE_SIZE)
            ])
    
    def use_selected_item(self):
        """Use the currently selected item in the hotbar."""
        item = self.inventory.get_selected_item()
        if item:
            # Handle item usage based on type
            if item.type == 'consumable':
                if item.effect == 'heal':
                    self.health = min(self.max_health, self.health + item.value)
                elif item.effect == 'stamina':
                    self.stamina = min(self.max_stamina, self.stamina + item.value)
                
                # Remove the item if it's consumed
                self.inventory.remove_item(item, 1)
                return f"Used {item.name}"
        return None
