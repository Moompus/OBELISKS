import pygame
import sys
import os
import random
from PIL import Image

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 700  # Extra height for display area
GRID_SIZE = 3
CELL_SIZE = 150
GRID_MARGIN = 75
GLYPH_SIZE = 100
BG_COLOR = (30, 30, 40)
GRID_COLOR = (100, 100, 120)
SELECTED_COLOR = (100, 180, 255, 150)
SUCCESS_COLOR = (100, 255, 100)
FAIL_COLOR = (255, 100, 100)
BUTTON_COLOR = (80, 120, 200)
BUTTON_HOVER_COLOR = (100, 140, 220)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Glyph Code Unlocker")

# Glyph definitions with image support
class Glyph:
    def __init__(self, id, name, image_path):
        self.id = id
        self.name = name
        self.image_path = image_path
        self.pygame_image = None
        self.load_image()
        
    def load_image(self):
        try:
            # Use PIL to open and resize the image
            pil_image = Image.open(self.image_path)
            pil_image = pil_image.resize((GLYPH_SIZE, GLYPH_SIZE))
            
            # Convert PIL image to pygame surface
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()
            
            self.pygame_image = pygame.image.fromstring(data, size, mode)
            
            # Handle transparency for different image formats
            if mode == 'RGBA':
                self.pygame_image = self.pygame_image.convert_alpha()
            else:
                self.pygame_image = self.pygame_image.convert()
                self.pygame_image.set_colorkey((255, 255, 255))  # Set white as transparent
                
        except Exception as e:
            print(f"Error loading image {self.image_path}: {e}")
            # Create a fallback surface with text
            self.pygame_image = pygame.Surface((GLYPH_SIZE, GLYPH_SIZE), pygame.SRCALPHA)
            self.pygame_image.fill((80, 80, 100))
            font = pygame.font.SysFont('Arial', 20)
            text = font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(GLYPH_SIZE//2, GLYPH_SIZE//2))
            self.pygame_image.blit(text, text_rect)

# Define 9 glyphs using the PNG files
glyphs = [
    Glyph(0, "barcode", "barcode.png"),
    Glyph(1, "cassette", "cassette.png"),
    Glyph(2, "eject", "eject.png"),
    Glyph(3, "film", "film.png"),
    Glyph(4, "games", "games.png"),
    Glyph(5, "play", "play-button-arrowhead.png"),
    Glyph(6, "rewind", "rewind-sign.png"),
    Glyph(7, "stop", "stop-button.png"),
    Glyph(8, "vhs", "vhs.png")
]

# Place glyphs on the grid
grid = []
for i in range(GRID_SIZE):
    row = []
    for j in range(GRID_SIZE):
        index = i * GRID_SIZE + j
        row.append(glyphs[index])
    grid.append(row)

# Generate random code at startup (3 symbols long)
correct_code = random.sample(range(9), 3)
current_code = []
input_active = False
show_button = True
show_code = False  # Hide the code by default, only show when 'P' is pressed

# Create small versions of glyph images for the code display
small_glyph_images = {}
for glyph in glyphs:
    try:
        pil_image = Image.open(glyph.image_path)
        pil_image = pil_image.resize((30, 30))
        
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        
        small_image = pygame.image.fromstring(data, size, mode)
        if mode == 'RGBA':
            small_image = small_image.convert_alpha()
        else:
            small_image = small_image.convert()
            small_image.set_colorkey((255, 255, 255))  # Set white as transparent
            
        small_glyph_images[glyph.id] = small_image
    except Exception as e:
        print(f"Error creating small image for {glyph.image_path}: {e}")
        small_glyph_images[glyph.id] = pygame.Surface((30, 30), pygame.SRCALPHA)
        small_glyph_images[glyph.id].fill((100, 100, 150))

# Font setup
font = pygame.font.SysFont('Arial', 30)
small_font = pygame.font.SysFont('Arial', 20)
button_font = pygame.font.SysFont('Arial', 24)

# Button properties
start_button = pygame.Rect(WIDTH//2 - 100, GRID_MARGIN + CELL_SIZE*GRID_SIZE + 30, 200, 50)
button_text = "Start Entering Code"

# Code display box
code_box = pygame.Rect(WIDTH - 150, 20, 130, 50)

# Get names of glyphs in the correct code
def get_code_symbols():
    return [next(g for g in glyphs if g.id == glyph_id) for glyph_id in correct_code]

code_symbols = get_code_symbols()
message = "Press 'P' to reveal the access code"
code_status = None

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Calculate cell position
            x = col * CELL_SIZE + GRID_MARGIN
            y = row * CELL_SIZE + GRID_MARGIN
            
            # Draw cell background
            pygame.draw.rect(screen, GRID_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 2)
            
            # Draw glyph image
            glyph = grid[row][col]
            if glyph.pygame_image:
                image_rect = glyph.pygame_image.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                screen.blit(glyph.pygame_image, image_rect)

def draw_current_code():
    # Draw current code entry
    code_text = "Current Code: "
    text = font.render(code_text, True, (220, 220, 220))
    screen.blit(text, (GRID_MARGIN, HEIGHT - 100))
    
    # Draw the glyph images for the current code
    if len(current_code) == 0:
        text = font.render("None", True, (220, 220, 220))
        screen.blit(text, (GRID_MARGIN + text.get_width() + 10, HEIGHT - 100))
    else:
        for i, glyph_id in enumerate(current_code):
            small_image = small_glyph_images[glyph_id]
            screen.blit(small_image, (GRID_MARGIN + text.get_width() + 10 + i * 40, HEIGHT - 105))

def draw_message():
    # Draw status message
    color = (220, 220, 220)
    if code_status == "success":
        color = SUCCESS_COLOR
    elif code_status == "fail":
        color = FAIL_COLOR
    
    display_message = message
    if not show_code and code_status is None and not input_active:
        display_message = "Press 'P' to reveal the access code"
    elif not show_code and input_active:
        display_message = "Enter your 3-symbol code"
        
    text = font.render(display_message, True, color)
    screen.blit(text, (GRID_MARGIN, HEIGHT - 150))

def draw_code_box():
    # Only draw the code box if show_code is True
    if not show_code:
        return
        
    # Draw background
    pygame.draw.rect(screen, (50, 50, 70), code_box, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 130), code_box, 2, border_radius=5)
    
    # Draw title
    title = small_font.render("Access Code:", True, (200, 200, 200))
    screen.blit(title, (code_box.x + 10, code_box.y + 5))
    
    # Draw code images
    for i, glyph in enumerate(code_symbols):
        small_image = small_glyph_images[glyph.id]
        screen.blit(small_image, (code_box.x + 15 + i * 35, code_box.y + 25))

def draw_button():
    if not show_button:
        return
        
    mouse_pos = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER_COLOR if start_button.collidepoint(mouse_pos) else BUTTON_COLOR
    
    # Draw the button
    pygame.draw.rect(screen, button_color, start_button, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), start_button, 2, border_radius=8)
    
    # Draw the button text
    text = button_font.render(button_text, True, (255, 255, 255))
    text_rect = text.get_rect(center=start_button.center)
    screen.blit(text, text_rect)

