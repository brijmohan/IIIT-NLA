#!/usr/bin/env python
import argparse
import sys
import utils
import heapq
from collections import namedtuple

'''
	File to initiate decoding process by reading TM, LM, and input values
'''

def stack_decoder(inputFile='data/input', phraseTable='data/phrases_scored.txt', langModel='data/enLM.txt'):

	tm = utils.TM(phraseTable, sys.maxint)
	lm = utils.LM(langModel)
	num_sents = sys.maxint
	stack_size = 50
	verbose = True
	sys.stderr.write('Decoding %s...\n' % (inputFile,))
	input_sents = [tuple(line.strip().split()) for line in open(inputFile).readlines()[:num_sents]]

	hypothesis = namedtuple('hypothesis', 'logprob, lm_state, predecessor, phrase')
	for f in input_sents:
		
		initial_hypothesis = hypothesis(0.0, lm.begin(), None, None)
		
		stacks = [{} for _ in f] + [{}]
		stacks[0][lm.begin()] = initial_hypothesis
		for i, stack in enumerate(stacks[:-1]):
			# extend the top s hypotheses in the current stack
			for h in heapq.nlargest(stack_size, stack.itervalues(), key=lambda h: h.logprob): # prune
			
			#Get continguous phrases from i:j for all j
				for j in xrange(i+1,len(f)+1):
					if f[i:j] in tm:
						for ijphrase in tm[f[i:j]]:
							logprob = h.logprob + ijphrase.logprob
							lm_state = h.lm_state
							for word in ijphrase.english.split():
								(lm_state, word_logprob) = lm.score(lm_state, word)
								logprob += word_logprob
							logprob += lm.end(lm_state) if j == len(f) else 0.0
							ijnode = hypothesis(logprob, lm_state, h, ijphrase)
							if lm_state not in stacks[j] or stacks[j][lm_state].logprob < logprob: # second case is recombination
								stacks[j][lm_state] = ijnode
				else:
					continue
				#Allow for local reordering
				for k in xrange(j+1,len(f)+1):
					if f[j:k] in tm:
						for jkphrase in tm[f[j:k]]:
							lp1 = h.logprob + jkphrase.logprob
							lms1 = tuple(h.lm_state)
							for w1 in jkphrase.english.split():
								(lms1, wlp1) = lm.score(lms1, w1)
								lp1 += wlp1
							lp1 += lm.end(lms1) if k == len(f) else 0.0
							jknode = hypothesis(lp1, lms1, h, jkphrase)
							lp2 = jknode.logprob + ijphrase.logprob
							lms2 = tuple(jknode.lm_state)
							for w2 in ijphrase.english.split():
								(lms2, wlp2) = lm.score(lms2, w2)
								lp2 += wlp2
							lp2 += lm.end(lms2) if j == len(f) else 0.0
							iknode = hypothesis(lp2, lms2, jknode, ijphrase)
							if lms2 not in stacks[k] or stacks[k][lms2].logprob < lp2:
												stacks[k][lms2] = iknode
							else:
								continue
							for l in xrange(k+1,len(f)+1):
								if f[k:l] in tm:
									for klphrase in tm[f[k:l]]:
										lp3 = jknode.logprob + klphrase.logprob
										lms3 = tuple(jknode.lm_state)
										for w3 in klphrase.english.split():
											(lms3, wlp3) = lm.score(lms3, w3)
											lp3 += wlp3
										lp3 += lm.end(lms3) if l == len(f) else 0.0
										klnode = hypothesis(lp3, lms3, jknode, klphrase)
										lp4 = klnode.logprob + ijphrase.logprob
										lms4 = tuple(klnode.lm_state)
										for w4 in ijphrase.english.split():
											(lms4, wlp4) = lm.score(lms4, w4)
											lp4 += wlp4
										lp4 += lm.end(lms4) if j == len(f) else 0.0
										ilnode = hypothesis(lp4, lms4, klnode, ijphrase)
										if lms4 not in stacks[l] or stacks[l][lms4].logprob < lp4:
											stacks[l][lms4] = ilnode

		# find best translation by looking at the best scoring hypothesis
		# on the last stack
		winner = max(stacks[-1].itervalues(), key=lambda h: h.logprob)
		def extract_english_recursive(h):
			return '' if h.predecessor is None else '%s%s ' % (extract_english_recursive(h.predecessor), h.phrase.english)
		print extract_english_recursive(winner)

		if verbose:
			def extract_tm_logprob(h):
				return 0.0 if h.predecessor is None else h.phrase.logprob + extract_tm_logprob(h.predecessor)
			tm_logprob = extract_tm_logprob(winner)
