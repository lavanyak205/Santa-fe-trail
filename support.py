from bisect import bisect_right
from collections import defaultdict
from copy import deepcopy
from functools import partial
from operator import eq

def identity(obj):
    return obj


class registerfitness(object):
    def __init__(self, key=identity):
        self.key = key
        self.functions = dict()
        self.fields = []

    def register(self, name, function, *args, **kargs):
        self.functions[name] = partial(function, *args, **kargs)
        self.fields.append(name)

    def compile(self, data):
        values = tuple(self.key(elem) for elem in data)
        entry = dict()
        for key, func in self.functions.items():
            entry[key] = func(values)
        return entry


class LogStats(list):

    def __init__(self):
        self.buffindex = 0
        self.chapters = defaultdict(LogStats)
        self.columns_len = None
        self.header = None
        self.log_header = True

    def record(self, **infos):

        apply_to_all = {k: v for k, v in list(infos.items()) if not isinstance(v, dict)}
        for key, value in list(infos.items()):
            if isinstance(value, dict):
                chapter_infos = value.copy()
                chapter_infos.update(apply_to_all)
                self.chapters[key].record(**chapter_infos)
                del infos[key]
        self.append(infos)


class HallOfFame(object):

    def __init__(self, maxsize, similar=eq):
        self.maxsize = maxsize
        self.keys = list()
        self.items = list()
        self.similar = similar

    def update(self, population):
        for ind in population:
            if len(self) == 0 and self.maxsize != 0:
                # Working on an empty hall of fame is problematic for the
                # "for else"
                self.insert(population[0])
                continue
            if ind.fitness > self[-1].fitness or len(self) < self.maxsize:
                for hofer in self:
                    # Loop through the hall of fame to check for any
                    # similar individual
                    if self.similar(ind, hofer):
                        break
                else:
                    # The individual is unique and strictly better than
                    # the worst
                    if len(self) >= self.maxsize:
                        self.remove(-1)
                    self.insert(ind)

    def insert(self, item):

        item = deepcopy(item)
        i = bisect_right(self.keys, item.fitness)
        self.items.insert(len(self) - i, item)
        self.keys.insert(i, item.fitness)

    def remove(self, index):

        del self.keys[len(self) - (index % len(self) + 1)]
        del self.items[index]

    def clear(self):

        del self.items[:]
        del self.keys[:]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

    def __iter__(self):
        return iter(self.items)

    def __reversed__(self):
        return reversed(self.items)

    def __str__(self):
        return str(self.items)

