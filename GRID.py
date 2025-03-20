import pygame
import os
import sys
from pygame.locals import *
import random

# Initialize pygame
pygame.init()

# Set up the window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Minesweeper Code Lock")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)  # Classic Windows gray
DARK_GRAY = (128, 128, 128)
LIGHT_GRAY = (224, 224, 224)
GREEN = (0, 128, 0)  # Darker green for retro look
RED = (255, 0, 0)
BLUE = (0, 0, 128)  # Classic Windows blue

# Font - use a more pixelated/retro font
font = pygame.font.SysFont('Courier New', 24)
small_font = pygame.font.SysFont('Courier New', 18)
title_font = pygame.font.SysFont('Courier New', 30, bold=True)

# Symbol names - we'll use minesweeper themes
SYMBOLS = [
    'mine',
    'flag',
    'clock',
    'one',
    'two',
    'three',
    'blank',
    'question',
    'smiley'
]

# Correct code - which cells should be toggled on
CORRECT_CODE = [False, True, False, 
                True, False, True, 
                False, True, False]  # A pattern like an X

class MinesweeperCodeLock:
    def __init__(self):
        self.grid_size = 3
        self.cell_size = 100
        self.grid_margin = 8  # Classic chunky borders
        
        # Calculate grid position to center it
        self.grid_width = self.grid_size * self.cell_size + (self.grid_size - 1) * self.grid_margin
        self.grid_height = self.grid_size * self.cell_size + (self.grid_size - 1) * self.grid_margin
        
        self.grid_x = (WINDOW_WIDTH - self.grid_width) // 2
        self.grid_y = 150
        
        # Create grid cells - True means toggled/revealed, False means not toggled
        self.grid = [False] * 9
        self.grid_symbols = [random.choice(SYMBOLS) for _ in range(9)]  # Assign random symbols
        self.status = None  # None = not checked, True = correct, False = incorrect
        self.attempts = 0
        
        # Create reset button (smiley face)
        self.reset_button = pygame.Rect(
            WINDOW_WIDTH // 2 - 30,
            self.grid_y - 80,
            60, 60
        )
        
        # Create check button
        self.check_button = pygame.Rect(
            WINDOW_WIDTH // 2 - 100,
            self.grid_y + self.grid_height + 40,
            200, 50
        )
        
        # Create borders like classic Windows
        self.outer_border = pygame.Rect(
            self.grid_x - 12, 
            self.grid_y - 12,
            self.grid_width + 24,
            self.grid_height + 24
        )
        
        # Game title
        self.title = "MINESWEEPER CODE"
        
    def get_cell_rect(self, row, col):
        x = self.grid_x + col * (self.cell_size + self.grid_margin)
        y = self.grid_y + row * (self.cell_size + self.grid_margin)
        return pygame.Rect(x, y, self.cell_size, self.cell_size)
    
    def get_cell_index(self, position):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                rect = self.get_cell_rect(row, col)
                if rect.collidepoint(position):
                    return row * self.grid_size + col
        return None
    
    def toggle_cell(self, index):
        if index is None:
            return
            
        # Simply toggle the state
        self.grid[index] = not self.grid[index]
        
        # Reset status when changing grid
        self.status = None
    
    def check_code(self):
        # Check if current grid matches correct code
        self.status = (self.grid == CORRECT_CODE)
        self.attempts += 1
        return self.status
    
    def reset(self):
        self.grid = [False] * 9
        # Reassign random symbols for fun
        self.grid_symbols = [random.choice(SYMBOLS) for _ in range(9)]
        self.status = None
    
    def draw_3d_rect(self, surface, rect, color, raised=True):
        """Draw a 3D-looking rectangle like in Windows 95"""
        pygame.draw.rect(surface, color, rect)
        
        # Draw the 3D effect
        if raised:
            # Raised effect (light on top-left, dark on bottom-right)
            pygame.draw.line(surface, WHITE, rect.topleft, rect.topright, 2)
            pygame.draw.line(surface, WHITE, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(surface, DARK_GRAY, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(surface, DARK_GRAY, rect.topright, rect.bottomright, 2)
        else:
            # Sunken effect (dark on top-left, light on bottom-right)
            pygame.draw.line(surface, DARK_GRAY, rect.topleft, rect.topright, 2)
            pygame.draw.line(surface, DARK_GRAY, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(surface, WHITE, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(surface, WHITE, rect.topright, rect.bottomright, 2)
    
    def draw_mine(self, surface, rect):
        """Draw a classic minesweeper mine"""
        center = rect.center
        radius = min(rect.width, rect.height) // 3
        
        # Draw the mine circle
        pygame.draw.circle(surface, BLACK, center, radius)
        
        # Draw the spikes
        for angle in range(0, 360, 45):
            rads = angle * 3.14159 / 180
            x1 = center[0] + radius * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).x
            y1 = center[1] + radius * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).y
            x2 = center[0] + radius * 1.5 * pygame.math.Vector2(1, 0).rotate(angle).x
            y2 = center[1] + radius * 1.5 * pygame.math.Vector2(1, 0).rotate(angle).y
            pygame.draw.line(surface, BLACK, (x1, y1), (x2, y2), 3)
        
        # Draw the shine
        shine_pos = (center[0] - radius // 2, center[1] - radius // 2)
        pygame.draw.circle(surface, WHITE, shine_pos, radius // 5)
    
    def draw_flag(self, surface, rect):
        """Draw a classic minesweeper flag"""
        # Flag pole
        pole_start = (rect.centerx, rect.centery + rect.height // 5)
        pole_end = (rect.centerx, rect.centery - rect.height // 3)
        pygame.draw.line(surface, BLACK, pole_start, pole_end, 3)
        
        # Flag triangle
        flag_points = [
            pole_end,
            (rect.centerx + rect.width // 5, rect.centery - rect.height // 6),
            (rect.centerx, rect.centery)
        ]
        pygame.draw.polygon(surface, RED, flag_points)
        
        # Base
        base_rect = pygame.Rect(
            rect.centerx - rect.width // 6,
            rect.centery + rect.height // 5,
            rect.width // 3,
            rect.height // 10
        )
        pygame.draw.rect(surface, DARK_GRAY, base_rect)
    
    def draw_symbol(self, surface, rect, symbol, toggled):
        """Draw the appropriate symbol based on the symbol name and toggle state"""
        if not toggled:
            # Just draw a raised button if not toggled
            return
        
        if symbol == 'mine':
            self.draw_mine(surface, rect)
        elif symbol == 'flag':
            self.draw_flag(surface, rect)
        elif symbol == 'one':
            text = font.render("1", True, BLUE)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        elif symbol == 'two':
            text = font.render("2", True, GREEN)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        elif symbol == 'three':
            text = font.render("3", True, RED)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        elif symbol == 'clock':
            pygame.draw.circle(surface, BLACK, rect.center, rect.width // 5, 2)
            # Clock hands
            hand_length = rect.width // 8
            center = rect.center
            pygame.draw.line(surface, BLACK, center, 
                            (center[0], center[1] - hand_length), 2)
            pygame.draw.line(surface, BLACK, center, 
                            (center[0] + hand_length, center[1]), 2)
        elif symbol == 'question':
            text = font.render("?", True, BLUE)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        elif symbol == 'smiley':
            # Draw smiley face
            pygame.draw.circle(surface, (255, 255, 0), rect.center, rect.width // 4)
            # Eyes
            eye_offset = rect.width // 10
            pygame.draw.circle(surface, BLACK, 
                              (rect.centerx - eye_offset, rect.centery - eye_offset), 
                              rect.width // 20)
            pygame.draw.circle(surface, BLACK, 
                              (rect.centerx + eye_offset, rect.centery - eye_offset), 
                              rect.width // 20)
            # Smile
            smile_rect = pygame.Rect(
                rect.centerx - rect.width // 6,
                rect.centery,
                rect.width // 3,
                rect.height // 6
            )
            pygame.draw.arc(surface, BLACK, smile_rect, 0, 3.14, 2)
        # 'blank' symbol is just empty
    
    def draw_smiley(self, surface, rect, status):
        """Draw a smiley face based on status"""
        # Face background
        pygame.draw.circle(surface, (255, 255, 0), rect.center, rect.width // 2 - 5)
        
        # Eyes
        eye_offset = rect.width // 6
        pygame.draw.circle(surface, BLACK, 
                          (rect.centerx - eye_offset, rect.centery - eye_offset), 
                          rect.width // 10)
        pygame.draw.circle(surface, BLACK, 
                          (rect.centerx + eye_offset, rect.centery - eye_offset), 
                          rect.width // 10)
        
        # Mouth depends on status
        if status is None:
            # Normal smile
            smile_rect = pygame.Rect(
                rect.centerx - rect.width // 4,
                rect.centery,
                rect.width // 2,
                rect.height // 3
            )
            pygame.draw.arc(surface, BLACK, smile_rect, 0, 3.14, 3)
        elif status:
            # Cool sunglasses for win
            pygame.draw.rect(surface, BLACK, 
                            pygame.Rect(rect.centerx - rect.width // 3, 
                                      rect.centery - eye_offset - rect.height // 12,
                                      rect.width // 1.5,
                                      rect.height // 6))
            # Big smile
            smile_rect = pygame.Rect(
                rect.centerx - rect.width // 3,
                rect.centery + rect.height // 12,
                rect.width // 1.5,
                rect.height // 3
            )
            pygame.draw.arc(surface, BLACK, smile_rect, 0, 3.14, 3)
        else:
            # Dead face for loss (X eyes and sad mouth)
            eye_size = rect.width // 12
            
            # X eyes
            pygame.draw.line(surface, BLACK, 
                            (rect.centerx - eye_offset - eye_size, rect.centery - eye_offset - eye_size),
                            (rect.centerx - eye_offset + eye_size, rect.centery - eye_offset + eye_size), 3)
            pygame.draw.line(surface, BLACK, 
                            (rect.centerx - eye_offset + eye_size, rect.centery - eye_offset - eye_size),
                            (rect.centerx - eye_offset - eye_size, rect.centery - eye_offset + eye_size), 3)
            
            pygame.draw.line(surface, BLACK, 
                            (rect.centerx + eye_offset - eye_size, rect.centery - eye_offset - eye_size),
                            (rect.centerx + eye_offset + eye_size, rect.centery - eye_offset + eye_size), 3)
            pygame.draw.line(surface, BLACK, 
                            (rect.centerx + eye_offset + eye_size, rect.centery - eye_offset - eye_size),
                            (rect.centerx + eye_offset - eye_size, rect.centery - eye_offset + eye_size), 3)
            
            # Sad mouth
            pygame.draw.arc(surface, BLACK, 
                           pygame.Rect(rect.centerx - rect.width // 4,
                                     rect.centery + rect.height // 6,
                                     rect.width // 2,
                                     rect.height // 3), 
                           3.14, 2*3.14, 3)
    
    def draw(self, surface):
        # Fill background with classic Windows gray
        surface.fill(GRAY)
        
        # Draw title
        title = title_font.render(self.title, True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        surface.blit(title, title_rect)
        
        # Draw attempts counter
        attempts_text = small_font.render(f"Attempts: {self.attempts}", True, BLACK)
        surface.blit(attempts_text, (20, 20))
        
        # Draw outer border (Windows 95 style raised panel)
        self.draw_3d_rect(surface, self.outer_border, GRAY, True)
        
        # Draw reset button (smiley face)
        self.draw_3d_rect(surface, self.reset_button, GRAY, True)
        self.draw_smiley(surface, self.reset_button, self.status)
        
        # Draw grid cells
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                index = row * self.grid_size + col
                rect = self.get_cell_rect(row, col)
                
                # Draw cell background - raised if not toggled, sunken if toggled
                if self.grid[index]:
                    # Toggled cell is sunken with light gray background
                    pygame.draw.rect(surface, LIGHT_GRAY, rect)
                    self.draw_3d_rect(surface, rect, LIGHT_GRAY, False)
                    # Draw the symbol
                    self.draw_symbol(surface, rect, self.grid_symbols[index], True)
                else:
                    # Untoggled cell is raised button
                    self.draw_3d_rect(surface, rect, GRAY, True)
        
        # Draw check button (Windows 95 style)
        self.draw_3d_rect(surface, self.check_button, GRAY, True)
        
        check_text = font.render("Check Code", True, BLACK)
        check_text_rect = check_text.get_rect(center=self.check_button.center)
        surface.blit(check_text, check_text_rect)
        
        # Draw status message if applicable
        if self.status is not None:
            if self.status:
                status_text = font.render("ACCESS GRANTED!", True, GREEN)
            else:
                status_text = font.render("ACCESS DENIED!", True, RED)
            
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, self.check_button.bottom + 40))
            surface.blit(status_text, status_rect)
        
        # Draw hint/tips
        tip_text = small_font.render("Click cells to toggle them on/off", True, BLACK)
        tip_rect = tip_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
        surface.blit(tip_text, tip_rect)

def main():
    clock = pygame.time.Clock()
    code_lock = MinesweeperCodeLock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if a grid cell was clicked
                    cell_index = code_lock.get_cell_index(event.pos)
                    if cell_index is not None:
                        code_lock.toggle_cell(cell_index)
                    
                    # Check if reset button was clicked
                    if code_lock.reset_button.collidepoint(event.pos):
                        code_lock.reset()
                    
                    # Check if check button was clicked
                    if code_lock.check_button.collidepoint(event.pos):
                        code_lock.check_code()
        
        # Draw the code lock
        code_lock.draw(window)
        
        pygame.display.update()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()