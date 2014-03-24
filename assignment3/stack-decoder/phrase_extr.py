#!/usr/bin/python

"""Implementation of the phrase extraction algorithm from Koehn 5.2.3"""

# The sentence pair used to test the algorithm
sent_pair = (("michael", "assumes", "that", "he", "will", "stay", "in", "the",
        "house"), ("michael", "geht", "davon", "aus", ",", "dass", "er", "im",
        "haus", "bleibt"))

# The word alignments as a set of pairs. The first value in each pair is the
# index of the English word, the second is the index of the foreign word.
A = {(0, 0), (1, 1), (1, 2), (1, 3), (2, 5), (3, 6), (4, 9), (5, 9),
        (6, 7), (7, 7), (8, 8)}

def extract(A, (e, f), f_start, f_end, e_start, e_end):
    """The extract function takes as input rectangle in the alignment grid,
    bounded by f_start, f_end, e_start and e_end. With this rectangle it
    considers all aligned word pairs and returns the empty set when a foreign
    word located within the rectangle is aligned to an english word outside the
    rectangle.

    That is, what the english phrase will be is fixed. The function simply
    tries to find foreign phrases to pair with the english phrase that do not
    'violate the consistency' of the word alignment. If any of the forein words
    bounded between f_start and f_end align to an English word outside the
    rectangle, then the rectangle is rejected as there is no foreign phrase
    corresponding to the fixed English phrase.

    The first section ensures this consistency. The second section with the
    nested loops adds the foreign phrase contained in f_start and f_end, and
    extends beyond the rectangle to find foreign words that are unaligned, and
    also pairs them to the fixed English phrase.
    """

    # Check if the alignment points violate consistency
    for e_word, f_word in A:
        if e_word < e_start or e_word > e_end:
            if f_start <= f_word <= f_end:
                return set()

    # Add phrase pairs (incl. additional unaligned f)
    E = set()
    f_s = f_start
    while True:
        f_e = f_end
        while True:
            E.add((e[e_start:e_end+1], f[f_s:f_e+1]))
            f_e += 1
            if any(f_index == f_e for (_, f_index) in A) or f_e >= len(f):
                break
        f_s -= 1
        if any(f_index == f_s for (_, f_index) in A) or f_s < 0:
            break

    return E

def phrase_extraction(A, (e,f)):
    """Implementation of the phrase extraction algorithm from Koehn 5.2.3.

    This function iterates over all possible English phrases, the starting and
    end points being used to bound the visual rectangle vertically. It looks at
    all the aligned words, and finds the first and last foreign word that align
    to English words in that rectangle. The rectangle is then passed to
    extract() and the phrase pairs are added to the BP set of all phrase pairs.
    """

    # Initialize BP
    BP = set()

    for e_start in range(0,len(e)):
        for e_end in range(e_start, len(e)):
            # Find the minimally matching foreign phrase
            f_start, f_end = len(f), -1
            for e_word, f_word in A:
                if e_start <= e_word <= e_end:
                    f_start = min(f_word, f_start)
                    f_end = max(f_word, f_end)
            BP |= extract(A, (e,f), f_start, f_end, e_start, e_end)

    return BP

print phrase_extraction(A, sent_pair)
