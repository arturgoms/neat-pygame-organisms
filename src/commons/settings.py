from collections import namedtuple
from itertools import cycle

import pygame

pygame.init()

Direction = namedtuple("Direction", ["x", "y"])

UP = Direction(0, -1)
DOWN = Direction(0, 1)
RIGHT = Direction(1, 0)
LEFT = Direction(-1, 0)

Scenes = namedtuple("Scenes", ["menu", "play"])
Size = namedtuple("Size", ["horizontal", "vertical"])
Location = namedtuple("Location", [
    "x",
    "y",
])
font = pygame.font.Font("interface/assets/pixelart-1.ttf", 24)

# Debug
DEBUG = True


class Colors:
    WHITE = (255, 255, 255)
    LIGHTEST_GREY = (200, 200, 200)
    LIGHTER_GREY = (150, 150, 150)
    LIGHT_GREY = (110, 110, 110)
    GREY = (64, 64, 64)
    BLACK = (0, 0, 0)
    DEAD_COLORS = [LIGHTEST_GREY, LIGHTER_GREY, LIGHT_GREY, WHITE]
    DEAD_COLOR = cycle(DEAD_COLORS)
    GRID_COLORS = [GREY, WHITE, None]
    GRID_COLOR = cycle(GRID_COLORS)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    GREEN_light = (0, 200, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    DARKGRAY = (40, 40, 40)


class WindowSettings:
    WIDTH = 1280
    HEIGHT = 720
    REC_WIDTH = 16
    REC_HEIGHT = 16
    MARGIN = 15
    FPS = 60


class DefaultSettings:
    CELL_SQUARE_SIZE = 50
    POPULATION_SIZE = 1
    FOOD_SIZE = 2
    FOOD_NUM = 20
    I_NODES = 8
    H_NODES = 5
    O_NODES = 2
    VELOCITY_DECAY_FACTOR = 0.22

    SEED = 333
    TIME_STEPS = 200
    ELITISM = 0.50
    MUTATION_RATE = 0.5
