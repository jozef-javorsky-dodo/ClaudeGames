import pygame
import sys
import random
import time
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 1000
LINE_WIDTH = 4
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = 200
BOARD_OFFSET_X = (WIDTH - (SQUARE_SIZE * 3)) // 2
BOARD_OFFSET_Y = (HEIGHT - (SQUARE_SIZE * 3)) // 2
CIRCLE_RADIUS = 50
CIRCLE_WIDTH = 10
CROSS_WIDTH = 15
SPACE = 55

# Colors
BG_COLOR = (0, 10, 0)
LINE_COLOR = (0, 200, 0)
CIRCLE_COLOR = (0, 230, 230)
CROSS_COLOR = (0, 255, 0)
TIMER_COLOR = (200, 255, 200)
HOVER_COLOR = (0, 100, 0, 100)  # With alpha for transparency
MATRIX_RAIN_COLOR = (0, 210, 0)
GAME_OVER_BG = (0, 0, 0, 190)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

# Load fonts
try:
    matrix_font = pygame.font.Font("matrix.ttf", 36)
    timer_font = pygame.font.Font("matrix.ttf", 60)
    game_over_font = pygame.font.Font("matrix.ttf", 80)
    player_font = pygame.font.Font("matrix.ttf", 42)
except:
    # Fallback to system font if matrix.ttf isn't available
    matrix_font = pygame.font.SysFont("monospace", 36)
    timer_font = pygame.font.SysFont("monospace", 60)
    game_over_font = pygame.font.SysFont("monospace", 80)
    player_font = pygame.font.SysFont("monospace", 42)

# Board setup
board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
player = "X"
game_over = False
winner = None
winning_line = None

# Timer setup
MAX_TIME = 10  # 10 seconds per game
start_time = time.time()


# Matrix rain setup
class MatrixRain:
    def __init__(self):
        self.chars = []
        for i in range(100):
            self.chars.append(
                {
                    "x": random.randint(0, WIDTH),
                    "y": random.randint(-HEIGHT, 0),
                    "speed": random.randint(5, 15),
                    "char": chr(random.randint(33, 126)),
                    "size": random.randint(10, 24),
                }
            )

    def update(self):
        for char in self.chars:
            char["y"] += char["speed"]
            if char["y"] > HEIGHT:
                char["y"] = random.randint(-100, 0)
                char["x"] = random.randint(0, WIDTH)
                char["char"] = chr(random.randint(33, 126))

    def draw(self, surface):
        for char in self.chars:
            # Don't draw matrix rain over the game board area
            if (
                BOARD_OFFSET_X <= char["x"] <= BOARD_OFFSET_X + SQUARE_SIZE * 3
                and BOARD_OFFSET_Y <= char["y"] <= BOARD_OFFSET_Y + SQUARE_SIZE * 3
            ):
                continue

            font = pygame.font.SysFont("monospace", char["size"])
            text = font.render(char["char"], True, MATRIX_RAIN_COLOR)
            surface.blit(text, (char["x"], char["y"]))


matrix_rain = MatrixRain()


# Function to draw the board
def draw_board():
    # Draw vertical lines
    pygame.draw.line(
        screen,
        LINE_COLOR,
        (BOARD_OFFSET_X + SQUARE_SIZE, BOARD_OFFSET_Y),
        (BOARD_OFFSET_X + SQUARE_SIZE, BOARD_OFFSET_Y + 3 * SQUARE_SIZE),
        LINE_WIDTH,
    )
    pygame.draw.line(
        screen,
        LINE_COLOR,
        (BOARD_OFFSET_X + 2 * SQUARE_SIZE, BOARD_OFFSET_Y),
        (BOARD_OFFSET_X + 2 * SQUARE_SIZE, BOARD_OFFSET_Y + 3 * SQUARE_SIZE),
        LINE_WIDTH,
    )

    # Draw horizontal lines
    pygame.draw.line(
        screen,
        LINE_COLOR,
        (BOARD_OFFSET_X, BOARD_OFFSET_Y + SQUARE_SIZE),
        (BOARD_OFFSET_X + 3 * SQUARE_SIZE, BOARD_OFFSET_Y + SQUARE_SIZE),
        LINE_WIDTH,
    )
    pygame.draw.line(
        screen,
        LINE_COLOR,
        (BOARD_OFFSET_X, BOARD_OFFSET_Y + 2 * SQUARE_SIZE),
        (BOARD_OFFSET_X + 3 * SQUARE_SIZE, BOARD_OFFSET_Y + 2 * SQUARE_SIZE),
        LINE_WIDTH,
    )

    # Draw the grid cells with digital effect
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            cell_x = BOARD_OFFSET_X + col * SQUARE_SIZE
            cell_y = BOARD_OFFSET_Y + row * SQUARE_SIZE

            # Draw cell border with digital effect
            for i in range(4):
                alpha = 100 - i * 20
                if alpha < 0:
                    alpha = 0
                border_color = (0, 200, 0, alpha)
                pygame.draw.rect(
                    screen,
                    border_color,
                    (cell_x - i, cell_y - i, SQUARE_SIZE + i * 2, SQUARE_SIZE + i * 2),
                    1,
                )


