import sys
import magellan as mg
from magellan.gui.debug_gui_base import vis_debug_dt

sys.path.append('/Users/Pradap/Documents/Research/Python-Package/enrique/')
mg.init_jvm()

A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')
ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', ['name'], ['name'])
L = mg.read_csv('label_demo.csv', ltable=A, rtable=B)
feat_table = mg.get_features_for_matching(A, B)
G = mg.extract_feat_vecs(L, feature_table=feat_table, attrs_after='gold')
S = mg.train_test_split(G, 8, 7)
dt = mg.DTMatcher(name='DecisionTree')
dt.fit(table = S['train'], exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'], target_attr='gold')
dt.predict(table=S['test'], exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'], target_attr='predicted',
           append=True)
d = mg.eval_matches(S['test'], 'gold', 'predicted')

vis_debug_dt(dt, d, S['test'], exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'], feat_table=feat_table)
print "Hi"