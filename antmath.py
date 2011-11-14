

def reverse_dir(direction):
    '''What is the opposite NESW direction?'''
    return {'N':'S',
            'E':'W',
            'S':'N',
            'W':'E'}[direction]


def naive_dir(a, b):
    '''Which two NESW directions orient a toward b?'''
    ar, ac = a
    br, bc = b
    deltar = br - ar
    deltac = bc - ac
    r = 'N' if deltar < 0 else 'S'
    c = 'W' if deltac < 0 else 'E'
    return [r, c] if deltar ** 2 > deltac ** 2 else [c, r]


def nearest(a, others, dist):
    '''Return the object in others nearest to loc a, given a distance func.'''
    return reduce(lambda acc,x: x if dist(a,x) < dist(a,acc) else acc, others)


def distance2(a, b):
    '''Euclidean distance squared.'''
    return (a[0] - b[0]) ** 2 + \
           (a[1] - b[1]) ** 2


def allinradius(radius, radius2, loc):
    '''Yield all values within the radius of the location.

    radius  -- integer radius
    radius2 -- integer squared-radius

    '''
    for r in xrange(-radius, radius + 1):
        for c in xrange(-radius, radius + 1):
            locb = loc[0] + r, loc[1] + c
            if distance2(loc, locb) <= radius2:
                yield locb