# Function to draw X and O markers
def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == "X":
                # Digital X
                center_x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2

                # Draw multiple X's with fading effect for digital look
                for i in range(5):
                    factor = 1 - i * 0.15
                    if factor < 0:
                        factor = 0
                    color = (
                        int(CROSS_COLOR[0] * factor),
                        int(CROSS_COLOR[1] * factor),
                        int(CROSS_COLOR[2] * factor),
                    )

                    # Main X
                    pygame.draw.line(
                        screen,
                        color,
                        (center_x - SPACE + i, center_y - SPACE + i),
                        (center_x + SPACE - i, center_y + SPACE - i),
                        CROSS_WIDTH,
                    )
                    pygame.draw.line(
                        screen,
                        color,
                        (center_x + SPACE - i, center_y - SPACE + i),
                        (center_x - SPACE + i, center_y + SPACE - i),
                        CROSS_WIDTH,
                    )

            elif board[row][col] == "O":
                # Digital O
                center_x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2

                # Draw multiple circles with fading effect for digital look
                for i in range(5):
                    factor = 1 - i * 0.15
                    if factor < 0:
                        factor = 0
                    color = (
                        int(CIRCLE_COLOR[0] * factor),
                        int(CIRCLE_COLOR[1] * factor),
                        int(CIRCLE_COLOR[2] * factor),
                    )

                    pygame.draw.circle(
                        screen,
                        color,
                        (center_x, center_y),
                        CIRCLE_RADIUS - i * 2,
                        CIRCLE_WIDTH - i,
                    )

                # Add digital patterns to O
                for angle in range(0, 360, 45):
                    end_x = center_x + int(
                        CIRCLE_RADIUS * 0.8 * math.cos(math.radians(angle))
                    )
                    end_y = center_y + int(
                        CIRCLE_RADIUS * 0.8 * math.sin(math.radians(angle))
                    )
                    pygame.draw.line(
                        screen, CIRCLE_COLOR, (center_x, center_y), (end_x, end_y), 2
                    )


# Function to check for win
def check_win():
    # Check rows
    for row in range(BOARD_ROWS):
        if (
            board[row][0] == board[row][1] == board[row][2]
            and board[row][0] is not None
        ):
            return board[row][0], [(row, 0), (row, 1), (row, 2)]

    # Check columns
    for col in range(BOARD_COLS):
        if (
            board[0][col] == board[1][col] == board[2][col]
            and board[0][col] is not None
        ):
            return board[0][col], [(0, col), (1, col), (2, col)]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0], [(0, 0), (1, 1), (2, 2)]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2], [(0, 2), (1, 1), (2, 0)]

    # Check for tie
    if all(
        board[row][col] is not None
        for row in range(BOARD_ROWS)
        for col in range(BOARD_COLS)
    ):
        return "Tie", None

    return None, None


# Draw the timer
def draw_timer():
    elapsed = time.time() - start_time
    remaining = max(0, MAX_TIME - elapsed)

    # Format timer
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)
    timer_str = f"{minutes:02d}:{seconds:02d}"

    # Create glowing effect based on remaining time
    glow_factor = min(1.0, remaining / MAX_TIME * 2)
    timer_color = (
        int(TIMER_COLOR[0] * glow_factor),
        int(TIMER_COLOR[1]),
        int(TIMER_COLOR[2] * glow_factor),
    )

    timer_text = timer_font.render(timer_str, True, timer_color)
    screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 120))

    # Draw progress bar
    bar_width = 400
    bar_height = 10
    progress = remaining / MAX_TIME

    # Background bar
    pygame.draw.rect(
        screen, (30, 30, 30), (WIDTH // 2 - bar_width // 2, 100, bar_width, bar_height)
    )

    # Progress bar with smooth color transition from green to black
    green_value = int(255 * progress)  # As progress decreases, green value decreases
    bar_color = (0, green_value, 0)  # Green fades to black

    pygame.draw.rect(
        screen,
        bar_color,
        (WIDTH // 2 - bar_width // 2, 100, int(bar_width * progress), bar_height),
    )

    # Draw current player indicator centered under the timer bar
    if not game_over:
        player_text = player_font.render(
            f"PLAYER {player}'S TURN",
            True,
            CROSS_COLOR if player == "X" else CIRCLE_COLOR,
        )
        screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, 810))

    return remaining <= 0


