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

# Colors (green aesthetic)
BACKGROUND = (10, 20, 15)
NODE_COLOR = (100, 255, 150)
EDGE_COLOR = (40, 180, 100)
TEXT_COLOR = (180, 255, 200)
HIGHLIGHT_COLOR = (200, 255, 220)

# Neural Network Parameters
INPUT_NEURONS = 5
HIDDEN_NEURONS = 8
OUTPUT_NEURONS = 3
TOTAL_NEURONS = INPUT_NEURONS + HIDDEN_NEURONS + OUTPUT_NEURONS


class Neuron:
    def __init__(self, x, y, layer_type):
        self.x = x
        self.y = y
        self.radius = 15
        self.layer_type = layer_type
        self.activation = random.random()
        self.target_activation = random.random()
        self.color = NODE_COLOR
        self.connections = []

    def update(self):
        # Smoothly transition activation level
        self.activation += (self.target_activation - self.activation) * 0.05

        # Occasionally change target activation for animation
        if random.random() < 0.02:
            self.target_activation = random.random()

    def draw(self, screen):
        # Draw neuron
        intensity = int(155 + 100 * self.activation)
        color = (
            int(100 * (1 - self.activation)),
            intensity,
            int(150 * (1 - self.activation) + 100),
        )
        gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, color)
        gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, HIGHLIGHT_COLOR)

        # Draw activation level inside neuron
        font = pygame.font.SysFont("Arial", 10)
        text = font.render(f"{self.activation:.1f}", True, TEXT_COLOR)
        screen.blit(
            text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2)
        )


