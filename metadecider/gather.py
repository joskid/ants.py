# local
import antmath


'''
Simple strategy to gather food.

Assigns no more than one ant to each food; not necessarily the closest ant.

'''


def gendist(logfn, game):

    # functions
    wrap = lambda loc: antmath.wrap_loc(loc, (game['rows'], game['cols']))
    default = {v: 0.0 for v in list('NESW=')}

    # turn state
    ag = {} # id --> loc (ant ids to goal locs)
    ga = {} # loc --> id (goal locs to ant ids)
    dist = {} # id --> [vect --> int] (ant ids to vector distributions)

    # loop
    while True:
        env = yield dist

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
            # set dist to move toward our goal if we have one
            if aI in ag:
                vect1, vect2 = antmath.naive_dir(aN, ag[aI])
                dist[aI] = default.copy()
                dist[aI].update({vect1: 0.75, vect2: 0.25})
            # remove our dist entry if we don't have a goal
            elif aI in dist:
                dist.pop(aI)
