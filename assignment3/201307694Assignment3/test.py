#!/usr/bin/env python

import decoder

'''
	Run this file to initiate decoding
	Input needed
	 Phrase table (TM): default location (data/phrases_scored.txt)
	 Language Model (LM): default location (data/enLM.txt)
	 Input file: default location (data/input)
'''
decoder.stack_decoder()
