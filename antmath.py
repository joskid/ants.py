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


##def nearest_unwrapped_loc(origin, size, target):
##    oR, oC = origin
##    h, w = size
##    hh, hw = h * 0.5, w * 0.5
##    tR, tC = target
##    if abs(oR - tR) > hh:
##        tR += h * cmp(oR, tR)
##    if abs(oC - tC) > hw:
##        tC += w * cmp(oC, tC)
##    ans = distance2(origin, (tR, tC)), (tR, tC)
####    old = nearest_unwrapped_locOLD(origin, size, target)
####    if old[0] != ans[0]:
####        import os
####        os.write(2, 'FOO unwrap o {} s {} t{}\n'.format(origin, size, target))
####        os.write(2, 'FOO new {}\n'.format(ans))
####        os.write(2, 'FOO old {}\n'.format(old))
##    return ans
    


def wrap_loc(loc, size):
    '''Finds the true on-map coordinates of an unwrapped location.'''
    row, col = loc
    height, width = size
    return row % height, col % width


def displace_loc(direction, location):
    return {'N': lambda loc: (loc[0] - 1, loc[1]    ),
            'E': lambda loc: (loc[0]    , loc[1] + 1),
            'S': lambda loc: (loc[0] + 1, loc[1]    ),
            'W': lambda loc: (loc[0]    , loc[1] - 1),
            '=': lambda loc: loc,
            }[direction](location)


def loc_displacement(oldloc, newloc):
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


##def loc_displacement(oldloc, newloc):
##    rO, cO = oldloc
##    rN, cN = newloc
##    return {(-1, 0):'N',
##            ( 0, 1):'E',
##            ( 1, 0):'S',
##            ( 0,-1):'W',
##            ( 0, 0):'=',
##            }[, cN - cO]


def neighbors(loc):
    r, c = loc
    return [(r-1, c  ),
            (r  , c+1),
            (r+1, c  ),
            (r  , c-1)]


def eightsquare(loc):
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
    '''Which two NESW directions orient origin toward target?'''
    ar, ac = origin
    br, bc = target
    deltar = br - ar
    deltac = bc - ac
    r = {-1:'N', 0:'=', 1:'S'}[cmp(br, ar)]
    c = {-1:'W', 0:'=', 1:'E'}[cmp(bc, ac)]
    r = c if r == '=' else r
    c = r if c == '=' else c
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
