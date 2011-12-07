# stdlib
import itertools as it
# local
from hedge import Hedge
import antmath
#
import clump
import defend
import explore
import march
import gather


'''
Learning meta-decider for the 2011 Google AI Challenge.
Not yet submitted.

Stochastically learns which of several strategies are best via the hedge
algorithm.

(5)
'''


class Decider(object):
    '''Decider object as required by protocol.py.'''

    def __init__(self, logfn=None):
        self.log = logfn
        self.__think = None

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.__think = meta(self.log, game)
        self.__think.next()

    def think(self, *args):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        return self.__think.send(args)


def meta(logfn, game):
    #
    # experts (generators)
    experts = [e(logfn, game) for e in (
        clump.Genmoves,
        march.Genmoves,
        gather.Genmoves,
        defend.Genmoves,
        explore.Genmoves
    )]
    for e in experts:
        e.next()
    #
    # learner (generator)
    hedge = Hedge(0.9, len(STRATEGIES))
    faith = hedge.next()
    #
    # initialize environment (blank)
    # tuple of: water, food, enemyhill, enemyant, myhill, myant, mydead
    environment = ({}, {}, {}, {}, {}, {}, [])
    #
    # loop
    while True:
        # process/digest environment into ant-perspectives
        antenvs = []
        for aN, (aI, aO) in myant.iteritems():
            pass
        # query each strategy to impose a distribution over all ants
        #   s1 =
        #       a1 = { n:50%, e:50% }
        #       a2 = { e:100% }
        #   s2 =
        #       a1 = ( n:100% }
        #       a2 = { e:75%, =:25% }
        # take the weighted linear combination over recommendations
        #   faith =
        #       s1 = 0.8
        #       s2 = 0.2
        #   a1 = { n:60%, e:40% }
        #   a2 = { e:95%, =:5% }
        # generate one random number per ant to decide where to go
        # store decisions and weights until next round
        environment = yield myant
        # figure out whether each ant's action was good or bad
        # generate a loss value for each ant relative to the number of ants
        # -- do we need to weight losses according to last turn's weights? no...
        # -- indicate loss for strategy(s) which were followed for this ant



# A Size is a tuple:
# -- integer - height
# -- integer - width

# A Loc is a tuple:
# -- integer - row location
# -- integer - column location

# A GoalDict is a dictionary:
# -- Loc : or<bool,int,tuple> - maps locations to goal information

# An Goal is a tuple:
# -- integer - squared distance goal is from onlooker
# -- Loc - nearest location of goal relative to onlooker

# An AntPerspective is a tuple:
# -- Loc - location of this ant (onlooker)
# -- list<Goal> - goals within viewradius2 of this ant

def digest(gd, size, rad, aloc):
    '''Convert a colony-wide view of the environment to an ant's view.
    GoalDict Size int Loc --> AntPerspective

    '''
    rad2 = rad ** 2
    return sorted((dist2, gloc) \
                  for dist2, gloc in antmath.allinradius(rad, aloc) \
                  if dist2 <= rad2 and antmath.wrap_loc(gloc, size) in gd)
