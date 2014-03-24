'''
Created on 23-Jan-2014

@author: brij - 201307694
'''

from __future__ import division
from optparse import OptionParser
from collections import defaultdict
from sys import stderr
from operator import itemgetter
import math

"""
This function goes through both the files, read one sentence at a time, tokenize it and yield it.
"""
def readCorpus(source, target):
    sourcefile = source if hasattr(source, 'read') else open(source, 'r')
    targetfile = target if hasattr(target, 'read') else open(target, 'r')
    for (src, tgt) in zip(sourcefile, targetfile):
        yield ([None] + src.strip().split(), tgt.strip().split())  # NULL can be present on the source side
     
"""
Calculate partial perplexity over a pair of sentence
""" 
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
        return math.log(perp, 2) - math.log(pow(len(s), len(t)), 2)
    else:
        return 0
    
"""
Calculate perplexity over the corpus for one given iteration
and the values accumulated as t(e|f)
"""
def calculatePerplexity(source, target, pTable):
    total = 0
    for s, t in readCorpus(source, target):
        temp = _perplexityPair(s, t, pTable)
        total = total + temp
    total = -total
    print "Perplexity: ", total
           
"""
Perform n iterations of EM training
"""
def emTraining(source, target, tTable, n=1):
    
    e_keys = set()
    for (fs, es) in readCorpus(source, target):
        for e in es:
            e_keys.add(e)
    # default value provided as uniform probability
    for (fs, es) in readCorpus(source, target):
        for fword in fs:
            for eword in es:
                tTable[fword][eword] = 1/len(e_keys)
                
    for i in xrange(n):
        print >> stderr, 'iteration {0}...'.format(i)
            
        # initialize
        count = defaultdict(float)
        total = defaultdict(float)
        s_total = defaultdict(float)
        
        for (f, e) in readCorpus(source, target):
            # Compute normalization
            for fw in f:
                s_total[fw] = 0
                for ew in e:
                    s_total[fw] += tTable[fw][ew]
            # Collect counts
            for fw in f:
                for ew in e:
                    if s_total[fw] != 0:
                        count[(fw, ew)] += (tTable[fw][ew] / s_total[fw])
                        total[ew] += (tTable[fw][ew] / s_total[fw])
        
        # Estimate probabilities
        for (fw, ew) in count.keys():
            tTable[fw][ew] = count[(fw, ew)] / total[ew]
            
        calculatePerplexity(source, target, tTable)
            
    #printProbabilityTable(tTable)

def printProbabilityTable(tTable):
    for (fword, twtable) in tTable.iteritems():
        print '{0}'.format(fword),
        for (eword, prob) in sorted(twtable.iteritems(), reverse=True, key=itemgetter(1)):
            if prob < 0.0001: continue # neglecting the extremely low possibilities
            print '{0}:{1:.4f}'.format(eword, prob),
        print
        print
        
"""
Given a pair of source/target sentences s, t, output the optimal 
alignment.
"""
def align_sentence(s, t, tTable):
    for sw in s:
        best_prob = 0.
        best_align = -1
        for (i, tw) in enumerate(t):
            p = tTable[sw][tw]
            if p > best_prob: # best one so far
                best_prob = p
                best_align = i
        yield sw, t[best_align]
        
"""
Generator of the optimal decodings for the training sentences
"""
def align_corpus(source, target, tTable):
    for s, t in readCorpus(source, target):
        yield align_sentence(s, t, tTable)
    
def print_alignment(src, dest, tTable):
    for alignment in align_corpus(src, dest, tTable):
        srcSentence = ""
        tgtSentence = ""
        for (src_words, tgt_words) in alignment:
            if src_words is not None:
                srcSentence += (src_words + " ")
            if tgt_words is not None:
                tgtSentence += (tgt_words + " ")
        print srcSentence
        print tgtSentence
        print

if __name__ == '__main__':
    usage = "usage: %prog -s <source_language_file> -d <target_language_file> -n <num_of_iterations_for_EM>"
    #-s /home/brij/Documents/IIIT/NLP/assignment1/data/en20000.txt -d /home/brij/Documents/IIIT/NLP/assignment1/data/de20000.txt -n 10
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
    
    # Perform n iterations of EM training
    emTraining(options.src, options.dst, tTable, 10)
    
    # Print alignment for 5 sentences from training set de -> en
    #print_alignment("/home/brij/Documents/IIIT/NLP/assignment1/data/decode_training_de.txt", 
    #                "/home/brij/Documents/IIIT/NLP/assignment1/data/decode_training_en.txt", tTable)
    # Print alignment for 5 sentences from outside training set de -> en
    #print_alignment("/home/brij/Documents/IIIT/NLP/assignment1/data/decode_outside_de.txt", 
    #                "/home/brij/Documents/IIIT/NLP/assignment1/data/decode_outside_en.txt", tTable)
    
    
    # Print alignment for 5 sentences from training set en -> de
    print_alignment("/home/brij/Documents/IIIT/NLP/assignment1/data/decode_training_en.txt", 
                    "/home/brij/Documents/IIIT/NLP/assignment1/data/decode_training_de.txt", tTable)
    # Print alignment for 5 sentences from outside training set en -> de
    print_alignment("/home/brij/Documents/IIIT/NLP/assignment1/data/decode_outside_en.txt", 
                    "/home/brij/Documents/IIIT/NLP/assignment1/data/decode_outside_de.txt", tTable)
    
    
    # Print the computed probability table t(e|f)
    #printProbabilityTable(tTable)
    
    
            
            
