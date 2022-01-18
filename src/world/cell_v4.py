from collections import namedtuple
import copy
from algorithm.brain import Brain
from commons.functions import euclidian_distance
from commons.nn_maths_functions import dist_between, dist_to_item, xy_dist_to_item
from commons.settings import WindowSettings, UP, DOWN, LEFT, RIGHT, font, Location, Colors
from numpy.random import uniform, randint
import pygame
from math import radians, sin, cos

from world import Food

DNA = namedtuple("DNA", [
    "color",
    "size",
    "speed",
    "vision_range",
    "rotation_speed"
])

State = namedtuple("State", [
    "health"
])

Limits = namedtuple("Limits", [
    "top_distance_to_edge",
    "bottom_distance_to_edge",
    "left_distance_to_edge",
    "right_distance_to_edge"
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
            speed=3,
            rotation_speed=3,
            vision_range=200,
        )

        self.STATE = State(
            health=100,
        )

        # TODO: how the cell will know the position of the nose?
        self.LOCATION = Location(
            x=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.WIDTH - WindowSettings.MARGIN),
            y=uniform(0 + WindowSettings.MARGIN,
                      WindowSettings.HEIGHT - WindowSettings.MARGIN)
        )

        self.LIMITS = Limits(
            top_distance_to_edge=self.LOCATION.y,
            bottom_distance_to_edge=WindowSettings.HEIGHT - self.LOCATION.y,
            left_distance_to_edge=self.LOCATION.x,
            right_distance_to_edge=WindowSettings.WIDTH - self.LOCATION.x
        )

        self.rectangle = pygame.image.load("interface/assets/cell.png")
        self.rectangle = pygame.transform.scale(self.rectangle, (32, 32))
        self.original_image = self.rectangle
        self.image = self.rectangle
        self.rect = self.rectangle.get_rect()
        self.screen = screen
        self.up = pygame.K_w
        self.down = pygame.K_s
        self.left = pygame.K_a
        self.right = pygame.K_d
        self.direction = []
        self.angle = 0
        self.childs = []

        self.age = 0
        self.foods = 0
        self.distance_travelled = 0
        self.screen = screen
        self.name = name
        self.brain = brain
        self.brain.fitness = 0

        self.set_direction()

    def __repr__(self):
        return f"Cell: {self.name} " \
               f"Health - {self.STATE.health} - " \
               f"Age - {self.age} - " \
               f"Distance - {round(self.distance_travelled, 2)} - " \
               f" {self.brain}"

    def render(self):
        self.screen.blit(self.image, (self.LOCATION.x - int(self.image.get_width() / 2),
                                      self.LOCATION.y - int(self.image.get_height() / 2)))
        health = font.render(f"{self.STATE.health}", 0, (255, 255, 255))
        self.screen.blit(health, (self.LOCATION.x + 35, self.LOCATION.y + 10))
        brain_id = font.render(f"{self.brain.id}", 0, (255, 255, 255))
        self.screen.blit(brain_id, (self.LOCATION.x - 40, self.LOCATION.y + 10))
        pygame.draw.circle(self.screen, Colors.GREEN,
                           [self.LOCATION.x, self.LOCATION.y], self.DNA.vision_range, 1)
        pygame.draw.circle(self.screen, Colors.YELLOW,
                           [self.LOCATION.x, self.LOCATION.y], self.DNA.vision_range - 170, 1)
        self.rect = self.rectangle.get_rect()

    def think(self, objects_in_view):
        outputs = []
        inputs = []

        if len(objects_in_view) == 0:
            object_inputs = [-1000, -1000]
            inputs.append([self.STATE.health] + list(self.LOCATION) + object_inputs)
        else:
            object_inputs = self.info_to_vec(objects_in_view)
            inputs.append([self.STATE.health] + list(self.LOCATION) + object_inputs)

        for input_ in inputs:
            outputs.append(self.brain.predict(input_))

        # print(inputs, outputs)
        return outputs

    def set_direction(self):
        rad = radians(self.angle)
        self.direction = [sin(rad), cos(rad)]

    def do_rotate(self):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = list(self.LOCATION)
        self.set_direction()

    def update_dna(self, **kwargs):
        self.DNA = self.DNA._replace(**kwargs)

    def update_location(self, **kwargs):
        self.LOCATION = self.LOCATION._replace(**kwargs)
        self.update_limits(
            top_distance_to_edge=self.LOCATION.y,
            bottom_distance_to_edge=WindowSettings.HEIGHT - self.LOCATION.y,
            left_distance_to_edge=self.LOCATION.x,
            right_distance_to_edge=WindowSettings.WIDTH - self.LOCATION.x
        )

    def update_limits(self, **kwargs):
        self.LIMITS = self.LIMITS._replace(**kwargs)

    def update_health(self, health):
        self.STATE = State(health=min(round(self.STATE.health + health, 2), 200))

    def update_fitness(self, fitness):
        self.brain.fitness = self.brain.fitness + fitness

    def apply_movement(self, outputs):

        for output in outputs:
            if output[0] > 0:
                tmp_pos = [i * self.DNA.speed for i in self.direction]
                self.update_location(x=self.LOCATION.x - tmp_pos[0], y=self.LOCATION.y - tmp_pos[1])
                self.rect.center = list(self.LOCATION)
            elif output[0] < 0:
                tmp_pos = [i * (self.DNA.speed / 2) for i in self.direction]
                self.update_location(x=self.LOCATION.x + tmp_pos[0], y=self.LOCATION.y + tmp_pos[1])
                self.rect.center = list(self.LOCATION)

            if output[1] > 0:
                self.angle = (self.angle - self.DNA.rotation_speed) % 360
                self.do_rotate()
            elif output[1] < 0:
                self.angle = (self.angle + self.DNA.rotation_speed) % 360
                self.do_rotate()

    def update_creature_properties(self) -> None:
        """
        Updates the creature properties according to its actions.
        """
        self.update_fitness(1)
        self.update_health(-0.5)

        #if (self.LOCATION.x <= 0 or self.LOCATION.x >= WindowSettings.WIDTH) or \
        #        (self.LOCATION.y <= 0 or self.LOCATION.y >= WindowSettings.HEIGHT):
        #    self.kill()

        if self.STATE.health <= 0:
            self.kill()

        # print(self, self.brain.fitness)

    def is_dead(self):
        if self.STATE.health <= 0:
            return True
        return False

    def kill(self):
        self.STATE = State(health=0)

    def eat(self, food):
        self.update_health(food.energy)
        self.foods += 1
        if self.foods >= 2:
            print('REPRODUZIU')
            self.reproduce()

    def on_manual(self, keys_press):

        if keys_press[self.up]:
            tmp_pos = [i * self.DNA.speed for i in self.direction]
            self.update_location(x=self.LOCATION.x - tmp_pos[0], y=self.LOCATION.y - tmp_pos[1])
            self.rect.center = list(self.LOCATION)
        elif keys_press[self.down]:
            tmp_pos = [i * (self.DNA.speed / 2) for i in self.direction]
            self.update_location(x=self.LOCATION.x + tmp_pos[0], y=self.LOCATION.y + tmp_pos[1])
            self.rect.center = list(self.LOCATION)

        if keys_press[self.right]:
            self.angle = (self.angle - self.DNA.rotation_speed) % 360
            self.do_rotate()
        elif keys_press[self.left]:
            self.angle = (self.angle + self.DNA.rotation_speed) % 360
            self.do_rotate()

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
            # Calculate dx and dy.
            dx, dy = dist_between(self, other)

            # Build network input.
            network_input = [dx, dy]
            return [other.LOCATION.x, other.LOCATION.y]
        else:
            raise NotImplementedError("Creatures can only 'see' other creatures and foods")

    def reproduce(self):
        child = copy.copy(self.brain)
        child.mutate()
        self.childs.append(child)

    def birth(self):
        self.childs = []
