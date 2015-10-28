import magellan as mg
import pandas as pd
mg.init_jvm()

A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')
mg.init_jvm()
#not reqd
ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', ['name', 'address'], ['name', 'address'])

L = mg.read_csv('label_ab_correct_labels.csv', ltable=A, rtable=B)
feat_table = mg.get_features_for_matching(A, B)
f = feat_table.ix[[9, 10, 17]]
G = mg.extract_feat_vecs(L, feature_table=f, attrs_after='gold')

dt = mg.DTMatcher()
dt.fit(table=G,  exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'], target_attr='gold')
t = dt.predict(table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'], append=True, inplace=False,
               target_attr='predicted')


# ret_val, node_list = mg.vis_tuple_debug_dt_matcher(dt, G.ix[0],
#                                   exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'], ensemble_flag=False)


# print ret_val
# print node_list


