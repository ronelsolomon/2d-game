import pygame
from typing import List
from ..utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT, UI_FONT_SIZE, UI_SMALL_FONT_SIZE,
    UI_TINY_FONT_SIZE, UI_PADDING, UI_BG_COLOR, UI_BORDER_COLOR, UI_ACCENT_COLOR,
    UI_TEXT_COLOR, UI_TEXT_COLOR_DISABLED, BLACK, WHITE, RED, GREEN, BLUE, YELLOW,
    SLOT_SIZE, SLOT_MARGIN, SLOT_BG_COLOR, SLOT_SELECTED_COLOR, SLOT_HOVER_COLOR
)

class HUD:
    def __init__(self, player):
        self.player = player
        self.messages: List[str] = []
        self.message_timer = 0
        self.message_duration = 5000  # 5 seconds in milliseconds
        
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
        
        # Dialogue
        self.dialogue = None
        self.dialogue_index = 0
        self.dialogue_typing = False
        self.dialogue_text = ""
        self.dialogue_speed = 2  # characters per frame
        self.dialogue_timer = 0
    
    def update(self, dt):
        # Update message timer
        if self.messages:
            self.message_timer += dt * 1000  # Convert to milliseconds
            if self.message_timer > self.message_duration:
                self.messages.pop(0)
                self.message_timer = 0
        
        # Update dialogue typing effect
        if self.dialogue_typing and self.dialogue:
            self.dialogue_timer += dt * 60  # Approximate frames per second
            if self.dialogue_timer >= 1.0 / self.dialogue_speed:
                self.dialogue_timer = 0
                if len(self.dialogue_text) < len(self.dialogue[self.dialogue_index]):
                    self.dialogue_text += self.dialogue[self.dialogue_index][len(self.dialogue_text)]
                else:
                    self.dialogue_typing = False
    
    def add_message(self, message: str):
        """Add a message to the HUD."""
        self.messages.append(message)
        self.message_timer = 0
        print(f"HUD: {message}")  # Also print to console for debugging
    
    def start_dialogue(self, dialogue: List[str]):
        """Start a dialogue sequence."""
        self.dialogue = dialogue
        self.dialogue_index = 0
        self.dialogue_typing = True
        self.dialogue_text = ""
        self.dialogue_timer = 0
    
    def next_dialogue(self) -> bool:
        """Advance to the next line of dialogue or finish the dialogue."""
        if not self.dialogue:
            return False
            
        if self.dialogue_typing:
            # Skip typing effect and show full text
            self.dialogue_typing = False
            self.dialogue_text = self.dialogue[self.dialogue_index]
            return True
        elif self.dialogue_index < len(self.dialogue) - 1:
            # Go to next line
            self.dialogue_index += 1
            self.dialogue_typing = True
            self.dialogue_text = ""
            self.dialogue_timer = 0
            return True
        else:
            # End of dialogue
            self.dialogue = None
            return False
    
    def render(self, surface: pygame.Surface):
        """Render the HUD."""
        self._render_health_bar(surface)
        self._render_messages(surface)
        self._render_hotbar(surface)
    
    def _render_health_bar(self, surface: pygame.Surface):
        """Render the player's health bar."""
        bar_width = 200
        bar_height = 20
        x = SCREEN_WIDTH - bar_width - 20
        y = 20
        
        # Background
        pygame.draw.rect(surface, (50, 50, 50), (x - 2, y - 2, bar_width + 4, bar_height + 4))
        
        # Health bar
        health_ratio = self.player.health / self.player.max_health
        health_width = int(bar_width * health_ratio)
        health_color = (
            int(255 * (1 - health_ratio)),  # Red component
            int(255 * health_ratio),       # Green component
            0                              # Blue component
        )
        
        pygame.draw.rect(surface, (100, 100, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, health_color, (x, y, health_width, bar_height))
        
        # Health text
        health_text = f"HP: {self.player.health}/{self.player.max_health}"
        text_surface = self.small_font.render(health_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        surface.blit(text_surface, text_rect)
    
    def _render_messages(self, surface: pygame.Surface):
        """Render the message log."""
        if not self.messages:
            return
        
        # Only show the most recent message for now
        message = self.messages[0]
        
        # Calculate text size
        text_surface = self.small_font.render(message, True, WHITE)
        text_rect = text_surface.get_rect()
        
        # Create background
        bg_rect = pygame.Rect(
            20,
            SCREEN_HEIGHT - 80,
            text_rect.width + 20,
            text_rect.height + 20
        )
        
        # Draw background and text
        pygame.draw.rect(surface, (0, 0, 0, 200), bg_rect)
        pygame.draw.rect(surface, WHITE, bg_rect, 1)
        surface.blit(text_surface, (bg_rect.x + 10, bg_rect.y + 10))
    
    def _render_hotbar(self, surface: pygame.Surface):
        """Render the hotbar at the bottom of the screen."""
        if not hasattr(self.player, 'inventory'):
            return
            
        hotbar_width = self.player.inventory.hotbar_size * (SLOT_SIZE + SLOT_MARGIN) - SLOT_MARGIN
        hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
        hotbar_y = SCREEN_HEIGHT - SLOT_SIZE - 20
        
        # Draw hotbar background
        pygame.draw.rect(
            surface,
            (50, 50, 50, 200),
            (hotbar_x - 10, hotbar_y - 10, hotbar_width + 20, SLOT_SIZE + 20)
        )
        
        # Draw hotbar slots
        for i in range(self.player.inventory.hotbar_size):
            x = hotbar_x + i * (SLOT_SIZE + SLOT_MARGIN)
            y = hotbar_y
            
            # Draw slot background
            color = SLOT_SELECTED_COLOR if i == self.player.inventory.selected_slot else SLOT_BG_COLOR
            pygame.draw.rect(surface, color, (x, y, SLOT_SIZE, SLOT_SIZE))
            pygame.draw.rect(surface, (100, 100, 100), (x, y, SLOT_SIZE, SLOT_SIZE), 1)
            
            # Draw item in slot if it exists and is not None
            if i < len(self.player.inventory.items) and self.player.inventory.items[i] is not None:
                item = self.player.inventory.items[i]
                
                # Draw item icon (placeholder)
                pygame.draw.rect(surface, (200, 200, 200), (x + 4, y + 4, SLOT_SIZE - 8, SLOT_SIZE - 8))
                
                # Draw item quantity if stackable and quantity > 1
                if hasattr(item, 'quantity') and item.quantity > 1:
                    qty_text = self.tiny_font.render(str(item.quantity), True, WHITE)
                    surface.blit(qty_text, (x + SLOT_SIZE - qty_text.get_width() - 2, 
                                         y + SLOT_SIZE - qty_text.get_height() - 2))
    
    def render_dialogue(self, surface: pygame.Surface):
        """Render the current dialogue."""
        if not self.dialogue:
            return
        
        # Calculate dialogue box position and size
        box_width = SCREEN_WIDTH - 100
        box_height = 150
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = SCREEN_HEIGHT - box_height - 20
        
        # Draw dialogue box background
        pygame.draw.rect(surface, (0, 0, 0, 220), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surface, WHITE, (box_x, box_y, box_width, box_height), 1)
        
        # Draw speaker name (placeholder)
        speaker = "NPC"
        name_surface = self.font.render(speaker, True, WHITE)
        surface.blit(name_surface, (box_x + 20, box_y + 10))
        
        # Draw dialogue text with word wrapping
        text = self.dialogue_text
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.small_font.render(test_line, True, WHITE)
            
            if test_surface.get_width() <= box_width - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Render each line of text
        for i, line in enumerate(lines):
            if i >= 3:  # Limit to 3 lines
                break
                
            text_surface = self.small_font.render(line, True, WHITE)
            surface.blit(text_surface, (box_x + 20, box_y + 50 + i * 25))
        
        # Draw "Press to continue" prompt
        if not self.dialogue_typing and (self.dialogue_index < len(self.dialogue) - 1 or len(self.dialogue) > 1):
            prompt = "Press SPACE to continue..."
            prompt_surface = self.tiny_font.render(prompt, True, (200, 200, 200))
            surface.blit(prompt_surface, (box_x + box_width - prompt_surface.get_width() - 20, 
                                       box_y + box_height - 30))
