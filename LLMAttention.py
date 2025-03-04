import pygame
import pygame.gfxdraw
import numpy as np
import random
import sys
import math
from pygame import font

# Initialize pygame
pygame.init()
font.init()

# Constants
WIDTH, HEIGHT = 500, 500
BACKGROUND = (10, 20, 10)
GREEN_LIGHT = (120, 230, 120)
GREEN_MID = (40, 180, 40)
GREEN_DARK = (20, 80, 20)
TEXT_COLOR = (220, 255, 220)
TOKEN_RADIUS = 18
ATTENTION_STRENGTH_MAX = 4

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Attention is All You Need - LLM Visualizer")
clock = pygame.time.Clock()

# Fonts
small_font = pygame.font.SysFont("monospace", 14)
medium_font = pygame.font.SysFont("monospace", 18)
large_font = pygame.font.SysFont("monospace", 24)


class Token:
    def __init__(self, value, position, index):
        self.value = value
        self.position = position
        self.index = index
        self.attention_scores = {}
        self.highlight = 0
        self.active = False

    def draw(self, surface):
        # Draw token circle
        color = GREEN_MID
        if self.active:
            color = GREEN_LIGHT
            # Glow effect for active token
            for i in range(5, 0, -1):
                alpha = 100 - i * 20
                radius = TOKEN_RADIUS + i * 2
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*GREEN_LIGHT, alpha), (radius, radius), radius)
                surface.blit(s, (self.position[0] - radius, self.position[1] - radius))

        pygame.draw.circle(surface, color, self.position, TOKEN_RADIUS)
        pygame.draw.circle(surface, GREEN_DARK, self.position, TOKEN_RADIUS, 2)

        # Draw token text
        text = small_font.render(self.value, True, TEXT_COLOR)
        text_rect = text.get_rect(center=self.position)
        surface.blit(text, text_rect)


