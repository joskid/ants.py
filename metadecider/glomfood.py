# stdlib
from random import random, choice
# local
import antmath as am


'''
Simple strategy to gather food.

Tells each ant to move toward its nearest reachable food.

'''

def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, _) in env.myid.iteritems():
            food = env.digest('food', aN)

            while food:
                d2, f = food.pop(0)
                if env.ray(aN, f):
                    v1, v2 = am.naive_dir(aN, f)
                    moves[aI] = v1 if random() < 0.75 else v2
                    break

        moves = env.supplement(moves)
