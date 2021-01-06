from lib.dequedict import DequeDict
from lib.pollutionator import Pollutionator


class LRU:
    class LRU_Entry:
        def __init__(self, oblock):
            self.oblock = oblock

        def __repr__(self):
            return "(o={})".format(self.oblock)

    def __init__(self, cache_size, **kwargs):

        self.cache_size = cache_size
        self.lru = DequeDict()

        self.time = 0

        self.pollution = Pollutionator(cache_size)

        self.cache = []

    def __contains__(self, oblock):
        return oblock in self.lru

    def addToCache(self, oblock):
        x = self.LRU_Entry(oblock)
        self.lru[oblock] = x

    def hit(self, oblock):
        x = self.lru[oblock]
        self.lru[oblock] = x

    def evict(self):
        lru = self.lru.popFirst()
        self.pollution.remove(lru.oblock)
        return lru

    def miss(self, oblock):
        if len(self.lru) == self.cache_size:
            self.evict()
        self.addToCache(oblock)


    def request(self, oblock):
        miss = True
        eviction = False
        self.time += 1

        if oblock in self.lru:
            miss = False
            self.hit(oblock)
        else:
            eviction = self.miss(oblock)

        self.cache.append(oblock)

        # Pollutionator
        if miss:
            self.pollution.incrementUniqueCount()
        self.pollution.setUnique(oblock)
        self.pollution.update(self.time)

        return miss
