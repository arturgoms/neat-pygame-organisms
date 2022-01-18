import math
from collections import namedtuple

import pygame

from algorithm.brain import Brain
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


class Cell(pygame.sprite.Sprite):
    """
    Class that represent a living cell in the environment
    actions: [
    ]
    """

    def __init__(self, screen, name: str, brain: Brain):
        pygame.sprite.Sprite.__init__(self)
        self.DNA = DNA(
            color=(uniform(2, 255), uniform(2, 255), uniform(2, 255)),
            size=32,
            speed=10,
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
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()

        self.age = 0
        self.distance_travelled = 0
        self.screen = screen
        self.name = name
        self.brain = brain
        self.brain.fitness = 0

    def __repr__(self):
        return f"Cell: {self.name} " \
               f"Health - {self.STATE.health} - " \
               f"Age - {self.age} - " \
               f"Distance - {round(self.distance_travelled,2)} - " \
               f" {self.brain}"

    def label(self):
        return font.render(f"{self.STATE.health}", 0, (255, 255, 255))

    def render(self):
        self.screen.blit(self.image, [self.LOCATION.x, self.LOCATION.y])
        self.screen.blit(self.label(), (self.LOCATION.x + 35, self.LOCATION.y + 10))
        # pygame.draw.circle(self.screen, Colors.GREEN, [self.LOCATION.x, self.LOCATION.y], self.DNA.vision_range, 1)

    def think(self, inputs):
        print('input', list(self.LOCATION) + list(inputs))
        output = self.brain.predict(list(self.LOCATION) + list(inputs))
        print('output', output)
        return output

    def interpret_decisions(self, decisions):
        """
        Converts creature network output to creature actions.
        :param decisions: All decisions creature made towards all other objects in its line of sight.
        """

        # Avg out everything the creature wants to do, using main__a weighted average against the urgency of each
        # decision.
        move_x, move_y, total = 0, 0, 0
        for decision in decisions:
            left, right, up, down, urgency = decision
            total += 1

            # Movement.
            if right > left:
                move_x += -right * urgency
            elif right < left:
                move_x += +left * urgency
            if up > down:
                move_y += -up * urgency
            elif up < down:
                move_y += +down * urgency

        # Sometimes the creature can't 'see' anything, so total would be 0.
        if total:
            move_x = move_x * self.DNA.speed / total
            move_y = move_y * self.DNA.speed / total

        actions = [move_x, move_y]
        return actions

    def apply_action(self, actions) -> None:
        self.update_location(x=self.LOCATION.x + actions[0], y=self.LOCATION.y + actions[1])

    def move(self, direction):
        if direction == UP:
            self.update_location(x=self.LOCATION.x,
                                 y=self.LOCATION.y + (self.DNA.speed * direction.y))
        if direction == LEFT:
            self.update_location(x=self.LOCATION.x + (self.DNA.speed * direction.x),
                                 y=self.LOCATION.y + direction.y)
        if direction == DOWN:
            self.update_location(x=self.LOCATION.x + direction.x,
                                 y=self.LOCATION.y + (self.DNA.speed * direction.y))
        if direction == RIGHT:
            self.update_location(x=self.LOCATION.x + (self.DNA.speed * direction.x),
                                 y=self.LOCATION.y + direction.y)

        self.rect = self.image.get_rect(x=self.LOCATION.x, y=self.LOCATION.y)

    def update_dna(self, **kwargs):
        self.DNA = self.DNA._replace(**kwargs)

    def update_location(self, **kwargs):
        self.LOCATION = self.LOCATION._replace(**kwargs)

    def update_health(self, health):
        self.STATE = State(health=min(round(self.STATE.health + health, 2), 200))

    def update_fitness(self, fitness):
        self.brain.fitness = self.brain.fitness + fitness

    def update_creature_properties(self) -> None:
        """
        Updates the creature properties according to its actions.
        """

        # The more the creature moves, the higher its fitness.
        # distance = math.sqrt(math.pow(actions[0], 2) + math.pow(actions[1], 2))
        # self.update_fitness(distance)
        # self.distance_travelled += distance
        self.age += 1
        #self.update_health(-0.5)

        if (self.LOCATION.x <= 0 or self.LOCATION.x >= WindowSettings.WIDTH) or \
                (self.LOCATION.y <= 0 or self.LOCATION.y >= WindowSettings.HEIGHT):
            self.kill()

        if self.STATE.health <= 0:
            self.kill()

    def kill(self):
        self.STATE = State(health=0)
        self.brain.fitness = self.age
        # print(self, 'died saving fitness', self.brain)

    def eat(self, food):
        self.update_health(food.energy)
