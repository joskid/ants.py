# stdlib
from math import fsum
import itertools as it
import random
# local
from hedge import Hedge
import antmath
import environment
#
import betterexplore
import brownian
import clump
import defend
import explore
import foodcalling
import glomfood
import glomhill
import keepdistance
import mob
import movein
import stayoffhill
import unstuck


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
    betterexplore, # not in comp #7
    brownian,
    clump,
    defend,
    explore,
    foodcalling,
    glomfood, # not in comp #7
    glomhill,
    keepdistance,
    mob, # not in comp #7
    movein,
    stayoffhill,
    unstuck,
)


def meta(logfn, game):
    vectors = list('NESW=')

    # experts (generators)
    experts = [e.genmoves(logfn, game) for e in EXPERTS]
    enames = [e.__name__ for e in EXPERTS]
    logfn and logfn('# ' + ' '.join(n[n.find('.') + 1:] for n in \
                                    enames + ['ant-count']),
                    noprefix=True)
    for e in experts:
        e.next() # coroutine warmup

    # learner (generator)
    # 0.9 learns slowly and 0.1 learns quickly
    hedge = Hedge(0.25, len(experts))
    faith = hedge.next()

    # loop
    env = environment.LazyEnvDigest((0, 0), 0, None) # for warmup
    while True:

        logfn and logfn(' '.join(str(f) for f in \
                                 faith + [len(env.myant)]), noprefix=True)

        # query each strategy
        # eg:
        #   moves = [{1:'N', 2:'E',        5:'='},
        #            {1:'N', 2:'S', 4:'S', 5:'W'}]

        if len(env.myant) >= 250:
            env.food.clear()
        moves = [e.send(env) for e in experts]

        # make sure ants have orders from at least one strategy
        #assert all(env.myid - m.viewkeys() == set() for m in moves)

        # combine the move recommendations into distributions
        # eg:
        #   faith = [0.8, 0.2]
        # result:
        #   lincomb = {1: ({'N':1.0, 'E':0.0, 'S':0.0, 'W':0.0, '=':0.0}, {}),
        #              2: ({'N':0.0, 'E':0.8, 'S':0.2, 'W':0.0, '=':0.0}, {}),
        #              4: ({'N':0.0, 'E':0.0, 'S':0.2, 'W':0.0, '=':0.0}, {}),
        #              5: ({'N':0.0, 'E':0.0, 'S':0.0, 'W':0.8, '=':0.2}, {})}
        #
        # actually, each probability is really a 2-tuple in which the second
        # part is a list of the strategy indexes that output that vector
        # eg:
        #   lincomb = {1: {'N':(1.0, [0, 1]), ...
        #
        # this way we blame strategy 0 and strategy 1 when moving ant 1 north
        # causes it to die
        #
        # you'll notice in the example that ant 4's entry doesn't sum to one
        # because strategy 0 didn't recommend anything for it -- this is
        # compensated for in 'distpick'

        lincomb = {aI: {vect: (fsum(f for f, m in it.izip(faith, moves) \
                                    if aI in m and m[aI] == vect),
                               [i for i, m in enumerate(moves) \
                                if aI in m and m[aI] == vect]
                               ) \
                        for vect in vectors} \
                   for aI in env.myid}

        # make a probabalistic generator for each ant's decision-vector
        # get a new environment

        oldfood = env.food.copy()
        env = yield {env.myid[aI][0]: distpicker(vd) \
                     for aI, vd in lincomb.iteritems()}

        # last minute hack: don't process more than 100 ants each turn
        # unfortunately, this bot is not efficient, and frequently times-out
        # without this hack

        keys = env.myant.keys()
        while len(env.myant) > 100:
            k = random.choice(keys)
            keys.remove(k)
            env.myant.pop(k)

        # assign loss to strategies according to how the ants fared

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
            try:
                aN, aO = env.myid[aI] if alive else env.mydeadid[aI]
            except KeyError:
                continue
            move = antmath.loc_displacement(aO, env.unwrap(aO, aN))
            prob, blame = vd[move] if move in vd else (None, None)
            if prob:
                # determine loss for this ant
                als = (0.0 if tookfood(oldfood, env, aN) else 0.1) \
                      if alive else 1.0
                for i in blame:
                    loss[i].append(als)

        # sum loss by strategy and apply to hedge

        faith = hedge.send([fsum(l) / len(lincomb) if lincomb else 0.0 \
                            for l in loss])


def tookfood(oldfood, env, aloc):
    '''Did any locations neighboring the ant contain food last turn?'''
    return any(loc in oldfood for loc in env.wrapiter(env.tonari(aloc)))


def distpicker(dist):
    '''Generate keys from dist according to their probabilities.
    dist is a [vect --> (prob, blame)]

    Stop after yielding all keys with probablitity greater than zero.

    '''
    def distpick(d):
        '''Return a key from d according to its probability.
        d is a [vect --> prob]
        return a 2-tuple (vect, prob)
        '''
        # produce cdf
        _, cdf = reduce(lambda (pdf, cdf), (vect, prob): \
                        (pdf + [prob], cdf + [(vect, fsum(pdf + [prob]))]),
                        dist.iteritems(),
                        ([], []))
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
