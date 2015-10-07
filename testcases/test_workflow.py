import magellan as mg
import numpy as np

A = mg.read_csv('../magellan/datasets/table_A.csv', key='ID')
A.ix[1, 'ID'] = np.NAN
A.to_csv('tbla.csv')
A1 = mg.read_csv('tbla.csv')
print A1