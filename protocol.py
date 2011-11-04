# stdlib
from math import sqrt
from random import seed
from collections import defaultdict


###############################################################################


MAPCHARS = {
    'water' : lambda o: '#',
    'food'  : lambda o: '*',
    'hill'  : lambda o: str(o),
    'ant'   : lambda o: chr(97 + o),
    'see'   : lambda o: ' ',
}


DISPLACE = {
    'N': lambda loc: (loc[0] - 1, loc[1]    ),
    'E': lambda loc: (loc[0]    , loc[1] + 1),
    'S': lambda loc: (loc[0] + 1, loc[1]    ),
    'W': lambda loc: (loc[0]    , loc[1] - 1),
    '=': lambda loc: loc,
}


###############################################################################


def inradius(a, radius2, b):
    '''Is loc 'a' within the squared-radius of loc 'b'?'''
    return (locb[0] - loca[0]) ** 2 + \
           (locb[1] - loca[1]) ** 2 <= radius2


def allinradius(radius, radius2, loc):
    '''Yield all values within the radius of the location.

    radius  -- integer radius
    radius2 -- integer squared-radius

    '''
    for r in xrange(-radius, radius + 1):
        for c in xrange(-radius, radius + 1):
            locb = loc[0] + r, loc[1] + c
            if inradius(loc, radius2, locb):
                yield locb


###############################################################################


class Bot(object):

    def __init__(self, decider, logfn=None):
        '''Takes an object, decider, which makes decisions about the game.
        Optionally takes a function which logs any strings applied to it.

        The decider must have the following methods:

            def start(game):
                pass

            def think(dirt, food, enemyhill, enemyant, myhill, myant):
                pass

        start

        -- will be called at the start of the game
        -- arguments are as follows:

            A dictionary, game, with the following keys:

                loadtime        (milliseconds)
                turntime        (milliseconds)
                rows            (height)
                cols            (width)
                turns           (turn limit)
                viewradius2
                viewradius
                attackradius2
                attackradius
                spawnradius2
                spawnradius
                player_seed

        think

        -- will be called for each game turn
        -- arguments are as follows:

            Each argument is a dictionary mapping (row, col) locations to
            either boolean or integer values.

            dirt        True
            food        True
            enemyhill   int (owner)
            enemyant    int (owner)
            myhill      True
            myant       True

        -- return value must be as follows:
        
            A dictionary having the same set of keys as myant, each of which
            maps to a list of prioritized vectors including 'N', 'E', 'S', 'W',
            and '=' (indicating no movement).

        '''
        self.decider = decider
        self.logfn = logfn
        # message handlers
        self.handlers = collections.defaultdict(lambda: lambda *args: None)
        for msg in ['player_seed','loadtime','turntime','turns','rows','cols']:
            self.handlers[msg] = self.handle_number
        for msg in ['attackradius2','spawnradius2','viewradius2']:
            self.handlers[msg] = self.handle_radius
        self.handlers['ready'] = lambda *args: self.pregame() or ['go']
        self.handlers['turn'] = lambda *args: self.presense()
        self.handlers['go'] = lambda *args: self.postsense() + ['go']
        self.handlers['w'] = lambda msg, r, c   : self.sense_water((r, c))
        self.handlers['f'] = lambda msg, r, c   : self.sense_food ((r, c))
        self.handlers['h'] = lambda msg, r, c, o: self.sense_hill((r, c), o)
        self.handlers['a'] = lambda msg, r, c, o: self.sense_ant ((r, c), o)
        self.handlers['d'] = lambda msg, r, c, o: None
        # game details
        self.game = {}
        # sensory maps { ... (row, col): or<bool,int>, ... }
        self.dirt      = {}
        self.food      = {}
        self.enemyhill = {}
        self.enemyant  = {}
        self.myhill    = {}
        self.myant     = {}

    def handle(self, s):
        args = s.split()
        msg = args.pop(0)
        return self.handlers[msg](msg, *map(int, args))

    def handle_number(self, msg, val):
        self.game[msg] = int(val)

    def handle_radius(self, msg, val):
        self.game[msg] = int(val)
        self.game[msg[:-1]] = int(math.sqrt(int(val)))

    def pregame(self):
        random.seed(self.game['player_seed'])
        for row in xrange(self.game['rows']):
            for col in xrange(self.game['cols']):
                self.dirt[row, col] = True
        self.decider.start()

    def sense_water(self, loc):
        del self.dirt[loc]

    def sense_food(self, loc):
        self.food[loc] = True

    def sense_hill(self, loc, owner):
        if owner == 0:
            self.myhill[loc] = True
        else:
            self.enemyhill[loc] = owner

    def sense_ant(self, loc, owner):
        if owner == 0:
            self.myant[loc] = True
        else:
            self.enemyant[loc] = owner

    def presense(self):
        self.food.clear()
        self.enemyhill.clear()
        self.enemyant.clear()
        self.myhill.clear()
        self.myant.clear()

    def postsense(self):
        if self.logfn is not None:
            self.logfn(self.draw_map())
        # decide where ants should go
        thoughts = self.decider.think(self.dirt.copy(), self.food,
                                      self.enemyhill, self.enemyant,
                                      self.myhill, self.myant)
        # apply next-turn decisions
        final = reconcile(thoughts)
        # issue orders to ants who are to move
        return [' '.join(['o', oldloc[0], oldloc[1], vector]) \
                for newloc, (oldloc, vector) in final.iteritems() \
                if newloc != oldloc]

