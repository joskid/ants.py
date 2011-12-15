# stdlib
import random
import math
# local
import antmath


'''
Complete strategy to drift toward food deposits..

'''


def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, aO) in env.myid.iteritems():
            localfood = env.digest('food', aN)
            if env.food and not localfood:
                sumr = math.fsum(r for r, c in env.food)
                sumc = math.fsum(c for r, c in env.food)
                target = sumr / len(env.food), sumc / len(env.food)
                moves[aI] = random.choice(antmath.naive_dir(aN, target))

        moves = env.supplement(moves)
