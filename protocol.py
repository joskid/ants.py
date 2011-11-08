# stdlib
from datetime import datetime as DateTime
from math import sqrt as math_sqrt
from random import seed as random_seed
from collections import defaultdict as collections_defaultdict


# ant property identifier suffixes:
#   O=oldloc
#   N=newloc
#   I=identity
#   V=vectorlist
#   D=vector(direction)


DISPLACE = {
    'N': lambda loc: (loc[0] - 1, loc[1]    ),
    'E': lambda loc: (loc[0]    , loc[1] + 1),
    'S': lambda loc: (loc[0] + 1, loc[1]    ),
    'W': lambda loc: (loc[0]    , loc[1] - 1),
    '=': lambda loc: loc,
}


###############################################################################


class Bot(object):

    def __init__(self, decider, logfn=None):
        '''Takes an object, decider, which makes decisions about the game.
        Optionally takes a function which logs any strings applied to it.

        The decider must have the following methods:

            def start(game):
                pass

            def think(water, food, enemyhill, enemyant, myhill, myant):
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

            Most arguments are dictionaries mapping (row, col) locations to
            either boolean or integer values.

            water       True
            food        True
            enemyhill   int (owner)
            enemyant    int (owner)
            myhill      True
            myant       int (id), oldloc

            mydead      [int] (ids of dead ants)

        -- return value must be as follows:

            A dictionary having the same set of keys as myant, each of which
            maps to a list of prioritized vectors including 'N', 'E', 'S', 'W',
            and '=' (indicating no movement).

        '''
        self.decider = decider
        self.logfn = logfn
        # message handlers
        self.handlers = collections_defaultdict(lambda: lambda *args: None)
        for msg in ['player_seed','loadtime','turntime','turns','rows','cols']:
            self.handlers[msg] = self.handle_number
        for msg in ['attackradius2','spawnradius2','viewradius2']:
            self.handlers[msg] = self.handle_radius
        self.handlers['ready'] = lambda *args: self.pregame() or ['go']
        self.handlers['turn'] = lambda msg, num: self.presense(msg, num)
        self.handlers['go'] = lambda *args: self.postsense() + ['go']
        self.handlers['w'] = lambda msg, r, c   : self.sense_water((r, c))
        self.handlers['f'] = lambda msg, r, c   : self.sense_food ((r, c))
        self.handlers['h'] = lambda msg, r, c, o: self.sense_hill((r, c), o)
        self.handlers['a'] = lambda msg, r, c, o: self.sense_ant ((r, c), o)
        self.handlers['d'] = lambda msg, r, c, o: self.sense_dead((r, c), o)
        # game details
        self.game = {}
        self.turn = None
        self.timer = None
        # sensory maps { ... (row, col): or<bool,int>, ... }
        self.water     = {}
        self.food      = {}
        self.enemyhill = {}
        self.enemyant  = {}
        self.myhill    = {}
        self.myant     = {}
        self.mydead    = 0
        # ant state
        self.antcount = 1
        self.antplans  = {}

    def handle(self, s):
        args = s.split()
        msg = args.pop(0)
        return self.handlers[msg](msg, *map(int, args))

    def handle_number(self, msg, val):
        self.game[msg] = int(val)

    def handle_radius(self, msg, val):
        self.game[msg] = int(val)
        self.game[msg[:-1]] = int(math_sqrt(int(val)))

    def pregame(self):
        random_seed(self.game['player_seed'])
        self.decider.start(self.game)

    def sense_water(self, loc):
        self.water[loc] = True

    def sense_food(self, loc):
        self.food[loc] = True

    def sense_hill(self, loc, owner):
        if owner == 0:
            self.myhill[loc] = True
        else:
            self.enemyhill[loc] = owner

    def sense_ant(self, loc, owner):
        if owner == 0:
            if loc in self.antplans:
                # recognize it as the one which planned to move to loc
                # and got there successfully
                aO, aI, aD, aV = self.antplans[loc]
                del self.antplans[loc]
                self.myant[loc] = (aI, aO)
#                 self.logfn('Ant #{} at {} -{}-> {}'.format(
#                     aI, aO, aD, loc)) if self.logfn else None
            else:
                # no ant planned to move to loc...
                r, c = loc
                failed = [(n, self.antplans[n]) \
                          for n in [(r-1,c), (r+1,c), (r,c-1), (r,c+1)] \
                          if n in self.antplans \
                          and self.antplans[n][0] == loc]
                # failed is a list of ants who were at loc, and planned to be
                # somewhere adjacent to it
                for aN, (aO, aI, aD, aV) in failed:
                    # recognize it as the one which planned to move to loc
                    # but was blocked by the game system
                    assert len(failed) == 1 # because gale-shapley prevents
                    assert aO == loc # because we found it there..
                    del self.antplans[aN]
                    self.myant[loc] = (aI, aO)