##    def draw_map(self, vis=None):
##        # determine what is currently visible
##        visible = {}
##        for antloc in self.mynow:
##            for loc in Bot.allinradius(self.game['viewradius'], self.game['viewradius2'], *antloc):
##                visible[loc] = True
##        m = {} if vis is None else {loc:Thing(SEEE) for loc in vis}
##        m.update(self.static)
##        m.update(self.immobile)
##        m.update(self.theirs)
##        m.update(self.mynow)
##        s = []
##        for r in xrange(self.game['rows']):
##            s.append([])
##            for c in xrange(self.game['cols']):
##                try:
##                    thing = m[r, c]
##                except KeyError:
##                    s[-1].append('-')
##                else:
##                    s[-1].append(MAPCHARS[thing.type](thing.owner))
##            s[-1] = ''.join(s[-1])
##        return '\n'.join(s)

###############################################################################

# a vector is one of:
# -- 'N' indicating north
# -- 'S' indicating south
# -- 'E' indicating east
# -- 'W' indicating west
# -- '=' indicating no movement

# a location is a tuple<number,number>
# -- first number represents row
# -- second number represents column

def reconcile(m):
    '''{location: [vector]}
    --> {location: (location, vector)}'''
    def f0(m, f):
        '''[(location, [vector])] {location: (location, vector)}
        --> {location:tuple<location,vector>}'''
##        def f1(m):
##            pass
##        return f1()
    return f0(m.items(), {})
##        final = {}
##        for loc, vectors in thoughts.iteritems():
##            def resolve(final, loc, vectors):
##                
##            while vectors:
##                v = vectors.pop()
##                nl = DISPLACE[](loc)
##        # { ... newloc : (ant, oldloc, vector), ... }
##        self.mynext.clear()
##        for oldloc, vects in dirs.iteritems():
##            # consume vects until ant has a next location
##            # if blocked by water, 
##            newloc = DISPLACE[vect](oldloc)
##            # if blocked by water or another ant's move, stay put
##            if newloc in self.mynext or newloc in self.static:
##                self.mynext[oldloc] = ant, oldloc, '!' + vect
##            else:
##                self.mynext[newloc] = ant, oldloc, vect

###############################################################################

if __name__ == '__main__':
    import doctest
    doctest.testmod()
