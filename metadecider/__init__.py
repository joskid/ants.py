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
            (game['rows'], game['cols']), game['viewradius'])

    def think(self, *args):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        self.env.update_env(*args)
        return self.__think.send(self.env)


###############################################################################


def brownian_gendist(logfn, game):
    vects = list('NESW=')
    pdf = len(vects) * [1.0 / len(vects)]
    dist = None # first distribution is thrown out

    rand = {v: p for v, p in zip(vects, pdf)}
    while True:
        env = yield dist
        r = rand.copy()
        dist = {aI:r for aI in env.myid}


###############################################################################


def meta(logfn, game):

    # experts (generators)
    experts = [e(logfn, game) for e in (brownian_gendist, gather.gendist)]
##               (clump.gendist, march.gendist, gather.gendist, defend.gendist,
##                explore.gendist)]
    for e in experts:
        e.next() # warm up their loop

    # learner (generator)
    hedge = Hedge(0.9, len(experts))
    faith = hedge.next()

    # loop
    env = environment.LazyEnvDigest((0, 0), 0) # will be thrown out anyway
    while True:
        logfn and logfn('faith: {}'.format(faith))

        # query each strategy to impose a distribution over all ants
        # eg:
        #   dists = [{1: {'N': 0.50, 'E': 0.50, 'S': 0.00, 'W': 0.00, '=': 0.00},
        #             2: {'N': 0.00, 'E': 1.00, 'S': 0.00, 'W': 0.00, '=': 0.00} },
        #            {1: {'N': 1.00, 'E': 0.00, 'S': 0.00, 'W': 0.00, '=': 0.00},
        #             2: {'N': 0.00, 'E': 0.75, 'S': 0.00, 'W': 0.00, '=': 0.25} } ]

        dists = [e.send(env) for e in experts]
        logfn and logfn('dists: {}'.format(dists))

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

        oldfood = env.food
        logfn and logfn('moves: {}'.format(moves))
        env = yield moves

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
            obey = decisions[aI][0] == \
                     (env.myid[aI][0] if alive else env.mydead[aI][0])
            if obey:
                # determine loss for this ant
                if alive:
                    als = 0.0 if any(loc in oldfood for loc in \
                                     env.wrapiter(env.tonari(aN))) else 0.1
                else:
                    als = 1.0
                # assign loss to each strategy (scaled by probability)
                for i, prob in blame.iteritems():
                    loss[i].append(prob * als)

        logfn and logfn('loss: {}'.format(loss))

        # condense loss down to one value (divided by old ant-count) and apply to hedge

        faith = hedge.send([fsum(l) / len(decisions) if decisions else 0.0 \
                            for l in loss])


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
