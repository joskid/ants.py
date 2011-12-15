# stdlib
from random import random, choice
from math import fsum
# local
import antmath as am


'''
Complete strategy to move away from where we've been (and water).

'''


def genmoves(logfn, game):
    moves = {}
    past = {}
    lr = 0.4
    pf = 0.7
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, aO) in env.myid.iteritems():

##            if abs(aN[0] - aO[0]) > 1:
##                past[aI] = past[aI][0] * -1, past[aI][1]
##            if abs(aN[1] - aO[1]) > 1:
##                past[aI] = past[aI][0], past[aI][1] * -1

            # weighted average of all previous moves
            if aI in past:
                aOr, aOc = aO
                pr, pc = past[aI]
                past[aI] = (aOr * lr + pr * (1.0 - lr),
                            aOc * lr + pc * (1.0 - lr))
            else:
                past[aI] = aO
            pr, pc = past[aI]

            # average of visible water
            water = env.digest('water', aN)
            wr = fsum(r for d2, (r, c) in water) / max(len(water), 1)
            wc = fsum(c for d2, (r, c) in water) / max(len(water), 1)

            # weighted average of water and move history
            target = (pr * pf + wr * (1.0 - pf),
                      pc * pf + wc * (1.0 - pf))
            c = choice(am.naive_dir(target, aN))
            if c != '=':
                moves[aI] = c
        moves = env.supplement(moves)