class AttentionVisualizer:
    def __init__(self):
        self.tokens = []
        self.token_values = [
            "[START]",
            "the",
            "quick",
            "brown",
            "fox",
            "jumps",
            "over",
            "lazy",
            "dog",
            "[END]",
        ]
        self.token_positions = []
        self.active_token_index = -1
        self.generate_positions()
        self.create_tokens()
        self.generate_attention_scores()
        self.next_token = ""
        self.next_token_timer = 0
        self.generation_phase = False
        self.generated_tokens = []
        self.frames_since_last_update = 0

    def generate_positions(self):
        # Create a semi-circle arrangement for input tokens
        num_tokens = len(self.token_values)
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        radius = 180

        for i in range(num_tokens):
            angle = math.pi * (0.8 + 0.4 * i / (num_tokens - 1))
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.token_positions.append((x, y))

    def create_tokens(self):
        for i, value in enumerate(self.token_values):
            token = Token(value, self.token_positions[i], i)
            self.tokens.append(token)

    def generate_attention_scores(self):
        # Create realistic attention patterns
        for i, token in enumerate(self.tokens):
            for j, other_token in enumerate(self.tokens):
                # Tokens attend more to nearby tokens and related words
                distance = abs(i - j)
                if i == j:  # Self-attention is strong
                    score = 0.8 + random.random() * 0.2
                elif distance <= 2:  # Nearby tokens
                    score = 0.4 + random.random() * 0.4
                else:
                    score = random.random() * 0.3

                # Some token pairs have stronger relationships (like "the" -> "fox")
                if (i, j) in [(1, 4), (4, 5), (5, 6), (6, 8)]:
                    score += 0.3

                token.attention_scores[j] = score

    def draw_attention_lines(self, surface, from_token):
        # Draw attention lines from active token to others
        if from_token is None:
            return

        for to_token in self.tokens:
            if from_token == to_token:
                continue

            score = from_token.attention_scores.get(to_token.index, 0)
            if score > 0.05:
                # Calculate line thickness based on attention score
                thickness = int(score * ATTENTION_STRENGTH_MAX)

                # Create a surface for the line with transparency
                line_color = (*GREEN_LIGHT, int(score * 200))

                # Draw the line
                start_pos = from_token.position
                end_pos = to_token.position

                # Calculate perpendicular offset to create curved lines
                mid_x = (start_pos[0] + end_pos[0]) / 2
                mid_y = (start_pos[1] + end_pos[1]) / 2

                # Add slight curve to line
                curve = 30 * math.sin((from_token.index - to_token.index) * 0.5)
                control_point = (mid_x - curve, mid_y - curve)

                # Draw the curved line as a series of points
                points = []
                steps = 20
                for t in range(steps + 1):
                    t = t / steps
                    # Quadratic Bezier curve
                    x = (
                        (1 - t) ** 2 * start_pos[0]
                        + 2 * (1 - t) * t * control_point[0]
                        + t**2 * end_pos[0]
                    )
                    y = (
                        (1 - t) ** 2 * start_pos[1]
                        + 2 * (1 - t) * t * control_point[1]
                        + t**2 * end_pos[1]
                    )
                    points.append((x, y))

                # Draw the curved line
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        pygame.draw.line(
                            surface, line_color, points[i], points[i + 1], thickness
                        )

    def update(self):
        self.frames_since_last_update += 1

        # In reading phase, cycle through tokens to show attention
        if not self.generation_phase:
            if (
                self.frames_since_last_update >= 60
            ):  # Change active token every 60 frames
                self.frames_since_last_update = 0
                self.active_token_index = (self.active_token_index + 1) % len(
                    self.tokens
                )

                # After cycling through all tokens, start generation phase
                if self.active_token_index == 0 and len(self.generated_tokens) == 0:
                    self.generation_phase = True
                    self.active_token_index = -1
                    self.next_token_timer = 100

        # In generation phase, produce tokens one by one
        else:
            if self.next_token_timer > 0:
                self.next_token_timer -= 1

                # When timer expires, generate next token
                if self.next_token_timer == 0:
                    self.generate_next_token()

        # Update active state for tokens
        for i, token in enumerate(self.tokens):
            token.active = i == self.active_token_index

    def generate_next_token(self):
        # Simulate generating the next token
        generation_options = [
            "a",
            "smart",
            "computer",
            "learns",
            "to",
            "write",
            "text",
            "using",
            "attention",
            ".",
        ]

        if len(self.generated_tokens) < len(generation_options):
            self.next_token = generation_options[len(self.generated_tokens)]
            self.generated_tokens.append(self.next_token)

            # Calculate position for the new token
            token_y = HEIGHT - 100
            start_x = WIDTH / 2 - (len(generation_options) * 30) / 2
            token_x = start_x + len(self.generated_tokens) * 30

            # Create a new token for the UI but don't add to main tokens
            new_token = Token(self.next_token, (token_x, token_y), -1)
            new_token.active = True
            new_token.highlight = 20

            # Simulate attention from all input tokens to this new token
            self.active_token_index = random.randint(0, len(self.tokens) - 1)

            # Set timer for next token
            self.next_token_timer = 100
        else:
            # Reset to reading phase after generating all tokens
            self.generation_phase = False
            self.active_token_index = 0
            self.generated_tokens = []
            self.frames_since_last_update = 0

    def draw(self, surface):
        # Draw title
        title = large_font.render("Attention Is All You Need", True, TEXT_COLOR)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Draw subtitle based on current phase
        if not self.generation_phase:
            subtitle = medium_font.render(
                "Reading Phase: Building Attention", True, GREEN_LIGHT
            )
        else:
            subtitle = medium_font.render(
                "Generation Phase: Using Attention", True, GREEN_LIGHT
            )
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 50))

        # Draw active token's attention lines
        active_token = None
        if 0 <= self.active_token_index < len(self.tokens):
            active_token = self.tokens[self.active_token_index]
        self.draw_attention_lines(surface, active_token)

        # Draw all tokens
        for token in self.tokens:
            token.draw(surface)

        # Draw generated tokens
        if self.generated_tokens:
            # Draw a box for generated text
            box_width = min(400, len(self.generated_tokens) * 30 + 40)
            box_height = 60
            box_x = WIDTH // 2 - box_width // 2
            box_y = HEIGHT - 120

            # Draw box
            pygame.draw.rect(surface, GREEN_DARK, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(
                surface, GREEN_MID, (box_x, box_y, box_width, box_height), 2
            )

            # Draw generated text
            generated_text = " ".join(self.generated_tokens)
            text = medium_font.render(generated_text, True, TEXT_COLOR)
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))

            # Draw "Generated:" label
            label = small_font.render("Generated:", True, GREEN_LIGHT)
            surface.blit(label, (box_x + 10, box_y + 10))

        # Draw explanation text
        if not self.generation_phase:
            explanation = small_font.render(
                "Each token attends to others with varying strength", True, TEXT_COLOR
            )
            surface.blit(
                explanation, (WIDTH // 2 - explanation.get_width() // 2, HEIGHT - 40)
            )
        else:
            explanation = small_font.render(
                "Using attention patterns to generate new tokens", True, TEXT_COLOR
            )
            surface.blit(
                explanation, (WIDTH // 2 - explanation.get_width() // 2, HEIGHT - 40)
            )


def main():
    visualizer = AttentionVisualizer()
    running = True

    while running:
        screen.fill(BACKGROUND)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update and draw
        visualizer.update()
        visualizer.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
