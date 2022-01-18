from math import cos, radians, sin

import pygame
from algorithm.brain import Brain
from commons.settings import Colors, font
from world.population.base import BaseCell


class Cell(BaseCell):
    """
    Class that represent a living cell in the environment
    actions: [
    ]
    """

    def __init__(self, screen, name: str, brain: Brain):
        BaseCell.__init__(self, brain)

        self.age = 0
        self.screen = screen
        self.name = name

    def __repr__(self):
        return f"Cell: {self.name} " \
               f"Age - {self.age}"

    def render(self):
        tail_len = 20
        x2 = cos(radians(self.LOCATION.orientation)) * tail_len + self.LOCATION.x
        y2 = sin(radians(self.LOCATION.orientation)) * tail_len + self.LOCATION.y
        # Body
        pygame.draw.circle(self.screen, (self.DNA.color_r, self.DNA.color_g, self.DNA.color_b),
                           (self.LOCATION.x, self.LOCATION.y), 10, 2)
        pygame.draw.line(self.screen, (self.DNA.color_r, self.DNA.color_g, self.DNA.color_b),
                         (self.LOCATION.x, self.LOCATION.y), (x2, y2), 2)

        # Vision
        pygame.draw.circle(self.screen, Colors.GREEN,
                           [self.LOCATION.x, self.LOCATION.y], self.DNA.vision_range, 1)
        pygame.draw.circle(self.screen, Colors.YELLOW,
                           [self.LOCATION.x, self.LOCATION.y], self.DNA.vision_range - 170, 1)

        # Labels
        health = font.render(f"{self.STATE.health}", 0, (255, 255, 255))
        self.screen.blit(health, (self.LOCATION.x + 35, self.LOCATION.y + 10))
        brain_id = font.render(f"{self.brain.id}", 0, (255, 255, 255))
        self.screen.blit(brain_id, (self.LOCATION.x - 40, self.LOCATION.y + 10))

    def think(self, objects_in_view):
        outputs = []
        inputs = []

        if len(objects_in_view) == 0:
            #inputs.append([self.STATE.health, 0])
            inputs.append([0])
        else:
            object_inputs = self.info_to_vec(objects_in_view)
            #inputs.append([self.STATE.health, object_inputs])
            inputs.append([object_inputs])

        for input_ in inputs:
            outputs.append(self.brain.predict(input_))
        return outputs

    def apply_decisions(self, decisions):
        for decision in decisions:
            tmp_orientation = self.LOCATION.orientation + decision[0] * 720 * self.magic
            self.update_location(orientation=tmp_orientation % 360)

            tmp_speed = self.DNA.speed + decision[1] * self.magic
            if tmp_speed < 0:
                tmp_speed = 0

            dx = tmp_speed * cos(radians(self.LOCATION.orientation)) * self.magic
            dy = tmp_speed * sin(radians(self.LOCATION.orientation)) * self.magic
            self.update_location(x=self.LOCATION.x+dx, y=self.LOCATION.y+dy)

    def eat(self, food):
        self.update_health(food.energy)

    def update_creature_properties(self) -> None:
        """
        Updates the creature properties according to its actions.
        """
        self.update_fitness(1)
        self.update_health(-0.1)

        if self.STATE.health <= 0:
            self.kill()


