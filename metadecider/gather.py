# local
import antmath


'''
Simple strategy to gather food.

Assigns no more than one ant to each food; not necessarily the closest ant.

'''


def gendist(logfn, game):

    # functions
    wrap = lambda loc: antmath.wrap_loc(loc, (game['rows'], game['cols']))

    # turn state
    ag = {} # id --> loc (ant ids to goal locs)
    taken = set() # loc (goal locs)
    dist = {} # id --> [vect --> int] (ant ids to vector distributions)

    # loop
    while True:
        env = yield dist
        for aI, goal in ag.items():
            aN, aO = env.myid[aI]

            # if the goal has disappeared
            if wrap(goal) not in env.food:
                # remove goal from taken
                taken.remove(goal)
                ag.pop(goal)
                # pick a new not-taken goal
                for dist2, gloc in env.digest('food', aN):
                    if gloc not in taken:
                        taken.add(gloc)
                        ag[aI] = gloc
                        break

            # if we have a goal
            if ag[aI]:
                # set entry in dist to move toward it
                vect1, vect2 = antmath.naive_dir(aN, ag[aI])
                dist[aI] = {vect1: 0.75, vect2: 0.25}
            # else if we don't have a goal but do have a dist entry
            elif dist[aI]:
                # remove dist entry
                dist.pop(aI)
