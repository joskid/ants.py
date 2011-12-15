# stdlib
from random import random, choice
# local
import antmath as am


'''
Simple strategy to intimidate enemies.

Tells ants not to get too cozy and to hold a safe distance.

'''


def genmoves(logfn, game):
    battle = game['attackradius']
    moveback = (battle + 2) ** 2
    moves = {} # id --> vect (ant ids to vector distributions)
    while True:
        env = yield moves
        moves = {}

        for aI, (aN, _) in env.myid.iteritems():
            goals = env.digest('enemyant', aN)
            if goals:
                d2, target = goals[0]
                if d2 <= moveback and env.ray(aN, target):
                        v1, v2 = am.naive_dir(target, aN)
                        # favor an indirect retreat to retain ground
                        moves[aI] = v1 if random() < 0.25 else v2

        moves = env.supplement(moves)
