'''
Created on 23-Jan-2014

@author: brij
'''

from sys import stderr
from collections import defaultdict

def bitext(source, target):
    """
    Run through the bitext files, yielding one sentence at a time.
    """
    sourcef = source if hasattr(source, 'read') else open(source, 'r')
    targetf = target if hasattr(target, 'read') else open(target, 'r')
    for (s, t) in zip(sourcef, targetf):
        yield ([None] + s.strip().split(), t.strip().split())
        # null on source side only
        
class IBMModel1(object):
    """
    A class wrapping an IBM Model 1 t-table. After initialization, training
    is performed by calling the iterate() method on the instance.

    >>> model = M1('data/hansards.f.small', 'data/hansards.e.small')
    >>> print round(model['GOUVERNEMENT']['GOVERNMENT'], 3) # before
    0.031
    >>> model.iterate(10)
    >>> print round(model['GOUVERNEMENT']['GOVERNMENT'], 3) # after
    0.859
    """

    def __init__(self, source, target):
        """
        Takes two arguments, specifying the paths (or a file-like objects
        with appropriate 'read' methods) of source and target bitexts
        """
        self.source = source
        self.target = target
        self.ttable = defaultdict(lambda: defaultdict(float)) # p(s|t)
        # compute raw co-occurrence frequencies 
        for (s, t) in bitext(self.source, self.target):
            for sw in s: # FIXME set
                for tw in t: # FIXME set?
                    self.ttable[sw][tw] += 1
        # normalize them
        self._normalize()
        self.n = 0 # number of iterations thus far
 
    def __repr__(self):
        return 'M1({0}, {1})'.format(self.source, self.target)

    def __getitem__(self, item):
        return self.ttable[item]

    def _normalize(self):
        for (sw, twtable) in self.ttable.iteritems():
            Z = sum(twtable.values())
            for tw in twtable:
                twtable[tw] = twtable[tw] / Z

    def iterate(self, n=1, verbose=False):
        """
        Perform n iterations of EM training
        """
        for i in xrange(n):
            if verbose:
                print >> stderr, 'iteration {0}...'.format(self.n)
            acounts = defaultdict(float)
            tcounts = defaultdict(float)
            ## E-step
            for (s, t) in bitext(self.source, self.target):
                for sw in s: # FIXME
                    for tw in t: # FIXME
                        # compute expectation and preserve it
                        c = self.ttable[sw][tw]
                        acounts[(sw, tw)] += c
                        tcounts[tw] += c
            ## M-step
            for ((sw, tw), val) in acounts.iteritems():
                self.ttable[sw][tw] = val / tcounts[tw]
            self._normalize()
            ## wrap up
            self.n += 1

    def decode_pair(self, s, t):
        """
        Given a pair of source/target sentences s, t, output the optimal 
        alignment.
        """
        for sw in s:
            best_p = 0.
            best_a = -1
            for (i, tw) in enumerate(t):
                p = self.ttable[sw][tw]
                if p > best_p: # best one so far
                    best_p = p
                    best_a = i
            yield sw, t[best_a]

    def decode_training(self):
        """
        Generator of the optimal decodings for the training sentences
        """
        for s, t in bitext(self.source, self.target):
            yield self.decode_pair(s, t)