# Draw hover effect for current player
def draw_hover(row, col):
    if (
        0 <= row < BOARD_ROWS
        and 0 <= col < BOARD_COLS
        and board[row][col] is None
        and not game_over
    ):
        cell_x = BOARD_OFFSET_X + col * SQUARE_SIZE
        cell_y = BOARD_OFFSET_Y + row * SQUARE_SIZE

        # Create a transparent surface for the hover effect
        hover_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        hover_surface.fill(HOVER_COLOR)
        screen.blit(hover_surface, (cell_x, cell_y))

        # Draw a preview of the current player's mark
        center_x = cell_x + SQUARE_SIZE // 2
        center_y = cell_y + SQUARE_SIZE // 2

        if player == "X":
            # Draw a faint preview X
            preview_color = (0, 150, 0, 100)
            pygame.draw.line(
                screen,
                preview_color,
                (center_x - SPACE // 2, center_y - SPACE // 2),
                (center_x + SPACE // 2, center_y + SPACE // 2),
                CROSS_WIDTH // 2,
            )
            pygame.draw.line(
                screen,
                preview_color,
                (center_x + SPACE // 2, center_y - SPACE // 2),
                (center_x - SPACE // 2, center_y + SPACE // 2),
                CROSS_WIDTH // 2,
            )
        else:
            # Draw a faint preview O
            preview_color = (0, 150, 150, 100)
            pygame.draw.circle(
                screen,
                preview_color,
                (center_x, center_y),
                CIRCLE_RADIUS // 1.5,
                CIRCLE_WIDTH // 2,
            )


# Draw winning line with animation
def draw_winning_effect(winning_cells):
    if winning_cells:
        # Time-based animation
        pulse = (math.sin(time.time() * 10) + 1) / 2  # Value between 0 and 1
        thickness = int(10 + pulse * 10)
        brightness = int(200 + pulse * 55)

        # Draw glowing cells for winning line
        for row, col in winning_cells:
            cell_x = BOARD_OFFSET_X + col * SQUARE_SIZE
            cell_y = BOARD_OFFSET_Y + row * SQUARE_SIZE

            # Create pulsing highlight effect
            highlight_surface = pygame.Surface(
                (SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA
            )
            highlight_color = (0, brightness, 0, 100 + int(pulse * 100))
            highlight_surface.fill(highlight_color)
            screen.blit(highlight_surface, (cell_x, cell_y))

            # Draw cell border with enhanced effect
            for i in range(thickness):
                alpha = 255 - i * 10
                if alpha < 0:
                    alpha = 0
                border_color = (0, brightness, 0, alpha)
                pygame.draw.rect(
                    screen,
                    border_color,
                    (cell_x - i, cell_y - i, SQUARE_SIZE + i * 2, SQUARE_SIZE + i * 2),
                    1,
                )

                # Connect the winning cells with a line
            if len(winning_cells) >= 2:
                start_row, start_col = winning_cells[0]
                end_row, end_col = winning_cells[-1]

                start_x = BOARD_OFFSET_X + start_col * SQUARE_SIZE + SQUARE_SIZE // 2
                start_y = BOARD_OFFSET_Y + start_row * SQUARE_SIZE + SQUARE_SIZE // 2
                end_x = BOARD_OFFSET_X + end_col * SQUARE_SIZE + SQUARE_SIZE // 2
                end_y = BOARD_OFFSET_Y + end_row * SQUARE_SIZE + SQUARE_SIZE // 2

                # Draw pulsing line connecting winning cells
                pulse_width = int(5 + pulse * 10)
                pygame.draw.line(
                    screen,
                    (0, brightness, brightness),
                    (start_x, start_y),
                    (end_x, end_y),
                    pulse_width,
                )

                # Add particle effects along the winning line
                particles = 20
                for i in range(particles):
                    # Position along the line
                    t = i / particles
                    particle_x = start_x + (end_x - start_x) * t
                    particle_y = start_y + (end_y - start_y) * t

                    # Size based on pulse
                    particle_size = int(3 + pulse * 5)

                    # Draw particle
                    pygame.draw.circle(
                        screen,
                        (0, 255, 255),
                        (int(particle_x), int(particle_y)),
                        particle_size,
                    )


# Draw game over screen
def draw_game_over():
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(GAME_OVER_BG)
    screen.blit(overlay, (0, 0))

    # Draw winner message
    if winner == "Tie":
        text = "DRAW"
    elif winner == "Timeout":
        text = f"PLAYER {player} TIMED OUT"  # Show which player timed out
    else:
        text = f"PLAYER {winner} WINS"

    # Create glowing text effect
    glow_offset = int((time.time() * 5) % 50)
    glow_color = (0, 200 + glow_offset, 0)

    game_over_text = game_over_font.render(text, True, glow_color)
    screen.blit(
        game_over_text,
        (
            WIDTH // 2 - game_over_text.get_width() // 2,
            HEIGHT * 0.7,  # Move to 70% down the screen instead of centered
        ),
    )

    # Restart instruction
    restart_text = matrix_font.render("PRESS 'R' TO RESTART SYSTEM", True, TIMER_COLOR)
    screen.blit(
        restart_text,
        (
            WIDTH // 2 - restart_text.get_width() // 2,
            HEIGHT * 0.7 + game_over_text.get_height() + 20,
        ),
    )

    # Additional visual effects for game over
    # Radial pulse from center
    pulse_radius = int(500 + 100 * math.sin(time.time() * 5))
    pulse_width = int(5 + 3 * math.sin(time.time() * 10))
    pygame.draw.circle(
        screen, glow_color, (WIDTH // 2, HEIGHT // 2), pulse_radius, pulse_width
    )

    # Digital artifacts
    for _ in range(10):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        width = random.randint(5, 30)
        height = random.randint(2, 10)

        # Draw digital glitch rectangles
        glitch_color = (
            0,
            random.randint(150, 255),
            random.randint(100, 200),
            random.randint(50, 150),
        )
        glitch_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        glitch_surface.fill(glitch_color)
        screen.blit(glitch_surface, (x, y))


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Reset game
                board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
                player = "X"
                game_over = False
                winner = None
                winning_line = None
                start_time = time.time()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouseX, mouseY = pygame.mouse.get_pos()

            # Check if click is within board boundaries
            if (
                BOARD_OFFSET_X <= mouseX <= BOARD_OFFSET_X + 3 * SQUARE_SIZE
                and BOARD_OFFSET_Y <= mouseY <= BOARD_OFFSET_Y + 3 * SQUARE_SIZE
            ):

                # Convert mouse position to board indices
                col = (mouseX - BOARD_OFFSET_X) // SQUARE_SIZE
                row = (mouseY - BOARD_OFFSET_Y) // SQUARE_SIZE

                # Make a move if the cell is empty
                if board[row][col] is None:
                    board[row][col] = player

                    # Check for win
                    result, cells = check_win()
                    if result:
                        winner = result
                        winning_line = cells
                        game_over = True

                    # Switch player and reset timer
                    player = "O" if player == "X" else "X"
                    start_time = time.time()  # Reset timer for next player

    # Fill the screen with the background color
    screen.fill(BG_COLOR)

    # Update and draw matrix rain
    matrix_rain.update()
    matrix_rain.draw(screen)

    # Draw board
    draw_board()
    draw_figures()

    # Draw winning effect if there is a winner (except for ties)
    if game_over and winner != "Tie" and winner != "Timeout" and winning_line:
        draw_winning_effect(winning_line)

    # Draw hover effect for the current cell
    if not game_over:
        mouseX, mouseY = pygame.mouse.get_pos()
        if (
            BOARD_OFFSET_X <= mouseX <= BOARD_OFFSET_X + 3 * SQUARE_SIZE
            and BOARD_OFFSET_Y <= mouseY <= BOARD_OFFSET_Y + 3 * SQUARE_SIZE
        ):

            col = (mouseX - BOARD_OFFSET_X) // SQUARE_SIZE
            row = (mouseY - BOARD_OFFSET_Y) // SQUARE_SIZE
            draw_hover(row, col)

    # Check timer
    if not game_over and draw_timer():
        game_over = True
        winner = "Timeout"
    else:
        draw_timer()  # Still draw the timer if not game over

    # Draw game over screen if the game is over
    if game_over:
        draw_game_over()

    # Draw title
    title_text = matrix_font.render("TIC TAC TOE", True, LINE_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

    # Update the display
    pygame.display.flip()
    clock.tick(60)
