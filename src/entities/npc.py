import pygame

class NPC:
    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 2

    def update(self, game):
        # Basic NPC movement logic - can be expanded as needed
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def render(self, surface, offset=(0, 0)):
        # Draw the NPC
        render_rect = self.rect.copy()
        render_rect.x -= offset[0]
        render_rect.y -= offset[1]
        pygame.draw.rect(surface, self.color, render_rect)
