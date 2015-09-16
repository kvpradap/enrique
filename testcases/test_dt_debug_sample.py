import magellan as mg
import pandas as pd

from magellan.debug.decisiontree import visualize_tree, debug_dt
from magellan.feature.extractfeatures import apply_feat_fns

mg.init_jvm()

A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')

ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', l_output_attrs=['name', 'hourly_wage', 'zipcode'],
                    r_output_attrs=['name', 'hourly_wage', 'zipcode'])

S = mg.sample_one_table(C, 10)
L = mg.load_table('../notebooks/demo_label.pkl')
L.set_property('ltable', A)
L.set_property('rtable', B)
feat_table = mg.get_features_for_blocking(A, B)

x = [17, 19]
feat_table = feat_table.ix[x]

S_prime = mg.extract_feat_vecs(L, attrs_after='label', feat_table=feat_table)
dt = mg.DTMatcher(random_state=80)
dt.fit(table=S_prime, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'label'], target_attr='label')

cols = [c not in ['_id', 'ltable.ID', 'rtable.ID', 'label'] for c in S_prime.columns]
feature_names = S_prime.columns[cols]
visualize_tree(dt, S_prime.columns, ['_id', 'ltable.ID', 'rtable.ID', 'label'])

t1 = A.ix[1]
t2 = B.ix[5]
feat_values = apply_feat_fns(t1, t2, feat_table)
feat_values = pd.Series(feat_values)
feat_values =  feat_values[feature_names]
v = feat_values.values
clf = dt.clf
p = clf.predict_proba(v)
print feat_values
print p
mg.debug_dt(dt, t1, t2, feat_table, S_prime.columns, ['_id', 'ltable.ID', 'rtable.ID', 'label'])


# for id1, t1 in A.iterrows():
#     for id2, t2 in B.iterrows():
#         feat_values = apply_feat_fns(t1, t2, feat_table)
#         feat_values = pd.Series(feat_values)
#         feat_values =  feat_values[feature_names]
#         v = feat_values.values
#         clf = dt.clf
#         p = clf.predict_proba(v)
#
#         print id1, id2, p


#print feat_values

