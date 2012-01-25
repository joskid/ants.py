# stdlib
import random
# local
import antmath


'''
Simple strategy to raze enemy hills.

Tells each ant to move toward enemy hills if there are no enemys adjacent.

'''


def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aN, (aI, _) in env.myant.iteritems():
            goals = env.digest('enemyhill', aN)
            if goals:
                d2, gloc = goals[0]
                around = env.wrapiter(antmath.eightsquare(gloc) + [gloc])
                if not env.enemyant.viewkeys() & around and env.ray(aN, gloc):
                    moves[aI] = env.ray(aN, gloc)

        moves = env.supplement(moves)
