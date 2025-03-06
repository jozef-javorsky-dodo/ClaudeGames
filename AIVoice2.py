import pygame
import math
import random
from pygame import gfxdraw
import numpy as np

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 500, 500
FPS = 60
BG_COLOR = (10, 12, 20)
ACCENT_COLOR = (0, 200, 255)
SECONDARY_COLOR = (255, 100, 200)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futuristic AI Voice Visualization")
clock = pygame.time.Clock()


# Particle class
class Particle:
    def __init__(self, x, y, angle, speed, size, color, life=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = size
        self.color = color
        self.alpha = 255
        self.life = life or random.randint(20, 60)
        self.age = 0

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.age += 1
        self.alpha = 255 * (1 - self.age / self.life)
        self.size -= self.size / self.life
        return self.age < self.life and self.size > 0.5

    def draw(self, surface):
        if self.alpha > 0:
            color = list(self.color) + [int(self.alpha)]
            gfxdraw.filled_circle(
                surface, int(self.x), int(self.y), int(self.size), color
            )


# Voice wave class
class VoiceWave:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius * 4
        self.color = color
        self.alpha = 255
        self.growing = True

    def update(self):
        if self.growing:
            self.radius += 2
            self.alpha = max(0, 255 * (1 - self.radius / self.max_radius))
            if self.radius >= self.max_radius:
                self.growing = False
                self.alpha = 0
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            color = list(self.color) + [int(self.alpha)]
            pygame.gfxdraw.aacircle(
                surface, int(self.x), int(self.y), int(self.radius), color
            )


# Initialize variables
particles = []
waves = []
center_x, center_y = WIDTH // 2, HEIGHT // 2
base_radius = 50
pulse_value = 0
is_active = False
activity_level = 0
wave_points = np.zeros(360)
last_spawn = 0


# Generate a color gradient
def get_gradient_color(percent, start_color, end_color):
    r = start_color[0] + (end_color[0] - start_color[0]) * percent
    g = start_color[1] + (end_color[1] - start_color[1]) * percent
    b = start_color[2] + (end_color[2] - start_color[2]) * percent
    return (int(r), int(g), int(b))


# Draw a wave circle
def draw_wave_circle(surface, x, y, radius, points, color, width=2):
    prev_pos = None
    for i in range(360):
        angle = math.radians(i)
        wave_radius = radius + points[i]
        pos_x = x + math.cos(angle) * wave_radius
        pos_y = y + math.sin(angle) * wave_radius
        if prev_pos:
            pygame.draw.line(surface, color, prev_pos, (pos_x, pos_y), width)
        prev_pos = (pos_x, pos_y)

    # Connect the last point to the first
    angle = math.radians(0)
    wave_radius = radius + points[0]
    first_pos = (x + math.cos(angle) * wave_radius, y + math.sin(angle) * wave_radius)
    pygame.draw.line(surface, color, prev_pos, first_pos, width)


# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            is_active = True
            activity_level = min(1.0, activity_level + 0.2)
        elif event.type == pygame.MOUSEBUTTONUP:
            is_active = False

    # Clear the screen
    screen.fill(BG_COLOR)

    # Update pulse value
    pulse_value = (pulse_value + 0.05) % (2 * math.pi)
    pulse_factor = (math.sin(pulse_value) + 1) * 0.5

    # Adjust activity level
    if is_active:
        activity_level = min(1.0, activity_level + 0.01)
    else:
        activity_level = max(0.0, activity_level - 0.02)

    # Update wave points
    for i in range(360):
        # Create a smooth base wave
        wave_points[i] *= 0.9
        if activity_level > 0:
            # Add random fluctuations based on activity level
            if random.random() < activity_level * 0.2:
                wave_points[i] += random.uniform(0, 15 * activity_level)

    # Spawn particles
    current_time = pygame.time.get_ticks()
    if is_active and current_time - last_spawn > 50:
        for _ in range(int(5 * activity_level)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3) * activity_level
            size = random.uniform(2, 5)

            # Use gradient color based on angle
            percent = (math.cos(angle) + 1) * 0.5
            color = get_gradient_color(percent, ACCENT_COLOR, SECONDARY_COLOR)

            particles.append(Particle(center_x, center_y, angle, speed, size, color))
        last_spawn = current_time

        # Add wave circles occasionally
        if random.random() < 0.2 * activity_level:
            waves.append(VoiceWave(center_x, center_y, base_radius, ACCENT_COLOR))

    # Update and draw particles
    particles = [p for p in particles if p.update()]
    for particle in particles:
        particle.draw(screen)

    # Update and draw waves
    waves = [w for w in waves if w.update()]
    for wave in waves:
        wave.draw(screen)

    # Calculate current radius with pulse effect
    current_radius = base_radius + pulse_factor * 5 + activity_level * 10

    # Draw outer gradient circles
    for i in range(5, 0, -1):
        size_factor = i / 5
        alpha = int(100 * size_factor * (0.5 + activity_level * 0.5))
        outer_radius = current_radius + 20 * size_factor
        outer_color = get_gradient_color(size_factor, ACCENT_COLOR, SECONDARY_COLOR)
        outer_color = outer_color + (alpha,)
        pygame.gfxdraw.aacircle(
            screen, center_x, center_y, int(outer_radius), outer_color
        )

    # Draw the wave circle
    draw_wave_circle(
        screen, center_x, center_y, current_radius, wave_points, ACCENT_COLOR
    )

    # Draw inner circle (microphone)
    inner_radius = int(current_radius * 0.7)
    # Draw gradient fill for inner circle
    for r in range(inner_radius, 0, -1):
        percent = r / inner_radius
        color = get_gradient_color(percent, ACCENT_COLOR, SECONDARY_COLOR)
        alpha = int(150 + 105 * pulse_factor * activity_level)
        color = color + (alpha,)
        pygame.gfxdraw.aacircle(screen, center_x, center_y, r, color)

    # Draw center dot
    center_size = 5 + pulse_factor * 3 + activity_level * 5
    pygame.draw.circle(screen, SECONDARY_COLOR, (center_x, center_y), center_size)

    # Draw text
    if activity_level > 0:
        font = pygame.font.SysFont(None, 24)
        alpha = int(255 * activity_level)
        text_surface = font.render("AI LISTENING...", True, ACCENT_COLOR + (alpha,))
        text_rect = text_surface.get_rect(
            center=(center_x, center_y + current_radius + 40)
        )
        screen.blit(text_surface, text_rect)

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
