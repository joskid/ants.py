# stdlib
from math import fsum
import itertools as it
import random
# local
from hedge import Hedge
import antmath
import environment
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


###############################################################################


class Decider(object):
    '''Decider object as required by protocol.py.'''

    def __init__(self, logfn=None):
        self.log = logfn
        self.__think = None
        self.env = None

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.__think = meta(self.log, game)
        self.__think.next()
        self.env = environment.LazyEnvDigest(
            (game['rows'], game['cols']), game['viewradius'], self.log)

    def think(self, *args):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        self.env.update_env(*args)
        return self.__think.send(self.env)


###############################################################################


def brownian_genmoves(logfn, game):
    vects = list('NESW=')
    moves = None # first move set is thrown out
    while True:
        env = yield moves
        moves = {aI:random.choice(vects) for aI in env.myid}


###############################################################################


def meta(logfn, game):

    # experts (generators)
    experts = [e(logfn, game) for e in (brownian_gendist, gather.gendist)]
    for e in experts:
        e.next() # coroutine warmup

    # learner (generator)
    # 0.9 learns slowly and 0.1 learns quickly
    hedge = Hedge(0.25, len(experts))
    faith = hedge.next()

    # loop
    env = environment.LazyEnvDigest((0, 0), 0, None) # will be thrown out
    while True:
        logfn and logfn('faith: {}'.format(faith))

        # query each strategy to impose a distribution over all ants
        # eg:
        #   dists = [{1: {'N': 0.50, 'E': 0.50, 'S': 0.00, 'W': 0.00, '=': 0.00},
        #             2: {'N': 0.00, 'E': 1.00, 'S': 0.00, 'W': 0.00, '=': 0.00} },
        #            {1: {'N': 1.00, 'E': 0.00, 'S': 0.00, 'W': 0.00, '=': 0.00},
        #             2: {'N': 0.00, 'E': 0.75, 'S': 0.00, 'W': 0.00, '=': 0.25} } ]

        movelists = [e.send(env) for e in experts]
        for i, moves in enumerate(movelists):
            logfn and logfn('moves: strat{} moves{}'.format(i, moves))

        assert all(all(ad.viewkeys() ^ set('NESW=') == set() \
                       for ad in sd.itervalues()) for sd in dists) # all vectors
        assert all(all(1.0 == fsum(ad.itervalues()) \
                       for ad in sd.itervalues()) for sd in dists) # sum to 1

        # take the weighted linear combination over distributions
        # eg:
        #   faith = [0.8, 0.2]
        # result:
        #   lincomb = {1: {'N': 0.60, 'E': 0.40, 'S': 0.00, 'W': 0.00, '=': 0.00},
        #              2: {'N': 0.00, 'E': 0.95, 'S': 0.00, 'W': 0.00, '=': 0.05} }
        #
        # actually, each probability is really a 2-tuple in which the second
        # part is a dict of "blame tags" which maps strategy indexes to the
        # strategy probality of the vector
        # eg:
        #   lincomb = {1: {'N': (0.60, {0: 0.50, 1: 1.00}), ...
        #
        # this way we blame strategy 0 half as much as we blame strategy 1 when
        # moving ant 1 north causes it to die

        lincomb = {aI: {vect: (fsum\
                               ((f * d[aI][vect]) \
                                for f, d in it.izip(faith, dists) \
                                if aI in d),
                               {i: d[aI][vect] \
                                for i, d in enumerate(dists) \
                                if aI in d})
                        for vect in list('NESW=')} \
                   for aI in env.myid}
        for aI, dist in lincomb.iteritems():
            logfn and logfn('lincomb: ant{} --> {}'.format(aI, sorted([(v, p) for v, (p, b) in dist.iteritems()])))

        # not every dist in lincomb sums to 1 because some ants were left out by
        # some strategies; this is relevant in 'distpick'
        #
        # brownian_gendist always includes all ants, which prevents us from
        # having to add in those left out by all strategies

        assert lincomb.viewkeys() ^ env.myid == set() # all ants

        # probabalistically make each ant's decision; keep data for loss
        # analysis later and generate moves to yield out

        moves = {}
        decisions = {}
        for aI, vd in lincomb.iteritems():
            aN, aO = env.myid[aI]
            #
            vector, blame = distpick(vd)
            decisions[aI] = env.wrap(antmath.displace_loc(vector, aN)), blame
            moves[aN] = [vector]

        # yield move decisions and get a new environment

        oldf = env.food.copy()
        logfn and logfn('moves: {}'.format(moves))
        env = yield moves
        assert oldf is not env.food

        # for each old-ant:
        #   did it follow the vector we recommended?
        #     yes-> is it still alive?
        #             yes-> did the action result in good things?
        #                     yes-> NO LOSS (0)
        #                     no--> MINOR LOSS (0, 1)
        #             no--> MAJOR LOSS (1)

        loss = [[] for e in experts]

        for aI, (vector, blame) in decisions.iteritems():
            alive = aI in env.myid
            aN, aO = env.myid[aI] if alive else env.mydead[aI]
            obey = decisions[aI][0] == aN
            if obey:
                # determine loss for this ant
                als = (0.0 if goodmove(oldf, env, aN, logfn) else 0.1) \
                      if alive else 1.0
                for i in blame:
                    loss[i].append(als)
##                # assign loss to each strategy (scaled by probability)
##                for i, prob in blame.iteritems():
##                    loss[i].append(prob * als)

        logfn and logfn('loss: {}'.format(loss))

        # condense loss down to one value (divided by old ant-count) and apply to hedge

        faith = hedge.send([fsum(l) / len(decisions) if decisions else 0.0 \
                            for l in loss])


def goodmove(oldfood, env, aloc, logfn):
    '''Did any locations neighboring the ant contain food last turn?'''
    logfn('goodmove {} {}'.format(
        aloc, [loc in oldfood for loc in env.wrapiter(env.tonari(aloc))]))
    return any(loc in oldfood for loc in env.wrapiter(env.tonari(aloc)))


def distpick(distblame):
    '''Randomly pick a key from distblame according to the probabilities.

    Also return the blame dictionary for that vector.
    '''
    _, cdf = reduce(lambda (pdf, cdf), (vect, (prob, _)): \
                    (pdf + [prob], cdf + [(vect, fsum(pdf + [prob]))]),
                    distblame.iteritems(),
                    ([], []))
    assert round(cdf[-1][1], 6) <= 1.0 # sum to at most 1

    # lazily fix distributions which sum to less than 1
    pick = cdf[-1][1] * random.random()

    # find first prob in cdf which is strictly greater than than 'pick'
    vector = reduce(lambda acc, (vect, cprob): \
                    (vect, cprob) if cprob > pick and not acc else acc,
                    cdf, False)[0]
    return vector, distblame[vector][1]
