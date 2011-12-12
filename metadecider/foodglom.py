# local
import antmath


'''
Simplest strategy to gather food.

Tells each ant to move toward its nearest food.

'''

def genmoves(logfn, game):
    moves = {}
    while True:

        env = yield moves
        moves = {}

        for aI, (aN, aO) in env.myid.iteritems():
            goals = env.digest('food', aN)
            if goals:
                _, g = goals[0]
                moves[aI] = antmath.naive_dir(aN, g)[0]