#                     self.logfn('Ant #{} at {} -FAIL{}-> {}'.format(
#                         aI, aO, aD, aN)) if self.logfn else None
                    break
                else:
                    # recognize it as a new ant (hope it's on a hill!)
                    self.myant[loc] = aI, loc = (self.antcount, loc)
                    self.antcount += 1
#                     self.logfn('Ant #{} born at {}'.format(
#                         aI, loc)) if self.logfn else None
        else:
            self.enemyant[loc] = owner

    def sense_dead(self, loc, owner):
        if owner == 0:
#             self.logfn('Ant died at {}'.format(loc)) if self.logfn else None
            self.mydead += 1

    def presense(self, msg, num):
        self.timer = DateTime.now()
        self.turn = num
        if self.logfn:
            self.logfn('TURN ' + str(num))
        self.food.clear()
        self.enemyhill.clear()
        self.enemyant.clear()
        self.myhill.clear()
        self.myant.clear()
        self.mydead = 0

    def wrap(self, loc):
        '''Finds the true on-map coordinates of an unwrapped location.'''
        return loc[0] % self.game['rows'], loc[1] % self.game['cols']

    def postsense(self):
        self.logfn('DECIDER TURN '+str(self.turn)) if self.logfn else None
        assert self.mydead == len(self.antplans)
        #
        # query where ants should go
        decidertime = DateTime.now()
        moves = self.decider.think(
            self.water.copy(),
            self.food,
            self.enemyhill,
            self.enemyant,
            self.myhill,
            self.myant.copy(),
            [aI for aO, aI, aD, aV in self.antplans.itervalues()]
        )
        decidertime = (DateTime.now() - decidertime).total_seconds()
        #
        # filter orders for ants that don't exist
        # also append 'stay' to the end of every order vector
        moves = {loc:vectors + ['='] \
                 for loc, vectors in moves.iteritems() \
                 if loc in self.myant}
        #
        # add 'stay' orders for the left-out ants
        # also copy ant ids from myant to moves
        for loc, (antid, oldloc) in self.myant.iteritems():
            if loc not in moves:
                moves[loc] = ['=']
            moves[loc] = (antid, moves[loc])
        #
        # define a function to get the next valid vector in a list
        # pop is okay b/c vector lists end with '=' (which locations prefer)
        def poporder(oldloc, vectors):
            vector = vectors.pop(0)
            newloc = self.wrap(DISPLACE[vector](oldloc))
            return (newloc, vector) \
                   if newloc not in self.water and newloc not in self.food \
                   else poporder(oldloc, vectors)
        #
        # gale-shapley stable matching algorithm
        # - single men "moves" oldloc:(identity,[vector])
        # - single women "antplans" any key which isn't set
        # - couples "antplans" newloc:(oldloc,identity,vector,[vector])
        self.antplans.clear()
        while moves:
            for aO, (aI, aV) in moves.items():              # each ant "a"
                aN, aD = poporder(aO, aV)                   # proposes to a location
                if aN in self.antplans:                     # if the location is claimed
                    if aD == '=':                           #   but prefers "a"
                        bO, bI, bD, bV = self.antplans[aN]  #     get the claimant "b"
                        moves[bO] = bI, bV                  #     remove the claim of "b"
                        self.antplans[aN] = (aO, aI, aD, aV)#     set a claim for "a"
                        del moves[aO]                       #     "a" is no longer single
                else:                                       # if the location is free
                    self.antplans[aN] = (aO, aI, aD, aV)    #   set a claim for "a"
                    del moves[aO]                           #   "a" is no longer single
        #
        # log elapsed time
        if self.logfn:
            maxtime = self.game['turntime']
            decidertime *= 1000.0
            totaltime = (DateTime.now() - self.timer).total_seconds() * 1000.0
            self.logfn(
                'Ants: {} Time: {:f}ms of {:.2f}ms; {:f}ms decider, {:f}ms protocol'.format(
                len(self.antplans), totaltime, maxtime, decidertime, totaltime - decidertime))
        #
        # issue orders to ants who are to move
        return ['o {} {} {}'.format(row, col, vector) \
                for newloc, ((row, col), identity, vector, vectors) \
                in self.antplans.iteritems() \
                if vector != '=']

###############################################################################
