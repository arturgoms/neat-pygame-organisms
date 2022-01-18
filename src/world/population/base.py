from collections import namedtuple
from math import degrees, atan2
from random import uniform

import pygame

from algorithm.brain import Brain
from commons.nn_maths_functions import dist_to_item
from commons.settings import WindowSettings
from world import Food

DNA = namedtuple("DNA", [
    "color_r",
    "color_g",
    "color_b",
    "size",
    "speed",
    "vision_range",
    "rotation_speed"
])

State = namedtuple("State", [
    "health"
])

Location = namedtuple("Location", [
    "x",
    "y",
    "orientation",

])


class BaseCell:

    def __init__(self, brain: Brain):

        self.DNA = DNA(
            color_r=255,
            color_g=255,
            color_b=255,
            size=32,
            speed=30,
            rotation_speed=3,
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
            orientation=0
        )

        self.brain = brain
        self.brain.fitness = 0
        self.magic = 0.04

    def calc_heading(self, other):
        d_x = other.LOCATION.x - self.LOCATION.x
        d_y = other.LOCATION.y - self.LOCATION.y
        theta_d = degrees(atan2(d_y, d_x)) - self.LOCATION.orientation
        if abs(theta_d) > 180:
            theta_d += 360
        return theta_d / 180

    def info_to_vec(self, others):
        """
        Meaningfully convert CreatureInfo of a target creature to a CreatureNetworkInput named tuple,
        based on the creature info of the source creature.
        :param others: Destination Thing (creature SEEN).
        :return: Network input for creature LOOKING at creature SEEN.
        """
        # Get the closest other
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

    def update_fitness(self, fitness):
        self.brain.fitness = self.brain.fitness + fitness

    def update_health(self, health):
        self.STATE = State(health=min(round(self.STATE.health + health, 2), 200))

    def update_location(self, **kwargs):
        self.LOCATION = self.LOCATION._replace(**kwargs)

    def kill(self):
        self.STATE = State(health=0)

    def is_dead(self):
        if self.STATE.health <= 0:
            return True
        return False
