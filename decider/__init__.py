# resources
import antmath as math


# deciders
from brownian import Decider as Brownian
from navigator import Decider as Navigator
from kmeans import Decider as KMeans
##from borg import Decider as Borg


DECIDERS = {
    'Brownian'  :   Brownian,
    'Navigator' :   Navigator,
    'KMeans'    :   KMeans,
}


DEFAULT = ('KMeans', KMeans)


__all__ = [
    DECIDERS,
    DEFAULT,
    math,
]
