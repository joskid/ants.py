# stdlib
import random
from datetime import datetime as DateTime
# local
import antmath


'''
Squad-based goal seeking decider for the 2011 Google AI Challenge.
Maximum Rank was around 1200th of 5400 contestants.

Finds goals and assigns ants to squads each turn. Moves squads toward their
goal each turn. Eliminates goals which have been visible for too long.

(3)
'''


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

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.g.update(game)
        self.MAXAGE = 2.0 * game['viewradius']
        self.PERIMETER = 4 * game['viewradius2']
        self.PERIMETER2 = self.PERIMETER ** 2
        self.ENEMYHILL = (0**2,
                          0**2)
        self.ENEMYANT = ((game['attackradius'] + 3) ** 2,
                         (game['viewradius']) ** 2)
        self.ENEMYANTBATTLE = ((game['attackradius'] + 1) ** 2,
                               (game['attackradius'] + 6) ** 2)
        self.FOOD = (1**2,
                     1**2)
        self.MYHILL = (2 ** 2,
                       6 ** 2)

    def think(self, dirt, food, enemyhill, enemyant, myhill, myant, mydead):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''


        #if self.logfn:
        #    self.logfn('\n' + self._make_map(
        #        dirt, food, enemyhill, enemyant, myhill, myant, mydead))


        # build a list of goals
        goaltime = DateTime.now()
        # active goals
        active = {}
        active.update({loc:self.ENEMYHILL for loc in enemyhill})
        if len(myant) > 1.35 * len(enemyant):
            active.update({loc:self.ENEMYANTBATTLE for loc in enemyant})
        else:
            active.update({loc:self.ENEMYANT for loc in enemyant})
        # log about active goals
        self.logfn('\nactive goals: {}'.format(active)) if self.logfn else None
        # passive goals
        passive = {}
        if len(myant) < 125:
            passive.update({loc:self.FOOD for loc in food})
            # increase age of passive goals; keep ages of old and visible ones
            self.age = {loc:age + 1 for loc, age in self.age.iteritems() \
                        if age > self.MAXAGE or loc in passive}
            # track age new passive goals
            new = {loc:0 for loc in passive}
            new.update(self.age)
            self.age = new
        # filter passive goals which are old
        passive = {loc:rad for loc, rad in passive.iteritems() \
                   if loc in self.age and self.age[loc] <= self.MAXAGE}
        # if there are enemies near a hill, protect the hill
        nearhill = [antmath.allinradius(self.PERIMETER, self.PERIMETER2, loc) \
                    for loc in myhill]
        if set(enemyant).intersection(nearhill):
            passive.update({loc:self.MYHILL for loc in myhill})
        # log about passive goals
        self.logfn('\npassive goals: {}\nages: {}'.format(passive, self.age)
                   ) if self.logfn else None
        # combine goal lists, giving active goals priority
        passive.update(active)
        goals = passive
        # log about goal descision time
        self.logfn('goal time: {}ms'.format(
            (DateTime.now() - goaltime).total_seconds() * 1000.0)
            ) if self.logfn else None


        # assign moves to ants
        if goals:

            if len(goals) > 1:
                # divide ants by location into len(goals) groups
                clustime = DateTime.now()
                squads = self.cluster(1, goals.keys(), myant.keys())
                assert sum(map(len, squads.values())) == len(myant)
                self.logfn('cluster: {}ms'.format(
                    (DateTime.now() - clustime).total_seconds() * 1000.0)
                    ) if self.logfn else None
            else:
                # all ants are in one supercluster
                self.logfn('supercluster') if self.logfn else None
                rows, cols = zip(*myant.keys())
                r = float(sum(rows)) / len(myant)
                c = float(sum(cols)) / len(myant)
                squads = {(r, c): myant.keys()}

            # assign each squad the closest goal
            for sM, sA in squads.iteritems():
                dist, gloc = min([self.unwrapped_dir(sM, loc) for loc in goals])
                gradmin, gradmax = goals[self.wrap(gloc)]
                for aN in sA:
                    # make ants keep the right distance from goals
                    vect = antmath.naive_dir(aN, gloc)
                    dist = antmath.distance2(aN, gloc)
                    if dist > gradmax and dist < 7 * self.g['viewradius2']:
                        myant[aN] = vect
                        random.shuffle(myant[aN]) if gradmax != gradmin else None
                        myant[aN] += [antmath.reverse_dir(v) for v in vect]
                    elif dist < gradmin:
                        myant[aN] = [antmath.reverse_dir(v) for v in vect]
                        random.shuffle(myant[aN]) if gradmax != gradmin else None
                        myant[aN] += vect
                    else:
                        myant[aN] = self.v[:]
                        random.shuffle(myant[aN])

        else:

            # move each ant individually randomly
            self.logfn('brownian') if self.logfn else None
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
            self.logfn('squads: {}'.format(squads)) if self.logfn else None
            # assign each ant to a squad
            for aN in ants:
                (dist, loc), sA = min([(self.unwrapped_dir(aN, sM), sA) \
                                       for sM, sA in squads.iteritems()])
                sA.append(aN)
            # average the location of each squad
            for sM, sA in squads.items():
                if sA:
                    del squads[sM]
                    sumr = sumc = 0
                    for aN in sA:
                        sumr += aN[0]
                        sumc += aN[1]
                    avg = float(sumr) / len(sA), float(sumc) / len(sA)
                    squads[avg] = squads[avg] + sA if avg in squads else sA
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
