# stdlib
import math as m
import itertools as it
import operator as op


def Hedge(beta, count):
    assert 0 <= beta <= 1
    weights = it.repeat(1000, count)
    while True:
        #
        # yield a distribution from the weights
        weights = list(weights)                         # O(n)
        total = m.fsum(weights)                         # O(n)
        losses = yield [wi / total for wi in weights]   # O(n) + external
        #
        # update the weights according to losses
        assert len(losses) == count
        assert all(0 <= li <= 1 for li in losses)       # O(n)
        punishments = it.imap(op.pow, it.repeat(beta), losses)
        weights = it.imap(op.mul, weights, punishments)
