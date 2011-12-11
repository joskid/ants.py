# local
import antmath


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
        # curried functions
        self.wrap = lambda loc: antmath.wrap_loc(loc, self.size)
        self.allinradius = lambda loc: antmath.allinradius(self.rad, loc)
        # shortened functions
        self.dist2 = lambda a, b: antmath.distance2(a, b)
        self.tonari = lambda loc: antmath.neighbors(loc)
        # utility functions
        self.wrapiter = lambda seq: (self.wrap(loc) for loc in seq)

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

##    def bfsdigest(self, key, aloc):
##        '''Expensive. Digest an ant's environment for objective reachability.
##        str wLoc --> list<Goals>
##        '''
##        apm = self.persp[key] # wLoc --> [wLoc --> (bool, list<Goal>)]
##
##        self.digest(key, aloc)
##
##        bfs, ap = apm[aloc]
##        if not bfs:
##            fringe = [(aloc, 0.0)]
##            bfs = set()
##            apl[aloc] = []
##            while fringe:
##                loc, dist2 = fringe.pop(0)
##                bfs.add(loc)
##                if self.wrap(loc) in self.env[key]:
##                    apl[aloc].append((dist2, loc))
##                fringe.extend(
##                    (n, self.dist2(aloc, n)) \
##                    for n in self.tonari(loc) \
##                    if n not in bfs and self.wrap(n) not in self.envwater \
##                    and self.dist2(aloc, n) <= self.rad2
##                )
##            apl[aloc].sort()
##            # mark it with "true"
##
##        # a bfs-map is present
##        return apm[aloc][1]
##
##
####            apm[aloc] = sorted(
####                (dist2, gloc) \
####                for gloc, dist2 in 
######                for gloc, dist2 in self.perspdirt[aloc].iteritems() \
####                if self.wrap(gloc) in self.env[key])
##        return apl[aloc]
##        pass

    def digest(self, key, aloc):
        '''Digest an ant's environment for objective presence.
        str wLoc --> list<Goals>
        '''
        apm = self.persp[key] # wLoc --> (bool, list<Goal>)
        if aloc not in apm:
            apm[aloc] = False, sorted((self.dist2(aloc, gloc), gloc) \
                                      for gloc in self.env[key] \
                                      if self.dist2(aloc, gloc) <= self.rad2)
        return apm[aloc][1]

##    def __reachable_dirt(self, aloc):
##        '''Create a persistent view of reachable dirt within the radius.'''
##        self.perspdirt[aloc] = bfs = {}
##        fringe = [(aloc, 0.0)]
##        while fringe:
##            loc, dist2 = fringe.pop(0)
##            bfs[loc] = dist2
##            fringe.extend(
##                (n, self.dist2(aloc, n)) for n in self.tonari(loc) \
##                if self.wrap(n) in self.envdirt \
##                and n not in bfs \
##                and self.dist2(aloc, n) <= self.rad2
##            )
##        self.logfn and self.logfn(
##            'reachable dirt {} len {}'.format(aloc, len(bfs)))
