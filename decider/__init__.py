# deciders
from brownian import Decider as Brownian
from navigator import Decider as Navigator
from kmeans import Decider as KMeans
##from borg import Decider as Borg
from metadecider import Decider as Hedge


DECIDERS = {
    'Brownian'  :   Brownian,
    'Navigator' :   Navigator,
    'KMeans'    :   KMeans,
    'Hedge'     :   Hedge,
}


DEFAULT = ('KMeans', KMeans)


__all__ = [
    DECIDERS,
    DEFAULT,
]
