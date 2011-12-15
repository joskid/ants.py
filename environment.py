# stdlib
import datetime
import random
import itertools
# local
import antmath as am


'''
Contain the environment dictionaries. Digest ant perspectives lazilly. Rock.

A Size is a tuple:
-- integer - height
-- integer - width

A wLoc is a tuple:
-- integer - row location
-- integer - column location
Must be a location inside the borders of the actual map.

An unwLoc is a wLoc without the restriction that the location must be within the
map borders. Negative values and those greater than the Size of the map are both
okay.

A GoalDict is a dictionary: wLoc --> any
Maps locations to goal information.

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

    def __init__(self, size, radius, logfn):
        self.logfn = logfn
        self.size = size
        self.rad = radius
        self.rad2 = radius ** 2
        self.nneR = set(xrange(int(round(self.rad)),
                               int(round(self.size[0] - self.rad))))
        self.nneC = set(xrange(int(round(self.rad)),
                               int(round(self.size[1] - self.rad))))
        # environment data
        self.env = {            # wLoc --> metadata
            'water'     :{},
            'food'      :{},
            'enemyhill' :{},
            'enemyant'  :{},
            'myhill'    :{},
            'myant'     :{},
            'mydead'    :{},
        }
        self.rays = {}          # wLoc, wLoc --> bool
        self.envwater = set()
        self.__myid = None      # id --> wLoc, old_wLoc
        self.__mydeadid = None  # id --> wLoc, old_wLoc
        # ant perspective data
        self.persp = {          # wLoc --> (bool, list<Goal>)
            'water'     :{},
            'food'      :{},
            'enemyhill' :{},
            'enemyant'  :{},
            'myhill'    :{},
            'myant'     :{},
            'mydead'    :{},
        }
        self.supplemental = {}  # moves to supplement partial strategies

    #
    # curried

    def wrap(self, loc):
        return am.wrap_loc(loc, self.size)

    def unwrap(self, a, b):
        if self.not_near_edge(a):
            return b
        else:
            d2, unwr = am.nearest_unwrapped_loc(a, self.size, b)
            return unwr

    def allinradius(self, loc):
        return am.allinradius(self.rad, loc)

    #
    # shortened

    @staticmethod
    def dist2(a, b):
        return am.distance2(a, b)

    @staticmethod
    def tonari(loc):
        return am.neighbors(loc)

    #
    # utility

    def wrapiter(self, seq):
        return (self.wrap(loc) for loc in seq)

    def not_near_edge(self, loc):
        r, c = loc
        return r in self.nneR and c in self.nneC

    @staticmethod
    def int(loc):
        r, c = loc
        return int(r), int(c)

    #
    # api

    def update_env(self,
                   water, food, enemyhill, enemyant, myhill, myant, mydead):
        # environment data
        self.env = {
            'water'     :water,
            'food'      :food,
            'enemyhill' :enemyhill,
            'enemyant'  :enemyant,
            'myhill'    :myhill,
            'myant'     :myant,
            'mydead'    :mydead,
        }
        self.envwater = self.envwater | water.viewkeys()
        self.__myid = None
        self.__mydeadid = None
        # ant perspective data
        for apm in self.persp.itervalues():
            apm.clear()
        self.supplemental.clear()

    @property
    def water(self):
        return self.env['water']

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
            self.__myid = {
                aI: (aN, aO) for aN, (aI, aO) in self.myant.iteritems()}
        return self.__myid

    @property
    def mydeadid(self):
        if self.__mydeadid is None:
            self.__mydeadid = {
                aI: (aN, aO) for aN, (aI, aO) in self.mydead.iteritems()}
        return self.__mydeadid

    def digest(self, key, aloc):
        '''Digest an ant's environment for object presence.
        str wLoc --> list<Goals>
        '''
        aloc = self.wrap(aloc)
        apm = self.persp[key] # wLoc --> (bool, list<Goal>)
        if aloc not in apm:
            goals = [] # list<Goal>
            apm[aloc] = False, goals
            for gloc in self.env[key]:
                #gloc = self.unwrap(aloc, gloc)
                d2 = self.dist2(aloc, gloc)
                if d2 <= self.rad2:
                    goals.append((d2, gloc))
            if key == 'myant' and goals and aloc == goals[0][1]:
                goals.pop(0)
            goals.sort()
        return apm[aloc][1]

##    def ray(self, origin, target):
##        '''Is there a direct path from the origin to the target?'''
##        origin = self.wrap(self.int(origin))
##        target = self.unwrap(origin, self.int(target))
##        try:
##            # return a stored answer
##            return self.rays[origin, target]
##        except KeyError:
##            if self.dist2(origin, target) > self.rad2:
##                # don't check long paths
##                self.rays[origin, target] = None
##            else:
##                # check path
##                ... = self.__ray(origin, target, set())
##        return self.rays[origin, target]
##
##
##
##        # remember the result
##        for co, ct in itertools.izip(o[:-1], t[:-1]):
##            self.rays[co, ct] = result
##
##        return self.rays[origin, target]
##
##    def __ray(self, origin, target):
##        origin = self.wrap(origin)
##        target = self.unwrap(origin, target)
##        if origin == target:
##            return []
##        else:
##            v1, v2 = am.naive_dir(origin, target)
##            n1 = self.wrap(am.displace_loc(v1, origin))
##            n2 = self.wrap(am.displace_loc(v2, origin))
##            if n1 not in self.water:                
##            elif n2

    def ray(self, origin, target):
        '''Is there a direct path from the origin to the target?'''
        origin = self.wrap(self.int(origin))
        target = self.unwrap(origin, self.int(target))

        # return a stored answer
        try:
            return self.rays[origin, target]
        except KeyError:
            pass

        # trivial
        if origin == target:
            return True

        # don't check long paths
        if self.dist2(origin, target) > self.rad2:
            return False

        # check path
        o = [origin]
        t = [target]
##        while :
        for _ in xrange(150):
            v, _ = am.naive_dir(o[-1], t[-1])
            o.append(self.wrap(am.displace_loc(v, o[-1])))
            t.append(self.unwrap(o[-1], t[-1]))
            if o[-1] == t[-1]:
                break

        # did the path pass through water?
        if self.water.viewkeys() & o:
            return False

        # remember the result
        for co, ct in itertools.izip(o[:-1], t[:-1]):
            self.rays[co, ct] = True

        return self.rays[origin, target]

##    def supplement(self, moves):
##        if not self.supplemental:
##            for aI, (aN, aO) in self.myid.iteritems():
##                self.supplemental[aI] = '='#random.choice('NESW')
##        m = self.supplemental.copy()
##        m.update(moves)
##        return m
  
    def supplement(self, moves):
        return moves
