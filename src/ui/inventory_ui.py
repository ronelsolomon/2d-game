import pygame
from typing import Optional, Tuple, List
from ..utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT, UI_FONT_SIZE, UI_SMALL_FONT_SIZE,
    UI_TINY_FONT_SIZE, UI_PADDING, UI_BG_COLOR, UI_BORDER_COLOR, UI_ACCENT_COLOR,
    UI_TEXT_COLOR, UI_TEXT_COLOR_DISABLED, BLACK, WHITE, SLOT_SIZE, SLOT_MARGIN,
    SLOT_BG_COLOR, SLOT_SELECTED_COLOR, SLOT_HOVER_COLOR, INVENTORY_SLOTS,
    HOTBAR_SLOTS
)

class InventoryUI:
    def __init__(self, inventory):
        self.inventory = inventory
        self.visible = False
        self.selected_slot = 0
        self.dragging_item = None
        self.drag_offset = (0, 0)
        
        # Calculate inventory grid layout
        self.slots_x = 8  # Number of slots per row
        self.slots_y = (INVENTORY_SLOTS + self.slots_x - 1) // self.slots_x  # Calculate rows needed
        
        # Calculate inventory position and size
        self.width = self.slots_x * (SLOT_SIZE + SLOT_MARGIN) - SLOT_MARGIN + 40
        self.height = self.slots_y * (SLOT_SIZE + SLOT_MARGIN) - SLOT_MARGIN + 80
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Load fonts
        try:
            self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE)
            self.small_font = pygame.font.SysFont(UI_FONT, UI_SMALL_FONT_SIZE)
            self.tiny_font = pygame.font.SysFont(UI_FONT, UI_TINY_FONT_SIZE)
        except:
            # Fallback to default fonts if the specified font isn't available
            self.font = pygame.font.Font(None, UI_FONT_SIZE)
            self.small_font = pygame.font.Font(None, UI_SMALL_FONT_SIZE)
            self.tiny_font = pygame.font.Font(None, UI_TINY_FONT_SIZE)
    
    def toggle(self):
        """Toggle the visibility of the inventory."""
        self.visible = not self.visible
        return self.visible
    
    def is_visible(self) -> bool:
        """Check if the inventory is visible."""
        return self.visible
    
    def get_slot_at(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get the inventory slot at the given screen position, or None if outside."""
        x, y = pos
        
        # Check if position is within inventory bounds
        if not (self.x <= x <= self.x + self.width and 
                self.y + 40 <= y <= self.y + self.height - 20):
            return None
        
        # Calculate which slot was clicked
        rel_x = x - self.x - 20
        rel_y = y - self.y - 60
        
        if rel_x < 0 or rel_y < 0:
            return None
            
        slot_x = rel_x // (SLOT_SIZE + SLOT_MARGIN)
        slot_y = rel_y // (SLOT_SIZE + SLOT_MARGIN)
        
        if slot_x >= self.slots_x or slot_y >= self.slots_y:
            return None
            
        slot = slot_y * self.slots_x + slot_x
        
        return slot if slot < INVENTORY_SLOTS else None
    
    def handle_event(self, event):
        """Handle pygame events for the inventory UI."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                slot = self.get_slot_at(event.pos)
                if slot is not None:
                    # Start dragging item
                    if slot < len(self.inventory.items):
                        self.dragging_item = (slot, self.inventory.items[slot])
                        self.drag_offset = (
                            event.pos[0] - (self.x + 20 + (slot % self.slots_x) * (SLOT_SIZE + SLOT_MARGIN)),
                            event.pos[1] - (self.y + 60 + (slot // self.slots_x) * (SLOT_SIZE + SLOT_MARGIN))
                        )
                        return True
            
            elif event.button == 3:  # Right click
                slot = self.get_slot_at(event.pos)
                if slot is not None and slot < len(self.inventory.items):
                    # Use item on right click
                    item = self.inventory.items[slot]
                    # TODO: Handle item usage
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_item is not None:  # Left click release
                slot = self.get_slot_at(event.pos)
                src_slot, item = self.dragging_item
                
                if slot is not None:  # Dropped on a valid slot
                    if slot < len(self.inventory.items):
                        # Swap items if the target slot is not empty
                        self.inventory.items[src_slot] = self.inventory.items[slot]
                        self.inventory.items[slot] = item
                    else:
                        # Move item to empty slot
                        self.inventory.items[src_slot] = None
                        if slot < len(self.inventory.items):
                            self.inventory.items[slot] = item
                        else:
                            self.inventory.items.append(item)
                
                # Clean up
                self.dragging_item = None
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.visible = False
                return True
            
            # Handle number keys for hotbar selection
            if pygame.K_1 <= event.key <= pygame.K_8:  # 1-8 keys
                slot = event.key - pygame.K_1
                if slot < self.inventory.hotbar_size:
                    self.inventory.selected_slot = slot
                    return True
        
        return False
    
    def update(self, dt):
        """Update the inventory UI."""
        pass  # No continuous updates needed for now
    
    def render(self, surface: pygame.Surface):
        """Render the inventory UI."""
        if not self.visible:
            return
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
        # Draw inventory background
        pygame.draw.rect(surface, (50, 50, 50), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (100, 100, 100), (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        title = self.font.render("INVENTORY", True, WHITE)
        surface.blit(title, (self.x + (self.width - title.get_width()) // 2, self.y + 15))
        
        # Draw inventory slots
        for i in range(self.slots_y):
            for j in range(self.slots_x):
                slot = i * self.slots_x + j
                if slot >= INVENTORY_SLOTS:
                    continue
                    
                x = self.x + 20 + j * (SLOT_SIZE + SLOT_MARGIN)
                y = self.y + 60 + i * (SLOT_SIZE + SLOT_MARGIN)
                
                # Draw slot background
                color = SLOT_SELECTED_COLOR if slot == self.inventory.selected_slot else SLOT_BG_COLOR
                pygame.draw.rect(surface, color, (x, y, SLOT_SIZE, SLOT_SIZE))
                pygame.draw.rect(surface, (100, 100, 100), (x, y, SLOT_SIZE, SLOT_SIZE), 1)
                
                # Draw item in slot if it exists
                if slot < len(self.inventory.items) and self.inventory.items[slot] is not None:
                    item = self.inventory.items[slot]
                    
                    # Skip if this is the item being dragged
                    if self.dragging_item and self.dragging_item[0] == slot:
                        continue
                    
                    # Draw item icon (placeholder)
                    pygame.draw.rect(surface, (200, 200, 200), (x + 4, y + 4, SLOT_SIZE - 8, SLOT_SIZE - 8))
                    
                    # Draw item quantity if stackable
                    if item.quantity > 1:
                        qty_text = self.tiny_font.render(str(item.quantity), True, WHITE)
                        surface.blit(qty_text, (x + SLOT_SIZE - qty_text.get_width() - 2, 
                                             y + SLOT_SIZE - qty_text.get_height() - 2))
        
        # Draw the item being dragged
        if self.dragging_item:
            slot, item = self.dragging_item
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Draw item at mouse position with offset
            x = mouse_x - self.drag_offset[0]
            y = mouse_y - self.drag_offset[1]
            
            # Draw item icon (placeholder)
            pygame.draw.rect(surface, (200, 200, 200), (x + 4, y + 4, SLOT_SIZE - 8, SLOT_SIZE - 8))
            
            # Draw item quantity if stackable
            if item.quantity > 1:
                qty_text = self.tiny_font.render(str(item.quantity), True, WHITE)
                surface.blit(qty_text, (x + SLOT_SIZE - qty_text.get_width() - 2, 
                                     y + SLOT_SIZE - qty_text.get_height() - 2))
