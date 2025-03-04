import pygame
import numpy as np
import random
import math
from pygame import gfxdraw

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 1000
FPS = 60

# Matrix-themed colors
BACKGROUND = (0, 10, 0)
NODE_COLOR = (0, 255, 0)
EDGE_COLOR = (0, 180, 50)
TEXT_COLOR = (0, 255, 100)
HIGHLIGHT_COLOR = (200, 255, 220)
MATRIX_GREEN = (0, 255, 60)
DARK_GREEN = (0, 100, 30)

# Transformer Parameters
TOKEN_COUNT = 8
ATTENTION_HEADS = 4
LAYERS = 3
TOKEN_EMBEDDING_SIZE = 64
MATRIX_CHARACTERS = "01"


class MatrixCode:
    def __init__(self):
        self.streams = []
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(-500, 0)
            speed = random.uniform(5, 15)
            length = random.randint(5, 20)
            self.streams.append(
                {
                    "x": x,
                    "y": y,
                    "speed": speed,
                    "length": length,
                    "chars": [random.choice(MATRIX_CHARACTERS) for _ in range(length)],
                    "intensities": [random.random() for _ in range(length)],
                }
            )

    def update(self):
        for stream in self.streams:
            stream["y"] += stream["speed"]

            # Reset stream if it goes off screen
            if stream["y"] > HEIGHT + stream["length"] * 20:
                stream["y"] = random.randint(-200, 0)
                stream["x"] = random.randint(0, WIDTH)

            # Randomly change characters
            if random.random() < 0.1:
                for i in range(len(stream["chars"])):
                    if random.random() < 0.3:
                        stream["chars"][i] = random.choice(MATRIX_CHARACTERS)

            # Update character intensities
            for i in range(len(stream["intensities"])):
                if random.random() < 0.1:
                    stream["intensities"][i] = random.random()

    def draw(self, screen):
        for stream in self.streams:
            for i in range(stream["length"]):
                y_pos = int(stream["y"] - i * 20)
                if 0 <= y_pos < HEIGHT:
                    intensity = stream["intensities"][i]
                    color = (0, int(100 + 155 * intensity), 0)
                    font = pygame.font.SysFont("monospace", 16)
                    char = font.render(stream["chars"][i], True, color)
                    screen.blit(char, (stream["x"], y_pos))


class Token:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.radius = 25
        self.activation = random.random()
        self.target_activation = random.random()
        self.embedding = np.random.rand(TOKEN_EMBEDDING_SIZE) * 2 - 1
        self.processed = False

    def update(self):
        # Smoothly transition activation level
        self.activation += (self.target_activation - self.activation) * 0.1

        # Occasionally change target activation for animation
        if random.random() < 0.05:
            self.target_activation = random.random()

    def draw(self, screen):
        # Draw token circle
        intensity = int(100 + 155 * self.activation)
        color = (0, intensity, int(intensity * 0.6))
        gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, color)
        gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, HIGHLIGHT_COLOR)

        # Draw token text
        font = pygame.font.SysFont("Arial", 14)
        text = font.render(self.text, True, TEXT_COLOR)
        screen.blit(
            text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2)
        )


class AttentionHead:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.attention_matrix = np.random.rand(TOKEN_COUNT, TOKEN_COUNT)
        self.normalize_attention()
        self.active = 0.0
        self.target_active = 0.0

    def normalize_attention(self):
        # Apply softmax to each row to make it a probability distribution
        for i in range(TOKEN_COUNT):
            row_exp = np.exp(self.attention_matrix[i])
            self.attention_matrix[i] = row_exp / np.sum(row_exp)

    def update(self):
        # Occasionally update attention patterns
        if random.random() < 0.03:
            # Create new random attention matrix
            new_matrix = np.random.rand(TOKEN_COUNT, TOKEN_COUNT)

            # Add diagonal bias for self-attention
            for i in range(TOKEN_COUNT):
                new_matrix[i, i] += 1.0

            # Add local context bias
            for i in range(TOKEN_COUNT):
                for j in range(TOKEN_COUNT):
                    dist = abs(i - j)
                    if dist <= 2:
                        new_matrix[i, j] += (3 - dist) / 3

            # Blend old and new matrices
            self.attention_matrix = 0.7 * self.attention_matrix + 0.3 * new_matrix
            self.normalize_attention()

        # Update activation
        self.active += (self.target_active - self.active) * 0.1
        if random.random() < 0.02:
            self.target_active = random.random()

    def draw(self, screen):
        cell_size = self.size / TOKEN_COUNT

        # Draw attention matrix cells
        for i in range(TOKEN_COUNT):
            for j in range(TOKEN_COUNT):
                x = self.x + j * cell_size
                y = self.y + i * cell_size
                intensity = int(self.attention_matrix[i, j] * 255)
                color = (0, intensity, int(intensity * 0.5))

                pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))
                pygame.draw.rect(screen, DARK_GREEN, (x, y, cell_size, cell_size), 1)

        # Draw border
        pygame.draw.rect(
            screen, MATRIX_GREEN, (self.x, self.y, self.size, self.size), 2
        )


