import pygame
import sys
import random
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants - adjusted for fast gameplay
WIDTH, HEIGHT = 1000, 700
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 70
BALL_SIZE = 15
POWERUP_SIZE = 25  # Slightly larger for better visibility
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
FPS = 60

# Game variables
base_ball_speed = 7  # Higher default speed for more exciting gameplay
paddle_speed = 9  # Slightly faster paddles to match ball speed
score_player1 = 0
score_player2 = 0
powerup_duration = 7000  # 7 seconds for powerups

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('PONG 2: ELECTRIC BOOGALOO')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Create game objects
player1 = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2 = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball class for multiple ball powerup
class Ball:
    def __init__(self, x=None, y=None, dx=None, dy=None, size=BALL_SIZE):
        if x is None:
            x = WIDTH // 2 - size // 2
        if y is None:
            y = HEIGHT // 2 - size // 2
        
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        
        if dx is None or dy is None:
            angle = random.uniform(-math.pi/4, math.pi/4)
            direction = random.choice([-1, 1])
            self.dx = direction * base_ball_speed * math.cos(angle)
            self.dy = base_ball_speed * math.sin(angle)
        else:
            self.dx = dx
            self.dy = dy
            
    def update(self):
        # Update position
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Wall collisions
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy = -self.dy
            
        # Check if out of bounds (scoring)
        if self.rect.left <= 0:
            return "right_score"
        elif self.rect.right >= WIDTH:
            return "left_score"
        
        return None
    
    def check_paddle_collision(self, paddle1, paddle2):
        if self.rect.colliderect(paddle1):
            self.rect.left = paddle1.right + 1  # Prevent sticking
            self.dx = abs(self.dx) * 1.05  # Slight speed increase on hits
            
            # Add bounce angle variation
            relative_intersect_y = (paddle1.y + paddle1.height / 2) - self.rect.centery
            normalized_relative_intersect_y = relative_intersect_y / (paddle1.height / 2)
            bounce_angle = normalized_relative_intersect_y * (math.pi / 3)  # Wider angle range (60°)
            speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
            self.dx = speed * math.cos(bounce_angle)
            self.dy = -speed * math.sin(bounce_angle)
            
            return True
            
        elif self.rect.colliderect(paddle2):
            self.rect.right = paddle2.left - 1  # Prevent sticking
            self.dx = -abs(self.dx) * 1.05  # Slight speed increase on hits
            
            # Add bounce angle variation
            relative_intersect_y = (paddle2.y + paddle2.height / 2) - self.rect.centery
            normalized_relative_intersect_y = relative_intersect_y / (paddle2.height / 2)
            bounce_angle = normalized_relative_intersect_y * (math.pi / 3)  # Wider angle range (60°)
            speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
            self.dx = -speed * math.cos(bounce_angle)
            self.dy = -speed * math.sin(bounce_angle)
            
            return True
            
        return False
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Initialize primary ball
balls = [Ball()]

# Powerup related variables
active_powerups = []
powerup_types = [
    {"name": "Big Ball", "color": RED, "duration": powerup_duration, "stack_limit": 3},
    {"name": "Speed Boost", "color": GREEN, "duration": powerup_duration, "stack_limit": 3},
    {"name": "Paddle Growth", "color": BLUE, "duration": powerup_duration, "stack_limit": 3},
    {"name": "Multi-Ball", "color": ORANGE, "duration": powerup_duration, "stack_limit": 3},  # Added multi-ball
    {"name": "Paddle Speed", "color": CYAN, "duration": powerup_duration, "stack_limit": 3}   # Added paddle speed boost
]
powerups = []
powerup_spawn_timer = 0
next_powerup_time = random.randint(3000, 6000)  # More frequent powerups (3-6 seconds)

# Track stacking levels for each powerup
powerup_stacks = {
    "Big Ball": 0,
    "Speed Boost": 0,
    "Paddle Growth": 0,
    "Multi-Ball": 0,
    "Paddle Speed": 0
}

# Original values for resetting
original_ball_size = BALL_SIZE
original_paddle_height = PADDLE_HEIGHT
original_paddle_speed = paddle_speed

def reset_primary_ball():
    # Reset only the main ball while keeping any additional balls
    balls[0] = Ball()

