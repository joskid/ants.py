# stdlib
import random
from datetime import datetime as DateTime
# local
import protocol
import antmath


'''
Squad-based maze navigation decider for the 2011 Google AI Challenge.
Not yet submitted

Moves ants around a maze in groups of nine.

(4)
'''


class Decider(object):

    def __init__(self, logfn=None):
        self.g = {}
        self.l = logfn
        self.v = list('NESW')
        # s maps squad id to (node, center, exploration index)
        # { ... num:(loc, loc, ) ...}
        self.s = {}
        # m maps graph nodes to (, exploration stack)
        # { ... loc:(or<loc,None>, [vector]) ... }
        self.m = {}
        # h maps ant id to hill id

    def start(self, game):
        self.g.update(game)

    def think(self, dirt, food, enemyhill, enemyant, myhill, myant, mydead):
        myant = (
            (aN, aI, aO, min((self.unwrapped_dir(aN, loc) for loc in myhill))) \
            for aN, (aI, aO) in myant.iteritems()
        )
        return self.assignmoves


        d2, node = 




        moves = {}
        reg = {}

        # register existing squad ants, create new squads, kick non-squad ants
        for aN, (aI, aO) in myant.items():
            sI = aI / 9
            saI = aI % 9
            if sI in self.s:
                # if the ant is in a squad
                del myant[aN]
                reg[sI] = reg[sI] + [(aN, aO)] if sI in reg else [(aN, aO)]
            elif saI == 8:
                # elif the ant's squad just completed spawning
                d2, node = min([self.unwrapped_dir(aN, loc) for loc in self.m])
                self.s[sI] = (node, None)
            else:
                # else the ant is part of an incomplete squad
                del myant[aN]
                random.shuffle(self.v)
                moves[aN] = self.v[:]

        # register new squad ants
        for aN, (aI, aO) in myant.items():
            sI = aI / 9
            del myant[aN]
            reg[sI] = reg[sI] + [(aN, aO)] if sI in reg else [(aN, aO)]

        # assign moves to each squad of ants
        for sI, sA in reg.iteritems():
            sN, sC, sX = self.s[sI] # squad node, squad center, squad exploration stack
            nP, nX = self.m[sN] # node parent, node exploration stack
            # assign moves to squad members
            moves.update(self.movesquad(sC, sA, vnxt sN))

        return moves

    def nearest(self, origin, targets):
        return min([self.unwrapped_dir(origin, t) for t in targets])[1]

    def unwrapped_dir(self, origin, target):
        '''Find the shortest path to the target.

        Return closest unwrapped location and its distance squared as a tuple:
        (distance2, location)

        '''
        h = self.g['rows']
        w = self.g['cols']
        r, c = target
        options = [target, (r-h, c), (r+h, c), (r, c-w), (r, c+w)]
        return min([(antmath.distance2(origin, t), t) for t in options])

    def wrap(self, loc):
        '''Finds the true on-map coordinates of an unwrapped location.'''
        return loc[0] % self.g['rows'], loc[1] % self.g['cols']
