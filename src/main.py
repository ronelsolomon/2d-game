import pygame
import sys
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.game import Game

def main():
    # Initialize Pygame
    pygame.init()
    
    # Create game instance
    game = Game()
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to game
            game.handle_event(event)
        
        # Update game state
        game.update(dt)
        
        # Render game
        game.render()
        
        # Update display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
