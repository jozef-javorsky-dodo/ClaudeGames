import pygame
import math
import random
from pygame import gfxdraw
import colorsys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futuristic AI Voice Visualization")

# Colors
BACKGROUND = (10, 15, 30)
PRIMARY = (0, 180, 255)
SECONDARY = (255, 100, 255)
TERTIARY = (50, 255, 180)


# Particle class for voice visualization
class VoiceParticle:
    def __init__(self, x, y, size, color, speed=1.0, decay=0.95):
        self.x = x
        self.y = y
        self.size = size
        self.original_size = size
        self.max_size = size * 4
        self.color = color
        self.alpha = 255
        self.growing = True
        self.speed = speed
        self.decay = decay
        self.angle = random.uniform(0, math.pi * 2)
        self.distance = random.uniform(0, 100)
        self.drift_speed = random.uniform(0.2, 1.0)

    def update(self):
        # Update size based on growth state
        if self.growing:
            self.size = min(self.size * 1.1, self.max_size)
            if self.size >= self.max_size * 0.95:
                self.growing = False
        else:
            self.size *= self.decay
            self.alpha *= self.decay

        # Add some drift motion
        self.x += math.cos(self.angle) * self.drift_speed
        self.y += math.sin(self.angle) * self.drift_speed

        # Adjust angle for orbital effect
        self.angle += 0.01 * self.speed

        return self.size > 0.5 and self.alpha > 10

    def draw(self, surface):
        # Calculate color with alpha
        color = (*self.color, int(self.alpha))
        # Draw with anti-aliasing using gfxdraw - using integer coordinates
        gfxdraw.filled_circle(
            surface, int(self.x), int(self.y), max(1, int(self.size)), color
        )
        gfxdraw.aacircle(
            surface,
            int(self.x),
            int(self.y),
            max(1, int(self.size)),
            (*self.color, 255),
        )


# Circular waveform visualizer
class CircularWaveform:
    def __init__(self, x, y, radius, color, segments=32):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.current_radius = radius
        self.color = color
        self.segments = segments
        self.amplitudes = [0] * segments
        self.target_amplitudes = [0] * segments
        self.phase = 0

    def update(self, intensity):
        # Update phase for rotation
        self.phase += 0.02

        # Generate new target amplitudes
        for i in range(self.segments):
            # Smoothly transition to new target values
            if random.random() < 0.05:
                self.target_amplitudes[i] = random.uniform(0, intensity * 30)

            # Move current amplitude toward target
            diff = self.target_amplitudes[i] - self.amplitudes[i]
            self.amplitudes[i] += diff * 0.1

    def draw(self, surface):
        points = []
        for i in range(self.segments):
            angle = 2 * math.pi * i / self.segments + self.phase
            # Calculate radius with amplitude variation
            radius = self.base_radius + self.amplitudes[i]
            x = self.x + radius * math.cos(angle)
            y = self.y + radius * math.sin(angle)
            points.append((int(x), int(y)))  # Convert to integers

        # Draw connecting lines with alpha gradient
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]

            # Create gradient color based on amplitude
            intensity = self.amplitudes[i] / 30
            color = (
                int(self.color[0] * (0.5 + 0.5 * intensity)),
                int(self.color[1] * (0.5 + 0.5 * intensity)),
                int(self.color[2] * (0.5 + 0.5 * intensity)),
            )

            pygame.draw.line(surface, color, start, end, 2)


# Neon glow effect
def draw_with_glow(surface, color, center, radius, glow_radius=20):
    # Convert parameters to integers
    center = (int(center[0]), int(center[1]))
    radius = int(radius)

    # Draw the main circle
    gfxdraw.filled_circle(surface, center[0], center[1], radius, color)
    gfxdraw.aacircle(surface, center[0], center[1], radius, color)

    # Draw glow layers
    for i in range(glow_radius, 0, -2):
        alpha = 100 * (i / glow_radius)
        gfxdraw.aacircle(
            surface, center[0], center[1], radius + i, (*color[:3], int(alpha))
        )


