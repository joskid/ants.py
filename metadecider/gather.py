# local
import antmath


'''
Simple strategy to gather food.

Assigns no more than one ant to each food; not necessarily the closest ant.

'''


def genmoves(logfn, game):

    # functions
    wrap = lambda loc: antmath.wrap_loc(loc, (game['rows'], game['cols']))

    # turn state
    ag = {} # id --> loc (ant ids to goal locs)
    ga = {} # loc --> id (goal locs to ant ids)

    # loop
    moves = {} # id --> vect (ant ids to vector distributions)
    while True:
        env = yield moves

        # for dead ants
        for aN, (aI, aN) in env.mydead.iteritems():
            # forget ants if dead
            if aI in ag:
                goal = ag.pop(aI)
                ga.pop(goal)

        # for ants with goals
        for aI, goal in ag.items():
            aN, aO = env.myid[aI]
            # release the goal if it has disappeared
            if wrap(goal) not in env.food:
                ag.pop(aI)
                ga.pop(goal)

        # for living ants
        for aI, (aN, aO) in env.myid.iteritems():
            # pick a new not-taken goal if we don't have one
            if aI not in ag:
                for dist2, gloc in env.digest('food', aN):
                    if gloc not in ga:
                        ag[aI] = gloc
                        ga[gloc] = aI
                        break

        # for ants with goals
        for aI, goal in ag.items():
            aN, aO = env.myid[aI]
            # set to move toward our goal if we have one
            if aI in ag:
                vect1, vect2 = antmath.naive_dir(aN, ag[aI])
                moves[aI] = vect1
            # remove our moves entry if we don't have a goal
            elif aI in moves:
                moves.pop(aI)
