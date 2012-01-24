# stdlib
from datetime import datetime as DateTime
from math import sqrt as math_sqrt
from random import seed as random_seed
from collections import defaultdict as collections_defaultdict
from itertools import repeat as itertools_repeat
# local
import antmath


'''
Implements a protocol handler for the 2011 Google AI Challenge "ants" game.

Provides a high level interface for ant bots to be developed quickly.

Ant property identifier suffixes:
    O=oldloc
    N=newloc
    I=identity
    V=vectorlist
    D=vector(direction)

'''


###############################################################################


class Bot(object):

    def __init__(self, decider, logfn=None):
        '''Takes a Decider instance which makes decisions about the game.
        Optionally takes a function to log strings.

        The Decider must have the following methods:

            def start(game):

                -- will be called at the start of the game
                -- the argument is a dictionary with the following keys:

                    loadtime        (milliseconds)
                    turntime        (milliseconds)
                    rows            (height)
                    cols            (width)
                    turns           (turn limit)
                    viewradius2     (squared)
                    viewradius
                    attackradius2   (squared)
                    attackradius
                    spawnradius2    (squared)
                    spawnradius
                    player_seed     (random seed)

            def think(water, food, enemyhill, enemyant, myhill, myant, mydead):

                -- will be called for each turn
                -- arguments are dictionaries mapping (row, col) locations to
                   metadata:

                    water       True
                    food        True
                    enemyhill   int         (owner)
                    enemyant    int         (owner)
                    myhill      bool        (active and visible)
                    myant       int, loc    (id, oldloc)
                    mydead      int, loc    (id, oldloc)

                -- return value must be a dictionary having the same set of
                   keys as myant, each mapping to a prioritized list of vectors
                   from this list: N, E, S, W, =

        '''
        self.decider = decider
        self.logfn = logfn
        # message handlers
        self.handlers = collections_defaultdict(lambda: lambda *args: None)
        for msg in ['player_seed','loadtime','turntime','turns','rows','cols']:
            self.handlers[msg] = self.handle_number
        for msg in ['attackradius2','spawnradius2','viewradius2']:
            self.handlers[msg] = self.handle_radius
        self.handlers['ready'] = lambda *args   : self.pregame() or ['go']
        self.handlers['turn'] = lambda msg, num : self.presense(msg, num)
        self.handlers['go'] = lambda *args      : self.postsense() + ['go']
        self.handlers['w'] = lambda msg, r, c   : self.sense_water((r, c))
        self.handlers['f'] = lambda msg, r, c   : self.sense_food ((r, c))
        self.handlers['h'] = lambda msg, r, c, o: self.sense_hill((r, c), o)
        self.handlers['a'] = lambda msg, r, c, o: self.sense_ant ((r, c), o)
        self.handlers['d'] = lambda msg, r, c, o: self.sense_dead((r, c), o)
        # game details
        self.game = {}
        # game state (never cleared)
        self.anttotal   = 0
        self.water      = {} # map loc --> True
        self.myhill0    = {} # map loc --> False
        # turn state (cleared each turn; usually in presense)
        self.timer      = None
        self.turn       = None
        self.food       = {} # map loc --> True
        self.enemyhill  = {} # map loc --> int
        self.enemyant   = {} # map loc --> int
        self.myhill     = {} # map loc --> True
        self.myant      = {} # map loc --> int, loc (id, oldloc)
        self.mydead     = {} # map loc --> int, loc (id, oldloc)
        self.antplans   = {} # map loc (new) --> loc, int, str, list<str>
        #                                        (old, id, vector, vectors)

    def handle(self, s):
        args = s.split()
        msg = args.pop(0)
        return self.handlers[msg](msg, *map(int, args))

    def handle_number(self, msg, val):
        self.game[msg] = int(val)

    def handle_radius(self, msg, val):
        self.game[msg] = int(val)
        self.game[msg[:-1]] = math_sqrt(int(val))

    def pregame(self):
        random_seed(self.game['player_seed'])
        self.decider.start(self.game)

    def presense(self, msg, num):
        self.timer = DateTime.now()
        self.turn = num
        self.logfn and self.logfn('TURN #{} presense'.format(num))
        self.food.clear()
        self.enemyhill.clear()
        self.enemyant.clear()
        self.myhill.clear()
        self.myant.clear()
        self.mydead.clear()
        if self.logfn:
            for k, v in self.antplans.iteritems():
                self.logfn('plan {} <-- {}'.format(k, v))

    def sense_water(self, loc):
        self.water[loc] = True

    def sense_food(self, loc):
        self.food[loc] = True

    def sense_hill(self, loc, owner):
        if owner == 0:
            self.myhill[loc] = True
            if self.turn == 1:
                self.myhill0[loc] = False
        else:
            self.enemyhill[loc] = owner

    def sense_ant(self, loc, owner):
        if owner == 0:
            self.myant[loc] = True
        else:
            self.enemyant[loc] = owner

    def sense_dead(self, loc, owner):
        if owner == 0:
            self.mydead[loc] = True

    def recognize_moved(self, loc):
        '''Recognize an ant which moved. Clear its plan.
        Return a 2-tuple of loc & plan.

        '''
        if loc in self.antplans:
            return loc, self.antplans.pop(loc)
        # unrecognized
        return None, 4 * (None,)

    def recognize_stuck(self, loc):
        '''Recognize an ant which failed to move. Clear its plan.
        Return a 2-tuple of loc & plan.

        '''
        fail = [f for f in antmath.neighbors(loc) \
                if (self.wrap(f) in self.antplans and
                    self.antplans[f][0] == loc)]
        if fail:
            return fail[0], self.antplans.pop(fail[0])
        # unrecognized
        return None, 4 * (None,)

    @staticmethod
    def recognize(recognizer, sensor, fromdict, todict):
        '''Sense the ants in fromdict that the recognizer finds.'''
        for loc in fromdict.keys():
            plan = recognizer(loc)
            if plan[0]:
                del fromdict[loc]
                sensor(todict, plan)

    def gen_sensor(self, msg=''):
        #staticmethod
        def fn(todict, plan):
            aN, (aO, aI, aD, aV) = plan
            todict[aN] = aI, aO
            if self.logfn:
                if aN == aO and aD != '=':
                    self.logfn('Ant #{} at {} -FAIL{}-> {}{}'.\
                               format(aI, aO, aD, aN, ' ' + msg))
                else:
                    self.logfn('Ant #{} at {} -{}-> {}{}'.\
                               format(aI, aO, aD, aN, ' ' + msg))
        return fn

    def postsense(self):
        self.logfn and self.logfn('TURN #{} postsense '.format(self.turn))
        #
        # recognize our dead ants
        mydead = {}
        self.recognize(self.recognize_moved, self.gen_sensor('and died'),
                       self.mydead, mydead)
        self.recognize(self.recognize_stuck, self.gen_sensor('and died'),
                       self.mydead, mydead)
        #assert self.mydead == {} # all were recognized
        self.mydead = mydead
        del mydead # don't use the local ref
        #
        # recognize our living ants
        myant = {}
        self.recognize(self.recognize_moved, self.gen_sensor(), self.myant,
                       myant)
        self.recognize(self.recognize_stuck, self.gen_sensor(), self.myant,
                       myant)
        # still unrecognized ants must have just been born
        for loc in self.myant.keys():
            #assert loc in self.myhill # ants must be born on an anthill
            del self.myant[loc]
            aI = self.anttotal
            self.anttotal += 1
            myant[loc] = aI, loc
            self.logfn and self.logfn('Ant #{} at {} born'.format(aI, loc))
        #assert self.myant == {} # all were recognized
        self.myant = myant
        del myant # don't use the local ref
        #
        # all living and dead ants are recognized
        #assert self.antplans == {}
        #
        # combine the original hill list with the current hill list
        hills = {}
        hills.update(self.myhill0) # adds false for all my hills
        hills.update(self.myhill)  # adds true for my visible and active hills
        #
        # query where ants should go
        decidertime = DateTime.now()
        moves = self.decider.think(
            self.water.copy(),
            self.food,
            self.enemyhill,
            self.enemyant,
            hills,
            self.myant.copy(),
            self.mydead,
        )
        decidertime = (DateTime.now() - decidertime).total_seconds()
        #
        # filter moves to only ants that actually exist
        moves = {loc:vectors for loc, vectors in moves.iteritems() \
                 if loc in self.myant}
        #
        # add a 'stay' order for each ant that was left-out
        # copy ant ids from myant to moves
        for loc, (antid, oldloc) in self.myant.iteritems():
            if loc not in moves:
                moves[loc] = itertools_repeat('=')
            elif type(moves[loc]) == type([]):
                moves[loc] = (v for v in moves[loc])
            moves[loc] = (antid, moves[loc])
        #
        # def for use later:
        # get next move which doesn't place the ant on water or food
        def poporder(oldloc, vectors):
            try:
                vector = vectors.next()
            except StopIteration:
                vector = '='
            newloc = self.wrap(antmath.displace_loc(vector, oldloc))
            return (newloc, vector) \
                   if newloc not in self.water and newloc not in self.food \
                   else poporder(oldloc, vectors)
        #
        # assign ants to locations; resolve conflicts for the same location
        # gale-shapley stable matching algorithm
        # - single men "moves" oldloc:(identity,[vector])
        # - single women "antplans" any key which isn't set
        # - couples "antplans" newloc:(oldloc,identity,vector,[vector])
        # sorry about the long lines here...
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
            self.logfn('''AntCt: {} Time: {:f}ms of {:.2f}ms; {:f}ms decider,
                          {:f}ms protocol'''.\
                          format(len(self.antplans), totaltime, maxtime,
                          decidertime, totaltime - decidertime))
        #
        # issue orders to ants who are to move
        return ['o {} {} {}'.format(row, col, vector) \
                for newloc, ((row, col), identity, vector, vectors) \
                in self.antplans.iteritems() \
                if vector != '=']

    def wrap(self, loc):
        '''Finds the true on-map coordinates of an unwrapped location.'''
        return antmath.wrap_loc(loc, (self.game['rows'], self.game['cols']))

###############################################################################
