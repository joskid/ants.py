# stdlib
from random import random, choice
# local
import antmath as am

'''
Simple strategy to gang up on enemies.

Tells the farthest visible ant (of mine) who can see each enemy to approach.

'''


def genmoves(logfn, game):
    battle = game['attackradius']
    holddist = (battle + 2) ** 2
    moves = {}
    rec = {}
    while True:
        env = yield moves
        moves = {}
        rec = {}

        for e in env.enemyant:
            mine = env.digest('myant', e)
            while mine:
                d2, m = mine.pop()
                aN = env.wrap(m)
                if d2 > holddist and env.ray(m, e):
                    if aN not in rec:
                        rec[aN] = []
                    v1, v2 = am.naive_dir(m, e)
                    rec[aN].append(v1 if random() < 0.65 else v2)

        for aI, (aN, _) in env.myid.iteritems():
            if aN in rec:
                moves[aI] = choice(rec[aN])

        moves = env.supplement(moves)
