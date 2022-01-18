from collections import namedtuple
import copy

import numpy

from algorithm.brain import Brain
from commons.functions import euclidian_distance
from commons.nn_maths_functions import dist_between, dist_to_item, xy_dist_to_item
from commons.settings import WindowSettings, UP, DOWN, LEFT, RIGHT, font, Location, Colors
from numpy.random import uniform, randint
import pygame
from math import radians, sin, cos, atan2, degrees

from world import Food

settings = {}

# EVOLUTION SETTINGS
settings['pop_size'] = 50  # number of organisms
settings['food_num'] = 100  # number of food particles
settings['gens'] = 50  # number of generations
settings['elitism'] = 0.20  # elitism (selection bias)
settings['mutate'] = 0.10  # mutation rate

# SIMULATION SETTINGS
settings['gen_time'] = 100  # generation length         (seconds)
settings['dt'] = 0.04  # simulation time step      (dt)
settings['dr_max'] = 720  # max rotational speed      (degrees per second)
settings['v_max'] = 50  # max velocity              (units per second)
settings['dv_max'] = 1  # max acceleration (+/-)    (units per second^2)

# ORGANISM NEURAL NET SETTINGS
settings['inodes'] = 1  # number of input nodes
settings['hnodes'] = 5  # number of hidden nodes
settings['onodes'] = 2  # number of output nodes


class Cell(pygame.sprite.Sprite):
    """
    Class that represent a living cell in the environment
    actions: [
    ]
    """

    def __init__(self, screen, name: str, brain: Brain):
        pygame.sprite.Sprite.__init__(self)

        self.x = uniform(0 + WindowSettings.MARGIN,
                         WindowSettings.WIDTH - WindowSettings.MARGIN)  # position (x)
        self.y = uniform(0 + WindowSettings.MARGIN,
                         WindowSettings.HEIGHT - WindowSettings.MARGIN)  # position (y)
        self.vision_range = 200
        self.r = uniform(0, 360)  # orientation   [0, 360]
        self.v = 30  # velocity      [0, v_max]
        self.dv = 300  # dv

        self.d_food = 100  # distance to nearest food
        self.r_food = 0  # orientation to nearest food

        self.wih = numpy.random.uniform(-1, 1, (settings['hnodes'], settings['inodes']))
        self.who = numpy.random.uniform(-1, 1, (settings['onodes'], settings['hnodes']))

        self.name = name

        self.age = 0
        self.health = 100
        self.screen = screen
        self.name = name
        self.brain = brain
        self.brain.fitness = 0

        # manual pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d
        self.up = pygame.K_w
        self.down = pygame.K_s
        self.left = pygame.K_a
        self.right = pygame.K_d

    def __repr__(self):
        return f"Cell: {self.name} " \
               f"Age - {self.age} - "

    def render(self):
        tail_len = 20
        x2 = cos(radians(self.r)) * tail_len + self.x
        y2 = sin(radians(self.r)) * tail_len + self.y
        pygame.draw.circle(self.screen, Colors.GREEN, (self.x, self.y), 10, 2)
        pygame.draw.line(self.screen, Colors.GREEN, (self.x, self.y), (x2, y2), 2)
        pygame.draw.circle(self.screen, Colors.GREEN,
                           [self.x, self.y], self.vision_range, 1)
        pygame.draw.circle(self.screen, Colors.YELLOW,
                           [self.x, self.y], self.vision_range - 170, 1)
        health = font.render(f"{self.health}", 0, (255, 255, 255))
        self.screen.blit(health, (self.x + 35, self.y + 10))
        brain_id = font.render(f"{self.brain.id}", 0, (255, 255, 255))
        self.screen.blit(brain_id, (self.x - 40, self.y + 10))

    def think(self, objects_in_view):
        outputs = []
        inputs = []

        if len(objects_in_view) == 0:
            inputs.append([self.health, 0])
        else:
            object_inputs = self.info_to_vec(objects_in_view)
            inputs.append([self.health, object_inputs])

        for input_ in inputs:
            outputs.append(self.brain.predict(input_))
        return outputs

    def apply_decisions(self, decisions):
        for decision in decisions:
            # UPDATE HEADING
            self.r += decision[0] * settings['dr_max'] * settings['dt']
            self.r = self.r % 360

            # UPDATE VELOCITY
            self.v += decision[1] * settings['dv_max'] * settings['dt']
            if self.v < 0:
                self.v = 0
            if self.v > settings['v_max']:
                self.v = settings['v_max']

            # UPDATE POSITION
            dx = self.v * cos(radians(self.r)) * settings['dt']
            dy = self.v * sin(radians(self.r)) * settings['dt']
            self.x += dx
            self.y += dy

    def eat(self, food):
        self.update_health(food.energy)

    def is_dead(self):
        if self.health <= 0:
            return True
        return False

    def calc_heading(self, food):
        d_x = food.LOCATION.x - self.x
        d_y = food.LOCATION.y - self.y
        theta_d = degrees(atan2(d_y, d_x)) - self.r
        if abs(theta_d) > 180: theta_d += 360
        return theta_d / 180

    def update_fitness(self, fitness):
        self.brain.fitness = self.brain.fitness + fitness

    def update_health(self, health):
        self.health = min(round(self.health + health, 2), 300)

    def update_creature_properties(self) -> None:
        """
        Updates the creature properties according to its actions.
        """
        self.update_fitness(1)
        self.update_health(-0.1)

        if self.health <= 0:
            self.kill()

        # print(self, self.brain.fitness)

    def info_to_vec(self, others):
        """
        Meaningfully convert CreatureInfo of a target creature to a CreatureNetworkInput named tuple,
        based on the creature info of the source creature.
        :param others: Destination Thing (creature SEEN).
        :return: Network input for creature LOOKING at creature SEEN.
        """
        # Get the closest food
        closest_dist_so_far = None
        other = None
        for item in others:
            other_org_dist = dist_to_item(self, item)
            if closest_dist_so_far is None or other_org_dist < closest_dist_so_far:
                closest_dist_so_far = other_org_dist
                other = item

        if isinstance(other, Food):
            return self.calc_heading(other)
        else:
            raise NotImplementedError("Creatures can only 'see' other creatures and foods")