# Main microphone visualization
class AIVoiceVisualization:
    def __init__(self):
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.radius = 80
        self.outer_radius = 150
        self.active = False
        self.particles = []
        self.activity_level = 0
        self.pulse_size = 0
        self.waveform = CircularWaveform(
            self.center_x, self.center_y, 120, PRIMARY, segments=48
        )
        self.second_waveform = CircularWaveform(
            self.center_x, self.center_y, 180, SECONDARY, segments=36
        )
        self.outer_waveform = CircularWaveform(
            self.center_x, self.center_y, 220, TERTIARY, segments=64
        )
        self.orbit_particles = []
        self.time = 0

        # Create initial orbit particles
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(240, 280)
            speed = random.uniform(0.2, 0.8)
            size = random.uniform(2, 5)
            particle = {
                "angle": angle,
                "distance": distance,
                "speed": speed,
                "size": size,
                "color": self.get_random_color(bright=True),
            }
            self.orbit_particles.append(particle)

    def get_random_color(self, bright=False):
        h = random.uniform(0, 1)
        s = random.uniform(0.8, 1.0) if bright else random.uniform(0.5, 0.8)
        v = random.uniform(0.8, 1.0) if bright else random.uniform(0.6, 0.9)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def activate(self, intensity=1.0):
        self.active = True
        self.activity_level = min(1.0, self.activity_level + 0.2)
        self.pulse_size = min(30, self.pulse_size + 10)

        # Generate particles
        num_particles = int(random.randint(5, 15) * intensity)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(self.radius, self.radius * 1.5)
            x = self.center_x + math.cos(angle) * distance
            y = self.center_y + math.sin(angle) * distance
            size = random.uniform(2, 8) * intensity

            # Choose color based on position
            hue = (math.atan2(y - self.center_y, x - self.center_x) + math.pi) / (
                2 * math.pi
            )
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            color = (int(r * 255), int(g * 255), int(b * 255))

            particle = VoiceParticle(x, y, size, color, speed=random.uniform(0.5, 2.0))
            self.particles.append(particle)

    def update(self):
        self.time += 0.01

        # Update activity level
        if self.active:
            self.active = False
        else:
            self.activity_level *= 0.95
            self.pulse_size *= 0.9

        # Update particles
        self.particles = [p for p in self.particles if p.update()]

        # Update waveforms with current activity level
        self.waveform.update(self.activity_level)
        self.second_waveform.update(self.activity_level * 0.8)
        self.outer_waveform.update(self.activity_level * 0.6)

        # Update orbit particles
        for particle in self.orbit_particles:
            particle["angle"] += particle["speed"] * 0.01
            # Make orbits pulse with activity
            pulse = math.sin(self.time * 3) * 10 * self.activity_level
            particle["distance"] = particle["distance"] + pulse

    def draw(self, surface):
        # Create a transparent surface for better blending
        transparent = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Draw outer waveforms
        self.outer_waveform.draw(transparent)
        self.second_waveform.draw(transparent)
        self.waveform.draw(transparent)

        # Draw orbit particles
        for particle in self.orbit_particles:
            x = int(self.center_x + math.cos(particle["angle"]) * particle["distance"])
            y = int(self.center_y + math.sin(particle["angle"]) * particle["distance"])

            # Add trail effect
            trail_length = int(5 * particle["speed"])
            for i in range(trail_length):
                trail_angle = particle["angle"] - (i * 0.05)
                trail_x = int(
                    self.center_x + math.cos(trail_angle) * particle["distance"]
                )
                trail_y = int(
                    self.center_y + math.sin(trail_angle) * particle["distance"]
                )
                alpha = 200 * (1 - i / trail_length)
                # Use max(1, int()) to ensure we never pass a zero or negative radius
                pygame.draw.circle(
                    transparent,
                    (*particle["color"], int(alpha)),
                    (trail_x, trail_y),
                    max(1, int(particle["size"] * (1 - i / trail_length))),
                )

            # Draw the particle
            pygame.draw.circle(
                transparent, particle["color"], (x, y), max(1, int(particle["size"]))
            )

        # Draw center microphone with glow effect
        pulse_effect = self.activity_level * 20
        draw_with_glow(
            transparent,
            (*PRIMARY, 180),
            (self.center_x, self.center_y),
            self.radius + pulse_effect,
        )

        # Draw voice particles
        for particle in self.particles:
            particle.draw(transparent)

        # Draw pulse ring if active
        if self.pulse_size > 1:
            pygame.draw.circle(
                transparent,
                (*PRIMARY, 50),
                (self.center_x, self.center_y),
                int(self.radius + self.pulse_size),
                2,
            )

        # Add center detail
        pygame.draw.circle(
            transparent,
            (255, 255, 255, 200),
            (self.center_x, self.center_y),
            int(self.radius * 0.7),
        )

        # Add microphone icon
        mic_height = 40
        mic_width = 20
        mic_x = int(self.center_x - mic_width // 2)
        mic_y = int(self.center_y - mic_height // 2)

        # Draw microphone body
        pygame.draw.rect(
            transparent,
            (50, 50, 60, 220),
            (mic_x, mic_y, mic_width, mic_height),
            border_radius=10,
        )

        # Draw microphone grille
        grille_lines = 6
        for i in range(grille_lines):
            line_y = mic_y + 8 + i * 4
            pygame.draw.line(
                transparent,
                (30, 30, 35, 200),
                (mic_x + 3, line_y),
                (mic_x + mic_width - 3, line_y),
                2,
            )

        # Blit the transparent surface to the main screen
        surface.blit(transparent, (0, 0))


# Main game loop
def main():
    clock = pygame.time.Clock()
    running = True

    visualization = AIVoiceVisualization()
    font = pygame.font.SysFont(None, 24)
    last_click_time = 0

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Trigger voice animation on click
                visualization.activate(random.uniform(0.5, 1.0))
                last_click_time = current_time

        # Fill the background
        screen.fill(BACKGROUND)

        # Update and draw the visualization
        visualization.update()
        visualization.draw(screen)

        # Draw instruction text
        instruction = font.render(
            "Click anywhere to simulate AI voice activity", True, (200, 200, 220)
        )
        screen.blit(
            instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT - 40)
        )

        # Auto-trigger visualization occasionally if no recent clicks
        if current_time - last_click_time > 3000 and random.random() < 0.02:
            visualization.activate(random.uniform(0.3, 0.7))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