def spawn_powerup():
    powerup_type = random.choice(powerup_types)
    powerup = {
        "rect": pygame.Rect(
            random.randint(WIDTH // 4, 3 * WIDTH // 4 - POWERUP_SIZE),
            random.randint(POWERUP_SIZE, HEIGHT - POWERUP_SIZE * 2),
            POWERUP_SIZE,
            POWERUP_SIZE
        ),
        "type": powerup_type,
        "collected": False
    }
    powerups.append(powerup)

def apply_powerup(powerup_type):
    global paddle_speed
    
    powerup_name = powerup_type["name"]
    
    # Check if we've hit the stack limit
    if powerup_stacks[powerup_name] >= powerup_type["stack_limit"]:
        # If at stack limit, refresh the duration instead
        for effect in active_powerups:
            if effect["type"]["name"] == powerup_name:
                effect["start_time"] = pygame.time.get_ticks()
        return
    
    # Stack the powerup
    powerup_stacks[powerup_name] += 1
    
    new_effect = {
        "type": powerup_type,
        "start_time": pygame.time.get_ticks(),
        "duration": powerup_type["duration"],
        "stack_level": powerup_stacks[powerup_name]
    }
    active_powerups.append(new_effect)
    
    # Apply effect based on the current stack level
    if powerup_name == "Big Ball":
        # Increase ball size for all balls
        scale_factor = 1.3 ** powerup_stacks[powerup_name]  # Exponential scaling
        new_size = int(original_ball_size * scale_factor)
        for ball in balls:
            ball.size = new_size
            ball.rect.width = new_size
            ball.rect.height = new_size
    
    elif powerup_name == "Speed Boost":
        # Increase ball speed for all balls
        speed_factor = 1.2 ** powerup_stacks[powerup_name]
        for ball in balls:
            ball.dx *= speed_factor
            ball.dy *= speed_factor
    
    elif powerup_name == "Paddle Growth":
        # Increase paddle size
        scale_factor = 1.25 ** powerup_stacks[powerup_name]
        new_height = int(original_paddle_height * scale_factor)
        player1.height = new_height
        player2.height = new_height
    
    elif powerup_name == "Multi-Ball":
        # Add more balls based on stack level (1 extra at level 1, 2 at level 2, 4 at level 3)
        new_balls_count = 2 ** (powerup_stacks[powerup_name] - 1)
        for _ in range(new_balls_count):
            # Create a new ball with random direction
            existing_ball = random.choice(balls)  # Pick a random existing ball
            # Create a new ball at same position but different angle
            new_ball = Ball(
                existing_ball.rect.centerx - BALL_SIZE//2,
                existing_ball.rect.centery - BALL_SIZE//2,
                None,  # Random direction
                None,
                existing_ball.size  # Same size as source ball
            )
            balls.append(new_ball)
    
    elif powerup_name == "Paddle Speed":
        # Increase paddle movement speed
        speed_factor = 1.25 ** powerup_stacks[powerup_name]
        paddle_speed = int(original_paddle_speed * speed_factor)

def update_powerups():
    global paddle_speed
    
    current_time = pygame.time.get_ticks()
    
    # Check for expired powerups
    expired_powerups = []
    for effect in active_powerups:
        if current_time - effect["start_time"] >= effect["duration"]:
            expired_powerups.append(effect)
    
    # Remove expired powerups and revert their effects
    for effect in expired_powerups:
        powerup_name = effect["type"]["name"]
        stack_level = effect["stack_level"]
        
        # Reduce stack count
        powerup_stacks[powerup_name] -= 1
        
        # Only revert effects if all stacks of this powerup are gone
        if powerup_stacks[powerup_name] == 0:
            if powerup_name == "Big Ball":
                # Reset ball size
                for ball in balls:
                    ball.size = original_ball_size
                    ball.rect.width = original_ball_size
                    ball.rect.height = original_ball_size
            
            elif powerup_name == "Speed Boost":
                # Reset ball speeds to base speed but preserve direction
                for ball in balls:
                    current_speed = math.sqrt(ball.dx*ball.dx + ball.dy*ball.dy)
                    direction_x = ball.dx / current_speed
                    direction_y = ball.dy / current_speed
                    ball.dx = direction_x * base_ball_speed
                    ball.dy = direction_y * base_ball_speed
            
            elif powerup_name == "Paddle Growth":
                # Reset paddle size
                player1.height = original_paddle_height
                player2.height = original_paddle_height
            
            elif powerup_name == "Multi-Ball":
                # Remove extra balls, always keep at least one
                if len(balls) > 1:
                    # Keep only the first ball
                    balls[:] = [balls[0]]
            
            elif powerup_name == "Paddle Speed":
                # Reset paddle speed
                paddle_speed = original_paddle_speed
        
        # Remove the expired effect
        active_powerups.remove(effect)

def draw_game():
    screen.fill(BLACK)
    
    # Draw paddles
    pygame.draw.rect(screen, WHITE, player1)
    pygame.draw.rect(screen, WHITE, player2)
    
    # Draw all balls
    for ball in balls:
        ball.draw()
    
    # Draw powerups
    for powerup in powerups:
        if not powerup["collected"]:
            pygame.draw.rect(screen, powerup["type"]["color"], powerup["rect"])
            # Add a pulsing effect for visibility
            pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() / 200))
            pygame.draw.rect(screen, (pulse, pulse, pulse), powerup["rect"], 2)
    
    # Draw center line
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 10))
    
    # Draw score
    score_text1 = font.render(str(score_player1), True, WHITE)
    score_text2 = font.render(str(score_player2), True, WHITE)
    screen.blit(score_text1, (WIDTH // 4, 20))
    screen.blit(score_text2, (3 * WIDTH // 4 - score_text2.get_width(), 20))
    
    # Draw title
    title_font = pygame.font.Font(None, 30)
    title_text = title_font.render("PONG 2: ELECTRIC BOOGALOO", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))
    
    # Draw active powerups with stack counts
    active_powerup_text = []
    for powerup_name, stack_count in powerup_stacks.items():
        if stack_count > 0:
            active_powerup_text.append(f"{powerup_name} x{stack_count}")
    
    y_offset = 50
    for text in active_powerup_text:
        powerup_display = font.render(text, True, WHITE)
        screen.blit(powerup_display, (WIDTH // 2 - powerup_display.get_width() // 2, y_offset))
        y_offset += 30
        
    # Draw ball count
    ball_count_text = font.render(f"Balls: {len(balls)}", True, WHITE)
    screen.blit(ball_count_text, (WIDTH // 2 - ball_count_text.get_width() // 2, HEIGHT - 30))

# Main game loop
def main():
    global powerup_spawn_timer, next_powerup_time
    global score_player1, score_player2
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        
        # Player 1 (left) controls - W and S
        if keys[K_w] and player1.top > 0:
            player1.y -= paddle_speed
        if keys[K_s] and player1.bottom < HEIGHT:
            player1.y += paddle_speed
        
        # Player 2 (right) controls - Up and Down arrows
        if keys[K_UP] and player2.top > 0:
            player2.y -= paddle_speed
        if keys[K_DOWN] and player2.bottom < HEIGHT:
            player2.y += paddle_speed
        
        # Update all balls
        for ball in balls[:]:  # Use a copy for safe iteration
            result = ball.update()
            
            # Handle scoring
            if result == "right_score":
                score_player2 += 1
                if ball is balls[0]:  # If it's the primary ball
                    reset_primary_ball()
                else:
                    balls.remove(ball)  # Remove this extra ball
            elif result == "left_score":
                score_player1 += 1
                if ball is balls[0]:  # If it's the primary ball
                    reset_primary_ball()
                else:
                    balls.remove(ball)  # Remove this extra ball
            
            # Check paddle collisions
            ball.check_paddle_collision(player1, player2)
        
        # Make sure we always have at least one ball
        if not balls:
            balls.append(Ball())
        
        # Powerup handling
        current_time = pygame.time.get_ticks()
        powerup_spawn_timer = current_time
        
        # Spawn new powerups more frequently
        if powerup_spawn_timer >= next_powerup_time:
            spawn_powerup()
            # More frequent as game progresses
            next_powerup_time = current_time + random.randint(2000, 5000)
        
        # Check for powerup collisions with any ball
        for powerup in powerups[:]:
            is_collected = False
            for ball in balls:
                if powerup["rect"].colliderect(ball.rect) and not powerup["collected"]:
                    is_collected = True
                    break
                    
            if is_collected:
                powerup["collected"] = True
                apply_powerup(powerup["type"])
                powerups.remove(powerup)
        
        # Update active powerups
        update_powerups()
        
        # Draw everything
        draw_game()
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()