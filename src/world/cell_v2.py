import math
from collections import namedtuple

import pygame

from algorithm.brain import Brain
from commons.functions import euclidian_distance
from commons.settings import WindowSettings, UP, DOWN, LEFT, RIGHT, font, Location, Colors
from numpy.random import uniform, randint

DNA = namedtuple("DNA", [
    "color",
    "size",
    "speed",
    "vision_range",
])

State = namedtuple("State", [
    "health"
])

vec = pygame.math.Vector2

WIDTH = WindowSettings.WIDTH
HEIGHT = WindowSettings.HEIGHT
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)

# Mob properties
MAX_FORCE = 0.1


class Mob(pygame.sprite.Sprite):
    def __init__(self, screen, name: str, brain: Brain):
        pygame.sprite.Sprite.__init__(self)

        self.DNA = DNA(
            color=(uniform(2, 255), uniform(2, 255), uniform(2, 255)),
            size=32,
            speed=1,
            vision_range=200,
        )

        self.STATE = State(
            health=100,
        )

        self.LOCATION = Location(
            x=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.WIDTH - WindowSettings.MARGIN),
            y=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.HEIGHT - WindowSettings.MARGIN),
        )

        self.image = pygame.Surface((self.DNA.size, self.DNA.size))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.pos = vec(self.LOCATION.x + self.DNA.size/2, self.LOCATION.y + self.DNA.size/2)
        self.vel = vec(self.DNA.speed, 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.screen = screen
        self.desired = None
        self.name = name
        self.brain = brain
        self.brain.fitness = 0

    def seek_with_approach(self, target):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < self.DNA.vision_range:
            self.desired *= dist / self.DNA.speed * self.DNA.speed
        else:
            self.desired *= self.DNA.speed
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def update(self, target):
        for action in target:
            self.acc = self.seek_with_approach(action)
            # equations of motion
            self.vel += self.acc
            if self.vel.length() > self.DNA.speed:
                self.vel.scale_to_length(self.DNA.speed)
            self.pos += self.vel
            if self.pos.x > WIDTH:
                self.pos.x = 0
            if self.pos.x < 0:
                self.pos.x = WIDTH
            if self.pos.y > HEIGHT:
                self.pos.y = 0
            if self.pos.y < 0:
                self.pos.y = HEIGHT
            self.rect.center = self.pos
            self.update_location(x=self.pos[0], y=self.pos[1])

    def render(self):
        self.screen.blit(self.image, self.pos)
        if self.desired:
            scale = 25
            # vel
            pygame.draw.line(self.screen, GREEN, self.pos, (self.pos + self.vel * scale), 5)
            # desired
            pygame.draw.line(self.screen, RED, self.pos, (self.pos + self.desired * scale), 5)
            # approach radius
            pygame.draw.circle(self.screen, Colors.GREEN, self.pos, self.DNA.vision_range, 1)

    def think(self, inputs):
        return list(inputs.LOCATION)

    def update_health(self, health):
        self.STATE = State(health=min(round(self.STATE.health + health, 2), 100))

    def update_fitness(self, fitness):
        self.brain.fitness = self.brain.fitness + fitness

    def update_location(self, **kwargs):
        self.LOCATION = self.LOCATION._replace(**kwargs)