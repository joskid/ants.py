# stdlib
import random


'''
Complete strategy.

'''


def genmoves(logfn, game):
    vects = list('NESW')
    v = 0
    moves = None # first move set is thrown out
    while True:
        env = yield moves
        moves = {}
        for aI in env.myid:
            moves[aI] = vects[v]
            v = (v + 1) % 4
