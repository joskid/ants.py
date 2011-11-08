# stdlib
import random
from datetime import datetime as DateTime
# local
import antmath


class Decider(object):

    def __init__(self, logfn=None):
        self.g = {}
        self.logfn = logfn
        self.v = list('NESW')
        # graph of shortest paths between pairs of locations
        # net = { ... loc:{loc:(number, [vector])}, ... loc:{loc:None}, ... }
        self.net = {}
        # goal ages
        # age = { ... loc:age ... }
        self.age = {}
        self.maxage = 0

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.g.update(game)
        self.maxage = 1.5 * self.g['viewradius']

    def think(self, dirt, food, enemyhill, enemyant, myhill, myant, mydead):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        #if self.logfn:
        #    self.logfn('\n' + self._make_map(
        #        dirt, food, enemyhill, enemyant, myhill, myant, mydead))
        goaltime = DateTime.now()
        active = {}
        active.update({loc:0**2 for loc in enemyhill})
        active.update({loc:self.g['attackradius2'] + 1 for loc in enemyant})
        self.logfn('\nactive goals: {}'.format(active))
        passive = {}
        passive.update({loc:1**2 for loc in food})
        # age passive goals; keep old and visible ones; track new ones
        self.age = {loc:age + 1 for loc, age in self.age.iteritems() \
                    if age > self.maxage or loc in passive}
        new = {loc:0 for loc in passive}
        new.update(self.age)
        self.age = new
        # filter passive goals which are old
        passive = {loc:rad for loc, rad in passive.iteritems() \
                   if loc in self.age and self.age[loc] <= self.maxage}
        # if there are some passive goals, add the hill too
        if len(passive) > 2:
            passive.update({loc:self.g['viewradius2'] for loc in myhill})
        self.logfn('\npassive goals: {}\nages: {}'.format(passive, self.age))
        # combine goal lists, giving active goals priority
        passive.update(active)
        goals = passive
        self.logfn('goal time: {}ms'.format(
            (DateTime.now() - goaltime).total_seconds() * 1000.0))
        if goals:
            # divide ants by location into len(goals) groups
            if len(goals) > 1:
                clustime = DateTime.now()
                squads = self.cluster(2, goals.keys(), myant.keys())
                self.logfn('cluster time: {}ms'.format(
                    (DateTime.now() - clustime).total_seconds() * 1000.0))
            else:
                # one 'cluster'
                self.logfn('onecluster')
                rows, cols = zip(*myant.keys())
                r = float(sum(rows)) / len(myant)
                c = float(sum(cols)) / len(myant)
                squads = {(r, c): myant.keys()}
            # assign each squad the closest goal
            for sM, sA in squads.iteritems():
                dist, gloc = min([self.unwrapped_dir(sM, loc) for loc in goals])
                grad = goals[self.wrap(gloc)]
                for aN in sA:
                    # make ants keep the right distance from goals
                    vect = antmath.naive_dir(aN, gloc)
                    #random.shuffle(vect)
                    dist = antmath.distance2(aN, gloc)
                    if dist > grad:
                        myant[aN] = vect
                    elif dist < grad:
                        myant[aN] = [antmath.reverse_dir(v) for v in vect]
                    else:
                        random.shuffle(self.v)
                        myant[aN] = self.v[:]
        else:
            self.logfn('brownian')
            # move each ant individually randomly
            for aN, (aI, aO) in myant.iteritems():
                random.shuffle(self.v)
                myant[aN] = self.v[:]
        return myant

    def cluster(self, iterations, means, ants):
        '''
        means -- [location]
        ants -- [location]

        return {location:[location]}
        '''
        squads = means
        for i in xrange(iterations):
            squads = {sM:[] for sM in squads}
            self.logfn('squads: {}'.format(squads))
            # assign each ant to a squad
            for aN in ants:
                (dist, loc), sA = min([(self.unwrapped_dir(aN, sM), sA) \
                                       for sM, sA in squads.iteritems()])
                sA.append(aN)
            # average the location of each squad
            for sM, sA in squads.items():
                if sA:
                    del squads[sM]
                    rows, cols = zip(*sA)
                    r = float(sum(rows)) / len(sA)
                    c = float(sum(cols)) / len(sA)
                    squads[r, c] = sA
        return squads

    def unwrapped_dir(self, origin, target):
        '''Find the shortest path to the target.

        Return closest unwrapped location and its distance squared as a tuple:
        (distance2, location)

        '''
        h = self.g['rows']
        w = self.g['cols']
        r, c = target
        options = [target, (r-h, c), (r+h, c), (r, c-w), (r, c+w)]
        return min([(antmath.distance2(origin, t), t) for t in options])

    def wrap(self, loc):
        '''Finds the true on-map coordinates of an unwrapped location.'''
        return loc[0] % self.g['rows'], loc[1] % self.g['cols']

    def _make_map(self, dirt, food, enemyhill, enemyant, myhill, myant,
                   mydead):
        # determine what is currently visible
        m = {}
        for antloc in myant:
            for r, c in antmath.allinradius(self.g['viewradius'],
                                            self.g['viewradius2'], antloc):
                r %= self.g['rows']
                c %= self.g['cols']
                m[r, c] = '.'
        m.update({loc:'*' for loc in food})
        m.update({loc:chr(65 + num) for loc, num in enemyhill.iteritems()})
        m.update({loc:chr(97 + num) for loc, num in enemyant.iteritems()})
        m.update({loc:'0' for loc in myhill})
        m.update({loc:str(num) + '!' for loc, num in mydead.iteritems()})
        m.update({loc:str(num) + '@' for loc, (num, oldloc) in myant.iteritems()})
        # make a big string
        s = []
        for r in xrange(self.g['rows']):
            s.append([])
            for c in xrange(self.g['cols']):
                s[-1].append('|' if (r, c) in dirt else '#')
                if (r, c) in m:
                    s[-1][-1] = m[r, c]
            s[-1] = 'MAP:' + ''.join(s[-1])
        return '\n'.join(s)
