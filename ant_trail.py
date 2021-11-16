import copy
import random

import numpy as np

from functools import partial
from operator import attrgetter
import algorithms
import base
import creator
import support
import gp
import matplotlib.pyplot as plt
def Tournament(individuals, k, tournsize, fit_attr="fitness"):
    chosen = []
    for i in range(k):
        aspirants = [random.choice(individuals) for i in range(tournsize)]
        chosen.append(max(aspirants, key=attrgetter(fit_attr)))
    return chosen


def progn(*args):
    for arg in args:
        arg()


def prog2(out1, out2):
    return partial(progn, out1, out2)


def prog3(out1, out2, out3):
    return partial(progn, out1, out2, out3)


def if_then_else(condition, out1, out2):
    out1() if condition() else out2()


def initRepeat(container, func, n):
    return container(func() for _ in range(n))


def initIterate(container, generator):
    return container(generator())


class AntSimulator(object):
    direction = ["north", "east", "south", "west"]
    dir_row = [1, 0, -1, 0]
    dir_col = [0, 1, 0, -1]

    def __init__(self, max_moves):
        self.max_moves = max_moves
        self.moves = 0
        self.eaten = 0
        self.routine = None

    def _reset(self):
        self.row = self.row_start
        self.col = self.col_start
        self.dir = 1
        self.moves = 0
        self.eaten = 0
        self.matrix_exc = copy.deepcopy(self.matrix)

    @property
    def position(self):
        return (self.row, self.col, self.direction[self.dir])

    def turnleft(self):
        if self.moves < self.max_moves:
            self.moves += 1
            self.dir = (self.dir - 1) % 4

    def turnright(self):
        if self.moves < self.max_moves:
            self.moves += 1
            self.dir = (self.dir + 1) % 4

    def moveforward(self):
        if self.moves < self.max_moves:
            self.moves += 1
            self.row = (self.row + self.dir_row[self.dir]) % self.matrix_row
            self.col = (self.col + self.dir_col[self.dir]) % self.matrix_col
            if self.matrix_exc[self.row][self.col] == "food":
                self.eaten += 1
            self.matrix_exc[self.row][self.col] = "passed"

    def sense_food(self):
        ahead_row = (self.row + self.dir_row[self.dir]) % self.matrix_row
        ahead_col = (self.col + self.dir_col[self.dir]) % self.matrix_col
        return self.matrix_exc[ahead_row][ahead_col] == "food"

    def if_food_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_food, out1, out2)

    def run(self, routine):
        self._reset()
        while self.moves < self.max_moves:
            routine()

    def matrix_parse(self, matrix):
        self.matrix = list()
        for index, line in enumerate(matrix):
            self.matrix.append(list())
            for lIndex, lcol in enumerate(line):
                if lcol == "#":
                    self.matrix[-1].append("food")
                elif lcol == ".":
                    self.matrix[-1].append("empty")
                elif lcol == "S":
                    self.matrix[-1].append("empty")
                    self.row_start = self.row = index
                    self.col_start = self.col = lIndex
                    self.dir = 1
        self.matrix_row = len(self.matrix)
        self.matrix_col = len(self.matrix[0])
        self.matrix_exc = copy.deepcopy(self.matrix)


ant_trail = AntSimulator(600)

pTree = gp.PrimitiveSet("MAIN", 0)
pTree.functionSet(ant_trail.if_food_ahead, 2)
pTree.functionSet(prog2, 2)
pTree.functionSet(prog3, 3)
pTree.terminalSet(ant_trail.moveforward)
pTree.terminalSet(ant_trail.turnleft)
pTree.terminalSet(ant_trail.turnright)

creator.createClass("FitnessMax", base.Fitness, weights=(1.0,))
creator.createClass("Individual", gp.Tree, fitness=creator.FitnessMax)

toolbox = base.Toolkit()

# Attribute generator
toolbox.register("expr_init", gp.generationHalfAndHalf, pset=pTree, min_=1, max_=6)

# Structure initializers
toolbox.register("individual", initIterate, creator.Individual, toolbox.expr_init)
toolbox.register("population", initRepeat, list, toolbox.individual)


def evalSantaFeTrail(individual):
    # Transform the tree expression to functionnal Python code
    routine = gp.compile(individual, pTree)
    # Run the generated routine
    ant_trail.run(routine)
    return ant_trail.eaten,


toolbox.register("evaluate", evalSantaFeTrail)
toolbox.register("select", Tournament, tournsize=7)
toolbox.register("mate", gp.onepointcrossover)
toolbox.register("expr_mut", gp.generationHalfAndHalf, min_=0, max_=6)
toolbox.register("mutate", gp.uniformmutation, expr=toolbox.expr_mut, pset=pTree)


def run_santa_fe_trail():
    random.seed(69)

    with  open("santa-fe-trail.txt") as trail_file:
        ant_trail.matrix_parse(trail_file)

    population = toolbox.population(n=500)
    hof = support.HallOfFame(1)
    stats = support.registerfitness(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    _, logbook = algorithms.evolutionaryAlgorithm(population, toolbox, 0.9, 0.1, 50, stats, halloffame=hof)

    return logbook

if __name__ == "__main__":
    fitness_stats = run_santa_fe_trail()
    generations_x = [fitness_stats[val]['gen'] for val in range(len(fitness_stats))]
    fitness_y = [[fitness_stats[val]['min'], fitness_stats[val]['avg'], fitness_stats[val]['max']] for val in
                 range(len(fitness_stats))]
    plt.plot(generations_x, fitness_y)
    labels = ['worst', 'average', 'best']
    plt.legend(labels)
    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.title('Fitness across each generation')
    plt.show()