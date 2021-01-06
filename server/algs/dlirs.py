from lib.dequedict import DequeDict
from visual.visualizinator import Visualizinator
from lib.optional_args import process_kwargs
from lib.pollutionator import Pollutionator


class DLIRS:
    class DLIRS_Entry:
        def __init__(self, oblock, is_LIR=False, in_cache=True):
            self.oblock = oblock
            self.is_LIR = is_LIR
            self.is_demoted = False
            self.in_cache = in_cache

        def __repr__(self):
            return "(o={}, is_LIR={}, is_demoted={}, in_cache={})".format(
                self.oblock, self.is_LIR, self.is_demoted, self.in_cache)

    def __init__(self, cache_size, **kwargs):
        self.cache_size = cache_size

        self.hirs_ratio = 0.01

        process_kwargs(self, kwargs, acceptable_kws=['hirs_ratio'])

        self.hirs_limit = max(1,
                              int((self.cache_size * self.hirs_ratio) + 0.5))
        self.lirs_limit = self.cache_size - self.hirs_limit

        self.hirs_count = 0
        self.lirs_count = 0
        self.demoted = 0
        self.nonresident = 0

        # s stack, semi-split to find nonresident HIRs quickly
        self.lirs = DequeDict()
        self.hirs = DequeDict()
        # q, the resident HIR stack
        self.q = DequeDict()

        self.time = 0
        self.visual = Visualizinator(labels=['Q size'])
        self.pollution = Pollutionator(cache_size)

    def __contains__(self, oblock):
        if oblock in self.lirs:
            return self.lirs[oblock].in_cache
        return oblock in self.q

    def hitLIR(self, oblock):
        lru_lir = self.lirs.first()
        x = self.lirs[oblock]
        self.lirs[oblock] = x
        if lru_lir is x:
            self.prune()

    def prune(self):
        while self.lirs:
            x = self.lirs.first()
            if x.is_LIR:
                break

            del self.lirs[x.oblock]
            del self.hirs[x.oblock]

            if not x.in_cache:
                self.nonresident -= 1

    def hitHIRinLIRS(self, oblock):
        x = self.lirs[oblock]
        in_cache = x.in_cache

        x.is_LIR = True

        del self.lirs[oblock]
        del self.hirs[oblock]

        if in_cache:
            del self.q[oblock]
            self.hirs_count -= 1
        else:
            self.adjustSize(True)
            x.in_cache = True
            self.nonresident -= 1

        while self.lirs_count >= self.lirs_limit:
            self.ejectLIR()
        while self.hirs_count + self.lirs_count >= self.cache_size:
            self.ejectHIR()

        self.lirs[oblock] = x
        self.lirs_count += 1

        return not in_cache

    def ejectLIR(self):
        lru = self.lirs.popFirst()
        self.lirs_count -= 1
        lru.is_LIR = False

        lru.is_demoted = True
        self.demoted += 1

        self.q[lru.oblock] = lru
        self.hirs_count += 1

        self.prune()

    def ejectHIR(self):
        lru = self.q.popFirst()
        if lru.oblock in self.lirs:
            lru.in_cache = False
            self.nonresident += 1
        if lru.is_demoted:
            self.demoted -= 1
        self.hirs_count -= 1
        self.pollution.remove(lru.oblock)

    def hitHIRinQ(self, oblock):
        x = self.q[oblock]
        if x.is_demoted:
            self.adjustSize(False)
            x.is_demoted = False
            self.demoted -= 1

        self.q[oblock] = x
        self.lirs[oblock] = x
        self.hirs[oblock] = x
        self.limitStack()

    def limitStack(self):
        while self.hirs_count + self.lirs_count + self.nonresident > 2 * self.cache_size:
            lru = self.hirs.popFirst()
            del self.lirs[lru.oblock]
            if not lru.in_cache:
                self.nonresident -= 1

    def miss(self, oblock):
        if self.lirs_count < self.lirs_limit and self.hirs_count == 0:
            x = self.DLIRS_Entry(oblock, is_LIR=True)
            self.lirs[oblock] = x
            self.lirs_count += 1
            return

        while self.hirs_count + self.lirs_count >= self.cache_size:
            while self.lirs_count > self.lirs_limit:
                self.ejectLIR()
            self.ejectHIR()

        x = self.DLIRS_Entry(oblock, is_LIR=False)
        self.lirs[oblock] = x
        self.hirs[oblock] = x
        self.q[oblock] = x

        self.hirs_count += 1
        self.limitStack()

    def adjustSize(self, hit_nonresident_hir):
        if hit_nonresident_hir:
            self.hirs_limit = min(
                self.cache_size - 1, self.hirs_limit +
                max(1, int((self.demoted / self.nonresident) + 0.5)))
            self.lirs_limit = self.cache_size - self.hirs_limit
        else:
            self.lirs_limit = min(
                self.cache_size - 1, self.lirs_limit +
                max(1, int((self.nonresident / self.demoted) + 0.5)))
            self.hirs_limit = self.cache_size - self.lirs_limit

    def request(self, oblock):
        miss = False
        self.time += 1

        if oblock in self.lirs:
            x = self.lirs[oblock]
            if x.is_LIR:
                self.hitLIR(oblock)
            else:
                miss = self.hitHIRinLIRS(oblock)
        elif oblock in self.q:
            self.hitHIRinQ(oblock)
        else:
            miss = True
            self.miss(oblock)

        # Visualizinator
        self.visual.add({'Q size': (self.time, self.hirs_limit)})

        # Pollutionator
        if miss:
            self.pollution.incrementUniqueCount()
        self.pollution.setUnique(oblock)
        self.pollution.update(self.time)

        return miss

    def get_hir_size(self):
        #print("in the dlir hir size method")
        #print(len(self.q))
        return len(self.q)