'''
Basic math operations relevant to the ants competition.

Loc - A tuple of two integers representing a row & column pair.
Size - A tuple of two integers representing a height & width pair.

'''

def nearest_unwrapped_loc(origin, size, target):
    '''Find the nearest of the five possible target locations to the origin.
    Loc Size Loc --> Loc

    Return the squared distance and the location as a tuple.

    '''
    h, w = size
    r, c = target
    options = [target, (r-h, c), (r+h, c), (r, c-w), (r, c+w)]
    return min((distance2(origin, t), t) for t in options)


def wrap_loc(loc, size):
    '''Finds the true on-map coordinates of an unwrapped location.'''
    row, col = loc
    height, width = size
    return row % height, col % width


def reverse_dir(direction):
    '''What is the opposite NESW direction?'''
    return {'N':'S',
            'E':'W',
            'S':'N',
            'W':'E'}[direction]


def naive_dir(origin, target):
    '''Which two NESW directions orient origin toward target?'''
    ar, ac = origin
    br, bc = target
    deltar = br - ar
    deltac = bc - ac
    r = 'N' if deltar < 0 else 'S'
    c = 'W' if deltac < 0 else 'E'
    return [r, c] if deltar ** 2 > deltac ** 2 else [c, r]


##def nearest(a, others, dist):
##    '''Return the object in others nearest to loc a, given a distance func.'''
##    return reduce(lambda acc,x: x if dist(a,x) < dist(a,acc) else acc, others)


def distance2(a, b):
    '''Euclidean distance squared.'''
    return (a[0] - b[0]) ** 2 + \
           (a[1] - b[1]) ** 2


def allinradius(radius, loc):
    '''Yield unwrapped Locs within the radius of the given Loc.

    radius  -- integer radius
    loc     -- Loc at center

    '''
    radius2 = radius ** 2
    rA, cA = locA = loc
    for r in xrange(-radius, radius + 1):
        for c in xrange(-radius, radius + 1):
            locB = rA+r, cA+c
            dist = distance2(locA, locB)
            if dist <= radius2:
                yield dist, locB
