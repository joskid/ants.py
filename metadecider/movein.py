# stdlib
from random import random, choice
# local
import antmath as am

'''
Simple strategy to close in on outnumbered enemies.

'''


def genmoves(logfn, game):
    moves = {}
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, _) in env.myid.iteritems():
            if aI not in moves:
                friends = env.digest('myant', aN)
                enemies = env.digest('enemyant', aN)
                if friends and enemies:
                    t2, target = enemies[0]
                    if env.ray(aN, target):
                        enemies = env.digest('enemyant', target)[1:]
                        myclump = [env.myant[f][0] for d2, f in friends \
                                   if d2 < 3 ** 2 and f in env.myant]
                        enclump = [e for d2, e in enemies \
                                   if d2 < 3 ** 2] + [target]
                        if len(myclump) > len(enclump):
                            v1, v2 = am.naive_dir(aN, target)
                            vect = v1 if random() < 0.75 else v2
                            for aI in myclump + [aI]:
                                moves[aI] = vect
        moves = env.supplement(moves)