class TransformerLayer:
    def __init__(self, y, layer_index):
        self.y = y
        self.layer_index = layer_index
        self.attention_heads = []
        self.head_size = 150

        # Create attention heads horizontally
        for i in range(ATTENTION_HEADS):
            x = 200 + i * (self.head_size + 20)
            self.attention_heads.append(AttentionHead(x, y, self.head_size))

        self.pulses = []
        self.processed = False
        self.processing_time = 0

    def update(self):
        # Update attention heads
        for head in self.attention_heads:
            head.update()

        # Update processing animation
        if not self.processed:
            self.processing_time += 1
            if self.processing_time > 60:  # Process for 1 second
                self.processed = True

        # Update pulses
        for pulse in self.pulses[:]:
            pulse["progress"] += 0.02
            if pulse["progress"] >= 1.0:
                self.pulses.remove(pulse)

        # Occasionally send pulses to next layer
        if self.processed and random.random() < 0.05:
            self.pulses.append(
                {
                    "from_x": 200
                    + random.randint(0, ATTENTION_HEADS - 1) * (self.head_size + 20)
                    + self.head_size / 2,
                    "from_y": self.y + self.head_size / 2,
                    "to_y": self.y + 150,
                    "progress": 0.0,
                }
            )

    def draw(self, screen):
        # Draw layer label
        font = pygame.font.SysFont("Arial", 18)
        text = font.render(f"Transformer Layer {self.layer_index+1}", True, TEXT_COLOR)
        screen.blit(text, (80, self.y + self.head_size / 2 - text.get_height() / 2))

        # Draw attention heads
        for head in self.attention_heads:
            head.draw(screen)

        # Draw attention mechanism label
        mechanism_font = pygame.font.SysFont("Arial", 14)
        for i, mechanism in enumerate(
            ["Self-Attention", "Multi-Head Attention", "Feed Forward", "Layer Norm"]
        ):
            text = mechanism_font.render(mechanism, True, TEXT_COLOR)
            x = 200 + i * (self.head_size + 20) + self.head_size / 2
            screen.blit(text, (x - text.get_width() / 2, self.y - 25))

        # Draw pulses
        for pulse in self.pulses:
            pulse_x = pulse["from_x"]
            pulse_y = (
                pulse["from_y"] + (pulse["to_y"] - pulse["from_y"]) * pulse["progress"]
            )

            # Draw pulse
            pulse_radius = 5
            opacity = int(255 * (1 - abs(pulse["progress"] - 0.5) * 2))
            color = (0, min(255, 100 + opacity), 0)
            gfxdraw.filled_circle(
                screen, int(pulse_x), int(pulse_y), pulse_radius, color
            )
            gfxdraw.aacircle(
                screen, int(pulse_x), int(pulse_y), pulse_radius, HIGHLIGHT_COLOR
            )


