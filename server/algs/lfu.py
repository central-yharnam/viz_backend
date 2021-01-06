from lib.heapdict import HeapDict
from lib.pollutionator import Pollutionator
import numpy as np

class LFU:
    class LFU_Entry:
        def __init__(self, oblock, freq=1, time=0):
            self.oblock = oblock
            self.freq = freq
            self.time = time

        def __lt__(self, other):
            if self.freq == other.freq:
                return np.random.choice([True, False])
            return self.freq < other.freq

        def __repr__(self):
            return "(o={}, f={}, t={})".format(self.oblock, self.freq,
                                               self.time)

    def __init__(self, cache_size, **kwargs):
        self.cache_size = cache_size
        self.lfu = HeapDict()
        self.time = 0
        np.random.seed(123)

        self.pollution = Pollutionator(cache_size)

    def __contains__(self, oblock):
        return oblock in self.lfu

    def addToCache(self, oblock):
        x = self.LFU_Entry(oblock, freq=1, time=self.time)
        self.lfu[oblock] = x

    def hit(self, oblock):
        x = self.lfu[oblock]
        x.freq += 1
        x.time = self.time
        self.lfu[oblock] = x

    def evict(self):
        lfu_min = self.lfu.popMin()
        self.pollution.remove(lfu_min.oblock)
        return lfu_min

    def miss(self, oblock):
        if len(self.lfu) == self.cache_size:
            self.evict()
        self.addToCache(oblock)

    def request(self, oblock):
        miss = True

        self.time += 1

        if oblock in self:
            miss = False
            self.hit(oblock)
        else:
            self.miss(oblock)

        # Pollutionator
        if miss:
            self.pollution.incrementUniqueCount()
        self.pollution.setUnique(oblock)
        self.pollution.update(self.time)

        return miss
