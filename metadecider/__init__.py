# stdlib
import itertools as it
# local
from hedge import Hedge
import antmath
import stats
#
import clump
import defend
import explore
import march
import gather


'''
Learning meta-decider for the 2011 Google AI Challenge.
Not yet submitted.

Stochastically learns which of several strategies are best via the hedge
algorithm.

(5)


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

An Environment is a dictionary: str --> dict
-- 'water' --> GoalDict
-- 'food' --> GoalDict
-- 'enemyhill' --> GoalDict
-- 'enemyant' --> GoalDict
-- 'myhill' --> GoalDict
-- 'myant' --> GoalDict
-- 'mydead' --> GoalDict

'''


###############################################################################


class Decider(object):
    '''Decider object as required by protocol.py.'''

    def __init__(self, logfn=None):
        self.log = logfn
        self.__think = None

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.__think = meta(self.log, game)
        self.__think.next()

    def think(self, water, food, enemyhill, enemyant, myhill, myant, mydead):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        return self.__think.send({
            'water'     :water,
            'food'      :food,
            'enemyhill' :enemyhill,
            'enemyant'  :enemyant,
            'myhill'    :myhill,
            'myant'     :myant,
            'mydead'    :mydead,
        })


###############################################################################


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
        }
        self.envdirt = set()
        for row in size[0]:
            for col in size[1]:
                self.envdirt.add((row, col))
        # ant perspective data
        self.persp = { # map: wrapped Loc --> [map: unwrapped Loc --> metadata]
            'food'      :{},
            'enemyhill' :{},
            'enemyant'  :{},
            'myhill'    :{},
            'myant'     :{},
        }
        self.perspdirt = {}
        # data for iteration
        self.myloc = {} # loc --> id, oldloc
        self.myid = {} # id --> loc, oldloc
        # delicious curry
        self.wrap = lambda loc: antmath.wrap_loc(loc, self.size)
        self.allinradius = lambda loc: antmath.allinradius(self.rad, loc)
        # functions for lazy people
        self.dist2 = lambda a, b: antmath.distance2(a, b)
        self.tonari = lambda loc: antmath.neighbors(loc)
        # actually useful functions
        self.wrapiter = lambda seq: (self.wrap(loc) for loc in seq)

    def update_env(self, water, food, enemyhill, enemyant, myhill, myant):
        # environment data
        self.env = {
            'food'      :food,
            'enemyhill' :enemyhill,
            'enemyant'  :enemyant,
            'myhill'    :myhill,
            'myant'     :myant,
        }
        for loc in water.iterkeys():
            self.envdirt.discard(loc)
        # ant perspective data
        for apm in self.persp.itervalues():
            apm.clear()
        # data for iteration
        self.myloc = myant
        self.myid = {aI: (aN, aO) for aN, (aI, aO) in myant.iteritems()}

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


###############################################################################


def meta(logfn, game):

    # experts (generators)
    experts = [e(logfn, game) for e in (gather.gendist)]
##               (clump.gendist, march.gendist, gather.gendist, defend.gendist,
##                explore.gendist)]
    for e in experts:
        e.next()

    # learner (generator)
    hedge = Hedge(0.9, len(experts))
    faith = hedge.next()
    loss = [0] * len(experts)

    # environment
    env = LazyEnvDigest((game['rows'], game['cols']), game['viewradius'])

    # loop
    while True:

        # query each strategy to impose a distribution over all ants
        # eg:
        #   strategy1 =
        #               ant1 = { n:50%, e:50% }
        #               ant2 = { e:100% }
        #   strategy2 =
        #               ant1 = { n:100% }
        #               ant2 = { e:75%, =:25% }
        dists = [e.send(env) for e in experts]
        assert all(sd.viewkeys() ^ env.myid == set() and \
                   all(1.0 == fsum(ad.itervalues()) \
                       for ad in sd.itervalues()) \
                   for sd in dists)
        # assert: strategies produce distributions (sum to 1) over _all_ ants

        # take the weighted linear combination over distributions
        # eg:
        #   faith =
        #           strategy1 = 0.8
        #           strategy2 = 0.2
        #   lincomb =
        #           ant1 = { n:60%, e:40% }
        #           ant2 = { e:95%, =:5% }
        lincomb = {aI: {vect: (fsum((f * d[aI][vect]) \
                                    for f, d in it.izip(faith, dists)),
                               ((f * d[aI][vect]) for f, d in it.izip(faith, dists))
                               )
                        for vect in list('NESW=')} \
                   for aI in env.myid}
        #if aI in d and vect in d[aI]
        assert lincomb.viewkeys() ^ env.myid == set() and \
               all(1.0 == fsum(v[0] for v in d.itervalues()) \
                   for d in lincomb.itervalues())
        # assert: lincomb is a distribution (sum to 1) over _all_ ants

        # linear combination
        {v: stats.dotprod(faith, (d['N'] for d in antx-dists)) \
         for v in list('NESW=')}

        # generate one random number per ant to decide where to go
        # store decisions and weights until next round
        e = yield myant
        env.update_env(e['water'], e['food'], e['enemyhill'], e['enemyant'],
                       e['myhill'], e['myant'])
        # figure out whether each ant's action was good or bad
        # generate a loss value for each ant relative to the number of ants
        # -- do we need to weight losses according to last turn's weights? no...
        # -- indicate loss for strategy(s) which were followed for this ant
