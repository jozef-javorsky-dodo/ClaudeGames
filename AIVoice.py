import pygame
import math
import random
from pygame import gfxdraw

# Initialize pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futuristic AI Voice Interface")

# Colors
DARK_BG = (10, 15, 25)
GLOW_COLOR = (0, 200, 255)
GLOW_COLOR_DIM = (0, 100, 127)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)


# Particles class for the voice visualization
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(0.5, 2)
        self.life = random.uniform(50, 100)
        self.max_life = self.life
        self.angle = random.uniform(0, math.pi * 2)
        self.distance = random.uniform(50, 150)
        self.target_x = x + math.cos(self.angle) * self.distance
        self.target_y = y + math.sin(self.angle) * self.distance

    def update(self, activated):
        if activated:
            self.life -= 1
            progress = 1 - (self.life / self.max_life)
            self.x = self.x + (self.target_x - self.x) * self.speed * 0.01
            self.y = self.y + (self.target_y - self.y) * self.speed * 0.01

    def draw(self, surface, activated):
        alpha = int(255 * (self.life / self.max_life)) if activated else 50
        color = GLOW_COLOR if activated else GLOW_COLOR_DIM
        surf = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            (*color, alpha),
            (int(self.size * 2), int(self.size * 2)),
            int(self.size),
        )
        surface.blit(surf, (int(self.x - self.size * 2), int(self.y - self.size * 2)))

    def is_dead(self):
        return self.life <= 0


# Voice waves class
class VoiceWave:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius + random.uniform(30, 70)
        self.speed = random.uniform(1, 2)
        self.alpha = 255

    def update(self):
        self.radius += self.speed
        self.alpha -= 5

    def draw(self, surface):
        if self.alpha > 0:
            pygame.gfxdraw.aacircle(
                surface,
                int(self.x),
                int(self.y),
                int(self.radius),
                (*GLOW_COLOR, self.alpha),
            )

    def is_dead(self):
        return self.alpha <= 0 or self.radius >= self.max_radius


# Microphone class
class Microphone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.inner_radius = 15
        self.activated = False
        self.pulse = 0
        self.particles = []
        self.waves = []
        self.lines = []
        self.generate_lines()

    def generate_lines(self):
        for i in range(12):
            angle = (i / 12) * math.pi * 2
            length = random.uniform(40, 80)
            self.lines.append(
                {
                    "angle": angle,
                    "length": length,
                    "speed": random.uniform(0.01, 0.05),
                    "offset": random.uniform(0, math.pi * 2),
                }
            )

    def toggle(self):
        self.activated = not self.activated
        if self.activated:
            self.generate_particles()

    def generate_particles(self):
        for _ in range(20):
            self.particles.append(Particle(self.x, self.y))

    def generate_wave(self):
        if self.activated and random.random() < 0.1:
            self.waves.append(VoiceWave(self.x, self.y, self.radius + 5))

    def update(self):
        self.pulse = (self.pulse + 0.05) % (math.pi * 2)

        # Update particles
        for particle in self.particles[:]:
            particle.update(self.activated)
            if particle.is_dead():
                self.particles.remove(particle)
                if self.activated:
                    self.particles.append(Particle(self.x, self.y))

        # Update waves
        for wave in self.waves[:]:
            wave.update()
            if wave.is_dead():
                self.waves.remove(wave)

        # Generate new wave
        self.generate_wave()

    def draw(self, surface):
        # Draw background lines
        for line in self.lines:
            angle = (
                line["angle"]
                + math.sin(self.pulse * line["speed"] + line["offset"]) * 0.2
            )
            end_x = self.x + math.cos(angle) * line["length"]
            end_y = self.y + math.sin(angle) * line["length"]
            alpha = 100 if self.activated else 50
            pygame.draw.line(
                surface, (*GLOW_COLOR, alpha), (self.x, self.y), (end_x, end_y), 1
            )

        # Draw waves
        for wave in self.waves:
            wave.draw(surface)

        # Draw particles
        for particle in self.particles:
            particle.draw(surface, self.activated)

        # Draw outer circle
        glow_size = 2 + math.sin(self.pulse) * (2 if self.activated else 0.5)
        color = GLOW_COLOR if self.activated else GLOW_COLOR_DIM

        # Outer glow
        for i in range(3):
            size = self.radius + i * 2
            alpha = 100 - i * 30
            if self.activated:
                alpha += 50
            pygame.gfxdraw.aacircle(
                surface, int(self.x), int(self.y), int(size), (*color, alpha)
            )

        # Main circle
        pygame.draw.circle(surface, DARK_BG, (int(self.x), int(self.y)), self.radius)
        pygame.gfxdraw.aacircle(surface, int(self.x), int(self.y), self.radius, color)

        # Inner circle
        if self.activated:
            pulse_radius = self.inner_radius + math.sin(self.pulse) * 3
            pygame.draw.circle(
                surface, color, (int(self.x), int(self.y)), int(pulse_radius)
            )
        else:
            pygame.draw.circle(
                surface, GRAY, (int(self.x), int(self.y)), self.inner_radius
            )
            pygame.gfxdraw.aacircle(
                surface, int(self.x), int(self.y), self.inner_radius, WHITE
            )

    def is_clicked(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx * dx + dy * dy <= self.radius * self.radius


# Main function
def main():
    clock = pygame.time.Clock()
    running = True

    # Create microphone at center of screen
    mic = Microphone(WIDTH // 2, HEIGHT // 2)

    # Font for text
    font = pygame.font.SysFont(None, 24)

    while running:
        screen.fill(DARK_BG)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mic.is_clicked(event.pos):
                    mic.toggle()

        # Update and draw microphone
        mic.update()
        mic.draw(screen)

        # Draw instruction text
        if not mic.activated:
            text = font.render("Click the microphone to activate", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 50))
        else:
            text = font.render("AI Voice Interface Active", True, GLOW_COLOR)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
