import pygame
import sys
import random
import time
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BOX_WIDTH = 100
BOX_HEIGHT = 150
BOX_SPACING = 50
FONT_SIZE = 36
SMALL_FONT_SIZE = 24
LETTER_SPEED = 0.5  # Speed of scrolling letters (lower is faster)
GAME_TIME = 30  # Time limit in seconds
VISIBLE_LETTERS = 5  # Number of letters visible in the scrolling window

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MATRIX-AESTHETICS: Safe Cracking")

# Fonts
font = pygame.font.Font(None, FONT_SIZE)
small_font = pygame.font.Font(None, SMALL_FONT_SIZE)


class ScrollingLetters:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.letter_list = list(self.letters)
        random.shuffle(self.letter_list)
        self.position = 0
        self.last_update = time.time()
        self.letter_height = font.get_height()

    def update(self):
        current_time = time.time()
        if current_time - self.last_update > LETTER_SPEED:
            self.position += 1
            if self.position >= len(self.letter_list):
                self.position = 0
            self.last_update = current_time

    def draw(self, surface):
        # Draw a small window for the scrolling letters
        pygame.draw.rect(surface, DARK_GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.width, self.height), 2)

        # Draw the current letter in the center
        center_index = self.position
        current_letter = self.letter_list[center_index]
        text = font.render(current_letter, True, GREEN)
        text_rect = text.get_rect(
            center=(self.x + self.width // 2, self.y + self.height // 2)
        )
        surface.blit(text, text_rect)

        # Draw letters above and below
        for i in range(1, VISIBLE_LETTERS // 2 + 1):
            # Letters above
            above_index = (center_index - i) % len(self.letter_list)
            above_letter = self.letter_list[above_index]
            above_text = small_font.render(above_letter, True, DARK_GREEN)
            above_rect = above_text.get_rect(
                center=(
                    self.x + self.width // 2,
                    self.y + self.height // 2 - i * (self.letter_height * 0.8),
                )
            )
            surface.blit(above_text, above_rect)

            # Letters below
            below_index = (center_index + i) % len(self.letter_list)
            below_letter = self.letter_list[below_index]
            below_text = small_font.render(below_letter, True, DARK_GREEN)
            below_rect = below_text.get_rect(
                center=(
                    self.x + self.width // 2,
                    self.y + self.height // 2 + i * (self.letter_height * 0.8),
                )
            )
            surface.blit(below_text, below_rect)

    def get_current_letter(self):
        return self.letter_list[self.position]


def generate_code():
    return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=3))


def main():
    clock = pygame.time.Clock()

    # Game variables
    target_code = generate_code()
    attempts_left = 3
    current_box = 0
    selected_letters = ["", "", ""]
    box_states = [
        False,
        False,
        False,
    ]  # False = not selected, True = correctly selected

    # Calculate box positions
    total_width = 3 * BOX_WIDTH + 2 * BOX_SPACING
    start_x = (WIDTH - total_width) // 2
    box_positions = [
        (start_x, HEIGHT // 2 - BOX_HEIGHT // 2),
        (start_x + BOX_WIDTH + BOX_SPACING, HEIGHT // 2 - BOX_HEIGHT // 2),
        (start_x + 2 * (BOX_WIDTH + BOX_SPACING), HEIGHT // 2 - BOX_HEIGHT // 2),
    ]

    # Create scrolling letter displays
    scroll_height = font.get_height() * 3
    scrolling_letters = [
        ScrollingLetters(
            box_pos[0] + BOX_WIDTH // 2 - 25,
            box_pos[1] - scroll_height - 20,
            50,
            scroll_height,
        )
        for box_pos in box_positions
    ]

    game_start_time = time.time()
    game_over = False
    win = False

    # Main game loop
    while True:
        current_time = time.time()
        elapsed_time = current_time - game_start_time
        time_left = max(0, GAME_TIME - elapsed_time)

        # Check if time is up
        if time_left <= 0 and not game_over:
            attempts_left -= 1
            if attempts_left <= 0:
                game_over = True
            else:
                # Reset for next attempt
                target_code = generate_code()
                current_box = 0
                selected_letters = ["", "", ""]
                box_states = [False, False, False]
                game_start_time = time.time()

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == K_SPACE and not game_over and not win:
                    if not box_states[current_box]:
                        selected_letters[current_box] = scrolling_letters[
                            current_box
                        ].get_current_letter()
                        box_states[current_box] = (
                            selected_letters[current_box] == target_code[current_box]
                        )

                        current_box += 1

                        # Check if all boxes are filled
                        if current_box >= 3:
                            if all(box_states):
                                win = True
                            else:
                                attempts_left -= 1
                                if attempts_left <= 0:
                                    game_over = True
                                else:
                                    # Reset for next attempt
                                    target_code = generate_code()
                                    current_box = 0
                                    selected_letters = ["", "", ""]
                                    box_states = [False, False, False]
                                    game_start_time = time.time()

                # Restart game if game over or win
                if (game_over or win) and event.key == K_r:
                    target_code = generate_code()
                    attempts_left = 3
                    current_box = 0
                    selected_letters = ["", "", ""]
                    box_states = [False, False, False]
                    game_start_time = time.time()
                    game_over = False
                    win = False

        # Update scrolling letters
        for i, scroller in enumerate(scrolling_letters):
            if i == current_box and not box_states[i] and not game_over and not win:
                scroller.update()

        # Drawing
        screen.fill(BLACK)

        # Draw matrix-style background effect
        for i in range(20):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            text = small_font.render(random.choice("01"), True, DARK_GREEN)
            screen.blit(text, (x, y))

        # Draw scrolling letter displays
        for i, scroller in enumerate(scrolling_letters):
            if i == current_box and not box_states[i] and not game_over and not win:
                scroller.draw(screen)

        # Draw boxes
        for i, (x, y) in enumerate(box_positions):
            color = GREEN if box_states[i] else WHITE
            pygame.draw.rect(screen, color, (x, y, BOX_WIDTH, BOX_HEIGHT), 2)

            # Draw selected letter if any
            if selected_letters[i]:
                text = font.render(selected_letters[i], True, GREEN)
                text_rect = text.get_rect(
                    center=(x + BOX_WIDTH // 2, y + BOX_HEIGHT // 2)
                )
                screen.blit(text, text_rect)

            # Draw indicator for current box
            if i == current_box and not box_states[i] and not game_over and not win:
                indicator_text = small_font.render("ACTIVE", True, GREEN)
                screen.blit(
                    indicator_text,
                    (
                        x + BOX_WIDTH // 2 - indicator_text.get_width() // 2,
                        y + BOX_HEIGHT + 10,
                    ),
                )

        # Draw target code
        code_text = font.render(f"TARGET: {target_code}", True, GREEN)
        screen.blit(code_text, (WIDTH // 2 - code_text.get_width() // 2, 50))

        # Draw attempts and timer
        attempts_text = font.render(f"ATTEMPTS: {attempts_left}", True, GREEN)
        screen.blit(attempts_text, (50, 20))

        timer_text = font.render(f"TIME: {int(time_left)}", True, GREEN)
        screen.blit(timer_text, (WIDTH - timer_text.get_width() - 50, 20))

        # Draw game over or win message
        if game_over:
            message = font.render("ACCESS DENIED - PRESS R TO RETRY", True, RED)
            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT - 100))

        if win:
            message = font.render("ACCESS GRANTED - PRESS R TO PLAY AGAIN", True, GREEN)
            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT - 100))

        # Instructions
        instructions = small_font.render("Press SPACE to select a letter", True, WHITE)
        screen.blit(
            instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 50)
        )

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
