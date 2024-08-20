import pygame
import sys
import random
import math
import json
import os
import hashlib


# Initialize pygame
pygame.init()

# Load the background image
background_image = pygame.image.load(r'C:\Users\nims0\pongbackground.jpg')


# Constants
WIDTH, HEIGHT = 1280, 720
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FPS = 60
POWERUP_SIZE = 20
#Sonja Sosa
BORDER_THICKNESS = 10     
BORDER_SHRINK_AMOUNT = 1  
SHRINK_AMOUNT = 3 * 2  # Tripled the paddle shrink amount
PADDLE_MARGIN = 10  # Margin to keep paddles inside the border
RIGHT_PADDLE_MARGIN = 20  # Additional margin for the right paddle
WINNING_SCORE = 50  # Game ends at 50 points
PLAYER_DATA_FILE = 'player_data.json'

# Load player data
if os.path.exists(PLAYER_DATA_FILE):
    with open(PLAYER_DATA_FILE, 'r') as f:
        player_data = json.load(f)
else:
    player_data = {}

def get_player_name(prompt):
    # Function to get player name with input prompt
    name = input(prompt)
    if name not in player_data:
        player_data[name] = {'wins': 0, 'games': 0}
        with open(PLAYER_DATA_FILE, 'w') as f:
            json.dump(player_data, f, indent=4)
    return name

def get_win_ratio(name):
    # Function to calculate win ratio
    data = player_data.get(name, {'wins': 0, 'games': 0})
    wins = data['wins']
    games = data['games']
    return wins / games if games > 0 else 0






# Get player names
player1_name = get_player_name('Player 1, enter your name: ')
player2_name = get_player_name('Player 2, enter your name: ')

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')

class Ball:
    def __init__(self, x, y, size, color, speed_x, speed_y, is_main_ball=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.is_main_ball = is_main_ball
        self.stuck_to_player = None

# Set up game objects
initial_ball_speed = 3
main_ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, WHITE, initial_ball_speed, initial_ball_speed, True)
player1 = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2 = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH - RIGHT_PADDLE_MARGIN, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball speed increment
ball_speed_increment = 0.5

# Scores
score1 = 0
score2 = 0

# Font for displaying scores and winner
font = pygame.font.Font(None, 36)

# Power-ups
powerups = []
#Vanessa Mejia
POWERUP_INTERVAL = 5000  # Time interval (ms) to spawn power-ups
last_powerup_time = pygame.time.get_ticks()

# Extra balls
extra_balls = []

# Stuck ball logic
ball_stuck = False
last_touched_player = None

def spawn_powerup():
    powerup_type = random.choice(['P', 'R', 'S'])  # Changed 'G' to 'S'
    x = random.randint(border_left + POWERUP_SIZE, border_right - POWERUP_SIZE)
    y = random.randint(border_top + POWERUP_SIZE, border_bottom - POWERUP_SIZE)
    powerup = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
    return powerup, powerup_type


def update_paddle_size(paddle):
    if paddle.height > SHRINK_AMOUNT * 2:  # Ensure paddle doesn't get too small
        paddle.height -= SHRINK_AMOUNT

#Sonja Sosa
def shrink_border():
    global border_left, border_right, border_top, border_bottom
    border_left += BORDER_SHRINK_AMOUNT
    border_right -= BORDER_SHRINK_AMOUNT
    border_top += BORDER_SHRINK_AMOUNT
    border_bottom -= BORDER_SHRINK_AMOUNT

    # Ensure the border doesn't shrink below the goal area
    border_left = max(border_left, PADDLE_WIDTH + PADDLE_MARGIN)
    border_right = min(border_right, WIDTH - PADDLE_WIDTH - RIGHT_PADDLE_MARGIN)
    border_top = max(border_top, 0)
    border_bottom = min(border_bottom, HEIGHT)

def check_border_collision(ball):
    if ball.rect.left <= border_left:
        ball.speed_x *= -1
        ball.rect.left = border_left
    elif ball.rect.right >= border_right:
        ball.speed_x *= -1
        ball.rect.right = border_right

    if ball.rect.top <= border_top:
        ball.speed_y *= -1
        ball.rect.top = border_top
    elif ball.rect.bottom >= border_bottom:
        ball.speed_y *= -1
        ball.rect.bottom = border_bottom

# Add this loop in your game loop where you update the position of extra balls:
for extra_ball in extra_balls:
    extra_ball.rect.x += extra_ball.speed_x
    extra_ball.rect.y += extra_ball.speed_y
    check_border_collision(extra_ball)

    if extra_ball.rect.colliderect(player1):
        extra_ball.speed_x *= -1
        extra_ball.rect.left = player1.right  # Ensure the ball is outside the paddle to avoid sticking
        last_touched_player = 1
        # Increase ball speed after each volley
        extra_ball.speed_x += ball_speed_increment if extra_ball.speed_x > 0 else -ball_speed_increment
        extra_ball.speed_y += ball_speed_increment if extra_ball.speed_y > 0 else -ball_speed_increment

    elif extra_ball.rect.colliderect(player2):
        extra_ball.speed_x *= -1
        extra_ball.rect.right = player2.left  # Ensure the ball is outside the paddle to avoid sticking
        last_touched_player = 2
        # Increase ball speed after each volley
        extra_ball.speed_x += ball_speed_increment if extra_ball.speed_x > 0 else -ball_speed_increment
        extra_ball.speed_y += ball_speed_increment if extra_ball.speed_y > 0 else -ball_speed_increment




