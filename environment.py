# local
import antmath


'''
Contain the environment dictionaries. Digest ant perspectives lazilly. Rock.

A Size is a tuple:
-- integer - height
-- integer - width

A Loc is a tuple:
-- integer - row location
-- integer - column location

A GoalDict is a dictionary: Loc --> any
-- maps locations to goal information

An Goal is a tuple:
-- integer - squared distance goal is from onlooker
-- Loc - nearest location of goal relative to onlooker

An AntPerspective is a tuple:
-- Loc - location of this ant (onlooker)
-- list<Goal> - goals within viewradius2 of this ant

'''


class LazyEnvDigest(object):
    '''Digest the environment into ant perspectives when requested.

    Perspectives persist until the environment is updated.

    '''

    def __init__(self, size, radius):
        self.size = size
        self.rad = radius
        self.rad2 = radius ** 2
        # environment data
        self.env = { # map: wrapped Loc --> metadata
            'food'      :{},
            'enemyhill' :{},
            'enemyant'  :{},
            'myhill'    :{},
            'myant'     :{},
            'mydead'    :{},
        }
        self.envdirt = set()
        for row in xrange(size[0]):
            for col in xrange(size[1]):
                self.envdirt.add((row, col))
        self.__myid = None # id --> loc, oldloc
        self.__mydeadid = None # id --> loc, oldloc
        # ant perspective data
        self.persp = { # map: wrapped Loc --> [map: unwrapped Loc --> metadata]
            'food'      :{},
            'enemyhill' :{},
            'enemyant'  :{},
            'myhill'    :{},
            'myant'     :{},
            'mydead'    :{},
        }
        self.perspdirt = {}
        # delicious curry
        self.wrap = lambda loc: antmath.wrap_loc(loc, self.size)
        self.allinradius = lambda loc: antmath.allinradius(self.rad, loc)
        # functions for lazy people
        self.dist2 = lambda a, b: antmath.distance2(a, b)
        self.tonari = lambda loc: antmath.neighbors(loc)
        # actually useful functions
        self.wrapiter = lambda seq: (self.wrap(loc) for loc in seq)

    def update_env(self, water, food, enemyhill, enemyant, myhill, myant,
                   mydead):
        # environment data
        self.env = {
            'food'      :food,
            'enemyhill' :enemyhill,
            'enemyant'  :enemyant,
            'myhill'    :myhill,
            'myant'     :myant,
            'mydead'    :mydead,
        }
        for loc in water.iterkeys():
            self.envdirt.discard(loc)
        self.__myid = None # id --> loc, oldloc
        # ant perspective data
        for apm in self.persp.itervalues():
            apm.clear()

    @property
    def food(self):
        return self.env['food']

    @property
    def enemyhill(self):
        return self.env['enemyhill']

    @property
    def enemyant(self):
        return self.env['enemyant']

    @property
    def myhill(self):
        return self.env['myhill']

    @property
    def myant(self):
        return self.env['myant']

    @property
    def mydead(self):
        return self.env['mydead']

    @property
    def myid(self):
        if self.__myid is None:
            self.__myid = {aI: (aN, aO) \
                           for aN, (aI, aO) in self.myant.iteritems()}
        return self.__myid

    @property
    def mydeadid(self):
        if self.__mydeadid is None:
            self.__mydeadid = {aI: (aN, aO) \
                               for aN, (aI, aO) in self.mydead.iteritems()}
        return self.__myid

    def digest(self, key, aloc):
        '''Convert a colony-wide view of a map to an ant's view.
        str Loc --> list<Goal>

        '''
        aloc = self.wrap(aloc)
        # create a persistent view of reachable dirt within the radius
        if aloc not in self.perspdirt:
            self.perspdirt[aloc] = bfs = {}
            fringe = [(aloc, 0.0)]
            while fringe:
                loc, dist2 = fringe.pop(0)
                bfs[loc] = dist2
                fringe.extend(
                    (n, self.dist2(aloc, n)) for n in self.tonari(loc) \
                    if self.wrap(n) in self.envdirt and n not in bfs \
                    and self.dist2(aloc, n) <= self.rad2)
        # create a short-term view of goals on that dirt
        apm = self.persp[key]
        if aloc not in apm:
            apm[aloc] = sorted(
                (dist2, gloc) \
                for gloc, dist2 in self.perspdirt[aloc].iteritems() \
                if self.wrap(gloc) in self.env[key])
        return apm[aloc]
