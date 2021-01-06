import numpy as np
from .dequedict import DequeDict


# TODO Documentation
class Pollutionator:
    def __init__(self, period_length):
        self.period_length = period_length

        # Running sum of pollution taken at the end of a period
        self.pollution_period_sum = 0

        self.unique = {}
        self.unique_count = 0

        self.clean_q = DequeDict()
        self.pollution = set()

        # TODO what *IS* this?
        self.unique_block_count = 0

        self.X = []
        self.Y = []
        self.Y_period_sum = []

    def getPollutions(self):
        return self.Y_period_sum

    def _is_pollution(self, oblock):
        return (self.unique_count -
                self.unique[oblock]) >= (2 * self.period_length)

    def incrementUniqueCount(self):
        self.unique_count += 1
        while self.clean_q:
            first = self.clean_q.first()
            if not self._is_pollution(first):
                break
            self.clean_q.popFirst()
            self.pollution.add(first)

    def setUnique(self, oblock):
        self.unique[oblock] = self.unique_count
        self.clean_q[oblock] = oblock
        self.pollution.discard(oblock)

    def remove(self, oblock):
        del self.unique[oblock]
        if oblock in self.clean_q:
            del self.clean_q[oblock]
        self.pollution.discard(oblock)

    def getPollution(self):
        return len(self.pollution)

    def update(self, time):
        if time % self.period_length == 0:
            pollution = self.getPollution()
            pollution_value = 100 * pollution / self.period_length
            self.X.append(time)
            self.Y.append(pollution_value)
            self.pollution_period_sum += pollution_value
            self.Y_period_sum.append(self.pollution_period_sum)
