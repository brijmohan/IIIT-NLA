#Input: word alignment A for sentence pair (e,f)
#Output: set of phrase pairs BP
import sys
e=sys.argv[1]
f=sys.argv[2]

BP=() # set of dictionary
for estart in xrange (1, len(e)) :
	for eend in xrange (estart,len(e)) :

#// find the minimally matching foreign phrase

		(fstart , fend ) = ( len(f), 0 )

		for all (e1,f1) in A :

			if estart ≤ e1 and e1 ≤ eend :

				fstart = min( f1, fstart )

				fend = max( f1, fend )

			

		

		BP.append(extract (fstart , fend , estart , eend )) 

	


function extract (fstart , fend , estart , eend )
	if fend == 0: #// check if at least one alignment point
		return {}
# // check if alignment points violate consistency
	for all (e1,f1) in A.getItems():

		 if e < e start or e > e end:
			return {}

# add pharse pairs (incl. additional unaligned f)
	E = {}
	fs = fstart
	repeat

		fe = fend

		repeat

			add phrase pair ( e start .. e end , f s .. f e ) to set E

			fe=fe +1

		until fe aligned

		fs=fs-1# − −
	until fs aligned
	return E
