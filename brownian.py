# stdlib
import random
# local
import protocol


class Decider(object):

    def __init__(self, logfn=None):
        self.g = {}

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.g.update(game)

    def think(self, dirt, food, enemyhill, enemyant, myhill, myant):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        d = list('NESW=')
        for loc in myant:
            random.shuffle(d)
            mine[loc] = d[:]
        return myant
