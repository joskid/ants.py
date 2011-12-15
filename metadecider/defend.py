# stdlib
from random import random, choice
# local
import antmath as am


'''
Simple strategy to get between the anthill and enemies.

'''


def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, _) in env.myid.iteritems():
            hill = env.digest('myhill', aN)
            enemy = env.digest('enemyant', aN)
            if hill and enemy:
                hill = hill[0][1]
                enemy = enemy[0][1]
                if env.ray(aN, enemy):
                    hr, hc = hill
                    er, ec = enemy
                    target = (hr + er) / 2.0, (hc + ec) / 2.0
                    if env.ray(aN, target):
                        v1, v2 = am.naive_dir(aN, target)
                        moves[aI] = v1 if random() < 0.75 else v2

        moves = env.supplement(moves)
