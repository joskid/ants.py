# deciders
from brownian import Decider as Brownian
from navigator import Decider as Navigator
from kmeans import Decider as KMeans
from metadecider import Decider as Hedge


DECIDERS = {
    'Brownian'  :   Brownian,
    'Navigator' :   Navigator,
    'KMeans'    :   KMeans,
    'Hedge'     :   Hedge,
}


DEFAULT = ('Hedge', Hedge)


__all__ = [
    DECIDERS,
    DEFAULT,
]
