from lib.dequedict import DequeDict
from lib.pollutionator import Pollutionator


class MRU:
    class MRU_Entry:
        def __init__(self, oblock):
            self.oblock = oblock

        def __repr__(self):
            return "(o={})".format(self.oblock)

    def __init__(self, cache_size, **kwargs):
        self.cache_size = cache_size
        self.mru = DequeDict()

        self.time = 0

        self.pollution = Pollutionator(cache_size)

    def __contains__(self, oblock):
        return oblock in self.mru

    def addToCache(self, oblock):
        x = self.MRU_Entry(oblock)
        self.mru[oblock] = x

    def hit(self, oblock):
        x = self.mru[oblock]
        self.mru[oblock] = x

    def evict(self):
        mru = self.mru.popLast()
        self.pollution.remove(mru.oblock)
        return mru

    def miss(self, oblock):
        if len(self.mru) == self.cache_size:
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

        if miss:
            self.pollution.incrementUniqueCount()
        self.pollution.setUnique(oblock)
        self.pollution.update(self.time)

        return miss