class NeuralNetwork:
    def __init__(self):
        self.neurons = []
        self.connections = []
        self.setup_network()
        self.thought_bubbles = []
        self.messages = [
            "Processing data...",
            "Analyzing patterns...",
            "Learning from experience...",
            "Adjusting weights...",
            "Optimizing neural pathways...",
            "Recognizing features...",
            "Predicting outcomes...",
            "Generating insights...",
        ]
        self.current_message = random.choice(self.messages)
        self.message_timer = 0
        self.data_points = self.generate_data_points()
        self.thought_timer = 0

    def generate_data_points(self):
        points = []
        for _ in range(20):
            x = random.randint(50, WIDTH - 50)
            y = random.randint(HEIGHT - 200, HEIGHT - 50)
            color = (
                random.randint(40, 100),
                random.randint(150, 255),
                random.randint(100, 150),
            )
            speed = random.uniform(0.5, 2.0)
            points.append({"x": x, "y": y, "color": color, "speed": speed})
        return points

    def setup_network(self):
        # Create neurons for each layer
        # Input layer
        for i in range(INPUT_NEURONS):
            x = 200
            y = 300 + i * (400 / (INPUT_NEURONS - 1))
            self.neurons.append(Neuron(x, y, "input"))

        # Hidden layer
        for i in range(HIDDEN_NEURONS):
            x = 500
            y = 250 + i * (500 / (HIDDEN_NEURONS - 1))
            self.neurons.append(Neuron(x, y, "hidden"))

        # Output layer
        for i in range(OUTPUT_NEURONS):
            x = 800
            y = 300 + i * (400 / (OUTPUT_NEURONS - 1))
            self.neurons.append(Neuron(x, y, "output"))

        # Create connections
        # Input to hidden
        for i in range(INPUT_NEURONS):
            for j in range(HIDDEN_NEURONS):
                weight = random.uniform(0.1, 0.9)
                self.connections.append(
                    {"from": i, "to": INPUT_NEURONS + j, "weight": weight}
                )

        # Hidden to output
        for i in range(HIDDEN_NEURONS):
            for j in range(OUTPUT_NEURONS):
                weight = random.uniform(0.1, 0.9)
                self.connections.append(
                    {
                        "from": INPUT_NEURONS + i,
                        "to": INPUT_NEURONS + HIDDEN_NEURONS + j,
                        "weight": weight,
                    }
                )

    def update(self):
        # Update neurons
        for neuron in self.neurons:
            neuron.update()

        # Update connections (pulse animation)
        for conn in self.connections:
            if random.random() < 0.01:
                conn["active"] = 1.0
            else:
                conn["active"] = conn.get("active", 0) * 0.95

        # Update thought bubbles
        self.thought_timer += 1
        if self.thought_timer > 60 and random.random() < 0.05:
            self.thought_timer = 0
            self.thought_bubbles.append(
                {
                    "text": random.choice(
                        ["AGI", "LLM", "Neural Network", "Transformer", "Deep Learning"]
                    ),
                    "x": random.randint(300, 700),
                    "y": random.randint(100, 200),
                    "opacity": 255,
                    "size": random.randint(12, 24),
                }
            )

        # Update existing thought bubbles
        for bubble in self.thought_bubbles[:]:
            bubble["y"] -= 1
            bubble["opacity"] -= 2
            if bubble["opacity"] <= 0:
                self.thought_bubbles.remove(bubble)

        # Update message
        self.message_timer += 1
        if self.message_timer > 180:  # Change message every 3 seconds
            self.message_timer = 0
            self.current_message = random.choice(self.messages)

        # Update data points
        for point in self.data_points:
            point["y"] -= point["speed"]
            if point["y"] < 0:
                point["y"] = HEIGHT
                point["x"] = random.randint(50, WIDTH - 50)

    def draw(self, screen):
        # Draw connections
        for conn in self.connections:
            start_neuron = self.neurons[conn["from"]]
            end_neuron = self.neurons[conn["to"]]

            # Calculate connection color based on weight and activity
            activity = conn.get("active", 0)
            color = (
                int(EDGE_COLOR[0] * (1 - activity)),
                int(EDGE_COLOR[1] * (1 - activity) + activity * 255),
                int(EDGE_COLOR[2] * (1 - activity)),
            )

            width = 1 + int(3 * conn["weight"])
            if activity > 0.1:
                width += 2

            pygame.draw.line(
                screen,
                color,
                (start_neuron.x, start_neuron.y),
                (end_neuron.x, end_neuron.y),
                width,
            )

            # Draw data pulse traveling along active connections
            if activity > 0.1:
                pulse_pos = activity
                pulse_x = start_neuron.x + (end_neuron.x - start_neuron.x) * (
                    1 - pulse_pos
                )
                pulse_y = start_neuron.y + (end_neuron.y - start_neuron.y) * (
                    1 - pulse_pos
                )

                pulse_radius = 5
                gfxdraw.filled_circle(
                    screen, int(pulse_x), int(pulse_y), pulse_radius, HIGHLIGHT_COLOR
                )

        # Draw neurons
        for neuron in self.neurons:
            neuron.draw(screen)

        # Draw layer labels
        font = pygame.font.SysFont("Arial", 20)
        input_text = font.render("Input Layer", True, TEXT_COLOR)
        hidden_text = font.render("Hidden Layer", True, TEXT_COLOR)
        output_text = font.render("Output Layer", True, TEXT_COLOR)

        screen.blit(input_text, (200 - input_text.get_width() // 2, 250))
        screen.blit(hidden_text, (500 - hidden_text.get_width() // 2, 200))
        screen.blit(output_text, (800 - output_text.get_width() // 2, 250))

        # Draw data points
        for point in self.data_points:
            gfxdraw.filled_circle(
                screen, int(point["x"]), int(point["y"]), 4, point["color"]
            )
            gfxdraw.aacircle(
                screen, int(point["x"]), int(point["y"]), 4, point["color"]
            )

        # Draw thought bubbles
        for bubble in self.thought_bubbles:
            font = pygame.font.SysFont("Arial", bubble["size"])
            text = font.render(bubble["text"], True, (180, 255, 200, bubble["opacity"]))
            text.set_alpha(bubble["opacity"])
            screen.blit(text, (bubble["x"], bubble["y"]))

        # Draw title
        title_font = pygame.font.SysFont("Arial", 36)
        title = title_font.render("AI Neural Network Visualization", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Draw processing message
        message_font = pygame.font.SysFont("Arial", 24)
        message = message_font.render(self.current_message, True, TEXT_COLOR)
        screen.blit(message, (WIDTH // 2 - message.get_width() // 2, 100))

        # Draw LLM status in bottom corner
        llm_font = pygame.font.SysFont("Arial", 16)
        llm_status = llm_font.render(
            "LLM Status: Active | AGI Development: In Progress", True, TEXT_COLOR
        )
        screen.blit(llm_status, (20, HEIGHT - 30))


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Neural Network Visualization")
    clock = pygame.time.Clock()

    neural_network = NeuralNetwork()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        neural_network.update()

        # Draw
        screen.fill(BACKGROUND)
        neural_network.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
