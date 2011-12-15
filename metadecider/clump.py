# stdlib
from random import random, choice
# local
import antmath as am


'''
Simple strategy to stay together.

Tells each ant to move toward it's nearest buddy.

'''


def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, _) in env.myid.iteritems():
            goals = env.digest('myant', aN)
            if goals:
                d2, gloc = goals[0]
                if 2 ** 2 < d2 < 4 ** 2 and env.ray(aN, gloc):
                    moves[aI] = am.naive_dir(aN, gloc)

        moves = env.supplement(moves)
