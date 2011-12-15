# stdlib
import random
# local
import antmath


'''
Simple strategy to keep moving despite obstacles.

Tells stuck ants which directions might un-stick them.

'''


def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, _) in env.myid.iteritems():
            neighbors = antmath.neighbors(aN)
            walls = set(n for n in neighbors if n in env.water)
            if walls:
                ways = list(set(neighbors) - walls)
                moves[aI] = antmath.loc_displacement(aN, random.choice(ways))

        moves = env.supplement(moves)
