#!/usr/bin/env python

'''
	Main file to start the phrase extraction, scoring,
	and decoding processing
'''

from __future__ import print_function
from __future__ import division
import alignmentReader
import phraseExtraction
import decoder

# Provide A3 file location here
A3_FILE_LOCATION = "data/20k/A320k.final"

output_file = open("data/phrases.txt", "w")
output_file_scored = open("data/phrases_scored.txt", "w")

dict_vocab = dict()
dict_pairs = dict()

# Read A3 file, extract phrase pairs and write to phrases.txt file
for aa in alignmentReader.GizaA3Reader(A3_FILE_LOCATION):
	output = aa()
	#print output[0], output[1]
	phrase_set = phraseExtraction.phrase_extraction(output[1], output[0])
	for phrase_pair in phrase_set:
		if len(phrase_pair[1]) > 0:
			#print((' '.join(phrase_pair[0]) + ' ||| ' + ' '.join(phrase_pair[1])).encode('utf8'), file=output_file)
			output_file.write((' '.join(phrase_pair[0]) + ' ||| ' + ' '.join(phrase_pair[1]) + '\n').encode('utf8'))
output_file.close()

unscored_phrase_pairs = [tuple(line.strip().split(' ||| ')) for line in open("data/phrases.txt").readlines()]

for (de_phrase, en_phrase) in unscored_phrase_pairs:
	# add german phrase to dictionary
	if de_phrase in dict_vocab:
		dict_vocab[de_phrase] = dict_vocab[de_phrase] + 1
	else:
		dict_vocab[de_phrase] = 1
		
	# add german-english phrase pair to dictionary
	if (de_phrase, en_phrase) in dict_pairs:
		dict_pairs[(de_phrase, en_phrase)] = dict_pairs[(de_phrase, en_phrase)] + 1
	else:
		dict_pairs[(de_phrase, en_phrase)] = 1
		
# iterate ove dict_pars and assign probability values
for (de_phrase, en_phrase) in dict_pairs:
	dict_pairs[(de_phrase, en_phrase)] = dict_pairs[(de_phrase, en_phrase)] / dict_vocab[de_phrase]

#clear vocab dictionary
dict_vocab.clear()
	
for (de_phrase, en_phrase) in sorted(dict_pairs):
	#print(de_phrase + ' ||| ' + en_phrase + ' ||| ' + str(dict_pairs[(de_phrase, en_phrase)]), file=output_file_scored)
	output_file_scored.write(de_phrase + ' ||| ' + en_phrase + ' ||| ' + str(dict_pairs[(de_phrase, en_phrase)]) + '\n')

#clear vocab dictionary
dict_pairs.clear()
	
output_file_scored.close()

'''
	Uncomment below line to continue the decoding process. 
	Should be run separately in order to avoid memory issues
'''	
#decoder.stack_decoder()
