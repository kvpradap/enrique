import sys
import magellan as mg
import pandas as pd


p = '/Users/pradap/Documents/Research/Drug-mapping'
A = mg.read_csv(p + '/data/freepharma_data.csv', low_memory=False)
B = mg.read_csv(p + '/data/shp_data.csv', low_memory=False)
B['DRUG_ID'] = -1*B['DRUG_ID']
A1 = mg.read_csv(p + '/data/freepharma_data_subset_nodrids.csv')

# cleaning
A = A[A.THERAPEUTIC_STANDARD_DESC != 'Medical Supplies']
B = B[B.THERAPEUTIC_STANDARD_DESC != 'Medical Supplies']

# group by generic name
g1 = A.groupby('GENERIC_NAME')
g2 = B.groupby('GENERIC_NAME')

keys_1 = g1.groups.keys()
keys_2 = g2.groups.keys()

df1 = pd.DataFrame(keys_1)
df2 = pd.DataFrame(keys_2)

df1.columns = ['GENERIC_NAME']
df2.columns = ['GENERIC_NAME']

df1 = mg.MTable(df1)
df2 = mg.MTable(df2)

ab = mg.AttrEquivalenceBlocker()
dd = ab.block_tables(df1, df2, 'GENERIC_NAME', 'GENERIC_NAME')

candset_list = []
for row in dd.itertuples(index=False):
    id1, id2 = row[1], row[2]
    k1 = keys_1[id1]
    k2 = keys_2[id2]
    m1 = pd.DataFrame(A.ix[g1.groups[k1]]['DRUG_ID'])
    m2 = pd.DataFrame(B.ix[g2.groups[k2]]['DRUG_ID'])
    m1['tmp'] = 1
    m2['tmp'] = 1
    m11 = mg.MTable(m1, key='DRUG_ID')
    m22 = mg.MTable(m2, key='DRUG_ID')
    c = ab.block_tables(m11, m22, 'tmp', 'tmp')
    candset_list.append(c)
