import magellan as mg
A = mg.load_dataset('table_A', 'id')
B = mg.load_dataset('table_B', 'id')

Ap, Bp = mg.down_sample(A, B, 5, 2)

print Ap

print Bp