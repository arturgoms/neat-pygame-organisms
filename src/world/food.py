import pygame
import pyxel
from numpy.random import uniform
from commons.settings import DefaultSettings, WindowSettings, Direction, Size, font, Location


class Food(pygame.sprite.Sprite):
    def __init__(self, screen, color, name, position: list = None):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("interface/assets/food.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.LOCATION = Location(
            x=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.WIDTH - WindowSettings.MARGIN),
            y=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.HEIGHT - WindowSettings.MARGIN),
        )
        if position:
            self.update_location(x=position[0], y=position[1])

        self.rect = self.image.get_rect(x=self.LOCATION.x, y=self.LOCATION.y)
        self.energy = 20
        self.color = color
        self.screen = screen
        self.name = str(name)

    def __repr__(self):
        return f"Food {self.name} - Position(x={self.LOCATION.x}, y={self.LOCATION.y})"

    def respawn(self):
        self.LOCATION = Location(
            x=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.WIDTH - WindowSettings.MARGIN),
            y=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.HEIGHT - WindowSettings.MARGIN))

    def label(self):
        return font.render(f"{self.name}", 0, (255, 255, 255))

    def render(self):
        self.screen.blit(self.image, [self.LOCATION.x, self.LOCATION.y])
        self.screen.blit(self.label(), (self.LOCATION.x + 35, self.LOCATION.y + 10))
        self.rect = self.image.get_rect()
        # pygame.draw.rect(self.screen, self.color, self.rect)

    def update_location(self, **kwargs):
        self.LOCATION = self.LOCATION._replace(**kwargs)