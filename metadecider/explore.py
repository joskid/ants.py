# stdlib
from random import random, choice
from math import fsum
# local
import antmath as am


'''
Simple strategy to move away from other ants.

'''


def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, aO) in env.myid.iteritems():
            ants = [gloc for d2, gloc in \
                    env.digest('myant', aN) + env.digest('enemyant', aN) \
                    if d2 > 2.5 ** 2] # don't consider your clump
            if ants:
                sumr = fsum(r for r, c in ants)
                sumc = fsum(c for r, c in ants)
                target = sumr / len(ants), sumc / len(ants)
                v1, v2 = am.naive_dir(target, aN)
                moves[aI] = v1 if random() < 0.75 else v2

        moves = env.supplement(moves)