def verify_code():
    global message, code_status, input_active, show_button
    if current_code == correct_code:
        message = "Code Correct! Access Granted"
        code_status = "success"
        input_active = False
        show_button = False
        return True
    else:
        message = "Incorrect Code. Press R to try again."
        code_status = "fail"
        input_active = False
        show_button = False
        return False

def reset_code():
    global current_code, code_status, show_button, input_active, message, show_code
    # Reset everything EXCEPT the correct code
    current_code = []
    code_status = None
    show_button = True
    input_active = False
    show_code = False
    message = "Press 'P' to reveal the access code"

def start_code_entry():
    global input_active, message, current_code, code_status, show_button
    input_active = True
    current_code = []
    code_status = None
    message = "Enter your 3-symbol code"
    show_button = False

def toggle_code_visibility():
    global show_code, message
    show_code = not show_code
    if show_code:
        message = "Access code revealed"
    else:
        message = "Access code hidden. Press 'P' to reveal."

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the button was clicked
            if show_button and start_button.collidepoint(event.pos):
                if not input_active:
                    start_code_entry()
            
            # Check if a grid cell was clicked during active input
            elif input_active:
                pos = event.pos
                
                # Calculate grid position
                if (GRID_MARGIN <= pos[0] < GRID_MARGIN + CELL_SIZE * GRID_SIZE and 
                    GRID_MARGIN <= pos[1] < GRID_MARGIN + CELL_SIZE * GRID_SIZE):
                    col = (pos[0] - GRID_MARGIN) // CELL_SIZE
                    row = (pos[1] - GRID_MARGIN) // CELL_SIZE
                    
                    # Add glyph to current code if we haven't reached the limit
                    if len(current_code) < len(correct_code):
                        glyph_id = grid[row][col].id
                        current_code.append(glyph_id)
                        
                        # Check code if we have the correct number of glyphs
                        if len(current_code) == len(correct_code):
                            verify_code()
        
        elif event.type == pygame.KEYDOWN:
            # Reset on R key
            if event.key == pygame.K_r:
                reset_code()
            # Toggle code visibility on P key
            elif event.key == pygame.K_p:
                toggle_code_visibility()
    
    # Clear the screen
    screen.fill(BG_COLOR)
    
    # Draw elements
    draw_grid()
    draw_current_code()
    draw_message()
    draw_button()
    draw_code_box()  # This will only draw if show_code is True
    
    # Draw instruction text
    if input_active:
        status = f"Entering code: {len(current_code)}/{len(correct_code)} symbols"
    elif show_button:
        status = "Press the button to begin"
    else:
        status = "Press 'R' to reset and try again"
    
    instructions = font.render(status, True, (180, 180, 180))
    screen.blit(instructions, (GRID_MARGIN, HEIGHT - 50))
    
    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()