# stdlib
import random
# local
import protocol


'''
Goal seeking decider for the 2011 Google AI Challenge.
Maximum Rank was around 1560th of 5400 contestants.

Assigns wayward ants to goals each turn. Moves goal oriented ants toward their
goal each turn. Eliminates goals which ants do not make progress toward.

(2)
'''


class Decider(object):

    def __init__(self, logfn=None):
        self.g = {}
        self.logfn = logfn
        self.d = list('NESW')
        self.ds = set(self.d)
        self.maxage = 0
        # ant goals and state
        # ant = { ... id:(loc, [nogo]) ... }
        self.goal = {}
        # graph of shortest paths between pairs of locations
        # net = { ... loc:{loc:(number, [vector])}, ... loc:{loc:None}, ... }
        self.net = {}

    def start(self, game):
        '''Set up the decider according to the game specifications.'''
        self.g.update(game)
        self.maxage = self.g['viewradius'] * 1.5

    def think(self, dirt, food, enemyhill, enemyant, myhill, myant, mydead):
        '''Return a dict with the keys of myant mapped to lists of NESW=.'''
        d = Decider.distance2
        #if self.logfn:
        #    self.logfn('\n' + self._make_map(
        #        dirt, food, enemyhill, enemyant, myhill, myant, mydead))
        goals = {}
        goals.update(food)
        goals.update(enemyant)
        goals.update(enemyhill)
        for aN, (aI, aO) in myant.iteritems():
            gloc, nogo = self.goal[aI] if aI in self.goal else (None, [])
            # does the goal exist?
            if gloc in goals:
                # did the ant get closer?
                if d(gloc, aN) < d(gloc, aO):
                    # move closer still
                    self.goal[aI] = (gloc, nogo)
                    myant[aN] = Decider.naive_path(aN, gloc)
                else:
                    # forget that goal
                    self.goal[aI] = gloc, nogo = (None, nogo + [gloc])
            # is the goal a fantasy?
            if gloc not in goals:
                # find the nearest one not in nogo
                option = set(goals).difference(nogo)
                gloc = Decider.nearest(aN, option) if option else None
                if gloc:
                    # set goal and move there
                    del goals[gloc]
                    self.goal[aI] = (gloc, nogo)
                    myant[aN] = Decider.naive_path(aN, gloc)
                else:
                    # move randomly
                    random.shuffle(self.d)
                    myant[aN] = self.d[:]
                #self.logfn('#{} to {} for goal {}'.format(
                #    ant, myant[loc], self.ant[ant] if ant in self.ant else 'explore'))
        return myant

    def extend(self, vectors):
        return self.vectors + list(self.ds.difference(vectors))

    @staticmethod
    def reverse(direction):
        return {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]

    @staticmethod
    def naive_path(a, b):
        ar, ac = a
        br, bc = b
        deltar = br - ar
        deltac = bc - ac
        r = 'N' if deltar < 0 else 'S'
        c = 'W' if deltac < 0 else 'E'
        return [r, c] if deltar ** 2 > deltac ** 2 else [c, r]

    @staticmethod
    def nearest(a, others):
        '''Return the nearest object to loc a from the seq others.'''
        d = Decider.distance2
        return reduce(lambda acc, x: x if d(a,x) < d(a,acc) else acc, others)

    @staticmethod
    def distance2(a, b):
        '''Euclidean distance squared.'''
        return (a[0] - b[0]) ** 2 + \
               (a[1] - b[1]) ** 2

    def _make_map(self, dirt, food, enemyhill, enemyant, myhill, myant,
                   mydead):
        # determine what is currently visible
        m = {}
        for antloc in myant:
            for _, (r, c) in protocol.allinradius(self.g['viewradius'], antloc):
                r %= self.g['rows']
                c %= self.g['cols']
                m[r, c] = '.'
        m.update({loc:'*' for loc in food})
        m.update({loc:chr(65 + num) for loc, num in enemyhill.iteritems()})
        m.update({loc:chr(97 + num) for loc, num in enemyant.iteritems()})
        m.update({loc:'0' for loc in myhill})
        m.update({loc:str(num) + '!' for loc, num in mydead.iteritems()})
        m.update({loc:str(num) + '@' for loc, num in myant.iteritems()})
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
