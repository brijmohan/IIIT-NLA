#!/usr/bin/env python

"""Implementation of the phrase extraction algorithm"""

def extract(A, (e, f), f_start, f_end, e_start, e_end):
    # Check if the alignment points violate consistency
    for e_word, f_word in A:
        if e_word < e_start or e_word > e_end:
            if f_start <= f_word <= f_end:
                return set()

    # Add phrase pairs
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
