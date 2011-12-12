# stdlib
from math import fsum
import itertools as it
import random
# local
from hedge import Hedge
import antmath
import environment
#
import brownian
import gather
import foodglom
#
import clump
import defend
import explore
import march


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


EXPERTS = (
##    brownian,
    gather,
    foodglom,
)


def meta(logfn, game):
    vectors = list('NESW=')

    # experts (generators)
    experts = [e.genmoves(logfn, game) for e in EXPERTS]
    enames = [e.__name__ for e in EXPERTS]
    for e in experts:
        e.next() # coroutine warmup

    # learner (generator)
    # 0.9 learns slowly and 0.1 learns quickly
    hedge = Hedge(0.25, len(experts))
    faith = hedge.next()

    # loop
    env = environment.LazyEnvDigest((0, 0), 0, None) # for warmup
    while True:

        for n, f in zip(enames, faith):
            logfn and logfn('faith: {} \t {}'.format(n, f))

        # query each strategy
        # eg:
        #   moves = [{1:'N', 2:'E',        5:'='},
        #            {1:'N', 2:'S', 4:'S', 5:'W'}]

        moves = [e.send(env) for e in experts]

        for n, m in zip(enames, moves):
            logfn and logfn('moves: {} \t {}'.format(n, m))

        # combine the move recommendations into distributions
        # eg:
        #   faith = [0.8, 0.2]
        # result:
        #   lincomb = {1: ({'N':1.0, 'E':0.0, 'S':0.0, 'W':0.0, '=':0.0}, {}),
        #              2: ({'N':0.0, 'E':0.8, 'S':0.2, 'W':0.0, '=':0.0}, {}),
        #              4: ({'N':0.0, 'E':0.0, 'S':0.2, 'W':0.0, '=':0.0}, {}),
        #              5: ({'N':0.0, 'E':0.0, 'S':0.0, 'W':0.8, '=':0.2}, {})}
        #
        # actually, each probability is really a 3-tuple in which the second
        # part is a generator of the strategy indexes that output that vector
        # eg:
        #   lincomb = {1: {'N':(1.0, [0, 1]), ...
        #
        # this way we blame strategy 0 and strategy 1 when moving ant 1 north
        # causes it to die
        #
        # you'll notice in the example that ant 4's entry doesn't sum to one
        # because strategy 0 didn't recommend anything for it -- this is
        # compensated for in 'distpick'
        #
        # the extra dictionary is where vector entries are put when popped from
        # the distribution

        lincomb = {aI: {vect: (fsum(f for f, m in it.izip(faith, moves) \
                                    if aI in m and m[aI] == vect),
                               [i for i, m in enumerate(moves) \
                                if aI in m and m[aI] == vect]
                               ) \
                        for vect in vectors} \
                   for aI in env.myid}

        for aI, mdist in lincomb.iteritems():
            logfn and logfn('lincomb: ant{} --> {}'.format(aI, mdist))

        # make a probabalistic generator for each ant's decision-vector
        # get a new environment

        oldfood = env.food.copy()
        env = yield {env.myid[aI][0]: distpicker(vd, logfn) \
                     for aI, vd in lincomb.iteritems()}

        # for each old-ant:
        #   did any strategy tell the ant to do what it did?
        #     Tr> is the ant still alive?
        #           Tr> did the action result in good things?
        #                 Tr> NO LOSS (0)
        #                 Fa> MINOR LOSS (0, 1)
        #           Fa> MAJOR LOSS (1)

        loss = [[] for e in experts]

        for aI, vd in lincomb.iteritems():
            alive = aI in env.myid
            aN, aO = env.myid[aI] if alive else env.mydead[aI]
            move = antmath.loc_displacement(aO, aN)
            prob, blame = vd[move] if move in vd else (None, None)
            logfn('dist: a{} {}'.format(aI, vd))
            logfn and logfn('loss: a{} alive {} move {} prob {} blame {}'.\
                            format(aI, alive, move, prob, blame))
            if prob:
                # determine loss for this ant
                als = (0.0 if tookfood(oldfood, env, aN) else 0.1) \
                      if alive else 1.0
                for i in blame:
                    loss[i].append(als)

        for n, l in zip(enames, loss):
            logfn and logfn('loss: {} \t {}'.format(n, l))

        # condense loss down to one value and apply to hedge (div by antcount)

        faith = hedge.send([fsum(l) / len(lincomb) if lincomb else 0.0 \
                            for l in loss])


def tookfood(oldfood, env, aloc):
    '''Did any locations neighboring the ant contain food last turn?'''
    return any(loc in oldfood for loc in env.wrapiter(env.tonari(aloc)))


def distpicker(dist, logfn):
    '''Generate keys from dist according to their probabilities.
    dist is a [vect --> (prob, blame)]

    Stop after yielding all keys with probablitity greater than zero.

    '''
    def distpick(d):
        '''Return a key from d according to its probability.
        d is a [vect --> prob]
        return a 2-tuple (vect, prob)
        '''
        logfn('distpick: d {}'.format(d))
        # produce cdf
        _, cdf = reduce(lambda (pdf, cdf), (vect, prob): \
                        (pdf + [prob], cdf + [(vect, fsum(pdf + [prob]))]),
                        dist.iteritems(),
                        ([], []))
        logfn('distpick: cdf {}'.format(cdf))
        # produce a scaled random picker
        pick = cdf[-1][1] * random.random()
        # return vect of first prob in cdf which is greater than picker
        return reduce(lambda acc, (vect, cprob): \
                      (vect, cprob) if cprob > pick and not acc else acc,
                      cdf,
                      False)
    ### INNER ###
    # strip blame; filter zero probabilities
    dist = {v: p for v, (p, _) in dist.iteritems() if p}
    assert round(fsum(dist.viewvalues()), 6) <= 1.0 # sum to at most 1.000000
    while dist:
        vect, prob = distpick(dist)
        yield vect
        dist.pop(vect)
