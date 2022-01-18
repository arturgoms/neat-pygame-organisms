import os
from datetime import datetime

from pygame.locals import *

from algorithm.activations import tanh
from algorithm.draw import draw_brain_pygame, draw_species_bar_pygame
from algorithm.options import Options
from algorithm.population import Population
from algorithm.save import save_brain, load_brain
from commons.functions import euclidian_distance
from commons.settings import *
from world import Food, CellV5


class MainWindow:
    def __init__(self, load_state=None):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.display.set_caption("Game of Life (?)")
        pygame.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])
        self.FPS = 60
        self.delta = 0
        self.screen = pygame.display.set_mode([WindowSettings.WIDTH, WindowSettings.HEIGHT])
        self.clock = pygame.time.Clock()
        self.paused = True
        self.new_gen_event = pygame.USEREVENT + 1
        self.gens_per_sec = 100
        pygame.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))
        self.cells = []
        self.foods = []
        self.world_info = []
        self.generation = 0
        self.simulation_time = 1
        self.move = False
        self.load_state = load_state
        self.mobs = []
        Options.set_options(1, 2, 20, activation_func=tanh)
        self.population = None
        self.best = None
        self.best_score = None
        self.generate_population(first_gen=True)
        self.generate_world_environment()
        self.update_population()

    def update_world(self, manual=False):
        self.simulation_time += 1
        dead_cells = []

        for x, cell in enumerate(self.cells):
            objects_in_view = [other_info for other_info in self.world_info
                               if euclidian_distance(cell.LOCATION.x,
                                                     cell.LOCATION.y,
                                                     other_info.LOCATION.x,
                                                     other_info.LOCATION.y) < cell.DNA.vision_range]

            if not manual:
                cell.apply_decisions(cell.think(objects_in_view))
            else:
                # FIXME: Manual movement not working
                cell.think()
                #keys = pygame.key.get_pressed()
                #self.cells[-1].on_manual(keys)

            cell.update_creature_properties()

            if cell.is_dead():
                dead_cells.append(cell)

            if self.simulation_time > 30:
                for food in objects_in_view:
                    distance = euclidian_distance(food.LOCATION.x + 10,
                                                  food.LOCATION.y + 10,
                                                  cell.LOCATION.x,
                                                  cell.LOCATION.y)
                    if distance < cell.DNA.vision_range - 170:
                        cell.eat(food)
                        food.respawn()

        for cell in dead_cells:
            self.cells.remove(cell)

        if len(self.cells) == 0:
            self.generate_population(first_gen=False)
            self.generate_world_environment()

        self.update_population()

    def generate_population(self, first_gen):
        # TODO: if we had a body parameter inside the cell and mix the brain and
        #  body when doing the crossover and mutation stuff?

        if first_gen:
            self.population = Population()
        else:
            self.population.epoch()
            print(f'Generation {self.population.gen}, melhorzin: {self.population.best}')
            print(self.population)
            self.best = self.population.best.id
            self.best_score = self.population.best.fitness

        if self.load_state and first_gen:
            # FIXME: Does not evolve if load_state
            self.cells = [CellV5(self.screen, name=brain.id, brain=load_brain(self.load_state))
                          for brain in self.population.pool]
        else:
            self.cells = [CellV5(self.screen, name=brain.id, brain=brain) for brain in self.population.pool]

    def generate_world_environment(self):
        self.foods = []
        for i in range(20):
            self.foods.append(Food(self.screen, name=i, color=(255, 0, 255)))

    def update_population(self):
        self.screen.fill(Colors.DARKGRAY)
        for cell in self.cells:
            cell.render()
        for food in self.foods:
            food.render()
        for mob in self.mobs:
            mob.render()

        self.update_label()
        self.world_info = self.foods
        pygame.display.update()

    def update_label(self):
        if self.population:
            draw_brain_pygame(self.screen, self.population.best, 10, WindowSettings.HEIGHT - 300, 200, circle_size=8)
            draw_species_bar_pygame(self.screen, self.population, 300, 10)

        self.screen.blit(font.render(f"Generation: {self.population.gen}", True,
                                     (255, 255, 255)), (10, WindowSettings.HEIGHT - 100))

        self.screen.blit(font.render(f"Best: Cell {self.best} Score {self.best_score}", True,
                                     (255, 255, 255)), (10, WindowSettings.HEIGHT - 50))

    def run(self):
        """
        Starts the game and loops until the quit state
        """
        while True:
            self.handle_events()
            self.delta = self.clock.tick(self.FPS)

    def handle_mouse_buttons(self, event: pygame.event.Event, button: (bool, bool, bool)):
        """
        This function handles all the events related to the mouse buttons
        :param event: pygame Event
        :param button: tuple of booleans
        """
        pass

    def handle_keys(self, event: pygame.event.Event):
        """
        This function handles all the events related to the keyboard
        :param event: pygame Event
        """
        if event.key == pygame.K_p:
            print("'p' pressed! - toggling pause")
            self.paused = not self.paused
        if not self.paused:
            if event.key == K_DOWN:
                self.cells[-1].move(DOWN)
            if event.key == K_UP:
                self.cells[-1].move(UP)
            if event.key == K_RIGHT:
                self.cells[-1].move(RIGHT)
            if event.key == K_LEFT:
                self.cells[-1].move(LEFT)

    def handle_events(self):
        """
        Handle all the events
        """
        for event in pygame.event.get():

            if event.type == self.new_gen_event and not self.paused:
                self.update_world(manual=False)
            elif event.type == QUIT:
                save_brain(self.population.best, f'cell-{datetime.now()}.json')
                quit("App window was closed!")
            elif event.type == KEYDOWN:
                self.handle_keys(event)
            elif button := pygame.mouse.get_pressed(num_buttons=3):
                self.handle_mouse_buttons(event, button)
