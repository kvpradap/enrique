import magellan as mg

from magellan.core.mtable import MTable

# read_csv
A = mg.read_csv('../magellan/datasets/table_A.csv', key='ID')
B = mg.read_csv('../magellan/datasets/table_B.csv', key='ID')

print A
print B


