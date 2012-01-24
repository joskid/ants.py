'''
Basic math operations relevant to the ants competition.

Loc - A tuple of two integers representing a row & column pair.
Size - A tuple of two integers representing a height & width pair.

'''

def nearest_unwrapped_loc(origin, size, target):
    '''Find the nearest of the five possible target locations to the origin.
    Loc Size Loc --> Loc

    Return the squared distance and the location as a tuple.

    Memoizes answers for a given origin and target location; size is assumed
    not to change during the course of a game.

    '''
    memo = nearest_unwrapped_loc.memo
    try:
        return memo[origin, target]
    except KeyError:
        h, w = size
        r, c = target
        options = [target, (r-h, c), (r+h, c), (r, c-w), (r, c+w)]
        memo[origin, target] = min((distance2(origin, t), t) for t in options)
        return memo[origin, target]
nearest_unwrapped_loc.memo = {}


def wrap_loc(loc, size):
    '''Finds the true on-map coordinates of an unwrapped location.'''
    row, col = loc
    height, width = size
    return row % height, col % width


def displace_loc(direction, location):
    '''Give the new location after displacing in the given direction.'''
    return {'N': lambda loc: (loc[0] - 1, loc[1]    ),
            'E': lambda loc: (loc[0]    , loc[1] + 1),
            'S': lambda loc: (loc[0] + 1, loc[1]    ),
            'W': lambda loc: (loc[0]    , loc[1] - 1),
            '=': lambda loc: loc,
            }[direction](location)


def loc_displacement(oldloc, newloc):
    '''Tell in what direction the displacement from old to new occurred.

    oldloc and newloc do not have to be adjacent, but they must be on either
    the same row or column.

    '''
    rO, cO = oldloc
    rN, cN = newloc
    sign = cmp
    return {(-1, 0):'N',
            ( 0, 1):'E',
            ( 1, 0):'S',
            ( 0,-1):'W',
            ( 0, 0):'=',
            }[sign(rN, rO),
              sign(cN, cO)]


def neighbors(loc):
    '''Return the list of immediate neighbors to the given location.'''
    r, c = loc
    return [(r-1, c  ),
            (r  , c+1),
            (r+1, c  ),
            (r  , c-1)]


def eightsquare(loc):
    '''Return the list of all eight squares surrounding the given location.'''
    r, c = loc
    return [(r-1, c  ), (r-1, c+1),
            (r  , c+1), (r+1, c+1),
            (r+1, c  ), (r+1, c-1),
            (r  , c-1), (r-1, c-1)]


def reverse_dir(direction):
    '''What is the opposite NESW direction?'''
    return {'N':'S',
            'E':'W',
            'S':'N',
            'W':'E',
            '=':'='}[direction]


def naive_dir(origin, target):
    '''Which two NESW directions orient origin toward target?
    
    Returns the directions in order of directness.
    EG. ['N', 'E'] indicates that target is more north than east of origin,
        while ['E', 'N'] indicates it is more east than north.
    
    Returns a list of same vectors when the target is on the same row or
    column as the origin.
    EG: ['N', 'N'] indicates that the target is due north from origin.
    
    '''
    ar, ac = origin
    br, bc = target
    deltar = br - ar
    deltac = bc - ac
    r = {-1:'N', 0:'=', 1:'S'}[cmp(br, ar)]
    c = {-1:'W', 0:'=', 1:'E'}[cmp(bc, ac)]
    r = c if r == '=' else r
    c = r if c == '=' else c
    return [r, c] if deltar ** 2 > deltac ** 2 else [c, r]


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
