from magellan.matcherselection._mlmatcherselection import select_matcher_test
from magellan.matcherselection.mlmatcherselection import select_matcher

import magellan as mg
mg.init_jvm()

A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')
ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', ['name'], ['name'])
# L = mg.read_csv('../../magellan/testcases/debug-tests/label_ab_correct_books.csv', ltable=A, rtable=B)
L = mg.label_table(C, 'gold')
L.to_csv('mur_labels')
F = mg.get_features_for_matching(A, B)
G = mg.extract_feat_vecs(L, feature_table=F, attrs_after='gold')

dt = mg.DTMatcher()

select_matcher_test(dt, table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'], target_attr='gold',
                    random_state=0)


