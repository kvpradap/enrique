from magellan.evaluation.matcher_and_trigger_crossvalidation import cv_matcher_and_trigger
import magellan as mg
A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')
ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', ['name'], ['name'])
mg.init_jvm()
#L = mg.label_table(C, 'gold')
#L.to_csv('label.csv')
L = mg.read_csv('label.csv', ltable=A, rtable=B)
feature_table = mg.get_features_for_matching(A, B)
G = mg.extract_feature_vecs(L, feature_table=feature_table, attrs_after='gold')
m = mg.LinRegMatcher()
t = cv_matcher_and_trigger(m, None, table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'],
                           target_attr='gold', k=5, metric='precision', random_state=0)

res = mg.select_matcher([m], table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'],
                           target_attr='gold', k=5, metric='f1', random_state=0)
print res['cv_stats']

