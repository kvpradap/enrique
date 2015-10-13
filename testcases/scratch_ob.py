import magellan as mg
import numpy as np

A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')

ob = mg.OverlapBlocker()

C = ob.block_tables(A, B, 'address', 'address', word_level=False, qgram=3,  overlap_size=3, l_output_attrs=['name', 'name'])
D = ob.block_candset(C, 'name', 'name', overlap_size=1)

E = ob.block_tuples(A.ix[1], B.ix[1], 'name', 'name', overlap_size=1)

print C
print "-----"
print D

print " ----- "

print E