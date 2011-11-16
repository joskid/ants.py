# local
import hedge
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

    def __init__(self, logfn=None):
        self.log = logfn
        self.vect = list('NESW=')
        self.game = None
        # strategy stubs
        self.strategies = [
            clump.Decider,
            defend.Decider,
            explore.Decider,
            march.Decider,
            gather.Decider,
        ]
        # learner
        self.hedge = hedge.Hedge(0.9, len(self.strategies))
        self.faith = self.hedge.next()
        self.loss = [0.0] * len(self.strategies)

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.game.update(game)
        for s in self.strategies:
            s.start(self.game)

    def think(self, dirt, food, enemyhill, enemyant, myhill, myant, mydead):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        ### FINISH LAST TURN'S STUFF ###
        # figure out whether each ant's action was good or bad
        # generate a loss value for each ant relative to the number of ants
        # -- do we need to weight losses according to last turn's weights? no...
        # -- indicate loss for strategy(s) which were followed for this ant
        ### START THIS TURN'S STUFF ###
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
        return myant