def adjust_paddle_positions():
    # Adjust paddles to keep them within the new border limits
    player1.x = max(border_left + PADDLE_MARGIN, player1.x)
    player1.x = min(border_left + PADDLE_MARGIN + PADDLE_WIDTH, player1.x)
    
    player2.x = max(border_right - PADDLE_WIDTH - RIGHT_PADDLE_MARGIN, player2.x)
    player2.x = min(border_right - RIGHT_PADDLE_MARGIN, player2.x)

# Initial border dimensions
border_left = BORDER_THICKNESS + 50  # Adjusted border left
border_right = WIDTH - BORDER_THICKNESS - 50  # Adjusted border right
border_top = BORDER_THICKNESS + 50  # Adjusted border top
border_bottom = HEIGHT - BORDER_THICKNESS - 50  # Adjusted border bottom

# Game loop
clock = pygame.time.Clock()
game_over = False
winner = None

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and ball_stuck:
                # Serve the ball again if it's stuck
                if last_touched_player == 1:
                    main_ball.speed_x = initial_ball_speed
                    main_ball.speed_y = initial_ball_speed
                elif last_touched_player == 2:
                    main_ball.speed_x = -initial_ball_speed
                    main_ball.speed_y = -initial_ball_speed
                main_ball.rect.center = (WIDTH // 2, HEIGHT // 2)
                ball_stuck = False

    # Move paddles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player1.y -= 7
    if keys[pygame.K_s]:
        player1.y += 7
    if keys[pygame.K_UP]:
        player2.y -= 7
    if keys[pygame.K_DOWN]:
        player2.y += 7

    # Ensure paddles stay within the window
    player1.y = max(min(player1.y, HEIGHT - PADDLE_HEIGHT), 0)
    player2.y = max(min(player2.y, HEIGHT - PADDLE_HEIGHT), 0)

    # Adjust paddle positions with shrinking border
    adjust_paddle_positions()

    # Ball movement
    main_ball.rect.x += main_ball.speed_x
    main_ball.rect.y += main_ball.speed_y

    # Extra balls movement
    for extra_ball in extra_balls:
        extra_ball.rect.x += extra_ball.speed_x
        extra_ball.rect.y += extra_ball.speed_y
        check_border_collision(extra_ball)

    # Collision with paddles
    if main_ball.rect.colliderect(player1):
        main_ball.speed_x *= -1
        last_touched_player = 1
        ball_stuck = False
        # Increase ball speed after each volley
        main_ball.speed_x += ball_speed_increment if main_ball.speed_x > 0 else -ball_speed_increment
        main_ball.speed_y += ball_speed_increment if main_ball.speed_y > 0 else -ball_speed_increment
        # Shrink the border by Sonja Sosa
        shrink_border()
    elif main_ball.rect.colliderect(player2):
        main_ball.speed_x *= -1
        last_touched_player = 2
        ball_stuck = False
        # Increase ball speed after each volley
        main_ball.speed_x += ball_speed_increment if main_ball.speed_x > 0 else -ball_speed_increment
        main_ball.speed_y += ball_speed_increment if main_ball.speed_y > 0 else -ball_speed_increment
        # Shrink the border
        shrink_border()

    # Check border collision
    check_border_collision(main_ball)

    # Handle scoring
    if main_ball.rect.left <= border_left:
        # Player 2 scores
        score2 += 1
        if score2 % 2 == 0:
            update_paddle_size(player2)
        if score2 >= WINNING_SCORE:
            game_over = True
            winner = player2_name
            player_data[player2_name]['wins'] += 1
            player_data[player2_name]['games'] += 1
            player_data[player1_name]['games'] += 1
            with open(PLAYER_DATA_FILE, 'w') as f:
                json.dump(player_data, f, indent=4)
        else:
            # Reset main ball position and speed
            main_ball.rect.center = (WIDTH // 2, HEIGHT // 2)
            main_ball.speed_x = initial_ball_speed
            main_ball.speed_y = initial_ball_speed
            extra_balls = []  # Remove all extra balls

    elif main_ball.rect.right >= border_right:
        # Player 1 scores
        score1 += 5
        if score1 % 2 == 0:
            update_paddle_size(player1)
        if score1 >= WINNING_SCORE:
            game_over = True
            winner = player1_name
            player_data[player1_name]['wins'] += 1
            player_data[player1_name]['games'] += 1
            player_data[player2_name]['games'] += 1
            with open(PLAYER_DATA_FILE, 'w') as f:
                json.dump(player_data, f, indent=4)
        else:
            # Reset main ball position and speed
            main_ball.rect.center = (WIDTH // 2, HEIGHT // 2)
            main_ball.speed_x = -initial_ball_speed
            main_ball.speed_y = -initial_ball_speed
            extra_balls = []  # Remove all extra balls

    # Extra balls scoring
    for extra_ball in extra_balls:
        if extra_ball.rect.left <= border_left:
            # Player 2 scores
            score2 += 1
            extra_balls.remove(extra_ball)
        elif extra_ball.rect.right >= border_right:
            # Player 1 scores
            score1 += 1
            extra_balls.remove(extra_ball)

    # Power-up logic
    current_time = pygame.time.get_ticks()
    if current_time - last_powerup_time > POWERUP_INTERVAL:
        last_powerup_time = current_time
        powerup, powerup_type = spawn_powerup()
        powerups.append((powerup, powerup_type))

    # Ball collision with power-ups
    for powerup, powerup_type in powerups:
        if main_ball.rect.colliderect(powerup):
            powerups.remove((powerup, powerup_type))
            if powerup_type == 'P': #Caleb Mylius
                for _ in range(2):
                    extra_ball = Ball(main_ball.rect.x, main_ball.rect.y, BALL_SIZE, YELLOW, main_ball.speed_x + random.choice([-1, 1]), main_ball.speed_y + random.choice([-1, 1]))
                    extra_balls.append(extra_ball)
            elif powerup_type == 'R': #Dylan Flores
                # Preserve current speed while redirecting the ball
                speed = math.hypot(main_ball.speed_x, main_ball.speed_y)  # Get current speed magnitude
                angle = random.uniform(-math.pi / 2, math.pi / 2)  # Random angle between -90 and 90 degrees
                main_ball.speed_x = speed * math.cos(angle)  # Calculate new x speed
                main_ball.speed_y = speed * math.sin(angle)  # Calculate new y speed
            elif powerup_type == 'S': #Vanessa Mejia
                # Double the ball's current speed
                main_ball.speed_x *= 2
                main_ball.speed_y *= 2

    # Drawing everything
    # Draw the background image
    screen.blit(background_image, (0, 0))


    pygame.draw.rect(screen, WHITE, player1)
    pygame.draw.rect(screen, WHITE, player2)
    pygame.draw.ellipse(screen, main_ball.color, main_ball.rect)
    for extra_ball in extra_balls:
        pygame.draw.ellipse(screen, extra_ball.color, extra_ball.rect)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Draw border
    pygame.draw.rect(screen, WHITE, pygame.Rect(border_left, border_top, border_right - border_left, border_bottom - border_top), BORDER_THICKNESS)

    # Draw power-ups
    for powerup, powerup_type in powerups:
        if powerup_type == 'P':
            pygame.draw.circle(screen, BLUE, powerup.center, POWERUP_SIZE // 2)
            p_text = font.render('P', True, WHITE)
            screen.blit(p_text, (powerup.center[0] - p_text.get_width() // 2, powerup.center[1] - p_text.get_height() // 2))
        elif powerup_type == 'R':
            pygame.draw.circle(screen, RED, powerup.center, POWERUP_SIZE // 2)
            r_text = font.render('R', True, WHITE)
            screen.blit(r_text, (powerup.center[0] - r_text.get_width() // 2, powerup.center[1] - r_text.get_height() // 2))
        elif powerup_type == 'S':
            pygame.draw.circle(screen, GREEN, powerup.center, POWERUP_SIZE // 2)
            s_text = font.render('S', True, WHITE)
            screen.blit(s_text, (powerup.center[0] - s_text.get_width() // 2, powerup.center[1] - s_text.get_height() // 2))

    # Display scores
    score1_text = font.render(f'{score1}', True, YELLOW)
    score2_text = font.render(f'{score2}', True, YELLOW)
    screen.blit(score1_text, (WIDTH // 2 - score1_text.get_width() - 50, 20))
    screen.blit(score2_text, (WIDTH // 2 + 50, 20))

    # Display player stats
    p1_wins = player_data[player1_name]['wins']
    p1_games = player_data[player1_name]['games']
    p1_ratio = get_win_ratio(player1_name)

    p2_wins = player_data[player2_name]['wins']
    p2_games = player_data[player2_name]['games']
    p2_ratio = get_win_ratio(player2_name)

    p1_text = font.render(f'{player1_name}: {p1_wins}W / {p1_games}G ({p1_ratio:.2f})', True, WHITE)
    p2_text = font.render(f'{player2_name}: {p2_wins}W / {p2_games}G ({p2_ratio:.2f})', True, WHITE)

    screen.blit(p1_text, (10, 10))
    screen.blit(p2_text, (WIDTH - p2_text.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(FPS)

# End of game
if winner:
    print(f'{winner} wins!')
pygame.quit()
