import pygame
import sys

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 400
GREEN = (0, 200, 0)

pygame.init()
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MINESWEEPER")
surface.fill(GREEN)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            pygame.quit()
            sys.exit()
    pygame.display.update()
