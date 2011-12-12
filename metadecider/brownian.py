# stdlib
import random

def genmoves(logfn, game):
    vects = list('NESW=')
    moves = None # first move set is thrown out
    while True:
        env = yield moves
        moves = {aI:random.choice(vects) for aI in env.myid}
