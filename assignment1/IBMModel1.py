'''
Created on 23-Jan-2014

@author: brij
'''

from __future__ import division
from optparse import OptionParser
from collections import defaultdict
from sys import stderr
from operator import itemgetter
import math
import itertools

"""
This function goes through both the files, read one sentence at a time, tokenize it and yield it.
"""
def readCorpus(source, target):
    sourcefile = source if hasattr(source, 'read') else open(source, 'r')
    targetfile = target if hasattr(target, 'read') else open(target, 'r')
    for (src, tgt) in zip(sourcefile, targetfile):
        yield ([None] + src.strip().split(), tgt.strip().split())  # NULL can be present on the source side

"""
Compute Normalization
"""        
def normalizeProbabilties(tTable):
    for (srcword, twtable) in tTable.iteritems():
        Z = sum(twtable.values())
        for tw in twtable:
            twtable[tw] = twtable[tw] / Z
            
"""
Perform n iterations of EM training
"""
def emTraining(source, dest, tTable, n=1, verbose=False):
    
    e_keys = set()
    for (fs, es) in readCorpus(source, dest):
        for e in es:
            e_keys.add(e)
    # default value provided as uniform probability)
    for (fs, es) in readCorpus(source, dest):
        for fword in fs:
            for eword in es:
                tTable[fword][eword] = 1/len(e_keys)
                
    for i in xrange(n):
        if verbose:
            print >> stderr, 'iteration {0}...'.format(i)
            
        # initialize
        count = defaultdict(float)
        total = defaultdict(float)
        s_total = defaultdict(float)
        """
        # Expectation - collect counts
        for (f, e) in readCorpus(source, dest):
            for fword in f:
                for eword in e:
                    # accumulate the expectation value
                    temp = tTable[fword][eword]
                    count[(fword, eword)] += temp
                    total[eword] += temp
        
        # Maximization - estimate probabilities
        for ((sw, tw), val) in count.iteritems():
            tTable[sw][tw] = val / total[tw]
        normalizeProbabilties(tTable)
        calculatePerplexity(source, dest, tTable)
        """
        
        for (f, e) in readCorpus(source, dest):
            for fw in f:
                s_total[fw] = 0
                for ew in e:
                    s_total[fw] += tTable[fw][ew]
            for fw in f:
                for ew in e:
                    if s_total[fw] != 0:
                        count[(fw, ew)] += (tTable[fw][ew] / s_total[fw])
                        total[ew] += (tTable[fw][ew] / s_total[fw])
            
        for (fw, ew) in count.keys():
            tTable[fw][ew] = count[(fw, ew)] / total[ew]
            
        calculatePerplexity(source, dest, tTable)
            
    #printProbabilityTable(tTable)
            
        
def _perplexityPair(s, t, ttable):
    perp = 1
    for sw in s:
        temp = 0
        for tw in t:
            p = ttable[sw][tw]
            temp = temp + p
        perp = perp * temp
    #print perp, (pow(len(s), len(t)))
    if perp != 0:
        return math.log((perp / (pow(len(s), len(t)))), 2)
    else:
        return 0
    

def calculatePerplexity(source, target, pTable):
    """
    Generator of the optimal decodings for the training sentences
    """
    total = 0
    for s, t in readCorpus(source, target):
        temp = _perplexityPair(s, t, pTable)
        total = total + temp
    total = -total
    print total
    
def printProbabilityTable(tTable):
    for (fword, twtable) in tTable.iteritems():
        print '{0}'.format(fword),
        for (eword, prob) in sorted(twtable.iteritems(), reverse=True, key=itemgetter(1)):
            if prob < 0.0001: continue # neglecting the extremely low possibilities
            print '{0}:{1:.4f}'.format(eword, prob),
        print
        print
    

if __name__ == '__main__':
    usage = "usage: %prog -s <source_language_file> -d <target_language_file> -n <num_of_iterations_for_EM>"
    # Parse the command line arguments to retrieve source and destination language corpuses
    parser = OptionParser(usage)
    parser.add_option("-s", "--source", "--src", dest="src")
    parser.add_option("-d", "--destination", "--dst", dest="dst")
    parser.add_option("-n", "--iterations", type="int", dest="iterCount")
    (options, args) = parser.parse_args()

    # Check the supplied arguments
    if not options.src:
        exit('Source file not specified (use -s)')
    elif not options.dst:
        exit('Target file not specified (use -d)')
    elif options.iterCount < 1:
        exit('Number of iterations not specified (use -n)')
        
    tTable = defaultdict(lambda: defaultdict(float))  # t(e|f)
        
    """
    Count how many times foreign and english word pairs co-occured (computing co-occurrence frequency)
    Intializing t(e|f)
    
    for (srcSentence, dstSentence) in readCorpus(options.src, options.dst):
        for srcword in srcSentence:
            for dstword in dstSentence:
                tTable[srcword][dstword] += 1
                """
                
    # Normalize the t-table - assigning initial probabilities as 1/N
    #normalizeProbabilties(tTable);
    
    #printProbabilityTable(tTable)
    
    #calculatePerplexity(options.src, options.dst, tTable)
    
    # Perform n iterations of EM training
    emTraining(options.src, options.dst, tTable, 10, True)
    
    # Print the computed probability table t(e|f)
    #printProbabilityTable(tTable)
    
    
            
            
