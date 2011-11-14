# stdlib
import random
# local
import protocol


'''
Baseline decider for the 2011 Google AI Challenge.
Maximum Rank was around 1400th of 5000 contestants.

Moves each ant randomly each turn.

(1)
'''


class Decider(object):

    def __init__(self, logfn=None):
        self.g = {}
        self.logfn = logfn
        self.v = list('NESW=')

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.g.update(game)

    def think(self, dirt, food, enemyhill, enemyant, myhill, myant, mydead):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        for loc in myant:
            random.shuffle(self.v)
            myant[loc] = self.v[:]
        return myant
