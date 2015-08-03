import magellan as mg

#i/o
A = mg.read_csv('../magellan/datasets/table_A.csv', key = 'ID')
B = mg.read_csv('../magellan/datasets/table_B.csv', key = 'ID')

print A.properties

A.to_csv('./table_a_test.csv', index=False)
A.save_table('./table_a.pkl')

A1 = mg.load_table('./table_a.pkl')
print type(A1)
#print A1.properties

A1 = mg.sample_one_table(A, 4)
#print A1
#print A1.properties
A1, B1 = mg.sample_two_tables(A, B, 4, 2)
print A1

print B1
