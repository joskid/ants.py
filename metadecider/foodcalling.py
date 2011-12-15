# stdlib
from random import random, choice
# local
import antmath as am


'''
Simple strategy to gather food.

Each food calls out to its nearest unoccupied ant.

'''

def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for f in env.food.iterkeys():
            ants = env.digest('myant', f)

            while ants:
                d2, a = ants.pop(0)
                aN = env.wrap(a)
                aI, aO = env.myant[aN]
                if aI not in moves and env.ray(a, f):
                    v1, v2 = am.naive_dir(a, f)
                    moves[aI] = v1 if random() < 0.75 else v2
                    break

        moves = env.supplement(moves)
