# stdlib
from random import random, choice
# local
import antmath as am


'''
Simple strategy to stay off our hills.

'''


def genmoves(logfn, game):
    moves = {}
    arounds = {}
    while True:
        env = yield moves
        moves = {}

        if not arounds:
            for h in env.myhill:
                arounds[h] = set()
                for n in am.neighbors(h):
                    arounds[h] = arounds[h].union(am.eightsquare(n))
                arounds[h] = arounds[h].difference([h] + am.neighbors(h))

        for aI, (aN, _) in env.myid.iteritems():
            hills = env.digest('myhill', aN)
            if hills:
                d2, h = hills[0]
                if aN == h or aN in am.neighbors(h):
                    moves[aI] = choice('NESW')
                elif aN in arounds[h]:
                    moves[aI] = choice(am.naive_dir(h, aN))

        moves = env.supplement(moves)