class LLMVisualizer:
    def __init__(self):
        self.tokens = []
        self.layers = []
        self.matrix_code = MatrixCode()
        self.setup_model()
        self.thoughts = []
        self.attention_message = "Attention is all you need"
        self.attention_opacity = 255
        self.attention_growing = False

    def setup_model(self):
        # Create input tokens
        token_texts = ["Attention", "is", "all", "you", "need", "for", "AGI", "!"]
        for i, text in enumerate(token_texts):
            x = 100 + (800 / (TOKEN_COUNT - 1)) * i
            y = 150
            self.tokens.append(Token(x, y, text))

        # Create transformer layers
        for i in range(LAYERS):
            y = 250 + i * 200
            self.layers.append(TransformerLayer(y, i))

    def update(self):
        # Update matrix code
        self.matrix_code.update()

        # Update tokens
        for token in self.tokens:
            token.update()

        # Update layers
        for layer in self.layers:
            layer.update()

        # Update thoughts
        if random.random() < 0.02:
            thought = random.choice(
                [
                    "Processing context...",
                    "Calculating attention scores...",
                    "Generating embeddings...",
                    "Transformer magic...",
                    "Self-attention active...",
                    "Contextual learning...",
                    "Probability distribution...",
                ]
            )
            self.thoughts.append(
                {
                    "text": thought,
                    "x": random.randint(100, WIDTH - 200),
                    "y": random.randint(50, HEIGHT - 100),
                    "opacity": 255,
                    "life": 120,  # 2 seconds at 60 FPS
                }
            )

        # Update existing thoughts
        for thought in self.thoughts[:]:
            thought["life"] -= 1
            thought["opacity"] = min(255, thought["life"] * 2)
            if thought["life"] <= 0:
                self.thoughts.remove(thought)

        # Animate "Attention is all you need" text
        if self.attention_growing:
            self.attention_opacity += 2
            if self.attention_opacity >= 255:
                self.attention_opacity = 255
                self.attention_growing = False
        else:
            self.attention_opacity -= 2
            if self.attention_opacity <= 150:
                self.attention_opacity = 150
                self.attention_growing = True

    def draw(self, screen):
        # Draw matrix code background
        self.matrix_code.draw(screen)

        # Draw title
        title_font = pygame.font.SysFont("Arial", 36)
        title = title_font.render("LLM Transformer Architecture", True, MATRIX_GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Draw "Attention is all you need" subtitle
        subtitle_font = pygame.font.SysFont("Arial", 28)
        color = (0, self.attention_opacity, int(self.attention_opacity * 0.5))
        subtitle = subtitle_font.render("ATTENTION IS ALL YOU NEED", True, color)
        subtitle_outline = subtitle_font.render(
            "ATTENTION IS ALL YOU NEED", True, DARK_GREEN
        )

        # Create subtle glow effect
        screen.blit(subtitle_outline, (WIDTH // 2 - subtitle.get_width() // 2 + 2, 68))
        screen.blit(subtitle_outline, (WIDTH // 2 - subtitle.get_width() // 2 - 2, 68))
        screen.blit(subtitle_outline, (WIDTH // 2 - subtitle.get_width() // 2, 68 + 2))
        screen.blit(subtitle_outline, (WIDTH // 2 - subtitle.get_width() // 2, 68 - 2))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 68))

        # Draw input tokens
        for token in self.tokens:
            token.draw(screen)

        # Draw connections between tokens
        for i in range(len(self.tokens) - 1):
            pygame.draw.line(
                screen,
                EDGE_COLOR,
                (self.tokens[i].x, self.tokens[i].y + 30),
                (self.tokens[i + 1].x, self.tokens[i + 1].y + 30),
                2,
            )

        # Draw transformer layers
        for layer in self.layers:
            layer.draw(screen)

        # Draw connections between layers
        for i in range(len(self.layers) - 1):
            for j in range(ATTENTION_HEADS):
                start_x = (
                    200
                    + j * (self.layers[i].head_size + 20)
                    + self.layers[i].head_size / 2
                )
                start_y = self.layers[i].y + self.layers[i].head_size
                end_x = (
                    200
                    + j * (self.layers[i + 1].head_size + 20)
                    + self.layers[i + 1].head_size / 2
                )
                end_y = self.layers[i + 1].y

                pygame.draw.line(
                    screen, EDGE_COLOR, (start_x, start_y), (end_x, end_y), 1
                )

        # Draw thoughts
        for thought in self.thoughts:
            thought_font = pygame.font.SysFont("Arial", 16)
            text = thought_font.render(
                thought["text"],
                True,
                (0, thought["opacity"], int(thought["opacity"] * 0.5)),
            )
            screen.blit(text, (thought["x"], thought["y"]))

        # Draw explanation
        explanation_font = pygame.font.SysFont("Arial", 14)
        explanations = [
            "LLMs are built on Transformer architecture",
            "Self-attention mechanism allows tokens to attend to each other",
            "Multiple attention heads capture different relationship patterns",
            "The core insight: 'Attention is all you need' - no recurrence required",
            "Each token processes information from all other tokens simultaneously",
            "This enables understanding of long-range dependencies in text",
        ]

        for i, exp in enumerate(explanations):
            text = explanation_font.render(exp, True, TEXT_COLOR)
            screen.blit(text, (WIDTH - text.get_width() - 20, HEIGHT - 150 + i * 20))

        # Draw status message
        status_font = pygame.font.SysFont("Arial", 16)
        status = status_font.render(
            "Towards AGI: Matrix-themed LLM visualization", True, MATRIX_GREEN
        )
        screen.blit(status, (20, HEIGHT - 30))


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("LLM Transformer Visualization | Matrix Theme")
    clock = pygame.time.Clock()

    llm_visualizer = LLMVisualizer()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        llm_visualizer.update()

        # Draw
        screen.fill(BACKGROUND)
        llm_visualizer.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
